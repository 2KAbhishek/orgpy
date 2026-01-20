#!/usr/bin/env python3
import argparse
import os
from collections import defaultdict

# Directory mapping, maps file extensions to directories
dir_map = {'.pdf': 'Docs' + os.sep + 'PDF'}

dir_map.update(dict.fromkeys(['.md', '.txt'], 'Docs'))

# Word files
dir_map.update(dict.fromkeys(
    ['.doc', '.docx', '.odt', '.rtf'], 'Docs' + os.sep + 'Word'))

# Sheets
dir_map.update(dict.fromkeys(
    ['.ods', '.xls', '.xlsm', '.xlsx'], 'Docs' + os.sep + 'Sheets'))

# Presentations
dir_map.update(dict.fromkeys(
    ['.key', '.odp', '.pps', '.ppt', '.pptx'], 'Docs' + os.sep + 'Presentations'))

# Images
dir_map.update(dict.fromkeys(['.ai', '.bmp', '.gif', '.ico', '.jpeg',
                              '.jpg', '.png', '.ps', '.psd', '.svg', '.tif', '.tiff', '.webp'], 'Images'))

# Audio
dir_map.update(dict.fromkeys(
    ['.aif', '.cda', '.mid', '.mp3', '.mpa', '.ogg', '.wav', '.wma', '.wpl'], 'Audio'))

# Videos
dir_map.update(dict.fromkeys(['.3g2', '.3gp', '.avi', '.flv', '.h264', '.m4v',
                              '.mkv', '.mov', '.mp4', '.mpg', '.rm', '.swf', '.vob', '.wmv'], 'Videos'))

# Archives
dir_map.update(dict.fromkeys(['.7z', '.arj', '.bz2',  '.gz', '.lz4',
                              '.rar', '.tar', '.xz', '.z', '.zip', '.zstd'], 'Archives'))

# Programs
dir_map.update(dict.fromkeys(
    ['.apk', '.bin', '.deb', '.exe', '.jar', '.msi', '.rpm'], 'Programs'))

# Code
dir_map.update(dict.fromkeys(['.c', '.cpp', '.java', '.py', '.js', '.class', '.h', '.sh', '.bat', '.css',
                              '.go', '.rs', '.cs', '.swift', '.r', '.php', '.dart', '.kt', '.mat', '.pl', '.rb', '.scala'], 'Code'))

# Markup
dir_map.update(dict.fromkeys(
    ['.html', '.xml', '.xhtml', '.mhtml'], 'Code' + os.sep + 'Markup'))

# Database
dir_map.update(dict.fromkeys(
    ['.sql', '.db', '.json', '.csv'], 'Code' + os.sep + 'Database'))

# Initialize parser
parser = argparse.ArgumentParser(prog="orgpy", description="Organize yor digital mess.",
                                 epilog="Visit github.com/2KAbhishek/orgpy for more.")

# Optional path
parser.add_argument("-p", "--path", metavar="path", type=str, default=os.getcwd(),
                    help="The directory path to organize.")

# Dry run flag
parser.add_argument("--dry-run", action="store_true",
                    help="Preview changes without actually moving files.")

args = parser.parse_args()

# Use current dir if path is not specified or incorrect
path = os.getcwd()

if args.path and os.path.exists(args.path):
    path = args.path


# Main organize method
def organize(path: str, dry_run: bool = False) -> None:
    files_by_dir = defaultdict(list)
    skipped_files = []

    # Group files by destination directory
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            file_name, ext = os.path.splitext(file)
            if ext.lower() in dir_map:
                files_by_dir[dir_map[ext.lower()]].append(file)
            else:
                skipped_files.append(file)

    # Display organized output
    if dry_run:
        print(f"\n🔍 DRY RUN - Preview for: {os.path.basename(path)}")
        print("=" * 50)
    else:
        print(f"\n📂 Organizing: {os.path.basename(path)}")
        print("=" * 50)

    total_files = 0
    for dest_dir, files in files_by_dir.items():
        if files:
            print(f"\n📁 {dest_dir}/ ({len(files)} files)")
            for file in sorted(files):
                if dry_run:
                    print(f"   ➤ {file}")
                else:
                    try:
                        if not os.path.exists(os.path.join(path, dest_dir)):
                            os.makedirs(os.path.join(path, dest_dir))

                        os.replace(os.path.join(path, file),
                                 os.path.join(path, dest_dir, file))
                        print(f"   ✅ {file}")
                        total_files += 1
                    except Exception as e:
                        print(f"   ❌ {file} (Error: {str(e)})")
                        skipped_files.append(file)

            if dry_run:
                total_files += len(files)

    # Show skipped files
    if skipped_files:
        print(f"\n⚠️  Skipped files ({len(skipped_files)}):")
        for file in sorted(skipped_files):
            print(f"   • {file}")

    # Summary
    action = "Would organize" if dry_run else "Organized"
    print(f"\n📊 Summary: {action} {total_files} files")
    if skipped_files:
        print(f"   Skipped: {len(skipped_files)} files")
    print()


if args.dry_run:
    organize(path, dry_run=True)
elif input(f"Organize directory '{os.path.basename(path)}'? (y/N): ") in ['y', 'Y', 'yes', 'Yes']:
    organize(path)
else:
    print("Operation cancelled.")
