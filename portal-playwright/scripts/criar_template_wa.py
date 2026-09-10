import os
import json
import urllib.request
import urllib.error

token = (os.environ.get("WHATSAPP_API_TOKEN") or "").strip().strip("'")
base = (os.environ.get("WHATSAPP_API_URL") or "https://api.reservaai.com.br/api").rstrip("/")
url = f"{base}/whatsapp/externo/templates/carga-aceita"
print("POST", url)
print("token_len", len(token))

payloads = [
  {},
  {"codigo_estabelecimento": 9},
]

for payload in payloads:
  corpo = json.dumps(payload).encode()
  request = urllib.request.Request(
    url,
    data=corpo,
    method="POST",
    headers={
      "Content-Type": "application/json",
      "Accept": "application/json",
      "Authorization": f"Bearer {token}",
    },
  )
  print("--- payload:", payload)
  try:
    with urllib.request.urlopen(request, timeout=60) as resposta:
      print("OK", resposta.status, resposta.read().decode())
  except urllib.error.HTTPError as erro:
    print("HTTP", erro.code, erro.read().decode())
  except Exception as erro:
    print("ERR", erro)
