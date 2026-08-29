from app.repositories.vector_store import cosine_similarity


def test_identical_vectors_have_similarity_one():
    vector = [1.0, 0.0, 0.0]

    assert cosine_similarity(vector, vector) == 1.0


def test_orthogonal_vectors_have_similarity_zero():
    a = [1.0, 0.0]
    b = [0.0, 1.0]

    assert cosine_similarity(a, b) == 0.0
