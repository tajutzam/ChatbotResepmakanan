<?php

use Illuminate\Support\Facades\Route;

foreach (['/' => 'home', '/chatbot' => 'chatbot', '/rekomendasi' => 'recommendations', '/rencana-masak' => 'planner', '/dashboard' => 'dashboard', '/resep' => 'recipes', '/history' => 'history', '/login' => 'login', '/signup' => 'signup'] as $path => $page) {
    Route::view($path, 'app', ['page' => $page])->name($page);
}
