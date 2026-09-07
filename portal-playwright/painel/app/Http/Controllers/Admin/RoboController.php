<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Services\RoboPortainerService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;
use Throwable;

class RoboController extends Controller
{
    public function __construct(protected RoboPortainerService $robo)
    {
    }

    public function index(): View
    {
        $status = $this->statusSeguro();
        $logs = '';
        try {
            $logs = $this->robo->logs(200);
        } catch (Throwable $erro) {
            $logs = $erro->getMessage();
        }

        return view('admin.robo.index', compact('status', 'logs'));
    }

    public function status(): JsonResponse
    {
        try {
            return response()->json(['ok' => true, 'data' => $this->robo->status()]);
        } catch (Throwable $erro) {
            return response()->json(['ok' => false, 'message' => $erro->getMessage()], 422);
        }
    }

    public function start(): RedirectResponse
    {
        try {
            $this->robo->start();

            return back()->with('success', 'Robô iniciado.');
        } catch (Throwable $erro) {
            return back()->with('error', $erro->getMessage());
        }
    }

    public function stop(): RedirectResponse
    {
        try {
            $this->robo->stop();

            return back()->with('success', 'Robô parado.');
        } catch (Throwable $erro) {
            return back()->with('error', $erro->getMessage());
        }
    }

    public function logs(Request $request): JsonResponse
    {
        $tail = max(50, min(1000, (int) $request->query('tail', 200)));

        try {
            return response()->json([
                'ok' => true,
                'logs' => $this->robo->logs($tail),
            ]);
        } catch (Throwable $erro) {
            return response()->json(['ok' => false, 'message' => $erro->getMessage()], 422);
        }
    }

    protected function statusSeguro(): array
    {
        try {
            return $this->robo->status();
        } catch (Throwable $erro) {
            return [
                'running' => false,
                'status' => 'error',
                'message' => $erro->getMessage(),
                'name' => config('robo.container_name'),
            ];
        }
    }
}
