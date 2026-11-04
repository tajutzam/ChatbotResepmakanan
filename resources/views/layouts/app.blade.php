<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#ed7626">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <meta name="description" content="Temukan inspirasi resep dari bahan yang ada di dapurmu bersama DapurKita.">
    <title>DapurKita — Teman masak sehari-hari</title>
    <link rel="stylesheet" href="{{ asset('css/app.css') }}">
    <script>window.recipeData = @json(config('recipes'));</script>
    <script src="{{ asset('js/app.js') }}" defer></script>
</head>
<body data-page="{{ $page }}" data-authenticated="{{ auth()->check() ? '1' : '0' }}">
    @include('partials.sidebar')
    <div class="workspace">
        @include('partials.topbar')
        @yield('content')
        @include('partials.footer')
    </div>
    @include('partials.recipe-dialog')
    <div id="toast" role="status" aria-live="polite"></div>
</body>
</html>
