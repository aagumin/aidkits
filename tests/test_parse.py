import os
import tempfile
from unittest.mock import patch

import pytest

from crawler.models import CodeChunk, LibrarySource
from crawler.parse import run, split_by_headers


@pytest.mark.parametrize(
    "markdown_content, expected_chunks",
    [
        (
            "# Header 1\nContent 1\n# Header 2\nContent 2",
            ["# Header 1\nContent 1", "# Header 2\nContent 2"],
        ),
        (
            "# Header 1\nContent 1\n## Subheader 1\nContent 2",
            ["# Header 1\nContent 1", "## Subheader 1\nContent 2"],
        ),
        ("No headers, only text", ["No headers, only text"]),
    ],
)
def test_split_by_headers(markdown_content, expected_chunks):
    chunks = split_by_headers(markdown_content)
    assert chunks == expected_chunks


def test_library_source_from_json():
    json_data = {
        "title": "example.md",
        "chunks": [
            {
                "title": "Header 1",
                "content": "Content under Header 1",
                "length": 120,
                "chunk_num": 1,
                "chunk_amount": 2,
            },
        ],
    }
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    temp_file.write(bytes(str(json_data).replace("'", '"'), encoding="utf-8"))
    temp_file.close()

    library_source = LibrarySource.from_json(temp_file.name)
    os.unlink(temp_file.name)

    assert library_source.title == "example.md"
    assert len(library_source.chunks) == 1
    assert library_source.chunks[0].title == "Header 1"
    assert library_source.chunks[0].content == "Content under Header 1"


def test_library_source_save_json():
    library_source = LibrarySource(
        title="example.md",
        chunks=[
            CodeChunk(
                title="Header 1",
                content="Content under Header 1",
                length=120,
                chunk_num=1,
                chunk_amount=1,
            ),
        ],
    )

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    temp_file.close()

    try:
        library_source.save_json(temp_file.name)

        with open(temp_file.name) as f:
            saved_data = f.read()

        assert '"title": "example.md"' in saved_data
        assert '"content": "Content under Header 1"' in saved_data
    finally:
        os.unlink(temp_file.name)


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
def mocked_clone_git_repo(markdown_test_repo):
    with patch("crawler.parse.clone_git_repo", return_value=str(markdown_test_repo)):
        yield


def test_run_happy_path(mocked_clone_git_repo):

    repo_url = "https://github.com/example/test_repo.git"

    result = run(repo_url)


    for i in range(len(result)):
        assert isinstance(result[i], LibrarySource)
        assert result[i] == LibrarySource(
            title=f"file{i + 1}.md",
            chunks=[
                CodeChunk(
                    title=f"file{i + 1}.md",
                    content=f"# Header {i + 1}\nContent for file {i + 1}",
                    length=29,
                    chunk_num=1,
                    chunk_amount=1,
                ),
            ],
        )
        assert (
            result[i].chunks[0].content == f"# Header {i + 1}\nContent for file {i + 1}"
        )


def test_run_no_markdown_files_found(mocked_clone_git_repo, tmp_path):
    empty_repo = tmp_path / "empty_repo"
    empty_repo.mkdir()

    with patch("crawler.parse.clone_git_repo", return_value=str(empty_repo)):
        result = run("https://github.com/example/empty_repo.git")

    assert result == []


def test_run_invalid_repo_url():

    with pytest.raises(ValueError, match="Invalid repository URL"):
        run("invalid_url")
