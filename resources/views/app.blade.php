@extends('layouts.app')

@section('content')
    <main>
        @include('pages.' . $page)
    </main>
@endsection
