# split_epub.py
# Extracts and splits EPUB content into chapters_txt(epub)/ using real chapter detection

import os
import re
from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup

# === CONFIG ===
EPUB_FILE = 'mybook.epub'  # You can rename this dynamically if needed
OUTPUT_FOLDER = 'chapters_txt(epub)'
MIN_CONTENT_CHARS = 100
WRITE_HEADERS = True
CLEAN_EXISTING_HEADERS = True

# === REGEX ===
IN_TEXT_HEADER_RE = re.compile(r'(?i)^chapter\s+\d+(\s*[-–:]\s*.+)?$')

# === UTILS ===
def clean_text(text):
    return '\n'.join([line.strip() for line in text.splitlines()])

def detect_and_replace_header(text, true_title):
    lines = text.splitlines()
    non_empty_lines = [line for line in lines if line.strip()]

    for i in range(min(3, len(non_empty_lines))):
        if IN_TEXT_HEADER_RE.match(non_empty_lines[i].strip()):
            idx = lines.index(non_empty_lines[i])
            lines[idx] = true_title
            return '\n'.join(lines).strip()

    # No header found
    return f"{true_title}\n\n{text.strip()}" if WRITE_HEADERS else text.strip()

def extract_clean_chapters(epub_file):
    if not os.path.exists(epub_file):
        print(f"❌ EPUB file not found: {epub_file}")
        return

    print(f"📖 Extracting from: {epub_file}")
    book = epub.read_epub(epub_file)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    chapter_num = 1
    saved_count = 0

    for item in book.get_items_of_type(ITEM_DOCUMENT):
        soup = BeautifulSoup(item.get_body_content(), 'html.parser')
        raw_text = soup.get_text(separator='\n', strip=True)
        text = clean_text(raw_text)

        if len(text) < MIN_CONTENT_CHARS:
            continue  # skip short garbage sections

        # Check if it looks like a chapter
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        first_few = lines[:5]
        found_chapter_line = any(IN_TEXT_HEADER_RE.match(line) for line in first_few)

        if not found_chapter_line and not WRITE_HEADERS:
            continue  # no header and not writing new headers? skip

        chapter_title = f"Chapter {chapter_num:04d}"

        # Process header
        if CLEAN_EXISTING_HEADERS:
            text = detect_and_replace_header(text, chapter_title if WRITE_HEADERS else "")
        elif WRITE_HEADERS:
            text = f"{chapter_title}\n\n{text.strip()}"

        # Write chapter to file
        out_path = os.path.join(OUTPUT_FOLDER, f'chapter_{chapter_num:04d}.txt')
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(text.strip() + '\n')

        print(f"📄 Saved: chapter_{chapter_num:04d}.txt")
        chapter_num += 1
        saved_count += 1

    print(f"\n✅ Done. Total chapters saved: {saved_count}")

if __name__ == '__main__':
    extract_clean_chapters(EPUB_FILE)
