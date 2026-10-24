"""
OCR 通道：图片 → 文本行（统一 Line 结构，供 layout.build_blocks 复用）。

引擎用 RapidOCR（onnxruntime 后端，Apache-2.0）：
  · 不依赖 paddlepaddle，Windows + Python 3.13 可装
  · 中英混排模型，适合「英文材料里夹中文注释」的真实场景
  · 懒加载 + 失败降级：引擎不可用时明确报错，不静默返回空结果

如需换成 PaddleOCR / 云 OCR，只要实现 image_to_lines 即可。
"""
from __future__ import annotations

import os
import sys
from typing import Any

from .layout import Line

_engine: Any = None
_engine_error: str | None = None

# 低于该置信度的识别结果丢弃
MIN_SCORE = 0.45


def _silence() -> None:
    os.environ.setdefault("OMP_NUM_THREADS", "4")
    os.environ.setdefault("ORT_LOG_SEVERITY_LEVEL", "3")


def load() -> tuple[bool, str]:
    """懒加载 OCR 引擎。返回 (是否可用, 说明)。"""
    global _engine, _engine_error
    if _engine is not None:
        return True, "ready"
    if _engine_error is not None:
        return False, _engine_error

    _silence()
    try:
        from rapidocr import RapidOCR  # type: ignore

        # rapidocr 3.x 的构造签名是 (config_path=None, params=None)。
        # params 里的键名跨版本不稳定，因此默认零参数启动 —— 默认配置即可用。
        _engine = RapidOCR()
        return True, "ready"
    except Exception as e:  # noqa: BLE001
        _engine_error = f"{type(e).__name__}: {e}"
        return False, _engine_error


def _normalize(result: Any) -> tuple[list, list, list]:
    """兼容 RapidOCR 2.x（tuple）与 3.x（对象）两种返回结构。"""
    boxes = txts = scores = None

    if hasattr(result, "boxes"):
        boxes, txts, scores = result.boxes, result.txts, result.scores
    elif isinstance(result, (tuple, list)) and result:
        first = result[0]
        if first is None:
            return [], [], []
        if isinstance(first, (list, tuple)) and len(first) and isinstance(first[0], (list, tuple)):
            # [[box, text, score], ...]
            boxes = [it[0] for it in first]
            txts = [it[1] for it in first]
            scores = [it[2] if len(it) > 2 else 1.0 for it in first]

    if boxes is None:
        return [], [], []

    def as_list(x):
        if x is None:
            return []
        return list(x)

    return as_list(boxes), as_list(txts), as_list(scores)


def image_to_lines(image, *, scale: float = 1.0,
                   page_w: float | None = None,
                   page_h: float | None = None) -> list[Line]:
    """
    对一张图做 OCR，返回按阅读顺序的 Line 列表。

    image : PIL.Image 或 numpy 数组
    scale : 渲染倍率。OCR 得到的是像素坐标，除以 scale 换算回页面点数，
            这样文字层 PDF 与扫描件可以共用同一套 layout 逻辑与坐标语义。
    """
    ok, msg = load()
    if not ok:
        raise RuntimeError(f"OCR 引擎不可用：{msg}")

    try:
        import numpy as np
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("OCR 需要 numpy") from e

    if not isinstance(image, np.ndarray):
        image = np.asarray(image.convert("RGB"))

    result = _engine(image)
    boxes, txts, scores = _normalize(result)

    lines: list[Line] = []
    for box, text, score in zip(boxes, txts, scores):
        try:
            s = float(score)
        except (TypeError, ValueError):
            s = 1.0
        if s < MIN_SCORE:
            continue
        t = (str(text) if text is not None else "").strip()
        if not t:
            continue

        arr = np.asarray(box, dtype=float).reshape(-1, 2)
        x0 = float(arr[:, 0].min()) / scale
        x1 = float(arr[:, 0].max()) / scale
        y0 = float(arr[:, 1].min()) / scale
        y1 = float(arr[:, 1].max()) / scale
        h = max(y1 - y0, 1.0)

        lines.append(Line(text=t, x0=x0, y0=y0, x1=x1, y1=y1,
                          size=round(h * 0.72, 1)))

    # 按版面从上到下、从左到右排出阅读顺序
    lines.sort(key=lambda ln: (round(ln.y0 / max(ln.height, 1) * 0.6), ln.x0))
    return lines


def engine_info() -> dict:
    ok, msg = load()
    name = "unknown"
    if ok:
        name = type(_engine).__module__ + "." + type(_engine).__name__
    return {"available": ok, "engine": name, "message": msg,
            "python": f"{sys.version_info.major}.{sys.version_info.minor}"}
