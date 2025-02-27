import os
import tempfile
import pytest
from crowler.parse import split_by_headers, LibrarySource, CodeChunk


@pytest.mark.parametrize(
    "markdown_content, expected_chunks",
    [
        ("# Header 1\nContent 1\n# Header 2\nContent 2",
         ["# Header 1\nContent 1", "# Header 2\nContent 2"]),
        ("# Header 1\nContent 1\n## Subheader 1\nContent 2",
         ["# Header 1\nContent 1", "## Subheader 1\nContent 2"]),
        ("No headers, only text",
         ["No headers, only text"]),
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
                "chunk_amount": 2
            }
        ]
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
                chunk_amount=1
            )
        ]
    )

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    temp_file.close()

    try:
        library_source.save_json(temp_file.name)

        with open(temp_file.name, "r") as f:
            saved_data = f.read()

        assert '"title": "example.md"' in saved_data
        assert '"content": "Content under Header 1"' in saved_data
    finally:
        os.unlink(temp_file.name)
