@php($isRecipes = in_array($page, ['recipes', 'recommendations'], true))
<section class="page-head">
    <div class="eyebrow">{{ $page === 'recipes' ? 'KOLEKSI DAPUR' : 'DIPILIH UNTUK INSPIRASIMU' }}</div>
    <h1>{{ $page === 'recipes' ? 'Menu resep' : 'Rekomendasi resep' }}</h1>
    <p>{{ $page === 'recipes' ? 'Jelajahi resep rumahan dan simpan yang ingin kamu coba.' : 'Ide masakan sederhana untuk setiap hari. Mulai dari bahan favoritmu.' }}
    </p>
</section>
<div class="filter-row">@include('partials.search')<select id="saved-filter" aria-label="Tampilkan koleksi">
        <option value="all">Semua koleksi</option>
        <option value="saved">Resep tersimpan</option>
    </select></div><p class="subtitle" id="result-count"></p>@include('partials.recipe-grid')
