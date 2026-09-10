<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Cliente;
use App\Models\User;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\Rule;
use Illuminate\Validation\Rules\Password;
use Illuminate\View\View;

class UsuarioController extends Controller
{
    public function index(): View
    {
        $usuarios = User::query()
            ->with('cliente')
            ->orderByDesc('is_super_admin')
            ->orderBy('name')
            ->get();

        return view('admin.usuarios.index', compact('usuarios'));
    }

    public function create(): View
    {
        return view('admin.usuarios.form', [
            'usuario' => new User(['is_super_admin' => false]),
            'clientes' => Cliente::query()->where('ativo', true)->orderBy('nome')->get(),
        ]);
    }

    public function store(Request $request): RedirectResponse
    {
        $dados = $this->validar($request);
        User::query()->create([
            'name' => $dados['name'],
            'email' => $dados['email'],
            'password' => Hash::make($dados['password']),
            'is_super_admin' => $dados['is_super_admin'],
            'cliente_id' => $dados['cliente_id'],
            'email_verified_at' => now(),
        ]);

        return redirect()
            ->route('admin.usuarios.index')
            ->with('success', 'Usuário criado.');
    }

    public function edit(User $usuario): View
    {
        return view('admin.usuarios.form', [
            'usuario' => $usuario,
            'clientes' => Cliente::query()->where('ativo', true)->orderBy('nome')->get(),
        ]);
    }

    public function update(Request $request, User $usuario): RedirectResponse
    {
        $dados = $this->validar($request, $usuario);
        $payload = [
            'name' => $dados['name'],
            'email' => $dados['email'],
            'is_super_admin' => $dados['is_super_admin'],
            'cliente_id' => $dados['cliente_id'],
        ];
        if (! empty($dados['password'])) {
            $payload['password'] = Hash::make($dados['password']);
        }
        $usuario->update($payload);

        return redirect()
            ->route('admin.usuarios.index')
            ->with('success', 'Usuário atualizado.');
    }

    /**
     * @return array<string, mixed>
     */
    protected function validar(Request $request, ?User $usuario = null): array
    {
        $isSuper = $request->boolean('is_super_admin');
        $senhaRules = $usuario
            ? ['nullable', 'confirmed', Password::defaults()]
            : ['required', 'confirmed', Password::defaults()];

        $dados = $request->validate([
            'name' => ['required', 'string', 'max:120'],
            'email' => [
                'required',
                'email',
                'max:255',
                Rule::unique('users', 'email')->ignore($usuario?->id),
            ],
            'password' => $senhaRules,
            'is_super_admin' => ['nullable', 'boolean'],
            'cliente_id' => [
                $isSuper ? 'nullable' : 'required',
                'nullable',
                'integer',
                'exists:clientes,id',
            ],
        ]);

        $dados['is_super_admin'] = $isSuper;
        $dados['cliente_id'] = $isSuper ? null : (int) $dados['cliente_id'];

        return $dados;
    }
}
