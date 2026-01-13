import os
import zipfile
from pathlib import Path
import fnmatch

# ===============================
# CONFIG
# ===============================
PROJECT_ROOT = Path(__file__).resolve().parent
GITIGNORE_FILE = PROJECT_ROOT / ".gitignore"
OUTPUT_ZIP = PROJECT_ROOT / "datsys_snapshot.zip"

# ===============================
# GITIGNORE PARSER (simple + safe)
# ===============================
def load_gitignore(path):
    patterns = []
    if not path.exists():
        return patterns

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            patterns.append(line)
    return patterns


def is_ignored(rel_path, patterns):
    rel_path = rel_path.as_posix()

    for pat in patterns:
        # directory ignore (e.g. __pycache__/)
        if pat.endswith("/"):
            if rel_path.startswith(pat.rstrip("/")):
                return True

        # wildcard or file match
        if fnmatch.fnmatch(rel_path, pat):
            return True

        # match basename
        if fnmatch.fnmatch(Path(rel_path).name, pat):
            return True

    return False


# ===============================
# ZIP BUILDER
# ===============================
def make_snapshot_zip():
    patterns = load_gitignore(GITIGNORE_FILE)

    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(PROJECT_ROOT):
            root_path = Path(root)
            rel_root = root_path.relative_to(PROJECT_ROOT)

            # prune ignored directories early
            dirs[:] = [
                d for d in dirs
                if not is_ignored((rel_root / d), patterns)
            ]

            for file in files:
                rel_file = rel_root / file

                if is_ignored(rel_file, patterns):
                    continue

                z.write(root_path / file, rel_file)

    print(f"Snapshot created: {OUTPUT_ZIP}")


# ===============================
# ENTRY
# ===============================
if __name__ == "__main__":
    make_snapshot_zip()
