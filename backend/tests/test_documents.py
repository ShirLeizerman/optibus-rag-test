from app.repositories.documents import DocumentRepository


def test_load_documents():
    repository = DocumentRepository("data/documents.json")

    documents = repository.get_all()

    assert len(documents) == 15
    assert documents[0].id == "planning_1"
