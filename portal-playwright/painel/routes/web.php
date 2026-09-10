<?php

use App\Http\Controllers\Admin\ClienteController;
use App\Http\Controllers\Admin\DashboardController;
use App\Http\Controllers\Admin\MotoristaController;
use App\Http\Controllers\Admin\ParametroController;
use App\Http\Controllers\Admin\RelatorioController;
use App\Http\Controllers\Admin\RoboController;
use App\Http\Controllers\Admin\RotaController;
use App\Http\Controllers\Admin\UsuarioController;
use App\Http\Controllers\CargaPublicaController;
use App\Http\Controllers\ProfileController;
use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return auth()->check()
        ? redirect()->route('admin.dashboard')
        : redirect()->route('login');
});

// Healthcheck do container — sem banco, para o watchdog não travar
Route::get('/healthz', function () {
    return response('ok', 200)->header('Content-Type', 'text/plain');
});

Route::get('/carga/{publicId}', [CargaPublicaController::class, 'show'])
    ->where('publicId', '[0-9a-fA-F-]{36}')
    ->name('carga.publica');

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
    Route::get('/admin/robo/acompanhamento', [RoboController::class, 'acompanhamento'])->name('admin.robo.acompanhamento');
    Route::post('/admin/robo/screenshot/pedir', [RoboController::class, 'pedirScreenshot'])->name('admin.robo.screenshot.pedir');
    Route::get('/admin/robo/screenshot', [RoboController::class, 'screenshot'])->name('admin.robo.screenshot');
    Route::post('/admin/robo/start', [RoboController::class, 'start'])->name('admin.robo.start');
    Route::post('/admin/robo/stop', [RoboController::class, 'stop'])->name('admin.robo.stop');
    Route::post('/admin/robo/agenda', [RoboController::class, 'salvarAgenda'])->name('admin.robo.agenda');
    Route::get('/admin/robo/logs', [RoboController::class, 'logs'])->name('admin.robo.logs');

    Route::middleware('super_admin')->group(function () {
        Route::get('/admin/clientes', [ClienteController::class, 'index'])->name('admin.clientes.index');
        Route::get('/admin/clientes/criar', [ClienteController::class, 'create'])->name('admin.clientes.create');
        Route::post('/admin/clientes', [ClienteController::class, 'store'])->name('admin.clientes.store');
        Route::get('/admin/clientes/{cliente}/editar', [ClienteController::class, 'edit'])->name('admin.clientes.edit');
        Route::put('/admin/clientes/{cliente}', [ClienteController::class, 'update'])->name('admin.clientes.update');
        Route::post('/admin/clientes/{cliente}/selecionar', [ClienteController::class, 'selecionar'])->name('admin.clientes.selecionar');

        Route::get('/admin/usuarios', [UsuarioController::class, 'index'])->name('admin.usuarios.index');
        Route::get('/admin/usuarios/criar', [UsuarioController::class, 'create'])->name('admin.usuarios.create');
        Route::post('/admin/usuarios', [UsuarioController::class, 'store'])->name('admin.usuarios.store');
        Route::get('/admin/usuarios/{usuario}/editar', [UsuarioController::class, 'edit'])->name('admin.usuarios.edit');
        Route::put('/admin/usuarios/{usuario}', [UsuarioController::class, 'update'])->name('admin.usuarios.update');
    });

    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
});

require __DIR__.'/auth.php';
