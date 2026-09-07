@extends('layouts.admin')

@section('title', 'Relatórios')

@section('content')
    <div class="mb-6 flex flex-wrap items-end justify-between gap-4">
        <div>
            <p class="text-xs font-bold uppercase tracking-[0.16em] text-brand">Acompanhamento</p>
            <h1 class="page-title font-display mt-1">Relatórios</h1>
            <p class="page-subtitle">Cargas que não foram vinculadas e o motivo.</p>
        </div>
        <a href="{{ route('admin.relatorios.export', request()->query()) }}" class="btn-secondary">Exportar CSV</a>
    </div>

    <form method="GET" class="panel-pad mb-4 grid md:grid-cols-3 gap-3">
        <div>
            <label class="field-label">Busca</label>
            <input type="text" name="q" value="{{ $busca }}" placeholder="Doc, origem ou destino" class="field-input">
        </div>
        <div>
            <label class="field-label">Motivo</label>
            <input type="text" name="motivo" value="{{ $motivo }}" placeholder="Ex: Não tem motorista" class="field-input">
        </div>
        <div class="flex items-end gap-2">
            <button class="btn-primary">Filtrar</button>
            @if ($busca !== '' || $motivo !== '')
                <a href="{{ route('admin.relatorios.index') }}" class="btn-secondary">Limpar</a>
            @endif
        </div>
    </form>

    <div class="table-shell overflow-x-auto">
        <table class="data-table">
            <thead>
            <tr>
                <th>Documento</th>
                <th>Rota</th>
                <th>Tipo</th>
                <th>Motivo</th>
                <th>Quando</th>
            </tr>
            </thead>
            <tbody>
            @forelse ($relatorios as $relatorio)
                <tr>
                    <td class="font-semibold">{{ $relatorio->doc_transporte }}</td>
                    <td>
                        <div class="font-medium">{{ $relatorio->origem_rota }}</div>
                        <div class="text-xs text-slate-500 mt-0.5">→ {{ $relatorio->destino_rota }}</div>
                    </td>
                    <td><span class="badge-muted">{{ $relatorio->tipo_veiculo }}</span></td>
                    <td><span class="badge-warn">{{ $relatorio->motivo }}</span></td>
                    <td class="text-slate-500 whitespace-nowrap">{{ optional($relatorio->created_at)?->format('d/m/Y H:i') }}</td>
                </tr>
            @empty
                <tr>
                    <td colspan="5" class="px-4 py-12 text-center text-slate-500">
                        Nenhum relatório encontrado.
                    </td>
                </tr>
            @endforelse
            </tbody>
        </table>
    </div>
    <div class="mt-4">{{ $relatorios->links() }}</div>
@endsection
