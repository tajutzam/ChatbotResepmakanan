import os
import re
import secrets
import tempfile
from typing import Any

from flask import Blueprint, current_app, jsonify, request

from backend.rag.generator import GeminiNotConfiguredError, GeminiRequestError, generate_recipe_reply
from backend.rag.retriever import build_recipe_embeddings, get_recipe_retriever, import_recipe_file, update_recipe_embedding
from backend.rag.vectorstore import has_recipe_embeddings, load_recipe_embeddings


chatbot_blueprint = Blueprint("chatbot", __name__)

RECIPE_KEYWORDS = {
    "resep", "masak", "memasak", "bahan", "menu", "makanan", "masakan",
    "ayam", "telur", "nasi", "tahu", "tempe", "sayur", "kangkung", "kecap",
    "goreng", "rebus", "tumis", "sup", "sambal", "bumbu", "dapur", "rencana", "jadwal", "minggu",
}


def is_recipe_question(message: str) -> bool:
    words = set(re.findall(r"[a-zA-ZÀ-ÿ]+", message.lower()))
    return bool(words & RECIPE_KEYWORDS)


def requested_plan_days(message: str) -> int | None:
    lowered_message = message.lower()
    has_plan_intent = re.search(
        r"\b(rencana|jadwal|menu|plan|planning|rekomendasi|dibuat|buatkan|buat)\b",
        lowered_message,
    )
    if not has_plan_intent:
        return None

    match = re.search(r"\b(\d+)\s*hari\b|(?:untuk|selama)\s*(\d+)\s*hari\b", lowered_message)
    if match is None:
        words = {"tiga": 3, "lima": 5, "tujuh": 7}
        match = re.search(r"\b(tiga|lima|tujuh)\b", message.lower())
        return words.get(match.group(1)) if match else 7

    return int(match.group(1) or match.group(2))


@chatbot_blueprint.get("/health")
def health() -> tuple[Any, int]:
    try:
        retriever = get_recipe_retriever()
        return jsonify({"status": "ok", "embedding_ready": True, "count": len(retriever.recipes)}), 200
    except RuntimeError as error:
        return jsonify({"status": "error", "embedding_ready": False, "message": str(error)}), 503


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


def _admin_token_is_valid() -> bool:
    expected_token = current_app.config.get('EMBEDDING_ADMIN_TOKEN', '')
    return bool(expected_token) and request.headers.get('X-Embedding-Token') == expected_token


@chatbot_blueprint.post('/recipes/import')
def import_recipes() -> tuple[Any, int]:
    if not _admin_token_is_valid():
        return jsonify({'message': 'Token admin tidak valid.'}), 403
    uploaded_file = request.files.get('file')
    if uploaded_file is None or not uploaded_file.filename.lower().endswith(('.csv', '.xlsx')):
        return jsonify({'message': 'File harus berformat CSV atau XLSX.'}), 422
    temporary_path = os.path.join(tempfile.gettempdir(), f'recipe-upload-{secrets.token_hex(8)}-{uploaded_file.filename}')
    try:
        uploaded_file.save(temporary_path)
        count = import_recipe_file(temporary_path)
        get_recipe_retriever.cache_clear()
        current_app.extensions.pop('recipe_retriever', None)
    except Exception as error:
        current_app.logger.exception('Recipe import failed: %s', error)
        return jsonify({'message': 'Import resep gagal.'}), 500
    finally:
        if os.path.exists(temporary_path):
            os.remove(temporary_path)
    return jsonify({'message': 'Resep berhasil diimpor dan di-embedding.', 'count': count}), 200


@chatbot_blueprint.patch('/recipes/<recipe_id>')
def update_recipe(recipe_id: str) -> tuple[Any, int]:
    if not _admin_token_is_valid():
        return jsonify({'message': 'Token admin tidak valid.'}), 403
    payload = request.get_json(silent=True) or {}
    fields = [payload.get(key, '').strip() for key in ('title', 'ingredients', 'steps')]
    if not fields[0] or not fields[1]:
        return jsonify({'message': 'Nama dan bahan resep wajib diisi.'}), 422
    try:
        if not update_recipe_embedding(recipe_id, *fields):
            return jsonify({'message': 'Resep tidak ditemukan.'}), 404
        get_recipe_retriever.cache_clear()
        current_app.extensions.pop('recipe_retriever', None)
    except Exception as error:
        current_app.logger.exception('Recipe update failed: %s', error)
        return jsonify({'message': 'Update resep gagal.'}), 500
    return jsonify({'message': 'Resep berhasil diperbarui.'}), 200


@chatbot_blueprint.patch('/recipes/<recipe_id>/photo')
def update_recipe_photo(recipe_id: str) -> tuple[Any, int]:
    if not _admin_token_is_valid():
        return jsonify({'message': 'Token admin tidak valid.'}), 403
    photo_url = request.form.get('photo_url', '').strip()
    if not photo_url:
        return jsonify({'message': 'URL foto wajib diisi.'}), 422
    from backend.rag.vectorstore import update_recipe as update_recipe_document
    if not update_recipe_document(recipe_id, {'photo_url': photo_url}):
        return jsonify({'message': 'Resep tidak ditemukan.'}), 404
    return jsonify({'message': 'Foto resep berhasil diperbarui.'}), 200


@chatbot_blueprint.post("/embeddings/build")
def build_embeddings() -> tuple[Any, int]:
    expected_token = current_app.config.get("EMBEDDING_ADMIN_TOKEN", "")
    if not expected_token or request.headers.get("X-Embedding-Token") != expected_token:
        return jsonify({"message": "Token ingest tidak valid."}), 403

    try:
        count = build_recipe_embeddings()
        get_recipe_retriever.cache_clear()
        current_app.extensions.pop('recipe_retriever', None)
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
    plan_days = requested_plan_days(clean_message)
    if plan_days is None and re.search(r"\b(?:mau|ingin|jadi|buat)\s+(?:yang\s+)?(\d+)\b", clean_message.lower()):
        previous_plan_request = any(
            requested_plan_days(turn["content"]) is not None
            for turn in history
            if turn.get("role") == "user"
        )
        if previous_plan_request:
            plan_days = int(re.search(r"\b(?:mau|ingin|jadi|buat)\s+(?:yang\s+)?(\d+)\b", clean_message.lower()).group(1))
    is_weekly_plan = plan_days is not None

    is_supported_plan = plan_days in {3, 5, 7}
    is_unsupported_plan = plan_days is not None and not is_supported_plan

    if is_unsupported_plan:
        try:
            reply = generate_recipe_reply(clean_message, history, [], True, plan_days)['message']
        except GeminiNotConfiguredError:
            reply = 'Rencana resep hanya bisa dibuat untuk 3, 5, atau 7 hari.'
        except GeminiRequestError as error:
            current_app.logger.warning('Gemini request failed: %s', error)
            reply = 'Rencana resep hanya bisa dibuat untuk 3, 5, atau 7 hari.'
        return jsonify({'message': reply, 'recipes': [], 'plan': []}), 200

    if is_recipe_question(clean_message) or is_weekly_plan:
        retriever = current_app.extensions.get("recipe_retriever")

        if retriever is None:
            try:
                retriever = get_recipe_retriever()
            except RuntimeError as error:
                current_app.logger.exception("Recipe retriever initialization failed")
                return jsonify({
                    "message": str(error),
                    "recipes": [],
                }), 503
            current_app.extensions["recipe_retriever"] = retriever

        if is_supported_plan:
            retrieved_recipes = retriever.recipes[:plan_days]
        elif is_weekly_plan:
            retrieved_recipes = retriever.recipes[:7]
        else:
            retrieved_recipes = retriever.search_relevant_recipes(
                f"{clean_message} {previous_user_message}", top_k=3
            )
        recipes = [
            {key: value for key, value in recipe.items() if key not in {"score", "document", "embedding_vector"}}
            for recipe in retrieved_recipes
        ]

    try:
        generated = generate_recipe_reply(clean_message, history, recipes, is_weekly_plan, plan_days)
        reply = generated['message']
    except GeminiNotConfiguredError:
        reply = "Gemini belum dikonfigurasi. Isi GEMINI_API_KEY di backend/.env untuk mengaktifkan jawaban AI."
    except GeminiRequestError as error:
        current_app.logger.warning("Gemini request failed: %s", error)
        reply = "Gemini belum berhasil menjawab saat ini. Coba lagi sebentar lagi."

    plan = []
    if is_supported_plan:
        days = ['Senin', 'Selasa', 'Rabu', 'Kamis', 'Jumat', 'Sabtu', 'Minggu'][:plan_days]
        plan = [{'day': day, 'recipe': recipe} for day, recipe in zip(days, recipes)]

    return jsonify({'message': reply, 'recipes': recipes, 'plan': plan}), 200
