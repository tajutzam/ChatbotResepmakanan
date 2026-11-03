<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="theme-color" content="#ed7626">
    <meta name="description" content="Temukan inspirasi resep dari bahan yang ada di dapurmu bersama DapurKita.">
    <title>DapurKita — Teman masak sehari-hari</title>
    <link rel="stylesheet" href="{{ asset('css/app.css') }}">
    <script src="{{ asset('js/recipes.js') }}" defer></script>
    <script src="{{ asset('js/app.js') }}" defer></script>
</head>
<body data-page="{{ $page }}">
    <aside class="sidebar">
        <a href="{{ route('home') }}" class="brand"><span class="brand-icon">♨</span>Dapur<span>Kita</span><small>TEMAN MASAK SEHARI-HARI</small></a>
        <div class="nav-label">JELAJAHI DAPUR</div>
        <nav aria-label="Navigasi utama">
            @foreach (['home' => ['⌂', 'Beranda'], 'chatbot' => ['✧', 'Chatbot resep'], 'recommendations' => ['♡', 'Rekomendasi resep'], 'planner' => ['▦', 'Rencana masak']] as $key => [$icon, $label])
                <a href="{{ route($key) }}" class="nav-item {{ $page === $key ? 'active' : '' }}" @if($page === $key) aria-current="page" @endif><span>{{ $icon }}</span>{{ $label }}@if($key === 'chatbot')<small>COBA</small>@endif</a>
            @endforeach
        </nav>
        <div class="nav-label second">DAPUR PRIBADI</div>
        <nav aria-label="Area pengguna">
            @foreach (['dashboard' => ['◫', 'Dashboard'], 'recipes' => ['▤', 'Menu resep'], 'history' => ['◷', 'Riwayat pencarian']] as $key => [$icon, $label])
                <a href="{{ route($key) }}" class="nav-item {{ $page === $key ? 'active' : '' }}" @if($page === $key) aria-current="page" @endif><span>{{ $icon }}</span>{{ $label }}</a>
            @endforeach
        </nav>
        <div class="sidebar-note"><span>✧</span><h3>Bahan sederhana,<br>rasa luar biasa.</h3><p>Mulai dari apa yang ada<br>di dapurmu hari ini.</p><a href="{{ route('chatbot') }}">Yuk, cari ide masak ↗</a></div>
        <div class="sidebar-bottom">Dibuat untuk dapur Indonesia <span>♡</span></div>
    </aside>
    <div class="workspace">
        <header class="topbar"><span class="breadcrumb">DapurKita <span>/</span> <b id="breadcrumb">Beranda</b></span><div class="account"><span class="demo-label">UI PREVIEW</span><a href="{{ route('login') }}">Masuk</a><a class="button small" href="{{ route('signup') }}">Daftar gratis <span>↗</span></a></div></header>
        <main id="content" tabindex="-1"></main>
        <footer><span>© {{ date('Y') }} DapurKita</span><span>Sedikit inspirasi. Banyak cerita dari dapur.</span><span>Selamat memasak ♡</span></footer>
    </div>
    <dialog id="recipe-dialog" aria-labelledby="recipe-title"><button class="close" aria-label="Tutup detail resep">×</button><div id="recipe-detail"></div></dialog>
    <div id="toast" role="status" aria-live="polite"></div>
</body>
</html>
