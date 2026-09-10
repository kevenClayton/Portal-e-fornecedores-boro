<?php

namespace App\Models\Concerns;

use App\Support\Tenant;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;

trait BelongsToCliente
{
    public static function bootBelongsToCliente(): void
    {
        static::addGlobalScope('cliente', function (Builder $builder): void {
            $clienteId = Tenant::id();
            if ($clienteId === null) {
                return;
            }

            $builder->where($builder->getModel()->getTable().'.cliente_id', $clienteId);
        });

        static::creating(function (Model $model): void {
            if ($model->getAttribute('cliente_id') === null && Tenant::id() !== null) {
                $model->setAttribute('cliente_id', Tenant::id());
            }
        });
    }
}
