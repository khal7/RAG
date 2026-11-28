
from typing import Any
from transformers import AutoTokenizer, AutoModelForCausalLM
import re

MODEL_NAME = "Qwen/Qwen3-0.6B"
SYSTEM_PROMPT = (
    "You answer questions about the vLLM project. Use ONLY the "
    "context provided. If the context does not contain the answer, "
    "say that you could not find it. Be concise. "
    "Answer in one or two full sentences. If the question asks for a command, "
    "give the full command."
)


def load_model() -> tuple[Any, Any]:

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

    return (tokenizer, model)

    # intpus = tokenizer(query + "\n" + "\n".join(top_chunks))
    # model_result = model.generate(**inputs)


def generate_answer(tokenizer: Any, model: Any,
                    question: str, top_chunks: list[str],
                    max_new_tokens: int = 256) -> str:
    context = "\n\n---\n\n".join(top_chunks)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",
         "content": f"Context:\n{context}\n\nQuestion: {question}"},
    ]
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True,
        enable_thinking=False)

    inputs = tokenizer(prompt, return_tensors="pt")
    inputs_len = inputs["input_ids"].shape[1]

    model_result = model.generate(
        **inputs, max_new_tokens=max_new_tokens, do_sample=False)
    decode = tokenizer.decode(
        model_result[0][inputs_len:], skip_special_tokens=True)
    decode = re.sub(r"<think>.*?</think>", "", decode, flags=re.S)

    return decode.strip()


if __name__ == "__main__":
    # import time
    # start = time.time()
    # tokenizer, model = load_model()
    # print("loaded in", round(time.time() - start, 1), "seconds")
    tok, model = load_model()
    print(generate_answer(tok, model, "What is the capital of France?",
                          ["Paris is the capital of France."]))
