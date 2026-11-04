<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class SearchHistory extends Model
{
    protected $fillable = ['user_id', 'query', 'recipe_ids'];

    protected function casts(): array
    {
        return ['recipe_ids' => 'array'];
    }
}
