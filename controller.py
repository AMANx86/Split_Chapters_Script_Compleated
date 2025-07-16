# controller.py
# Runs the full pipeline: split EPUB, split TXT, rename/merge, validate

import subprocess
import os

# === CONFIG ===
SCRIPT_SEQUENCE = [
    ('split_epub.py', '📖 Splitting EPUB...'),
    ('split_txt.py', '📄 Splitting TXT...'),
    ('rename_and_merge.py', '🧩 Renaming & Merging...'),
    ('final_validator.py', '🔍 Final Validation...')
]

# === EXECUTION ===
def run_script(script_name, label):
    print(f"\n{label}")
    if not os.path.exists(script_name):
        print(f"❌ Script not found: {script_name}")
        return False
    result = subprocess.run(['python', script_name])
    return result.returncode == 0

def main():
    print("🚀 Starting Audiobook Chapter Processor Pipeline\n")

    for script, label in SCRIPT_SEQUENCE:
        success = run_script(script, label)
        if not success:
            print(f"❌ Failed at: {script}. Halting pipeline.")
            return

    print("\n✅ All steps completed successfully. Check 'chapters_txt/' for final output.")

if __name__ == '__main__':
    main()
