@extends('layouts.admin')

@section('title', 'Uso do robô')

@section('content')
    <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
            <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Acompanhamento</p>
            <h1 class="page-title font-display mt-1">Uso do robô</h1>
            <p class="page-subtitle">Auditoria leve: decisões por carga e captchas. Retenção automática de 15 dias.</p>
        </div>
    </div>

    <div class="grid gap-4 sm:grid-cols-2 xl:grid-cols-4 mb-6">
        <div class="stat-card">
            <div class="text-xs font-bold uppercase tracking-wide text-slate-500">Captchas ({{ $diaLabel }})</div>
            <div class="mt-3 text-3xl font-extrabold tracking-tight">{{ $captchasHoje }}</div>
            <p class="mt-2 text-xs text-slate-500">Login {{ $captchasLogin }} · Pesquisa/Filtro {{ $captchasPesquisar }}</p>
        </div>
        <div class="stat-card">
            <div class="text-xs font-bold uppercase tracking-wide text-slate-500">Vinculadas</div>
            <div class="mt-3 text-3xl font-extrabold tracking-tight text-emerald-700">{{ $vinculadosHoje }}</div>
        </div>
        <div class="stat-card">
            <div class="text-xs font-bold uppercase tracking-wide text-slate-500">Puladas</div>
            <div class="mt-3 text-3xl font-extrabold tracking-tight">{{ $puladosHoje }}</div>
            <p class="mt-2 text-xs text-slate-500">Sem motorista / tipo incompatível</p>
        </div>
        <div class="stat-card">
            <div class="text-xs font-bold uppercase tracking-wide text-slate-500">Rejeitadas</div>
            <div class="mt-3 text-3xl font-extrabold tracking-tight text-amber-700">{{ $rejeitadosHoje }}</div>
        </div>
    </div>

    <form method="GET" class="panel-pad mb-4 grid md:grid-cols-5 gap-3">
        <div class="md:col-span-2">
            <label class="field-label">Busca (doc / destino / motivo)</label>
            <input type="text" name="q" value="{{ $busca }}" placeholder="Ex: 11079159" class="field-input">
        </div>
        <div>
            <label class="field-label">Data</label>
            <input type="date" name="data" value="{{ $data }}" class="field-input">
        </div>
        <div>
            <label class="field-label">Tipo</label>
            <select name="tipo" class="field-input">
                <option value="">Todos</option>
                <option value="decisao_carga" @selected($tipo === 'decisao_carga')>Decisão de carga</option>
                <option value="captcha" @selected($tipo === 'captcha')>Captcha</option>
            </select>
        </div>
        <div>
            <label class="field-label">Decisão</label>
            <select name="decisao" class="field-input">
                <option value="">Todas</option>
                <option value="vinculado" @selected($decisao === 'vinculado')>Vinculado</option>
                <option value="pulado" @selected($decisao === 'pulado')>Pulado</option>
                <option value="rejeitado" @selected($decisao === 'rejeitado')>Rejeitado</option>
            </select>
        </div>
        <div class="md:col-span-5 flex items-end gap-2">
            <button class="btn-primary">Filtrar</button>
            @if ($busca !== '' || $tipo !== '' || $decisao !== '' || $data !== '')
                <a href="{{ route('admin.auditoria.index') }}" class="btn-secondary">Limpar</a>
            @endif
        </div>
    </form>

    <div class="table-shell overflow-x-auto">
        <table class="data-table">
            <thead>
            <tr>
                <th>Quando</th>
                <th>Slot</th>
                <th>Evento</th>
                <th>Documento / Captcha</th>
                <th>Detalhe</th>
                <th>Motivo</th>
            </tr>
            </thead>
            <tbody>
            @forelse ($eventos as $evento)
                <tr>
                    <td class="text-slate-500 whitespace-nowrap">{{ optional($evento->created_at)?->format('d/m/Y H:i:s') }}</td>
                    <td>R{{ $evento->slot }}</td>
                    <td>
                        @if ($evento->tipo_evento === 'captcha')
                            <span class="badge-warn">Captcha</span>
                        @elseif ($evento->decisao === 'vinculado')
                            <span class="badge-ok">Vinculado</span>
                        @elseif ($evento->decisao === 'pulado')
                            <span class="badge-muted">Pulado</span>
                        @else
                            <span class="badge-warn">Rejeitado</span>
                        @endif
                    </td>
                    <td class="font-semibold">
                        @if ($evento->tipo_evento === 'captcha')
                            {{ $evento->origem_captcha ?: '—' }}
                            @if ($evento->proxy_host)
                                <div class="text-xs text-slate-500 font-normal mt-0.5">IP {{ $evento->proxy_host }} · tentativa #{{ $evento->tentativa }}</div>
                            @endif
                        @else
                            {{ $evento->doc_transporte ?: '—' }}
                            @if ($evento->tipo_veiculo)
                                <div class="text-xs text-slate-500 font-normal mt-0.5">{{ $evento->tipo_veiculo }}</div>
                            @endif
                        @endif
                    </td>
                    <td>
                        @if ($evento->tipo_evento === 'captcha')
                            —
                        @else
                            <div class="font-medium">{{ $evento->destino ?: '—' }}</div>
                        @endif
                    </td>
                    <td class="text-sm text-slate-600 max-w-md">{{ \Illuminate\Support\Str::limit($evento->motivo, 120) }}</td>
                </tr>
            @empty
                <tr>
                    <td colspan="6" class="px-4 py-12 text-center text-slate-500">
                        Nenhum evento de auditoria ainda. Eles passam a ser gravados nos próximos ciclos do robô.
                    </td>
                </tr>
            @endforelse
            </tbody>
        </table>
    </div>
    <div class="mt-4">{{ $eventos->links() }}</div>
@endsection
