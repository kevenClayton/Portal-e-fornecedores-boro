<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Destino;
use App\Models\Motorista;
use App\Models\Origem;
use App\Models\TipoVeiculo;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Schema;
use Illuminate\View\View;

class MotoristaController extends Controller
{
    public function index(Request $request): View
    {
        $busca = trim((string) $request->query('q', ''));

        $motoristas = Motorista::query()
            ->with(['destinos', 'origens', 'tiposVeiculo'])
            ->when($busca !== '', function ($query) use ($busca) {
                $query->where(function ($inner) use ($busca) {
                    $inner->where('nome', 'like', "%{$busca}%")
                        ->orWhere('placa', 'like', "%{$busca}%")
                        ->orWhere('cpf', 'like', "%{$busca}%");
                });
            })
            ->orderBy('ordem_motorista')
            ->orderBy('nome')
            ->paginate(20)
            ->withQueryString();

        return view('admin.motoristas.index', compact('motoristas', 'busca'));
    }

    public function create(): View
    {
        return view('admin.motoristas.form', [
            'motorista' => new Motorista([
                'situacao' => true,
                'aceita_bobina' => false,
                'ordem_motorista' => 100,
            ]),
            'origens' => Origem::query()->where('ativo', true)->orderBy('nome_origem')->get(),
            'destinos' => Destino::query()->where('ativo', true)->orderBy('nome_destino')->get(),
            'tipos' => TipoVeiculo::query()->orderBy('nome_tipo_veiculo')->get(),
        ]);
    }

    public function store(Request $request): RedirectResponse
    {
        $dados = $this->validar($request);
        $motorista = Motorista::query()->create($dados);
        $this->syncRelacoes($motorista, $request);

        return redirect()
            ->route('admin.motoristas.index')
            ->with('success', 'Motorista cadastrado.');
    }

    public function edit(Motorista $motorista): View
    {
        $motorista->load(['destinos', 'origens', 'tiposVeiculo', 'tiposVeiculoCarreta']);

        return view('admin.motoristas.form', [
            'motorista' => $motorista,
            'origens' => Origem::query()->where('ativo', true)->orderBy('nome_origem')->get(),
            'destinos' => Destino::query()->where('ativo', true)->orderBy('nome_destino')->get(),
            'tipos' => TipoVeiculo::query()->orderBy('nome_tipo_veiculo')->get(),
        ]);
    }

    public function update(Request $request, Motorista $motorista): RedirectResponse
    {
        $dados = $this->validar($request);
        $motorista->update($dados);
        $this->syncRelacoes($motorista, $request);

        return redirect()
            ->route('admin.motoristas.index')
            ->with('success', 'Motorista atualizado.');
    }

    public function destroy(Motorista $motorista): RedirectResponse
    {
        $motorista->delete();

        return redirect()
            ->route('admin.motoristas.index')
            ->with('success', 'Motorista removido.');
    }

    public function gerenciar(): View
    {
        $motoristasAtivos = Motorista::query()
            ->where('situacao', true)
            ->orderBy('ordem_motorista')
            ->orderBy('nome')
            ->get();

        $motoristasInativos = Motorista::query()
            ->where('situacao', false)
            ->orderBy('ordem_motorista')
            ->orderBy('nome')
            ->get();

        return view('admin.motoristas.gerenciar', compact('motoristasAtivos', 'motoristasInativos'));
    }

    public function reordenar(Request $request)
    {
        $dados = $request->validate([
            'motoristasAtivos' => ['nullable', 'array'],
            'motoristasAtivos.*.id' => ['required', 'integer'],
            'motoristasAtivos.*.ordem' => ['required', 'integer', 'min:1'],
            'motoristasInativos' => ['nullable', 'array'],
            'motoristasInativos.*.id' => ['required', 'integer'],
            'motoristasInativos.*.ordem' => ['required', 'integer', 'min:1'],
        ]);

        foreach ($dados['motoristasAtivos'] ?? [] as $item) {
            Motorista::query()->whereKey($item['id'])->update([
                'situacao' => true,
                'ordem_motorista' => (int) $item['ordem'],
            ]);
        }

        foreach ($dados['motoristasInativos'] ?? [] as $item) {
            Motorista::query()->whereKey($item['id'])->update([
                'situacao' => false,
                'ordem_motorista' => (int) $item['ordem'],
            ]);
        }

        if ($request->expectsJson() || $request->ajax()) {
            return response()->json(['ok' => true, 'message' => 'Lista atualizada com sucesso']);
        }

        return back()->with('success', 'Ordem atualizada.');
    }

    protected function validar(Request $request): array
    {
        $dados = $request->validate([
            'nome' => ['required', 'string', 'max:200'],
            'placa' => ['required', 'string', 'max:20'],
            'placa_carreta' => ['nullable', 'string', 'max:20'],
            'cpf' => ['required', 'string', 'max:20'],
            'celular' => ['nullable', 'string', 'max:30'],
            'ordem_motorista' => ['nullable', 'integer', 'min:1'],
            'aceita_bobina' => ['nullable', 'boolean'],
            'situacao' => ['nullable', 'boolean'],
        ]);

        $dados['aceita_bobina'] = $request->boolean('aceita_bobina');
        $dados['situacao'] = $request->boolean('situacao');
        $dados['ordem_motorista'] = (int) ($dados['ordem_motorista'] ?? 100);
        $dados['placa_carreta'] = $dados['placa_carreta'] ?? null;
        $dados['celular'] = trim((string) ($dados['celular'] ?? ''));

        return $this->completarCamposLegado($dados);
    }

    /**
     * Schema Boro ainda exige colunas legadas (celular/regioes_*) sem default.
     */
    protected function completarCamposLegado(array $dados): array
    {
        $schema = Schema::connection('tenant');

        if ($schema->hasColumn('motoristas', 'celular')) {
            $dados['celular'] = (string) ($dados['celular'] ?? '');
        } else {
            unset($dados['celular']);
        }

        if ($schema->hasColumn('motoristas', 'regioes_origem')) {
            $dados['regioes_origem'] = (string) ($dados['regioes_origem'] ?? '');
        }

        if ($schema->hasColumn('motoristas', 'regioes_cluster')) {
            $dados['regioes_cluster'] = (string) ($dados['regioes_cluster'] ?? '');
        }

        return $dados;
    }

    protected function syncRelacoes(Motorista $motorista, Request $request): void
    {
        $motorista->origens()->sync($request->input('origens', []));
        $motorista->destinos()->sync($request->input('destinos', []));
        $motorista->tiposVeiculo()->sync($request->input('tipos_veiculo', []));
        $motorista->tiposVeiculoCarreta()->sync($request->input('tipos_veiculo_carreta', []));
    }
}
