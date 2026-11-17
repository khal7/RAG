from src.chunking.chunker import call_right_chunker
from src.retrieval.tokenizer import tokenize
from pathlib import Path
from rank_bm25 import BM25Okapi
import time

if __name__=="__main__":
	start = time.time()
	p = Path("data/raw/vllm-0.10.1")
	chunks = call_right_chunker(p, 2000)
	corpus = [tokenize(c.content) for c in chunks]   # a list of word lists
	print(len(corpus))
	print(len(chunks), "chunks")
	print("time:", round(time.time() - start, 1), "seconds")
	bm25 = BM25Okapi(corpus) 
	print(bm25)