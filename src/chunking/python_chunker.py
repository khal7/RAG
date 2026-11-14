from pydantic import BaseModel, Field, field_validator, ValidationError
from pathlib import Path
import ast


class Chunk(BaseModel):
	content: str
	file_path: Path
	char_start: int
	char_end: int


def find_python_files(root: Path) -> list[Path]:
	paths = []
	for file in root.rglob("*.py"):
		paths.append(file)
	return paths


def split_class_or_function(chunk: str, chunk_size: int) -> list[str]: # 100
	i = 0
	chunk_len = len(chunk)
	chunk_lines = chunk.splitlines(keepends=True)
	chunks: list[str] = []
	res = ""
	for line in chunk_lines:
		if len(line) > chunk_size:
			if res:
				chunks.append(res)
				res = ""
			i = 0
			while i < chunk_len:
				chunks.append(line[i:i + chunk_size])
				i += chunk_size
		elif len(res) + len(line) <= chunk_size:
			res += line
		elif len(res) + len(line) > chunk_size:
			chunks.append(res)
			if len(line) > chunk_size:
				i = 0
				while i < len(line):
					chunks.append(line[i:i + chunk_size])
					i += chunk_size
			res = line
	if res:
		chunks.append(res)
	return chunks


def split_statement_chunk(
		statement: list[str], chunk_size: int
) -> list[str]:
	strings = "\n".join(statement)
	return (split_class_or_function(strings, chunk_size))

def between_nodes(start_line: int, end_line: int, lines: list[str]) -> str:
    gap = lines[end_line: start_line - 1]
    return "".join(gap)

def get_statements(
	temp_chunk: str,
	accum_chunk: str,
	chunks: list[str],
	chunk_size: int
) -> str:
	# Case 1: The statement itself is oversized.
	if len(temp_chunk) > chunk_size:
		if accum_chunk:
			chunks.append(accum_chunk)

		chunks.extend(split_statement_chunk([temp_chunk], chunk_size))
		return ""

	# Case 2: The statement fits in the current accumulated chunk.
	if len(accum_chunk) + len(temp_chunk) <= chunk_size:
		return accum_chunk + temp_chunk

	# Case 3: It doesn't fit in the current accumulated chunk.
	if accum_chunk:
		chunks.append(accum_chunk)

	return temp_chunk


def get_offset(lines: list[str]) -> list[int]:

	res: list[int] = []
	previous = 0
	for i in range(len(lines)):
		res.append(previous)
		previous += len(lines[i])
	res.append(previous)
	return res


def chunk_python_file(file_path: Path, chunk_size: int=2000) -> list[Chunk]:
	code = file_path.read_text()
	node = ast.parse(code)
	lines = code.splitlines(keepends=True)
	offsets = get_offset(lines)
	chunks: list[str] = []
	accum_chunk = ""
	if len(code) <= chunk_size:
		return [Chunk(content=code, char_start=0, char_end=len(code), file_path=str(file_path))]
	end = 0
	for n in node.body:
		start = n.lineno
		btw_node = between_nodes(start, end, lines)
		temp_chunk = ""
		if isinstance(n, ast.FunctionDef) or isinstance(n, ast.ClassDef):
			if n.end_lineno is None:
				continue
			end = n.end_lineno
			node_source = code[offsets[start - 1]:offsets[end]]
			temp_chunk = btw_node + node_source
			if len(temp_chunk) > chunk_size:
				if accum_chunk:
					chunks.append(accum_chunk)
				chunks.extend(split_class_or_function(temp_chunk, chunk_size))
				accum_chunk = ""
			else:
				if len(accum_chunk) + len(temp_chunk) <= chunk_size:
					accum_chunk += temp_chunk
				else:
					if accum_chunk:
						chunks.append(accum_chunk)
					accum_chunk = temp_chunk
		else:
			if n.end_lineno is None:
				continue
			end = n.end_lineno
			node_source = code[offsets[start - 1]:offsets[end]]
			temp_chunk = btw_node + node_source
			accum_chunk = get_statements(
				temp_chunk, accum_chunk, chunks, chunk_size)

	if accum_chunk:
		chunks.append(accum_chunk)
	pos = 0
	result = []
	for text in chunks:
		result.append(Chunk(file_path=str(file_path),
							char_start=pos,
							char_end=pos + len(text),
							content=text))
		pos += len(text)
	#print(result[-1].char_end, len(code))
	return result


root = Path("vllm-0.10.1")
paths = find_python_files(root)
failed = []
# chunks =
# [chunk_python_file(p) for p in paths]

for p in paths:
	try:
		chunks = chunk_python_file(Path(p), 2000)
		text = Path(p).read_text(encoding="utf-8")
	except Exception as e:
		failed.append((p, repr(e)))
		continue
print("files:", len(paths), "failed:", len(failed))
for p, why in failed:
	print(p, why)
	# for chunk in chunks:
	# 	print(chunk.content)
	# 	print(len(chunk.content))
	# 	print("*" * 100)
	# 	if (len(chunk.content) > 1000):
	# 		raise ValueError


# chunks = chunk_python_file(Path("testt.py"), 1000)
# text = Path("testt.py").read_text(encoding="utf-8")

# for c in chunks:
#     assert text[c.char_start:c.char_end] == c.content

# assert chunks[0].char_start == 0
# for a, b in zip(chunks, chunks[1:]):
#     assert a.char_end == b.char_start
# assert chunks[-1].char_end == len(text)

# print("ok")
# res = ast.parse(code)
# print(res)
# print(ast.dump(res, indent=1, include_attributes=True))
