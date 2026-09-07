<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class LoginPortal extends Model
{
    protected $table = 'login';

    protected $guarded = [];

    protected function casts(): array
    {
        return [
            'ativo' => 'boolean',
        ];
    }
}
