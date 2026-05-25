# Repositório Transcribrothers

## Pré-requisitos

- **Python 3.10+** (recomendado 3.11+ em produção)
- **Node.js 20+** (para o frontend Vite)
- **ffmpeg** e **ffprobe** no `PATH` (Windows: build oficial, pasta `bin` no PATH). O backend chama-os via `subprocess` num thread pool — evita `NotImplementedError` do `asyncio` com alguns loops no Windows.

## Variáveis de ambiente

Copie [.env.example](.env.example) para `backend/.env` (recomendado ao rodar o `uvicorn` a partir da pasta `backend`) ou exporte as variáveis no shell.

- **`LITELLM_API_KEY`** / **`LITELLM_ENDPOINT`**: credenciais do **proxy LiteLLM** (URL base do gateway). O tutorial e a transcrição multimodal usam apenas **`POST …/v1/chat/completions`** nesse endpoint. A transcrição **Whisper** (`TRANSCRICAO_BACKEND=openai_whisper`) usa o SDK de transcrições apontando para o **mesmo** `LITELLM_ENDPOINT` (rota `/v1/audio/transcriptions` precisa existir no proxy).
- **`LITELLM_HTTP_VERIFY_SSL`** (padrão `true`) / **`LITELLM_SSL_CA_BUNDLE`**: se o proxy usar HTTPS com certificado interno e o Python reclamar `CERTIFICATE_VERIFY_FAILED`, defina **`LITELLM_SSL_CA_BUNDLE`** com o caminho de um PEM da CA (recomendado). Só em ambiente de teste use **`LITELLM_HTTP_VERIFY_SSL=false`** para desativar a verificação TLS (não use em produção exposta).
- **`TRANSCRICAO_BACKEND`**: `openai_whisper` = áudio via **`/v1/audio/transcriptions`** no proxy. `litellm_multimodal_audio` = áudio WAV em base64 no chat (**`/v1/chat/completions`**) com **`TRANSCRICAO_LITELLM_MODELO`** (ex.: `gemini/gemini-3.1-flash-lite-preview`) ou primeiro `gemini/` da lista provisionada.
- `OPENAI_API_KEY` (opcional): **não** é “conta na OpenAI” neste projeto — só nome de variável alternativo se quiser guardar **a mesma** chave do proxy em outro campo; o fluxo recomendado é só `LITELLM_*`.
- `LITELLM_MODEL`: modelo padrão quando a UI não escolhe outro.
- `LITELLM_MODELOS_PROVISIONADOS`: opcional — lista separada por vírgula; se preenchida, só esses modelos são aceitos (whitelist no servidor + opções no select da UI).
- **`REVISAO_PROFUNDA_MAX_TOPICOS`** (opcional, default **8**): tecto de tópicos do plano do analista processados na regeneração com `revisao_profunda_multifase=true` (valor clamp 1–32 no servidor).
- **Verificação de sustentação do tutorial** (pós-geração): após o Markdown ser gerado (pipeline inicial ou regeneração), o servidor faz **uma chamada extra** ao LiteLLM com a transcrição (JSON) e o tutorial, e grava o resultado em `steps_json.verificacao_sustentacao_tutorial` (classificação `ok` / `atencao` / `risco` e lista curta de pontos). **`VERIFICACAO_SUSTENTACAO_TUTORIAL_DESATIVADA=true`** desliga a etapa. Opcional: **`VERIFICACAO_SUSTENTACAO_TUTORIAL_MAX_CHARS_PAYLOAD_TRANSCRICAO_JSON`** e **`VERIFICACAO_SUSTENTACAO_TUTORIAL_MAX_CHARS_MARKDOWN_ENVIADO`** (limites do texto enviado ao modelo).

## Executar em desenvolvimento (PowerShell)

Terminal 1 — backend (na raiz do repositório):

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn transcribrothers_backend.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2 — frontend:

```powershell
cd frontend
npm install
npm run dev
```

Abra `http://localhost:5183`. O frontend faz proxy de `/api` para o backend.

### API (resumo)

- `GET /api/health` — `status` e **`pipeline_identificador`** (string fixa do build). Se o job falhar e `steps_json.pipeline_identificador` for diferente do health, o backend em execução **não** é o mesmo código que você editou (reinicie o `uvicorn` / serviço).
- `POST /api/jobs/upload` — `multipart/form-data` com campo `video` (arquivo no PC).
- `GET /api/config/transcribrothers` — lista de modelos e padrão para a UI (sem expor segredos).
- `POST /api/jobs/{job_id}/regenerate-tutorial` — JSON opcional: `instrucoes_revisao_humana`, `litellm_model`, **`revisao_profunda_multifase`** (boolean, default `false`). Se `true`, o servidor corre **várias** chamadas ao LiteLLM em sequência: analista (plano JSON por tópicos), um passe por tópico (até **`REVISAO_PROFUNDA_MAX_TOPICOS`**, default 8, configurável no `.env`), e consolidação final com o mesmo fluxo multimodal da regeneração simples. Consome mais tempo e quota do modelo.
- `PATCH /api/jobs/{job_id}/result-markdown` — grava edição manual do tutorial (SQLite + arquivo `tutorial_gerado_transcribrothers.md`) e registra uma linha no histórico se o texto for novo em relação ao último snapshot.
- `GET /api/jobs/{job_id}/tutorial-markdown/historico-versoes` — lista compacta das versões guardadas (`id`, `criado_em`, `origem`, `tamanho_caracteres`, `preview_linha`).
- `GET /api/jobs/{job_id}/tutorial-markdown/historico-versoes/{historico_id}` — devolve `markdown`, `origem` e `criado_em` dessa versão.
- `GET /api/config/transcribrothers/prompts-fixos-revisao-profunda-e-verificacao-sustentacao-tutorial` — devolve os textos fixos (`system` / instruções) usados na revisão profunda e na verificação de sustentação do tutorial (somente leitura; alinhado a `pipeline_identificador` do health).
- `POST /api/gitlab/issues/create-in-project` — JSON `{ "title", "job_id", "incluir_imagens_png_markdown" }` (ou `description` sem imagens) cria issue no projeto `portal-da-defensoria/portal-defensoria-gateway` com label `squad::bravo`. Com `job_id` e imagens ativas, o servidor envia cada PNG de `assets/` via API de upload do GitLab e reescreve `![](assets/…)` para `/uploads/…` na descrição. Requer `GITLAB_BASE_URL` e `GITLAB_TOKEN` (ex.: `env.local` na raiz).

### Job com erro — onde olhar

1. Campo **`error_message`** do job: agora inclui o **traceback completo** (além do tipo da exceção).
2. **`steps_json.pipeline_fase`**: última fase alcançada antes da falha (ex.: `transcrevendo_audio`, `gerando_tutorial_http_chat_completions`).
3. **`steps_json.error_traceback`**: mesmo traceback (a UI pode exibir em bloco separado).

## Testes (backend)

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest -q
```

## Push (!push)

1. `git status` / `git add` / `git commit`
2. `git push` para o remoto configurado (`git remote -v`).

Ajuste branch padrão e credenciais conforme a política da Defensoria.
