

from pathlib import Path
from .markdown_chunker import chunk_markdown_file
from .python_chunker import chunk_python_file
from .model import Chunk

def call_right_chunker(root: Path, chunk_size: int) -> list[Chunk]:
	sfx = [".py", ".md", ".txt"]
	path_files = [path for path in root.rglob(
		"*") if path.suffix.lower() in sfx]
	chunks: list[Chunk] = []
	for p in path_files:
		try:
			if p.suffix.lower() == ".py":
				chunks.extend(chunk_python_file(p, chunk_size))
			else:
				chunks.extend(chunk_markdown_file(p, chunk_size))
		except Exception as e:
			print("failed:", p, repr(e))
	return chunks


if __name__ == "__main__":
	chunk_size = 50
	root = Path("data/raw/vllm-0.10.1")
	chunks = call_right_chunker(root, chunk_size)
	print(chunks[0].file_path)
	print(len(chunks))
