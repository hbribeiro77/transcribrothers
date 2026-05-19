@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ============================================
echo  Transcribrothers - iniciando servidores
echo ============================================
echo.
echo Certifique-se de ter:
echo  - Python no PATH
echo  - Node.js ^(npm^) no PATH
echo  - ffmpeg no PATH
echo  - Arquivo .env na pasta backend ^(copie de .env.example^)
echo.

if not exist "backend\.venv\Scripts\python.exe" (
  echo [1/2] Criando venv e instalando dependencias do backend...
  pushd backend
  python -m venv .venv
  if errorlevel 1 (
    echo ERRO: falha ao criar venv. Verifique se o Python esta instalado.
    pause
    exit /b 1
  )
  call .venv\Scripts\activate.bat
  python -m pip install --upgrade pip
  pip install -e ".[dev]"
  if errorlevel 1 (
    echo ERRO: pip install falhou.
    popd
    pause
    exit /b 1
  )
  popd
  echo.
) else (
  echo [1/2] Backend: venv ja existe ^(pulando install^).
  echo.
)

if not exist "frontend\node_modules\" (
  echo Instalando dependencias do frontend ^(npm install^)...
  pushd frontend
  call npm install
  if errorlevel 1 (
    echo ERRO: npm install falhou.
    popd
    pause
    exit /b 1
  )
  popd
  echo.
)

echo Abrindo duas janelas:
echo   - Backend:  http://127.0.0.1:8000  ^(API + /docs^)
echo   - Frontend: http://localhost:5183
echo.
echo Feche cada janela para parar o respectivo servidor.
echo.

start "Transcribrothers-Backend-FastAPI" cmd /k pushd "%~dp0backend" ^& call .venv\Scripts\activate.bat ^& uvicorn transcribrothers_backend.main:app --reload --host 127.0.0.1 --port 8000

timeout /t 2 /nobreak >nul

start "Transcribrothers-Frontend-Vite" cmd /k pushd "%~dp0frontend" ^& npm run dev

echo Pronto. Voce pode fechar esta janela; os servidores ficam nas outras duas.
timeout /t 4 /nobreak >nul

endlocal
exit /b 0
