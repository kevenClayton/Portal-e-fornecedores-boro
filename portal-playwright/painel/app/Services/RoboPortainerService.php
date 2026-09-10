<?php

namespace App\Services;

use Exception;
use Illuminate\Support\Facades\Http;

class RoboPortainerService
{
    /** @var list<string> */
    protected array $containerNames;

    protected string $baseUrl;

    protected string $apiKey;

    protected int $endpointId;

    public function __construct()
    {
        $this->baseUrl = (string) config('robo.portainer_url');
        $this->apiKey = (string) config('robo.portainer_api_key');
        $this->endpointId = (int) config('robo.portainer_endpoint_id', 1);
        $this->aplicarContainersPadrao();
    }

    public function aplicarContainersPadrao(): void
    {
        $nomes = config('robo.container_names', []);
        if (! is_array($nomes) || $nomes === []) {
            $nomes = [(string) config('robo.container_name', 'portal-fornecedores')];
        }
        $this->definirContainers($nomes);
    }

    /**
     * @param  list<string>  $nomes
     */
    public function definirContainers(array $nomes): void
    {
        $filtrados = array_values(array_unique(array_filter(array_map('strval', $nomes))));
        $this->containerNames = $filtrados !== []
            ? $filtrados
            : [(string) config('robo.container_name', 'portal-fornecedores')];
    }

    /**
     * @return list<string>
     */
    public function nomesDisponiveis(): array
    {
        return $this->containerNames;
    }

    /**
     * @return list<string>
     */
    public function nomesAtivos(int $quantidade): array
    {
        $quantidade = max(1, min(count($this->containerNames), $quantidade));

        return array_slice($this->containerNames, 0, $quantidade);
    }

    public function status(?int $quantidadeDesejada = null): array
    {
        $robots = [];
        foreach ($this->containerNames as $indice => $nome) {
            $slot = $indice + 1;
            $robots[] = array_merge(
                $this->statusUm($nome),
                ['slot' => $slot, 'active_slot' => $quantidadeDesejada === null || $slot <= $quantidadeDesejada],
            );
        }

        $ligados = array_values(array_filter(
            $robots,
            fn (array $robot) => ($robot['active_slot'] ?? true) && ($robot['running'] ?? false),
        ));
        $runningCount = count(array_filter($robots, fn (array $robot) => $robot['running'] ?? false));

        return [
            'running' => $runningCount > 0,
            'running_count' => $runningCount,
            'desired_count' => $quantidadeDesejada,
            'robots' => $robots,
            'name' => $this->containerNames[0] ?? 'portal-fornecedores',
            'status' => $runningCount > 0 ? 'running' : 'stopped',
            'message' => $runningCount > 0
                ? "{$runningCount} robô(s) em execução"
                : 'Nenhum robô em execução',
        ];
    }

    public function start(int $quantidade = 1): array
    {
        $ativos = $this->nomesAtivos($quantidade);
        $erros = [];

        foreach ($this->containerNames as $nome) {
            try {
                if (in_array($nome, $ativos, true)) {
                    $this->executarAcao($nome, 'start');
                } else {
                    $this->executarAcao($nome, 'stop');
                }
            } catch (Exception $erro) {
                $erros[] = "{$nome}: ".$erro->getMessage();
            }
        }

        $status = $this->status($quantidade);
        if ($erros !== [] && ($status['running_count'] ?? 0) === 0) {
            throw new Exception(implode(' | ', $erros));
        }

        return $status;
    }

    public function stop(): array
    {
        $erros = [];
        foreach ($this->containerNames as $nome) {
            try {
                $this->executarAcao($nome, 'stop');
            } catch (Exception $erro) {
                $erros[] = "{$nome}: ".$erro->getMessage();
            }
        }

        $status = $this->status(0);
        if ($erros !== [] && ($status['running_count'] ?? 0) > 0) {
            throw new Exception(implode(' | ', $erros));
        }

        return $status;
    }

    public function logs(int $tail = 200, ?int $slot = null): string
    {
        $tail = max(20, min(400, $tail));
        if ($slot !== null) {
            $indice = max(1, min(count($this->containerNames), $slot)) - 1;
            $nome = $this->containerNames[$indice];

            return "===== {$nome} (slot ".($indice + 1).") =====\n".$this->logsUm($nome, $tail);
        }

        // Só o primeiro container por padrão (rápido). Evita bloquear o php -S com 3x docker logs.
        $nome = $this->containerNames[0] ?? 'portal-fornecedores';

        return "===== {$nome} (slot 1) =====\n".$this->logsUm($nome, $tail)
            ."\n\n(Dica: logs dos slots 2/3 sob demanda — use ?slot=2 ou ?slot=3)";
    }

    protected function statusUm(string $nome): array
    {
        if (config('robo.usar_docker_cli')) {
            $escaped = escapeshellarg($nome);
            $estado = trim((string) shell_exec("timeout 2s docker inspect -f '{{.State.Status}}' {$escaped} 2>/dev/null"));
            $running = $estado === 'running';

            return [
                'running' => $running,
                'status' => $estado !== '' ? $estado : 'not_found',
                'name' => $nome,
                'message' => $running ? 'Em execução' : ($estado !== '' ? 'Parado' : 'Container não encontrado'),
            ];
        }

        $container = $this->encontrarContainer($nome);
        if (! $container) {
            return [
                'running' => false,
                'status' => 'not_found',
                'name' => $nome,
                'message' => 'Container não encontrado',
            ];
        }

        $state = $container['State'] ?? 'unknown';
        $running = $state === 'running';

        return [
            'running' => $running,
            'status' => $state,
            'id' => $container['Id'] ?? null,
            'name' => $nome,
            'message' => $running ? 'Em execução' : 'Parado',
        ];
    }

    protected function executarAcao(string $nome, string $acao): void
    {
        $acao = $acao === 'start' ? 'start' : 'stop';

        if (config('robo.usar_docker_cli')) {
            $escaped = escapeshellarg($nome);
            shell_exec("docker {$acao} {$escaped} 2>&1");

            return;
        }

        $container = $this->encontrarContainer($nome);
        if (! $container) {
            if ($acao === 'stop') {
                return;
            }
            throw new Exception('Container não encontrado: '.$nome);
        }

        $path = $acao === 'start'
            ? "/api/endpoints/{$this->endpointId}/docker/containers/{$container['Id']}/start"
            : "/api/endpoints/{$this->endpointId}/docker/containers/{$container['Id']}/stop?t=10";

        $response = $this->request('POST', $path);
        if ($response['status'] >= 400 && $response['status'] !== 304) {
            throw new Exception('Falha ao '.$acao.': HTTP '.$response['status'].' '.$response['body']);
        }
    }

    protected function logsUm(string $nome, int $tail): string
    {
        if (config('robo.usar_docker_cli')) {
            $escaped = escapeshellarg($nome);
            $tail = max(10, min(200, $tail));
            $saida = (string) shell_exec("timeout 2s docker logs --tail {$tail} {$escaped} 2>&1");
            if ($saida === '') {
                return "(sem saída / timeout ao ler logs de {$nome})";
            }

            return $saida;
        }

        $container = $this->encontrarContainer($nome);
        if (! $container) {
            return "Container não encontrado: {$nome}\n";
        }

        $query = http_build_query([
            'stdout' => 1,
            'stderr' => 1,
            'timestamps' => 0,
            'tail' => $tail,
        ]);

        $response = $this->request('GET', "/api/endpoints/{$this->endpointId}/docker/containers/{$container['Id']}/logs?{$query}");
        if ($response['status'] >= 400) {
            return 'Erro ao ler logs: HTTP '.$response['status'];
        }

        return $this->limparLogsDocker($response['body']);
    }

    protected function encontrarContainer(string $nome): ?array
    {
        $this->garantirConfig();

        $response = $this->request('GET', "/api/endpoints/{$this->endpointId}/docker/containers/json?all=1");
        if ($response['status'] >= 400) {
            throw new Exception('Falha ao listar containers no Portainer: HTTP '.$response['status']);
        }

        $containers = json_decode($response['body'], true);
        if (! is_array($containers)) {
            return null;
        }

        foreach ($containers as $container) {
            foreach ($container['Names'] ?? [] as $name) {
                if (trim($name, '/') === trim($nome, '/')) {
                    return $container;
                }
            }
        }

        return null;
    }

    /**
     * @return array{status:int,body:string}
     */
    protected function request(string $method, string $path): array
    {
        $this->garantirConfig();

        $http = Http::withHeaders(['X-API-Key' => $this->apiKey])
            ->timeout(30)
            ->withoutVerifying()
            ->baseUrl($this->baseUrl);

        $response = match (strtoupper($method)) {
            'POST' => $http->post($path),
            default => $http->get($path),
        };

        return [
            'status' => $response->status(),
            'body' => $response->body(),
        ];
    }

    protected function garantirConfig(): void
    {
        if ($this->baseUrl === '' || $this->apiKey === '') {
            throw new Exception('Configure ROBO_PORTAINER_URL e ROBO_PORTAINER_API_KEY no .env do painel.');
        }
    }

    protected function limparLogsDocker(string $raw): string
    {
        if ($raw === '') {
            return '';
        }

        if (! str_contains($raw, "\0") && preg_match('/^[\x09\x0A\x0D\x20-\x7E\xC2-\xF4]/', $raw)) {
            return $raw;
        }

        $saida = '';
        $offset = 0;
        $length = strlen($raw);

        while ($offset + 8 <= $length) {
            $header = substr($raw, $offset, 8);
            $size = unpack('N', substr($header, 4, 4))[1];
            $offset += 8;
            if ($size <= 0 || $offset + $size > $length) {
                break;
            }
            $saida .= substr($raw, $offset, $size);
            $offset += $size;
        }

        return $saida !== '' ? $saida : $raw;
    }
}
