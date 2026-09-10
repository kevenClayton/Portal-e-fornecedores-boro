<?php

return [
    /*
    | Mapa host → slug do cliente (branding na tela de login).
    | Domínio genérico (efornecedor) fica null = marca ReservaAI / E-Fornecedor.
    */
    'host_map' => [
        'madeforte.reservaai.com.br' => 'madeforte',
        'www.madeforte.reservaai.com.br' => 'madeforte',
        'efornecedor.reservaai.com.br' => null,
        'www.efornecedor.reservaai.com.br' => null,
    ],

    'marca_generica' => [
        'nome' => 'E-Fornecedor',
        'subtitulo' => 'Portal multi-cliente',
        'cor_primaria' => '#1e4d6b',
        'cor_accent' => '#163a52',
    ],
];
