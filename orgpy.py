#!/usr/bin/env python3
import argparse
import os

# Directory mapping, maps file extensions to directories
dir_map = {'.txt': 'Docs', '.pdf': 'Docs' + os.sep + 'PDF'}

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
                              '.jpg', '.png', '.ps', '.psd', '.svg', '.tif', '.tiff'], 'Images'))

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
    ['.md', '.html', '.xml', '.xhtml', '.mhtml'], 'Code' + os.sep + 'Markup'))

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
    for file in os.listdir(path):
        file_name, ext = os.path.splitext(os.path.join(path, file))
        try:
            if dry_run:
                print("Would move: " + file + " -> " +
                      os.path.join(dir_map[ext], file))
            else:
                if not os.path.exists(os.path.join(path, dir_map[ext])):
                    os.makedirs(os.path.join(path, dir_map[ext]))

                os.replace(os.path.join(path, file),
                           os.path.join(path, dir_map[ext], file))

                print("Moved: " + file + " -> " +
                      os.path.join(dir_map[ext], file))
        except:
            print("Skipped: " + file)


if args.dry_run:
    print("DRY RUN MODE - No files will be moved")
    organize(path, dry_run=True)
elif input("Organize directory: " + os.path.basename(path) + " ? -> ") in ['y', 'Y', 'yes', 'Yes']:
    organize(path)
    print(os.listdir(path))
else:
    print("OK, Bye!")
