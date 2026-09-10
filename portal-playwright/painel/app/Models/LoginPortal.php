<?php

namespace App\Models;

use App\Models\Concerns\BelongsToCliente;
use Illuminate\Database\Eloquent\Model;

class LoginPortal extends Model
{
    use BelongsToCliente;

    protected $table = 'login';

    protected $guarded = [];

    protected function casts(): array
    {
        return [
            'ativo' => 'boolean',
        ];
    }
}
