# rename_and_merge.py
# Compares chapters from EPUB and TXT split folders, renames/matches/merges, then outputs verified chapters

import os
import re
import shutil
import json
from difflib import SequenceMatcher

# === CONFIG ===
EPUB_DIR = 'chapters_txt(epub)'
TXT_DIR = 'chapters_txt(txt)'
OUTPUT_DIR = 'chapters_txt'
MERGE_LOG = 'merge_log.json'
RENAME_LOG = 'rename_log.json'
ERROR_LOG = 'rename_errors.log'

HEADER_PATTERN = re.compile(r'chapter\s*\d+', re.IGNORECASE)

# === UTILS ===
def read_first_nonempty_line(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if stripped:
                return stripped
    return ""

def normalize_header(header):
    return re.sub(r'[^a-z0-9]', '', header.lower())

def fuzzy_match(a, b):
    a = normalize_header(a)
    b = normalize_header(b)
    return SequenceMatcher(None, a, b).ratio()

def safe_filename(index, merged=False):
    return f"chapter_{index:04d}{'_merged' if merged else ''}.txt"

# === MAIN ===
def main():
    if not os.path.exists(EPUB_DIR) or not os.path.exists(TXT_DIR):
        print("❌ Missing one of the required directories.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    epub_files = sorted(os.listdir(EPUB_DIR))
    txt_files = sorted(os.listdir(TXT_DIR))

    rename_map = {}
    merge_events = []
    errors = []
    header_to_file = {}

    print("🔍 Scanning EPUB headers...")
    for fname in epub_files:
        path = os.path.join(EPUB_DIR, fname)
        header = read_first_nonempty_line(path)
        norm = normalize_header(header)
        if not norm:
            errors.append(f"Empty or invalid header in EPUB file: {fname}")
            continue
        header_to_file[norm] = (path, header)

    print("🔁 Matching TXT headers and resolving conflicts...")
    chapter_index = 1
    used_names = set()

    for fname in txt_files:
        path = os.path.join(TXT_DIR, fname)
        txt_header = read_first_nonempty_line(path)
        norm_txt = normalize_header(txt_header)

        if not norm_txt:
            errors.append(f"Empty or invalid header in TXT file: {fname}")
            continue

        if norm_txt in header_to_file:
            epub_path, epub_header = header_to_file[norm_txt]
            match_score = fuzzy_match(txt_header, epub_header)

            if match_score > 1:
                outname = safe_filename(chapter_index)
                outpath = os.path.join(OUTPUT_DIR, outname)

                with open(outpath, 'w', encoding='utf-8') as out:
                    out.write(open(epub_path, 'r', encoding='utf-8').read().strip() + "\n\n")
                    out.write(open(path, 'r', encoding='utf-8').read().strip())

                merge_events.append({
                    'chapter': chapter_index,
                    'epub_file': epub_path,
                    'txt_file': path,
                    'score': match_score,
                    'output': outname
                })
                used_names.add(outname)
                chapter_index += 1

            else:
                # Mismatch
                outname = safe_filename(chapter_index)
                errors.append(f"❌ Header mismatch: {fname} vs EPUB ({match_score*100:.1f}%)")
                chapter_index += 1
        else:
            # No match in EPUB folder
            outname = safe_filename(chapter_index)
            src = os.path.join(TXT_DIR, fname)
            dst = os.path.join(OUTPUT_DIR, outname)
            shutil.copy(src, dst)
            rename_map[fname] = outname
            used_names.add(outname)
            chapter_index += 1

    # === Write Logs ===
    with open(MERGE_LOG, 'w', encoding='utf-8') as f:
        json.dump(merge_events, f, indent=2)
    with open(RENAME_LOG, 'w', encoding='utf-8') as f:
        json.dump(rename_map, f, indent=2)
    if errors:
        with open(ERROR_LOG, 'w', encoding='utf-8') as f:
            f.write('\n'.join(errors))

    print(f"\n✅ Done. Verified chapters saved to: {OUTPUT_DIR}")
    print(f"📒 Merge events: {MERGE_LOG}")
    print(f"✏️ Renames: {RENAME_LOG}")
    if errors:
        print(f"⚠️ Errors logged in: {ERROR_LOG}")

if __name__ == '__main__':
    main()
