@extends('layouts.admin')

@section('title', 'Motoristas')

@section('content')
    <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
            <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Cadastros</p>
            <h1 class="page-title font-display mt-1">Motoristas</h1>
            <p class="page-subtitle">Fila de quem pode pegar carga, com destinos e tipos de veículo.</p>
        </div>
        <div class="flex flex-wrap gap-2">
            <a href="{{ route('admin.motoristas.gerenciar') }}" class="btn-secondary">Ordem da fila</a>
            <a href="{{ route('admin.motoristas.create') }}" class="btn-primary">Novo motorista</a>
        </div>
    </div>

    <form method="GET" class="panel-pad mb-4">
        <div class="flex flex-col sm:flex-row gap-3 sm:items-end">
            <div class="flex-1">
                <label class="field-label" for="q">Buscar</label>
                <input id="q" type="search" name="q" value="{{ $busca }}" placeholder="Nome, placa ou CPF" class="field-input">
            </div>
            <div class="flex gap-2">
                <button class="btn-primary">Buscar</button>
                @if ($busca !== '')
                    <a href="{{ route('admin.motoristas.index') }}" class="btn-secondary">Limpar</a>
                @endif
            </div>
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
                <th class="text-right">Ações</th>
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
                        <div class="font-medium">{{ $motorista->placa }}</div>
                        @if ($motorista->placa_carreta)
                            <div class="text-xs text-slate-500">Carreta {{ $motorista->placa_carreta }}</div>
                        @endif
                    </td>
                    <td>
                        <div class="flex flex-wrap gap-1">
                            @if ($motorista->situacao)
                                <span class="badge-ok">Ativo</span>
                            @else
                                <span class="badge-muted">Inativo</span>
                            @endif
                            @if ($motorista->aceita_bobina)
                                <span class="badge-muted">Bobina</span>
                            @endif
                        </div>
                    </td>
                    <td>
                        <span class="font-semibold">{{ $motorista->destinos->count() }}</span>
                        <span class="text-slate-500 text-xs">destino(s)</span>
                    </td>
                    <td class="text-right whitespace-nowrap">
                        <a href="{{ route('admin.motoristas.edit', $motorista) }}" class="btn-secondary !px-3 !py-1.5">Editar</a>
                        <form action="{{ route('admin.motoristas.destroy', $motorista) }}" method="POST" class="inline" onsubmit="return confirm('Remover este motorista?')">
                            @csrf @method('DELETE')
                            <button class="btn-ghost !px-2 !text-red-600">Excluir</button>
                        </form>
                    </td>
                </tr>
            @empty
                <tr>
                    <td colspan="6" class="px-4 py-14 text-center">
                        <div class="font-semibold text-lg">Nenhum motorista encontrado</div>
                        <p class="text-sm text-slate-500 mt-1">Cadastre o primeiro para montar a fila do robô.</p>
                        <a href="{{ route('admin.motoristas.create') }}" class="btn-primary mt-4 inline-flex">Cadastrar motorista</a>
                    </td>
                </tr>
            @endforelse
            </tbody>
        </table>
    </div>

    <div class="mt-4">{{ $motoristas->links() }}</div>
@endsection
