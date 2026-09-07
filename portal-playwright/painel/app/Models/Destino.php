<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class Destino extends Model
{
    protected $table = 'destinos';

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
        return $this->belongsToMany(Motorista::class, 'motorista_destino', 'destino_id', 'motorista_id');
    }
}
