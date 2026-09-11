<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Support\Facades\Crypt;

class Cliente extends Model
{
    protected $connection = 'central';

    protected $table = 'clientes';

    protected $guarded = [];

    protected $hidden = [
        'db_password',
    ];

    protected function casts(): array
    {
        return [
            'max_robos' => 'integer',
            'ativo' => 'boolean',
            'db_port' => 'integer',
        ];
    }

    public function temBancoProprio(): bool
    {
        return filled($this->db_host)
            && filled($this->db_database)
            && filled($this->db_username);
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

    public function definirSenhaDb(?string $senhaPlain): void
    {
        if ($senhaPlain === null || $senhaPlain === '') {
            return;
        }

        $this->db_password = Crypt::encryptString($senhaPlain);
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
