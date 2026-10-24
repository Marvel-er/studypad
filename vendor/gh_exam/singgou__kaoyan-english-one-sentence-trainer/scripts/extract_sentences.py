#!/usr/bin/env python3
"""Extract Reading Part A sentences from one authentic exam file.

Supported inputs: PDF, DOC, DOCX (including binary DOC files mislabeled as
DOCX), TXT, and Markdown. Old Word files use a read-only Microsoft Word COM
fallback on Windows, then LibreOffice or antiword when available.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

from classify_sentences import classify, words


OLE_SIGNATURE = bytes.fromhex("D0CF11E0A1B11AE1")
ZIP_SIGNATURES = (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08")
STRUCTURAL_RE = re.compile(
    r"^(?:Section\s*[IⅠVⅡⅢ]+(?:\s+.*)?|Part\s*[ABC](?:\s+Directions:?)?|Directions:?|(?:Text|Passage)\s*[1-5]\s*[:：.]?)$",
    re.IGNORECASE,
)
TEXT_HEADING_RE = re.compile(r"^(?:Text|Passage)\s*([1-5])\s*[:：.]?$", re.IGNORECASE)
QUESTION_NUMBER_RE = re.compile(r"^(?:2[1-9]|3\d|40)\s*[.．、:]\s*")
OPTION_RE = re.compile(r"^(?:\[[ABCD]\]|\([ABCD]\)|[ABCD]\s*[.．、])\s*", re.IGNORECASE)
QUESTION_HINT_RE = re.compile(
    r"\b(?:according to|author|paragraph|text|passage|phrase|word|best title|"
    r"can be inferred|implies?|suggests?|indicates?|attitude|mainly about|"
    r"purpose|why|which of the following|what can we learn)\b",
    re.IGNORECASE,
)
END_PUNCTUATION_RE = re.compile(r"[.!?][\"'”’）)]*$")
ABBREVIATIONS = (
    "Mr.", "Mrs.", "Ms.", "Dr.", "Prof.", "St.", "No.", "vs.", "etc.",
    "e.g.", "i.e.", "U.S.", "U.K.", "U.N.", "a.m.", "p.m.",
)
SKILL_ROOT = Path(__file__).resolve().parents[1]
TEXT_CORRECTIONS_PATH = SKILL_ROOT / "data" / "passage_text_corrections.reviewed.json"


class ExtractionError(RuntimeError):
    """Raised when a source cannot be safely extracted."""


@dataclass(frozen=True)
class Block:
    text: str
    page: int | None = None
    kind: str = "paragraph"
    locator: int | None = None


def normalize_space(text: str) -> str:
    """Normalize layout whitespace without rewriting punctuation or wording."""
    text = text.replace("\u00ad", "").replace("\xa0", " ")
    text = text.replace("\x0b", " ").replace("\x0c", " ")
    return re.sub(r"\s+", " ", text).strip()


def normalized_key(text: str) -> str:
    """Return a layout-insensitive key for deduplication and corroboration."""
    return "".join(re.findall(r"[a-z0-9]+", text.lower().replace("’", "'")))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


@functools.lru_cache(maxsize=1)
def load_text_correction_config() -> dict[str, Any]:
    if not TEXT_CORRECTIONS_PATH.is_file():
        raise ExtractionError(
            f"required passage correction file is missing: {TEXT_CORRECTIONS_PATH}"
        )
    try:
        value = json.loads(TEXT_CORRECTIONS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ExtractionError(f"invalid passage correction file: {exc}") from exc
    if (
        not isinstance(value, dict)
        or value.get("schema_version") != 1
        or not isinstance(value.get("token_replacements"), dict)
        or not isinstance(value.get("phrase_corrections"), list)
        or not isinstance(value.get("known_source_gaps"), list)
    ):
        raise ExtractionError("invalid passage correction schema")
    return value


def passage_completeness_metadata(
    year: int,
    article_number: int,
    source_root: Path | None = None,
) -> dict[str, Any]:
    """Return fail-closed completeness metadata for one Reading Part A article."""

    matches = [
        item
        for item in load_text_correction_config()["known_source_gaps"]
        if isinstance(item, dict)
        and int(item.get("year", -1)) == year
        and int(item.get("article", -1)) == article_number
    ]
    if len(matches) > 1:
        raise ExtractionError(
            f"duplicate passage completeness entries for {year} Text {article_number}"
        )
    if not matches:
        return {
            "source_completeness_status": "no_known_gap",
            "safe_for_training": True,
            "known_source_gap": None,
        }
    item = matches[0]
    evidence_source = str(item.get("evidence_source", ""))
    evidence_pages = item.get("evidence_pages")
    description = str(item.get("description", ""))
    if (
        not evidence_source
        or not description
        or not isinstance(evidence_pages, list)
        or not evidence_pages
        or any(not isinstance(page, int) or page < 1 for page in evidence_pages)
        or item.get("safe_for_training") is not False
    ):
        raise ExtractionError(
            f"invalid passage completeness entry for {year} Text {article_number}"
        )
    evidence_hash: str | None = None
    if source_root is not None:
        evidence_path = source_root / evidence_source
        if not evidence_path.is_file():
            raise ExtractionError(
                f"passage completeness evidence source is missing: {evidence_source}"
            )
        evidence_hash = sha256_file(evidence_path)
    gap = {
        "description": description,
        "evidence_source": evidence_source,
        "evidence_source_sha256": evidence_hash,
        "evidence_pages": evidence_pages,
        "evidence_method": str(item.get("evidence_method", "visual_structure_review")),
        "external_corroboration_urls": list(
            item.get("external_corroboration_urls", [])
        ),
        "note": str(item.get("note", "")),
    }
    return {
        "source_completeness_status": "known_incomplete_source",
        "safe_for_training": False,
        "known_source_gap": gap,
    }


def clean_common_extraction_artifacts(text: str) -> tuple[str, list[str]]:
    """Normalize narrow, repeatedly verified extraction glyph artifacts."""

    cleaned = text
    warnings: list[str] = []

    def apply(pattern: str, replacement: str, label: str, flags: int = 0) -> None:
        nonlocal cleaned
        cleaned, count = re.subn(pattern, replacement, cleaned, flags=flags)
        if count:
            warnings.append(f"{label}:{count}")

    apply(r"\bfbr\b", "for", "normalized_fbr_for_artifact", re.IGNORECASE)
    apply(
        r"(?<=[A-Za-z.!?])\^\^(?=(?:\s|$))",
        "”",
        "normalized_pdf_double_caret_closing_quote",
    )
    apply(
        r"(?<=[A-Za-z])5s\b",
        "’s",
        "normalized_digit_apostrophe_artifact",
        re.IGNORECASE,
    )
    apply(
        r"(?<=s)[59]\b",
        "’",
        "normalized_plural_digit_apostrophe_artifact",
    )
    apply(
        r"(?<=[A-Za-z])9\s+s\b",
        "’s",
        "normalized_spaced_digit_apostrophe_artifact",
    )
    apply(
        r"(?<=[A-Za-z])55\b",
        "”",
        "normalized_double_digit_closing_quote_artifact",
    )
    apply(
        r"(?<=[A-Za-z])一(?=\s*[A-Za-z])",
        "—",
        "normalized_cjk_dash_artifact",
    )
    apply(r"\bandK\b", "and K", "normalized_missing_space_artifact")

    token_replacements = load_text_correction_config()["token_replacements"]
    for original, replacement in token_replacements.items():
        pattern = rf"(?<![A-Za-z]){re.escape(str(original))}(?![A-Za-z])"
        cleaned, count = re.subn(pattern, str(replacement), cleaned)
        if count:
            warnings.append(f"reviewed_token_case_correction:{original}:{count}")
    return normalize_space(cleaned), warnings


def clean_reading_text(
    text: str,
    year: int,
    article_number: int,
    source_root: Path | None = None,
) -> tuple[str, list[str], list[dict[str, Any]]]:
    """Apply common glyph rules and exact evidence-backed passage corrections."""

    cleaned, warnings = clean_common_extraction_artifacts(text)
    applied: list[dict[str, Any]] = []
    for item in load_text_correction_config()["phrase_corrections"]:
        if not isinstance(item, dict):
            raise ExtractionError("passage phrase correction must be an object")
        if int(item.get("year", -1)) != year or int(item.get("article", -1)) != article_number:
            continue
        expected = str(item.get("expected", ""))
        replacement = str(item.get("replacement", ""))
        evidence_source = str(item.get("evidence_source", ""))
        if not expected or not replacement or not evidence_source or expected == replacement:
            raise ExtractionError("invalid passage phrase correction")
        if expected not in cleaned:
            continue
        cleaned = cleaned.replace(expected, replacement, 1)
        evidence_hash: str | None = None
        if source_root is not None:
            evidence_path = source_root / evidence_source
            if not evidence_path.is_file():
                raise ExtractionError(
                    f"passage correction evidence source is missing: {evidence_source}"
                )
            evidence_hash = sha256_file(evidence_path)
        warnings.append(
            f"reviewed_passage_text_correction:{year}:Text{article_number}"
        )
        applied.append(
            {
                "original_extraction": expected,
                "replacement": replacement,
                "evidence_source": evidence_source,
                "evidence_source_sha256": evidence_hash,
                "evidence_method": str(item.get("evidence_method", "alternate_source_text_review")),
                "evidence_page": item.get("evidence_page"),
                "evidence_pages": item.get("evidence_pages"),
                "evidence_url": item.get("evidence_url"),
                "evidence_strength": item.get("evidence_strength"),
                "correction_class": item.get("correction_class", "text_correction"),
                "note": str(item.get("note", "")),
            }
        )
    return normalize_space(cleaned), warnings, applied


def detect_kind(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "pdf"
    if suffix in {".txt", ".md", ".markdown"}:
        return "text"
    if suffix not in {".doc", ".docx"}:
        raise ExtractionError(f"unsupported file type: {suffix or '<none>'}")
    with path.open("rb") as handle:
        signature = handle.read(8)
    if signature.startswith(ZIP_SIGNATURES):
        return "docx"
    if signature.startswith(OLE_SIGNATURE):
        return "doc"
    raise ExtractionError("Word file signature is neither OOXML nor legacy OLE")


def _iter_docx_body(path: Path) -> list[Block]:
    try:
        from docx import Document
        from docx.oxml.table import CT_Tbl
        from docx.oxml.text.paragraph import CT_P
        from docx.table import Table
        from docx.text.paragraph import Paragraph
    except ImportError as exc:
        raise ExtractionError("python-docx is required: python -m pip install python-docx") from exc

    try:
        document = Document(path)
    except Exception as exc:  # python-docx exposes several package exceptions
        raise ExtractionError(f"DOCX parsing failed: {exc}") from exc

    blocks: list[Block] = []
    locator = 0
    for child in document.element.body.iterchildren():
        if isinstance(child, CT_P):
            text = normalize_space(Paragraph(child, document).text)
            if text:
                blocks.append(Block(text=text, kind="paragraph", locator=locator))
                locator += 1
        elif isinstance(child, CT_Tbl):
            table = Table(child, document)
            for row in table.rows:
                text = normalize_space(" | ".join(cell.text for cell in row.cells))
                if text:
                    blocks.append(Block(text=text, kind="table_row", locator=locator))
                    locator += 1
    return blocks


def _iter_raw_ooxml(path: Path) -> list[Block]:
    """Recover text from nonstandard macro-enabled OOXML packages.

    This is a structural fallback for files that python-docx rejects because
    their main content type is macroEnabled. It never executes macros.
    """
    try:
        with zipfile.ZipFile(path) as archive:
            xml_bytes = archive.read("word/document.xml")
    except (zipfile.BadZipFile, KeyError, OSError) as exc:
        raise ExtractionError(f"raw OOXML recovery failed: {exc}") from exc
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        raise ExtractionError(f"word/document.xml is invalid: {exc}") from exc

    namespace = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    body = root.find(f"{namespace}body")
    if body is None:
        raise ExtractionError("word/document.xml has no document body")
    blocks: list[Block] = []
    locator = 0

    def element_text(element: ET.Element) -> str:
        pieces: list[str] = []
        for node in element.iter():
            if node.tag == f"{namespace}t" and node.text:
                pieces.append(node.text)
            elif node.tag in {f"{namespace}tab", f"{namespace}br", f"{namespace}cr"}:
                pieces.append(" ")
        return normalize_space("".join(pieces))

    for child in body:
        if child.tag == f"{namespace}p":
            text = element_text(child)
            if text:
                numbered = child.find(f".//{namespace}numPr") is not None
                kind = "raw_ooxml_numbered" if numbered else "raw_ooxml_paragraph"
                blocks.append(Block(text, kind=kind, locator=locator))
                locator += 1
        elif child.tag == f"{namespace}tbl":
            for row in child.findall(f"{namespace}tr"):
                cells = [element_text(cell) for cell in row.findall(f"{namespace}tc")]
                text = normalize_space(" | ".join(value for value in cells if value))
                if text:
                    blocks.append(Block(text, kind="raw_ooxml_table_row", locator=locator))
                    locator += 1
    if not blocks:
        raise ExtractionError("raw OOXML recovery produced no text blocks")
    return blocks


def _word_com_text(path: Path) -> str:
    powershell = shutil.which("powershell.exe") or shutil.which("powershell")
    if not powershell:
        raise ExtractionError("PowerShell is unavailable for the Microsoft Word fallback")

    script = r"""
$InputPath = $env:KAOYAN_WORD_INPUT
$OutputPath = $env:KAOYAN_WORD_OUTPUT
$word = $null
$document = $null
try {
  $word = New-Object -ComObject Word.Application
  $word.Visible = $false
  $word.DisplayAlerts = 0
  $document = $word.Documents.Open($InputPath, $false, $true)
  [System.IO.File]::WriteAllText(
    $OutputPath,
    $document.Content.Text,
    [System.Text.UTF8Encoding]::new($false)
  )
} finally {
  if ($null -ne $document) { $document.Close($false) }
  if ($null -ne $word) { $word.Quit() }
}
"""
    with tempfile.TemporaryDirectory(prefix="kaoyan-word-") as temp_dir:
        temp_root = Path(temp_dir)
        output = temp_root / "word-content.txt"
        word_input = path
        if path.suffix.lower() != ".doc" and detect_kind(path) == "doc":
            # Word refuses legacy OLE content carrying a .docx suffix.  A
            # read-only temp copy with the signature-correct suffix preserves
            # the original file and lets the same safe COM path open it.
            word_input = temp_root / "legacy-input.doc"
            shutil.copyfile(path, word_input)
        process_environment = os.environ.copy()
        process_environment["KAOYAN_WORD_INPUT"] = str(word_input)
        process_environment["KAOYAN_WORD_OUTPUT"] = str(output)
        completed = subprocess.run(
            [powershell, "-NoProfile", "-NonInteractive", "-Command", script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=120,
            env=process_environment,
        )
        if completed.returncode != 0 or not output.exists():
            detail = (completed.stderr or completed.stdout).strip()
            raise ExtractionError(f"Microsoft Word read-only extraction failed: {detail or 'unknown error'}")
        return output.read_text(encoding="utf-8")


def _libreoffice_text(path: Path) -> str:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        raise ExtractionError("LibreOffice is unavailable")
    with tempfile.TemporaryDirectory(prefix="kaoyan-lo-") as temp_dir:
        completed = subprocess.run(
            [soffice, "--headless", "--convert-to", "txt:Text", "--outdir", temp_dir, str(path)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=120,
        )
        outputs = list(Path(temp_dir).glob("*.txt"))
        if completed.returncode != 0 or not outputs:
            detail = (completed.stderr or completed.stdout).strip()
            raise ExtractionError(f"LibreOffice conversion failed: {detail or 'no text output'}")
        return outputs[0].read_text(encoding="utf-8", errors="replace")


def _antiword_text(path: Path) -> str:
    antiword = shutil.which("antiword")
    if not antiword:
        raise ExtractionError("antiword is unavailable")
    completed = subprocess.run(
        [antiword, str(path)], capture_output=True, shell=False, timeout=120
    )
    if completed.returncode != 0:
        raise ExtractionError(
            f"antiword failed: {completed.stderr.decode(errors='replace').strip()}"
        )
    for encoding in ("utf-8", "gb18030", "cp1252"):
        try:
            return completed.stdout.decode(encoding)
        except UnicodeDecodeError:
            continue
    return completed.stdout.decode("utf-8", errors="replace")


def _iter_legacy_word(path: Path) -> list[Block]:
    errors: list[str] = []
    extractors = []
    if os.name == "nt":
        extractors.append(("Microsoft Word", _word_com_text))
    extractors.extend((("LibreOffice", _libreoffice_text), ("antiword", _antiword_text)))
    text: str | None = None
    method = ""
    for method, extractor in extractors:
        try:
            text = extractor(path)
            break
        except (ExtractionError, subprocess.SubprocessError, OSError) as exc:
            errors.append(f"{method}: {exc}")
    if text is None:
        raise ExtractionError(
            "legacy Word extraction failed; install Microsoft Word, LibreOffice, or antiword. "
            + " | ".join(errors)
        )

    text = text.replace("\x07", " | ").replace("\r\n", "\n").replace("\r", "\n")
    blocks = []
    for index, line in enumerate(text.splitlines()):
        clean = normalize_space(line)
        if clean:
            blocks.append(Block(clean, kind=f"legacy_word:{method}", locator=index))
    return blocks


def _is_page_noise(line: str) -> bool:
    if not line:
        return True
    if re.fullmatch(r"[.·•\-—–\s]*\d+[.·•\-—–\s]*", line):
        return True
    if re.search(r"(?:英语(?:一)?试题|共\s*\d+\s*页).{0,20}$", line):
        return True
    if "全国硕士研究生招生考试" in line and len(re.findall(r"[A-Za-z]", line)) < 5:
        return True
    return False


def _iter_pdf(path: Path) -> list[Block]:
    try:
        import pdfplumber
    except ImportError as exc:
        raise ExtractionError("pdfplumber is required: python -m pip install pdfplumber") from exc

    blocks: list[Block] = []
    try:
        with pdfplumber.open(path) as pdf:
            if getattr(pdf, "is_encrypted", False):
                raise ExtractionError("PDF is encrypted")
            extracted_chars = 0
            locator = 0
            for page_number, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text(x_tolerance=2, y_tolerance=3) or ""
                extracted_chars += len(page_text)
                buffer = ""

                def flush() -> None:
                    nonlocal buffer, locator
                    clean = normalize_space(buffer)
                    if clean:
                        blocks.append(Block(clean, page=page_number, kind="pdf_text", locator=locator))
                        locator += 1
                    buffer = ""

                for raw_line in page_text.splitlines():
                    line = normalize_space(raw_line)
                    if _is_page_noise(line):
                        continue
                    structural = STRUCTURAL_RE.match(_roman_normalized(line))
                    explicit_item = QUESTION_NUMBER_RE.match(line) or OPTION_RE.match(line)
                    if structural or explicit_item:
                        flush()
                        blocks.append(Block(line, page=page_number, kind="pdf_text", locator=locator))
                        locator += 1
                        continue
                    if buffer:
                        if buffer.endswith("-") and line[:1].islower():
                            buffer += line
                        else:
                            buffer += " " + line
                    else:
                        buffer = line
                    if END_PUNCTUATION_RE.search(buffer):
                        flush()
                flush()
            if extracted_chars < max(200, len(pdf.pages) * 20):
                raise ExtractionError(
                    "PDF has almost no extractable text and may be scanned; OCR is optional but must be verified"
                )
    except ExtractionError:
        raise
    except Exception as exc:
        raise ExtractionError(f"PDF parsing failed: {type(exc).__name__}: {exc}") from exc
    return blocks


def _iter_plain_text(path: Path) -> list[Block]:
    text = path.read_text(encoding="utf-8-sig", errors="strict")
    return [
        Block(clean, kind="plain_text", locator=index)
        for index, line in enumerate(text.splitlines())
        if (clean := normalize_space(line))
    ]


def extract_blocks(path: Path) -> tuple[list[Block], str]:
    kind = detect_kind(path)
    if kind == "docx":
        try:
            return _iter_docx_body(path), "python-docx"
        except ExtractionError as primary_error:
            try:
                return _iter_raw_ooxml(path), "raw-ooxml"
            except ExtractionError as fallback_error:
                raise ExtractionError(f"{primary_error}; {fallback_error}") from fallback_error
    if kind == "doc":
        return _iter_legacy_word(path), "legacy-word-converter"
    if kind == "pdf":
        return _iter_pdf(path), "pdfplumber"
    return _iter_plain_text(path), "plain-text"


def _roman_normalized(text: str) -> str:
    return unicodedata.normalize("NFKC", text).replace("Ⅰ", "I").replace("Ⅱ", "II").replace("Ⅲ", "III")


def _heading_number(text: str, existing: list[tuple[int, int]], expected_articles: int) -> int | None:
    clean = _roman_normalized(text).strip()
    match = TEXT_HEADING_RE.match(clean)
    if match:
        return int(match.group(1))
    # A recurring OCR error turns the digit 2 into !, I, l, or |. Only infer
    # a number for a short standalone heading and choose the next missing slot.
    if re.fullmatch(r"(?:Text|Passage)\s*[!Il|]\s*[:：.]?", clean, re.IGNORECASE):
        used = {number for number, _index in existing}
        return next((number for number in range(1, expected_articles + 1) if number not in used), None)
    return None


def _is_part_b(text: str) -> bool:
    clean = _roman_normalized(text).strip()
    return bool(re.match(r"^Part\s*B(?:\s+Directions:?)?$", clean, re.IGNORECASE))


def _is_section_three(text: str) -> bool:
    clean = _roman_normalized(text).strip()
    return bool(re.match(r"^Section\s*III\b", clean, re.IGNORECASE))


def _question_boundary(region: list[Block]) -> int:
    candidates: list[int] = []
    for index, block in enumerate(region):
        if QUESTION_NUMBER_RE.match(block.text) or OPTION_RE.match(block.text):
            candidates.append(index)
            break
        if index >= 2 and "numbered" in block.kind:
            candidates.append(index)
            break

    for index, block in enumerate(region):
        if index < 2 or len(block.text) > 220:
            continue
        option_cluster = region[index + 1 : index + 5]
        has_question_signal = bool(QUESTION_HINT_RE.search(block.text)) or block.text.rstrip().endswith("?")
        if (
            has_question_signal
            and len(option_cluster) == 4
            and all(len(item.text) <= 160 for item in option_cluster)
        ):
            candidates.append(index)
            break

    # Some Word/PDF sources lose Q21-Q40 and A-D markers while preserving the
    # question stem and its four options as five short paragraphs.  Detect the
    # earliest terminal stem-plus-options cluster instead of returning a later
    # question that happens to retain an overt "Paragraph" or "Which" signal.
    for index in range(2, max(2, len(region) - 3)):
        stem = region[index].text.strip()
        options = region[index + 1 : index + 5]
        if len(options) < 4 or any(len(item.text) > 160 for item in options):
            continue
        stem_like = (
            len(stem) <= 240
            and (
                bool(QUESTION_HINT_RE.search(stem))
                or stem.endswith("?")
                or not END_PUNCTUATION_RE.search(stem)
            )
        )
        if stem_like:
            candidates.append(index)
            break

    return min(candidates, default=len(region))


def extract_reading_articles(
    blocks: list[Block], expected_articles: int = 4
) -> tuple[dict[int, list[Block]], list[str]]:
    warnings: list[str] = []
    reading_index = next(
        (
            index
            for index, block in enumerate(blocks)
            if re.search(r"Section\s*II\s+Reading\s+Comprehension", _roman_normalized(block.text), re.IGNORECASE)
        ),
        None,
    )
    search_start = reading_index + 1 if reading_index is not None else 0
    headings: list[tuple[int, int]] = []
    for index in range(search_start, len(blocks)):
        if _is_section_three(blocks[index].text):
            break
        number = _heading_number(blocks[index].text, headings, expected_articles)
        if number is not None:
            if 1 <= number <= expected_articles and not any(existing == number for existing, _ in headings):
                headings.append((number, index))
        if len(headings) == expected_articles:
            break
    if not headings:
        raise ExtractionError("could not find Reading Part A Text 1-4 headings")

    articles: dict[int, list[Block]] = {}
    for position, (number, heading_index) in enumerate(headings):
        next_heading = headings[position + 1][1] if position + 1 < len(headings) else len(blocks)
        if position + 1 == len(headings):
            for index in range(heading_index + 1, len(blocks)):
                if _is_part_b(blocks[index].text) or _is_section_three(blocks[index].text):
                    next_heading = index
                    break
        region = blocks[heading_index + 1 : next_heading]
        boundary = _question_boundary(region)
        passage = []
        for block in region[:boundary]:
            text = block.text
            if STRUCTURAL_RE.match(_roman_normalized(text)):
                continue
            if QUESTION_NUMBER_RE.match(text) or OPTION_RE.match(text):
                continue
            if "ANSWER SHEET" in text.upper() or "答案" in text or "解析" in text:
                continue
            if len(words(text)) < 4:
                previous = passage[-1] if passage else None
                cross_page_continuation = (
                    previous is not None
                    and previous.page is not None
                    and block.page is not None
                    and block.page > previous.page
                    and not END_PUNCTUATION_RE.search(previous.text)
                    and bool(re.search(r"[A-Za-z]", text))
                )
                if cross_page_continuation:
                    passage[-1] = Block(
                        normalize_space(previous.text + " " + text),
                        page=previous.page,
                        kind=f"{previous.kind}+cross_page_continuation",
                        locator=previous.locator,
                    )
                    warnings.append(
                        f"Text {number}: retained short cross-page continuation on page {block.page}"
                    )
                elif (
                    len(words(text)) >= 2
                    and bool(re.search(r"[A-Za-z]", text))
                    and bool(END_PUNCTUATION_RE.search(text))
                ):
                    passage.append(block)
                    warnings.append(
                        f"Text {number}: retained short punctuated passage block"
                    )
                continue
            passage.append(block)
        if not passage:
            warnings.append(f"Text {number} has no passage blocks")
        articles[number] = passage

    missing = sorted(set(range(1, expected_articles + 1)) - set(articles))
    if missing:
        warnings.append(f"missing article headings: {missing}")
    return articles, warnings


def split_sentences(text: str) -> list[str]:
    """Split a source paragraph while protecting common abbreviations."""
    protected = normalize_space(text)
    sentinel = "<DOT>"
    for abbreviation in ABBREVIATIONS:
        protected = re.sub(
            rf"(?<![A-Za-z]){re.escape(abbreviation)}",
            abbreviation.replace(".", sentinel),
            protected,
            flags=re.IGNORECASE,
        )
    protected = re.sub(
        r"\b([A-Z])\.(?=\s*[A-Z]\.)",
        lambda match: match.group(1) + sentinel,
        protected,
    )
    pieces = re.split(r"(?<=[.!?])(?:[\"”’')\]]*)\s*(?=[\"“‘'(]?[A-Z0-9])", protected)
    sentences = [normalize_space(piece.replace(sentinel, ".")) for piece in pieces]
    return [sentence for sentence in sentences if sentence]


def _is_candidate(sentence: str) -> bool:
    if len(words(sentence)) < 8:
        return False
    if QUESTION_NUMBER_RE.match(sentence) or OPTION_RE.match(sentence):
        return False
    upper = sentence.upper()
    if any(token in upper for token in ("ANSWER SHEET", "DIRECTIONS:", "READ THE FOLLOWING FOUR TEXTS")):
        return False
    if "(CID:" in upper or "�" in sentence:
        return False
    if re.search(r"[\u4e00-\u9fff]", sentence):
        # Typical PDF OCR confusion such as an em dash becoming Chinese "一".
        # Do not silently rewrite it; omit the sentence until a source is checked.
        return False
    letters = len(re.findall(r"[A-Za-z]", sentence))
    if letters < 20 or letters / max(1, len(sentence)) < 0.5:
        return False
    return True


def _relative_source(path: Path, source_root: Path | None) -> str:
    if source_root is not None:
        try:
            return str(path.resolve().relative_to(source_root.resolve()))
        except ValueError:
            pass
    return path.name


def extract_source(
    path: Path,
    year: int,
    source_root: Path | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    path = path.resolve()
    if not path.is_file():
        raise ExtractionError(f"source file does not exist: {path}")
    blocks, method = extract_blocks(path)
    ocr_tokens = ("ocr", "tesseract", "paddle", "easyocr", "rapidocr", "image_text", "scanned")
    extraction_signature = f"{path.name} {method}".lower()
    if any(token in extraction_signature for token in ocr_tokens):
        extraction_origin = "ocr"
    elif method == "pdfplumber":
        extraction_origin = "embedded_text"
    elif method in {"python-docx", "raw-ooxml", "legacy-word-converter"}:
        extraction_origin = "document_text"
    else:
        extraction_origin = "plain_text"
    expected_articles = 5 if year == 2001 else 4
    articles, warnings = extract_reading_articles(blocks, expected_articles)
    relative_source = _relative_source(path, source_root)
    file_hash = sha256_file(path)
    records: list[dict[str, Any]] = []

    for article_number in sorted(articles):
        completeness = passage_completeness_metadata(
            year, article_number, source_root
        )
        sentence_number = 0
        seen: set[str] = set()
        for paragraph_number, block in enumerate(articles[article_number], 1):
            cleaned_block, block_warnings, block_corrections = clean_reading_text(
                block.text, year, article_number, source_root
            )
            for sentence in split_sentences(cleaned_block):
                if not _is_candidate(sentence):
                    continue
                key = normalized_key(sentence)
                if not key or key in seen:
                    continue
                seen.add(key)
                sentence_number += 1
                normalized_hash = hashlib.sha256(key.encode("utf-8")).hexdigest()
                labels = classify(sentence)
                record: dict[str, Any] = {
                    "schema_version": 1,
                    "id": f"{year}-reading-text{article_number}-{normalized_hash[:12]}",
                    "year": year,
                    "exam": "english_one",
                    "section": "Reading Part A",
                    "article": f"Text {article_number}",
                    "paragraph": paragraph_number,
                    "sentence_number": sentence_number,
                    "original": sentence,
                    "normalized_sha256": normalized_hash,
                    "source_file": relative_source,
                    "source_file_sha256": file_hash,
                    "source_page": block.page,
                    "source_locator": {
                        "kind": block.kind,
                        "page": block.page,
                        "block": block.locator,
                        "paragraph": paragraph_number,
                    },
                    "source_status": "user_provided_question_file",
                    "provenance_status": "source_unverified",
                    "text_status": "auto_extracted",
                    "extraction_method": method,
                    "extraction_origin": extraction_origin,
                    "paragraph_confidence": "estimated" if method == "pdfplumber" else "high",
                    "needs_manual_review": True,
                    "corroboration": None,
                    "block_extraction_warnings": block_warnings,
                    "reviewed_text_corrections": [
                        item
                        for item in block_corrections
                        if item["replacement"] in sentence
                    ],
                    **completeness,
                }
                record.update(labels)
                records.append(record)

    info = {
        "path": str(path),
        "relative_path": relative_source,
        "year": year,
        "detected_kind": detect_kind(path),
        "extraction_method": method,
        "source_file_sha256": file_hash,
        "block_count": len(blocks),
        "article_count": sum(bool(articles.get(number)) for number in range(1, expected_articles + 1)),
        "sentence_count": len(records),
        "warnings": warnings,
        "normalization_warning_count": sum(
            len(record.get("block_extraction_warnings", [])) for record in records
        ),
    }
    return records, info


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    with temp.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
    os.replace(temp, path)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="one PDF, DOC, DOCX, TXT, or Markdown exam file")
    parser.add_argument("--year", type=int, required=True, help="exam year; never inferred silently")
    parser.add_argument("--source-root", type=Path, help="root used to store a relative source path")
    parser.add_argument("--output", type=Path, help="write JSONL here; otherwise print a JSON summary")
    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    try:
        records, info = extract_source(args.source, args.year, args.source_root)
    except ExtractionError as exc:
        raise SystemExit(f"extraction error: {exc}") from exc
    if args.output:
        write_jsonl(args.output, records)
        print(json.dumps(info, ensure_ascii=False, indent=2))
    else:
        preview = {"summary": info, "records_preview": records[:3]}
        print(json.dumps(preview, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
