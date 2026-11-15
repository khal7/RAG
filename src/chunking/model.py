from pydantic import BaseModel, Field, field_validator, ValidationError
from pathlib import Path


class Chunk(BaseModel):
    content: str
    file_path: Path
    char_start: int
    char_end: int
