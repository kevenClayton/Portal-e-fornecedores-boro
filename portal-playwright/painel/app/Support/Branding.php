<?php

namespace App\Support;

use App\Models\Cliente;
use Illuminate\Http\Request;

class Branding
{
    /**
     * @return array{nome:string,subtitulo:string,cor_primaria:string,cor_accent:string,cor_soft:string,slug:?string}
     */
    public static function fromRequest(Request $request): array
    {
        $cliente = Tenant::cliente();
        if ($cliente) {
            return static::fromCliente($cliente);
        }

        $host = strtolower($request->getHost());
        $mapa = config('tenancy.host_map', []);
        $slug = $mapa[$host] ?? null;

        if (is_string($slug) && $slug !== '') {
            $porSlug = Cliente::query()->where('slug', $slug)->where('ativo', true)->first();
            if ($porSlug) {
                return static::fromCliente($porSlug);
            }
        }

        $generica = config('tenancy.marca_generica');

        return [
            'nome' => (string) ($generica['nome'] ?? 'E-Fornecedor'),
            'subtitulo' => (string) ($generica['subtitulo'] ?? 'Portal multi-cliente'),
            'cor_primaria' => (string) ($generica['cor_primaria'] ?? '#1e4d6b'),
            'cor_accent' => (string) ($generica['cor_accent'] ?? '#163a52'),
            'cor_soft' => Cliente::corSuave((string) ($generica['cor_primaria'] ?? '#1e4d6b')),
            'slug' => null,
        ];
    }

    /**
     * @return array{nome:string,subtitulo:string,cor_primaria:string,cor_accent:string,cor_soft:string,slug:?string}
     */
    public static function fromCliente(Cliente $cliente): array
    {
        $primaria = $cliente->cor_primaria ?: '#0d7a6f';
        $accent = $cliente->cor_accent ?: '#0a635a';

        return [
            'nome' => $cliente->nome,
            'subtitulo' => 'Painel do robô',
            'cor_primaria' => $primaria,
            'cor_accent' => $accent,
            'cor_soft' => Cliente::corSuave($primaria),
            'slug' => $cliente->slug,
        ];
    }
}
