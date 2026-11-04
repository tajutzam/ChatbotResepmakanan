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
    <style>
        .mobile-bottom-nav{display:none}
        @media (max-width: 640px){
            body{padding-bottom:calc(74px + env(safe-area-inset-bottom))}
            .sidebar{display:none}
            .workspace{margin-left:0;min-height:100vh}
            .topbar{height:62px;padding:0 18px;border-bottom:1px solid var(--line)}
            .account{gap:10px}
            .account .demo-label,.account>a:not(.button),.account form{display:none}
            main{padding:24px 17px 34px}
            h1{font-size:28px;line-height:1.2}
            .page-head{margin-bottom:22px}
            .mobile-bottom-nav{display:flex;position:fixed;z-index:50;right:0;bottom:0;left:0;align-items:stretch;justify-content:space-around;padding:8px 8px calc(8px + env(safe-area-inset-bottom));background:rgba(255,255,255,.97);border-top:1px solid var(--line);box-shadow:0 -8px 24px rgba(48,45,41,.08)}
            .mobile-nav-item{display:flex;min-width:58px;flex:1;flex-direction:column;align-items:center;justify-content:center;gap:3px;padding:5px 2px;border-radius:10px;color:#928b83;font-size:20px;line-height:1}
            .mobile-nav-item small{font-size:9px;font-weight:600;white-space:nowrap}
            .mobile-nav-item.active{background:var(--pale);color:var(--orange)}
            .mobile-nav-item:focus-visible{outline-offset:-2px}
            .recipe-grid{grid-template-columns:1fr;gap:14px}
            .filter-row{display:grid;grid-template-columns:1fr;gap:10px}
            .admin-recipe{padding:17px}
            .recipe-photo{width:100%;height:150px;object-fit:cover;border-radius:12px;margin-bottom:10px}
        }
        .recipe-card[data-detail]{cursor:pointer}
        .planned-clickable{display:grid;width:100%;gap:5px;padding:14px;text-align:left;background:#fffaf4;border:1px solid #f1dfcc;border-radius:12px;color:var(--ink)}
        .planned-clickable strong{font:600 14px 'Plus Jakarta Sans',sans-serif}.planned-clickable .eyebrow{margin:0;color:var(--orange)}
        .planned-clickable:hover{border-color:var(--orange);background:#fff5ea}
        .recipe-card[data-detail]:focus-visible{outline:3px solid var(--orange);outline-offset:4px}
        .recipe-photo{width:100%;height:180px;object-fit:cover;border-radius:12px;margin-bottom:12px}
        #recipe-dialog .dialog-photo{width:100%;max-height:230px;object-fit:cover;border-radius:14px;margin-bottom:18px}
        .chat-related-title{margin:18px 0 8px;font-size:14px;color:var(--ink)}
    </style>
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
