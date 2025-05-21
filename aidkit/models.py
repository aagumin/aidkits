from typing import List

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
        with open(path, encoding="utf-8") as file:
            json_data = file.read()
        return cls.model_validate_json(json_data)
