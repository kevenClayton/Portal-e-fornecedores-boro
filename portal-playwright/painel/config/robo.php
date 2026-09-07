<?php

return [
    'portainer_url' => rtrim((string) env('ROBO_PORTAINER_URL', ''), '/'),
    'portainer_api_key' => (string) env('ROBO_PORTAINER_API_KEY', ''),
    'portainer_endpoint_id' => (int) env('ROBO_PORTAINER_ENDPOINT_ID', 1),
    'container_name' => (string) env('ROBO_CONTAINER_NAME', 'portal-fornecedores'),
    'usar_docker_cli' => filter_var(env('ROBO_USAR_DOCKER_CLI', false), FILTER_VALIDATE_BOOLEAN),
];
