import json
import os
from typing import Any

from google import genai
from google.genai import types


SYSTEM_INSTRUCTION = (
    "Kamu adalah Teman Dapur, chatbot resep berbahasa Indonesia. "
    "Klasifikasikan intent sebagai chat, recipe_search, atau meal_plan. "
    "Gunakan hanya fakta resep dari konteks dataset. Jangan mengarang nama, bahan, takaran, atau langkah. "
    "Durasi meal_plan hanya boleh 3, 5, atau 7 hari; selain itu tolak dan kembalikan recipes serta plan kosong. "
    "Untuk meal_plan valid, gunakan resep berbeda dari konteks untuk setiap hari yang diminta. "
    "Balas hanya JSON sesuai schema, tanpa markdown."
)


class GeminiNotConfiguredError(RuntimeError):
    pass


class GeminiRequestError(RuntimeError):
    pass


def generate_recipe_reply(
    message: str,
    history: list[dict[str, str]],
    recipes: list[dict[str, Any]],
    is_weekly_plan: bool = False,
    plan_days: int | None = None,
) -> dict[str, Any]:
    api_key = os.getenv('GEMINI_API_KEY', '').strip()
    if not api_key:
        raise GeminiNotConfiguredError('GEMINI_API_KEY belum diisi di backend/.env.')

    recipe_context = '\n\n'.join(
        '\n'.join([
            f'Resep {index}: {recipe.get("title", "")}',
            f'Sumber: {recipe.get("source", "Dataset resep")}',
            f'Bahan: {recipe.get("ingredients", "")}',
            f'Langkah: {recipe.get("steps", "")}',
        ])
        for index, recipe in enumerate(recipes, start=1)
    )
    conversation = '\n'.join(f'{turn["role"].upper()}: {turn["content"]}' for turn in history)
    prompt = '\n\n'.join(filter(None, [
        'KONTEKS RESEP:\n' + (recipe_context or 'Tidak ada resep relevan.'),
        f'RIWAYAT:\n{conversation}' if conversation else '',
        f'DURASI PLAN: {plan_days or "tidak ada"}',
        f'PESAN PENGGUNA:\n{message}',
    ]))

    try:
        client = genai.Client(api_key=api_key, http_options=types.HttpOptions(timeout=45_000))
        response = client.models.generate_content(
            model=os.getenv('GEMINI_MODEL', 'gemini-2.5-flash'),
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                max_output_tokens=2000,
                response_mime_type='application/json',
                response_schema={
                    'type': 'OBJECT',
                    'properties': {
                        'intent': {'type': 'STRING'},
                        'message': {'type': 'STRING'},
                        'recipes': {'type': 'ARRAY', 'items': {'type': 'OBJECT'}},
                        'plan': {'type': 'ARRAY', 'items': {'type': 'OBJECT'}},
                    },
                    'required': ['intent', 'message', 'recipes', 'plan'],
                },
            ),
        )
    except Exception as error:
        raise GeminiRequestError(f'Tidak dapat menerima jawaban dari Gemini API: {error}') from error

    try:
        result = json.loads(response.text or '{}')
    except json.JSONDecodeError as error:
        raise GeminiRequestError('Gemini mengembalikan JSON tidak valid.') from error

    if not isinstance(result, dict) or not isinstance(result.get('message'), str):
        raise GeminiRequestError('Format respons Gemini tidak valid.')

    return {
        'intent': result.get('intent', 'chat'),
        'message': result['message'].strip(),
        'recipes': result.get('recipes', []) if isinstance(result.get('recipes'), list) else [],
        'plan': result.get('plan', []) if isinstance(result.get('plan'), list) else [],
    }
