
import json
from src.chunking.model import Chunk
from pathlib import Path


def load_chunks(path: Path) -> list[Chunk]:
    with open(path, 'r', encoding="utf-8") as file:
        data = json.load(file)
    return [Chunk(**d) for d in data]


def dump_chunks(chunks: list[Chunk], path: Path) -> None:

    with open(path, 'w', encoding='utf-8') as file:
        json.dump([c.model_dump() for c in chunks], file)


# if __name__ == "__main__":
#     start = time.time()
#     p = Path("data/raw/vllm-0.10.1")
#     chunks = call_right_chunker(p, 2000)
#     corpus = [tokenize(c.content) for c in chunks]   # a list of word lists

#     print("time:", round(time.time() - start, 1), "seconds")
#     bm25 = BM25Okapi(corpus)

#     query = "How to configure the OpenAI server?"

#     Path("data/processed").mkdir(parents=True, exist_ok=True)
#     path_dump_file = "data/processed/chunks.json"

#     dump_chunks(path_dump_file)
#     loaded_chunks = load_chunks(path_dump_file)
#     for s in search("How to configure the OpenAI server?", bm25, chunks, 5):
#         print(s)
    # print(len(loaded_chunks))
    # print(loaded_chunks[0].file_path)
    # print(loaded_chunks == chunks)

    # for i in top:
    # 	c = chunks[i]
    # 	print(round(scores[i], 2), c.file_path, c.char_start, c.char_end)
    # 	print(repr(c.content[:100]))
    # 	print("-" * 50)
