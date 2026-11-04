<?php

namespace App\Http\Controllers;

use App\Models\Favorite;
use App\Models\SearchHistory;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class UserDataController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $user = $request->user();

        return response()->json([
            'favorites' => $user->favorites()->pluck('recipe_id')->values(),
            'history' => $user->searchHistories()->latest()->limit(50)->get(['id', 'query', 'created_at']),
        ]);
    }

    public function toggleFavorite(Request $request): JsonResponse
    {
        $validated = $request->validate(['recipe_id' => ['required', 'string', 'max:255']]);
        $favorite = Favorite::where('user_id', $request->user()->id)
            ->where('recipe_id', $validated['recipe_id'])
            ->first();

        if ($favorite) {
            $favorite->delete();

            return response()->json(['saved' => false]);
        }

        Favorite::create(['user_id' => $request->user()->id, 'recipe_id' => $validated['recipe_id']]);

        return response()->json(['saved' => true]);
    }

    public function storeHistory(Request $request): JsonResponse
    {
        $validated = $request->validate(['query' => ['required', 'string', 'min:2', 'max:300']]);
        SearchHistory::where('user_id', $request->user()->id)->where('query', $validated['query'])->delete();
        SearchHistory::create(['user_id' => $request->user()->id, 'query' => $validated['query']]);
        SearchHistory::where('user_id', $request->user()->id)->latest()->skip(50)->delete();

        return response()->json(['saved' => true]);
    }

    public function deleteHistory(Request $request, int $history): JsonResponse
    {
        $request->user()->searchHistories()->whereKey($history)->delete();

        return response()->json(['deleted' => true]);
    }

    public function clearHistory(Request $request): JsonResponse
    {
        $request->user()->searchHistories()->delete();

        return response()->json(['cleared' => true]);
    }
}
