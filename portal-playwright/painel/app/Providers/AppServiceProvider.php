<?php

namespace App\Providers;

use App\Support\Branding;
use App\Support\Tenant;
use Illuminate\Pagination\Paginator;
use Illuminate\Support\Facades\URL;
use Illuminate\Support\Facades\View;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        //
    }

    public function boot(): void
    {
        Paginator::useTailwind();

        // Nginx termina TLS; multi-host (madeforte + efornecedor) — não fixar APP_URL única
        URL::forceScheme('https');
        $hostAtual = strtolower((string) request()->getHost());
        if ($hostAtual !== '' && (
            array_key_exists($hostAtual, config('tenancy.host_map', []))
            || str_ends_with($hostAtual, '.reservaai.com.br')
        )) {
            URL::forceRootUrl('https://'.$hostAtual);
        }

        View::composer(['layouts.admin', 'auth.login', 'public.carga'], function ($view): void {
            $branding = Branding::fromRequest(request());
            $view->with('branding', $branding);
            $view->with('clienteAtual', Tenant::cliente());
        });
    }
}
