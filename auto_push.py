import argparse
import json
import logging
import shutil
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

# =====================================================
# CONFIGURATION
# =====================================================

SOURCE_DIR = Path(r"D:\pythonDriveallcode")
REPO_DIR = Path(r"D:\DailyPyDrops")
UPLOAD_DIR = REPO_DIR / "python_scripts"
PROGRESS_FILE = REPO_DIR / "progress.json"
LOG_DIR = REPO_DIR / "logs"

BATCH_SIZE = 10

# Local computer timezone is used.
START_DATE = datetime(2026, 10, 15).date()

# Schedule:
# Batch 1: 14 Oct 2026, 11:50 PM
# Batch 2: 15 Oct 2026, 12:10 AM
# Batch 3: 16 Oct 2026, 11:50 AM
# Batch 4: 17 Oct 2026, 12:10 AM
# Batch 5: 18 Oct 2026, 11:50 AM
# Batch 6: 19 Oct 2026, 12:10 AM

# =====================================================
# LOGGING
# =====================================================

LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(
            LOG_DIR / "auto_push.log",
            encoding="utf-8"
        ),
        logging.StreamHandler(sys.stdout),
    ],
)

log = logging.getLogger("DailyPyDrops")


# =====================================================
# GIT HELPER
# =====================================================

def git(*args, check=True):
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )

    if result.stdout.strip():
        log.info(result.stdout.strip())

    if result.returncode != 0 and check:
        raise RuntimeError(
            f"Git command failed: {' '.join(args)}\n"
            f"{result.stderr.strip()}"
        )

    return result


# =====================================================
# FILE DISCOVERY
# =====================================================

def get_source_files():
    if not SOURCE_DIR.is_dir():
        raise FileNotFoundError(
            f"Source folder not found: {SOURCE_DIR}"
        )

    # Top-level .py files only; alphabetical order.
    return sorted(
        [
            p for p in SOURCE_DIR.iterdir()
            if p.is_file() and p.suffix.lower() == ".py"
        ],
        key=lambda p: (p.name.casefold(), p.name),
    )


# =====================================================
# PROGRESS
# =====================================================

def load_progress():
    if not PROGRESS_FILE.exists():
        return {"completed_files": [], "completed_batches": []}

    with PROGRESS_FILE.open("r", encoding="utf-8") as f:
        data = json.load(f)

    data.setdefault("completed_files", [])
    data.setdefault("completed_batches", [])
    return data


def save_progress(progress):
    temp = PROGRESS_FILE.with_suffix(".tmp")

    with temp.open("w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2)

    temp.replace(PROGRESS_FILE)


# =====================================================
# EXACT SCHEDULE
# =====================================================

def scheduled_datetime(batch_number):
    if batch_number == 1:
        day = START_DATE
        hour, minute = 23, 50

    else:
        day = START_DATE + timedelta(days=batch_number - 1)

        if batch_number % 2 == 0:
            # Even batches: 12:10 AM
            hour, minute = 0, 10
        else:
            # Odd batches: 11:50 AM
            hour, minute = 11, 50

    return datetime.combine(
        day,
        datetime.min.time()
    ).replace(hour=hour, minute=minute)


# =====================================================
# BATCH PREVIEW
# =====================================================

def get_next_batch(files, progress):
    completed = set(progress["completed_files"])

    # Exclude files already tracked in GitHub repository.
    tracked_output = git(
        "ls-files", "--", "python_scripts"
    ).stdout.splitlines()

    tracked_names = {
        Path(name).name for name in tracked_output
    }

    remaining = [
        p for p in files
        if p.name not in completed
        and p.name not in tracked_names
    ]

    return remaining[:BATCH_SIZE]
def show_next_batch():
    files = get_source_files()
    progress = load_progress()
    batch = get_next_batch(files, progress)

    if not batch:
        log.info("All source files are already completed.")
        return

    batch_number = len(progress["completed_batches"]) + 1
    scheduled = scheduled_datetime(batch_number)

    log.info("DRY RUN: No files will be pushed.")
    log.info("Total source files: %d", len(files))
    log.info("Next batch number: %d", batch_number)
    log.info("Scheduled time: %s", scheduled.strftime("%d-%m-%Y %I:%M %p"))
    log.info("Files in next batch: %d", len(batch))

    for path in batch:
        log.info("Would upload: %s", path.name)


# =====================================================
# REAL PUSH
# =====================================================

def push_batch():
    if not (REPO_DIR / ".git").is_dir():
        raise RuntimeError("Git repository not found.")

    # Prevent accidental use of the wrong repository.
    remote = git("remote", "get-url", "origin").stdout.strip()

    expected_remote = (
        "https://github.com/"
        "omkarsuryawanshi2022/DailyPyDrops.git"
    )

    if remote.rstrip("/").lower() != expected_remote.lower():
        raise RuntimeError(f"Unexpected Git remote: {remote}")

    files = get_source_files()
    progress = load_progress()
    batch = get_next_batch(files, progress)

    if not batch:
        log.info("No files remaining.")
        return

    # Avoid overwriting uncommitted user changes.
    status = git("status", "--porcelain").stdout.strip()

    if status:
        raise RuntimeError(
            "Repository has uncommitted changes. "
            "Inspect git status before continuing."
        )

    batch_number = len(progress["completed_batches"]) + 1
    scheduled = scheduled_datetime(batch_number)

    log.info("Starting batch %d", batch_number)
    log.info("Scheduled slot: %s", scheduled.isoformat())
    log.info("Selected files: %d", len(batch))

        # Copy selected files only.
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    for source in batch:
        destination = UPLOAD_DIR / source.name

        if destination.exists():
            if destination.is_file():
                log.info("File already exists; skipping copy: %s", source.name)
            else:
                raise RuntimeError(
                    f"Destination is not a file: {destination}"
                )
        else:
            shutil.copy2(source, destination)
            log.info("Copied: %s", source.name)

    # Stage only the selected batch files.
    relative_paths = [
        (Path("python_scripts") / p.name).as_posix()
        for p in batch
    ]

    git("add", "--", *relative_paths)

    # Verify staged files against this batch.
    staged = {
        line.replace("\\", "/")
        for line in git(
            "diff", "--cached", "--name-only"
        ).stdout.splitlines()
    }

    expected_staged = set(relative_paths)

    if not expected_staged.issubset(staged):
        raise RuntimeError(
            "Some selected files are not staged correctly. "
            "Inspect git status before continuing."
        )

    git(
        "commit",
        "-m",
        f"Batch {batch_number}: Add {len(batch)} Python scripts",
    )

    # Push to GitHub. Progress is saved only after success.
    git("push", "-u", "origin", "main")

    progress["completed_files"].extend(p.name for p in batch)
    progress["completed_batches"].append({
        "batch": batch_number,
        "scheduled_time": scheduled.isoformat(),
        "uploaded_files": [p.name for p in batch],
        "success_time": datetime.now().isoformat(timespec="seconds"),
    })

    save_progress(progress)

    log.info("Batch %d pushed successfully.", batch_number)
    log.info(
        "Completed %d of %d files.",
        len(progress["completed_files"]),
        len(files),
    )


# =====================================================
# ENTRY POINT
# =====================================================

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview next batch without pushing.",
    )
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push the next batch immediately.",
    )

    args = parser.parse_args()

    if args.dry_run == args.push:
        parser.error("Choose exactly one: --dry-run or --push")

    if args.dry_run:
        show_next_batch()
    else:
        push_batch()


if __name__ == "__main__":
    try:
        main()
    except Exception:
        log.exception("Automation failed.")
        sys.exit(1)