<?php

namespace App\Models;

use App\Models\Concerns\BelongsToCliente;
use Illuminate\Database\Eloquent\Model;

class RoboAuditoria extends Model
{
    use BelongsToCliente;

    protected $table = 'robo_auditoria';

    public $timestamps = false;

    protected $guarded = [];

    protected function casts(): array
    {
        return [
            'created_at' => 'datetime',
            'tentativa' => 'integer',
            'slot' => 'integer',
        ];
    }
}
