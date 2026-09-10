<?php

namespace App\Models;

use App\Models\Concerns\BelongsToCliente;
use Illuminate\Database\Eloquent\Model;

class Rota extends Model
{
    use BelongsToCliente;

    protected $table = 'rotas';

    protected $guarded = [];

    protected function casts(): array
    {
        return [
            'situacao' => 'boolean',
        ];
    }
}
