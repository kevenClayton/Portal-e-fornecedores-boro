@extends('layouts.admin')

@section('title', 'Rotas')

@section('content')
    <div class="mb-6">
        <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Acompanhamento</p>
        <h1 class="page-title font-display mt-1">Rotas vinculadas</h1>
        <p class="page-subtitle">Cargas que o robô conseguiu vincular com sucesso.</p>
    </div>

    <form method="GET" class="panel-pad mb-4 flex flex-col sm:flex-row gap-3">
        <div class="flex-1">
            <label class="field-label" for="q">Buscar</label>
            <input id="q" type="text" name="q" value="{{ $busca }}" placeholder="Documento, motorista, origem ou destino" class="field-input">
        </div>
        <div class="flex items-end gap-2">
            <button class="btn-primary">Buscar</button>
            @if ($busca !== '')
                <a href="{{ route('admin.rotas.index') }}" class="btn-secondary">Limpar</a>
            @endif
        </div>
    </form>

    <div class="table-shell overflow-x-auto">
        <table class="data-table">
            <thead>
            <tr>
                <th>Documento</th>
                <th>Origem → Destino</th>
                <th>Motorista</th>
                <th>Tipo</th>
                <th>Valor</th>
                <th>Quando</th>
            </tr>
            </thead>
            <tbody>
            @forelse ($rotas as $rota)
                <tr>
                    <td class="font-semibold">{{ $rota->doc_transporte }}</td>
                    <td>
                        <div class="font-medium">{{ $rota->origem_rota }}</div>
                        <div class="text-xs text-slate-500 mt-0.5">→ {{ $rota->destino_rota }}</div>
                    </td>
                    <td>{{ $rota->motorista_rota }}</td>
                    <td><span class="badge-muted">{{ $rota->tipo_veiculo }}</span></td>
                    <td>{{ $rota->valor_carga ?: '—' }}</td>
                    <td class="text-slate-500 whitespace-nowrap">{{ optional($rota->created_at)?->format('d/m/Y H:i') }}</td>
                </tr>
            @empty
                <tr>
                    <td colspan="6" class="px-4 py-12 text-center text-slate-500">
                        Nenhuma rota vinculada ainda.
                    </td>
                </tr>
            @endforelse
            </tbody>
        </table>
    </div>
    <div class="mt-4">{{ $rotas->links() }}</div>
@endsection
