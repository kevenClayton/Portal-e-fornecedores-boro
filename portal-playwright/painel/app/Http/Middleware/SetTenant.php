<?php

namespace App\Http\Middleware;

use App\Models\Cliente;
use App\Support\Tenant;
use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class SetTenant
{
    public function handle(Request $request, Closure $next): Response
    {
        $user = $request->user();

        if (! $user) {
            Tenant::clear();

            return $next($request);
        }

        if ($user->is_super_admin) {
            $clienteAtivoId = (int) ($request->session()->get('cliente_ativo_id') ?: 0);
            if ($clienteAtivoId <= 0 || ! Cliente::query()->whereKey($clienteAtivoId)->where('ativo', true)->exists()) {
                $clienteAtivoId = (int) (Cliente::query()->where('ativo', true)->orderBy('id')->value('id') ?: 0);
                if ($clienteAtivoId > 0) {
                    $request->session()->put('cliente_ativo_id', $clienteAtivoId);
                }
            }
            Tenant::set($clienteAtivoId > 0 ? $clienteAtivoId : null);
        } else {
            Tenant::set($user->cliente_id ? (int) $user->cliente_id : null);
        }

        return $next($request);
    }
}
