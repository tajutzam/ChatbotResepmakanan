<aside class="sidebar">
    <a href="{{ route('home') }}" class="brand"><img src="{{ asset('images/logo.jpeg') }}" alt="KeenVado Meals"><span class="brand-name">KeenVado <strong>Meals</strong></span></a>
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
    @if(auth()->user() && in_array(auth()->user()->email, config('services.admin_emails', []), true))
        <a href="{{ route('admin.recipes') }}" class="nav-item {{ $page === 'admin' ? 'active' : '' }}"><span>⚙</span>Kelola resep</a>
    @endif
    <div class="sidebar-bottom">Dibuat untuk dapur Indonesia <span>♡</span></div>
</aside>
<nav class="mobile-bottom-nav" aria-label="Navigasi mobile">
    @foreach (['home' => ['⌂', 'Beranda'], 'dashboard' => ['◫', 'Dashboard'], 'chatbot' => ['✧', 'Chatbot'], 'recommendations' => ['♡', 'Rekomendasi']] as $key => [$icon, $label])
        <a href="{{ route($key) }}" class="mobile-nav-item {{ $page === $key ? 'active' : '' }}" @if($page === $key) aria-current="page" @endif><span>{{ $icon }}</span><small>{{ $label }}</small></a>
    @endforeach
    <button class="mobile-nav-item" id="mobile-more" type="button" aria-expanded="false"><span>•••</span><small>Lainnya</small></button>
</nav>
<div class="mobile-more-menu" id="mobile-more-menu" hidden>
    <a href="{{ route('recipes') }}"><span>▤</span>Menu resep</a>
    <a href="{{ route('history') }}"><span>◷</span>Riwayat</a>
    @auth
        <form method="POST" action="{{ route('logout') }}">@csrf<button type="submit"><span>↪</span>Keluar</button></form>
    @else
        <a href="{{ route('login') }}"><span>→</span>Masuk</a>
    @endauth
</div>
