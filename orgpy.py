#!/usr/bin/env python3
import argparse
import json
import os
from collections import defaultdict
from pathlib import Path

DEFAULT_SEPARATOR_LENGTH = 40
CONFIRMATION_RESPONSES = {'y', 'Y', 'yes', 'Yes'}
CONFIG_FILE = Path.home() / '.config' / 'orgpy.json'

DEFAULT_FILE_CATEGORIES = {
    'Docs': ['.md', '.txt'],
    'Docs/PDF': ['.pdf'],
    'Docs/Word': ['.doc', '.docx', '.odt', '.rtf'],
    'Docs/Sheets': ['.ods', '.xls', '.xlsm', '.xlsx'],
    'Docs/Presentations': ['.key', '.odp', '.pps', '.ppt', '.pptx'],

    'Images': ['.ai', '.bmp', '.gif', '.ico', '.jpeg', '.jpg', '.png',
               '.ps', '.psd', '.svg', '.tif', '.tiff', '.webp'],

    'Audio': ['.aif', '.cda', '.mid', '.mp3', '.mpa', '.ogg',
              '.wav', '.wma', '.wpl'],

    'Videos': ['.3g2', '.3gp', '.avi', '.flv', '.h264', '.m4v', '.mkv',
               '.mov', '.mp4', '.mpg', '.rm', '.swf', '.vob', '.wmv'],

    'Archives': ['.7z', '.arj', '.bz2', '.gz', '.lz4', '.rar',
                 '.tar', '.xz', '.z', '.zip', '.zstd'],

    'Programs': ['.apk', '.bin', '.deb', '.exe', '.jar', '.msi', '.rpm'],

    'Code': ['.c', '.cpp', '.java', '.py', '.js', '.class', '.h', '.sh',
             '.bat', '.css', '.go', '.rs', '.cs', '.swift', '.r', '.php',
             '.dart', '.kt', '.mat', '.pl', '.rb', '.scala'],

    'Code/Markup': ['.html', '.xml', '.xhtml', '.mhtml'],
    'Code/Database': ['.sql', '.db', '.json', '.csv'],
}


def load_config() -> dict:
    """Load configuration from config file, create default if not found."""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        else:
            create_default_config()
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def load_config_from_path(config_path: str) -> dict:
    """Load configuration from specific file path."""
    try:
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        else:
            print(f"❌ Config file not found: {config_file}")
    except (json.JSONDecodeError, OSError) as e:
        print(f"⚠️  Error loading config from {config_path}: {e}")
    return {}


def create_default_config() -> None:
    """Create a default configuration file."""
    default_config = {
        "file_categories": DEFAULT_FILE_CATEGORIES
    }

    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=2)
    except OSError:
        pass


def merge_categories(config: dict) -> dict:
    """Merge user config with default categories."""
    merged = DEFAULT_FILE_CATEGORIES.copy()

    if 'file_categories' in config:
        for category, extensions in config['file_categories'].items():
            merged[category] = extensions

    return merged


def build_extension_map(file_categories: dict) -> dict:
    """Build extension-to-directory mapping from categories."""
    dir_map = {}
    for directory, extensions in file_categories.items():
        for ext in extensions:
            dir_map[ext.lower()] = directory.replace('/', os.sep)
    return dir_map


config = load_config()
FILE_CATEGORIES = merge_categories(config)
dir_map = build_extension_map(FILE_CATEGORIES)


def categorize_file(file: str, path: str) -> tuple[str, bool]:
    """Categorize a single file and return (destination, is_categorized)."""
    if not os.path.isfile(os.path.join(path, file)):
        return '', False

    _, ext = os.path.splitext(file)
    if ext.lower() in dir_map:
        return dir_map[ext.lower()], True
    return '', False


def analyze_files(path: str) -> tuple[dict[str, list[str]], list[str]]:
    """Analyze files and group them by destination directory."""
    files_by_dir = defaultdict(list)
    skipped_files = []

    for file in os.listdir(path):
        dest_dir, is_categorized = categorize_file(file, path)
        if is_categorized:
            files_by_dir[dest_dir].append(file)
        else:
            skipped_files.append(file)

    return files_by_dir, skipped_files


def display_header(path: str, dry_run: bool) -> None:
    """Display the operation header."""
    if dry_run:
        print(f"\n🗂️ Dry Run - Preview for: {os.path.basename(path)}")
    else:
        print(f"\n🗂️ Organizing: {os.path.basename(path)}")
    print("-" * DEFAULT_SEPARATOR_LENGTH)


def move_file(source_path: str, dest_path: str, file: str) -> bool:
    """Move a single file, return success status."""
    try:
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)

        os.replace(os.path.join(source_path, file),
                  os.path.join(dest_path, file))
        return True
    except Exception:
        return False


def process_directory(path: str, dest_dir: str, files: list[str], dry_run: bool) -> tuple[int, list[str]]:
    """Process files for a single destination directory."""
    print(f"\n📁 {dest_dir}/ ({len(files)} files)")

    moved_count = 0
    failed_files = []

    for file in sorted(files):
        if dry_run:
            print(f"   ➤ {file}")
            moved_count += 1
            continue

        dest_path = os.path.join(path, dest_dir)
        if move_file(path, dest_path, file):
            print(f"   ✅ {file}")
            moved_count += 1
        else:
            print(f"   ❌ {file}")
            failed_files.append(file)

    return moved_count, failed_files


def display_summary(total_files: int, skipped_files: list[str], dry_run: bool) -> None:
    """Display the operation summary."""
    if skipped_files:
        print(f"\n⚠️  Skipped files ({len(skipped_files)}):")
        for file in sorted(skipped_files):
            print(f"   • {file}")

    action = "Would organize" if dry_run else "Organized"
    print(f"\n📊 Summary: {action} {total_files} files")
    if skipped_files:
        print(f"   Skipped: {len(skipped_files)} files")
    print()


def organize(path: str, dry_run: bool = False) -> None:
    """Main organize function - orchestrates the file organization process."""
    files_by_dir, skipped_files = analyze_files(path)
    display_header(path, dry_run)

    total_files = 0
    for dest_dir, files in files_by_dir.items():
        if files:
            moved_count, failed_files = process_directory(path, dest_dir, files, dry_run)
            total_files += moved_count
            skipped_files.extend(failed_files)

    display_summary(total_files, skipped_files, dry_run)

def create_arg_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="orgpy",
        description="Organize your digital mess.",
        epilog="Visit github.com/2KAbhishek/orgpy for more."
    )

    parser.add_argument("-p", "--path", metavar="path", type=str, default=os.getcwd(),
                        help="The directory path to organize.")

    parser.add_argument("-c", "--config", metavar="CONFIG_FILE", type=str,
                        help="Path to custom configuration file.")

    parser.add_argument("--config-path", action="store_true",
                        help="Show configuration file path and exit.")

    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without actually moving files.")

    return parser

def main() -> None:
    """Main entry point for the CLI application."""

    args = create_arg_parser().parse_args()

    if args.config_path:
        print(f"Configuration file: {CONFIG_FILE}")
        if CONFIG_FILE.exists():
            print("✅ Config file exists")
        else:
            print("❌ Config file does not exist, will be created on first run")
        return

    if args.config:
        global config, FILE_CATEGORIES, dir_map
        config = load_config_from_path(args.config)
        FILE_CATEGORIES = merge_categories(config)
        dir_map = build_extension_map(FILE_CATEGORIES)

    if not os.path.exists(args.path):
        print(f"Error: Directory '{args.path}' does not exist.")
        exit(1)

    path = args.path

    if args.dry_run:
        organize(path, dry_run=True)
    elif input(f"Organize directory '{os.path.basename(path)}'? (y/N): ") in CONFIRMATION_RESPONSES:
        organize(path)
    else:
        print("Operation cancelled.")


if __name__ == "__main__":
    main()
