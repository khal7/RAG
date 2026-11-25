from rank_bm25 import BM25Okapi
import re








def tokenize(text: str) -> list[str]:
	words = re.findall(r"\b\w+(?:[-']\w+)*\b", text)

	result: list[str] = []
	for w in words:
		w = w.lower()
		result.append(w)
		if "_" in w:
			result.extend(p for p in w.split("_") if p)
		if "-" in w:
			result.extend(p for p in w.split("-") if p)
	return result




if __name__ == "__main__":
	print(tokenize("How to configure the OpenAI server?"))
	print(tokenize("Set --max-model-len and call get_num_tokens"))