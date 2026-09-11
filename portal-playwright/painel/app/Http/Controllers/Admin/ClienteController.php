<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Cliente;
use App\Models\LoginPortal;
use App\Models\Parametro;
use App\Support\Tenant;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Str;
use Illuminate\Validation\Rule;
use Illuminate\View\View;

class ClienteController extends Controller
{
    public function index(): View
    {
        $clientes = Cliente::query()->orderBy('nome')->get();

        return view('admin.clientes.index', compact('clientes'));
    }

    public function create(): View
    {
        return view('admin.clientes.form', [
            'cliente' => new Cliente([
                'cor_primaria' => '#011a41',
                'cor_accent' => '#01122e',
                'max_robos' => 1,
                'db_port' => 3306,
                'ativo' => true,
            ]),
        ]);
    }

    public function store(Request $request): RedirectResponse
    {
        $dados = $this->validar($request);
        $senhaDb = $dados['db_password'] ?? null;
        unset($dados['db_password']);

        $cliente = new Cliente($dados);
        $cliente->definirSenhaDb($senhaDb);
        $cliente->save();

        $this->seedDadosBasicos($cliente);

        return redirect()
            ->route('admin.clientes.index')
            ->with('success', "Cliente {$cliente->nome} criado.");
    }

    public function edit(Cliente $cliente): View
    {
        return view('admin.clientes.form', compact('cliente'));
    }

    public function update(Request $request, Cliente $cliente): RedirectResponse
    {
        $dados = $this->validar($request, $cliente);
        $senhaDb = $dados['db_password'] ?? null;
        unset($dados['db_password']);

        $cliente->fill($dados);
        $cliente->definirSenhaDb($senhaDb);
        $cliente->save();

        return redirect()
            ->route('admin.clientes.index')
            ->with('success', 'Cliente atualizado.');
    }

    public function selecionar(Request $request, Cliente $cliente): RedirectResponse
    {
        if (! $cliente->ativo) {
            return back()->with('error', 'Cliente inativo.');
        }

        $request->session()->put('cliente_ativo_id', $cliente->id);
        Tenant::set((int) $cliente->id);

        return back()->with('success', "Gerenciando: {$cliente->nome}");
    }

    /**
     * @return array<string, mixed>
     */
    protected function validar(Request $request, ?Cliente $cliente = null): array
    {
        $clienteId = $cliente?->id;
        $dados = $request->validate([
            'nome' => ['required', 'string', 'max:120'],
            'slug' => [
                'nullable',
                'string',
                'max:80',
                'regex:/^[a-z0-9\-]+$/',
                Rule::unique(Cliente::class, 'slug')->ignore($clienteId),
            ],
            'cor_primaria' => ['required', 'regex:/^#[0-9A-Fa-f]{6}$/'],
            'cor_accent' => ['required', 'regex:/^#[0-9A-Fa-f]{6}$/'],
            'max_robos' => ['required', 'integer', 'min:1', 'max:3'],
            'containers' => ['nullable', 'string', 'max:500'],
            'db_host' => ['nullable', 'string', 'max:255'],
            'db_port' => ['nullable', 'integer', 'min:1', 'max:65535'],
            'db_database' => ['nullable', 'string', 'max:120'],
            'db_username' => ['nullable', 'string', 'max:120'],
            'db_password' => ['nullable', 'string', 'max:255'],
            'ativo' => ['nullable', 'boolean'],
        ]);

        $dados['ativo'] = $request->boolean('ativo', true);
        $dados['containers'] = trim((string) ($dados['containers'] ?? ''));
        if ($dados['containers'] === '') {
            $dados['containers'] = null;
        }

        foreach (['db_host', 'db_database', 'db_username'] as $campo) {
            $dados[$campo] = trim((string) ($dados[$campo] ?? ''));
            if ($dados[$campo] === '') {
                $dados[$campo] = null;
            }
        }
        $dados['db_port'] = $dados['db_port'] ?: 3306;

        $slug = trim((string) ($dados['slug'] ?? ''));
        if ($slug === '') {
            $slug = Str::slug($dados['nome']);
        }
        $dados['slug'] = $slug !== '' ? $slug : 'cliente-'.Str::random(6);

        return $dados;
    }

    protected function seedDadosBasicos(Cliente $cliente): void
    {
        Tenant::set((int) $cliente->id);

        try {
            if ($cliente->temBancoProprio()) {
                if (! Parametro::query()->exists()) {
                    Parametro::query()->create([
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
                        'painel_url_publica' => 'https://efornecedor.reservaai.com.br',
                        'robo_quantidade' => 1,
                        'robo_agenda_ativa' => false,
                    ]);
                }
                if (! LoginPortal::query()->exists()) {
                    LoginPortal::query()->create([
                        'usuario' => '',
                        'senha' => '',
                        'ativo' => false,
                    ]);
                }

                return;
            }

            Parametro::withoutGlobalScopes()->updateOrCreate(
                ['cliente_id' => $cliente->id],
                [
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
                    'robo_quantidade' => 1,
                    'robo_agenda_ativa' => false,
                ]
            );

            LoginPortal::withoutGlobalScopes()->updateOrCreate(
                ['cliente_id' => $cliente->id],
                [
                    'usuario' => '',
                    'senha' => '',
                    'ativo' => false,
                ]
            );
        } finally {
            // conexão permanece no cliente selecionado da sessão
        }
    }
}
