import csv
import glob
import os
import re
import zipfile
from functools import lru_cache
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

import numpy as np

from .embedding import generate_embeddings
from .vectorstore import has_recipe_embeddings, load_recipe_embeddings, replace_recipe_embeddings, update_recipe

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


def _read_xlsx(filename: str) -> list[dict[str, str]]:
    namespace = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main', 'rel': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
    with zipfile.ZipFile(filename) as workbook:
        shared = []
        if 'xl/sharedStrings.xml' in workbook.namelist():
            root = ElementTree.fromstring(workbook.read('xl/sharedStrings.xml'))
            shared = [''.join(node.itertext()) for node in root.findall('.//main:si', namespace)]
        sheet = ElementTree.fromstring(workbook.read('xl/worksheets/sheet1.xml'))
        rows = []
        for row in sheet.findall('.//main:row', namespace):
            values = []
            for cell in row.findall('main:c', namespace):
                value = cell.find('main:v', namespace)
                text = '' if value is None else value.text or ''
                if cell.get('t') == 's' and text:
                    text = shared[int(text)]
                values.append(text)
            rows.append(values)
    if not rows:
        return []
    headers = rows[0]
    return [dict(zip(headers, row + [''] * (len(headers) - len(row)))) for row in rows[1:]]


def load_recipe_rows(filename: str) -> list[dict[str, str]]:
    if filename.lower().endswith('.xlsx'):
        return _read_xlsx(filename)
    with open(filename, encoding='utf-8-sig', newline='') as dataset_file:
        return list(csv.DictReader(dataset_file))


def normalize_recipe_rows(rows: list[dict[str, str]], source: str) -> list[dict[str, str]]:
    recipes = []
    for row_number, row in enumerate(rows, start=1):
        recipe_id = (row.get('id') or '').strip()
        title = (row.get('nama resep') or '').strip()
        ingredients = (row.get('bahan lengkap + takaran') or '').strip()
        steps = (row.get('langkah memasak berurut') or '').strip()
        if not recipe_id or not title or not ingredients:
            continue
        recipes.append({'id': recipe_id, 'source': source, 'title': title, 'ingredients': ingredients, 'steps': steps, 'document': f'Nama resep: {title}. Bahan: {ingredients}. Langkah memasak: {steps}'})
    return recipes


def import_recipe_file(filename: str) -> int:
    recipes = normalize_recipe_rows(load_recipe_rows(filename), Path(filename).name)
    if not recipes:
        raise RuntimeError('File tidak berisi resep valid.')
    return replace_recipe_embeddings(recipes)


def build_recipe_embeddings() -> int:
    existing = {recipe['id']: recipe for recipe in load_recipe_embeddings()}
    recipes = {recipe['id']: recipe for recipe in load_recipe_dataset()}
    recipes.update(existing)
    if not recipes:
        raise RuntimeError(f'Dataset resep tidak ditemukan di {DATASET_DIRECTORY}.')
    recipe_list = list(recipes.values())
    vectors = generate_embeddings([recipe['document'] for recipe in recipe_list])
    documents = [{**recipe, 'embedding_vector': vector.tolist()} for recipe, vector in zip(recipe_list, vectors)]
    return replace_recipe_embeddings(documents)


def update_recipe_embedding(recipe_id: str, title: str, ingredients: str, steps: str) -> bool:
    document = f'Nama resep: {title}. Bahan: {ingredients}. Langkah memasak: {steps}'
    return update_recipe(recipe_id, {'title': title, 'ingredients': ingredients, 'steps': steps, 'document': document})


class RecipeRetriever:
    def __init__(self) -> None:
        if not has_recipe_embeddings():
            raise RuntimeError("Embedding resep belum tersedia. Jalankan proses ingest terlebih dahulu.")
        self.recipes = load_recipe_embeddings()
        dimensions = {len(recipe.get('embedding_vector', [])) for recipe in self.recipes}
        if len(dimensions) != 1:
            raise RuntimeError(
                f'Dimensi vector MongoDB bercampur: {sorted(dimensions)}. Jalankan python rebuild_embeddings.py.'
            )
        self.recipe_embeddings = np.array([recipe["embedding_vector"] for recipe in self.recipes])
        expected_dimension = generate_embeddings(['validasi dimensi embedding']).shape[1]
        if self.recipe_embeddings.shape[1] != expected_dimension:
            raise RuntimeError(
                f'Dimensi embedding tidak cocok: database {self.recipe_embeddings.shape[1]}, model {expected_dimension}. Jalankan embedding ulang dari halaman admin.'
            )

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
