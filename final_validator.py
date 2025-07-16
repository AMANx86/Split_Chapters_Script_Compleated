# final_validator.py
# Verifies final merged chapters for content integrity and missing files

import os
import re
import difflib

# === CONFIG ===
FINAL_DIR = 'chapters_txt'
EXPECTED_RANGE = (1, 9999)  # Adjust depending on max expected chapter number
MIN_MATCH_RATIO = 0.9
MISMATCH_LOG = 'mismatch_report.txt'

# === UTILS ===
def normalize(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def compare_chapter_texts(path_a, path_b):
    with open(path_a, 'r', encoding='utf-8') as f:
        a = f.read()
    with open(path_b, 'r', encoding='utf-8') as f:
        b = f.read()

    a_norm = normalize(a[:1000])
    b_norm = normalize(b[:1000])
    ratio = difflib.SequenceMatcher(None, a_norm, b_norm).ratio()
    return ratio

def find_missing_chapters(folder):
    present = set()
    pattern = re.compile(r'chapter_(\d+)', re.IGNORECASE)

    for fname in os.listdir(folder):
        match = pattern.search(fname)
        if match:
            present.add(int(match.group(1)))

    missing = []
    for i in range(EXPECTED_RANGE[0], EXPECTED_RANGE[1] + 1):
        if i in present:
            continue
        # Stop once there's a long gap
        if len(missing) >= 20:
            break
        missing.append(i)
    return missing

# === MAIN ===
def main():
    if not os.path.exists(FINAL_DIR):
        print("❌ Final verified folder not found.")
        return

    files = sorted(f for f in os.listdir(FINAL_DIR) if f.endswith('.txt'))
    mismatches = []

    print("🔎 Validating chapter consistency...")
    for fname in files:
        match = re.search(r'(\d+)', fname)
        if not match:
            continue
        ch_num = int(match.group(1))

        ref_name = f'chapter_{ch_num:04d}.txt'
        alt_name = f'chapter_{ch_num:04d}_merged.txt'

        ref_path = os.path.join(FINAL_DIR, ref_name)
        alt_path = os.path.join(FINAL_DIR, alt_name)

        if os.path.exists(ref_path) and os.path.exists(alt_path):
            ratio = compare_chapter_texts(ref_path, alt_path)
            if ratio < MIN_MATCH_RATIO:
                mismatches.append((ch_num, ratio))

    missing = find_missing_chapters(FINAL_DIR)

    # === REPORT ===
    with open(MISMATCH_LOG, 'w', encoding='utf-8') as f:
        for ch_num, ratio in mismatches:
            f.write(f"Mismatch in chapter {ch_num:04d}: match ratio = {ratio:.2f}\n")
        if missing:
            f.write("\nMissing chapters detected:\n")
            for m in missing:
                f.write(f"Chapter {m:04d}\n")

    print(f"✅ Verification complete.")
    if mismatches:
        print(f"⚠️ Mismatches logged in: {MISMATCH_LOG}")
    if missing:
        print(f"📭 Missing chapters found. See: {MISMATCH_LOG}")
    if not mismatches and not missing:
        print("🎉 All chapters verified successfully.")

if __name__ == '__main__':
    main()
