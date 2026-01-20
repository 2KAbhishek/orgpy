#!/usr/bin/env python3
import argparse
import json
import os
import shutil
from collections import defaultdict
from pathlib import Path

DEFAULT_SEPARATOR_LENGTH = 40
CONFIRMATION_RESPONSES = {"y", "Y", "yes", "Yes"}
CONFIG_FILE = Path.home() / ".config" / "orgpy.json"
TEMPLATE_CONFIG_FILE = Path(__file__).resolve().parent / "orgpy.json"


def load_template_config() -> dict:
    """Load the template configuration file."""
    try:
        if TEMPLATE_CONFIG_FILE.exists():
            with open(TEMPLATE_CONFIG_FILE, "r") as f:
                return json.load(f)
    except (json.JSONDecodeError, OSError):
        pass
    return {"file_categories": {}}


def load_config() -> dict:
    """Load configuration from config file, create default if not found."""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        else:
            return create_default_config()
    except (json.JSONDecodeError, OSError):
        return {}


def load_config_from_path(config_path: str) -> dict:
    """Load configuration from specific file path."""
    try:
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file, "r") as f:
                return json.load(f)
        else:
            print(f"❌ Config file not found: {config_file}")
    except (json.JSONDecodeError, OSError) as e:
        print(f"⚠️  Error loading config from {config_path}: {e}")
    return {}


def create_default_config() -> dict:
    """Create default config by copying template file."""
    template_config = load_template_config()

    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)

        if TEMPLATE_CONFIG_FILE.exists():
            shutil.copy2(TEMPLATE_CONFIG_FILE, CONFIG_FILE)
        else:
            with open(CONFIG_FILE, "w") as f:
                json.dump(template_config, f, indent=2)
    except OSError:
        pass

    return template_config


def merge_categories(config: dict) -> dict:
    """Return categories from config, or load from template if empty."""
    if "file_categories" in config and config["file_categories"]:
        return config["file_categories"]

    return load_template_config().get("file_categories", {})


def build_extension_map(file_categories: dict) -> dict:
    """Build extension-to-directory mapping from categories."""
    dir_map = {}
    for directory, extensions in file_categories.items():
        for ext in extensions:
            dir_map[ext.lower()] = directory.replace("/", os.sep)
    return dir_map


def get_config_and_mapping(custom_config_path: str = None) -> tuple[dict, dict]:
    """Load config and build extension mapping."""
    if custom_config_path:
        config = load_config_from_path(custom_config_path)
    else:
        config = load_config()

    file_categories = merge_categories(config)
    dir_map = build_extension_map(file_categories)
    return config, dir_map


def categorize_file(file: str, path: str, dir_map: dict) -> tuple[str, bool]:
    """Categorize a single file and return (destination, is_categorized)."""
    if not os.path.isfile(os.path.join(path, file)):
        return "", False

    _, ext = os.path.splitext(file)
    if ext.lower() in dir_map:
        return dir_map[ext.lower()], True
    return "", False


def analyze_files(path: str, dir_map: dict) -> tuple[dict[str, list[str]], list[str]]:
    """Analyze files and group them by destination directory."""
    files_by_dir = defaultdict(list)
    skipped_files = []

    for file in os.listdir(path):
        dest_dir, is_categorized = categorize_file(file, path, dir_map)
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

        os.replace(os.path.join(source_path, file), os.path.join(dest_path, file))
        return True
    except (OSError, PermissionError, FileNotFoundError):
        return False


def process_directory(
    path: str, dest_dir: str, files: list[str], dry_run: bool
) -> tuple[int, list[str]]:
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


def organize(path: str, dir_map: dict, dry_run: bool = False) -> None:
    """Orchestrate the file organization process."""
    files_by_dir, skipped_files = analyze_files(path, dir_map)
    display_header(path, dry_run)

    total_files = 0
    for dest_dir, files in files_by_dir.items():
        if files:
            moved_count, failed_files = process_directory(
                path, dest_dir, files, dry_run
            )
            total_files += moved_count
            skipped_files.extend(failed_files)

    display_summary(total_files, skipped_files, dry_run)


def create_arg_parser() -> argparse.ArgumentParser:
    """Create and return the argument parser."""
    parser = argparse.ArgumentParser(
        prog="orgpy",
        description="Organize your digital mess.",
        epilog="Visit github.com/2KAbhishek/orgpy for more.",
    )

    parser.add_argument(
        "path",
        nargs="?",
        default=os.getcwd(),
        help="The directory path to organize. [Default: current working directory]",
    )

    parser.add_argument(
        "-c",
        "--config",
        metavar="CONFIG_FILE",
        type=str,
        help="Path to custom configuration file.",
    )

    parser.add_argument(
        "--config-path",
        action="store_true",
        help="Show configuration file path and exit.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without actually moving files.",
    )

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

    if not os.path.exists(args.path):
        print(f"Error: Directory '{args.path}' does not exist.")
        exit(1)

    config, dir_map = get_config_and_mapping(args.config)

    if args.dry_run:
        organize(args.path, dir_map, dry_run=True)
    elif (
        input(f"Organize directory '{os.path.basename(args.path)}'? (y/N): ")
        in CONFIRMATION_RESPONSES
    ):
        organize(args.path, dir_map)
    else:
        print("Operation cancelled.")


if __name__ == "__main__":
    main()
