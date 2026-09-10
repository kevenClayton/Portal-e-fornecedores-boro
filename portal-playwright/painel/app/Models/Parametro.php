<?php

namespace App\Models;

use App\Models\Concerns\BelongsToCliente;
use Illuminate\Database\Eloquent\Model;

class Parametro extends Model
{
    use BelongsToCliente;

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
            'verificar_valor_carga' => 'boolean',
            'verificar_bobina' => 'boolean',
            'verificar_multiplos_destinos' => 'boolean',
            'whatsapp_codigo_estabelecimento' => 'integer',
            'robo_agenda_ativa' => 'boolean',
            'robo_quantidade' => 'integer',
        ];
    }
}
