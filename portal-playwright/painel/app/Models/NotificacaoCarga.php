<?php

namespace App\Models;

use App\Models\Concerns\BelongsToCliente;
use Illuminate\Database\Eloquent\Model;

class NotificacaoCarga extends Model
{
    use BelongsToCliente;

    protected $table = 'notificacoes_carga';

    public $timestamps = false;

    protected $guarded = [];

    protected function casts(): array
    {
        return [
            'created_at' => 'datetime',
        ];
    }
}
