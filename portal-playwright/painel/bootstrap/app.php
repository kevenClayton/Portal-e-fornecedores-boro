<?php

use Illuminate\Console\Scheduling\Schedule;
use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;
use Illuminate\Http\Request;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withSchedule(function (Schedule $schedule): void {
        $schedule->command('robo:aplicar-agenda')->everyMinute()->withoutOverlapping();
    })
    ->withMiddleware(function (Middleware $middleware): void {
        // Nginx termina o TLS; o Laravel precisa confiar em X-Forwarded-Proto
        $middleware->trustProxies(at: '*');
        $middleware->web(append: [
            \App\Http\Middleware\SetTenant::class,
        ]);
        // SetTenant precisa rodar DEPOIS da sessão e ANTES do route model binding,
        // senão edit/destroy de motorista (tenant Boro) resolve no DB errado → 404.
        $middleware->priority([
            \Illuminate\Foundation\Http\Middleware\HandlePrecognitiveRequests::class,
            \Illuminate\Cookie\Middleware\EncryptCookies::class,
            \Illuminate\Cookie\Middleware\AddQueuedCookiesToResponse::class,
            \Illuminate\Session\Middleware\StartSession::class,
            \Illuminate\View\Middleware\ShareErrorsFromSession::class,
            \Illuminate\Foundation\Http\Middleware\PreventRequestForgery::class,
            \App\Http\Middleware\SetTenant::class,
            \Illuminate\Routing\Middleware\SubstituteBindings::class,
        ]);
        $middleware->alias([
            'super_admin' => \App\Http\Middleware\EnsureSuperAdmin::class,
        ]);
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        $exceptions->shouldRenderJsonWhen(
            fn (Request $request) => $request->is('api/*') || $request->expectsJson(),
        );

        // php -S + Docker: Notice "Broken pipe" no log não deve virar 500
        $exceptions->report(function (\Throwable $erro): ?bool {
            $mensagem = $erro->getMessage();
            if (str_contains($mensagem, 'Broken pipe')
                || str_contains($mensagem, 'headers already sent by (output started at')
            ) {
                return false;
            }

            return null;
        });
    })->create();
