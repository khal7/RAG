# from pydantic import BaseModel, Field, field_validator, ValidationError
from pathlib import Path
import ast


def find_python_files(root: Path) -> list[Path]:
    paths = []
    for file in root.rglob("*.py"):
        paths.append(file)
    return paths


def split_class_or_function(chunk: str, chunk_size: int) -> list[str]:
    i = 0
    chunk_len = len(chunk)
    chunks: list[str] = []
    while i < chunk_len:
        chunks.append(chunk[i:i + chunk_size])
        i += chunk_size
    return chunks


def split_statement_chunk(
        statement: list[str], chunk_size: int
) -> list[str]:
    strings = "\n".join(statement)
    return (split_class_or_function(strings, chunk_size))

def between_nodes(start_line: int, end_line: int, lines: list[str]) -> str:
    gap = lines[end_line: start_line - 1]
    return "\n".join(gap) + ("\n" if gap else "")


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


def chunk_python_file(file_path: Path, chunk_size: int) -> list[str]:
    code = file_path.read_text()
    node = ast.parse(code)
    lines = code.splitlines()
    chunks: list[str] = []
    accum_chunk = ""
    if len(code) <= chunk_size:
        return [code]
    end = 0
    for n in node.body:
        start = n.lineno
        btw_node = between_nodes(start, end, lines)
        temp_chunk = ""
        if isinstance(n, ast.FunctionDef) or isinstance(n, ast.ClassDef):
            if n.end_lineno is None:
                continue
            end = n.end_lineno
            node_source = "\n".join(lines[start - 1: end])
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
            node_source = "\n".join(lines[start - 1: end])
            temp_chunk = btw_node + node_source
            accum_chunk = get_statements(temp_chunk, accum_chunk, chunks, chunk_size)

    if accum_chunk:
        chunks.append(accum_chunk)

    return chunks


root = Path("vllm-0.10.1")
paths = find_python_files(root)

# chunks =
# [chunk_python_file(p) for p in paths]
chunks = chunk_python_file(Path("testt.py"), 1500)

for chunk in chunks:
    print(chunk)
    print(len(chunk))


# res = ast.parse(code)
# print(res)
# print(ast.dump(res, indent=1, include_attributes=True))
