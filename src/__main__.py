import fire
from pathlib import Path
from rank_bm25 import BM25Okapi
from src.retrieval.bm25_index import load_chunks, dump_chunks
from src.retrieval.retriever import search
from src.retrieval.tokenizer import tokenize
from src.chunking.chunker import call_right_chunker
from src.retrieval.dataset import load_dataset
from src.chunking.model import MinimalSearchResults, StudentSearchResults
import json

RAW_DIR = Path("data/raw/vllm-0.10.1")
PROCESSED_DIR = Path("data/processed")
CHUNKS_FILE = PROCESSED_DIR / "chunks.json"


def search_cmd(query: str, k: int = 10) -> None:
    chunks = load_chunks(Path("data/processed/chunks.json"))
    bm25 = BM25Okapi([tokenize(c.content) + tokenize(c.file_path)
                     for c in chunks])
    for s in search(query, bm25, chunks, k):
        print(s)


def index_cmd(max_chunk_size: int = 2000,
              raw_dir: str = str(RAW_DIR)) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    chunks = call_right_chunker(Path(raw_dir), max_chunk_size)
    dump_chunks(chunks, CHUNKS_FILE)
    print(f"Ingestion complete! Indices saved under {PROCESSED_DIR}/")


def search_dataset_cmd(dataset_path: str, k: int = 10,
                       save_directory: str = "data/output") -> None:
    chunks = load_chunks(Path("data/processed/chunks.json"))
    bm25 = BM25Okapi([tokenize(c.content) + tokenize(c.file_path)
                     for c in chunks])
    data = load_dataset(
        Path(dataset_path))
    results = []
    for q in data:
        res = search(q.question, bm25, chunks, k)
        results.append(MinimalSearchResults(question_id=q.question_id,
                                            question=q.question,
                                            retrieved_sources=res))
    output = StudentSearchResults(search_results=results, k=k)
    out_dir = Path(save_directory)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / Path(dataset_path).name

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output.model_dump(), f)
    print(f"Saved student_search_results to {out_file}")


if __name__ == "__main__":
    fire.Fire({"search": search_cmd,
               "index": index_cmd,
               "search_dataset": search_dataset_cmd,
               "evaluate": ...})
