import os
import re
import shutil
import tempfile
from typing import List

from git import Repo
from pydantic import BaseModel


class CodeChunk(BaseModel):
    title: str
    content: str
    length: int
    chunk_num: int
    chunk_amount: int

    @property
    def markdown(self) -> str:
        text = f"{self.title}\n"
        text += f"Chunk {self.chunk_num}/{self.chunk_amount}\n\n"
        text += self.content
        return text


class LibrarySource(BaseModel):
    title: str
    chunks: List[CodeChunk]

    def save_json(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as file:
            file.write(self.model_dump_json(indent=4))

    @classmethod
    def from_json(cls, path: str) -> "LibrarySource":
        with open(path, "r", encoding="utf-8") as file:
            json_data = file.read()
        return cls.model_validate_json(json_data)


def clone_git_repo(repo_url: str) -> str:
    """
    Clones a Git repository from the given URL into a temporary directory.

    :param repo_url: URL of the repository (GitHub, Bitbucket, or other remote repositories)
    :return: The path to the temporary directory where the repository was cloned
    """
    temp_dir = tempfile.mkdtemp()
    try:
        print(f"Cloning repository {repo_url} into {temp_dir}...")
        Repo.clone_from(repo_url, temp_dir)
        return temp_dir
    except Exception as e:
        shutil.rmtree(temp_dir)
        raise RuntimeError(f"Failed to clone repository: {e}")


def split_by_headers(content: str) -> List[str]:
    """
    Splits the text into chunks by headers starting with symbols #, ##, or ###.

    Headers add their chunk number.
    If there is no newline after the header, do not extract its content.

    :param content: The string content of a markdown file
    :return: A list of chunks, each starting with a header
    """
    header_pattern = re.compile(r"^(#+ .+)", re.MULTILINE)
    matches = list(header_pattern.finditer(content))
    if not matches:
        return [content.strip()]

    chunks = []
    for i, match in enumerate(matches):
        start_idx = match.start()
        end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(content)
        header = match.group(1)
        chunk_content = content[start_idx:end_idx].strip()
        if '\n' not in chunk_content[len(header):]:
            continue

        header_with_chunk = f"{header}"
        chunk = f"{header_with_chunk}\n{chunk_content[len(header):].strip()}"
        chunks.append(chunk)

    return chunks


def collect_markdown_files(directory: str) -> List[LibrarySource]:
    """
    Iterates over the given directory and its subdirectories, collects markdown files,
    and reads them into the LibrarySource structure, splitting by headers.

    :param directory: Path to the root directory
    :return: A list of LibrarySource objects
    """
    library_sources = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                chunks = split_by_headers(content)
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
                library_sources.append(LibrarySource(title=file, chunks=code_chunks))

    return library_sources
