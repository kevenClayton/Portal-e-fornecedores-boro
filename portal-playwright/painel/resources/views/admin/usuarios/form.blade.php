@extends('layouts.admin')

@section('title', $usuario->exists ? 'Editar usuário' : 'Novo usuário')

@section('content')
    <div class="mb-6">
        <a href="{{ route('admin.usuarios.index') }}" class="text-sm font-semibold text-brand hover:underline">← Usuários</a>
        <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand mt-3">Super admin</p>
        <h1 class="page-title font-display mt-1">{{ $usuario->exists ? 'Editar usuário' : 'Novo usuário' }}</h1>
    </div>

    <form method="POST"
          action="{{ $usuario->exists ? route('admin.usuarios.update', $usuario) : route('admin.usuarios.store') }}"
          class="panel-pad max-w-xl space-y-5">
        @csrf
        @if ($usuario->exists)
            @method('PUT')
        @endif

        <div>
            <label class="field-label">Nome</label>
            <input name="name" value="{{ old('name', $usuario->name) }}" class="field-input" required>
        </div>
        <div>
            <label class="field-label">E-mail</label>
            <input type="email" name="email" value="{{ old('email', $usuario->email) }}" class="field-input" required>
        </div>
        <div>
            <label class="field-label">Senha {{ $usuario->exists ? '(deixe em branco para manter)' : '' }}</label>
            <input type="password" name="password" class="field-input" @required(! $usuario->exists) autocomplete="new-password">
        </div>
        <div>
            <label class="field-label">Confirmar senha</label>
            <input type="password" name="password_confirmation" class="field-input" autocomplete="new-password">
        </div>

        <label class="flex items-start gap-3 rounded-xl border border-line bg-mist/50 px-3.5 py-3 text-sm font-semibold">
            <input type="checkbox" name="is_super_admin" value="1" id="is_super_admin"
                   class="mt-0.5 rounded border-line text-brand focus:ring-brand"
                   @checked(old('is_super_admin', $usuario->is_super_admin))
                   onchange="document.getElementById('bloco-cliente').hidden = this.checked">
            <span>
                Super admin
                <span class="block text-xs font-medium text-slate-500 mt-0.5">Pode criar clientes, usuários e editar login do portal.</span>
            </span>
        </label>

        <div id="bloco-cliente" @if(old('is_super_admin', $usuario->is_super_admin)) hidden @endif>
            <label class="field-label">Cliente</label>
            <select name="cliente_id" class="field-input">
                <option value="">Selecione…</option>
                @foreach ($clientes as $cliente)
                    <option value="{{ $cliente->id }}" @selected((string) old('cliente_id', $usuario->cliente_id) === (string) $cliente->id)>
                        {{ $cliente->nome }}
                    </option>
                @endforeach
            </select>
        </div>

        <button class="btn-primary">Salvar</button>
    </form>
@endsection
