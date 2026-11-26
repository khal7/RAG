from src.chunking.model import MinimalSource, AnsweredQuestion, StudentSearchResults
from src.retrieval.dataset import load_dataset
import json
from pathlib import Path


def iou(a_start: int, a_end: int, b_start: int, b_end: int) -> float:

    shared = max(0, min(a_end, b_end) - max(a_start, b_start))
    total = (a_end - a_start) + (b_end - b_start) - shared
    if total == 0:
        return 0.0
    return shared / total


def score_question(found: list[MinimalSource],
                   truth: list[MinimalSource],
                   k: int) -> float:
    found_count = 0
    if not truth:
        return 0.0

    for t in truth:
        for f in found[:k]:
            overlap = iou(t.first_character_index,
                          t.last_character_index,
                          f.first_character_index,
                          f.last_character_index)
            if t.file_path == f.file_path and overlap >= 0.05:
                found_count += 1
                break
    return found_count / len(truth)


def recall_at_k(results_path: Path, dataset_path: Path, k: int) -> float:

    score = 0.0
    with open(results_path, 'r', encoding="utf-8") as file:
        data = StudentSearchResults(**json.load(file))

    mine = {d.question_id: d.retrieved_sources for d in data.search_results}
    questions = load_dataset(dataset_path)
    if not questions:
        return 0.0

    for q in questions:
        my_guess = mine.get(q.question_id, [])
        if isinstance(q, AnsweredQuestion):
            score += score_question(my_guess, q.sources, k)
    return score / len(questions)


if __name__ == "__main__":
    print(recall_at_k(
        Path("data/output/search_results/UnansweredQuestions/"
             "dataset_docs_public.json"),
        Path("data/datasets/AnsweredQuestions/dataset_docs_public.json"),
        5))

    # a = MinimalSource(file_path="x.md", first_character_index=0,
    # 		last_character_index=100)
    # b = MinimalSource(file_path="x.md", first_character_index=50,
    # 		last_character_index=150)
    # c = MinimalSource(file_path="y.md", first_character_index=0,
    # 		last_character_index=100)
    # print(score_question([a], [b], 1))  # 1.0
    # print(score_question([c], [b], 1))  # 0.0
