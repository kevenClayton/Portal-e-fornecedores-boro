<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>{{ config('app.name') }} — Entrar</title>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>
<body class="min-h-screen bg-paper text-ink antialiased">
<div class="min-h-screen grid lg:grid-cols-2">
    <section class="relative hidden lg:flex flex-col justify-between p-10 text-white overflow-hidden"
             style="background:
                radial-gradient(circle at 15% 20%, rgba(13,122,111,.55), transparent 40%),
                linear-gradient(160deg, #0f1c24 0%, #1a3340 55%, #0d7a6f 140%);">
        <div>
            <div class="inline-flex items-center gap-3">
                <div class="h-12 w-12 rounded-2xl bg-brand flex items-center justify-center">
                    <svg class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3 7h11v10H3V7Zm11 3h4l3 3v4h-7v-7Z"/>
                    </svg>
                </div>
                <div>
                    <div class="font-display text-2xl leading-none">MadeForte</div>
                    <div class="text-sm text-slate-300 mt-1">Portal E-Fornecedores</div>
                </div>
            </div>
        </div>

        <div class="max-w-md">
            <h1 class="font-display text-4xl leading-tight">Controle a captura de cargas com clareza.</h1>
            <p class="mt-4 text-slate-300 leading-relaxed">
                Gerencie motoristas, parâmetros e o robô em um só lugar — pensado para o dia a dia da operação.
            </p>
        </div>

        <div class="text-sm text-slate-400">Acesso restrito à equipe autorizada.</div>
    </section>

    <section class="flex items-center justify-center p-6 sm:p-10">
        <div class="w-full max-w-md">
            <div class="lg:hidden mb-8">
                <div class="font-display text-2xl">MadeForte</div>
                <div class="text-sm text-slate-500">Painel do robô</div>
            </div>

            <div class="panel-pad shadow-soft">
                <h2 class="font-display text-2xl">Entrar no painel</h2>
                <p class="text-sm text-slate-500 mt-1 mb-6">Use o e-mail e a senha da sua conta.</p>

                <x-auth-session-status class="mb-4" :status="session('status')" />

                <form method="POST" action="{{ route('login') }}" class="space-y-4">
                    @csrf

                    <div>
                        <label class="field-label" for="email">E-mail</label>
                        <input id="email" type="email" name="email" value="{{ old('email') }}" required autofocus autocomplete="username" class="field-input" placeholder="voce@empresa.com">
                        <x-input-error :messages="$errors->get('email')" class="mt-2" />
                    </div>

                    <div>
                        <label class="field-label" for="password">Senha</label>
                        <input id="password" type="password" name="password" required autocomplete="current-password" class="field-input" placeholder="••••••••">
                        <x-input-error :messages="$errors->get('password')" class="mt-2" />
                    </div>

                    <div class="flex items-center justify-between gap-3">
                        <label class="inline-flex items-center gap-2 text-sm font-medium text-slate-600">
                            <input id="remember_me" type="checkbox" class="rounded border-line text-brand focus:ring-brand" name="remember">
                            Manter conectado
                        </label>
                        @if (Route::has('password.request'))
                            <a class="text-sm font-semibold text-brand hover:underline" href="{{ route('password.request') }}">
                                Esqueci a senha
                            </a>
                        @endif
                    </div>

                    <button class="btn-primary w-full !py-3">Entrar</button>
                </form>
            </div>
        </div>
    </section>
</div>
</body>
</html>
