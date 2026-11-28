#!/usr/bin/env python3
"""Abre a interface do CommandGenerator (GPSR) com os dados deste evento, numa porta que não é a 8080.

Uso (na raiz do repositório):
  uv run --no-project --with git+https://github.com/RoboCupAtHome/CommandGenerator python tools/gpsr_ui.py --ollama
  --ollama            reescreve os comandos com um modelo local (Ollama), sem chave e sem internet
  --ollama-model M    modelo do Ollama (padrão: qwen2.5:7b)
  --ui-port 8091      porta da interface
  --lan               permite acesso pela rede (tablet); sem isso só esta máquina acessa
  --senha S           (opcional) com --lan, exige usuário `arbitro` e a senha S
  Sem --ollama, valem as opções do gerador:  -u URL  -a CHAVE  -m MODELO
"""
import base64
import secrets
import shutil
import socket
import subprocess
import sys
import time
import types
import urllib.request
from pathlib import Path

import requests
from nicegui import app as web, ui
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

OLLAMA = "http://127.0.0.1:11434"
args = sys.argv[1:]


def take(flag, default=None):
    """Retira `flag valor` da linha de comando e devolve o valor."""
    if flag not in args:
        return default
    i = args.index(flag)
    value = args[i + 1]
    del args[i:i + 2]
    return value


def ollama_up():
    try:
        urllib.request.urlopen(OLLAMA + "/api/version", timeout=2)
        return True
    except OSError:
        return False


port = int(take("--ui-port", 8091))
# Só esta máquina por padrão: os comandos do GPSR são secretos para as equipes.
host = "127.0.0.1"
password = take("--senha")
if "--lan" in args:
    args.remove("--lan")
    host = "0.0.0.0"
model = take("--ollama-model", "qwen2.5:7b")
if "--ollama" in args:
    args.remove("--ollama")
    if not ollama_up():
        exe = shutil.which("ollama") or str(Path.home() / ".local/ollama/bin/ollama")
        log = open(Path.home() / ".local/ollama/serve.log", "a")
        subprocess.Popen([exe, "serve"], stdout=log, stderr=log, start_new_session=True)
        for _ in range(30):
            if ollama_up():
                break
            time.sleep(1)
        else:
            sys.exit("Não consegui iniciar o Ollama (veja ~/.local/ollama/serve.log).")

    # O gerador envia `reasoning_effort` quando há modelo; modelos sem "raciocínio" do Ollama recusam o pedido.
    def post(url, *a, **k):
        if isinstance(k.get("json"), dict):
            k["json"] = {key: v for key, v in k["json"].items() if key != "reasoning_effort"}
        return requests.post(url, *a, **k)

    import robocupathome_generator.llm as llm
    llm.requests = types.SimpleNamespace(post=post)
    args += ["-u", OLLAMA + "/v1/chat/completions", "-m", model, "-a", "ollama"]

if host != "127.0.0.1" and password:
    # Opcional (--senha): fora desta máquina o navegador pede usuário (arbitro) e senha.
    expected = "Basic " + base64.b64encode(f"arbitro:{password}".encode()).decode()

    class Auth(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            local = request.client and request.client.host == "127.0.0.1"
            if local or secrets.compare_digest(request.headers.get("authorization", ""), expected):
                return await call_next(request)
            return Response("Senha necessária", status_code=401, headers={"WWW-Authenticate": 'Basic realm="GPSR"'})

    web.add_middleware(Auth)

if host != "127.0.0.1":
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        try:
            s.connect(("10.255.255.255", 1))
            ip = s.getsockname()[0]
        except OSError:
            ip = "IP-DESTA-MAQUINA"
    login = f"\n  usuário: arbitro   senha: {password}" if password else ""
    print(f"\n  No tablet (mesma rede): http://{ip}:{port}{login}\n", flush=True)

_run = ui.run
ui.run = lambda *a, **k: _run(*a, **{**k, "host": host, "port": port, "reload": False})
sys.argv = ["athome-generator-gpsr-ui", "-d", str(Path(__file__).resolve().parent.parent / "command_generator"), *args]
import robocupathome_generator.ui.gpsr_ui as app  # noqa: E402  (a importação já inicia a interface)
if hasattr(app, "main"):
    app.main()
