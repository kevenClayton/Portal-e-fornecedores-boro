<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;

class Motorista extends Model
{
    protected $table = 'motoristas';

    protected $guarded = [];

    protected function casts(): array
    {
        return [
            'aceita_bobina' => 'boolean',
            'situacao' => 'boolean',
            'ordem_motorista' => 'integer',
        ];
    }

    public function destinos(): BelongsToMany
    {
        return $this->belongsToMany(Destino::class, 'motorista_destino', 'motorista_id', 'destino_id');
    }

    public function origens(): BelongsToMany
    {
        return $this->belongsToMany(Origem::class, 'motorista_origem', 'motorista_id', 'origem_id');
    }

    public function tiposVeiculo(): BelongsToMany
    {
        return $this->belongsToMany(TipoVeiculo::class, 'motorista_tipo_veiculo', 'motorista_id', 'tipo_veiculo_id');
    }

    public function tiposVeiculoCarreta(): BelongsToMany
    {
        return $this->belongsToMany(TipoVeiculo::class, 'motorista_tipo_veiculo_carreta', 'motorista_id', 'tipo_veiculo_id');
    }
}
