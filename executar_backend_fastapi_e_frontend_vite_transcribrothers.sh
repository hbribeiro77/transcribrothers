#!/usr/bin/env bash
set -euo pipefail

# Resolve o diretório raiz do repositório (onde este script está)
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$RAIZ"

echo "============================================"
echo " Transcribrothers - iniciando servidores"
echo "============================================"
echo ""
echo "Certifique-se de ter:"
echo "  - Python 3.10+ no PATH"
echo "  - Node.js (npm) no PATH"
echo "  - ffmpeg no PATH"
echo "  - Arquivo backend/.env criado (copie de .env.example)"
echo ""

# ---------------------------------------------------------------------------
# Verificação de pré-requisitos
# ---------------------------------------------------------------------------
for cmd in python3 npm ffmpeg; do
    if ! command -v "$cmd" &>/dev/null; then
        echo "ERRO: '$cmd' não encontrado no PATH. Instale e tente novamente."
        exit 1
    fi
done

# ---------------------------------------------------------------------------
# Backend — venv + dependências
# ---------------------------------------------------------------------------
if [ ! -f "backend/.venv/bin/python" ]; then
    echo "[1/2] Criando venv e instalando dependências do backend..."
    cd backend
    python3 -m venv .venv
    .venv/bin/pip install --upgrade pip -q
    .venv/bin/pip install -e ".[dev]"
    cd "$RAIZ"
    echo ""
else
    echo "[1/2] Backend: venv já existe (pulando install)."
    echo ""
fi

# ---------------------------------------------------------------------------
# Frontend — node_modules
# ---------------------------------------------------------------------------
if [ ! -d "frontend/node_modules" ]; then
    echo "Instalando dependências do frontend (npm install)..."
    cd frontend
    npm install
    cd "$RAIZ"
    echo ""
fi

# ---------------------------------------------------------------------------
# PIDs para cleanup no Ctrl+C
# ---------------------------------------------------------------------------
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
    echo ""
    echo "Encerrando servidores..."
    [ -n "$BACKEND_PID" ]  && kill "$BACKEND_PID"  2>/dev/null || true
    [ -n "$FRONTEND_PID" ] && kill "$FRONTEND_PID" 2>/dev/null || true
    wait 2>/dev/null || true
    echo "Servidores encerrados."
    exit 0
}

trap cleanup INT TERM

# ---------------------------------------------------------------------------
# Sobe backend em background
# ---------------------------------------------------------------------------
echo "Iniciando backend  → http://127.0.0.1:8000  (API + /docs)"
cd backend
.venv/bin/uvicorn transcribrothers_backend.main:app \
    --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
cd "$RAIZ"

# Aguarda o backend subir antes de iniciar o frontend
sleep 2

# ---------------------------------------------------------------------------
# Sobe frontend em foreground (mantém o terminal ativo)
# ---------------------------------------------------------------------------
echo "Iniciando frontend → http://localhost:5183"
echo ""
echo "Pressione Ctrl+C para parar ambos os servidores."
echo ""

cd frontend
npm run dev &
FRONTEND_PID=$!
cd "$RAIZ"

# Aguarda ambos os processos
wait "$BACKEND_PID" "$FRONTEND_PID"
