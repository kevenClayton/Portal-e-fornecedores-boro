@extends('layouts.admin')

@section('title', 'Clientes')

@section('content')
    <div class="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
            <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Super admin</p>
            <h1 class="page-title font-display mt-1">Clientes</h1>
            <p class="page-subtitle">Nome, cor, máximo de robôs e containers Docker de cada operação.</p>
        </div>
        <a href="{{ route('admin.clientes.create') }}" class="btn-primary">Novo cliente</a>
    </div>

    <div class="panel overflow-hidden">
        <table class="w-full text-sm">
            <thead class="bg-mist text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
                <th class="px-4 py-3">Cliente</th>
                <th class="px-4 py-3">Cor</th>
                <th class="px-4 py-3">Banco</th>
                <th class="px-4 py-3">Máx. robôs</th>
                <th class="px-4 py-3">Containers</th>
                <th class="px-4 py-3">Status</th>
                <th class="px-4 py-3"></th>
            </tr>
            </thead>
            <tbody class="divide-y divide-line">
            @forelse ($clientes as $cliente)
                <tr>
                    <td class="px-4 py-3">
                        <div class="font-semibold">{{ $cliente->nome }}</div>
                        <div class="text-xs text-slate-500">{{ $cliente->slug }}</div>
                    </td>
                    <td class="px-4 py-3">
                        <span class="inline-flex items-center gap-2">
                            <span class="h-4 w-4 rounded-full border border-line" style="background: {{ $cliente->cor_primaria }}"></span>
                            {{ $cliente->cor_primaria }}
                        </span>
                    </td>
                    <td class="px-4 py-3 text-xs text-slate-600">
                        @if ($cliente->temBancoProprio())
                            <span class="font-semibold">{{ $cliente->db_database }}</span>
                            <div class="truncate max-w-[10rem]" title="{{ $cliente->db_host }}">{{ $cliente->db_host }}</div>
                        @else
                            compartilhado
                        @endif
                    </td>
                    <td class="px-4 py-3">{{ $cliente->max_robos }}</td>
                    <td class="px-4 py-3 text-xs text-slate-600 max-w-xs truncate" title="{{ $cliente->containers }}">
                        {{ $cliente->containers ?: '— não provisionado —' }}
                    </td>
                    <td class="px-4 py-3">
                        @if ($cliente->ativo)
                            <span class="badge-ok">Ativo</span>
                        @else
                            <span class="badge-warn">Inativo</span>
                        @endif
                    </td>
                    <td class="px-4 py-3 text-right space-x-2 whitespace-nowrap">
                        <form method="POST" action="{{ route('admin.clientes.selecionar', $cliente) }}" class="inline">
                            @csrf
                            <button class="text-sm font-semibold text-brand hover:underline">Usar</button>
                        </form>
                        <a href="{{ route('admin.clientes.edit', $cliente) }}" class="text-sm font-semibold text-ink hover:underline">Editar</a>
                    </td>
                </tr>
            @empty
                <tr>
                    <td colspan="7" class="px-4 py-8 text-center text-slate-500">Nenhum cliente cadastrado.</td>
                </tr>
            @endforelse
            </tbody>
        </table>
    </div>
@endsection
