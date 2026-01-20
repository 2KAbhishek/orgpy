#!/usr/bin/env python3

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import orgpy


class TestConfigSystem(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.test_config_file = os.path.join(self.temp_dir, "test_config.json")

    def tearDown(self):
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.temp_dir)

    def test_load_config_nonexistent_file(self):
        with (
            patch.object(orgpy, "CONFIG_FILE", Path("/nonexistent/config.json")),
            patch.object(
                orgpy, "TEMPLATE_CONFIG_FILE", Path("/nonexistent/template.json")
            ),
        ):
            config = orgpy.load_config()
            self.assertEqual(config, {"file_categories": {}})

    def test_load_config_valid_file(self):
        test_config = {
            "file_categories": {
                "TestDocs": [".test", ".spec"],
                "MyFiles": [".my", ".custom"],
            }
        }

        with open(self.test_config_file, "w") as f:
            json.dump(test_config, f)

        with patch.object(orgpy, "CONFIG_FILE", Path(self.test_config_file)):
            config = orgpy.load_config()
            self.assertEqual(config, test_config)

    def test_load_config_invalid_json(self):
        with open(self.test_config_file, "w") as f:
            f.write("{invalid json content")

        with patch.object(orgpy, "CONFIG_FILE", Path(self.test_config_file)):
            config = orgpy.load_config()
            self.assertEqual(config, {})

    def test_load_config_from_path_valid(self):
        test_config = {"file_categories": {"Custom": [".cust"]}}

        with open(self.test_config_file, "w") as f:
            json.dump(test_config, f)

        config = orgpy.load_config_from_path(self.test_config_file)
        self.assertEqual(config, test_config)

    def test_load_config_from_path_nonexistent(self):
        config = orgpy.load_config_from_path("/nonexistent/config.json")
        self.assertEqual(config, {})

    def test_merge_categories_empty_config(self):
        test_template_path = Path(self.temp_dir) / "template.json"
        template_config = {"file_categories": {"Default": [".default"]}}
        with open(test_template_path, "w") as f:
            json.dump(template_config, f)

        with patch.object(orgpy, "TEMPLATE_CONFIG_FILE", test_template_path):
            config = {}
            merged = orgpy.merge_categories(config)
            self.assertEqual(merged, {"Default": [".default"]})

    def test_merge_categories_with_custom(self):
        config = {
            "file_categories": {
                "CustomDocs": [".mydoc", ".notes"],
                "Images": [".jpg", ".png"],
            }
        }
        merged = orgpy.merge_categories(config)

        self.assertIn("CustomDocs", merged)
        self.assertIn("Images", merged)
        self.assertEqual(merged["CustomDocs"], [".mydoc", ".notes"])
        self.assertEqual(merged["Images"], [".jpg", ".png"])

    def test_merge_categories_no_file_categories_key(self):
        test_template_path = Path(self.temp_dir) / "template.json"
        template_config = {"file_categories": {"Fallback": [".fallback"]}}
        with open(test_template_path, "w") as f:
            json.dump(template_config, f)

        with patch.object(orgpy, "TEMPLATE_CONFIG_FILE", test_template_path):
            config = {"other_setting": "value"}
            merged = orgpy.merge_categories(config)
            self.assertEqual(merged, {"Fallback": [".fallback"]})

    def test_load_config_auto_create(self):
        test_config_path = Path(self.temp_dir) / "auto_config.json"
        test_template_path = Path(self.temp_dir) / "template.json"

        template_config = {"file_categories": {"Test": [".test"]}}
        with open(test_template_path, "w") as f:
            json.dump(template_config, f)

        if test_config_path.exists():
            test_config_path.unlink()

        with (
            patch.object(orgpy, "CONFIG_FILE", test_config_path),
            patch.object(orgpy, "TEMPLATE_CONFIG_FILE", test_template_path),
        ):
            config = orgpy.load_config()

        self.assertTrue(test_config_path.exists())
        self.assertIn("file_categories", config)
        self.assertEqual(config["file_categories"], {"Test": [".test"]})

    def test_create_default_config(self):
        test_config_path = Path(self.temp_dir) / "new_config.json"
        test_template_path = Path(self.temp_dir) / "template.json"

        template_config = {"file_categories": {"Sample": [".sample"]}}
        with open(test_template_path, "w") as f:
            json.dump(template_config, f)

        with (
            patch.object(orgpy, "CONFIG_FILE", test_config_path),
            patch.object(orgpy, "TEMPLATE_CONFIG_FILE", test_template_path),
        ):
            result = orgpy.create_default_config()

        self.assertTrue(test_config_path.exists())
        self.assertIn("file_categories", result)
        self.assertEqual(result["file_categories"], {"Sample": [".sample"]})

    def test_build_extension_map(self):
        categories = {
            "Docs": [".md", ".txt"],
            "Images": [".JPG", ".PNG"],
            "Custom/SubDir": [".custom"],
        }

        actual_map = orgpy.build_extension_map(categories)

        expected_map = {
            ".md": "Docs",
            ".txt": "Docs",
            ".jpg": "Images",
            ".png": "Images",
            ".custom": "Custom" + os.sep + "SubDir",
        }

        self.assertEqual(actual_map, expected_map)


class TestCategorizeFile(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        config, self.dir_map = orgpy.get_config_and_mapping()

    def tearDown(self):
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.temp_dir)

    def test_categorize_known_extensions(self):
        test_files = {
            "document.pdf": ("Docs" + os.sep + "PDF", True),
            "photo.jpg": ("Images", True),
            "song.mp3": ("Audio", True),
            "video.mp4": ("Videos", True),
            "archive.zip": ("Archives", True),
            "script.py": ("Code", True),
            "data.json": ("Code" + os.sep + "Database", True),
            "page.html": ("Code" + os.sep + "Markup", True),
        }

        for filename, expected in test_files.items():
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, "w") as f:
                f.write("test content")

            result = orgpy.categorize_file(filename, self.temp_dir, self.dir_map)
            self.assertEqual(result, expected, f"Failed for {filename}")

    def test_categorize_unknown_extensions(self):
        filename = "unknown.xyz"
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, "w") as f:
            f.write("test content")

        result = orgpy.categorize_file(filename, self.temp_dir, self.dir_map)
        self.assertEqual(result, ("", False))

    def test_categorize_case_insensitive(self):
        filename = "DOCUMENT.PDF"
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, "w") as f:
            f.write("test content")

        result = orgpy.categorize_file(filename, self.temp_dir, self.dir_map)
        self.assertEqual(result, ("Docs" + os.sep + "PDF", True))

    def test_categorize_no_extension(self):
        filename = "README"
        filepath = os.path.join(self.temp_dir, filename)
        with open(filepath, "w") as f:
            f.write("test content")

        result = orgpy.categorize_file(filename, self.temp_dir, self.dir_map)
        self.assertEqual(result, ("", False))

    def test_categorize_nonexistent_file(self):
        result = orgpy.categorize_file("nonexistent.pdf", self.temp_dir, self.dir_map)
        self.assertEqual(result, ("", False))

    def test_categorize_directory(self):
        dirname = "test_dir"
        dir_path = os.path.join(self.temp_dir, dirname)
        os.makedirs(dir_path)

        result = orgpy.categorize_file(dirname, self.temp_dir, self.dir_map)
        self.assertEqual(result, ("", False))


class TestAnalyzeFiles(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        config, self.dir_map = orgpy.get_config_and_mapping()

    def tearDown(self):
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.temp_dir)

    def test_analyze_mixed_files(self):
        test_files = [
            "document1.pdf",
            "document2.txt",
            "photo1.jpg",
            "photo2.png",
            "song.mp3",
            "video.mp4",
            "script.py",
            "README",
            "unknown.xyz",
        ]

        for filename in test_files:
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, "w") as f:
                f.write("test content")

        files_by_dir, skipped_files = orgpy.analyze_files(self.temp_dir, self.dir_map)

        expected_categorized = {
            "Docs" + os.sep + "PDF": ["document1.pdf"],
            "Docs": ["document2.txt"],
            "Images": ["photo1.jpg", "photo2.png"],
            "Audio": ["song.mp3"],
            "Videos": ["video.mp4"],
            "Code": ["script.py"],
        }

        for category, expected_files in expected_categorized.items():
            self.assertIn(category, files_by_dir)
            for expected_file in expected_files:
                self.assertIn(expected_file, files_by_dir[category])

        self.assertIn("README", skipped_files)
        self.assertIn("unknown.xyz", skipped_files)

    def test_analyze_empty_directory(self):
        files_by_dir, skipped_files = orgpy.analyze_files(self.temp_dir, self.dir_map)

        self.assertEqual(len(files_by_dir), 0)
        self.assertEqual(len(skipped_files), 0)

    def test_analyze_only_skipped_files(self):
        for filename in ["file1.unknown", "file2.xyz"]:
            filepath = os.path.join(self.temp_dir, filename)
            with open(filepath, "w") as f:
                f.write("test content")

        files_by_dir, skipped_files = orgpy.analyze_files(self.temp_dir, self.dir_map)

        self.assertEqual(len(files_by_dir), 0)
        self.assertEqual(len(skipped_files), 2)

    def test_analyze_permission_error(self):
        with self.assertRaises(FileNotFoundError):
            orgpy.analyze_files("/fake/path", self.dir_map)


class TestFileCategoriesMapping(unittest.TestCase):
    def test_dir_map_generation(self):
        config, dir_map = orgpy.get_config_and_mapping()

        self.assertIsInstance(dir_map, dict)

        for ext in [".pdf", ".jpg", ".mp3", ".py"]:
            self.assertIn(ext, dir_map)

    def test_case_insensitive_extensions(self):
        config, dir_map = orgpy.get_config_and_mapping()

        for ext in dir_map.keys():
            self.assertEqual(ext, ext.lower())

    def test_no_duplicate_extensions(self):
        config, dir_map = orgpy.get_config_and_mapping()

        seen_extensions = set()
        file_categories = orgpy.merge_categories(config)

        for extensions in file_categories.values():
            for ext in extensions:
                ext_lower = ext.lower()
                self.assertNotIn(
                    ext_lower,
                    seen_extensions,
                    f"Extension {ext} appears in multiple categories",
                )
                seen_extensions.add(ext_lower)


class TestMoveFile(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.temp_dir)

    def test_move_file_success(self):
        source_file = "test_file.txt"
        source_path = self.temp_dir
        dest_path = os.path.join(self.temp_dir, "dest_folder")

        with open(os.path.join(source_path, source_file), "w") as f:
            f.write("test content")

        result = orgpy.move_file(source_path, dest_path, source_file)

        self.assertTrue(result)
        self.assertTrue(os.path.exists(os.path.join(dest_path, source_file)))
        self.assertFalse(os.path.exists(os.path.join(source_path, source_file)))

    def test_move_file_creates_destination(self):
        source_file = "test_file.txt"
        source_path = self.temp_dir
        dest_path = os.path.join(self.temp_dir, "new_folder", "nested_folder")

        with open(os.path.join(source_path, source_file), "w") as f:
            f.write("test content")

        result = orgpy.move_file(source_path, dest_path, source_file)

        self.assertTrue(result)
        self.assertTrue(os.path.exists(dest_path))
        self.assertTrue(os.path.exists(os.path.join(dest_path, source_file)))

    def test_move_nonexistent_file(self):
        result = orgpy.move_file(self.temp_dir, self.temp_dir, "nonexistent.txt")
        self.assertFalse(result)

    def test_move_file_permission_error(self):
        result = orgpy.move_file("/fake/source", "/fake/dest", "fake.txt")
        self.assertFalse(result)


class TestProcessDirectory(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.temp_dir)

    def test_process_directory_dry_run(self):
        files = ["file1.txt", "file2.txt"]
        dest_dir = "TestDocs"

        for filename in files:
            with open(os.path.join(self.temp_dir, filename), "w") as f:
                f.write("test")

        with patch("builtins.print"):
            moved_count, failed_files = orgpy.process_directory(
                self.temp_dir, dest_dir, files, dry_run=True
            )

        self.assertEqual(moved_count, 2)
        self.assertEqual(len(failed_files), 0)

        for filename in files:
            self.assertTrue(os.path.exists(os.path.join(self.temp_dir, filename)))

    def test_process_directory_actual_move(self):
        files = ["file1.txt", "file2.txt"]
        dest_dir = "TestDocs"

        for filename in files:
            with open(os.path.join(self.temp_dir, filename), "w") as f:
                f.write("test")

        with patch("builtins.print"):
            moved_count, failed_files = orgpy.process_directory(
                self.temp_dir, dest_dir, files, dry_run=False
            )

        self.assertEqual(moved_count, 2)
        self.assertEqual(len(failed_files), 0)

        dest_path = os.path.join(self.temp_dir, dest_dir)
        for filename in files:
            self.assertTrue(os.path.exists(os.path.join(dest_path, filename)))
            self.assertFalse(os.path.exists(os.path.join(self.temp_dir, filename)))

    def test_process_directory_some_failures(self):
        files = ["good_file.txt", "bad_file.txt"]
        dest_dir = "TestDocs"

        with open(os.path.join(self.temp_dir, "good_file.txt"), "w") as f:
            f.write("test")

        with patch("builtins.print"):
            moved_count, failed_files = orgpy.process_directory(
                self.temp_dir, dest_dir, files, dry_run=False
            )

        self.assertEqual(moved_count, 1)
        self.assertEqual(len(failed_files), 1)
        self.assertIn("bad_file.txt", failed_files)


class TestOrganize(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        config, self.dir_map = orgpy.get_config_and_mapping()

    def tearDown(self):
        for root, dirs, files in os.walk(self.temp_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        os.rmdir(self.temp_dir)

    def test_organize_dry_run(self):
        test_files = ["document.pdf", "photo.jpg", "unknown.xyz"]
        for filename in test_files:
            with open(os.path.join(self.temp_dir, filename), "w") as f:
                f.write("test content")

        with patch("builtins.print"):
            orgpy.organize(self.temp_dir, self.dir_map, dry_run=True)

        for filename in test_files:
            self.assertTrue(os.path.exists(os.path.join(self.temp_dir, filename)))

    def test_organize_actual(self):
        test_files = ["document.pdf", "photo.jpg", "song.mp3"]

        for filename in test_files:
            with open(os.path.join(self.temp_dir, filename), "w") as f:
                f.write("test content")

        with patch("builtins.print"):
            orgpy.organize(self.temp_dir, self.dir_map, dry_run=False)

        expected_locations = {
            "document.pdf": "Docs" + os.sep + "PDF",
            "photo.jpg": "Images",
            "song.mp3": "Audio",
        }

        for filename, expected_dir in expected_locations.items():
            expected_path = os.path.join(self.temp_dir, expected_dir, filename)
            self.assertTrue(os.path.exists(expected_path))

            original_path = os.path.join(self.temp_dir, filename)
            self.assertFalse(os.path.exists(original_path))


if __name__ == "__main__":
    unittest.main()
