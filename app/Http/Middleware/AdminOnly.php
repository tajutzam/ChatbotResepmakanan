<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class AdminOnly
{
    public function handle(Request $request, Closure $next): Response
    {
        $emails = config('services.admin_emails', []);
        abort_unless($request->user() && in_array($request->user()->email, $emails, true), 403);

        return $next($request);
    }
}
