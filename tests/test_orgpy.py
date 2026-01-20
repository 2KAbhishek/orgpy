#!/usr/bin/env python3
"""Test suite for orgpy - File organization utility."""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import orgpy


class TestCategorizeFile(unittest.TestCase):
    """Test the categorize_file function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.temp_dir)

    def test_categorize_known_extensions(self):
        """Test categorization of known file extensions."""
        test_files = {
            'document.pdf': ('Docs' + os.sep + 'PDF', True),
            'photo.jpg': ('Images', True),
            'song.mp3': ('Audio', True),
            'video.mp4': ('Videos', True),
            'archive.zip': ('Archives', True),
            'script.py': ('Code', True),
            'data.json': ('Code' + os.sep + 'Database', True),
            'page.html': ('Code' + os.sep + 'Markup', True),
        }

        for filename, expected in test_files.items():
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write('test content')

            result = orgpy.categorize_file(filename, self.temp_dir)
            self.assertEqual(result, expected, f"Failed for {filename}")

    def test_categorize_unknown_extensions(self):
        """Test categorization of unknown file extensions."""
        filename = 'unknown.xyz'
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write('test content')

        result = orgpy.categorize_file(filename, self.temp_dir)
        self.assertEqual(result, ('', False))

    def test_categorize_no_extension(self):
        """Test categorization of files without extension."""
        filename = 'README'
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write('test content')

        result = orgpy.categorize_file(filename, self.temp_dir)
        self.assertEqual(result, ('', False))

    def test_categorize_case_insensitive(self):
        """Test that extension matching is case insensitive."""
        filename = 'DOCUMENT.PDF'
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, 'w') as f:
            f.write('test content')

        result = orgpy.categorize_file(filename, self.temp_dir)
        self.assertEqual(result, ('Docs' + os.sep + 'PDF', True))

    def test_categorize_nonexistent_file(self):
        """Test categorization of non-existent files."""
        result = orgpy.categorize_file('nonexistent.pdf', self.temp_dir)
        self.assertEqual(result, ('', False))

    def test_categorize_directory(self):
        """Test categorization of directories (should be skipped)."""
        dirname = 'test_directory'
        dirpath = os.path.join(self.temp_dir, dirname)
        os.mkdir(dirpath)

        result = orgpy.categorize_file(dirname, self.temp_dir)
        self.assertEqual(result, ('', False))


class TestAnalyzeFiles(unittest.TestCase):
    """Test the analyze_files function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.temp_dir)

    def test_analyze_mixed_files(self):
        """Test analysis of directory with mixed file types."""
        test_files = [
            'document1.pdf', 'document2.txt', 'photo1.jpg', 'photo2.png',
            'song.mp3', 'video.mp4', 'script.py', 'README', 'unknown.xyz'
        ]

        for filename in test_files:
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write('test content')

        files_by_dir, skipped_files = orgpy.analyze_files(self.temp_dir)

        expected_categorized = {
            'Docs' + os.sep + 'PDF': ['document1.pdf'],
            'Docs': ['document2.txt'],
            'Images': ['photo1.jpg', 'photo2.png'],
            'Audio': ['song.mp3'],
            'Videos': ['video.mp4'],
            'Code': ['script.py'],
        }

        for category, expected_files in expected_categorized.items():
            self.assertIn(category, files_by_dir)
            self.assertEqual(sorted(files_by_dir[category]), sorted(expected_files))

        expected_skipped = ['README', 'unknown.xyz']
        self.assertEqual(sorted(skipped_files), sorted(expected_skipped))

    def test_analyze_empty_directory(self):
        """Test analysis of empty directory."""
        files_by_dir, skipped_files = orgpy.analyze_files(self.temp_dir)

        self.assertEqual(len(files_by_dir), 0)
        self.assertEqual(len(skipped_files), 0)

    def test_analyze_only_skipped_files(self):
        """Test analysis of directory with only unrecognized files."""
        test_files = ['unknown1.xyz', 'unknown2.abc', 'README']

        for filename in test_files:
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write('test content')

        files_by_dir, skipped_files = orgpy.analyze_files(self.temp_dir)

        self.assertEqual(len(files_by_dir), 0)
        self.assertEqual(sorted(skipped_files), sorted(test_files))

    def test_analyze_permission_error(self):
        """Test behavior when directory cannot be accessed."""
        with patch('os.listdir') as mock_listdir:
            mock_listdir.side_effect = PermissionError("Permission denied")

            with self.assertRaises(PermissionError):
                orgpy.analyze_files('/fake/path')


class TestMoveFile(unittest.TestCase):
    """Test the move_file function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.temp_dir, 'source')
        self.dest_dir = os.path.join(self.temp_dir, 'dest')
        os.makedirs(self.source_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.temp_dir)

    def test_move_file_success(self):
        """Test successful file move."""
        filename = 'test.txt'
        source_file = os.path.join(self.source_dir, filename)
        with open(source_file, 'w') as f:
            f.write('test content')

        result = orgpy.move_file(self.source_dir, self.dest_dir, filename)

        self.assertTrue(result)
        self.assertFalse(os.path.exists(source_file))
        self.assertTrue(os.path.exists(os.path.join(self.dest_dir, filename)))

    def test_move_file_creates_destination(self):
        """Test that destination directory is created if it doesn't exist."""
        filename = 'test.txt'
        source_file = os.path.join(self.source_dir, filename)
        with open(source_file, 'w') as f:
            f.write('test content')

        nested_dest = os.path.join(self.dest_dir, 'nested', 'path')
        self.assertFalse(os.path.exists(nested_dest))

        result = orgpy.move_file(self.source_dir, nested_dest, filename)

        self.assertTrue(result)
        self.assertTrue(os.path.exists(nested_dest))
        self.assertTrue(os.path.exists(os.path.join(nested_dest, filename)))

    def test_move_nonexistent_file(self):
        """Test moving non-existent file."""
        result = orgpy.move_file(self.source_dir, self.dest_dir, 'nonexistent.txt')
        self.assertFalse(result)

    def test_move_file_permission_error(self):
        """Test handling of permission errors."""
        filename = 'test.txt'
        source_file = os.path.join(self.source_dir, filename)
        with open(source_file, 'w') as f:
            f.write('test content')

        with patch('os.replace') as mock_replace:
            mock_replace.side_effect = PermissionError("Permission denied")

            result = orgpy.move_file(self.source_dir, self.dest_dir, filename)
            self.assertFalse(result)


class TestProcessDirectory(unittest.TestCase):
    """Test the process_directory function."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.temp_dir)

    @patch('builtins.print')
    def test_process_directory_dry_run(self, mock_print):
        """Test process_directory in dry-run mode."""
        files = ['test1.txt', 'test2.txt', 'test3.txt']
        dest_dir = 'Docs'

        moved_count, failed_files = orgpy.process_directory(
            self.temp_dir, dest_dir, files, dry_run=True
        )

        self.assertEqual(moved_count, 3)
        self.assertEqual(failed_files, [])

        mock_print.assert_any_call(f"\n📁 {dest_dir}/ (3 files)")
        for file in files:
            mock_print.assert_any_call(f"   ➤ {file}")

    @patch('orgpy.move_file')
    @patch('builtins.print')
    def test_process_directory_actual_move(self, mock_print, mock_move_file):
        """Test process_directory with actual file moves."""
        files = ['test1.txt', 'test2.txt', 'test3.txt']
        dest_dir = 'Docs'

        mock_move_file.return_value = True

        moved_count, failed_files = orgpy.process_directory(
            self.temp_dir, dest_dir, files, dry_run=False
        )

        self.assertEqual(moved_count, 3)
        self.assertEqual(failed_files, [])

        self.assertEqual(mock_move_file.call_count, 3)

        for file in files:
            mock_print.assert_any_call(f"   ✅ {file}")

    @patch('orgpy.move_file')
    @patch('builtins.print')
    def test_process_directory_some_failures(self, mock_print, mock_move_file):
        """Test process_directory with some failed moves."""
        files = ['test1.txt', 'test2.txt', 'test3.txt']
        dest_dir = 'Docs'

        mock_move_file.side_effect = [True, False, False]

        moved_count, failed_files = orgpy.process_directory(
            self.temp_dir, dest_dir, files, dry_run=False
        )

        self.assertEqual(moved_count, 1)
        self.assertEqual(sorted(failed_files), ['test2.txt', 'test3.txt'])


class TestOrganize(unittest.TestCase):
    """Test the organize function (integration test)."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for file in files:
                try:
                    os.remove(os.path.join(root, file))
                except OSError:
                    pass
            for dir in dirs:
                try:
                    os.rmdir(os.path.join(root, dir))
                except OSError:
                    pass
        try:
            os.rmdir(self.temp_dir)
        except OSError:
            pass

    @patch('builtins.print')
    def test_organize_dry_run(self, mock_print):
        """Test organize function in dry-run mode."""
        test_files = ['document.pdf', 'photo.jpg', 'song.mp3', 'README']

        for filename in test_files:
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write('test content')

        orgpy.organize(self.temp_dir, dry_run=True)

        for filename in test_files:
            filepath = os.path.join(self.temp_dir, filename)
            self.assertTrue(os.path.exists(filepath))

    def test_organize_actual(self):
        """Test organize function with actual file moves."""
        test_files = {
            'document.pdf': 'Docs' + os.sep + 'PDF',
            'photo.jpg': 'Images',
            'song.mp3': 'Audio',
        }

        for filename in test_files.keys():
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, 'w') as f:
                f.write('test content')

        orgpy.organize(self.temp_dir, dry_run=False)

        for filename, expected_dir in test_files.items():
            original_path = os.path.join(self.temp_dir, filename)
            new_path = os.path.join(self.temp_dir, expected_dir, filename)

            self.assertFalse(os.path.exists(original_path), f"{filename} should be moved")
            self.assertTrue(os.path.exists(new_path), f"{filename} should be in {expected_dir}")

        for expected_dir in test_files.values():
            dir_path = os.path.join(self.temp_dir, expected_dir)
            self.assertTrue(os.path.exists(dir_path), f"Directory {expected_dir} should exist")


class TestFileCategoriesMapping(unittest.TestCase):
    """Test the FILE_CATEGORIES mapping and dir_map generation."""

    def test_dir_map_generation(self):
        """Test that dir_map is generated correctly from FILE_CATEGORIES."""
        expected_mappings = {
            '.pdf': 'Docs' + os.sep + 'PDF',
            '.jpg': 'Images',
            '.mp3': 'Audio',
            '.mp4': 'Videos',
            '.zip': 'Archives',
            '.py': 'Code',
            '.html': 'Code' + os.sep + 'Markup',
            '.json': 'Code' + os.sep + 'Database',
        }

        for ext, expected_dir in expected_mappings.items():
            self.assertIn(ext, orgpy.dir_map)
            self.assertEqual(orgpy.dir_map[ext], expected_dir)

    def test_case_insensitive_extensions(self):
        """Test that extensions are stored in lowercase."""
        for ext in orgpy.dir_map.keys():
            self.assertEqual(ext, ext.lower(), f"Extension {ext} should be lowercase")

    def test_no_duplicate_extensions(self):
        """Test that no extension appears in multiple categories."""
        all_extensions = []
        for extensions in orgpy.FILE_CATEGORIES.values():
            all_extensions.extend([ext.lower() for ext in extensions])

        unique_extensions = set(all_extensions)
        self.assertEqual(len(all_extensions), len(unique_extensions),
                        "Some extensions appear in multiple categories")


if __name__ == '__main__':
    unittest.main(verbosity=2, buffer=True)
