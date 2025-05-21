import os
import tempfile

import pytest

from aidkits.models import CodeChunk, LibrarySource


def test_code_chunk_initialization():
    chunk = CodeChunk(
        title="Section 1",
        content="This is the content of the chunk.",
        length=34,
        chunk_num=1,
        chunk_amount=3,
    )
    assert chunk.title == "Section 1"
    assert chunk.content == "This is the content of the chunk."
    assert chunk.length == 34
    assert chunk.chunk_num == 1
    assert chunk.chunk_amount == 3


def test_code_chunk_markdown_property():
    chunk = CodeChunk(
        title="Section 1",
        content="This is the content of the chunk.",
        length=34,
        chunk_num=1,
        chunk_amount=3,
    )
    expected_markdown = "Section 1\nChunk 1/3\n\nThis is the content of the chunk."
    assert chunk.markdown == expected_markdown


def test_code_chunk_empty_content():
    chunk = CodeChunk(
        title="Empty Content",
        content="",
        length=0,
        chunk_num=1,
        chunk_amount=1,
    )
    expected_markdown = "Empty Content\nChunk 1/1\n\n"
    assert chunk.markdown == expected_markdown


def test_code_chunk_multiple_chunks():
    chunk = CodeChunk(
        title="Part 1",
        content="This is part of the content.",
        length=28,
        chunk_num=2,
        chunk_amount=5,
    )
    expected_markdown = "Part 1\nChunk 2/5\n\nThis is part of the content."
    assert chunk.markdown == expected_markdown


def test_code_chunk_boundary_conditions():
    chunk = CodeChunk(
        title="Final Section",
        content="This is the final chunk.",
        length=25,
        chunk_num=5,
        chunk_amount=5,
    )
    expected_markdown = "Final Section\nChunk 5/5\n\nThis is the final chunk."
    assert chunk.markdown == expected_markdown


@pytest.mark.parametrize(
    "title,content,length,chunk_num,chunk_amount,expected_markdown",
    [
        ("Section A", "Content A", 9, 1, 3, "Section A\nChunk 1/3\n\nContent A"),
        (
            "Intro",
            "This is an introduction.",
            25,
            1,
            1,
            "Intro\nChunk 1/1\n\nThis is an introduction.",
        ),
        ("Middle Section", "", 0, 3, 5, "Middle Section\nChunk 3/5\n\n"),
    ],
)
def test_code_chunk_markdown_parametrize(
    title,
    content,
    length,
    chunk_num,
    chunk_amount,
    expected_markdown,
):
    chunk = CodeChunk(
        title=title,
        content=content,
        length=length,
        chunk_num=chunk_num,
        chunk_amount=chunk_amount,
    )
    assert chunk.markdown == expected_markdown


def test_librarysource_save_json():
    library_source = LibrarySource(
        title="Sample Library",
        chunks=[
            CodeChunk(
                title="Chunk 1",
                content="Sample content 1",
                length=17,
                chunk_num=1,
                chunk_amount=2,
            ),
            CodeChunk(
                title="Chunk 2",
                content="Sample content 2",
                length=17,
                chunk_num=2,
                chunk_amount=2,
            ),
        ],
    )
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        path = temp_file.name
    try:
        library_source.save_json(path)
        assert os.path.exists(path), "JSON file was not saved"
    finally:
        os.remove(path)


def test_librarysource_from_json():
    data = """
    {
        "title": "Sample Library",
        "chunks": [
            {
                "title": "Chunk 1",
                "content": "Sample content 1",
                "length": 17,
                "chunk_num": 1,
                "chunk_amount": 2
            },
            {
                "title": "Chunk 2",
                "content": "Sample content 2",
                "length": 17,
                "chunk_num": 2,
                "chunk_amount": 2
            }
        ]
    }
    """
    with tempfile.NamedTemporaryFile(
        delete=False,
        mode="w",
        encoding="utf-8",
    ) as temp_file:
        temp_file.write(data)
        path = temp_file.name
    try:
        library_source = LibrarySource.from_json(path)
        assert library_source.title == "Sample Library"
        assert len(library_source.chunks) == 2
        assert library_source.chunks[0].title == "Chunk 1"
        assert library_source.chunks[0].content == "Sample content 1"
    finally:
        os.remove(path)
