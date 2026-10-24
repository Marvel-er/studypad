# Matcher usage

This example shows how to run the matcher script to match OCR/text results against the prepared wordlists in this repo.

Requirements:
- Python 3.8+
- Install dependencies: pip install pandas nltk pillow pytesseract
- System: install Tesseract OCR (or remove images usage)

Example commands:
- Using a text file (OCR done elsewhere):
  python examples/matcher.py --wordlist cet6.csv --textfile sample.txt --out cet6_result.json

- Using images folder (will run pytesseract on images):
  python examples/matcher.py --wordlist cet6.csv --images_folder ./images --out cet6_result.json

Output: JSON with keys:
- by_level: mapping level -> list of matched words with count and links
- unmatched: list of words not found in the wordlist (each with youdao link)

