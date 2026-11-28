from pathlib import Path
from src.chunking.model import MinimalSource


def get_source_text(source: MinimalSource) -> str:
    with open(Path(source.file_path), encoding="utf-8",
              newline="") as f:
        text = f.read()
    return text[source.first_character_index:
                source.last_character_index]
