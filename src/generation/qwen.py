
from typing import Any
from transformers import AutoTokenizer, AutoModelForCausalLM


MODEL_NAME = "Qwen/Qwen3-0.6B"


def load_model() -> tuple[Any, Any]:

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

    return (tokenizer, model)

    # intpus = tokenizer(query + "\n" + "\n".join(top_chunks))
    # model_result = model.generate(**inputs)


def generate_answer(tokenizer: Any, model: Any,
                    question: str, top_chunks: list[str]) -> str:

    inputs = tokenizer(question + "\n" + "\n".join(top_chunks), return_tensors="pt")
    inputs_len = inputs["input_ids"].shape[1]
    model_result = model.generate(**inputs)
    decode = tokenizer.decode(
        model_result[0][inputs_len:], skip_special_tokens=True)
    return decode


if __name__ == "__main__":
    import time
    start = time.time()
    tokenizer, model = load_model()
    print("loaded in", round(time.time() - start, 1), "seconds")
