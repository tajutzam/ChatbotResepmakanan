<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class ExampleTest extends TestCase
{
    use RefreshDatabase;

    /**
     * A basic test example.
     */
    public function test_the_application_returns_a_successful_response(): void
    {
        $user = User::factory()->create();

        foreach (['/', '/chatbot', '/rekomendasi', '/rencana-masak', '/resep', '/history', '/login', '/signup'] as $path) {
            $response = in_array($path, ['/chatbot', '/rencana-masak', '/history'], true)
                ? $this->actingAs($user)->get($path)
                : $this->get($path);

            $response->assertOk()->assertSee('KeenVado Meals')->assertSee('data-page=', false);
        }

        $this->actingAs($user)->get('/dashboard')->assertOk()->assertSee('KeenVado Meals')->assertSee('data-page=', false);
    }
}
