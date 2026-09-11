@extends('layouts.admin')

@section('title', 'Robô')

@push('styles')
<style>
    .etapa-pill { display: inline-flex; align-items: center; border-radius: 0.5rem; padding: 0.25rem 0.625rem; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.04em; }
    .etapa-parado { color: #5b6f7c; background: var(--mist); }
    .etapa-login { color: #1d4ed8; background: #eff6ff; }
    .etapa-busca { color: var(--accent-hover); background: var(--accent-soft); }
    .etapa-filtro { color: #6d28d9; background: #f5f3ff; }
    .etapa-detalhe { color: #9a3412; background: #fff7ed; }
    .etapa-vinculo { color: var(--ok); background: var(--ok-soft); }
    .etapa-erro { color: var(--danger); background: var(--danger-soft); }
    .etapa-info { color: var(--ink-soft); background: var(--mist); }
    .slot-card { border-radius: 0.9rem; border: 1px solid var(--line); padding: 0.9rem 1rem; background: #fff; transition: .15s ease; }
    .slot-card.is-on { border-color: #abefc6; background: var(--ok-soft); }
    .slot-card.is-off { background: #f8fafb; }
    .slot-card.is-out { opacity: .55; }
    .slot-dot { display: inline-block; height: 0.55rem; width: 0.55rem; border-radius: 9999px; }
    .slot-dot.is-on { background: var(--ok); box-shadow: 0 0 0 3px rgba(6, 118, 71, .18); }
    .slot-dot.is-off { background: #94a3b8; }
    .qty-option { flex: 1; border-radius: 0.75rem; border: 1px solid var(--line); padding: 0.625rem 0.75rem; text-align: center; font-size: 0.875rem; font-weight: 700; cursor: pointer; background: #fff; transition: .15s ease; }
    .qty-option:has(input:checked) { border-color: var(--accent); background: var(--accent-soft); color: var(--accent-hover); box-shadow: 0 0 0 3px rgba(13, 122, 111, .12); }
    .qty-option input { position: absolute; width: 1px; height: 1px; padding: 0; margin: -1px; overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap; border: 0; }
    .timeline-rail { position: relative; }
    .timeline-rail::before { content: ''; position: absolute; left: 0.5rem; top: 0.5rem; bottom: 0.5rem; width: 1px; background: var(--line); }
    .timeline-item { position: relative; padding: 0.75rem 0 0.75rem 1.25rem; }
    .timeline-item::before { content: ''; position: absolute; left: 0.3125rem; top: 1.15rem; width: 7px; height: 7px; border-radius: 9999px; background: var(--accent); box-shadow: 0 0 0 3px var(--accent-soft); }
    .robo-tabs { display: flex; flex-wrap: wrap; gap: 0.35rem; border-bottom: 1px solid var(--line); padding-bottom: 0.35rem; }
    .robo-tab { border: 1px solid transparent; background: transparent; border-radius: 0.75rem; padding: 0.55rem 0.9rem; font-size: 0.875rem; font-weight: 700; color: #5b6f7c; cursor: pointer; transition: .15s ease; }
    .robo-tab:hover { background: var(--mist); color: var(--ink); }
    .robo-tab.is-active { background: var(--accent-soft); color: var(--accent-hover); border-color: rgba(13, 122, 111, 0.25); }
    .robo-tab-panel[hidden] { display: none !important; }
    .slot-tabs { display: flex; gap: 0.35rem; flex-wrap: wrap; }
    .slot-tab { border: 1px solid rgba(255,255,255,.12); background: transparent; color: #94a3b8; border-radius: 0.65rem; padding: 0.4rem 0.85rem; font-size: 0.8rem; font-weight: 700; cursor: pointer; }
    .slot-tab.is-active { background: rgba(13, 122, 111, .35); color: #fff; border-color: rgba(216, 240, 236, .35); }
    .meta-row { display: grid; grid-template-columns: 6.5rem 1fr; gap: 0.5rem; padding: 0.55rem 0; border-top: 1px solid var(--line); font-size: 0.875rem; }
    .meta-row dt { color: #5b6f7c; font-weight: 600; }
    .meta-row dd { font-weight: 600; text-align: right; word-break: break-word; }
</style>
@endpush

@section('content')
    @php
        $etapaAtual = $acompanhamento->etapa ?? 'parado';
        $horaLigar = old('robo_hora_ligar', substr((string) ($parametro->robo_hora_ligar ?? '06:00:00'), 0, 5));
        $horaDesligar = old('robo_hora_desligar', substr((string) ($parametro->robo_hora_desligar ?? '22:00:00'), 0, 5));
        $qtdAtual = (int) old('robo_quantidade', $parametro->robo_quantidade ?? 1);
        $maxRobos = max(1, (int) ($maxRobos ?? 1));
        $qtdAtual = max(1, min($maxRobos, $qtdAtual));
        $intervaloAtual = (int) old('intervalo_espera_seg', $parametro->intervalo_espera_seg ?? 15);
        $labelsEtapa = [
            'parado' => 'Parado',
            'login' => 'Login',
            'busca' => 'Buscando cargas',
            'filtro' => 'Filtrando clusters',
            'detalhe' => 'Detalhe da carga',
            'vinculo' => 'Vinculação',
            'erro' => 'Erro',
            'info' => 'Em operação',
        ];
        $runningCount = (int) ($status['running_count'] ?? 0);
        $frotaLigada = $runningCount > 0;
    @endphp

    <div class="mb-5 flex flex-wrap items-end justify-between gap-4">
        <div>
            <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Operação</p>
            <h1 class="page-title font-display mt-1">Controle do robô</h1>
            <p class="page-subtitle">Frota, agenda, timeline, captura e terminal por robô. Máximo deste cliente: {{ $maxRobos }} robô(s).</p>
        </div>
        <div class="flex flex-wrap items-center gap-2">
            <span id="refresh-hint" class="text-xs text-slate-500 mr-1">Atualização manual</span>
            <button type="button" id="btn-atualizar" class="btn-primary">Atualizar</button>
            <form method="POST" action="{{ route('admin.robo.stop') }}">
                @csrf
                <button type="submit" id="btn-parar-frota" class="btn-danger" @disabled(! $frotaLigada)>Parar frota</button>
            </form>
        </div>
    </div>

    <div class="robo-tabs mb-5" role="tablist" aria-label="Seções do robô">
        <button type="button" class="robo-tab is-active" role="tab" aria-selected="true" data-tab="status">Status</button>
        <button type="button" class="robo-tab" role="tab" aria-selected="false" data-tab="timeline">Linha do tempo</button>
        <button type="button" class="robo-tab" role="tab" aria-selected="false" data-tab="captura">Captura de tela</button>
        <button type="button" class="robo-tab" role="tab" aria-selected="false" data-tab="terminal">Terminal</button>
    </div>

    {{-- Aba Status --}}
    <div class="robo-tab-panel space-y-5" data-panel="status" role="tabpanel">
        {{-- 1) Frota --}}
        <section class="panel-pad">
            <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
                <div>
                    <h2 class="font-display text-xl">Frota</h2>
                    <p class="text-sm text-slate-500 mt-0.5">Estado de cada container</p>
                </div>
                <div class="flex flex-wrap items-center gap-2">
                    @if ($frotaLigada)
                        <span id="frota-badge" class="badge-ok">{{ $runningCount }} / {{ $quantidade }} ligado(s)</span>
                    @else
                        <span id="frota-badge" class="badge-warn">Frota parada</span>
                    @endif
                    <span id="cadencia-badge" class="badge-muted">
                        Busca a cada {{ $intervaloAtual }}s
                    </span>
                </div>
            </div>
            <div id="frota-slots" class="grid sm:grid-cols-3 gap-3">
                @for ($slot = 1; $slot <= 3; $slot++)
                    @php
                        $robot = collect($status['robots'] ?? [])->firstWhere('slot', $slot)
                            ?? collect($status['robots'] ?? [])->values()->get($slot - 1);
                        $ligado = (bool) ($robot['running'] ?? false);
                        $ativoNaFrota = $slot <= $quantidade;
                    @endphp
                    <div class="slot-card {{ $ligado ? 'is-on' : 'is-off' }} {{ $ativoNaFrota ? '' : 'is-out' }}"
                         data-slot="{{ $slot }}"
                         data-ativo="{{ $ativoNaFrota ? '1' : '0' }}">
                        <div class="flex items-center justify-between gap-2">
                            <span class="text-base font-bold">Robô {{ $slot }}</span>
                            <span class="slot-dot {{ $ligado ? 'is-on' : 'is-off' }}" data-dot></span>
                        </div>
                        <p class="mt-2 text-sm font-semibold" data-estado>
                            @if (! $ativoNaFrota)
                                Fora da frota
                            @elseif ($ligado)
                                Ligado
                            @else
                                Parado
                            @endif
                        </p>
                        <p class="mt-1 text-xs text-slate-500" data-nome>
                            {{ $robot['name'] ?? 'portal-fornecedores'.($slot > 1 ? "-{$slot}" : '') }}
                        </p>
                    </div>
                @endfor
            </div>
        </section>

        <div class="grid lg:grid-cols-12 gap-5">
            {{-- 2) Atividade --}}
            <section class="panel-pad lg:col-span-5 space-y-1">
                <div class="mb-3">
                    <h2 class="font-display text-xl">Atividade</h2>
                    <p class="text-sm text-slate-500 mt-0.5">Último status publicado no banco</p>
                </div>
                <div class="flex flex-wrap items-center gap-2 mb-3">
                    <span id="acomp-etapa" class="etapa-pill etapa-{{ $etapaAtual }}">
                        {{ $labelsEtapa[$etapaAtual] ?? 'Em operação' }}
                    </span>
                    <span class="text-xs text-slate-500">
                        às <span id="acomp-quando" class="font-semibold text-ink">{{ optional($acompanhamento?->atualizado_em)->timezone(config('app.timezone'))->format('H:i:s') ?: '—' }}</span>
                    </span>
                </div>
                <p id="acomp-mensagem" class="text-base font-semibold leading-snug text-ink mb-3">
                    {{ $acompanhamento->mensagem ?? 'Aguardando início' }}
                </p>
                <dl>
                    <div class="meta-row">
                        <dt>Documento</dt>
                        <dd id="acomp-doc">{{ $acompanhamento->documento_atual ?: '—' }}</dd>
                    </div>
                    <div class="meta-row">
                        <dt>Cluster</dt>
                        <dd id="acomp-cluster">{{ $acompanhamento->cluster_atual ?: '—' }}</dd>
                    </div>
                    <div class="meta-row">
                        <dt>Resumo</dt>
                        <dd id="acomp-resumo" class="!text-xs !font-semibold">{{ $acompanhamento->resumo_ciclo ?: '—' }}</dd>
                    </div>
                </dl>
            </section>

            {{-- 3) Controles --}}
            <div class="lg:col-span-7 space-y-5">
                <form method="POST" action="{{ route('admin.robo.start') }}" class="panel-pad space-y-4" id="form-iniciar">
                    @csrf
                    <div>
                        <h2 class="font-display text-xl">Iniciar / reiniciar</h2>
                        <p class="text-sm text-slate-500 mt-0.5">Quantidade e cadência da frota</p>
                    </div>
                    <div class="grid sm:grid-cols-2 gap-4">
                        <div>
                            <label class="field-label">Robôs</label>
                            <div class="flex gap-2" id="qty-group">
                                @foreach (range(1, max(1, (int) ($maxRobos ?? 1))) as $opcao)
                                    <label class="qty-option">
                                        <input type="radio" name="robo_quantidade" value="{{ $opcao }}"
                                               @checked($qtdAtual === $opcao) required>
                                        {{ $opcao }}
                                    </label>
                                @endforeach
                            </div>
                        </div>
                        <div>
                            <label class="field-label" for="intervalo_espera_seg">Intervalo (s)</label>
                            <input type="number" min="5" max="3600" name="intervalo_espera_seg" id="intervalo_espera_seg"
                                   value="{{ $intervaloAtual }}"
                                   class="field-input" required>
                        </div>
                    </div>
                    <p id="cadencia-preview" class="rounded-xl bg-mist border border-line px-3 py-2 text-xs text-slate-600 leading-relaxed">—</p>
                    <div class="rounded-xl border border-line bg-mist/40 p-3 space-y-2">
                        <p class="text-[11px] font-bold uppercase tracking-[0.14em] text-slate-500">Detalhes da carga</p>
                        <div class="flex flex-wrap gap-x-4 gap-y-2">
                            <label class="inline-flex items-center gap-2 text-sm font-semibold">
                                <input type="checkbox" name="verificar_valor_carga" value="1" class="rounded border-line text-brand focus:ring-brand"
                                       @checked(old('verificar_valor_carga', $parametro->verificar_valor_carga ?? true))>
                                Valor
                            </label>
                            <label class="inline-flex items-center gap-2 text-sm font-semibold">
                                <input type="checkbox" name="verificar_bobina" value="1" class="rounded border-line text-brand focus:ring-brand"
                                       @checked(old('verificar_bobina', $parametro->verificar_bobina ?? true))>
                                Bobina
                            </label>
                            <label class="inline-flex items-center gap-2 text-sm font-semibold">
                                <input type="checkbox" name="verificar_multiplos_destinos" value="1" class="rounded border-line text-brand focus:ring-brand"
                                       @checked(old('verificar_multiplos_destinos', $parametro->verificar_multiplos_destinos ?? true))>
                                Destinos
                            </label>
                        </div>
                    </div>
                    <button type="submit" id="btn-iniciar-frota" class="btn-success w-full">{{ $frotaLigada ? 'Reiniciar frota' : 'Iniciar frota' }}</button>
                </form>

                <form method="POST" action="{{ route('admin.robo.agenda') }}" class="panel-pad space-y-4">
                    @csrf
                    <div class="flex items-start justify-between gap-3">
                        <div>
                            <h2 class="font-display text-xl">Agenda</h2>
                            <p class="text-sm text-slate-500 mt-0.5">Horário de Brasília</p>
                        </div>
                        @if ($parametro->robo_agenda_ativa ?? false)
                            <span class="badge-ok shrink-0">Ativa</span>
                        @else
                            <span class="badge-muted shrink-0">Off</span>
                        @endif
                    </div>
                    <label class="flex items-center gap-3 text-sm font-semibold">
                        <input type="checkbox" name="robo_agenda_ativa" value="1" class="rounded border-line text-brand focus:ring-brand"
                               @checked(old('robo_agenda_ativa', $parametro->robo_agenda_ativa ?? false))>
                        Ligar e desligar automaticamente
                    </label>
                    <div class="grid grid-cols-2 gap-3">
                        <div>
                            <label class="field-label">Ligar</label>
                            <input type="time" name="robo_hora_ligar" value="{{ $horaLigar }}" class="field-input" required>
                        </div>
                        <div>
                            <label class="field-label">Desligar</label>
                            <input type="time" name="robo_hora_desligar" value="{{ $horaDesligar }}" class="field-input" required>
                        </div>
                    </div>
                    <button class="btn-secondary w-full">Salvar agenda</button>
                </form>
            </div>
        </div>
    </div>

    {{-- Aba Linha do tempo --}}
    <div class="robo-tab-panel" data-panel="timeline" role="tabpanel" hidden>
        <div class="panel overflow-hidden">
            <div class="px-5 py-4 border-b border-line flex items-center justify-between gap-3">
                <div>
                    <div class="text-xs font-bold uppercase tracking-wide text-slate-500">Linha do tempo</div>
                    <div class="text-sm text-slate-500 mt-0.5">Eventos da frota (R1–R3)</div>
                </div>
                <span class="badge-muted">40 últimos</span>
            </div>
            <ol id="acomp-eventos" class="timeline-rail max-h-[70vh] overflow-auto px-4 py-1">
                @forelse ($eventos as $evento)
                    @php
                        $mensagemEvento = (string) $evento->mensagem;
                        $slotMatch = [];
                        preg_match('/\[R([1-3])\]\s*(.*)/u', $mensagemEvento, $slotMatch);
                        $slotEvento = $slotMatch[1] ?? null;
                        $textoEvento = $slotMatch[2] ?? $mensagemEvento;
                        $etapaEvento = $evento->etapa ?? 'info';
                    @endphp
                    <li class="timeline-item text-sm">
                        <div class="flex items-center justify-between gap-2 flex-wrap">
                            <div class="flex items-center gap-2 min-w-0">
                                @if ($slotEvento)
                                    <span class="inline-flex h-5 min-w-5 items-center justify-center rounded-md bg-ink px-1.5 text-[10px] font-bold text-white">R{{ $slotEvento }}</span>
                                @endif
                                <span class="etapa-pill etapa-{{ $etapaEvento }}">{{ $labelsEtapa[$etapaEvento] ?? $etapaEvento }}</span>
                            </div>
                            <span class="text-xs text-slate-400 tabular-nums">{{ optional($evento->created_at)->timezone(config('app.timezone'))->format('H:i:s') }}</span>
                        </div>
                        <p class="mt-1.5 text-ink/90 leading-snug">{{ $textoEvento }}</p>
                    </li>
                @empty
                    <li class="px-3 py-10 text-sm text-slate-500 text-center">Sem eventos ainda. Inicie a frota.</li>
                @endforelse
            </ol>
        </div>
    </div>

    {{-- Aba Captura --}}
    <div class="robo-tab-panel" data-panel="captura" role="tabpanel" hidden>
        <div class="panel overflow-hidden">
            <div class="px-5 py-4 border-b border-line flex flex-wrap items-center justify-between gap-3">
                <div>
                    <div class="text-xs font-bold uppercase tracking-wide text-slate-500">Tela do Chrome</div>
                    <div id="shot-hint" class="text-sm text-slate-500 mt-0.5">Última captura do servidor</div>
                </div>
                <button type="button" id="btn-pedir-screenshot" class="btn-secondary">Capturar tela</button>
            </div>
            <div class="bg-mist p-4 md:p-6">
                <img id="robo-screenshot"
                     src="{{ route('admin.robo.screenshot') }}?t={{ time() }}"
                     alt="Screenshot do robô"
                     class="w-full max-w-5xl mx-auto rounded-xl border border-line bg-white min-h-[16rem] max-h-[75vh] object-contain"
                     onerror="this.style.opacity=0.35; this.alt='Screenshot ainda não disponível';">
            </div>
        </div>
    </div>

    {{-- Aba Terminal --}}
    <div class="robo-tab-panel" data-panel="terminal" role="tabpanel" hidden>
        <div class="panel overflow-hidden bg-ink text-slate-100">
            <div class="px-5 py-4 border-b border-white/10 space-y-3">
                <div class="flex flex-wrap items-center justify-between gap-3">
                    <div>
                        <div class="text-xs font-bold uppercase tracking-wide text-slate-400">Terminal</div>
                        <div class="text-sm text-slate-300 mt-0.5">Logs de um robô por vez</div>
                    </div>
                    <div class="flex flex-wrap items-center gap-3">
                        <label class="inline-flex items-center gap-2 text-sm font-semibold text-slate-200 cursor-pointer select-none">
                            <input type="checkbox" id="terminal-auto-refresh" class="rounded border-slate-500 text-brand focus:ring-brand">
                            <span>Auto 15s</span>
                        </label>
                        <span id="logs-hint" class="text-xs text-slate-400">Manual</span>
                    </div>
                </div>
                <div class="slot-tabs" role="tablist" aria-label="Robô do terminal">
                    <button type="button" class="slot-tab is-active" data-slot-tab="1">Robô 1</button>
                    <button type="button" class="slot-tab" data-slot-tab="2">Robô 2</button>
                    <button type="button" class="slot-tab" data-slot-tab="3">Robô 3</button>
                </div>
            </div>
            <pre id="robo-logs" class="px-5 py-4 text-[12px] leading-relaxed whitespace-pre-wrap overflow-auto max-h-[70vh] font-mono">Selecione um robô para carregar os logs.</pre>
        </div>
    </div>
@endsection

@push('scripts')
<script>
(() => {
    const csrf = document.querySelector('meta[name="csrf-token"]')?.content;
    const urlLogs = @json(route('admin.robo.logs'));
    const urlAcomp = @json(route('admin.robo.acompanhamento'));
    const urlPedirShot = @json(route('admin.robo.screenshot.pedir'));
    const urlShot = @json(route('admin.robo.screenshot'));
    const labels = @json($labelsEtapa);

    const pre = document.getElementById('robo-logs');
    const hint = document.getElementById('logs-hint');
    const refreshHint = document.getElementById('refresh-hint');
    const img = document.getElementById('robo-screenshot');
    const shotHint = document.getElementById('shot-hint');
    const listaEventos = document.getElementById('acomp-eventos');
    const etapaEl = document.getElementById('acomp-etapa');
    const frotaBadge = document.getElementById('frota-badge');
    const cadenciaBadge = document.getElementById('cadencia-badge');
    const cadenciaPreview = document.getElementById('cadencia-preview');
    const intervaloInput = document.getElementById('intervalo_espera_seg');
    const autoRefreshInput = document.getElementById('terminal-auto-refresh');
    const tabs = Array.from(document.querySelectorAll('.robo-tab'));
    const panels = Array.from(document.querySelectorAll('.robo-tab-panel'));
    const slotTabs = Array.from(document.querySelectorAll('[data-slot-tab]'));

    let carregando = false;
    let abaAtual = 'status';
    let slotTerminal = 1;
    let timerAutoRefresh = null;
    const btnAtualizar = document.getElementById('btn-atualizar');

    function horarioAgora() {
        return new Date().toLocaleTimeString('pt-BR', {
            hour: '2-digit', minute: '2-digit', second: '2-digit', timeZone: 'America/Sao_Paulo',
        });
    }

    function quantidadeSelecionada() {
        const marcado = document.querySelector('input[name="robo_quantidade"]:checked');
        return Math.max(1, Math.min(3, parseInt(marcado?.value || '1', 10)));
    }

    function atualizarCadenciaUi() {
        const quantidade = quantidadeSelecionada();
        const intervalo = Math.max(5, parseInt(intervaloInput?.value || '15', 10) || 15);
        const espera = intervalo * quantidade;
        const texto = quantidade === 1
            ? `1 robô · busca a cada ${intervalo}s`
            : `${quantidade} robôs · frota a cada ${intervalo}s · cada um espera ${espera}s (defasados)`;
        if (cadenciaPreview) cadenciaPreview.textContent = texto;
        if (cadenciaBadge) cadenciaBadge.textContent = `Busca a cada ${intervalo}s`;
    }

    function classeEtapa(etapa) {
        const chave = labels[etapa] ? etapa : 'info';
        return `etapa-pill etapa-${chave}`;
    }

    function parseMensagem(mensagem) {
        const texto = String(mensagem || '');
        const match = texto.match(/^\[R([1-3])\]\s*(.*)$/s);
        if (match) return { slot: match[1], texto: match[2] };
        return { slot: null, texto };
    }

    function escapeHtml(valor) {
        return String(valor || '')
            .replaceAll('&', '&amp;')
            .replaceAll('<', '&lt;')
            .replaceAll('>', '&gt;')
            .replaceAll('"', '&quot;');
    }

    function renderEventos(eventos) {
        if (!listaEventos) return;
        if (!eventos.length) {
            listaEventos.innerHTML = '<li class="px-3 py-10 text-sm text-slate-500 text-center">Sem eventos ainda. Inicie a frota.</li>';
            return;
        }
        listaEventos.innerHTML = eventos.map((evento) => {
            const parseado = parseMensagem(evento.mensagem);
            const etapa = evento.etapa || 'info';
            const slotHtml = parseado.slot
                ? `<span class="inline-flex h-5 min-w-5 items-center justify-center rounded-md bg-ink px-1.5 text-[10px] font-bold text-white">R${parseado.slot}</span>`
                : '';
            return `
                <li class="timeline-item text-sm">
                    <div class="flex items-center justify-between gap-2 flex-wrap">
                        <div class="flex items-center gap-2 min-w-0">
                            ${slotHtml}
                            <span class="${classeEtapa(etapa)}">${labels[etapa] || etapa}</span>
                        </div>
                        <span class="text-xs text-slate-400 tabular-nums">${evento.horario || ''}</span>
                    </div>
                    <p class="mt-1.5 text-ink/90 leading-snug">${escapeHtml(parseado.texto)}</p>
                </li>
            `;
        }).join('');
    }

    function atualizarFrota(status, quantidade) {
        const robots = Array.isArray(status?.robots) ? status.robots : [];
        const runningCount = Number(status?.running_count || 0);
        const maxRobos = Number(@json((int) ($maxRobos ?? 1))) || 1;
        const qtd = Math.max(1, Math.min(maxRobos, Number(quantidade || quantidadeSelecionada())));
        const frotaLigada = runningCount > 0;

        const btnParar = document.getElementById('btn-parar-frota');
        if (btnParar) btnParar.disabled = !frotaLigada;

        const btnIniciar = document.getElementById('btn-iniciar-frota');
        if (btnIniciar) btnIniciar.textContent = frotaLigada ? 'Reiniciar frota' : 'Iniciar frota';

        if (frotaBadge) {
            if (frotaLigada) {
                frotaBadge.className = 'badge-ok';
                frotaBadge.textContent = `${runningCount} / ${qtd} ligado(s)`;
            } else {
                frotaBadge.className = 'badge-warn';
                frotaBadge.textContent = 'Frota parada';
            }
        }

        document.querySelectorAll('#frota-slots .slot-card').forEach((card) => {
            const slot = Number(card.dataset.slot);
            const robot = robots.find((item) => Number(item.slot) === slot) || robots[slot - 1] || null;
            const ligado = Boolean(robot?.running);
            const ativoNaFrota = slot <= qtd;
            card.classList.toggle('is-on', ligado);
            card.classList.toggle('is-off', !ligado);
            card.classList.toggle('is-out', !ativoNaFrota);
            card.dataset.ativo = ativoNaFrota ? '1' : '0';
            const dot = card.querySelector('[data-dot]');
            const estado = card.querySelector('[data-estado]');
            const nome = card.querySelector('[data-nome]');
            if (dot) {
                dot.classList.toggle('is-on', ligado);
                dot.classList.toggle('is-off', !ligado);
            }
            if (estado) {
                if (!ativoNaFrota) estado.textContent = 'Fora da frota';
                else estado.textContent = ligado ? 'Ligado' : 'Parado';
            }
            if (nome && robot?.name) nome.textContent = robot.name;
        });
    }

    function ativarSlotTerminal(slot) {
        slotTerminal = Math.max(1, Math.min(3, Number(slot) || 1));
        slotTabs.forEach((tab) => {
            tab.classList.toggle('is-active', Number(tab.dataset.slotTab) === slotTerminal);
        });
        try { localStorage.setItem('robo_terminal_slot', String(slotTerminal)); } catch (_) {}
        if (abaAtual === 'terminal') atualizarLogs();
    }

    async function atualizarLogs() {
        if (!pre || !hint) return;
        const noFundo = pre.scrollHeight - pre.scrollTop - pre.clientHeight < 40;
        hint.textContent = `Carregando R${slotTerminal}...`;
        const response = await fetch(`${urlLogs}?slot=${slotTerminal}&tail=100`, {
            headers: { Accept: 'application/json' },
        });
        const data = await response.json();
        pre.textContent = data.ok ? data.logs : (data.message || 'Erro ao carregar logs');
        if (noFundo) pre.scrollTop = pre.scrollHeight;
        hint.textContent = data.ok ? `R${slotTerminal} · ${horarioAgora()}` : 'Falha';
    }

    async function atualizarAcompanhamento() {
        const response = await fetch(urlAcomp, { headers: { Accept: 'application/json' } });
        const data = await response.json();
        if (!data.ok) return;
        const acomp = data.acompanhamento || {};
        const etapa = acomp.etapa || 'info';

        if (etapaEl) {
            etapaEl.className = classeEtapa(etapa);
            etapaEl.textContent = acomp.etapa_label || labels[etapa] || etapa;
        }
        document.getElementById('acomp-mensagem').textContent = acomp.mensagem || '—';
        document.getElementById('acomp-doc').textContent = acomp.documento_atual || '—';
        document.getElementById('acomp-cluster').textContent = acomp.cluster_atual || '—';
        document.getElementById('acomp-resumo').textContent = acomp.resumo_ciclo || '—';
        document.getElementById('acomp-quando').textContent = (acomp.atualizado_em || '—').split(' ').pop();

        if (Array.isArray(data.eventos)) renderEventos(data.eventos);
        if (data.status) atualizarFrota(data.status, data.quantidade);

        if (acomp.tem_screenshot && img) {
            img.style.opacity = 1;
            img.src = `${urlShot}?t=${Date.now()}`;
            if (shotHint) {
                shotHint.textContent = acomp.screenshot_em ? `Captura: ${acomp.screenshot_em}` : 'Última captura do servidor';
            }
        }
    }

    async function atualizarTudo(opcoes = {}) {
        if (carregando) return;
        carregando = true;
        const soLogs = Boolean(opcoes.soLogs);
        const incluirLogs = soLogs || abaAtual === 'terminal';
        if (btnAtualizar && !soLogs) {
            btnAtualizar.disabled = true;
            btnAtualizar.textContent = 'Atualizando...';
        }
        if (hint && incluirLogs) hint.textContent = 'Atualizando...';
        if (refreshHint && !soLogs) refreshHint.textContent = 'Atualizando...';
        try {
            if (soLogs) await atualizarLogs();
            else if (incluirLogs) await Promise.all([atualizarAcompanhamento(), atualizarLogs()]);
            else await atualizarAcompanhamento();
            if (refreshHint && !soLogs) refreshHint.textContent = `Painel: ${horarioAgora()}`;
        } catch (erro) {
            if (hint) hint.textContent = 'Falha';
            if (refreshHint && !soLogs) refreshHint.textContent = 'Falha ao atualizar';
            if (pre && incluirLogs) pre.textContent = String(erro);
            console.warn(erro);
        } finally {
            carregando = false;
            if (btnAtualizar && !soLogs) {
                btnAtualizar.disabled = false;
                btnAtualizar.textContent = 'Atualizar';
            }
        }
    }

    function pararAutoRefresh() {
        if (timerAutoRefresh) {
            clearInterval(timerAutoRefresh);
            timerAutoRefresh = null;
        }
    }

    function sincronizarAutoRefresh() {
        pararAutoRefresh();
        if (!(autoRefreshInput?.checked && abaAtual === 'terminal')) return;
        if (hint) hint.textContent = `Auto 15s · R${slotTerminal}`;
        atualizarLogs();
        timerAutoRefresh = setInterval(() => {
            if (abaAtual !== 'terminal' || !autoRefreshInput?.checked) {
                pararAutoRefresh();
                return;
            }
            atualizarTudo({ soLogs: true });
        }, 15000);
    }

    function ativarAba(nome) {
        abaAtual = nome;
        tabs.forEach((tab) => {
            const ativa = tab.dataset.tab === nome;
            tab.classList.toggle('is-active', ativa);
            tab.setAttribute('aria-selected', ativa ? 'true' : 'false');
        });
        panels.forEach((panel) => {
            panel.hidden = panel.dataset.panel !== nome;
        });
        if (nome === 'terminal') {
            atualizarLogs();
            sincronizarAutoRefresh();
        } else {
            pararAutoRefresh();
        }
        try { localStorage.setItem('robo_aba', nome); } catch (_) {}
    }

    tabs.forEach((tab) => tab.addEventListener('click', () => ativarAba(tab.dataset.tab)));
    slotTabs.forEach((tab) => tab.addEventListener('click', () => ativarSlotTerminal(tab.dataset.slotTab)));

    autoRefreshInput?.addEventListener('change', () => {
        try { localStorage.setItem('robo_terminal_auto', autoRefreshInput.checked ? '1' : '0'); } catch (_) {}
        sincronizarAutoRefresh();
    });

    btnAtualizar?.addEventListener('click', () => atualizarTudo());
    document.getElementById('btn-pedir-screenshot')?.addEventListener('click', async () => {
        if (shotHint) shotHint.textContent = 'Pedindo captura...';
        try {
            const response = await fetch(urlPedirShot, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'X-CSRF-TOKEN': csrf,
                    'X-Requested-With': 'XMLHttpRequest',
                },
            });
            const data = await response.json();
            if (shotHint) shotHint.textContent = (data.message || 'Pedido enviado') + ' — atualizando em alguns segundos';
            setTimeout(() => atualizarTudo(), 3500);
        } catch (erro) {
            if (shotHint) shotHint.textContent = String(erro);
        }
    });

    document.querySelectorAll('input[name="robo_quantidade"]').forEach((input) => {
        input.addEventListener('change', atualizarCadenciaUi);
    });
    intervaloInput?.addEventListener('input', atualizarCadenciaUi);
    atualizarCadenciaUi();

    try {
        if (localStorage.getItem('robo_terminal_auto') === '1' && autoRefreshInput) {
            autoRefreshInput.checked = true;
        }
        const slotSalvo = Number(localStorage.getItem('robo_terminal_slot') || '1');
        ativarSlotTerminal(slotSalvo);
        const abaSalva = localStorage.getItem('robo_aba');
        if (abaSalva && ['status', 'timeline', 'captura', 'terminal'].includes(abaSalva)) {
            ativarAba(abaSalva);
        }
    } catch (_) {}

    atualizarAcompanhamento().catch(() => {});
})();
</script>
@endpush
