<?php

namespace App\Models;

use App\Models\Concerns\BelongsToCliente;
use Illuminate\Database\Eloquent\Model;

class RoboAcompanhamento extends Model
{
    use BelongsToCliente;

    protected $table = 'robo_acompanhamento';

    public $timestamps = false;

    protected $guarded = [];

    protected function casts(): array
    {
        return [
            'pedir_screenshot' => 'boolean',
            'screenshot_em' => 'datetime',
            'atualizado_em' => 'datetime',
        ];
    }
}
