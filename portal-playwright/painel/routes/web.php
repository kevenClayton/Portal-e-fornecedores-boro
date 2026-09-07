<?php

use App\Http\Controllers\Admin\DashboardController;
use App\Http\Controllers\Admin\MotoristaController;
use App\Http\Controllers\Admin\ParametroController;
use App\Http\Controllers\Admin\RelatorioController;
use App\Http\Controllers\Admin\RoboController;
use App\Http\Controllers\Admin\RotaController;
use App\Http\Controllers\ProfileController;
use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return auth()->check()
        ? redirect()->route('admin.dashboard')
        : redirect()->route('login');
});

Route::middleware('auth')->group(function () {
    Route::get('/dashboard', DashboardController::class)->name('dashboard');
    Route::get('/admin', DashboardController::class)->name('admin.dashboard');

    Route::get('/admin/motoristas/gerenciar', [MotoristaController::class, 'gerenciar'])->name('admin.motoristas.gerenciar');
    Route::post('/admin/motoristas/reordenar', [MotoristaController::class, 'reordenar'])->name('admin.motoristas.reordenar');
    Route::resource('/admin/motoristas', MotoristaController::class)
        ->except(['show'])
        ->names('admin.motoristas')
        ->parameters(['motoristas' => 'motorista']);

    Route::get('/admin/parametros', [ParametroController::class, 'index'])->name('admin.parametros.index');
    Route::post('/admin/parametros/valores', [ParametroController::class, 'atualizarValores'])->name('admin.parametros.valores');
    Route::post('/admin/parametros/login', [ParametroController::class, 'atualizarLogin'])->name('admin.parametros.login');
    Route::post('/admin/parametros/origens', [ParametroController::class, 'storeOrigem'])->name('admin.parametros.origens.store');
    Route::delete('/admin/parametros/origens/{origem}', [ParametroController::class, 'destroyOrigem'])->name('admin.parametros.origens.destroy');
    Route::post('/admin/parametros/destinos', [ParametroController::class, 'storeDestino'])->name('admin.parametros.destinos.store');
    Route::delete('/admin/parametros/destinos/{destino}', [ParametroController::class, 'destroyDestino'])->name('admin.parametros.destinos.destroy');
    Route::post('/admin/parametros/tipos', [ParametroController::class, 'storeTipo'])->name('admin.parametros.tipos.store');
    Route::delete('/admin/parametros/tipos/{tipo}', [ParametroController::class, 'destroyTipo'])->name('admin.parametros.tipos.destroy');

    Route::get('/admin/rotas', [RotaController::class, 'index'])->name('admin.rotas.index');
    Route::get('/admin/relatorios', [RelatorioController::class, 'index'])->name('admin.relatorios.index');
    Route::get('/admin/relatorios/export', [RelatorioController::class, 'export'])->name('admin.relatorios.export');

    Route::get('/admin/robo', [RoboController::class, 'index'])->name('admin.robo.index');
    Route::get('/admin/robo/status', [RoboController::class, 'status'])->name('admin.robo.status');
    Route::post('/admin/robo/start', [RoboController::class, 'start'])->name('admin.robo.start');
    Route::post('/admin/robo/stop', [RoboController::class, 'stop'])->name('admin.robo.stop');
    Route::get('/admin/robo/logs', [RoboController::class, 'logs'])->name('admin.robo.logs');

    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
});

require __DIR__.'/auth.php';
