<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Relatorio extends Model
{
    protected $table = 'relatorios';

    protected $guarded = [];

    protected function casts(): array
    {
        return [
            'mais_de_um_cliente' => 'boolean',
        ];
    }
}
