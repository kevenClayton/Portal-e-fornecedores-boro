@extends('layouts.admin')

@section('title', 'Ordem da fila')

@section('content')
    <div class="mb-6">
        <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Cadastros</p>
        <h1 class="page-title font-display mt-1">Ordem da fila</h1>
        <p class="page-subtitle">Defina quem o robô tenta primeiro na vinculação.</p>
    </div>

    <form method="POST" action="{{ route('admin.motoristas.reordenar') }}" class="table-shell">
        @csrf
        <div class="overflow-x-auto">
            <table class="data-table">
                <thead>
                <tr>
                    <th>Ordem</th>
                    <th>Motorista</th>
                    <th>Placa</th>
                    <th>Situação</th>
                </tr>
                </thead>
                <tbody>
                @forelse ($motoristas as $motorista)
                    <tr>
                        <td class="w-32">
                            <input type="number" name="ordem[{{ $motorista->id }}]" value="{{ $motorista->ordem_motorista }}" class="field-input !w-24">
                        </td>
                        <td class="font-semibold">{{ $motorista->nome }}</td>
                        <td>{{ $motorista->placa }}</td>
                        <td>
                            @if ($motorista->situacao)
                                <span class="badge-ok">Ativo</span>
                            @else
                                <span class="badge-muted">Inativo</span>
                            @endif
                        </td>
                    </tr>
                @empty
                    <tr><td colspan="4" class="px-4 py-10 text-center text-slate-500">Nenhum motorista cadastrado.</td></tr>
                @endforelse
                </tbody>
            </table>
        </div>
        <div class="px-4 py-4 border-t border-line flex justify-end">
            <button class="btn-primary">Salvar ordem</button>
        </div>
    </form>
@endsection
