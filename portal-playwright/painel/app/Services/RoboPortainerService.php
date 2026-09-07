<?php

namespace App\Services;

use Exception;
use Illuminate\Support\Facades\Http;

class RoboPortainerService
{
    protected string $baseUrl;

    protected string $apiKey;

    protected int $endpointId;

    protected string $containerName;

    public function __construct()
    {
        $this->baseUrl = (string) config('robo.portainer_url');
        $this->apiKey = (string) config('robo.portainer_api_key');
        $this->endpointId = (int) config('robo.portainer_endpoint_id', 1);
        $this->containerName = (string) config('robo.container_name', 'portal-fornecedores');
    }

    public function status(): array
    {
        if (config('robo.usar_docker_cli')) {
            return $this->statusDockerCli();
        }

        $container = $this->encontrarContainer();
        if (! $container) {
            return [
                'running' => false,
                'status' => 'not_found',
                'message' => 'Container não encontrado: '.$this->containerName,
                'name' => $this->containerName,
            ];
        }

        $state = $container['State'] ?? 'unknown';
        $running = $state === 'running';

        return [
            'running' => $running,
            'status' => $state,
            'id' => $container['Id'] ?? null,
            'name' => $this->containerName,
            'message' => $running ? 'Robô em execução' : 'Robô parado',
        ];
    }

    public function start(): array
    {
        if (config('robo.usar_docker_cli')) {
            return $this->execDockerCli('start');
        }

        $container = $this->encontrarContainer();
        if (! $container) {
            throw new Exception('Container não encontrado: '.$this->containerName);
        }

        $response = $this->request('POST', "/api/endpoints/{$this->endpointId}/docker/containers/{$container['Id']}/start");
        if ($response['status'] >= 400 && $response['status'] !== 304) {
            throw new Exception('Falha ao iniciar: HTTP '.$response['status'].' '.$response['body']);
        }

        return $this->status();
    }

    public function stop(): array
    {
        if (config('robo.usar_docker_cli')) {
            return $this->execDockerCli('stop');
        }

        $container = $this->encontrarContainer();
        if (! $container) {
            throw new Exception('Container não encontrado: '.$this->containerName);
        }

        $response = $this->request('POST', "/api/endpoints/{$this->endpointId}/docker/containers/{$container['Id']}/stop?t=10");
        if ($response['status'] >= 400 && $response['status'] !== 304) {
            throw new Exception('Falha ao parar: HTTP '.$response['status'].' '.$response['body']);
        }

        return $this->status();
    }

    public function logs(int $tail = 200): string
    {
        if (config('robo.usar_docker_cli')) {
            return $this->logsDockerCli($tail);
        }

        $container = $this->encontrarContainer();
        if (! $container) {
            return "Container não encontrado: {$this->containerName}\n";
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

    protected function encontrarContainer(): ?array
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
                if (trim($name, '/') === trim($this->containerName, '/')) {
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

    protected function statusDockerCli(): array
    {
        $nome = escapeshellarg($this->containerName);
        $estado = trim((string) shell_exec("docker inspect -f '{{.State.Status}}' {$nome} 2>/dev/null"));
        $running = $estado === 'running';

        return [
            'running' => $running,
            'status' => $estado !== '' ? $estado : 'unknown',
            'name' => $this->containerName,
            'message' => $running ? 'Robô em execução' : 'Robô parado',
        ];
    }

    protected function execDockerCli(string $acao): array
    {
        $nome = escapeshellarg($this->containerName);
        $acao = $acao === 'start' ? 'start' : 'stop';
        shell_exec("docker {$acao} {$nome} 2>&1");

        return $this->statusDockerCli();
    }

    protected function logsDockerCli(int $tail): string
    {
        $nome = escapeshellarg($this->containerName);
        $tail = (int) $tail;

        return (string) shell_exec("docker logs --tail {$tail} {$nome} 2>&1");
    }
}
