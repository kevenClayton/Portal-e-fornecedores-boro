<?php

namespace App\Models;

use App\Models\Concerns\BelongsToCliente;
use Illuminate\Database\Eloquent\Model;

class Relatorio extends Model
{
    use BelongsToCliente;

    protected $table = 'relatorios';

    protected $guarded = [];

    protected function casts(): array
    {
        return [
            'mais_de_um_cliente' => 'boolean',
        ];
    }
}
