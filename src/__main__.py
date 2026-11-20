import fire


def search_cmd(query: str, k: int = 10) -> None:
    print(query, k)


if __name__ == "__main__":
    fire.Fire({"search": search})