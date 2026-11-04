<section class="page-head">
    <div class="eyebrow">DAPUR PRIBADI</div>
    <h1>Halo, {{ auth()->user()->name }}! ☀</h1>
    <p>Sedikit inspirasi untuk cerita lezatmu berikutnya.</p>
</section>
<div class="stats"><a href="{{ route('recipes') }}" class="stat"><small>Resep tersimpan</small><strong
            id="saved-count">0</strong></a><a href="{{ route('planner') }}" class="stat"><small>Rencana
            masak</small><strong id="plan-count">0</strong></a><a href="{{ route('history') }}"
        class="stat"><small>Pencarianmu</small><strong id="history-count">0</strong></a></div>
<div class="content-grid">
    <section>
        <div class="section-heading">
            <h2>Resep favoritmu</h2><a href="{{ route('recipes') }}">Jelajahi resep ↗</a>
        </div>
        <p class="subtitle">Simpan ide sekarang, masak kapan saja.</p>@include('partials.recipe-grid')
    </section>
    <aside>@include('partials.promo')</aside>
</div>
