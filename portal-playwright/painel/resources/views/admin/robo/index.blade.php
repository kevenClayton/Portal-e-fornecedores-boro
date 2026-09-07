@extends('layouts.admin')

@section('title', 'Robô')

@section('content')
    <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
            <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Operação</p>
            <h1 class="page-title font-display mt-1">Controle do robô</h1>
            <p class="page-subtitle">Ligue, acompanhe e leia os logs do container <strong>{{ $status['name'] ?? config('robo.container_name') }}</strong>.</p>
        </div>
        <div class="flex flex-wrap gap-2">
            <form method="POST" action="{{ route('admin.robo.start') }}">
                @csrf
                <button class="btn-success">Iniciar robô</button>
            </form>
            <form method="POST" action="{{ route('admin.robo.stop') }}">
                @csrf
                <button class="btn-danger">Parar robô</button>
            </form>
            <button type="button" id="btn-refresh-logs" class="btn-secondary">Atualizar logs</button>
        </div>
    </div>

    <div class="grid lg:grid-cols-3 gap-5 mb-5">
        <div class="panel-pad lg:col-span-1">
            <div class="text-xs font-bold uppercase tracking-wide text-slate-500">Status atual</div>
            <div class="mt-3">
                @if ($status['running'] ?? false)
                    <span class="badge-ok">Em execução</span>
                @else
                    <span class="badge-warn">Parado</span>
                @endif
            </div>
            <p class="mt-4 text-lg font-semibold leading-snug">{{ $status['message'] ?? '—' }}</p>
            <dl class="mt-5 space-y-2 text-sm">
                <div class="flex justify-between gap-3 border-t border-line pt-2">
                    <dt class="text-slate-500">Estado</dt>
                    <dd class="font-semibold">{{ $status['status'] ?? 'unknown' }}</dd>
                </div>
                <div class="flex justify-between gap-3 border-t border-line pt-2">
                    <dt class="text-slate-500">Container</dt>
                    <dd class="font-semibold break-all text-right">{{ $status['name'] ?? config('robo.container_name') }}</dd>
                </div>
            </dl>
            <p class="mt-5 text-xs text-slate-500 leading-relaxed">
                Com o robô ligado, ele entra no portal, lista cargas e tenta vincular motoristas ativos da fila.
            </p>
        </div>

        <div class="panel overflow-hidden lg:col-span-2 bg-ink text-slate-100">
            <div class="px-5 py-4 border-b border-white/10 flex items-center justify-between gap-3">
                <div>
                    <div class="text-xs font-bold uppercase tracking-wide text-slate-400">Logs em tempo quase real</div>
                    <div class="text-sm text-slate-300 mt-0.5">Últimas linhas do container</div>
                </div>
                <span id="logs-hint" class="text-xs text-slate-400"></span>
            </div>
            <pre id="robo-logs" class="px-5 py-4 text-[12px] leading-relaxed whitespace-pre-wrap overflow-auto max-h-[28rem] font-mono">{{ $logs }}</pre>
        </div>
    </div>
@endsection

@push('scripts')
@endpush

<script>
    document.getElementById('btn-refresh-logs')?.addEventListener('click', async () => {
        const pre = document.getElementById('robo-logs');
        const hint = document.getElementById('logs-hint');
        hint.textContent = 'Atualizando...';
        try {
            const response = await fetch(@json(route('admin.robo.logs')));
            const data = await response.json();
            pre.textContent = data.ok ? data.logs : (data.message || 'Erro ao carregar logs');
            hint.textContent = data.ok ? 'Atualizado agora' : 'Falha';
        } catch (erro) {
            pre.textContent = String(erro);
            hint.textContent = 'Falha';
        }
    });
</script>
