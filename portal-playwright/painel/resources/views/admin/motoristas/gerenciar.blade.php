@extends('layouts.admin')

@section('title', 'Ordem da fila')

@section('content')
    <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
            <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Cadastros</p>
            <h1 class="page-title font-display mt-1">Gerenciar ordem</h1>
            <p class="page-subtitle">Arraste entre ativo e inativo, e reordene a fila do robô. Salva automaticamente.</p>
        </div>
        <span id="fila-status" class="text-sm font-semibold text-slate-500">Pronto</span>
    </div>

    <meta name="csrf-token" content="{{ csrf_token() }}">

    <div class="grid lg:grid-cols-2 gap-5">
        <section class="panel overflow-hidden">
            <div class="px-5 py-4 border-b border-line bg-[var(--ok-soft)]">
                <h2 class="font-display text-xl text-[var(--ok)]">Motoristas ativos</h2>
                <p class="text-sm text-slate-600 mt-0.5">Ordem = prioridade na vinculação</p>
            </div>
            <div id="lista-ativos" class="p-4 min-h-[20rem] space-y-2 cards-motorista" data-lista="ativos">
                @forelse ($motoristasAtivos as $motorista)
                    <div class="motorista-card" data-id="{{ $motorista->id }}">
                        <span class="motorista-handle" aria-hidden="true">⋮⋮</span>
                        <div class="min-w-0 flex-1">
                            <div class="font-semibold truncate">{{ $motorista->nome }}</div>
                            <div class="text-xs text-slate-500 truncate">{{ $motorista->cpf }} · {{ $motorista->placa }}</div>
                        </div>
                        <span class="ordenacao badge-ok">{{ $loop->iteration }}</span>
                    </div>
                @empty
                    <p class="lista-vazia text-sm text-slate-500 text-center py-8">Nenhum ativo — arraste da coluna da direita</p>
                @endforelse
            </div>
        </section>

        <section class="panel overflow-hidden">
            <div class="px-5 py-4 border-b border-line bg-[var(--danger-soft)]">
                <h2 class="font-display text-xl text-[var(--danger)]">Motoristas inativos</h2>
                <p class="text-sm text-slate-600 mt-0.5">Fora da fila até reativar</p>
            </div>
            <div id="lista-inativos" class="p-4 min-h-[20rem] space-y-2 cards-motorista" data-lista="inativos">
                @forelse ($motoristasInativos as $motorista)
                    <div class="motorista-card" data-id="{{ $motorista->id }}">
                        <span class="motorista-handle" aria-hidden="true">⋮⋮</span>
                        <div class="min-w-0 flex-1">
                            <div class="font-semibold truncate">{{ $motorista->nome }}</div>
                            <div class="text-xs text-slate-500 truncate">{{ $motorista->cpf }} · {{ $motorista->placa }}</div>
                        </div>
                        <span class="ordenacao badge-muted">{{ $loop->iteration }}</span>
                    </div>
                @empty
                    <p class="lista-vazia text-sm text-slate-500 text-center py-8">Nenhum inativo</p>
                @endforelse
            </div>
        </section>
    </div>
@endsection

@push('scripts')
<style>
    .motorista-card {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem 0.9rem;
        border-radius: 0.9rem;
        border: 1px solid var(--line);
        background: #fff;
        cursor: grab;
        user-select: none;
    }
    .motorista-card:active { cursor: grabbing; }
    .motorista-card.sortable-ghost {
        opacity: 0.45;
        background: var(--accent-soft);
    }
    .motorista-card.sortable-chosen {
        box-shadow: 0 8px 24px rgba(15, 28, 36, 0.12);
    }
    .motorista-handle {
        color: #94a3b8;
        font-size: 0.85rem;
        letter-spacing: -0.08em;
        line-height: 1;
    }
    .cards-motorista.sortable-drag-over {
        outline: 2px dashed var(--accent);
        outline-offset: -4px;
        border-radius: 0.75rem;
    }
</style>
<script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.6/Sortable.min.js"></script>
<script>
(() => {
    const listaAtivos = document.getElementById('lista-ativos');
    const listaInativos = document.getElementById('lista-inativos');
    const statusEl = document.getElementById('fila-status');
    const urlSalvar = @json(route('admin.motoristas.reordenar'));
    const csrf = document.querySelector('meta[name="csrf-token"]')?.content
        || document.querySelector('input[name="_token"]')?.value;

    function limparVazios(lista) {
        lista.querySelectorAll('.lista-vazia').forEach((el) => el.remove());
        const temCard = lista.querySelector('.motorista-card');
        if (!temCard) {
            const vazio = document.createElement('p');
            vazio.className = 'lista-vazia text-sm text-slate-500 text-center py-8';
            vazio.textContent = lista.dataset.lista === 'ativos'
                ? 'Nenhum ativo — arraste da coluna da direita'
                : 'Nenhum inativo';
            lista.appendChild(vazio);
        }
    }

    function renumerar() {
        listaAtivos.querySelectorAll('.motorista-card').forEach((card, indice) => {
            const badge = card.querySelector('.ordenacao');
            if (badge) {
                badge.className = 'ordenacao badge-ok';
                badge.textContent = String(indice + 1);
            }
        });
        listaInativos.querySelectorAll('.motorista-card').forEach((card, indice) => {
            const badge = card.querySelector('.ordenacao');
            if (badge) {
                badge.className = 'ordenacao badge-muted';
                badge.textContent = String(indice + 1);
            }
        });
        limparVazios(listaAtivos);
        limparVazios(listaInativos);
    }

    function coletar(lista, situacao) {
        return Array.from(lista.querySelectorAll('.motorista-card')).map((card, indice) => ({
            id: Number(card.dataset.id),
            ordem: indice + 1,
            situacao,
        }));
    }

    let salvando = false;
    let pendente = false;

    async function salvar() {
        if (salvando) {
            pendente = true;
            return;
        }
        salvando = true;
        statusEl.textContent = 'Salvando...';
        statusEl.className = 'text-sm font-semibold text-brand';

        try {
            const response = await fetch(urlSalvar, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                    'X-CSRF-TOKEN': csrf,
                    'X-Requested-With': 'XMLHttpRequest',
                },
                body: JSON.stringify({
                    motoristasAtivos: coletar(listaAtivos, 1),
                    motoristasInativos: coletar(listaInativos, 0),
                }),
            });
            const data = await response.json().catch(() => ({}));
            if (!response.ok) {
                throw new Error(data.message || 'Falha ao salvar');
            }
            statusEl.textContent = 'Salvo';
            statusEl.className = 'text-sm font-semibold text-[var(--ok)]';
        } catch (erro) {
            statusEl.textContent = String(erro.message || erro);
            statusEl.className = 'text-sm font-semibold text-[var(--danger)]';
        } finally {
            salvando = false;
            if (pendente) {
                pendente = false;
                salvar();
            }
        }
    }

    function aoMudar() {
        renumerar();
        salvar();
    }

    const opcoes = {
        group: 'motoristas-fila',
        animation: 150,
        ghostClass: 'sortable-ghost',
        chosenClass: 'sortable-chosen',
        dragClass: 'sortable-drag',
        onAdd: aoMudar,
        onUpdate: aoMudar,
        onRemove: () => {
            limparVazios(listaAtivos);
            limparVazios(listaInativos);
        },
    };

    Sortable.create(listaAtivos, opcoes);
    Sortable.create(listaInativos, opcoes);
    renumerar();
})();
</script>
@endpush
