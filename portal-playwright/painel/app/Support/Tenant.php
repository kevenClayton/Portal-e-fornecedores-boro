<?php

namespace App\Support;

use App\Models\Cliente;

class Tenant
{
    protected static ?int $clienteId = null;

    protected static ?Cliente $cliente = null;

    public static function set(?int $clienteId): void
    {
        static::$clienteId = $clienteId;
        static::$cliente = null;
    }

    public static function clear(): void
    {
        static::$clienteId = null;
        static::$cliente = null;
    }

    public static function id(): ?int
    {
        return static::$clienteId;
    }

    public static function cliente(): ?Cliente
    {
        if (static::$clienteId === null) {
            return null;
        }

        if (static::$cliente === null || (int) static::$cliente->id !== static::$clienteId) {
            static::$cliente = Cliente::query()->find(static::$clienteId);
        }

        return static::$cliente;
    }

    public static function requireId(): int
    {
        $clienteId = static::id();
        if (! $clienteId) {
            abort(403, 'Nenhum cliente selecionado.');
        }

        return $clienteId;
    }
}
