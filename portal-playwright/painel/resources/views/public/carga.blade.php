<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Atualização da carga — {{ $branding['nome'] ?? config('app.name') }}</title>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
    <style>
        :root {
            --accent: {{ $branding['cor_primaria'] ?? '#0d7a6f' }};
            --accent-hover: {{ $branding['cor_accent'] ?? '#0a635a' }};
            --accent-soft: {{ $branding['cor_soft'] ?? '#d8f0ec' }};
        }
    </style>
</head>
@php
    $aceita = strtolower((string) $notificacao->situacao) === 'aceita';
    $situacaoLabel = $aceita ? 'Aceita' : 'Perdida';
@endphp
<body class="bg-paper text-ink min-h-screen">
    <div class="min-h-screen relative overflow-hidden">
        <div class="absolute inset-0 pointer-events-none opacity-70"
             style="background:
                radial-gradient(circle at 12% 0%, color-mix(in srgb, var(--accent) 22%, transparent), transparent 42%),
                radial-gradient(circle at 90% 100%, rgba(36,54,66,.12), transparent 40%);"></div>

        <main class="relative mx-auto max-w-2xl px-4 py-10 md:py-16">
            <div class="mb-8">
                <div class="inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-bold uppercase tracking-[0.14em]
                    {{ $aceita ? 'bg-[var(--ok-soft)] text-[var(--ok)]' : 'bg-[var(--danger-soft)] text-[var(--danger)]' }}">
                    {{ $situacaoLabel }}
                </div>
                <h1 class="font-display text-3xl md:text-4xl mt-3 tracking-tight">Atualização da carga</h1>
                <p class="page-subtitle mt-2">
                    Documento <span class="font-semibold text-ink">{{ $notificacao->numero_documento }}</span>
                    · {{ optional($notificacao->created_at)->timezone(config('app.timezone'))->format('d/m/Y H:i') }}
                </p>
            </div>

            <section class="panel-pad space-y-5">
                <div>
                    <p class="text-xs font-bold uppercase tracking-[0.14em] text-slate-500">Situação</p>
                    <p class="mt-1 text-lg font-semibold">A carga foi {{ strtolower($situacaoLabel) }}.</p>
                </div>

                <dl class="grid sm:grid-cols-2 gap-4">
                    <div>
                        <dt class="text-xs font-bold uppercase tracking-[0.14em] text-slate-500">Motorista</dt>
                        <dd class="mt-1 font-medium">{{ $notificacao->motorista ?: '—' }}</dd>
                    </div>
                    <div>
                        <dt class="text-xs font-bold uppercase tracking-[0.14em] text-slate-500">Documento</dt>
                        <dd class="mt-1 font-medium">{{ $notificacao->numero_documento }}</dd>
                    </div>
                    <div>
                        <dt class="text-xs font-bold uppercase tracking-[0.14em] text-slate-500">Origem</dt>
                        <dd class="mt-1 font-medium">{{ $notificacao->origem ?: '—' }}</dd>
                    </div>
                    <div>
                        <dt class="text-xs font-bold uppercase tracking-[0.14em] text-slate-500">Destino</dt>
                        <dd class="mt-1 font-medium">{{ $notificacao->destino ?: '—' }}</dd>
                    </div>
                    <div>
                        <dt class="text-xs font-bold uppercase tracking-[0.14em] text-slate-500">Valor</dt>
                        <dd class="mt-1 font-medium">{{ $notificacao->valor_carga ?: '—' }}</dd>
                    </div>
                    <div>
                        <dt class="text-xs font-bold uppercase tracking-[0.14em] text-slate-500">Tipo</dt>
                        <dd class="mt-1 font-medium">{{ $notificacao->tipo_transporte ?: '—' }}</dd>
                    </div>
                    @if ($notificacao->placa)
                        <div>
                            <dt class="text-xs font-bold uppercase tracking-[0.14em] text-slate-500">Placa</dt>
                            <dd class="mt-1 font-medium">{{ $notificacao->placa }}</dd>
                        </div>
                    @endif
                    @if ($notificacao->cpf)
                        <div>
                            <dt class="text-xs font-bold uppercase tracking-[0.14em] text-slate-500">CPF</dt>
                            <dd class="mt-1 font-medium">{{ $notificacao->cpf }}</dd>
                        </div>
                    @endif
                </dl>

                <div class="rounded-xl px-4 py-3 {{ $aceita ? 'bg-[var(--ok-soft)]' : 'bg-[var(--danger-soft)]' }}">
                    <p class="text-xs font-bold uppercase tracking-[0.14em] {{ $aceita ? 'text-[var(--ok)]' : 'text-[var(--danger)]' }}">Motivo</p>
                    <p class="mt-1 font-medium">{{ filled($notificacao->motivo) ? $notificacao->motivo : '—' }}</p>
                </div>
            </section>

            <p class="mt-8 text-center text-sm text-slate-500">{{ $branding['nome'] ?? 'Portal' }} · Portal de cargas</p>
        </main>
    </div>
</body>
</html>
