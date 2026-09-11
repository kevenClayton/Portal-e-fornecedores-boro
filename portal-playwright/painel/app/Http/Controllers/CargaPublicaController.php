<?php

namespace App\Http\Controllers;

use App\Models\Cliente;
use App\Models\NotificacaoCarga;
use App\Support\Tenant;
use Illuminate\View\View;

class CargaPublicaController extends Controller
{
    public function show(string $publicId): View
    {
        $notificacao = $this->buscarNotificacao($publicId);
        if (! $notificacao) {
            abort(404);
        }

        return view('public.carga', [
            'notificacao' => $notificacao,
        ]);
    }

    protected function buscarNotificacao(string $publicId): ?NotificacaoCarga
    {
        Tenant::clear();
        $local = NotificacaoCarga::withoutGlobalScopes()
            ->where('public_id', $publicId)
            ->first();
        if ($local) {
            return $local;
        }

        $clientes = Cliente::query()
            ->where('ativo', true)
            ->whereNotNull('db_database')
            ->whereNotNull('db_host')
            ->orderBy('id')
            ->get();

        foreach ($clientes as $cliente) {
            try {
                Tenant::set((int) $cliente->id);
                $registro = NotificacaoCarga::withoutGlobalScopes()
                    ->where('public_id', $publicId)
                    ->first();
                if ($registro) {
                    return $registro;
                }
            } catch (\Throwable) {
                continue;
            }
        }

        Tenant::clear();

        return null;
    }
}
