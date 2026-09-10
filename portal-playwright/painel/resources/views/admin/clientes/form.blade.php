@extends('layouts.admin')

@section('title', $cliente->exists ? 'Editar cliente' : 'Novo cliente')

@section('content')
    <div class="mb-6">
        <a href="{{ route('admin.clientes.index') }}" class="text-sm font-semibold text-brand hover:underline">← Clientes</a>
        <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand mt-3">Super admin</p>
        <h1 class="page-title font-display mt-1">{{ $cliente->exists ? 'Editar cliente' : 'Novo cliente' }}</h1>
    </div>

    <form method="POST"
          action="{{ $cliente->exists ? route('admin.clientes.update', $cliente) : route('admin.clientes.store') }}"
          class="panel-pad max-w-2xl space-y-5">
        @csrf
        @if ($cliente->exists)
            @method('PUT')
        @endif

        <div class="grid sm:grid-cols-2 gap-4">
            <div class="sm:col-span-2">
                <label class="field-label">Nome</label>
                <input name="nome" value="{{ old('nome', $cliente->nome) }}" class="field-input" required placeholder="MadeForte">
            </div>
            <div>
                <label class="field-label">Slug</label>
                <input name="slug" value="{{ old('slug', $cliente->slug) }}" class="field-input" placeholder="madeforte">
                <p class="text-xs text-slate-500 mt-1">Identificador interno (a–z, 0–9, hífen).</p>
            </div>
            <div>
                <label class="field-label">Máximo de robôs</label>
                <input type="number" min="1" max="3" name="max_robos" value="{{ old('max_robos', $cliente->max_robos ?? 1) }}" class="field-input" required>
            </div>
            <div>
                <label class="field-label">Cor primária</label>
                <input type="color" name="cor_primaria" value="{{ old('cor_primaria', $cliente->cor_primaria ?: '#0d7a6f') }}" class="h-11 w-full rounded-xl border border-line bg-white p-1">
            </div>
            <div>
                <label class="field-label">Cor accent</label>
                <input type="color" name="cor_accent" value="{{ old('cor_accent', $cliente->cor_accent ?: '#0a635a') }}" class="h-11 w-full rounded-xl border border-line bg-white p-1">
            </div>
            <div class="sm:col-span-2">
                <label class="field-label">Containers Docker (CSV)</label>
                <input name="containers" value="{{ old('containers', $cliente->containers) }}" class="field-input"
                       placeholder="portal-fornecedores,portal-fornecedores-2">
                <p class="text-xs text-slate-500 mt-1">Na mesma EC2, separe containers por cliente. Ex.: MadeForte usa 1–2; outro cliente usa o 3º.</p>
            </div>
            <div class="sm:col-span-2">
                <label class="inline-flex items-center gap-2 text-sm font-semibold">
                    <input type="checkbox" name="ativo" value="1" class="rounded border-line text-brand focus:ring-brand"
                           @checked(old('ativo', $cliente->ativo ?? true))>
                    Cliente ativo
                </label>
            </div>
        </div>

        <button class="btn-primary">Salvar</button>
    </form>
@endsection
