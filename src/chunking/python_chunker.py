# from pydantic import BaseModel, Field, field_validator, ValidationError
from pathlib import Path
import ast


def find_python_files(root: Path) -> list[Path]:
	paths = []
	for file in root.rglob("*.py"):
		paths.append(file)
	return paths

def split_class_or_function(chunk: str, chunk_size: int) -> list[str]:
	...

def split_statement_chunk(statement: list[str], chunk_size: int) -> list[str]:
	...

def chunk_python_file(file_path: Path, chunk_size: int) -> list[str]:
	code = file_path.read_text()
	node = ast.parse(code)
	lines = code.splitlines()
	chunks: list[str] = []
	statement: list[str] = []
	for n in node.body:
		start = n.lineno
		end = n.end_lineno
		if isinstance(n, ast.FunctionDef) or isinstance(n, ast.ClassDef):
			if statement:
				chunks.append("\n".join(statement))
				statement = []
			if end is None:
				continue
			chunk = "\n".join(lines[start - 1:end])
			if len(chunk) <= chunk_size:
				chunks.append(chunk)
			else:
				res = split_class_or_function(chunk, chunk_size)
				chunks.extend(res)
		else:
			if end is None:
				continue
			chunk = "\n".join(lines[start - 1:end])
			statement.append(chunk)
			if len("\n".join(statement)) > chunk_size:
				res = split_statement_chunk(statement, chunk_size)
				chunks.extend(res)
				statement = []
	if statement:
		chunks.append("\n".join(statement))

	return chunks

root = Path("vllm-0.10.1")
paths = find_python_files(root)

# chunks =
# [chunk_python_file(p) for p in paths]
chunks = chunk_python_file(Path("testt.py"))

for chunk in chunks:
	print(chunk)
	print(len(chunk))


# res = ast.parse(code)
# print(res)
# print(ast.dump(res, indent=1, include_attributes=True))
