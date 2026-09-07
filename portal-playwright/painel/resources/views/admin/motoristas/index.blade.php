@extends('layouts.admin')

@section('title', 'Motoristas')

@section('content')
    <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
            <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Cadastros</p>
            <h1 class="page-title font-display mt-1">Motoristas</h1>
            <p class="page-subtitle">Quem pode pegar carga, com quais destinos e tipos de veículo.</p>
        </div>
        <a href="{{ route('admin.motoristas.create') }}" class="btn-primary">Novo motorista</a>
    </div>

    <form method="GET" class="panel-pad mb-4 flex flex-col sm:flex-row gap-3">
        <div class="flex-1">
            <label class="field-label" for="q">Buscar</label>
            <input id="q" type="text" name="q" value="{{ $busca }}" placeholder="Nome, placa ou CPF" class="field-input">
        </div>
        <div class="flex items-end gap-2">
            <button class="btn-primary">Buscar</button>
            @if ($busca !== '')
                <a href="{{ route('admin.motoristas.index') }}" class="btn-secondary">Limpar</a>
            @endif
        </div>
    </form>

    <div class="table-shell overflow-x-auto">
        <table class="data-table">
            <thead>
            <tr>
                <th>Ordem</th>
                <th>Motorista</th>
                <th>Placas</th>
                <th>Situação</th>
                <th>Destinos</th>
                <th></th>
            </tr>
            </thead>
            <tbody>
            @forelse ($motoristas as $motorista)
                <tr>
                    <td class="font-semibold text-slate-500">#{{ $motorista->ordem_motorista }}</td>
                    <td>
                        <div class="font-semibold">{{ $motorista->nome }}</div>
                        <div class="text-xs text-slate-500 mt-0.5">CPF {{ $motorista->cpf }}</div>
                    </td>
                    <td>
                        <div>{{ $motorista->placa }}</div>
                        @if ($motorista->placa_carreta)
                            <div class="text-xs text-slate-500">Carreta {{ $motorista->placa_carreta }}</div>
                        @endif
                    </td>
                    <td>
                        @if ($motorista->situacao)
                            <span class="badge-ok">Ativo</span>
                        @else
                            <span class="badge-muted">Inativo</span>
                        @endif
                        @if ($motorista->aceita_bobina)
                            <span class="badge-muted ml-1">Bobina</span>
                        @endif
                    </td>
                    <td class="text-slate-600">{{ $motorista->destinos->count() }}</td>
                    <td class="text-right whitespace-nowrap">
                        <a href="{{ route('admin.motoristas.edit', $motorista) }}" class="btn-ghost !px-2">Editar</a>
                        <form action="{{ route('admin.motoristas.destroy', $motorista) }}" method="POST" class="inline" onsubmit="return confirm('Remover este motorista?')">
                            @csrf @method('DELETE')
                            <button class="btn-ghost !px-2 !text-red-600">Excluir</button>
                        </form>
                    </td>
                </tr>
            @empty
                <tr>
                    <td colspan="6" class="px-4 py-12 text-center">
                        <div class="font-semibold">Nenhum motorista encontrado</div>
                        <p class="text-sm text-slate-500 mt-1">Cadastre o primeiro para começar a fila.</p>
                        <a href="{{ route('admin.motoristas.create') }}" class="btn-primary mt-4">Cadastrar motorista</a>
                    </td>
                </tr>
            @endforelse
            </tbody>
        </table>
    </div>

    <div class="mt-4">{{ $motoristas->links() }}</div>
@endsection
