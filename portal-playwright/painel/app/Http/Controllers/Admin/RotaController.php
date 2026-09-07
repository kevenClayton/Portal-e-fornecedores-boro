<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Rota;
use Illuminate\Http\Request;
use Illuminate\View\View;

class RotaController extends Controller
{
    public function index(Request $request): View
    {
        $busca = trim((string) $request->query('q', ''));

        $rotas = Rota::query()
            ->when($busca !== '', function ($query) use ($busca) {
                $query->where(function ($inner) use ($busca) {
                    $inner->where('doc_transporte', 'like', "%{$busca}%")
                        ->orWhere('motorista_rota', 'like', "%{$busca}%")
                        ->orWhere('origem_rota', 'like', "%{$busca}%")
                        ->orWhere('destino_rota', 'like', "%{$busca}%");
                });
            })
            ->orderByDesc('id')
            ->paginate(30)
            ->withQueryString();

        return view('admin.rotas.index', compact('rotas', 'busca'));
    }
}
