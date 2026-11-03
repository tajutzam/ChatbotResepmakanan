<?php

namespace Tests\Feature;

// use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class ExampleTest extends TestCase
{
    /**
     * A basic test example.
     */
    public function test_the_application_returns_a_successful_response(): void
    {
        foreach (['/', '/chatbot', '/rekomendasi', '/rencana-masak', '/dashboard', '/resep', '/history', '/login', '/signup'] as $path) {
            $this->get($path)->assertOk()->assertSee('DapurKita')->assertSee('data-page=', false);
        }
    }
}
