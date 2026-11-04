import re
from typing import Any

from flask import Blueprint, current_app, jsonify, request

from backend.rag.generator import GeminiNotConfiguredError, GeminiRequestError, generate_recipe_reply
from backend.rag.retriever import build_recipe_embeddings, get_recipe_retriever
from backend.rag.vectorstore import has_recipe_embeddings, load_recipe_embeddings


chatbot_blueprint = Blueprint("chatbot", __name__)

RECIPE_KEYWORDS = {
    "resep", "masak", "memasak", "bahan", "menu", "makanan", "masakan",
    "ayam", "telur", "nasi", "tahu", "tempe", "sayur", "kangkung", "kecap",
    "goreng", "rebus", "tumis", "sup", "sambal", "bumbu", "dapur",
}


def is_recipe_question(message: str) -> bool:
    words = set(re.findall(r"[a-zA-ZÀ-ÿ]+", message.lower()))
    return bool(words & RECIPE_KEYWORDS)


@chatbot_blueprint.get("/health")
def health() -> tuple[Any, int]:
    return jsonify({
        "status": "ok",
        "embedding_ready": has_recipe_embeddings(),
    }), 200


@chatbot_blueprint.get("/recipes")
def recipes() -> tuple[Any, int]:
    try:
        documents = load_recipe_embeddings()
    except RuntimeError:
        return jsonify({"message": "MongoDB belum dikonfigurasi.", "recipes": []}), 503

    recipes = [
        {key: value for key, value in recipe.items() if key not in {"embedding_vector", "document"}}
        for recipe in documents
    ]
    return jsonify({"recipes": recipes}), 200


@chatbot_blueprint.get("/recipes/search")
def search_recipes() -> tuple[Any, int]:
    query = request.args.get("q", "").strip()
    if not 2 <= len(query) <= 300:
        return jsonify({"message": "Query harus berisi 2 sampai 300 karakter.", "recipes": []}), 422

    try:
        retriever = get_recipe_retriever()
        results = retriever.search_relevant_recipes(query, top_k=12)
    except RuntimeError:
        return jsonify({"message": "Embedding resep belum tersedia.", "recipes": []}), 503

    recipes = [
        {key: value for key, value in recipe.items() if key not in {"score", "document"}}
        | {"score": recipe["score"]}
        for recipe in results
    ]
    return jsonify({"recipes": recipes}), 200


@chatbot_blueprint.get("/recipes/<recipe_id>")
def recipe(recipe_id: str) -> tuple[Any, int]:
    try:
        match = next((item for item in load_recipe_embeddings() if item.get("id") == recipe_id), None)
    except RuntimeError:
        return jsonify({"message": "MongoDB belum dikonfigurasi."}), 503

    if match is None:
        return jsonify({"message": "Resep tidak ditemukan."}), 404

    return jsonify({key: value for key, value in match.items() if key not in {"embedding_vector", "document"}}), 200


@chatbot_blueprint.post("/embeddings/build")
def build_embeddings() -> tuple[Any, int]:
    expected_token = current_app.config.get("EMBEDDING_ADMIN_TOKEN", "")
    if not expected_token or request.headers.get("X-Embedding-Token") != expected_token:
        return jsonify({"message": "Token ingest tidak valid."}), 403

    try:
        count = build_recipe_embeddings()
        get_recipe_retriever.cache_clear()
    except Exception as error:
        current_app.logger.exception("Embedding build failed: %s", error)
        return jsonify({"message": "Proses embedding gagal."}), 500

    return jsonify({"message": "Embedding berhasil disimpan.", "count": count}), 200


@chatbot_blueprint.post("/chat")
def chat() -> tuple[Any, int]:
    payload = request.get_json(silent=True) or {}

    if not isinstance(payload, dict):
        return jsonify({"message": "Format pesan tidak valid.", "recipes": []}), 422

    message = payload.get("message")
    history = payload.get("history", [])

    if not isinstance(message, str) or not 2 <= len(message.strip()) <= 300:
        return jsonify({"message": "Pesan harus berisi 2 sampai 300 karakter.", "recipes": []}), 422

    if not isinstance(history, list) or len(history) > 8:
        return jsonify({"message": "Riwayat percakapan tidak valid.", "recipes": []}), 422

    valid_roles = {"user", "assistant"}
    for turn in history:
        if (
            not isinstance(turn, dict)
            or turn.get("role") not in valid_roles
            or not isinstance(turn.get("content"), str)
            or len(turn["content"]) > 2000
        ):
            return jsonify({"message": "Format riwayat percakapan tidak valid.", "recipes": []}), 422

    clean_message = message.strip()

    previous_user_message = next(
        (turn["content"] for turn in reversed(history) if turn["role"] == "user"),
        "",
    )
    recipes = []

    if is_recipe_question(clean_message):
        retriever = current_app.extensions.get("recipe_retriever")

        if retriever is None:
            try:
                retriever = get_recipe_retriever()
            except RuntimeError:
                return jsonify({
                    "message": "Embedding resep belum tersedia. Jalankan proses ingest terlebih dahulu.",
                    "recipes": [],
                }), 503
            current_app.extensions["recipe_retriever"] = retriever

        retrieved_recipes = retriever.search_relevant_recipes(
            f"{clean_message} {previous_user_message}", top_k=3
        )
        recipes = [
            {key: value for key, value in recipe.items() if key != "score" and key != "document"}
            for recipe in retrieved_recipes
        ]

    try:
        reply = generate_recipe_reply(clean_message, history, recipes)
    except GeminiNotConfiguredError:
        reply = "Gemini belum dikonfigurasi. Isi GEMINI_API_KEY di backend/.env untuk mengaktifkan jawaban AI."
    except GeminiRequestError as error:
        current_app.logger.warning("Gemini request failed: %s", error)
        reply = "Gemini belum berhasil menjawab saat ini. Coba lagi sebentar lagi."

    return jsonify({"message": reply, "recipes": recipes}), 200
