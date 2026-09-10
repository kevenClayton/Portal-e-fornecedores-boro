<?php

namespace App\Console\Commands;

use App\Models\Cliente;
use App\Models\Parametro;
use App\Models\RoboAcompanhamento;
use App\Services\RoboPortainerService;
use App\Support\Tenant;
use Carbon\Carbon;
use Illuminate\Console\Command;
use Throwable;

class RoboAplicarAgendaCommand extends Command
{
    protected $signature = 'robo:aplicar-agenda';

    protected $description = 'Liga ou desliga os containers do robô conforme a agenda de cada cliente';

    public function handle(RoboPortainerService $robo): int
    {
        $clientes = Cliente::query()->where('ativo', true)->orderBy('id')->get();
        if ($clientes->isEmpty()) {
            $this->line('Nenhum cliente ativo.');

            return self::SUCCESS;
        }

        $falhas = 0;
        foreach ($clientes as $cliente) {
            Tenant::set((int) $cliente->id);
            try {
                $resultado = $this->aplicarParaCliente($robo, $cliente);
                $this->line("[{$cliente->slug}] {$resultado}");
            } catch (Throwable $erro) {
                $falhas++;
                $this->error("[{$cliente->slug}] ".$erro->getMessage());
            }
        }

        Tenant::clear();

        return $falhas > 0 ? self::FAILURE : self::SUCCESS;
    }

    protected function aplicarParaCliente(RoboPortainerService $robo, Cliente $cliente): string
    {
        $parametro = Parametro::query()->orderBy('id')->first();
        if (! $parametro || ! $parametro->robo_agenda_ativa) {
            return 'Agenda inativa — nada a fazer.';
        }

        $containers = $cliente->listaContainers();
        if ($containers === []) {
            return 'Sem containers configurados — agenda ignorada.';
        }

        $robo->definirContainers($containers);
        $maxRobos = $cliente->maxRobosEfetivo();
        $quantidade = max(1, min($maxRobos, (int) ($parametro->robo_quantidade ?? 1)));
        $horaLigar = $this->normalizarHora($parametro->robo_hora_ligar) ?? '06:00';
        $horaDesligar = $this->normalizarHora($parametro->robo_hora_desligar) ?? '22:00';

        if ($horaLigar === $horaDesligar) {
            return 'Hora de ligar e desligar iguais — agenda ignorada.';
        }

        $agora = Carbon::now(config('app.timezone'));
        $deveEstarLigado = $this->estaNaJanela($agora, $horaLigar, $horaDesligar);

        $status = $robo->status($quantidade);
        $estaLigado = (int) ($status['running_count'] ?? 0) > 0;
        $quantidadeLigada = (int) ($status['running_count'] ?? 0);

        if ($deveEstarLigado && $quantidadeLigada !== $quantidade) {
            $robo->start($quantidade);
            $this->gravarAcompanhamento('info', "Frota {$quantidade} ligada pela agenda ({$horaLigar}–{$horaDesligar})");

            return "Frota {$quantidade} ligada pela agenda ({$horaLigar}–{$horaDesligar}).";
        }

        if (! $deveEstarLigado && $estaLigado) {
            $robo->stop();
            $this->gravarAcompanhamento('parado', "Frota parada pela agenda ({$horaLigar}–{$horaDesligar})");

            return "Frota parada pela agenda ({$horaLigar}–{$horaDesligar}).";
        }

        return $deveEstarLigado
            ? "Dentro da janela — frota {$quantidade} ok ({$quantidadeLigada} ligados)."
            : 'Fora da janela — já parado.';
    }

    protected function gravarAcompanhamento(string $etapa, string $mensagem): void
    {
        $registro = RoboAcompanhamento::query()->orderBy('id')->first();
        if ($registro) {
            $registro->update(['etapa' => $etapa, 'mensagem' => $mensagem]);

            return;
        }

        RoboAcompanhamento::query()->create([
            'etapa' => $etapa,
            'mensagem' => $mensagem,
        ]);
    }

    protected function estaNaJanela(Carbon $agora, string $horaLigar, string $horaDesligar): bool
    {
        $minutosAgora = ((int) $agora->format('H')) * 60 + (int) $agora->format('i');
        $minutosLigar = $this->horaParaMinutos($horaLigar);
        $minutosDesligar = $this->horaParaMinutos($horaDesligar);

        if ($minutosLigar < $minutosDesligar) {
            return $minutosAgora >= $minutosLigar && $minutosAgora < $minutosDesligar;
        }

        return $minutosAgora >= $minutosLigar || $minutosAgora < $minutosDesligar;
    }

    protected function horaParaMinutos(string $hora): int
    {
        [$horas, $minutos] = array_pad(explode(':', $hora), 2, '0');

        return ((int) $horas) * 60 + (int) $minutos;
    }

    protected function normalizarHora(mixed $valor): ?string
    {
        if ($valor === null || $valor === '') {
            return null;
        }

        $texto = trim((string) $valor);
        if (preg_match('/^(\d{1,2}):(\d{2})(?::\d{2})?$/', $texto, $match)) {
            return sprintf('%02d:%02d', (int) $match[1], (int) $match[2]);
        }

        return null;
    }
}
