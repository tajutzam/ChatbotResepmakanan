<?php

use App\Http\Controllers\AuthController;
use App\Http\Controllers\ChatbotController;
use App\Http\Controllers\UserDataController;
use Illuminate\Support\Facades\Route;

foreach ([
    '/' => 'home',
    '/chatbot' => 'chatbot',
    '/rekomendasi' => 'recommendations',
    '/rencana-masak' => 'planner',
    '/dashboard' => 'dashboard',
    '/resep' => 'recipes',
    '/history' => 'history',
    '/login' => 'login',
    '/signup' => 'signup',
] as $path => $page) {
    $route = Route::view($path, 'app', ['page' => $page])->name($page);
    if ($page === 'dashboard') {
        $route->middleware('auth');
    }
}

Route::post('/login', [AuthController::class, 'login'])->name('login.store');
Route::post('/signup', [AuthController::class, 'register'])->name('signup.store');
Route::post('/logout', [AuthController::class, 'logout'])->middleware('auth')->name('logout');

Route::middleware('auth')->group(function (): void {
    Route::get('/api/user-data', [UserDataController::class, 'index'])->name('api.user-data');
    Route::post('/api/favorites/toggle', [UserDataController::class, 'toggleFavorite'])->name('api.favorites.toggle');
    Route::post('/api/history', [UserDataController::class, 'storeHistory'])->name('api.history.store');
    Route::delete('/api/history/{history}', [UserDataController::class, 'deleteHistory'])->name('api.history.delete');
    Route::delete('/api/history', [UserDataController::class, 'clearHistory'])->name('api.history.clear');
});

Route::get('/api/recipes', [ChatbotController::class, 'recipes'])->name('api.recipes');
Route::get('/api/recipes/search', [ChatbotController::class, 'searchRecipes'])->name('api.recipes.search');
Route::post('/chatbot/message', ChatbotController::class)->name('chatbot.message');
Route::post('/chatbot/embeddings/build', [ChatbotController::class, 'buildEmbeddings'])->name('chatbot.embeddings.build');
