import os
from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    model_name = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
    print(f"Memuat model embedding {model_name}...")

    return SentenceTransformer(model_name)


def generate_embeddings(texts: list[str]) -> np.ndarray:
    return get_embedding_model().encode(
        texts,
        batch_size=8,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
