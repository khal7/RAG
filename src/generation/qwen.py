

from transformers import AutoTOkenizer






def load_model(query: str) -> None:
	
	tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
	query = tokenizer()

