import json
import os
import tempfile
import unittest
from pathlib import Path

from aidkits.json_splitter import JsonSplitter


class TestJsonSplitter(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = os.path.join(self.temp_dir.name, "output")
        
        # Create a test JSON file
        self.test_data = [
            {"title": "Document 1", "content": "Content 1"},
            {"title": "Document 2", "content": "Content 2"},
            {"title": "Document 1", "content": "More content for Document 1"},
            {"title": "Document 3", "content": "Content 3"}
        ]
        self.test_file = os.path.join(self.temp_dir.name, "test.json")
        with open(self.test_file, "w", encoding="utf-8") as f:
            json.dump(self.test_data, f)
        
        # Create the JsonSplitter instance
        self.splitter = JsonSplitter(output_dir=self.output_dir)
    
    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()
    
    def test_split_json_file(self):
        # Split the test JSON file
        grouped_data = self.splitter.split_json_file(
            input_file=self.test_file,
            group_by_field="title"
        )
        
        # Check that the output directory was created
        self.assertTrue(os.path.exists(self.output_dir))
        
        # Check that the correct number of files were created
        self.assertEqual(len(grouped_data), 3)
        
        # Check that the files were created with the correct names
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "Document_1.json")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "Document_2.json")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "Document_3.json")))
        
        # Check the contents of the files
        with open(os.path.join(self.output_dir, "Document_1.json"), "r", encoding="utf-8") as f:
            doc1_data = json.load(f)
            self.assertEqual(len(doc1_data), 2)
            self.assertEqual(doc1_data[0]["title"], "Document 1")
            self.assertEqual(doc1_data[1]["title"], "Document 1")
        
        with open(os.path.join(self.output_dir, "Document_2.json"), "r", encoding="utf-8") as f:
            doc2_data = json.load(f)
            self.assertEqual(len(doc2_data), 1)
            self.assertEqual(doc2_data[0]["title"], "Document 2")
        
        with open(os.path.join(self.output_dir, "Document_3.json"), "r", encoding="utf-8") as f:
            doc3_data = json.load(f)
            self.assertEqual(len(doc3_data), 1)
            self.assertEqual(doc3_data[0]["title"], "Document 3")
    
    def test_split_json_data(self):
        # Split the test JSON data directly
        grouped_data = self.splitter.split_json_data(
            data=self.test_data,
            group_by_field="title"
        )
        
        # Check that the output directory was created
        self.assertTrue(os.path.exists(self.output_dir))
        
        # Check that the correct number of files were created
        self.assertEqual(len(grouped_data), 3)
        
        # Check that the files were created with the correct names
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "Document_1.json")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "Document_2.json")))
        self.assertTrue(os.path.exists(os.path.join(self.output_dir, "Document_3.json")))
        
        # Check the contents of the files
        with open(os.path.join(self.output_dir, "Document_1.json"), "r", encoding="utf-8") as f:
            doc1_data = json.load(f)
            self.assertEqual(len(doc1_data), 2)
            self.assertEqual(doc1_data[0]["title"], "Document 1")
            self.assertEqual(doc1_data[1]["title"], "Document 1")
        
        with open(os.path.join(self.output_dir, "Document_2.json"), "r", encoding="utf-8") as f:
            doc2_data = json.load(f)
            self.assertEqual(len(doc2_data), 1)
            self.assertEqual(doc2_data[0]["title"], "Document 2")
        
        with open(os.path.join(self.output_dir, "Document_3.json"), "r", encoding="utf-8") as f:
            doc3_data = json.load(f)
            self.assertEqual(len(doc3_data), 1)
            self.assertEqual(doc3_data[0]["title"], "Document 3")
    
    def test_sanitize_filename(self):
        # Test the _sanitize_filename method
        self.assertEqual(self.splitter._sanitize_filename("test"), "test.json")
        self.assertEqual(self.splitter._sanitize_filename("test.json"), "test.json")
        self.assertEqual(self.splitter._sanitize_filename("test/file"), "test_file.json")
        self.assertEqual(self.splitter._sanitize_filename("test\\file"), "test_file.json")
        self.assertEqual(self.splitter._sanitize_filename("test:file"), "test_file.json")
        self.assertEqual(self.splitter._sanitize_filename("test*file"), "test_file.json")
        self.assertEqual(self.splitter._sanitize_filename("test?file"), "test_file.json")
        self.assertEqual(self.splitter._sanitize_filename("test\"file"), "test_file.json")
        self.assertEqual(self.splitter._sanitize_filename("test<file"), "test_file.json")
        self.assertEqual(self.splitter._sanitize_filename("test>file"), "test_file.json")
        self.assertEqual(self.splitter._sanitize_filename("test|file"), "test_file.json")


if __name__ == "__main__":
    unittest.main()