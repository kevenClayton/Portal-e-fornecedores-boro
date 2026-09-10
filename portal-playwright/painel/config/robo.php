<?php

return [
    'portainer_url' => rtrim((string) env('ROBO_PORTAINER_URL', ''), '/'),
    'portainer_api_key' => (string) env('ROBO_PORTAINER_API_KEY', ''),
    'portainer_endpoint_id' => (int) env('ROBO_PORTAINER_ENDPOINT_ID', 1),
    'container_name' => (string) env('ROBO_CONTAINER_NAME', 'portal-fornecedores'),
    'container_names' => array_values(array_filter(array_map(
        'trim',
        explode(',', (string) env('ROBO_CONTAINER_NAMES', 'portal-fornecedores,portal-fornecedores-2,portal-fornecedores-3'))
    ))),
    'usar_docker_cli' => filter_var(env('ROBO_USAR_DOCKER_CLI', false), FILTER_VALIDATE_BOOLEAN),
];
