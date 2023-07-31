from pathlib import Path


def loadFileAsString(path: Path, errorMessage: str) -> str:
    with open(path) as file:
        try:
            return file.read().strip()
        except Exception as e:
            print(e)
            print(errorMessage)
            exit(1)


def writeToFile(path: Path, content: str, errorMessage: str):
    try:
        if not path.parent.exists():
            path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as file:
            file.write(content)
    except Exception as e:
        print(e)
        print(errorMessage)
        exit(1)
