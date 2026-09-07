<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Destino;
use App\Models\LoginPortal;
use App\Models\Origem;
use App\Models\Parametro;
use App\Models\TipoVeiculo;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;

class ParametroController extends Controller
{
    public function index(Request $request): View
    {
        $buscaDestino = trim((string) $request->query('destino', ''));

        return view('admin.parametros.index', [
            'parametro' => Parametro::query()->orderBy('id')->first() ?? new Parametro([
                'limite_valor_truck' => 0,
                'limite_valor_toco' => 0,
                'limite_valor_carreta' => 0,
                'modo_teste' => true,
                'email_notificacao' => '',
                'intervalo_espera_seg' => 30,
            ]),
            'loginPortal' => LoginPortal::query()->orderBy('id')->first() ?? new LoginPortal([
                'ativo' => true,
            ]),
            'origens' => Origem::query()->orderBy('nome_origem')->get(),
            'destinos' => Destino::query()
                ->when($buscaDestino !== '', fn ($query) => $query->where('nome_destino', 'like', "%{$buscaDestino}%"))
                ->orderBy('nome_destino')
                ->paginate(30, ['*'], 'destinos_page')
                ->withQueryString(),
            'tipos' => TipoVeiculo::query()->orderBy('nome_tipo_veiculo')->get(),
            'buscaDestino' => $buscaDestino,
        ]);
    }

    public function atualizarValores(Request $request): RedirectResponse
    {
        $dados = $request->validate([
            'limite_valor_truck' => ['required', 'numeric', 'min:0'],
            'limite_valor_toco' => ['required', 'numeric', 'min:0'],
            'limite_valor_carreta' => ['required', 'numeric', 'min:0'],
            'email_notificacao' => ['nullable', 'string', 'max:255'],
            'intervalo_espera_seg' => ['required', 'integer', 'min:1'],
            'modo_teste' => ['nullable', 'boolean'],
        ]);

        $dados['modo_teste'] = $request->boolean('modo_teste');
        $dados['email_notificacao'] = $dados['email_notificacao'] ?? '';

        $parametro = Parametro::query()->orderBy('id')->first();
        if ($parametro) {
            $parametro->update($dados);
        } else {
            Parametro::query()->create($dados);
        }

        return back()->with('success', 'Parâmetros salvos.');
    }

    public function atualizarLogin(Request $request): RedirectResponse
    {
        $dados = $request->validate([
            'usuario' => ['required', 'string', 'max:100'],
            'senha' => ['required', 'string', 'max:255'],
            'ativo' => ['nullable', 'boolean'],
        ]);
        $dados['ativo'] = $request->boolean('ativo');

        $login = LoginPortal::query()->orderBy('id')->first();
        if ($login) {
            $login->update($dados);
        } else {
            LoginPortal::query()->create($dados);
        }

        return back()->with('success', 'Login do portal atualizado.');
    }

    public function storeOrigem(Request $request): RedirectResponse
    {
        $dados = $request->validate([
            'nome_origem' => ['required', 'string', 'max:150', 'unique:origens,nome_origem'],
        ]);
        Origem::query()->create([
            'nome_origem' => $dados['nome_origem'],
            'ativo' => true,
            'created_at' => now(),
        ]);

        return back()->with('success', 'Origem cadastrada.');
    }

    public function destroyOrigem(Origem $origem): RedirectResponse
    {
        $origem->delete();

        return back()->with('success', 'Origem removida.');
    }

    public function storeDestino(Request $request): RedirectResponse
    {
        $dados = $request->validate([
            'nome_destino' => ['required', 'string', 'max:150', 'unique:destinos,nome_destino'],
        ]);
        Destino::query()->create([
            'nome_destino' => $dados['nome_destino'],
            'ativo' => true,
            'created_at' => now(),
        ]);

        return back()->with('success', 'Destino cadastrado.');
    }

    public function destroyDestino(Destino $destino): RedirectResponse
    {
        $destino->delete();

        return back()->with('success', 'Destino removido.');
    }

    public function storeTipo(Request $request): RedirectResponse
    {
        $dados = $request->validate([
            'nome_tipo_veiculo' => ['required', 'string', 'max:50', 'unique:tipo_veiculo,nome_tipo_veiculo'],
        ]);
        TipoVeiculo::query()->create([
            'nome_tipo_veiculo' => $dados['nome_tipo_veiculo'],
            'created_at' => now(),
        ]);

        return back()->with('success', 'Tipo de veículo cadastrado.');
    }

    public function destroyTipo(TipoVeiculo $tipo): RedirectResponse
    {
        $tipo->delete();

        return back()->with('success', 'Tipo de veículo removido.');
    }
}
