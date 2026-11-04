<?php

namespace App\Http\Controllers;

use App\Models\SearchHistory;
use Illuminate\Http\Client\ConnectionException;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;

class ChatbotController extends Controller
{
    public function searchRecipes(Request $request): JsonResponse
    {
        $validated = $request->validate(['q' => ['required', 'string', 'min:2', 'max:300']]);

        try {
            $response = Http::acceptJson()->connectTimeout(5)->timeout(30)->get(
                rtrim((string) config('services.chatbot.url'), '/').'/api/recipes/search',
                $validated,
            );
        } catch (ConnectionException) {
            return response()->json(['message' => 'Layanan resep Python belum berjalan.', 'recipes' => []], 503);
        }

        $result = $response->json() ?? ['message' => 'Respons pencarian tidak valid.', 'recipes' => []];

        if ($response->successful() && $request->user()) {
            $recipeIds = collect($result['recipes'] ?? [])->pluck('id')->map(fn ($id): string => (string) $id)->values()->all();
            SearchHistory::where('user_id', $request->user()->id)->where('query', $validated['q'])->delete();
            SearchHistory::create([
                'user_id' => $request->user()->id,
                'query' => $validated['q'],
                'recipe_ids' => $recipeIds,
            ]);
        }

        return response()->json($result, $response->status());
    }

    public function recipes(): JsonResponse
    {
        try {
            $response = Http::acceptJson()
                ->connectTimeout(5)
                ->timeout(30)
                ->get(rtrim((string) config('services.chatbot.url'), '/').'/api/recipes');
        } catch (ConnectionException) {
            return response()->json(['message' => 'Layanan resep Python belum berjalan.', 'recipes' => []], 503);
        }

        return response()->json($response->json() ?? ['message' => 'Respons resep tidak valid.', 'recipes' => []], $response->status());
    }

    public function buildEmbeddings(Request $request): JsonResponse
    {
        $configuredToken = (string) config('services.chatbot.embedding_token');
        $providedToken = (string) $request->header('X-Embedding-Token');

        if ($configuredToken === '') {
            return response()->json([
                'message' => 'CHATBOT_EMBEDDING_TOKEN belum diatur di Laravel .env.',
            ], 503);
        }

        if ($providedToken === '' || ! hash_equals($configuredToken, $providedToken)) {
            return response()->json([
                'message' => 'Admin token embedding tidak valid.',
            ], 403);
        }

        try {
            $response = Http::acceptJson()
                ->withHeader('X-Embedding-Token', $configuredToken)
                ->connectTimeout(5)
                ->timeout(300)
                ->post(rtrim((string) config('services.chatbot.url'), '/').'/api/embeddings/build');
        } catch (ConnectionException) {
            return response()->json(['message' => 'Layanan chatbot Python belum berjalan.'], 503);
        }

        return response()->json($response->json() ?? ['message' => 'Respons ingest tidak valid.'], $response->status());
    }

    public function __invoke(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'message' => ['required', 'string', 'min:2', 'max:300'],
            'history' => ['sometimes', 'array', 'max:8'],
            'history.*.role' => ['required', 'in:user,assistant'],
            'history.*.content' => ['required', 'string', 'max:2000'],
        ]);
        $chatbotUrl = rtrim((string) config('services.chatbot.url'), '/');

        try {
            $response = Http::acceptJson()
                ->connectTimeout(5)
                ->timeout(60)
                ->post($chatbotUrl.'/api/chat', $validated);
        } catch (ConnectionException) {
            return response()->json([
                'message' => 'Layanan chatbot Python belum berjalan. Jalankan Flask di port 5001 lalu coba lagi.',
                'recipes' => [],
            ], 503);
        }

        if (! $response->successful()) {
            return response()->json([
                'message' => $response->json('message') ?? 'Layanan chatbot belum berhasil menjawab. Coba lagi.',
                'recipes' => [],
            ], $response->status());
        }

        return response()->json($response->json() ?? [
            'message' => 'Layanan chatbot Python mengembalikan respons yang tidak valid.',
            'recipes' => [],
        ]);
    }
}
