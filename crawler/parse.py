import json
import os
import re
import shutil
from functools import cached_property
from pathlib import Path
from typing import List, Optional

from crawler.models import CodeChunk, LibrarySource
from crawler.storage import LocalFileSystem, RemoteGitRepository


class MarkdownCrawler:
    def __init__(
        self,
        repo_url: str,
        output_path: str = "output.json",
        path_prefix: str = None,
    ):
        self.repo_url = repo_url
        self.output_path = output_path
        self.path_prefix = path_prefix

    @cached_property
    def _is_remote(self) -> bool:
        is_remote = (
            True
            if any(
                self.repo_url.startswith(prefix)
                for prefix in ["https://", "http://", "git@", "ssh://"]
            )
            else False
        )
        return is_remote

    def split_markdown_by_headers(self, markdown_text):
        """Splits the Markdown document text by headers (the `#` symbol),
        excluding headers that are inside code blocks (` or `````).
        """
        code_block_pattern = re.compile(
            r"(```.*?```|`.*?`)",
            re.DOTALL,
        )  # Ищет блоки кода (одинарные/тройные)
        header_pattern = re.compile(
            r"^(#{1,6})\s+(.*)",
            re.MULTILINE,
        )  # Ищет заголовки вне блоков

        # Индексы всех блоков кода
        code_blocks = [
            (match.start(), match.end())
            for match in code_block_pattern.finditer(markdown_text)
        ]

        def is_inside_code_blocks(index):
            """Checks if the index is inside a code block."""
            for start, end in code_blocks:
                if start <= index < end:
                    return True
            return False

        headers = [
            (
                match.start(),
                match.group(1),
                match.group(2),
            )
            for match in header_pattern.finditer(markdown_text)
            if not is_inside_code_blocks(match.start())
        ]

        if not headers:
            return [markdown_text]

        chunks = []
        last_index = 0

        for start, header_level, header_text in headers:
            if start > last_index:
                chunks.append(markdown_text[last_index:start].strip())
            last_index = start

        if last_index < len(markdown_text):
            chunks.append(markdown_text[last_index:].strip())

        return chunks

    def collect_markdown_files(self, directory: str) -> List[LibrarySource]:
        """Iterates over the given directory and its subdirectories, collects markdown files,
        and reads them into the LibrarySource structure, splitting by headers.

        :param directory: Path to the root directory
        :return: A list of LibrarySource objects
        """
        library_sources = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".md"):
                    file_path = os.path.join(root, file)
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()
                    chunks = self.split_markdown_by_headers(content)
                    chunk_amount = len(chunks)
                    code_chunks = [
                        CodeChunk(
                            title=f"{file}",
                            content=chunk_content,
                            length=len(chunk_content),
                            chunk_num=chunk_num + 1,
                            chunk_amount=chunk_amount,
                        )
                        for chunk_num, chunk_content in enumerate(chunks)
                    ]
                    library_sources.append(
                        LibrarySource(title=file, chunks=code_chunks),
                    )

        return library_sources

    def work(self) -> Optional[list[LibrarySource]]:
        location = RemoteGitRepository if self._is_remote else LocalFileSystem

        directory_path = location(self.repo_url).fetch()
        try:
            if self.path_prefix:
                directory_path = Path(directory_path) / self.path_prefix

            library_sources = self.collect_markdown_files(directory_path)
            if library_sources:
                with open(self.output_path, "w", encoding="utf-8") as f:
                    json.dump(
                        [lib_source.model_dump() for lib_source in library_sources],
                        f,
                        ensure_ascii=False,
                        indent=4,
                    )
                print(f"JSON saved: {self.output_path}")

            if library_sources and library_sources[0].chunks:
                print(library_sources[0].chunks[0].markdown)

        finally:
            if self._is_remote:
                shutil.rmtree(directory_path)
                print(f"Temporary directory {directory_path} removed.")

        return library_sources
