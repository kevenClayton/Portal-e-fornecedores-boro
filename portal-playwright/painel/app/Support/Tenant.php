<?php

namespace App\Support;

use App\Models\Cliente;
use Illuminate\Support\Facades\Config;
use Illuminate\Support\Facades\Crypt;
use Illuminate\Support\Facades\DB;

class Tenant
{
    protected static ?int $clienteId = null;

    protected static ?Cliente $cliente = null;

    public static function set(?int $clienteId): void
    {
        static::$clienteId = $clienteId;
        static::$cliente = null;
        static::aplicarConexao();
    }

    public static function clear(): void
    {
        static::$clienteId = null;
        static::$cliente = null;
        static::aplicarConexao();
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
            static::$cliente = Cliente::on('central')->find(static::$clienteId);
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

    public static function usaBancoProprio(): bool
    {
        return (bool) static::cliente()?->temBancoProprio();
    }

    public static function aplicarConexao(): void
    {
        $cliente = static::cliente();
        $base = config('database.connections.central');

        if ($cliente && $cliente->temBancoProprio()) {
            $senha = '';
            if (filled($cliente->db_password)) {
                try {
                    $senha = Crypt::decryptString((string) $cliente->db_password);
                } catch (\Throwable) {
                    $senha = (string) $cliente->db_password;
                }
            }

            Config::set('database.connections.tenant', array_merge($base, [
                'host' => $cliente->db_host,
                'port' => (string) ($cliente->db_port ?: 3306),
                'database' => $cliente->db_database,
                'username' => $cliente->db_username,
                'password' => $senha,
            ]));
        } else {
            Config::set('database.connections.tenant', $base);
        }

        DB::purge('tenant');
    }
}
