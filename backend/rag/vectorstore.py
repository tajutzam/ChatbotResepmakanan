import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne

load_dotenv(Path(__file__).resolve().parents[1] / '.env')


@lru_cache(maxsize=1)
def get_collection() -> Any:
    uri = os.getenv("MONGO_URI", "").strip()
    if not uri:
        raise RuntimeError("MONGO_URI belum diatur di environment backend.")

    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    database = client[os.getenv("MONGO_DATABASE", "db_chatbot_menu")]
    return database[os.getenv("MONGO_COLLECTION", "resep_makanan")]


def get_mongo_collection() -> Any:
    return get_collection()


def has_recipe_embeddings() -> bool:
    return get_collection().count_documents({"embedding_vector": {"$exists": True}}, limit=1) > 0


def replace_recipe_embeddings(documents: list[dict[str, Any]]) -> int:
    collection = get_collection()
    if documents:
        collection.bulk_write([
            UpdateOne({'id': document['id']}, {'$set': document}, upsert=True)
            for document in documents
        ])
    return len(documents)


def update_recipe(recipe_id: str, fields: dict[str, Any]) -> bool:
    result = get_collection().update_one({'id': recipe_id}, {'$set': fields})
    return result.matched_count > 0


def load_recipe_embeddings() -> list[dict[str, Any]]:
    return list(get_collection().find({}, {"_id": 0}))
