#from pydantic import BaseModel, Field, field_validator, ValidationError
from pathlib import Path
import ast




def find_python_files(root: Path) -> list[Path]:
	paths = []	
	for file in root.rglob("*.py"):
		paths.append(file)
	return paths


def chunk_python_file(file_path: Path) -> None:
	code = file_path.read_text()
	node = ast.parse(code)
	for n in ast.walk(node):
		print(n)


root = Path("vllm-0.10.1")
paths = find_python_files(root)

#chunks = 
[chunk_python_file(p) for p in paths]

# res = ast.parse(code)
# print(res)
# print(ast.dump(res, indent=1, include_attributes=True))