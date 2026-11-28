import fire
import json
import sys
from pathlib import Path
from rank_bm25 import BM25Okapi
from src.retrieval.bm25_index import load_chunks, dump_chunks
from src.retrieval.retriever import search
from src.retrieval.tokenizer import tokenize
from src.chunking.chunker import call_right_chunker
from src.retrieval.dataset import load_dataset
from src.chunking.model import (MinimalSearchResults,
                                MinimalAnswer, StudentSearchResults,
                                StudentSearchResultsAndAnswer)
from src.evaluation import recall_at_k
from pydantic import ValidationError
from src.generation.context import get_source_text
from src.generation.qwen import generate_answer, load_model
from tqdm import tqdm


RAW_DIR = Path("data/raw/vllm-0.10.1")
PROCESSED_DIR = Path("data/processed")
CHUNKS_FILE = PROCESSED_DIR / "chunks.json"


def search_cmd(query: str, k: int = 10) -> None:
    if not query.strip():
        print("Error: empty query", file=sys.stderr)
        return
    if k <= 0:
        print("Error: k must be positive", file=sys.stderr)
        return
    try:
        chunks = load_chunks(Path("data/processed/chunks.json"))
    except FileNotFoundError:
        print("Error: run index first", file=sys.stderr)
        return
    bm25 = BM25Okapi([tokenize(c.content) + tokenize(c.file_path)
                      for c in chunks])
    for s in search(query, bm25, chunks, k):
        print(s)


def index_cmd(max_chunk_size: int = 2000,
              raw_dir: str = str(RAW_DIR)) -> None:
    if not 1 <= max_chunk_size <= 2000:
        print("Error: max_chunk_size must be between 1 and 2000",
              file=sys.stderr)
        return
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    chunks = call_right_chunker(Path(raw_dir), max_chunk_size)
    dump_chunks(chunks, CHUNKS_FILE)
    print(f"Ingestion complete! Indices saved under {PROCESSED_DIR}/")


def search_dataset_cmd(dataset_path: str, k: int = 10,
                       save_directory: str = "data/output") -> None:
    try:
        chunks = load_chunks(Path("data/processed/chunks.json"))
    except FileNotFoundError:
        print("Error: run index first", file=sys.stderr)
        return
    bm25 = BM25Okapi([tokenize(c.content) + tokenize(c.file_path)
                      for c in chunks])
    try:

        data = load_dataset(
            Path(dataset_path))
    except FileNotFoundError as e:
        print(f"Error: file not found: {e.filename}", file=sys.stderr)
        return
    except (json.JSONDecodeError, ValidationError):
        print("Error: malformed dataset file", file=sys.stderr)
        return
    results = []
    for q in tqdm(data):
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


def evaluate_cmd(student_search_results_path: str,
                 dataset_path: str) -> None:
    try:
        for k in (1, 3, 5, 10):
            value = recall_at_k(
                Path(student_search_results_path), Path(dataset_path), k)
            print(f"Recall@{k}: {value:.3f}")
    except FileNotFoundError as e:
        print(f"Error: file not found: {e.filename}", file=sys.stderr)
    except (FileExistsError, json.JSONDecodeError, ValidationError):
        print("Error: malformed JSON file", file=sys.stderr)


def answer_cmd(query: str, k: int = 5) -> None:
    if k <= 0:
        print("Error: k must be positive", file=sys.stderr)
        return
    if not query.strip():
        print("Error: No query provided", file=sys.stderr)
        return
    try:
        chunks = load_chunks(CHUNKS_FILE)
        if not chunks:
            print("Error: run index first", file=sys.stderr)
            return
    except FileNotFoundError:
        print("Error: run index first", file=sys.stderr)
        return

    bm25 = BM25Okapi([tokenize(c.content) + tokenize(c.file_path)
                      for c in chunks])
    sources = search(query, bm25, chunks, k)
    texts = [get_source_text(s) for s in sources[:3]]
    tokenizer, model = load_model()
    answer = generate_answer(tokenizer, model, query, texts)
    print(answer)
    for s in sources:
        print(s.file_path, s.first_character_index,
              s.last_character_index)


def answer_dataset_cmd(student_search_results_path: str,
                       save_directory: str,
                       limit: int = 0) -> None:
    try:
        with open(student_search_results_path, "r", encoding="utf-8") as f:
            data = StudentSearchResults(**json.load(f))
    except (FileNotFoundError, json.JSONDecodeError, ValidationError):
        print("Error: cannot read results file", file=sys.stderr)
        return
    answers: list[MinimalAnswer] = []
    items = data.search_results
    if limit > 0:
        items = items[:limit]
    tokenizer, model = load_model()
    for item in tqdm(items):
        try:
            texts = [get_source_text(s) for s in item.retrieved_sources[:3]]
            text = generate_answer(tokenizer, model, item.question, texts)
            answers.append(
                MinimalAnswer(
                    question_id=item.question_id,
                    question=item.question,
                    retrieved_sources=item.retrieved_sources,
                    answer=text))
        except Exception as e:
            print(f"Error on {item.question_id}: {e!r}", file=sys.stderr)
            answers.append(MinimalAnswer(
                question_id=item.question_id,
                question=item.question,
                retrieved_sources=item.retrieved_sources,
                answer=""))
    out = StudentSearchResultsAndAnswer(search_results=answers, k=data.k)
    Path(save_directory).mkdir(parents=True, exist_ok=True)
    out_path = Path(save_directory) / Path(student_search_results_path).name
    with open(out_path, "w", encoding="utf-8") as f_out:
        json.dump(out.model_dump(), f_out)
    print(f"Saved student_search_results_and_answer to {out_path}")


if __name__ == "__main__":
    fire.Fire({"search": search_cmd,
               "index": index_cmd,
               "search_dataset": search_dataset_cmd,
               "evaluate": evaluate_cmd,
               "answer": answer_cmd,
               "answer_dataset": answer_dataset_cmd})
