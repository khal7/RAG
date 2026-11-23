
from src.chunking.model import RagDataset, AnsweredQuestion, UnansweredQuestion
from pathlib import Path
import json


def load_dataset(
    path: Path
) -> list[AnsweredQuestion | UnansweredQuestion]:
    with open(path, 'r', encoding="utf-8") as file:
        data = json.load(file)

    return RagDataset(**data).rag_questions


if __name__ == "__main__":
    dataset = load_dataset(
        Path("data/datasets/UnansweredQuestions/dataset_docs_public.json"))
    print(len(dataset))
    print(dataset[0])
