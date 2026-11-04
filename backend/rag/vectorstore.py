import os
from functools import lru_cache
from typing import Any

from pymongo import MongoClient


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
    collection.delete_many({})
    if documents:
        collection.insert_many(documents)
    return len(documents)


def load_recipe_embeddings() -> list[dict[str, Any]]:
    return list(get_collection().find({}, {"_id": 0}))
