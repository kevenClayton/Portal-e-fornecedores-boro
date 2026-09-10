<?php

namespace App\Http\Controllers;

use App\Models\NotificacaoCarga;
use Illuminate\View\View;

class CargaPublicaController extends Controller
{
    public function show(string $publicId): View
    {
        $notificacao = NotificacaoCarga::withoutGlobalScopes()
            ->where('public_id', $publicId)
            ->firstOrFail();

        return view('public.carga', [
            'notificacao' => $notificacao,
        ]);
    }
}
