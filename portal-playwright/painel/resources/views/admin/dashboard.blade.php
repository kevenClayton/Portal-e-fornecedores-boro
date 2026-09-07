@extends('layouts.admin')

@section('title', 'Início')

@section('content')
    <div class="mb-8 flex flex-wrap items-end justify-between gap-4">
        <div>
            <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Operação</p>
            <h1 class="page-title font-display mt-1">Olá, {{ explode(' ', auth()->user()->name)[0] }}</h1>
            <p class="page-subtitle">Acompanhe o robô e os cadastros usados na captura de cargas.</p>
        </div>
        <div class="flex flex-wrap gap-2">
            <a href="{{ route('admin.robo.index') }}" class="btn-primary">Abrir controle do robô</a>
            <a href="{{ route('admin.motoristas.create') }}" class="btn-secondary">Novo motorista</a>
        </div>
    </div>

    <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4 mb-8">
        <div class="stat-card">
            <div class="text-xs font-bold uppercase tracking-wide text-slate-500">Status do robô</div>
            <div class="mt-3">
                @if ($statusRobo['running'] ?? false)
                    <span class="badge-ok">Em execução</span>
                @else
                    <span class="badge-warn">Parado</span>
                @endif
            </div>
            <p class="mt-3 text-sm text-slate-600 leading-relaxed">{{ $statusRobo['message'] ?? '—' }}</p>
            <p class="mt-2 text-xs text-slate-400">{{ $statusRobo['name'] ?? '' }} · {{ $statusRobo['status'] ?? '' }}</p>
        </div>

        <div class="stat-card">
            <div class="text-xs font-bold uppercase tracking-wide text-slate-500">Motoristas ativos</div>
            <div class="mt-3 flex items-baseline gap-2">
                <span class="text-3xl font-extrabold tracking-tight">{{ $motoristasAtivos }}</span>
                <span class="text-sm text-slate-400">de {{ $motoristasTotal }}</span>
            </div>
            <a href="{{ route('admin.motoristas.index') }}" class="mt-4 inline-block text-sm font-semibold text-brand hover:underline">Gerenciar fila →</a>
        </div>

        <div class="stat-card">
            <div class="text-xs font-bold uppercase tracking-wide text-slate-500">Rotas hoje</div>
            <div class="mt-3 text-3xl font-extrabold tracking-tight">{{ $rotasHoje }}</div>
            <a href="{{ route('admin.rotas.index') }}" class="mt-4 inline-block text-sm font-semibold text-brand hover:underline">Ver vinculadas →</a>
        </div>

        <div class="stat-card">
            <div class="text-xs font-bold uppercase tracking-wide text-slate-500">Rotas no total</div>
            <div class="mt-3 text-3xl font-extrabold tracking-tight">{{ $rotasTotal }}</div>
            <a href="{{ route('admin.relatorios.index') }}" class="mt-4 inline-block text-sm font-semibold text-brand hover:underline">Ver relatórios →</a>
        </div>
    </div>

    <div class="grid lg:grid-cols-2 gap-4">
        <div class="panel-pad">
            <h2 class="font-display text-xl mb-2">Atalhos rápidos</h2>
            <p class="text-sm text-slate-500 mb-5">As ações mais usadas no dia a dia da operação.</p>
            <div class="grid sm:grid-cols-2 gap-3">
                <a href="{{ route('admin.robo.index') }}" class="rounded-xl border border-line p-4 hover:bg-mist transition">
                    <div class="font-semibold">Ligar / desligar robô</div>
                    <div class="text-sm text-slate-500 mt-1">Start, stop e logs ao vivo</div>
                </a>
                <a href="{{ route('admin.parametros.index') }}" class="rounded-xl border border-line p-4 hover:bg-mist transition">
                    <div class="font-semibold">Parâmetros e clusters</div>
                    <div class="text-sm text-slate-500 mt-1">Limites, login do portal e destinos</div>
                </a>
                <a href="{{ route('admin.motoristas.gerenciar') }}" class="rounded-xl border border-line p-4 hover:bg-mist transition">
                    <div class="font-semibold">Ordem da fila</div>
                    <div class="text-sm text-slate-500 mt-1">Quem tem prioridade na vinculação</div>
                </a>
                <a href="{{ route('admin.rotas.index') }}" class="rounded-xl border border-line p-4 hover:bg-mist transition">
                    <div class="font-semibold">Cargas vinculadas</div>
                    <div class="text-sm text-slate-500 mt-1">Histórico do que o robô pegou</div>
                </a>
            </div>
        </div>

        <div class="panel-pad bg-ink text-white relative overflow-hidden">
            <div class="absolute inset-0 opacity-50 pointer-events-none"
                 style="background: radial-gradient(circle at 85% 20%, rgba(13,122,111,.55), transparent 45%);"></div>
            <div class="relative">
                <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand-soft">Dica</p>
                <h2 class="font-display text-2xl mt-2 mb-3">Clusters precisam bater com o portal</h2>
                <p class="text-sm text-slate-300 leading-relaxed">
                    O nome do destino do motorista deve ser igual ao cluster do e-Fornecedores
                    (ex.: <span class="text-white font-semibold">MCA -> SP-GUARULHOS</span>).
                    Sem isso, o robô encontra cargas mas não vincula.
                </p>
                <a href="{{ route('admin.parametros.index') }}" class="btn-primary mt-6">Ajustar destinos</a>
            </div>
        </div>
    </div>
@endsection
