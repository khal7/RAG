from src.chunking.chunker import call_right_chunker
from src.retrieval.tokenizer import tokenize
from pathlib import Path
from rank_bm25 import BM25Okapi
from pathlib import Path
import time
import json

if __name__=="__main__":
	start = time.time()
	p = Path("data/raw/vllm-0.10.1")
	chunks = call_right_chunker(p, 2000)
	corpus = [tokenize(c.content) for c in chunks]   # a list of word lists
	

	print("time:", round(time.time() - start, 1), "seconds")
	bm25 = BM25Okapi(corpus)

	query = "How to configure the OpenAI server?"
	scores = bm25.get_scores(tokenize(query))
	top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:5]
	Path("data/processed").mkdir(parents=True, exist_ok=True)

	with open("data/processed/chunks.json", 'w', encoding='utf-8') as file:
		json.dump([c.model_dump() for c in chunks], file)

	with open("data/processed/chunks.json", encoding="utf-8") as f:
		data = json.load(f)
	print(len(data))
	# for i in top:
	# 	c = chunks[i]
	# 	print(round(scores[i], 2), c.file_path, c.char_start, c.char_end)
	# 	print(repr(c.content[:100]))
	# 	print("-" * 50)
	