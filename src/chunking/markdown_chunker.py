
from .model import Chunk
from markdown_it import MarkdownIt
from pathlib import Path
from collections import Counter

from src.chunking.python_chunker import get_offset, split_class_or_function


def find_python_files(root: Path) -> list[Path]:
	paths = []
	for file in root.rglob("*.py"):
		paths.append(file)
	return paths


def get_offset(lines: list[str]) -> list[int]:

	res: list[int] = []
	previous = 0
	for i in range(len(lines)):
		res.append(previous)
		previous += len(lines[i])
	res.append(previous)
	return res


def chunk_markdown_file(file_path: Path, chunk_size: int = 2000) -> list[Chunk]:

	chunks: list[str] = []
	with open(file_path, encoding="utf-8", newline="") as f:
		text = f.read()
	if not text:
		return []
	text_lines = text.splitlines(keepends=True)
	offsets = get_offset(text_lines)
	tokens = MarkdownIt().parse(text)
	
	headings = [t.map[0] for t in tokens if t.type == "heading_open"]
	cuts = sorted(set([0] + headings + [len(text_lines)]))

	accum = ""
	for i in range(len(cuts) - 1):

		chunk = text[offsets[cuts[i]]:offsets[cuts[i + 1]]]
		if len(chunk) > chunk_size:
			if accum:
				chunks.append(accum)
				accum = ""
			chunks.extend(split_class_or_function(chunk, chunk_size))
		elif len(accum) + len(chunk) <= chunk_size:
			accum += chunk
		else:
			chunks.append(accum)
			accum = chunk
	if accum:
		chunks.append(accum)

	pos = 0
	result: list[Chunk] = []
	for content in chunks:
		result.append(Chunk(file_path=str(file_path),
							char_start=pos,
							char_end=pos + len(content),
							content=content))
		pos += len(content)
	return result

if __name__ == "__main__":
    root = Path("vllm-0.10.1")
    size = 2000
    paths = [p for p in root.rglob("*")
             if p.suffix.lower() in {".md", ".txt"}]
    failed = []

    for p in paths:
        try:
            chunks = chunk_markdown_file(p, size)
            with open(p, encoding="utf-8", newline="") as f:
                text = f.read()
            if not chunks:
                continue
            if any(text[c.char_start:c.char_end] != c.content
                   for c in chunks):
                failed.append((p, "not an exact copy"))
            elif chunks[0].char_start != 0:
                failed.append((p, "first chunk does not start at 0"))
            elif any(a.char_end != b.char_start
                     for a, b in zip(chunks, chunks[1:])):
                failed.append((p, "gap between chunks"))
            elif chunks[-1].char_end != len(text):
                failed.append((p, "last chunk ends too early"))
            elif any(len(c.content) > size for c in chunks):
                failed.append((p, "chunk too big"))
        except Exception as e:
            failed.append((p, repr(e)))

    print("files:", len(paths), "failed:", len(failed))
    for p, why in failed[:10]:
        print(p, why[:100])
