<?php

namespace App\Http\Controllers;

use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Storage;
use Illuminate\View\View;
use Symfony\Component\HttpFoundation\StreamedResponse;

class AdminController extends Controller
{
    public function index(): View
    {
        return view('app', ['page' => 'admin']);
    }

    public function recipes(): JsonResponse
    {
        $response = Http::acceptJson()->timeout(30)->get($this->url().'/api/recipes');

        return response()->json($response->json(), $response->status());
    }

    public function template(): StreamedResponse
    {
        return response()->streamDownload(function (): void {
            echo "id,nama resep,bahan lengkap + takaran,langkah memasak berurut\n";
            echo "contoh-001,Contoh resep,\"1 porsi bahan utama\",\"1. Siapkan bahan. 2. Masak sampai matang.\"\n";
        }, 'template-resep.csv', ['Content-Type' => 'text/csv; charset=UTF-8']);
    }

    public function buildEmbeddings(): JsonResponse
    {
        $response = Http::acceptJson()->withHeader('X-Embedding-Token', $this->token())
            ->timeout(600)->post($this->url().'/api/embeddings/build');

        return response()->json($response->json(), $response->status());
    }

    public function import(Request $request): JsonResponse
    {
        $validated = $request->validate(['file' => ['required', 'file', 'mimes:csv,txt,xlsx', 'max:20480']]);
        $response = Http::acceptJson()->withHeader('X-Embedding-Token', $this->token())->attach(
            'file',
            file_get_contents($validated['file']->getRealPath()),
            $validated['file']->getClientOriginalName(),
        )->timeout(600)->post($this->url().'/api/recipes/import');

        return response()->json($response->json(), $response->status());
    }

    public function update(Request $request, string $recipeId): JsonResponse
    {
        $validated = $request->validate([
            'title' => ['required', 'string', 'max:255'],
            'ingredients' => ['required', 'string'],
            'steps' => ['nullable', 'string'],
        ]);
        $response = Http::acceptJson()->withHeader('X-Embedding-Token', $this->token())
            ->timeout(180)->patch($this->url().'/api/recipes/'.$recipeId, $validated);

        return response()->json($response->json(), $response->status());
    }

    public function photo(Request $request, string $recipeId): JsonResponse
    {
        $validated = $request->validate(['photo' => ['required', 'image', 'mimes:jpg,jpeg,png,webp', 'max:5120']]);
        $path = $validated['photo']->store('recipes', 'public');
        $photoUrl = Storage::disk('public')->url($path);
        $response = Http::acceptJson()->withHeader('X-Embedding-Token', $this->token())
            ->asForm()->timeout(60)->patch($this->url().'/api/recipes/'.$recipeId.'/photo', ['photo_url' => url($photoUrl)]);

        return response()->json($response->json(), $response->status());
    }

    private function url(): string
    {
        return rtrim((string) config('services.chatbot.url'), '/');
    }

    private function token(): string
    {
        return (string) config('services.chatbot.embedding_token');
    }
}
