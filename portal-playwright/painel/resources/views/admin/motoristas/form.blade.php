@extends('layouts.admin')

@section('title', $motorista->exists ? 'Editar motorista' : 'Novo motorista')

@push('styles')
<style>
    .form-section-title { font-family: 'Source Serif 4', Georgia, serif; font-size: 1.25rem; font-weight: 700; color: var(--ink); }
    .check-grid { display: grid; gap: 0.5rem; max-height: 16rem; overflow: auto; padding: 0.75rem; border: 1px solid var(--line); border-radius: 0.9rem; background: #fafcfd; }
    .check-grid.tall { max-height: 22rem; }
    .check-item { display: flex; align-items: flex-start; gap: 0.65rem; padding: 0.55rem 0.65rem; border-radius: 0.65rem; cursor: pointer; transition: .12s ease; }
    .check-item:hover { background: var(--accent-soft); }
    .check-item input { margin-top: 0.15rem; border-radius: 0.3rem; border-color: var(--line); color: var(--accent); }
    .check-item span { font-size: 0.875rem; font-weight: 600; line-height: 1.35; color: var(--ink); }
    .toggle-chip { display: inline-flex; align-items: center; gap: 0.55rem; padding: 0.7rem 0.9rem; border: 1px solid var(--line); border-radius: 0.85rem; background: #fff; font-size: 0.875rem; font-weight: 700; cursor: pointer; }
    .toggle-chip:has(input:checked) { border-color: var(--accent); background: var(--accent-soft); color: var(--accent-hover); }
    .sticky-actions { position: sticky; bottom: 0; z-index: 20; background: rgba(247, 250, 251, 0.92); backdrop-filter: blur(8px); border-top: 1px solid var(--line); margin: 1.5rem -1rem -1rem; padding: 1rem; }
    @media (min-width: 768px) { .sticky-actions { margin-left: 0; margin-right: 0; border-radius: 1rem; } }
</style>
@endpush

@section('content')
    @php
        $origensSelecionadas = collect(old('origens', $motorista->exists ? $motorista->origens->pluck('id') : []))->map(fn ($id) => (int) $id);
        $destinosSelecionados = collect(old('destinos', $motorista->exists ? $motorista->destinos->pluck('id') : []))->map(fn ($id) => (int) $id);
        $tiposSelecionados = collect(old('tipos_veiculo', $motorista->exists ? $motorista->tiposVeiculo->pluck('id') : []))->map(fn ($id) => (int) $id);
        $tiposCarretaSelecionados = collect(old('tipos_veiculo_carreta', $motorista->exists ? $motorista->tiposVeiculoCarreta->pluck('id') : []))->map(fn ($id) => (int) $id);
    @endphp

    <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
            <a href="{{ route('admin.motoristas.index') }}" class="text-sm font-semibold text-brand hover:underline">← Motoristas</a>
            <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand mt-3">Cadastros</p>
            <h1 class="page-title font-display mt-1">{{ $motorista->exists ? 'Editar motorista' : 'Novo motorista' }}</h1>
            <p class="page-subtitle">Dados do motorista e rotas que ele pode atender no portal.</p>
        </div>
        @if ($motorista->exists)
            <div class="flex flex-wrap gap-2">
                @if ($motorista->situacao)
                    <span class="badge-ok">Ativo</span>
                @else
                    <span class="badge-muted">Inativo</span>
                @endif
                @if ($motorista->aceita_bobina)
                    <span class="badge-muted">Aceita bobina</span>
                @endif
            </div>
        @endif
    </div>

    <form method="POST"
          action="{{ $motorista->exists ? route('admin.motoristas.update', $motorista) : route('admin.motoristas.store') }}"
          class="space-y-5 max-w-6xl" id="form-motorista">
        @csrf
        @if ($motorista->exists) @method('PUT') @endif

        <div class="grid lg:grid-cols-12 gap-5">
            <section class="panel-pad lg:col-span-5 space-y-5">
                <div>
                    <h2 class="form-section-title">Identificação</h2>
                    <p class="text-sm text-slate-500 mt-1">Como o motorista aparece na fila do robô.</p>
                </div>

                <div>
                    <label class="field-label" for="nome">Nome completo</label>
                    <input id="nome" name="nome" value="{{ old('nome', $motorista->nome) }}" required class="field-input" placeholder="Nome do motorista" autocomplete="name">
                </div>
                <div>
                    <label class="field-label" for="cpf">CPF</label>
                    <input id="cpf" name="cpf" value="{{ old('cpf', $motorista->cpf) }}" required class="field-input" placeholder="000.000.000-00" inputmode="numeric">
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div>
                        <label class="field-label" for="placa">Placa do cavalo</label>
                        <input id="placa" name="placa" value="{{ old('placa', $motorista->placa) }}" required class="field-input uppercase" placeholder="ABC1D23">
                    </div>
                    <div>
                        <label class="field-label" for="placa_carreta">Placa da carreta</label>
                        <input id="placa_carreta" name="placa_carreta" value="{{ old('placa_carreta', $motorista->placa_carreta) }}" class="field-input uppercase" placeholder="Opcional">
                    </div>
                </div>

                <div>
                    <label class="field-label" for="ordem_motorista">Ordem na fila</label>
                    <input id="ordem_motorista" type="number" name="ordem_motorista" value="{{ old('ordem_motorista', $motorista->ordem_motorista ?? 100) }}" class="field-input w-36">
                    <p class="text-xs text-slate-500 mt-1.5">Menor número = prioridade maior na vinculação.</p>
                </div>

                <div class="flex flex-wrap gap-2 pt-1">
                    <label class="toggle-chip">
                        <input type="checkbox" name="situacao" value="1" class="rounded border-line text-brand focus:ring-brand" @checked(old('situacao', $motorista->situacao ?? true))>
                        Motorista ativo
                    </label>
                    <label class="toggle-chip">
                        <input type="checkbox" name="aceita_bobina" value="1" class="rounded border-line text-brand focus:ring-brand" @checked(old('aceita_bobina', $motorista->aceita_bobina))>
                        Aceita bobina
                    </label>
                </div>
            </section>

            <div class="lg:col-span-7 space-y-5">
                <section class="panel-pad space-y-4">
                    <div class="flex flex-wrap items-end justify-between gap-3">
                        <div>
                            <h2 class="form-section-title">Origens</h2>
                            <p class="text-sm text-slate-500 mt-1">Plantas de onde ele pode sair.</p>
                        </div>
                        <span class="badge-muted" id="count-origens">0 selecionadas</span>
                    </div>
                    <div class="check-grid" data-count-target="count-origens">
                        @forelse ($origens as $origem)
                            <label class="check-item">
                                <input type="checkbox" name="origens[]" value="{{ $origem->id }}"
                                       @checked($origensSelecionadas->contains($origem->id))>
                                <span>{{ $origem->nome_origem }}</span>
                            </label>
                        @empty
                            <p class="text-sm text-slate-500 px-1 py-2">Nenhuma origem cadastrada em Parâmetros.</p>
                        @endforelse
                    </div>
                </section>

                <section class="panel-pad space-y-4">
                    <div class="flex flex-wrap items-end justify-between gap-3">
                        <div>
                            <h2 class="form-section-title">Destinos</h2>
                            <p class="text-sm text-slate-500 mt-1">Clusters exatamente como no portal.</p>
                        </div>
                        <span class="badge-muted" id="count-destinos">0 selecionados</span>
                    </div>
                    <input type="search" id="filtro-destinos" class="field-input" placeholder="Filtrar destinos…">
                    <div class="check-grid tall" id="lista-destinos" data-count-target="count-destinos">
                        @forelse ($destinos as $destino)
                            <label class="check-item" data-filter-text="{{ mb_strtolower($destino->nome_destino) }}">
                                <input type="checkbox" name="destinos[]" value="{{ $destino->id }}"
                                       @checked($destinosSelecionados->contains($destino->id))>
                                <span>{{ $destino->nome_destino }}</span>
                            </label>
                        @empty
                            <p class="text-sm text-slate-500 px-1 py-2">Nenhum destino cadastrado em Parâmetros.</p>
                        @endforelse
                    </div>
                </section>

                <div class="grid md:grid-cols-2 gap-5">
                    <section class="panel-pad space-y-4">
                        <div class="flex flex-wrap items-end justify-between gap-3">
                            <div>
                                <h2 class="form-section-title">Tipos de veículo</h2>
                                <p class="text-sm text-slate-500 mt-1">Cavalo / composição.</p>
                            </div>
                            <span class="badge-muted" id="count-tipos">0</span>
                        </div>
                        <div class="check-grid" data-count-target="count-tipos">
                            @foreach ($tipos as $tipo)
                                <label class="check-item">
                                    <input type="checkbox" name="tipos_veiculo[]" value="{{ $tipo->id }}"
                                           @checked($tiposSelecionados->contains($tipo->id))>
                                    <span>{{ $tipo->nome_tipo_veiculo }}</span>
                                </label>
                            @endforeach
                        </div>
                    </section>

                    <section class="panel-pad space-y-4">
                        <div class="flex flex-wrap items-end justify-between gap-3">
                            <div>
                                <h2 class="form-section-title">Tipos de carreta</h2>
                                <p class="text-sm text-slate-500 mt-1">Quando houver carreta.</p>
                            </div>
                            <span class="badge-muted" id="count-carreta">0</span>
                        </div>
                        <div class="check-grid" data-count-target="count-carreta">
                            @foreach ($tipos as $tipo)
                                <label class="check-item">
                                    <input type="checkbox" name="tipos_veiculo_carreta[]" value="{{ $tipo->id }}"
                                           @checked($tiposCarretaSelecionados->contains($tipo->id))>
                                    <span>{{ $tipo->nome_tipo_veiculo }}</span>
                                </label>
                            @endforeach
                        </div>
                    </section>
                </div>
            </div>
        </div>

        <div class="sticky-actions flex flex-wrap items-center justify-between gap-3 max-w-6xl">
            <p class="text-sm text-slate-500">Revise destinos e tipos antes de salvar.</p>
            <div class="flex flex-wrap gap-2">
                <a href="{{ route('admin.motoristas.index') }}" class="btn-secondary">Cancelar</a>
                <button class="btn-primary">{{ $motorista->exists ? 'Salvar alterações' : 'Cadastrar motorista' }}</button>
            </div>
        </div>
    </form>
@endsection

@push('scripts')
<script>
(() => {
    function atualizarContagem(container) {
        const alvoId = container.dataset.countTarget;
        if (!alvoId) return;
        const alvo = document.getElementById(alvoId);
        if (!alvo) return;
        const total = container.querySelectorAll('input[type="checkbox"]:checked').length;
        const label = alvoId.includes('destino') ? (total === 1 ? 'selecionado' : 'selecionados')
            : (total === 1 ? 'selecionada' : 'selecionadas');
        if (alvoId === 'count-tipos' || alvoId === 'count-carreta') {
            alvo.textContent = String(total);
            return;
        }
        alvo.textContent = `${total} ${label}`;
    }

    document.querySelectorAll('[data-count-target]').forEach((container) => {
        atualizarContagem(container);
        container.addEventListener('change', () => atualizarContagem(container));
    });

    const filtro = document.getElementById('filtro-destinos');
    const lista = document.getElementById('lista-destinos');
    filtro?.addEventListener('input', () => {
        const termo = filtro.value.trim().toLowerCase();
        lista?.querySelectorAll('[data-filter-text]').forEach((item) => {
            const texto = item.dataset.filterText || '';
            item.style.display = !termo || texto.includes(termo) ? '' : 'none';
        });
    });
})();
</script>
@endpush
