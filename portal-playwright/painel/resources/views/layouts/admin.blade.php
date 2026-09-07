<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>@yield('title', 'Painel') — {{ config('app.name') }}</title>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
</head>
<body class="bg-paper text-ink min-h-screen">
@php
    $navGroups = [
        [
            'label' => 'Operação',
            'items' => [
                ['route' => 'admin.dashboard', 'match' => 'admin.dashboard', 'label' => 'Início', 'icon' => 'home'],
                ['route' => 'admin.robo.index', 'match' => 'admin.robo.*', 'label' => 'Robô', 'icon' => 'robot'],
            ],
        ],
        [
            'label' => 'Cadastros',
            'items' => [
                ['route' => 'admin.motoristas.index', 'match' => 'admin.motoristas.index|admin.motoristas.create|admin.motoristas.edit', 'label' => 'Motoristas', 'icon' => 'truck'],
                ['route' => 'admin.motoristas.gerenciar', 'match' => 'admin.motoristas.gerenciar', 'label' => 'Ordem da fila', 'icon' => 'list'],
                ['route' => 'admin.parametros.index', 'match' => 'admin.parametros.*', 'label' => 'Parâmetros', 'icon' => 'settings'],
            ],
        ],
        [
            'label' => 'Acompanhamento',
            'items' => [
                ['route' => 'admin.rotas.index', 'match' => 'admin.rotas.*', 'label' => 'Rotas vinculadas', 'icon' => 'check'],
                ['route' => 'admin.relatorios.index', 'match' => 'admin.relatorios.*', 'label' => 'Relatórios', 'icon' => 'file'],
            ],
        ],
    ];

    $iconSvg = function (string $name): string {
        return match ($name) {
            'home' => '<path stroke-linecap="round" stroke-linejoin="round" d="M3 10.5 12 3l9 7.5V21a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1v-10.5Z"/>',
            'robot' => '<path stroke-linecap="round" stroke-linejoin="round" d="M12 3v3m-6 4h12a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2Zm3 5h.01M15 15h.01"/>',
            'truck' => '<path stroke-linecap="round" stroke-linejoin="round" d="M3 7h11v10H3V7Zm11 3h4l3 3v4h-7v-7ZM7 19a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Zm10 0a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z"/>',
            'list' => '<path stroke-linecap="round" stroke-linejoin="round" d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
            'settings' => '<path stroke-linecap="round" stroke-linejoin="round" d="M12 15.5a3.5 3.5 0 1 0 0-7 3.5 3.5 0 0 0 0 7Zm7.4-3.5.5-1.2-1.7-1.5.2-1.9-1.9-.5-1-1.7-1.9.3L12 3l-1.1 1.5-1.9-.3-1 1.7-1.9.5.2 1.9-1.7 1.5.5 1.2-.5 1.2 1.7 1.5-.2 1.9 1.9.5 1 1.7 1.9-.3L12 21l1.1-1.5 1.9.3 1-1.7 1.9-.5-.2-1.9 1.7-1.5-.5-1.2Z"/>',
            'check' => '<path stroke-linecap="round" stroke-linejoin="round" d="M9 12.5 11 14.5 15.5 10M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z"/>',
            'file' => '<path stroke-linecap="round" stroke-linejoin="round" d="M8 3h6l4 4v14a1 1 0 0 1-1 1H8a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1Zm6 0v4h4"/>',
            default => '',
        };
    };
@endphp

<div class="min-h-screen md:flex">
    {{-- Desktop sidebar --}}
    <aside class="hidden md:flex md:w-72 md:flex-col bg-ink text-white relative overflow-hidden">
        <div class="absolute inset-0 opacity-40 pointer-events-none"
             style="background:
                radial-gradient(circle at 20% 10%, rgba(13,122,111,.45), transparent 40%),
                radial-gradient(circle at 90% 80%, rgba(36,54,66,.8), transparent 35%);"></div>

        <div class="relative px-5 py-6 border-b border-white/10">
            <div class="flex items-center gap-3">
                <div class="h-11 w-11 rounded-2xl bg-brand flex items-center justify-center shadow-soft">
                    <svg class="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M3 7h11v10H3V7Zm11 3h4l3 3v4h-7v-7Z"/>
                    </svg>
                </div>
                <div>
                    <div class="font-display text-xl leading-none">MadeForte</div>
                    <div class="text-xs text-slate-300 mt-1">Painel do robô</div>
                </div>
            </div>
        </div>

        <nav class="relative flex-1 px-3 py-5 space-y-5 overflow-y-auto">
            @foreach ($navGroups as $group)
                <div>
                    <div class="px-3 mb-2 text-[11px] font-bold uppercase tracking-[0.14em] text-slate-400">{{ $group['label'] }}</div>
                    <div class="space-y-1">
                        @foreach ($group['items'] as $item)
                            @php $ativo = request()->routeIs(...explode('|', $item['match'])); @endphp
                            <a href="{{ route($item['route']) }}" class="{{ $ativo ? 'nav-link-active' : 'nav-link-idle' }}">
                                <svg class="h-5 w-5 opacity-90" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">{!! $iconSvg($item['icon']) !!}</svg>
                                <span>{{ $item['label'] }}</span>
                            </a>
                        @endforeach
                    </div>
                </div>
            @endforeach
        </nav>

        <div class="relative px-4 py-4 border-t border-white/10">
            <div class="rounded-2xl bg-white/5 px-3 py-3">
                <div class="text-sm font-semibold truncate">{{ auth()->user()->name }}</div>
                <div class="text-xs text-slate-400 truncate">{{ auth()->user()->email }}</div>
                <form method="POST" action="{{ route('logout') }}" class="mt-3">
                    @csrf
                    <button type="submit" class="btn-ghost !text-slate-300 hover:!text-white hover:!bg-white/10 w-full !justify-start !px-2">Sair da conta</button>
                </form>
            </div>
        </div>
    </aside>

    {{-- Mobile top bar + drawer --}}
    <div class="flex-1 min-w-0 flex flex-col min-h-screen">
        <header class="md:hidden sticky top-0 z-30 border-b border-line bg-white/90 backdrop-blur">
            <div class="px-4 py-3 flex items-center justify-between gap-3">
                <button type="button" id="menu-open" class="btn-secondary !px-3" aria-label="Abrir menu">
                    <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" d="M4 7h16M4 12h16M4 17h16"/></svg>
                </button>
                <div class="font-display text-lg">MadeForte</div>
                <form method="POST" action="{{ route('logout') }}">@csrf<button class="text-sm font-semibold text-brand">Sair</button></form>
            </div>
        </header>

        <div id="mobile-drawer" class="fixed inset-0 z-40 hidden">
            <div id="menu-backdrop" class="absolute inset-0 bg-ink/50"></div>
            <aside class="absolute left-0 top-0 h-full w-72 bg-ink text-white p-4 overflow-y-auto">
                <div class="flex items-center justify-between mb-6">
                    <div class="font-display text-xl">Menu</div>
                    <button type="button" id="menu-close" class="btn-ghost !text-white">Fechar</button>
                </div>
                @foreach ($navGroups as $group)
                    <div class="mb-5">
                        <div class="px-2 mb-2 text-[11px] font-bold uppercase tracking-[0.14em] text-slate-400">{{ $group['label'] }}</div>
                        <div class="space-y-1">
                            @foreach ($group['items'] as $item)
                                @php $ativo = request()->routeIs(...explode('|', $item['match'])); @endphp
                                <a href="{{ route($item['route']) }}" class="{{ $ativo ? 'nav-link-active' : 'nav-link-idle' }}">
                                    <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.8">{!! $iconSvg($item['icon']) !!}</svg>
                                    {{ $item['label'] }}
                                </a>
                            @endforeach
                        </div>
                    </div>
                @endforeach
            </aside>
        </div>

        <main class="flex-1 p-4 md:p-8">
            <div class="max-w-7xl mx-auto">
                @if (session('success'))
                    <div class="flash-ok">{{ session('success') }}</div>
                @endif
                @if (session('error'))
                    <div class="flash-error">{{ session('error') }}</div>
                @endif
                @if ($errors->any())
                    <div class="flash-error">
                        <ul class="list-disc pl-4 space-y-1">
                            @foreach ($errors->all() as $erro)
                                <li>{{ $erro }}</li>
                            @endforeach
                        </ul>
                    </div>
                @endif

                @yield('content')
            </div>
        </main>
    </div>
</div>

<script>
    const drawer = document.getElementById('mobile-drawer');
    const openBtn = document.getElementById('menu-open');
    const closeBtn = document.getElementById('menu-close');
    const backdrop = document.getElementById('menu-backdrop');
    const open = () => drawer?.classList.remove('hidden');
    const close = () => drawer?.classList.add('hidden');
    openBtn?.addEventListener('click', open);
    closeBtn?.addEventListener('click', close);
    backdrop?.addEventListener('click', close);
</script>
</body>
</html>
