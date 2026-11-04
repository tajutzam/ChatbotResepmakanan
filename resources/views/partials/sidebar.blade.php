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
    @if(auth()->user() && in_array(auth()->user()->email, config('services.admin_emails', []), true))
        <a href="{{ route('admin.recipes') }}" class="nav-item {{ $page === 'admin' ? 'active' : '' }}"><span>⚙</span>Kelola resep</a>
    @endif
    <div class="sidebar-bottom">Dibuat untuk dapur Indonesia <span>♡</span></div>
</aside>
<nav class="mobile-bottom-nav" aria-label="Navigasi mobile">
    @foreach (['home' => ['⌂', 'Beranda'], 'chatbot' => ['✧', 'Chatbot'], 'recommendations' => ['♡', 'Rekomendasi'], 'recipes' => ['▤', 'Resep']] as $key => [$icon, $label])
        <a href="{{ route($key) }}" class="mobile-nav-item {{ $page === $key ? 'active' : '' }}" @if($page === $key) aria-current="page" @endif><span>{{ $icon }}</span><small>{{ $label }}</small></a>
    @endforeach
    @if(auth()->user() && in_array(auth()->user()->email, config('services.admin_emails', []), true))
        <a href="{{ route('admin.recipes') }}" class="mobile-nav-item {{ $page === 'admin' ? 'active' : '' }}"><span>⚙</span><small>Admin</small></a>
    @endif
</nav>
