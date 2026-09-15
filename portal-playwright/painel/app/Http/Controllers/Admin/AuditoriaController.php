<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\RoboAuditoria;
use Illuminate\Http\Request;
use Illuminate\Support\Carbon;
use Illuminate\View\View;

class AuditoriaController extends Controller
{
    public function index(Request $request): View
    {
        $busca = trim((string) $request->query('q', ''));
        $tipo = trim((string) $request->query('tipo', ''));
        $decisao = trim((string) $request->query('decisao', ''));
        $data = trim((string) $request->query('data', ''));

        $dia = today();
        if ($data !== '') {
            try {
                $dia = Carbon::createFromFormat('Y-m-d', $data)->startOfDay();
            } catch (\Throwable) {
                $dia = today();
                $data = '';
            }
        }

        $baseDia = RoboAuditoria::query()->whereDate('created_at', $dia);

        $captchasHoje = (clone $baseDia)->where('tipo_evento', 'captcha')->count();
        $captchasLogin = (clone $baseDia)->where('tipo_evento', 'captcha')->where('origem_captcha', 'Login')->count();
        $captchasPesquisar = (clone $baseDia)->where('tipo_evento', 'captcha')->whereIn('origem_captcha', ['Pesquisar', 'Filtrar'])->count();
        $vinculadosHoje = (clone $baseDia)->where('decisao', 'vinculado')->count();
        $puladosHoje = (clone $baseDia)->where('decisao', 'pulado')->count();
        $rejeitadosHoje = (clone $baseDia)->where('decisao', 'rejeitado')->count();

        $eventos = RoboAuditoria::query()
            ->when($busca !== '', function ($query) use ($busca) {
                $query->where(function ($inner) use ($busca) {
                    $inner->where('doc_transporte', 'like', "%{$busca}%")
                        ->orWhere('destino', 'like', "%{$busca}%")
                        ->orWhere('motivo', 'like', "%{$busca}%")
                        ->orWhere('proxy_host', 'like', "%{$busca}%");
                });
            })
            ->when($tipo !== '', fn ($query) => $query->where('tipo_evento', $tipo))
            ->when($decisao !== '', fn ($query) => $query->where('decisao', $decisao))
            ->when($data !== '', fn ($query) => $query->whereDate('created_at', $dia))
            ->orderByDesc('id')
            ->paginate(40)
            ->withQueryString();

        return view('admin.auditoria.index', [
            'eventos' => $eventos,
            'busca' => $busca,
            'tipo' => $tipo,
            'decisao' => $decisao,
            'data' => $data !== '' ? $dia->format('Y-m-d') : '',
            'diaLabel' => $dia->format('d/m/Y'),
            'captchasHoje' => $captchasHoje,
            'captchasLogin' => $captchasLogin,
            'captchasPesquisar' => $captchasPesquisar,
            'vinculadosHoje' => $vinculadosHoje,
            'puladosHoje' => $puladosHoje,
            'rejeitadosHoje' => $rejeitadosHoje,
        ]);
    }
}
