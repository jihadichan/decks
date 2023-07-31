from pathlib import Path


def loadFileAsString(path: Path, errorMessage: str) -> str:
    with open(path) as file:
        try:
            return file.read().strip()
        except Exception as e:
            print(e)
            print(errorMessage)
            exit(1)
