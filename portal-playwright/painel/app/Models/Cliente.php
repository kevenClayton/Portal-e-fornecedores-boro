<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Cliente extends Model
{
    protected $table = 'clientes';

    protected $guarded = [];

    protected function casts(): array
    {
        return [
            'max_robos' => 'integer',
            'ativo' => 'boolean',
        ];
    }

    /**
     * @return list<string>
     */
    public function listaContainers(): array
    {
        $raw = trim((string) ($this->containers ?? ''));
        if ($raw === '') {
            return [];
        }

        return array_values(array_filter(array_map('trim', explode(',', $raw))));
    }

    public function maxRobosEfetivo(): int
    {
        $disponiveis = count($this->listaContainers());
        $max = max(1, min(3, (int) ($this->max_robos ?: 1)));

        if ($disponiveis === 0) {
            return $max;
        }

        return max(1, min($max, $disponiveis));
    }

    public function users(): HasMany
    {
        return $this->hasMany(User::class, 'cliente_id');
    }

    public static function corSuave(string $hex): string
    {
        $hex = ltrim($hex, '#');
        if (strlen($hex) !== 6) {
            return '#d8f0ec';
        }

        $vermelho = hexdec(substr($hex, 0, 2));
        $verde = hexdec(substr($hex, 2, 2));
        $azul = hexdec(substr($hex, 4, 2));

        $mistura = static function (int $canal): int {
            return (int) round($canal + (255 - $canal) * 0.82);
        };

        return sprintf('#%02x%02x%02x', $mistura($vermelho), $mistura($verde), $mistura($azul));
    }
}
