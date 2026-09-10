<?php

namespace App\Models;

use App\Models\Concerns\BelongsToCliente;
use Illuminate\Database\Eloquent\Model;

class TipoVeiculo extends Model
{
    use BelongsToCliente;

    protected $table = 'tipo_veiculo';

    public $timestamps = false;

    protected $guarded = [];

    protected function casts(): array
    {
        return [
            'created_at' => 'datetime',
        ];
    }
}
