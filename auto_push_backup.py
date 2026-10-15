import json
import shutil
import subprocess
import time
from datetime import datetime, date, timedelta
from pathlib import Path

# =====================================================
# CONFIGURATION
# =====================================================

SOURCE_DIR = Path(r"D:\pythonDriveallcode")
REPO_DIR = Path(r"D:\DailyPyDrops")

UPLOAD_DIR = REPO_DIR / "python_scripts"
PROGRESS_FILE = REPO_DIR / "progress.json"
LOG_DIR = REPO_DIR / "logs"
LOG_FILE = LOG_DIR / "auto_push.log"

BATCH_SIZE = 10

# First scheduled execution
START_DATE = date(2026, 10, 14)

# First run: 14 Oct 2026, 11:50 PM
FIRST_RUN_TIME = (23, 50)

# =====================================================
# LOGGING
# =====================================================

def log(message):
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"

    print(line, flush=True)

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(line + "\n")


# =====================================================
# GIT COMMAND
# =====================================================

def run_git(*args):
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if result.stdout.strip():
        log(result.stdout.strip())

    if result.returncode != 0:
        raise RuntimeError(
            f"Git command failed: git {' '.join(args)}\n"
            f"{result.stderr}"
        )

    return result


# =====================================================
# PROGRESS TRACKING
# =====================================================

def load_progress():
    if not PROGRESS_FILE.exists():
        return {"completed_files": []}

    with PROGRESS_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return data


def save_progress(completed_files):
    temporary_file = PROGRESS_FILE.with_suffix(".tmp")

    data = {
        "completed_files": completed_files,
        "updated_at": datetime.now().isoformat(timespec="seconds")
    }

    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    temporary_file.replace(PROGRESS_FILE)


# =====================================================
# SCHEDULE CALCULATION
# =====================================================

def get_scheduled_time(batch_number):
    """
    Batch 1: 14 Oct 2026, 11:50 PM
    Batch 2: 15 Oct 2026, 12:10 AM
    Batch 3: 16 Oct 2026, 11:50 AM
    Batch 4: 17 Oct 2026, 12:10 AM
    Batch 5: 18 Oct 2026, 11:50 AM
    Batch 6: 19 Oct 2026, 12:10 AM

    The pattern continues automatically.
    """

    if batch_number == 1:
        hour, minute = FIRST_RUN_TIME
        scheduled_date = START_DATE

    else:
        scheduled_date = START_DATE + timedelta(
            days=batch_number - 1
        )

        if batch_number % 2 == 0:
            # Even batches: 12:10 AM
            hour, minute = 0, 10
        else:
            # Odd batches: 11:50 AM
            hour, minute = 11, 50

    return datetime.combine(
        scheduled_date,
        datetime.min.time()
    ).replace(hour=hour, minute=minute)


# =====================================================
# FILE DISCOVERY
# =====================================================

def get_python_files():
    if not SOURCE_DIR.is_dir():
        raise FileNotFoundError(
            f"Source folder does not exist: {SOURCE_DIR}"
        )

    files = sorted(
        (
            path for path in SOURCE_DIR.iterdir()
            if path.is_file() and path.suffix.lower() == ".py"
        ),
        key=lambda path: path.name.casefold()
    )

    return files


# =====================================================
# PUSH NEXT BATCH
# =====================================================

def push_next_batch():
    source_files = get_python_files()
    progress = load_progress()

    completed_files = progress.get("completed_files", [])

    remaining_files = [
        path for path in source_files
        if path.name not in completed_files
    ]

    if not remaining_files:
        log("All Python files have been uploaded.")
        return False

    batch = remaining_files[:BATCH_SIZE]
    batch_number = len(completed_files) // BATCH_SIZE + 1

    log(f"Starting batch {batch_number}")
    log(f"Files in this batch: {len(batch)}")

    # Check remote repository
    run_git("rev-parse", "--is-inside-work-tree")

    # Create upload folder
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    # Copy the selected files without changing originals
    for source_file in batch:
        destination = UPLOAD_DIR / source_file.name

        shutil.copy2(source_file, destination)

        log(f"Copied: {source_file.name}")

    # Create README if it does not exist
    readme = REPO_DIR / "README.md"

    if not readme.exists():
        readme.write_text(
            "# DailyPyDrops\n\n"
            "A collection of Python scripts with scheduled "
            "GitHub uploads and batch-wise code updates.\n",
            encoding="utf-8"
        )

    # Stage only the Python uploads and README.
    run_git("add", "--", "python_scripts", "README.md")

    # Check whether there are staged changes.
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=REPO_DIR
    )

    if result.returncode == 0:
        log("No new Git changes detected.")
    elif result.returncode == 1:
        filenames = ", ".join(path.name for path in batch)

        run_git(
            "commit",
            "-m",
            f"Batch {batch_number}: Add {len(batch)} Python scripts"
        )

        # Push to GitHub.
        run_git("push", "-u", "origin", "main")

        log(f"Successfully pushed batch {batch_number}: {filenames}")

    else:
        raise RuntimeError("Unable to inspect staged Git changes.")

    # Save progress only after the push succeeds.
    updated_files = completed_files + [
        path.name for path in batch
    ]

    save_progress(updated_files)

    log(
        f"Progress: {len(updated_files)}/"
        f"{len(source_files)} files completed."
    )

    return True


# =====================================================
# MAIN SCHEDULER
# =====================================================

def main():
    log("=" * 55)
    log("DailyPyDrops automation started.")

    log(f"Source: {SOURCE_DIR}")
    log(f"Repository: {REPO_DIR}")

    source_files = get_python_files()

    log(f"Python files found: {len(source_files)}")

    if not source_files:
        log("No Python files found. Exiting.")
        return

    if not (REPO_DIR / ".git").is_dir():
        raise RuntimeError(
            f"Git repository not found: {REPO_DIR}"
        )

    while True:
        progress = load_progress()
        completed_files = progress.get("completed_files", [])

        remaining = [
            path for path in source_files
            if path.name not in completed_files
        ]

        if not remaining:
            log("All files completed. Automation stopped.")
            break

        batch_number = len(completed_files) // BATCH_SIZE + 1
        scheduled_time = get_scheduled_time(batch_number)

        now = datetime.now()

        if now < scheduled_time:
            seconds_to_wait = (
                scheduled_time - now
            ).total_seconds()

            log(
                f"Next batch: {batch_number}. "
                f"Scheduled for {scheduled_time:%d-%m-%Y %I:%M %p}."
            )

            try:
                time.sleep(seconds_to_wait)
            except KeyboardInterrupt:
                log("Stopped by user.")
                break

            continue

        # If the computer was asleep or the script was
        # started late, run the overdue batch immediately.
        try:
            successful = push_next_batch()

            if not successful:
                break

        except KeyboardInterrupt:
            log("Stopped by user.")
            break

        except Exception as error:
            log(f"ERROR: {error}")
            log("Will retry this batch in 5 minutes.")

            try:
                time.sleep(300)
            except KeyboardInterrupt:
                log("Stopped by user.")
                break


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        log(f"FATAL ERROR: {error}")
        raise