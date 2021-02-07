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

