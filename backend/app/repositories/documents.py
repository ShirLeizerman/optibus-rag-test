import json
from pathlib import Path

from app.models import Document


class DocumentRepository:
    def __init__(self, path: str):
        self.path = Path(path)

    def get_all(self) -> list[Document]:
        with self.path.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return [Document(**item) for item in data]
