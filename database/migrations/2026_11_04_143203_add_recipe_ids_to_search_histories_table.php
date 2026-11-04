<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('search_histories', function (Blueprint $table): void {
            $table->text('recipe_ids')->nullable()->after('query');
        });
    }

    public function down(): void
    {
        Schema::table('search_histories', function (Blueprint $table): void {
            $table->dropColumn('recipe_ids');
        });
    }
};
