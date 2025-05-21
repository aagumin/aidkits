import os
import tempfile

import pytest

from aidkits.parse import MarkdownCrawler


@pytest.mark.parametrize(
    "markdown_content, expected_chunks",
    [
        (
            "# Header 1\nContent `# code` 1\n# Header 2\nContent 2",
            ["# Header 1\nContent `# code` 1", "# Header 2\nContent 2"],
        ),
        (
            "# Header 1\nContent 1\n## Subheader 1\nContent 2",
            ["# Header 1\nContent 1", "## Subheader 1\nContent 2"],
        ),
        ("No headers, only text", ["No headers, only text"]),
    ],
)
def test_split_by_headers(markdown_content, expected_chunks, tmp_path):
    with open(tmp_path / "test.md", "w") as f:
        f.write(markdown_content)
    mc = MarkdownCrawler(repo_url=str(tmp_path))
    chunks = mc.split_markdown_by_headers(markdown_content)
    assert chunks == expected_chunks


@pytest.fixture
def markdown_test_repo(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()

    (repo_dir / "file1.md").write_text("# Header 1\nContent for file 1")
    (repo_dir / "file2.md").write_text("# Header 2\nContent for file 2")

    (repo_dir / "file.txt").write_text("This is a text file")
    (repo_dir / "script.py").write_text("print('Hello, World!')")

    return repo_dir


@pytest.fixture
def markdown_files():
    """Create a temporary directory with sample markdown files for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        file1_path = os.path.join(temp_dir, "file1.md")
        file2_path = os.path.join(temp_dir, "file2.md")

        content1 = """
# Header 1

This is some content.

## Header 2

More content.

"""
        content2 = """
# Title of File 2

Simple text.

"""
        with (
            open(file1_path, "w", encoding="utf-8") as f1,
            open(file2_path, "w", encoding="utf-8") as f2,
        ):
            f1.write(content1)
            f2.write(content2)

        yield temp_dir  # Provide the temp directory path for the test to use


# def test_collect_markdown_files_single_file(markdown_files):
#     class_instance = MarkdownCrawler(
#         markdown_files
#     )  # Replace with the actual class name
#     sources = class_instance.collect_markdown_files(markdown_files)
#
#     assert len(sources) == 2  # Two files should be processed
#
#     # Check the first file
#     source1 = sources[0]
#     assert source1.title == "file1.md"  # File name should match
#     assert len(source1.chunks) == 2  # File 1 has 2 headers (so 2 chunks)
#
#     chunk1 = source1.chunks[0]
#     assert chunk1.chunk_num == 1
#     assert chunk1.chunk_amount == 3
#     assert "# Header 1" in chunk1.content
#     assert "This is some content." in chunk1.content
#
#     chunk2 = source1.chunks[1]
#     assert chunk2.chunk_num == 2
#     assert chunk2.chunk_amount == 2
#     assert "## Header 2" in chunk2.content
#     assert "More content." in chunk2.content
#
#     # Check the second file
#     source2 = sources[1]
#     assert source2.title == "file2.md"  # File name should match
#     assert len(source2.chunks) == 1  # File 2 has 1 header (so 1 chunk)
#     assert "# Title of File 2" in source2.chunks[0].content
#     assert "Simple text." in source2.chunks[0].content


def test_collect_markdown_files_empty_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        class_instance = MarkdownCrawler(temp_dir)  # Replace with the actual class name
        sources = class_instance.collect_markdown_files(temp_dir)

        assert len(sources) == 0  # No files to process, should return an empty list


def test_collect_markdown_files_no_markdown_files():
    # Create a temp directory with non-markdown files
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "not_a_markdown.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("This is not a markdown file.")

        class_instance = MarkdownCrawler(temp_dir)  # Replace with the actual class name
        sources = class_instance.collect_markdown_files(temp_dir)

        assert (
            len(sources) == 0
        )  # No markdown files to process, should return an empty list


# def test_collect_markdown_files_nested_directories():
#     # Create a directory structure with nested folders
#     with tempfile.TemporaryDirectory() as temp_dir:
#         nested_dir = os.path.join(temp_dir, "nested")
#         os.makedirs(nested_dir)
#
#         file1_path = os.path.join(temp_dir, "file1.md")
#         file2_path = os.path.join(nested_dir, "file2.md")
#
#         content1 = """
# # Header 1
#
# File 1 content.
# """
#         content2 = """
# # Header 2
#
# File 2 content.
# """
#         # Write the contents
#         with (
#             open(file1_path, "w", encoding="utf-8") as f1,
#             open(file2_path, "w", encoding="utf-8") as f2,
#         ):
#             f1.write(content1)
#             f2.write(content2)
#
#         class_instance = MarkdownCrawler(temp_dir)  # Replace with the actual class name
#         sources = class_instance.collect_markdown_files(temp_dir)
#
#         assert (
#                 len(sources) == 2
#         )  # Two files should be processed (one in root and one in nested dir)
#
#         # Validate the titles of the sources
#         assert sources[0].title == "file1.md"
#         assert sources[1].title == "file2.md"
#
#         # Validate the content of the first file
#         assert len(sources[0].chunks) == 1
#         assert "File 1 content." in sources[0].chunks[0].content
#
#         # Validate the content of the second file
#         assert len(sources[1].chunks) == 1
#         assert "File 2 content." in sources[1].chunks[0].content
