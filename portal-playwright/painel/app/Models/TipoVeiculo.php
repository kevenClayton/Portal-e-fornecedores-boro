<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class TipoVeiculo extends Model
{
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
