<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Parametro;
use App\Models\RoboAcompanhamento;
use App\Models\RoboEvento;
use App\Services\RoboPortainerService;
use App\Support\Tenant;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Illuminate\Support\Facades\File;
use Illuminate\View\View;
use Throwable;

class RoboController extends Controller
{
    public function __construct(protected RoboPortainerService $robo)
    {
    }

    public function index(): View
    {
        $this->aplicarContainersDoCliente();

        // Não busca docker logs no carregamento: trava o php -S (single-thread)
        // e derruba o site inteiro. Logs só na aba Terminal via AJAX.
        $logs = "Abra a aba Terminal e clique em Atualizar (ou ligue o refresh automático).";

        $parametro = Parametro::query()->orderBy('id')->first() ?? new Parametro([
            'intervalo_espera_seg' => 15,
            'robo_quantidade' => 1,
            'verificar_valor_carga' => true,
            'verificar_bobina' => true,
            'verificar_multiplos_destinos' => true,
        ]);

        $acompanhamento = RoboAcompanhamento::query()->orderBy('id')->first();
        $eventos = RoboEvento::query()->orderByDesc('id')->limit(40)->get();
        $maxRobos = $this->maxRobosCliente();
        $quantidade = max(1, min($maxRobos, (int) ($parametro->robo_quantidade ?? 1)));
        // Status Docker só via AJAX — inspect no carregamento derruba o php -S
        $status = [
            'running' => false,
            'running_count' => 0,
            'desired_count' => $quantidade,
            'robots' => [],
            'status' => 'unknown',
            'message' => 'Carregando status…',
            'name' => config('robo.container_name'),
        ];
        $containersConfigurados = count($this->robo->nomesDisponiveis()) > 0
            && Tenant::cliente()?->listaContainers() !== [];

        return view('admin.robo.index', compact(
            'status',
            'logs',
            'parametro',
            'acompanhamento',
            'eventos',
            'quantidade',
            'maxRobos',
            'containersConfigurados',
        ));
    }

    public function status(): JsonResponse
    {
        try {
            $this->aplicarContainersDoCliente();
            $maxRobos = $this->maxRobosCliente();
            $quantidade = (int) (Parametro::query()->orderBy('id')->value('robo_quantidade') ?: 1);

            return response()->json(['ok' => true, 'data' => $this->robo->status(max(1, min($maxRobos, $quantidade)))]);
        } catch (Throwable $erro) {
            return response()->json(['ok' => false, 'message' => $erro->getMessage()], 422);
        }
    }

    public function acompanhamento(): JsonResponse
    {
        $this->aplicarContainersDoCliente();
        $acompanhamento = RoboAcompanhamento::query()->orderBy('id')->first();
        $eventos = RoboEvento::query()
            ->orderByDesc('id')
            ->limit(40)
            ->get()
            ->map(fn (RoboEvento $evento) => [
                'etapa' => $evento->etapa,
                'mensagem' => $evento->mensagem,
                'horario' => optional($evento->created_at)->timezone(config('app.timezone'))->format('H:i:s'),
            ]);

        $labels = [
            'parado' => 'Parado',
            'login' => 'Login',
            'busca' => 'Buscando cargas',
            'filtro' => 'Filtrando clusters',
            'detalhe' => 'Detalhe da carga',
            'vinculo' => 'Vinculação',
            'erro' => 'Erro',
            'info' => 'Em operação',
        ];

        $maxRobos = $this->maxRobosCliente();
        $quantidade = max(1, min($maxRobos, (int) (Parametro::query()->orderBy('id')->value('robo_quantidade') ?: 1)));

        return response()->json([
            'ok' => true,
            'acompanhamento' => [
                'etapa' => $acompanhamento?->etapa ?? 'parado',
                'etapa_label' => $labels[$acompanhamento?->etapa ?? 'parado'] ?? 'Em operação',
                'mensagem' => $acompanhamento?->mensagem ?? 'Sem atualização ainda',
                'cluster_atual' => $acompanhamento?->cluster_atual,
                'documento_atual' => $acompanhamento?->documento_atual,
                'resumo_ciclo' => $acompanhamento?->resumo_ciclo,
                'atualizado_em' => optional($acompanhamento?->atualizado_em)->timezone(config('app.timezone'))->format('d/m/Y H:i:s'),
                'screenshot_em' => optional($acompanhamento?->screenshot_em)->timezone(config('app.timezone'))->format('d/m/Y H:i:s'),
                'tem_screenshot' => $this->caminhoScreenshot() !== null,
            ],
            'eventos' => $eventos,
            'status' => $this->statusSeguro($quantidade),
            'quantidade' => $quantidade,
        ]);
    }

    public function pedirScreenshot(): JsonResponse
    {
        $registro = RoboAcompanhamento::query()->orderBy('id')->first();
        if (! $registro) {
            RoboAcompanhamento::query()->create([
                'etapa' => 'info',
                'mensagem' => 'Pedido de screenshot',
                'pedir_screenshot' => true,
            ]);
        } else {
            $registro->update(['pedir_screenshot' => true]);
        }

        return response()->json([
            'ok' => true,
            'message' => 'Pedido enviado. A próxima atualização do robô captura a tela.',
        ]);
    }

    public function screenshot(): Response
    {
        $caminho = $this->caminhoScreenshot();
        if (! $caminho) {
            abort(404, 'Screenshot ainda não disponível');
        }

        return response(File::get($caminho), 200, [
            'Content-Type' => 'image/png',
            'Cache-Control' => 'no-store, no-cache, must-revalidate',
        ]);
    }

    public function start(Request $request): RedirectResponse
    {
        $maxRobos = $this->maxRobosCliente();
        $dados = $request->validate([
            'intervalo_espera_seg' => ['required', 'integer', 'min:5', 'max:3600'],
            'robo_quantidade' => ['required', 'integer', 'min:1', 'max:'.$maxRobos],
            'verificar_valor_carga' => ['nullable', 'boolean'],
            'verificar_bobina' => ['nullable', 'boolean'],
            'verificar_multiplos_destinos' => ['nullable', 'boolean'],
        ]);

        try {
            $this->aplicarContainersDoCliente();
            $containers = Tenant::cliente()?->listaContainers() ?? [];
            if ($containers === []) {
                return back()->with('error', 'Este cliente ainda não tem containers Docker configurados. Peça ao super admin para definir em Clientes.');
            }

            $quantidade = (int) $dados['robo_quantidade'];
            $this->salvarOpcoesCiclo(
                (int) $dados['intervalo_espera_seg'],
                $quantidade,
                $request->boolean('verificar_valor_carga'),
                $request->boolean('verificar_bobina'),
                $request->boolean('verificar_multiplos_destinos'),
            );
            $this->robo->start($quantidade);

            return back()->with(
                'success',
                "Frota iniciada: {$quantidade} robô(s), busca a cada {$dados['intervalo_espera_seg']}s."
            );
        } catch (Throwable $erro) {
            return back()->with('error', $erro->getMessage());
        }
    }

    public function stop(): RedirectResponse
    {
        try {
            $this->aplicarContainersDoCliente();
            $this->robo->stop();
            $registro = RoboAcompanhamento::query()->orderBy('id')->first();
            if ($registro) {
                $registro->update(['etapa' => 'parado', 'mensagem' => 'Robô parado pelo painel']);
            } else {
                RoboAcompanhamento::query()->create([
                    'etapa' => 'parado',
                    'mensagem' => 'Robô parado pelo painel',
                ]);
            }

            return back()->with('success', 'Robô parado.');
        } catch (Throwable $erro) {
            return back()->with('error', $erro->getMessage());
        }
    }

    public function salvarAgenda(Request $request): RedirectResponse
    {
        $dados = $request->validate([
            'robo_hora_ligar' => ['required', 'date_format:H:i'],
            'robo_hora_desligar' => ['required', 'date_format:H:i'],
            'robo_agenda_ativa' => ['nullable', 'boolean'],
        ]);

        $agenda = [
            'robo_agenda_ativa' => $request->boolean('robo_agenda_ativa'),
            'robo_hora_ligar' => $dados['robo_hora_ligar'].':00',
            'robo_hora_desligar' => $dados['robo_hora_desligar'].':00',
        ];

        $parametro = Parametro::query()->orderBy('id')->first();
        if ($parametro) {
            $parametro->update($agenda);
        } else {
            Parametro::query()->create(array_merge([
                'limite_valor_truck' => 0,
                'limite_valor_toco' => 0,
                'limite_valor_carreta' => 0,
                'modo_teste' => true,
                'email_notificacao' => '',
                'intervalo_espera_seg' => 30,
                'verificar_valor_carga' => true,
                'verificar_bobina' => true,
                'verificar_multiplos_destinos' => true,
            ], $agenda));
        }

        $mensagem = $agenda['robo_agenda_ativa']
            ? 'Agenda ativada: liga às '.substr($agenda['robo_hora_ligar'], 0, 5)
                .' e desliga às '.substr($agenda['robo_hora_desligar'], 0, 5).' (horário de Brasília).'
            : 'Agenda desativada. Use Iniciar/Parar manualmente.';

        return back()->with('success', $mensagem);
    }

    public function logs(Request $request): JsonResponse
    {
        $tail = max(30, min(300, (int) $request->query('tail', 80)));
        $slot = $request->query('slot');
        $slotFiltro = is_numeric($slot) ? (int) $slot : null;

        try {
            $this->aplicarContainersDoCliente();

            return response()->json([
                'ok' => true,
                'logs' => $this->robo->logs($tail, $slotFiltro),
            ]);
        } catch (Throwable $erro) {
            return response()->json(['ok' => false, 'message' => $erro->getMessage()], 422);
        }
    }

    protected function caminhoScreenshot(): ?string
    {
        $candidatos = [
            '/var/robo-logs/screenshots/atual.png',
            '/var/robo-logs/screenshots/atual_1.png',
            '/var/robo-logs/screenshots/atual_2.png',
            '/var/robo-logs/screenshots/atual_3.png',
            storage_path('app/robo-screenshot.png'),
        ];
        foreach ($candidatos as $caminho) {
            if (is_file($caminho) && filesize($caminho) > 0) {
                return $caminho;
            }
        }

        return null;
    }

    protected function salvarOpcoesCiclo(
        int $intervaloEsperaSeg,
        int $roboQuantidade,
        bool $verificarValor,
        bool $verificarBobina,
        bool $verificarDestinos,
    ): void {
        $maxRobos = $this->maxRobosCliente();
        $dados = [
            'intervalo_espera_seg' => $intervaloEsperaSeg,
            'robo_quantidade' => max(1, min($maxRobos, $roboQuantidade)),
            'verificar_valor_carga' => $verificarValor,
            'verificar_bobina' => $verificarBobina,
            'verificar_multiplos_destinos' => $verificarDestinos,
        ];

        $parametro = Parametro::query()->orderBy('id')->first();
        if ($parametro) {
            $parametro->update($dados);

            return;
        }

        Parametro::query()->create(array_merge([
            'limite_valor_truck' => 0,
            'limite_valor_toco' => 0,
            'limite_valor_carreta' => 0,
            'modo_teste' => true,
            'email_notificacao' => '',
        ], $dados));
    }

    protected function statusSeguro(?int $quantidade = null): array
    {
        try {
            return $this->robo->status($quantidade);
        } catch (Throwable $erro) {
            return [
                'running' => false,
                'running_count' => 0,
                'desired_count' => $quantidade,
                'robots' => [],
                'status' => 'error',
                'message' => $erro->getMessage(),
                'name' => config('robo.container_name'),
            ];
        }
    }

    protected function aplicarContainersDoCliente(): void
    {
        $cliente = Tenant::cliente();
        $containers = $cliente?->listaContainers() ?? [];
        if ($containers !== []) {
            $this->robo->definirContainers($containers);
        } else {
            $this->robo->aplicarContainersPadrao();
        }
    }

    protected function maxRobosCliente(): int
    {
        return Tenant::cliente()?->maxRobosEfetivo() ?? 1;
    }
}
