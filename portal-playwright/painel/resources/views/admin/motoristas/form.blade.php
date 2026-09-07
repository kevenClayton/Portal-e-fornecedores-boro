@extends('layouts.admin')

@section('title', $motorista->exists ? 'Editar motorista' : 'Novo motorista')

@section('content')
    <div class="mb-6">
        <a href="{{ route('admin.motoristas.index') }}" class="text-sm font-semibold text-brand hover:underline">← Voltar para lista</a>
        <h1 class="page-title font-display mt-2">{{ $motorista->exists ? 'Editar motorista' : 'Novo motorista' }}</h1>
        <p class="page-subtitle">Preencha os dados e selecione destinos exatamente como aparecem no portal.</p>
    </div>

    <form method="POST"
          action="{{ $motorista->exists ? route('admin.motoristas.update', $motorista) : route('admin.motoristas.store') }}"
          class="space-y-5 max-w-5xl">
        @csrf
        @if ($motorista->exists) @method('PUT') @endif

        <section class="panel-pad">
            <h2 class="font-display text-xl mb-4">Dados principais</h2>
            <div class="grid md:grid-cols-2 gap-4">
                <div>
                    <label class="field-label">Nome completo</label>
                    <input name="nome" value="{{ old('nome', $motorista->nome) }}" required class="field-input" placeholder="Nome do motorista">
                </div>
                <div>
                    <label class="field-label">CPF</label>
                    <input name="cpf" value="{{ old('cpf', $motorista->cpf) }}" required class="field-input" placeholder="000.000.000-00">
                </div>
                <div>
                    <label class="field-label">Placa do cavalo</label>
                    <input name="placa" value="{{ old('placa', $motorista->placa) }}" required class="field-input" placeholder="ABC1D23">
                </div>
                <div>
                    <label class="field-label">Placa da carreta <span class="font-normal text-slate-400">(opcional)</span></label>
                    <input name="placa_carreta" value="{{ old('placa_carreta', $motorista->placa_carreta) }}" class="field-input">
                </div>
                <div>
                    <label class="field-label">Ordem na fila</label>
                    <input type="number" name="ordem_motorista" value="{{ old('ordem_motorista', $motorista->ordem_motorista ?? 100) }}" class="field-input">
                    <p class="text-xs text-slate-500 mt-1">Números menores entram primeiro.</p>
                </div>
                <div class="flex flex-wrap items-center gap-6 pt-7">
                    <label class="inline-flex items-center gap-2 text-sm font-semibold">
                        <input type="checkbox" name="situacao" value="1" class="rounded border-line text-brand focus:ring-brand" @checked(old('situacao', $motorista->situacao))>
                        Motorista ativo
                    </label>
                    <label class="inline-flex items-center gap-2 text-sm font-semibold">
                        <input type="checkbox" name="aceita_bobina" value="1" class="rounded border-line text-brand focus:ring-brand" @checked(old('aceita_bobina', $motorista->aceita_bobina))>
                        Aceita bobina
                    </label>
                </div>
            </div>
        </section>

        <section class="panel-pad space-y-5">
            <div>
                <h2 class="font-display text-xl">Rotas aceitas</h2>
                <p class="text-sm text-slate-500 mt-1">Segure Ctrl/Cmd para marcar vários.</p>
            </div>
            <div>
                <label class="field-label">Origens</label>
                <select name="origens[]" multiple class="field-input h-36">
                    @foreach ($origens as $origem)
                        <option value="{{ $origem->id }}" @selected(collect(old('origens', $motorista->origens->pluck('id')))->contains($origem->id))>
                            {{ $origem->nome_origem }}
                        </option>
                    @endforeach
                </select>
            </div>
            <div>
                <label class="field-label">Destinos (clusters do portal)</label>
                <select name="destinos[]" multiple class="field-input h-52">
                    @foreach ($destinos as $destino)
                        <option value="{{ $destino->id }}" @selected(collect(old('destinos', $motorista->destinos->pluck('id')))->contains($destino->id))>
                            {{ $destino->nome_destino }}
                        </option>
                    @endforeach
                </select>
            </div>
            <div class="grid md:grid-cols-2 gap-4">
                <div>
                    <label class="field-label">Tipos de veículo</label>
                    <select name="tipos_veiculo[]" multiple class="field-input h-36">
                        @foreach ($tipos as $tipo)
                            <option value="{{ $tipo->id }}" @selected(collect(old('tipos_veiculo', $motorista->tiposVeiculo->pluck('id')))->contains($tipo->id))>
                                {{ $tipo->nome_tipo_veiculo }}
                            </option>
                        @endforeach
                    </select>
                </div>
                <div>
                    <label class="field-label">Tipos de carreta</label>
                    <select name="tipos_veiculo_carreta[]" multiple class="field-input h-36">
                        @foreach ($tipos as $tipo)
                            <option value="{{ $tipo->id }}" @selected(collect(old('tipos_veiculo_carreta', $motorista->tiposVeiculoCarreta->pluck('id')))->contains($tipo->id))>
                                {{ $tipo->nome_tipo_veiculo }}
                            </option>
                        @endforeach
                    </select>
                </div>
            </div>
        </section>

        <div class="flex flex-wrap gap-3">
            <button class="btn-primary">Salvar motorista</button>
            <a href="{{ route('admin.motoristas.index') }}" class="btn-secondary">Cancelar</a>
        </div>
    </form>
@endsection
