<section class="auth">
    <div class="eyebrow">SELAMAT DATANG DI DAPURKITA</div>
    <h1>{{ $page === 'signup' ? 'Cerita dapurmu dimulai di sini.' : 'Senang bertemu kamu lagi.' }}</h1>
    <p>{{ $page === 'signup' ? 'Simpan resep favorit dan susun rencana masakmu.' : 'Yuk, lanjutkan petualangan rasa hari ini.' }}
    </p>
    <p class="notice">Masuk untuk menyimpan resep favorit dan mengelola rencana masakmu.</p>
    @if ($errors->any())
        <div class="notice">{{ $errors->first() }}</div>
    @endif
    <form id="auth-form" method="POST" action="{{ route($page === 'signup' ? 'signup.store' : 'login.store') }}">
        @csrf
        @if ($page === 'signup')
            <label>Nama lengkap<input name="name" placeholder="Nama panggilanmu" required maxlength="60"
                    autocomplete="name"></label>
        @endif
        <label>
            Email<input type="email" name="email" placeholder="nama@email.com" required
                autocomplete="email"></label><label>Kata sandi<input type="password" name="password"
                placeholder="Masukkan kata sandi" required minlength="8" autocomplete="current-password"></label>
        @if ($page === 'signup')
            <label>Konfirmasi kata sandi<input type="password" name="password_confirmation" placeholder="Ulangi kata sandi" required minlength="8" autocomplete="new-password"></label>
        @endif
        @if ($page === 'signup')
            <label class="checkbox"><input type="checkbox" required>Saya menyetujui pembuatan akun DapurKita.</label>
        @endif
        <button class="button" type="submit">{{ $page === 'signup' ? 'Coba daftar' : 'Masuk demo' }} ↗</button>
    </form>
</section>
