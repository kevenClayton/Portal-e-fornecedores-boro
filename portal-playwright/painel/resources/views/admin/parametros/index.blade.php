@extends('layouts.admin')

@section('title', 'Parâmetros')

@section('content')
    <div class="mb-6">
        <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Cadastros</p>
        <h1 class="page-title font-display mt-1">Parâmetros</h1>
        <p class="page-subtitle">Limites, login do portal e cadastros base usados pelo robô.</p>
    </div>

    <div class="grid lg:grid-cols-2 gap-5 mb-5">
        <form method="POST" action="{{ route('admin.parametros.valores') }}" class="panel-pad space-y-4">
            @csrf
            <div>
                <h2 class="font-display text-xl">Limites e operação</h2>
                <p class="text-sm text-slate-500 mt-1">Valores máximos por tipo de veículo e intervalo entre ciclos.</p>
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
            <div>
                <label class="field-label">E-mail de notificação</label>
                <input type="email" name="email_notificacao" value="{{ old('email_notificacao', $parametro->email_notificacao) }}" class="field-input" placeholder="operacao@empresa.com">
            </div>
            <div>
                <label class="field-label">Intervalo de espera (segundos)</label>
                <input type="number" name="intervalo_espera_seg" value="{{ old('intervalo_espera_seg', $parametro->intervalo_espera_seg ?? 30) }}" class="field-input" required>
            </div>
            <label class="inline-flex items-center gap-2 text-sm font-semibold">
                <input type="checkbox" name="modo_teste" value="1" class="rounded border-line text-brand focus:ring-brand" @checked(old('modo_teste', $parametro->modo_teste))>
                Modo teste (não vincula de verdade no portal)
            </label>
            <div>
                <button class="btn-primary">Salvar parâmetros</button>
            </div>
        </form>

        <form method="POST" action="{{ route('admin.parametros.login') }}" class="panel-pad space-y-4">
            @csrf
            <div>
                <h2 class="font-display text-xl">Login do portal</h2>
                <p class="text-sm text-slate-500 mt-1">Credencial que o robô usa no e-Fornecedores.</p>
            </div>
            <div>
                <label class="field-label">Usuário</label>
                <input name="usuario" value="{{ old('usuario', $loginPortal->usuario) }}" class="field-input" required>
            </div>
            <div>
                <label class="field-label">Senha</label>
                <input name="senha" value="{{ old('senha', $loginPortal->senha) }}" class="field-input" required>
            </div>
            <label class="inline-flex items-center gap-2 text-sm font-semibold">
                <input type="checkbox" name="ativo" value="1" class="rounded border-line text-brand focus:ring-brand" @checked(old('ativo', $loginPortal->ativo ?? true))>
                Credencial ativa
            </label>
            <div>
                <button class="btn-primary">Salvar login</button>
            </div>
        </form>
    </div>

    <div class="grid lg:grid-cols-3 gap-5">
        <div class="panel-pad">
            <h2 class="font-display text-xl mb-1">Origens</h2>
            <p class="text-sm text-slate-500 mb-4">Plantas de origem aceitas.</p>
            <form method="POST" action="{{ route('admin.parametros.origens.store') }}" class="flex gap-2 mb-4">
                @csrf
                <input name="nome_origem" placeholder="Nome da origem" class="field-input" required>
                <button class="btn-secondary shrink-0">Add</button>
            </form>
            <ul class="space-y-2 max-h-72 overflow-auto pr-1">
                @forelse ($origens as $origem)
                    <li class="flex items-center justify-between gap-2 rounded-xl bg-mist px-3 py-2 text-sm">
                        <span class="font-medium">{{ $origem->nome_origem }}</span>
                        <form method="POST" action="{{ route('admin.parametros.origens.destroy', $origem) }}" onsubmit="return confirm('Remover origem?')">
                            @csrf @method('DELETE')
                            <button class="text-red-600 font-semibold text-xs">Remover</button>
                        </form>
                    </li>
                @empty
                    <li class="text-sm text-slate-500">Nenhuma origem cadastrada.</li>
                @endforelse
            </ul>
        </div>

        <div class="panel-pad">
            <h2 class="font-display text-xl mb-1">Destinos / clusters</h2>
            <p class="text-sm text-slate-500 mb-4">Use o nome igual ao do portal.</p>
            <form method="GET" class="mb-3">
                <input name="destino" value="{{ $buscaDestino }}" placeholder="Filtrar destino..." class="field-input">
            </form>
            <form method="POST" action="{{ route('admin.parametros.destinos.store') }}" class="flex gap-2 mb-4">
                @csrf
                <input name="nome_destino" placeholder="Ex: MCA -> SP-GUARULHOS" class="field-input" required>
                <button class="btn-secondary shrink-0">Add</button>
            </form>
            <ul class="space-y-2 max-h-64 overflow-auto pr-1">
                @forelse ($destinos as $destino)
                    <li class="flex items-center justify-between gap-2 rounded-xl bg-mist px-3 py-2 text-sm">
                        <span class="font-medium break-all">{{ $destino->nome_destino }}</span>
                        <form method="POST" action="{{ route('admin.parametros.destinos.destroy', $destino) }}" onsubmit="return confirm('Remover destino?')">
                            @csrf @method('DELETE')
                            <button class="text-red-600 font-semibold text-xs shrink-0">Remover</button>
                        </form>
                    </li>
                @empty
                    <li class="text-sm text-slate-500">Nenhum destino cadastrado.</li>
                @endforelse
            </ul>
            <div class="mt-3">{{ $destinos->links() }}</div>
        </div>

        <div class="panel-pad">
            <h2 class="font-display text-xl mb-1">Tipos de veículo</h2>
            <p class="text-sm text-slate-500 mb-4">Truck, carreta, toco etc.</p>
            <form method="POST" action="{{ route('admin.parametros.tipos.store') }}" class="flex gap-2 mb-4">
                @csrf
                <input name="nome_tipo_veiculo" placeholder="Ex: Truck" class="field-input" required>
                <button class="btn-secondary shrink-0">Add</button>
            </form>
            <ul class="space-y-2 max-h-72 overflow-auto pr-1">
                @forelse ($tipos as $tipo)
                    <li class="flex items-center justify-between gap-2 rounded-xl bg-mist px-3 py-2 text-sm">
                        <span class="font-medium">{{ $tipo->nome_tipo_veiculo }}</span>
                        <form method="POST" action="{{ route('admin.parametros.tipos.destroy', $tipo) }}" onsubmit="return confirm('Remover tipo?')">
                            @csrf @method('DELETE')
                            <button class="text-red-600 font-semibold text-xs">Remover</button>
                        </form>
                    </li>
                @empty
                    <li class="text-sm text-slate-500">Nenhum tipo cadastrado.</li>
                @endforelse
            </ul>
        </div>
    </div>
@endsection
