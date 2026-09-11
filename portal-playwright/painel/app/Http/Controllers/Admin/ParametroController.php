<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Destino;
use App\Models\LoginPortal;
use App\Models\Origem;
use App\Models\Parametro;
use App\Models\TipoVeiculo;
use App\Support\Tenant;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Validation\Rule;
use Illuminate\View\View;

class ParametroController extends Controller
{
    public function index(Request $request): View
    {
        $buscaDestino = trim((string) $request->query('destino', ''));
        $podeEditarLogin = (bool) $request->user()?->is_super_admin;

        return view('admin.parametros.index', [
            'parametro' => Parametro::query()->orderBy('id')->first() ?? new Parametro([
                'limite_valor_truck' => 0,
                'limite_valor_toco' => 0,
                'limite_valor_carreta' => 0,
                'modo_teste' => true,
                'email_notificacao' => '',
                'intervalo_espera_seg' => 30,
                'verificar_valor_carga' => true,
                'verificar_bobina' => true,
                'verificar_multiplos_destinos' => true,
                'whatsapp_telefones' => '',
                'whatsapp_codigo_estabelecimento' => null,
                'painel_url_publica' => 'https://efornecedor.reservaai.com.br',
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
            'podeEditarLogin' => $podeEditarLogin,
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
            'verificar_valor_carga' => ['nullable', 'boolean'],
            'verificar_bobina' => ['nullable', 'boolean'],
            'verificar_multiplos_destinos' => ['nullable', 'boolean'],
            'whatsapp_telefones' => ['nullable', 'string', 'max:2000'],
            'whatsapp_codigo_estabelecimento' => ['nullable', 'integer', 'min:1'],
            'painel_url_publica' => ['nullable', 'url', 'max:255'],
        ]);

        $dados['modo_teste'] = $request->boolean('modo_teste');
        $dados['verificar_valor_carga'] = $request->boolean('verificar_valor_carga');
        $dados['verificar_bobina'] = $request->boolean('verificar_bobina');
        $dados['verificar_multiplos_destinos'] = $request->boolean('verificar_multiplos_destinos');
        $dados['email_notificacao'] = $dados['email_notificacao'] ?? '';
        $dados['whatsapp_telefones'] = trim((string) ($dados['whatsapp_telefones'] ?? ''));
        $dados['painel_url_publica'] = rtrim((string) ($dados['painel_url_publica'] ?? ''), '/');
        if (($dados['whatsapp_codigo_estabelecimento'] ?? null) === '') {
            $dados['whatsapp_codigo_estabelecimento'] = null;
        }

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
        if (! $request->user()?->is_super_admin) {
            abort(403, 'Somente o super admin pode alterar o login do portal.');
        }

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
        $regrasNome = ['required', 'string', 'max:150'];
        if (Tenant::usaBancoProprio()) {
            $regrasNome[] = Rule::unique('origens', 'nome_origem')->connection('tenant');
        } else {
            $clienteId = Tenant::requireId();
            $regrasNome[] = Rule::unique('origens', 'nome_origem')
                ->connection('tenant')
                ->where(fn ($query) => $query->where('cliente_id', $clienteId));
        }
        $dados = $request->validate([
            'nome_origem' => $regrasNome,
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
        $regrasNome = ['required', 'string', 'max:150'];
        if (Tenant::usaBancoProprio()) {
            $regrasNome[] = Rule::unique('destinos', 'nome_destino')->connection('tenant');
        } else {
            $clienteId = Tenant::requireId();
            $regrasNome[] = Rule::unique('destinos', 'nome_destino')
                ->connection('tenant')
                ->where(fn ($query) => $query->where('cliente_id', $clienteId));
        }
        $dados = $request->validate([
            'nome_destino' => $regrasNome,
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
        $regrasNome = ['required', 'string', 'max:50'];
        if (Tenant::usaBancoProprio()) {
            $regrasNome[] = Rule::unique('tipo_veiculo', 'nome_tipo_veiculo')->connection('tenant');
        } else {
            $clienteId = Tenant::requireId();
            $regrasNome[] = Rule::unique('tipo_veiculo', 'nome_tipo_veiculo')
                ->connection('tenant')
                ->where(fn ($query) => $query->where('cliente_id', $clienteId));
        }
        $dados = $request->validate([
            'nome_tipo_veiculo' => $regrasNome,
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
