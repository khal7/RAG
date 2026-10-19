#from pydantic import BaseModel, Field, field_validator, ValidationError
from pathlib import Path
import ast




def find_python_files(root: Path) -> list[Path]:
	paths = []	
	for file in root.rglob("*.py"):
		paths.append(file)
	return paths

def chunk_python_file(file_path: Path) -> list[str]:
	code = file_path.read_text()
	node = ast.parse(code)
	lines = code.splitlines()
	chunks: list[str] = []
	for n in node.body:
		if isinstance(n, ast.FunctionDef):
			start = n.lineno
			end = n.end_lineno
			if end is None:
				continue
			chunk = "\n".join(lines[start - 1:end])
			chunks.append(chunk)
		elif isinstance(n, ast.ClassDef):
			start = n.lineno
			end = n.end_lineno
			if end is None:
				continue
			chunk = "\\n".join(lines[start - 1:end])
			chunks.append(chunk)
	return chunks



root = Path("vllm-0.10.1")
paths = find_python_files(root)

#chunks = 
[chunk_python_file(p) for p in paths]

# res = ast.parse(code)
# print(res)
# print(ast.dump(res, indent=1, include_attributes=True))