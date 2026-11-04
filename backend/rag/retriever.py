import csv
import glob
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

from .embedding import generate_embeddings
from .vectorstore import has_recipe_embeddings, load_recipe_embeddings, replace_recipe_embeddings

DATASET_DIRECTORY = Path(__file__).resolve().parents[1] / "dataset"


def load_recipe_dataset() -> list[dict[str, str]]:
    recipes = []
    for filename in sorted(glob.glob(str(DATASET_DIRECTORY / "*.csv"))):
        with open(filename, encoding="utf-8-sig", newline="") as dataset_file:
            for row_number, row in enumerate(csv.DictReader(dataset_file), start=1):
                title = (row.get("nama resep") or "").strip()
                ingredients = (row.get("bahan lengkap + takaran") or "").strip()
                steps = (row.get("langkah memasak berurut") or "").strip()
                if not title or not ingredients:
                    continue
                source = Path(filename).name
                recipes.append({
                    "id": f"{source}-{(row.get('id') or row_number).strip()}",
                    "source": source,
                    "title": title,
                    "ingredients": ingredients,
                    "steps": steps,
                    "document": f"Nama resep: {title}. Bahan: {ingredients}. Langkah memasak: {steps}",
                })
    return recipes


def build_recipe_embeddings() -> int:
    recipes = load_recipe_dataset()
    if not recipes:
        raise RuntimeError(f"Dataset resep tidak ditemukan di {DATASET_DIRECTORY}.")
    vectors = generate_embeddings([recipe["document"] for recipe in recipes])
    documents = [{**recipe, "embedding_vector": vector.tolist()} for recipe, vector in zip(recipes, vectors)]
    return replace_recipe_embeddings(documents)


class RecipeRetriever:
    def __init__(self) -> None:
        if not has_recipe_embeddings():
            raise RuntimeError("Embedding resep belum tersedia. Jalankan proses ingest terlebih dahulu.")
        self.recipes = load_recipe_embeddings()
        self.recipe_embeddings = np.array([recipe["embedding_vector"] for recipe in self.recipes])

    def search_relevant_recipes(self, query_text: str, top_k: int = 3) -> list[dict[str, object]]:
        query_embedding = generate_embeddings([query_text])[0]
        scores = np.dot(self.recipe_embeddings, query_embedding)
        minimum_score = float(os.getenv("RECIPE_MIN_SIMILARITY", "0.2"))
        ignored_words = {"aku", "punya", "ada", "saya", "mau", "ingin", "cari", "carikan", "resep", "masak", "masakan", "menu", "yang", "dan", "dengan", "untuk"}
        query_words = set(re.findall(r"[a-zA-ZÀ-ÿ]+", query_text.lower())) - ignored_words
        results = []
        seen_titles = set()

        for index in np.argsort(scores)[::-1]:
            score = float(scores[index])
            if score < minimum_score or len(results) >= top_k:
                break

            source_recipe = self.recipes[int(index)]
            title = str(source_recipe.get("title", ""))
            searchable_text = f"{title} {source_recipe.get('ingredients', '')}".lower()
            ingredient_matches = query_words & set(re.findall(r"[a-zA-ZÀ-ÿ]+", searchable_text))
            if query_words and not ingredient_matches:
                continue

            title_key = re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()
            if title_key in seen_titles:
                continue
            seen_titles.add(title_key)

            recipe = {key: value for key, value in source_recipe.items() if key != "embedding_vector"}
            results.append({**recipe, "score": score})

        return results


@lru_cache(maxsize=1)
def get_recipe_retriever() -> RecipeRetriever:
    return RecipeRetriever()


def search_relevant_recipes(query_text: str, top_k: int = 3) -> list[dict[str, object]]:
    return get_recipe_retriever().search_relevant_recipes(query_text, top_k)
