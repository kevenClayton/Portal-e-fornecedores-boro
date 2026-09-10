@extends('layouts.admin')

@section('title', 'Parâmetros')

@push('styles')
<style>
    .param-tabs { display: flex; flex-wrap: wrap; gap: 0.35rem; border-bottom: 1px solid var(--line); padding-bottom: 0.35rem; margin-bottom: 1.25rem; }
    .param-tab { border: 1px solid transparent; background: transparent; border-radius: 0.75rem; padding: 0.55rem 0.9rem; font-size: 0.875rem; font-weight: 700; color: #5b6f7c; cursor: pointer; }
    .param-tab:hover { background: var(--mist); color: var(--ink); }
    .param-tab.is-active { background: var(--accent-soft); color: var(--accent-hover); border-color: rgba(13, 122, 111, 0.25); }
    .param-panel[hidden] { display: none !important; }
    .catalog-item { display: flex; align-items: center; justify-content: space-between; gap: 0.75rem; border-radius: 0.85rem; background: var(--mist); padding: 0.7rem 0.85rem; font-size: 0.875rem; }
    .catalog-item span { font-weight: 600; word-break: break-word; }
    .destino-paginacao nav,
    .destino-paginacao > div { max-width: 100%; }
    .destino-paginacao nav > div:last-child { justify-content: flex-start !important; flex-wrap: wrap; gap: 0.25rem; }
    .destino-paginacao p { font-size: 0.75rem; margin-bottom: 0.5rem; }
</style>
@endpush

@section('content')
    <div class="mb-6">
        <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Cadastros</p>
        <h1 class="page-title font-display mt-1">Parâmetros</h1>
        <p class="page-subtitle">Operação do robô, login do portal e catálogos de origem, destino e veículo.</p>
    </div>

    <div class="param-tabs" role="tablist" aria-label="Seções de parâmetros">
        <button type="button" class="param-tab is-active" data-param-tab="operacao">Operação</button>
        <button type="button" class="param-tab" data-param-tab="login">Login do portal</button>
        <button type="button" class="param-tab" data-param-tab="catalogos">Catálogos</button>
        <button type="button" class="param-tab" data-param-tab="whatsapp">WhatsApp</button>
    </div>

    {{-- Operação --}}
    <div class="param-panel" data-param-panel="operacao">
        <form method="POST" action="{{ route('admin.parametros.valores') }}" class="grid lg:grid-cols-12 gap-5">
            @csrf
            <input type="hidden" name="whatsapp_telefones" value="{{ old('whatsapp_telefones', $parametro->whatsapp_telefones) }}">
            <input type="hidden" name="whatsapp_codigo_estabelecimento" value="{{ old('whatsapp_codigo_estabelecimento', $parametro->whatsapp_codigo_estabelecimento ?: 9) }}">
            <input type="hidden" name="painel_url_publica" value="{{ old('painel_url_publica', $parametro->painel_url_publica ?: 'https://madeforte.reservaai.com.br') }}">

            <section class="panel-pad lg:col-span-7 space-y-5">
                <div>
                    <h2 class="font-display text-xl">Limites de valor</h2>
                    <p class="text-sm text-slate-500 mt-1">Máximo aceito por tipo de veículo (quando a verificação de valor estiver ligada).</p>
                </div>
                <div class="grid sm:grid-cols-3 gap-3">
                    <div>
                        <label class="field-label">Truck</label>
                        <input type="number" step="0.01" name="limite_valor_truck" value="{{ old('limite_valor_truck', $parametro->limite_valor_truck) }}" class="field-input" required>
                    </div>
                    <div>
                        <label class="field-label">Toco</label>
                        <input type="number" step="0.01" name="limite_valor_toco" value="{{ old('limite_valor_toco', $parametro->limite_valor_toco) }}" class="field-input" required>
                    </div>
                    <div>
                        <label class="field-label">Carreta</label>
                        <input type="number" step="0.01" name="limite_valor_carreta" value="{{ old('limite_valor_carreta', $parametro->limite_valor_carreta) }}" class="field-input" required>
                    </div>
                </div>

                <div class="grid sm:grid-cols-2 gap-3">
                    <div>
                        <label class="field-label">E-mail de notificação</label>
                        <input type="email" name="email_notificacao" value="{{ old('email_notificacao', $parametro->email_notificacao) }}" class="field-input" placeholder="operacao@empresa.com">
                    </div>
                    <div>
                        <label class="field-label">Intervalo padrão (segundos)</label>
                        <input type="number" name="intervalo_espera_seg" value="{{ old('intervalo_espera_seg', $parametro->intervalo_espera_seg ?? 30) }}" class="field-input" required>
                        <p class="text-xs text-slate-500 mt-1">Usado como base da frota no painel do robô.</p>
                    </div>
                </div>
            </section>

            <section class="panel-pad lg:col-span-5 space-y-5">
                <div>
                    <h2 class="font-display text-xl">Comportamento</h2>
                    <p class="text-sm text-slate-500 mt-1">O que o robô verifica ao abrir a carga.</p>
                </div>

                <label class="flex items-start gap-3 rounded-xl border border-line bg-mist/50 px-3.5 py-3 text-sm font-semibold">
                    <input type="checkbox" name="modo_teste" value="1" class="mt-0.5 rounded border-line text-brand focus:ring-brand" @checked(old('modo_teste', $parametro->modo_teste))>
                    <span>
                        Modo teste
                        <span class="block text-xs font-medium text-slate-500 mt-0.5">Não vincula de verdade no portal.</span>
                    </span>
                </label>

                <div class="rounded-xl border border-line p-4 space-y-3">
                    <p class="text-[11px] font-bold uppercase tracking-[0.14em] text-slate-500">Abrir detalhes da carga</p>
                    <label class="flex items-start gap-3 text-sm font-semibold">
                        <input type="checkbox" name="verificar_valor_carga" value="1" class="mt-0.5 rounded border-line text-brand focus:ring-brand" @checked(old('verificar_valor_carga', $parametro->verificar_valor_carga ?? true))>
                        <span>Verificar valor</span>
                    </label>
                    <label class="flex items-start gap-3 text-sm font-semibold">
                        <input type="checkbox" name="verificar_bobina" value="1" class="mt-0.5 rounded border-line text-brand focus:ring-brand" @checked(old('verificar_bobina', $parametro->verificar_bobina ?? true))>
                        <span>Verificar bobina</span>
                    </label>
                    <label class="flex items-start gap-3 text-sm font-semibold">
                        <input type="checkbox" name="verificar_multiplos_destinos" value="1" class="mt-0.5 rounded border-line text-brand focus:ring-brand" @checked(old('verificar_multiplos_destinos', $parametro->verificar_multiplos_destinos ?? true))>
                        <span>Verificar múltiplos destinos</span>
                    </label>
                </div>

                <button class="btn-primary w-full">Salvar operação</button>
            </section>
        </form>
    </div>

    {{-- Login --}}
    <div class="param-panel" data-param-panel="login" hidden>
        <form method="POST" action="{{ route('admin.parametros.login') }}" class="panel-pad max-w-xl space-y-5">
            @csrf
            <div>
                <h2 class="font-display text-xl">Login do portal</h2>
                <p class="text-sm text-slate-500 mt-1">Credencial que o robô usa no e-Fornecedores.</p>
                @unless ($podeEditarLogin)
                    <p class="mt-2 rounded-xl border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
                        Somente o super admin pode alterar estas credenciais.
                    </p>
                @endunless
            </div>
            <div>
                <label class="field-label">Usuário</label>
                <input name="usuario" value="{{ old('usuario', $loginPortal->usuario) }}" class="field-input" required autocomplete="username"
                       @disabled(! $podeEditarLogin) @readonly(! $podeEditarLogin)>
            </div>
            <div>
                <label class="field-label">Senha</label>
                <input name="senha" type="{{ $podeEditarLogin ? 'password' : 'text' }}"
                       value="{{ $podeEditarLogin ? old('senha', $loginPortal->senha) : '••••••••' }}"
                       class="field-input" required autocomplete="current-password"
                       @disabled(! $podeEditarLogin) @readonly(! $podeEditarLogin)>
            </div>
            <label class="flex items-start gap-3 rounded-xl border border-line bg-mist/50 px-3.5 py-3 text-sm font-semibold {{ $podeEditarLogin ? '' : 'opacity-60' }}">
                <input type="checkbox" name="ativo" value="1" class="mt-0.5 rounded border-line text-brand focus:ring-brand"
                       @checked(old('ativo', $loginPortal->ativo ?? true)) @disabled(! $podeEditarLogin)>
                <span>Credencial ativa</span>
            </label>
            @if ($podeEditarLogin)
                <button class="btn-primary">Salvar login</button>
            @endif
        </form>
    </div>

    {{-- Catálogos --}}
    <div class="param-panel" data-param-panel="catalogos" hidden>
        <div class="grid lg:grid-cols-3 gap-5">
            <section class="panel-pad flex flex-col">
                <div class="mb-4">
                    <h2 class="font-display text-xl">Origens</h2>
                    <p class="text-sm text-slate-500 mt-1">Plantas de origem aceitas.</p>
                </div>
                <form method="POST" action="{{ route('admin.parametros.origens.store') }}" class="flex gap-2 mb-4">
                    @csrf
                    <input name="nome_origem" placeholder="Nome da origem" class="field-input" required>
                    <button class="btn-secondary shrink-0">Adicionar</button>
                </form>
                <ul class="space-y-2 max-h-80 overflow-auto pr-1 flex-1">
                    @forelse ($origens as $origem)
                        <li class="catalog-item">
                            <span>{{ $origem->nome_origem }}</span>
                            <form method="POST" action="{{ route('admin.parametros.origens.destroy', $origem) }}" onsubmit="return confirm('Remover origem?')">
                                @csrf @method('DELETE')
                                <button class="text-red-600 font-semibold text-xs">Remover</button>
                            </form>
                        </li>
                    @empty
                        <li class="text-sm text-slate-500 py-6 text-center">Nenhuma origem cadastrada.</li>
                    @endforelse
                </ul>
            </section>

            <section class="panel-pad flex flex-col min-w-0 overflow-hidden">
                <div class="mb-4">
                    <h2 class="font-display text-xl">Destinos</h2>
                    <p class="text-sm text-slate-500 mt-1">Nome igual ao cluster do portal.</p>
                </div>
                <form method="GET" class="mb-3">
                    <input type="hidden" name="aba" value="catalogos">
                    <input name="destino" value="{{ $buscaDestino }}" placeholder="Filtrar destino…" class="field-input">
                </form>
                <form method="POST" action="{{ route('admin.parametros.destinos.store') }}" class="flex gap-2 mb-4">
                    @csrf
                    <input name="nome_destino" placeholder="Ex: MCA -> SP-GUARULHOS" class="field-input" required>
                    <button class="btn-secondary shrink-0">Adicionar</button>
                </form>
                <ul class="space-y-2 max-h-72 overflow-auto pr-1 flex-1">
                    @forelse ($destinos as $destino)
                        <li class="catalog-item">
                            <span>{{ $destino->nome_destino }}</span>
                            <form method="POST" action="{{ route('admin.parametros.destinos.destroy', $destino) }}" onsubmit="return confirm('Remover destino?')">
                                @csrf @method('DELETE')
                                <button class="text-red-600 font-semibold text-xs shrink-0">Remover</button>
                            </form>
                        </li>
                    @empty
                        <li class="text-sm text-slate-500 py-6 text-center">Nenhum destino cadastrado.</li>
                    @endforelse
                </ul>
                <div class="mt-3 w-full min-w-0 overflow-x-auto">
                    <div class="destino-paginacao text-sm">
                        {{ $destinos->onEachSide(0)->appends(request()->query())->links() }}
                    </div>
                </div>
            </section>

            <section class="panel-pad flex flex-col">
                <div class="mb-4">
                    <h2 class="font-display text-xl">Tipos de veículo</h2>
                    <p class="text-sm text-slate-500 mt-1">Truck, carreta, toco etc.</p>
                </div>
                <form method="POST" action="{{ route('admin.parametros.tipos.store') }}" class="flex gap-2 mb-4">
                    @csrf
                    <input name="nome_tipo_veiculo" placeholder="Ex: Truck" class="field-input" required>
                    <button class="btn-secondary shrink-0">Adicionar</button>
                </form>
                <ul class="space-y-2 max-h-80 overflow-auto pr-1 flex-1">
                    @forelse ($tipos as $tipo)
                        <li class="catalog-item">
                            <span>{{ $tipo->nome_tipo_veiculo }}</span>
                            <form method="POST" action="{{ route('admin.parametros.tipos.destroy', $tipo) }}" onsubmit="return confirm('Remover tipo?')">
                                @csrf @method('DELETE')
                                <button class="text-red-600 font-semibold text-xs">Remover</button>
                            </form>
                        </li>
                    @empty
                        <li class="text-sm text-slate-500 py-6 text-center">Nenhum tipo cadastrado.</li>
                    @endforelse
                </ul>
            </section>
        </div>
    </div>

    {{-- WhatsApp --}}
    <div class="param-panel" data-param-panel="whatsapp" hidden>
        <form method="POST" action="{{ route('admin.parametros.valores') }}" class="panel-pad max-w-2xl space-y-5">
            @csrf
            {{-- Mantém os outros campos ao salvar só WhatsApp --}}
            <input type="hidden" name="limite_valor_truck" value="{{ old('limite_valor_truck', $parametro->limite_valor_truck) }}">
            <input type="hidden" name="limite_valor_toco" value="{{ old('limite_valor_toco', $parametro->limite_valor_toco) }}">
            <input type="hidden" name="limite_valor_carreta" value="{{ old('limite_valor_carreta', $parametro->limite_valor_carreta) }}">
            <input type="hidden" name="email_notificacao" value="{{ old('email_notificacao', $parametro->email_notificacao) }}">
            <input type="hidden" name="intervalo_espera_seg" value="{{ old('intervalo_espera_seg', $parametro->intervalo_espera_seg ?? 30) }}">
            @if (old('modo_teste', $parametro->modo_teste)) <input type="hidden" name="modo_teste" value="1"> @endif
            @if (old('verificar_valor_carga', $parametro->verificar_valor_carga ?? true)) <input type="hidden" name="verificar_valor_carga" value="1"> @endif
            @if (old('verificar_bobina', $parametro->verificar_bobina ?? true)) <input type="hidden" name="verificar_bobina" value="1"> @endif
            @if (old('verificar_multiplos_destinos', $parametro->verificar_multiplos_destinos ?? true)) <input type="hidden" name="verificar_multiplos_destinos" value="1"> @endif

            <div>
                <h2 class="font-display text-xl">WhatsApp</h2>
                <p class="text-sm text-slate-500 mt-1">Dispara template de carga aceita/perdida via API ReservaAI.</p>
            </div>
            <div>
                <label class="field-label">Telefones (DDI+DDD+número)</label>
                <textarea name="whatsapp_telefones" rows="4" class="field-input" placeholder="5531987654321&#10;31987654321">{{ old('whatsapp_telefones', $parametro->whatsapp_telefones) }}</textarea>
                <p class="text-xs text-slate-500 mt-1">Um por linha ou separados por vírgula. Sem DDI, assume 55.</p>
            </div>
            <div class="grid sm:grid-cols-2 gap-3">
                <div>
                    <label class="field-label">Código estabelecimento</label>
                    <input type="number" name="whatsapp_codigo_estabelecimento" value="{{ old('whatsapp_codigo_estabelecimento', $parametro->whatsapp_codigo_estabelecimento ?: 9) }}" class="field-input" placeholder="9" min="1">
                </div>
                <div>
                    <label class="field-label">URL pública do painel</label>
                    <input type="url" name="painel_url_publica" value="{{ old('painel_url_publica', $parametro->painel_url_publica ?: 'https://madeforte.reservaai.com.br') }}" class="field-input" placeholder="https://madeforte.reservaai.com.br">
                </div>
            </div>
            <button class="btn-primary">Salvar WhatsApp</button>
        </form>
    </div>
@endsection

@push('scripts')
<script>
(() => {
    const tabs = Array.from(document.querySelectorAll('[data-param-tab]'));
    const panels = Array.from(document.querySelectorAll('[data-param-panel]'));

    function ativar(nome) {
        tabs.forEach((tab) => tab.classList.toggle('is-active', tab.dataset.paramTab === nome));
        panels.forEach((panel) => { panel.hidden = panel.dataset.paramPanel !== nome; });
        try { localStorage.setItem('param_aba', nome); } catch (_) {}
        const url = new URL(window.location.href);
        url.searchParams.set('aba', nome);
        window.history.replaceState({}, '', url);
    }

    tabs.forEach((tab) => tab.addEventListener('click', () => ativar(tab.dataset.paramTab)));

    const daUrl = new URLSearchParams(window.location.search).get('aba');
    let inicial = daUrl;
    try { inicial = inicial || localStorage.getItem('param_aba'); } catch (_) {}
    if (inicial && ['operacao', 'login', 'catalogos', 'whatsapp'].includes(inicial)) {
        ativar(inicial);
    }
})();
</script>
@endpush
