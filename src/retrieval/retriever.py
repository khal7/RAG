from src.chunking.model import Chunk
from src.chunking.model import MinimalSource
from src.retrieval.tokenizer import tokenize
from rank_bm25 import BM25Okapi


def search(query: str, bm25: BM25Okapi,
           chunks: list[Chunk],
           k: int) -> list[MinimalSource]:
    if k <= 0:
        return []
    scores = bm25.get_scores(tokenize(query))
    top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]

    return [
        MinimalSource(
            file_path=chunks[i].file_path,
            first_character_index=chunks[i].char_start,
            last_character_index=chunks[i].char_end) for i in top]
