"""
matcher.py

简易示例：把 OCR/文本提取到的文章与词表匹配，按考试等级输出结果。
- 读取 CSV 词表（必须包含 'lemma' 和 'levels' 列；可参考仓库 cet6_expanded_sample.csv）
- 支持：输入纯文本文件或图片文件夹（使用 pytesseract OCR）
- 输出：按 level 分组的 JSON 和 CSV 结果（包含 oxford_link 与 youdao_link）

依赖：
  pip install pandas nltk pillow pytesseract
  系统需安装 tesseract 可执行文件（或在 Windows 指定 pytesseract.pytesseract.tesseract_cmd）

用法示例：
  python matcher.py --wordlist cet6.csv --textfile sample.txt --out results.json
  python matcher.py --wordlist cet6.csv --images_folder ./images --out results.json

"""

import argparse
import os
import re
import json
import urllib.parse
from collections import Counter, defaultdict

import pandas as pd
from PIL import Image
import pytesseract
import nltk
from nltk.stem import WordNetLemmatizer

nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)


def ocr_images_in_folder(folder):
    texts = []
    files = sorted([f for f in os.listdir(folder) if f.lower().endswith(('.png','.jpg','.jpeg'))])
    for f in files:
        path = os.path.join(folder, f)
        try:
            txt = pytesseract.image_to_string(Image.open(path), lang='eng')
        except Exception as e:
            print(f"OCR failed for {path}: {e}")
            txt = ''
        texts.append(txt)
    return "\n".join(texts)


def load_wordlist(path):
    df = pd.read_csv(path, dtype=str).fillna('')
    # ensure lemma lowercase
    if 'lemma' in df.columns:
        df['lemma'] = df['lemma'].str.lower()
    else:
        # fallback: use word column
        df['lemma'] = df['word'].str.lower()
    return df


def tokenize_and_lemmatize(text):
    tokens = nltk.word_tokenize(text)
    lemmatizer = WordNetLemmatizer()
    lemmas = []
    originals = []
    for t in tokens:
        if re.match(r"^[A-Za-z'-]+$", t):
            originals.append(t)
            lemmas.append(lemmatizer.lemmatize(t.lower()))
    return originals, lemmas


def match_lemmas(lemmas, df):
    cnt = Counter(lemmas)
    results_by_level = defaultdict(list)
    unmatched = []
    lemma_to_rows = {}
    if 'lemma' in df.columns:
        for idx, row in df.iterrows():
            lemma_to_rows.setdefault(row['lemma'], []).append(row)
    for lemma, c in cnt.items():
        rows = lemma_to_rows.get(lemma)
        if rows:
            # collect levels
            levels = set()
            ox_link = ''
            for r in rows:
                lv = r.get('levels', '')
                if lv:
                    for x in str(lv).split(';'):
                        levels.add(x.strip())
                if not ox_link and 'oxford_link' in r:
                    ox_link = r.get('oxford_link','')
            for lv in levels:
                results_by_level[lv].append({'word': lemma, 'count': c, 'oxford_link': ox_link, 'youdao_link': f"https://dict.youdao.com/search?q={urllib.parse.quote(lemma)}"})
        else:
            unmatched.append({'word': lemma, 'count': c, 'youdao_link': f"https://dict.youdao.com/search?q={urllib.parse.quote(lemma)}"})
    return results_by_level, unmatched


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--wordlist', required=True, help='path to wordlist csv')
    p.add_argument('--textfile', help='path to text file (optional)')
    p.add_argument('--images_folder', help='path to images folder (optional)')
    p.add_argument('--out', default='results.json', help='output json file')
    args = p.parse_args()

    if not args.textfile and not args.images_folder:
        print('Provide --textfile or --images_folder')
        return

    if args.textfile:
        with open(args.textfile, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = ocr_images_in_folder(args.images_folder)

    df = load_wordlist(args.wordlist)
    originals, lemmas = tokenize_and_lemmatize(text)
    results_by_level, unmatched = match_lemmas(lemmas, df)

    out = {'by_level': results_by_level, 'unmatched': unmatched}
    with open(args.out, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f'Wrote results to {args.out}')


if __name__ == '__main__':
    main()
