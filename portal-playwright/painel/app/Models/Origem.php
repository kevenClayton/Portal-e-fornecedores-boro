<?php

namespace App\Models;

use App\Models\Concerns\BelongsToCliente;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class Origem extends Model
{
    use BelongsToCliente;

    protected $table = 'origens';

    public $timestamps = false;

    protected $guarded = [];

    protected function casts(): array
    {
        return [
            'ativo' => 'boolean',
            'created_at' => 'datetime',
        ];
    }

    public function motoristas(): BelongsToMany
    {
        return $this->belongsToMany(Motorista::class, 'motorista_origem', 'origem_id', 'motorista_id');
    }
}
