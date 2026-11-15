
from .model import Chunk
from markdown_it import MarkdownIt
from pathlib import Path

from src.chunking.python_chunker import get_offset, split_class_or_function


def split_paragraph() -> str:
	...


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
	# for t in tokens[:5]:
	# 	print(t.type, t.tag, t.map, t.level)

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

	# for token in tokens:

	# 	if token.block and token.map is not None:

	# 		mp = token.map
	# 		print("".join(text_lines[mp[0]:mp[1]]))

	# if len(code) <= chunk_size:
	# 	return [Chunk(content=code, char_start=0, char_end=len(code), file_path=str(file_path))]


p = Path("README.md")
chunks = chunk_markdown_file(p, 100)
# for c in chunks:

# 	print(c)
# 	print(f"---------- len: {len(c)}")
# 	print("*" * 60)
text = open(p, encoding="utf-8", newline="").read()
for c in chunks:
	assert text[c.char_start:c.char_end] == c.content
assert chunks[0].char_start == 0
for a, b in zip(chunks, chunks[1:]):
	assert a.char_end == b.char_start
assert chunks[-1].char_end == len(text)
print("ok")
# for c in chunks:
#     assert text[c.char_start:c.char_end] == c.content
# assert chunks[0].char_start == 0
# for a, b in zip(chunks, chunks[1:]):
#     assert a.char_end == b.char_start
# assert chunks[-1].char_end == len(text)
# print("ok")
