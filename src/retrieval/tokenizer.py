from rank_bm25 import BM25Okapi
import re








def tokenize(text: str) -> list[str]:
	words = re.findall(r"\b\w+(?:[-']\w+)*\b", text)
	return [w.lower() for w in words]




if __name__ == "__main__":
    print(tokenize("How to configure the OpenAI server?"))
    print(tokenize("Set --max-model-len and call get_num_tokens"))