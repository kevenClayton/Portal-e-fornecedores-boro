<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Rota extends Model
{
    protected $table = 'rotas';

    protected $guarded = [];

    protected function casts(): array
    {
        return [
            'situacao' => 'boolean',
        ];
    }
}
