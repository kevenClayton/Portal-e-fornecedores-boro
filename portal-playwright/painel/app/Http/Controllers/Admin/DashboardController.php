<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\Motorista;
use App\Models\Rota;
use App\Services\RoboPortainerService;
use Illuminate\View\View;
use Throwable;

class DashboardController extends Controller
{
    public function __invoke(RoboPortainerService $robo): View
    {
        $statusRobo = [
            'running' => false,
            'status' => 'unknown',
            'message' => 'Status indisponível',
            'name' => config('robo.container_name'),
        ];

        try {
            $statusRobo = $robo->status();
        } catch (Throwable $erro) {
            $statusRobo['message'] = $erro->getMessage();
        }

        return view('admin.dashboard', [
            'statusRobo' => $statusRobo,
            'motoristasAtivos' => Motorista::query()->where('situacao', true)->count(),
            'motoristasTotal' => Motorista::query()->count(),
            'rotasHoje' => Rota::query()->whereDate('created_at', today())->count(),
            'rotasTotal' => Rota::query()->count(),
        ]);
    }
}
