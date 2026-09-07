<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Relatorio;
use Illuminate\Http\Request;
use Illuminate\View\View;
use Symfony\Component\HttpFoundation\StreamedResponse;

class RelatorioController extends Controller
{
    public function index(Request $request): View
    {
        $busca = trim((string) $request->query('q', ''));
        $motivo = trim((string) $request->query('motivo', ''));

        $relatorios = Relatorio::query()
            ->when($busca !== '', function ($query) use ($busca) {
                $query->where(function ($inner) use ($busca) {
                    $inner->where('doc_transporte', 'like', "%{$busca}%")
                        ->orWhere('origem_rota', 'like', "%{$busca}%")
                        ->orWhere('destino_rota', 'like', "%{$busca}%");
                });
            })
            ->when($motivo !== '', fn ($query) => $query->where('motivo', 'like', "%{$motivo}%"))
            ->orderByDesc('id')
            ->paginate(30)
            ->withQueryString();

        return view('admin.relatorios.index', compact('relatorios', 'busca', 'motivo'));
    }

    public function export(Request $request): StreamedResponse
    {
        $busca = trim((string) $request->query('q', ''));
        $motivo = trim((string) $request->query('motivo', ''));

        $query = Relatorio::query()
            ->when($busca !== '', function ($builder) use ($busca) {
                $builder->where(function ($inner) use ($busca) {
                    $inner->where('doc_transporte', 'like', "%{$busca}%")
                        ->orWhere('origem_rota', 'like', "%{$busca}%")
                        ->orWhere('destino_rota', 'like', "%{$busca}%");
                });
            })
            ->when($motivo !== '', fn ($builder) => $builder->where('motivo', 'like', "%{$motivo}%"))
            ->orderByDesc('id');

        $filename = 'relatorios-'.now()->format('Y-m-d-His').'.csv';

        return response()->streamDownload(function () use ($query) {
            $handle = fopen('php://output', 'w');
            fputcsv($handle, [
                'id', 'doc_transporte', 'origem_rota', 'destino_rota', 'data_hora_chegada',
                'valor_carga', 'peso_total', 'tipo_veiculo', 'motivo', 'created_at',
            ]);

            $query->chunk(200, function ($linhas) use ($handle) {
                foreach ($linhas as $linha) {
                    fputcsv($handle, [
                        $linha->id,
                        $linha->doc_transporte,
                        $linha->origem_rota,
                        $linha->destino_rota,
                        $linha->data_hora_chegada,
                        $linha->valor_carga,
                        $linha->peso_total,
                        $linha->tipo_veiculo,
                        $linha->motivo,
                        optional($linha->created_at)?->toDateTimeString(),
                    ]);
                }
            });

            fclose($handle);
        }, $filename, [
            'Content-Type' => 'text/csv; charset=UTF-8',
        ]);
    }
}
