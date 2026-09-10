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

        $appUrl = (string) config('app.url');
        if (str_starts_with($appUrl, 'https://')) {
            URL::forceScheme('https');
            URL::forceRootUrl($appUrl);
        }

        View::composer(['layouts.admin', 'auth.login', 'public.carga'], function ($view): void {
            $branding = Branding::fromRequest(request());
            $view->with('branding', $branding);
            $view->with('clienteAtual', Tenant::cliente());
        });
    }
}
