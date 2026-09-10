<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (! Schema::hasTable('clientes')) {
            Schema::create('clientes', function (Blueprint $table) {
                $table->id();
                $table->string('nome', 120);
                $table->string('slug', 80)->unique();
                $table->string('cor_primaria', 7)->default('#0d7a6f');
                $table->string('cor_accent', 7)->default('#0a635a');
                $table->unsignedTinyInteger('max_robos')->default(1);
                $table->string('containers', 500)->nullable();
                $table->boolean('ativo')->default(true);
                $table->timestamps();
            });
        }

        if (DB::table('clientes')->where('id', 1)->doesntExist()) {
            DB::table('clientes')->insert([
                'id' => 1,
                'nome' => 'MadeForte',
                'slug' => 'madeforte',
                'cor_primaria' => '#0d7a6f',
                'cor_accent' => '#0a635a',
                'max_robos' => 2,
                'containers' => 'portal-fornecedores,portal-fornecedores-2,portal-fornecedores-3',
                'ativo' => true,
                'created_at' => now(),
                'updated_at' => now(),
            ]);
        }

        Schema::table('users', function (Blueprint $table) {
            if (! Schema::hasColumn('users', 'is_super_admin')) {
                $table->boolean('is_super_admin')->default(false)->after('password');
            }
            if (! Schema::hasColumn('users', 'cliente_id')) {
                $table->unsignedBigInteger('cliente_id')->nullable()->after('is_super_admin');
            }
        });

        $tabelas = [
            'parametros',
            'login',
            'motoristas',
            'origens',
            'destinos',
            'tipo_veiculo',
            'rotas',
            'relatorios',
            'notificacoes_carga',
            'robo_eventos',
            'robo_acompanhamento',
            'rotas_processadas',
        ];

        foreach ($tabelas as $tabela) {
            if (! Schema::hasTable($tabela)) {
                continue;
            }
            if (! Schema::hasColumn($tabela, 'cliente_id')) {
                Schema::table($tabela, function (Blueprint $table) {
                    $table->unsignedBigInteger('cliente_id')->nullable();
                });
            }
            DB::table($tabela)->whereNull('cliente_id')->update(['cliente_id' => 1]);
        }

        // rotas_processadas: chave composta (cliente_id, doc_transporte)
        if (Schema::hasTable('rotas_processadas')) {
            try {
                Schema::table('rotas_processadas', function (Blueprint $table) {
                    $table->dropPrimary();
                });
            } catch (\Throwable) {
                // já pode ser composta
            }

            try {
                Schema::table('rotas_processadas', function (Blueprint $table) {
                    $table->primary(['cliente_id', 'doc_transporte']);
                });
            } catch (\Throwable) {
                // índice já existe
            }
        }

        // Um acompanhamento por cliente
        if (Schema::hasTable('robo_acompanhamento') && Schema::hasColumn('robo_acompanhamento', 'cliente_id')) {
            try {
                DB::statement('ALTER TABLE robo_acompanhamento MODIFY id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT');
            } catch (\Throwable) {
                // já auto_increment
            }

            try {
                Schema::table('robo_acompanhamento', function (Blueprint $table) {
                    $table->unique('cliente_id', 'uq_robo_acompanhamento_cliente');
                });
            } catch (\Throwable) {
                // já existe
            }
        }
    }

    public function down(): void
    {
        // Irreversível com segurança em produção — mantém colunas.
    }
};
