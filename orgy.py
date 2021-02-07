#!/usr/bin/env python3
import argparse
import os

# Directory mapping, maps file extensions to directories
dir_map = {'.txt': 'Docs', '.pdf': 'Docs' + os.sep + 'PDF'}

# Word files
dir_map.update(dict.fromkeys(
    ['.doc', '.docx', '.odt', 'rtf'], 'Docs' + os.sep + 'Word'))

# Sheets
dir_map.update(dict.fromkeys(
    ['.csv', '.ods', '.xls', '.xlsm', '.xlsx'], 'Docs' + os.sep + 'Sheets'))

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

# Initialize parser
parser = argparse.ArgumentParser(prog="orgy", description="Organize yor digital mess.",
                                 epilog="Visit github.com/2KAbhishek/orgy for more.")

# Optional path
parser.add_argument("-p", "--path", metavar="path", type=str,
                    help="The directory path to organize.")

args = parser.parse_args()

# Use current dir if path is not specified or incorrect
path = os.getcwd()

if args.path and os.path.exists(args.path):
    path = args.path


