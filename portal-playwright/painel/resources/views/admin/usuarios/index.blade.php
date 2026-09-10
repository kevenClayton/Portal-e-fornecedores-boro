@extends('layouts.admin')

@section('title', 'Usuários')

@section('content')
    <div class="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
            <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Super admin</p>
            <h1 class="page-title font-display mt-1">Usuários do painel</h1>
            <p class="page-subtitle">Só o super admin cria ou edita contas de acesso.</p>
        </div>
        <a href="{{ route('admin.usuarios.create') }}" class="btn-primary">Novo usuário</a>
    </div>

    <div class="panel overflow-hidden">
        <table class="w-full text-sm">
            <thead class="bg-mist text-left text-xs uppercase tracking-wide text-slate-500">
            <tr>
                <th class="px-4 py-3">Nome</th>
                <th class="px-4 py-3">E-mail</th>
                <th class="px-4 py-3">Cliente</th>
                <th class="px-4 py-3">Papel</th>
                <th class="px-4 py-3"></th>
            </tr>
            </thead>
            <tbody class="divide-y divide-line">
            @forelse ($usuarios as $usuario)
                <tr>
                    <td class="px-4 py-3 font-semibold">{{ $usuario->name }}</td>
                    <td class="px-4 py-3">{{ $usuario->email }}</td>
                    <td class="px-4 py-3">{{ $usuario->is_super_admin ? '—' : ($usuario->cliente?->nome ?? '—') }}</td>
                    <td class="px-4 py-3">
                        @if ($usuario->is_super_admin)
                            <span class="badge-ok">Super admin</span>
                        @else
                            <span class="text-slate-600">Operador</span>
                        @endif
                    </td>
                    <td class="px-4 py-3 text-right">
                        <a href="{{ route('admin.usuarios.edit', $usuario) }}" class="text-sm font-semibold text-brand hover:underline">Editar</a>
                    </td>
                </tr>
            @empty
                <tr>
                    <td colspan="5" class="px-4 py-8 text-center text-slate-500">Nenhum usuário.</td>
                </tr>
            @endforelse
            </tbody>
        </table>
    </div>
@endsection
