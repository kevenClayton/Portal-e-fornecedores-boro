<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Parametro extends Model
{
    protected $table = 'parametros';

    protected $guarded = [];

    protected function casts(): array
    {
        return [
            'limite_valor_truck' => 'float',
            'limite_valor_toco' => 'float',
            'limite_valor_carreta' => 'float',
            'modo_teste' => 'boolean',
            'intervalo_espera_seg' => 'integer',
        ];
    }
}
