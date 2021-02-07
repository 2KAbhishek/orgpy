#!/usr/bin/env python3
import argparse
import os

# Directory mapping, maps file extensions to directories
dir_map = {'.txt': 'Docs', '.pdf': 'Docs' + os.sep + 'PDF'}

# Word files
dir_map.update(dict.fromkeys(
    ['.doc', '.docx', '.odt', 'rtf'], 'Docs' + os.sep + 'Word'))

# Spreadsheets
dir_map.update(dict.fromkeys(
    ['.csv', '.ods', '.xls', '.xlsm', '.xlsx'], 'Docs' + os.sep + 'Sheets'))

