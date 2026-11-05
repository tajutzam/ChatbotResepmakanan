import sys
from pathlib import Path

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.rag.retriever import build_recipe_embeddings, get_recipe_retriever


if __name__ == '__main__':
    count = build_recipe_embeddings()
    get_recipe_retriever.cache_clear()
    print(f'Embedding berhasil dibuat ulang untuk {count} resep.')
