# Repositório Transcribrothers

Guia para clonar, configurar e rodar o projeto em desenvolvimento (Windows/PowerShell). Resumo do produto: [resumo.md](resumo.md).

## Pré-requisitos

- **Python 3.10+** (recomendado 3.11+; CI usa 3.12)
- **Node.js 20+** (frontend Vite)
- **ffmpeg** e **ffprobe** no `PATH` do processo que roda o `uvicorn` (no Windows, instale o build oficial e inclua a pasta `bin` no PATH). O backend chama-os via `subprocess` num thread pool — evita `NotImplementedError` do `asyncio` com alguns loops no Windows.
- Acesso a um **proxy LiteLLM** (`LITELLM_ENDPOINT` + `LITELLM_API_KEY`) para transcrever mídia e gerar documentos (tutorial/notas/bug); destino **só transcrição** exige só credenciais de STT

O frontend **não** usa arquivo `.env`; só o backend lê variáveis de ambiente.

## Primeira vez (checklist)

1. Clonar o repositório e abrir a pasta na raiz do monorepo.
2. Criar **`backend/.env`**: copie [.env.example](.env.example) para `backend/.env` e preencha pelo menos **`LITELLM_API_KEY`** e **`LITELLM_ENDPOINT`** (ver [Configuração mínima](#configuração-mínima)).
3. (Opcional) Copiar [env.local.example](env.local.example) para **`env.local`** na **raiz** e preencher GitLab — ver [Dois arquivos de ambiente](#dois-arquivos-de-ambiente).
4. Confirmar **ffmpeg** no PATH (ou `FFMPEG_BIN_DIR` / `FFMPEG_PATH` no `backend/.env` — ver [ffmpeg no Windows](#ffmpeg-no-windows)).
5. Subir **backend** e **frontend** (dois terminais abaixo).
6. Abrir `http://localhost:5183` e validar [Smoke test](#smoke-test-após-subir).

Arquivos `backend/.env`, `env.local` e qualquer `.env` estão no `.gitignore` — **não commitar** tokens.

## Dois arquivos de ambiente

O backend carrega **todos os arquivos que existirem**, nesta ordem (em chave repetida, **o último vence**):

| Ordem | Arquivo | Uso típico |
|------|---------|------------|
| 1 | `.env` na raiz | Opcional; pode omitir |
| 2 | `backend/.env` | Config principal (LiteLLM, transcrição, limites, CORS, `TRANSCRIBROTHERS_DATA_DIR`) |
| 3 | `env.local` na raiz | Opcional; overrides locais (ex.: só `GITLAB_*`) |

Não é preciso duplicar variáveis nos dois arquivos. Exemplo comum:

- **`backend/.env`** — tudo que veio do `.env.example`, exceto token GitLab.
- **`env.local`** (raiz) — copie de [env.local.example](env.local.example); em geral só `GITLAB_BASE_URL`, `GITLAB_TOKEN` e, se for usar wiki, `GITLAB_WIKI_PROJECT_PATH`.

O [.env.example](.env.example) na raiz lista **todas** as variáveis suportadas (referência); copie para `backend/.env` e apague ou deixe vazio o que for só GitLab se preferir mantê-lo em `env.local`.

## Configuração mínima

Para a UI abrir e o pipeline **vídeo → tutorial** funcionar, em `backend/.env`:

```env
LITELLM_API_KEY=sua-chave
LITELLM_ENDPOINT=https://url-base-do-seu-proxy-litellm
```

Opcional mas recomendado: `LITELLM_MODEL`, `TRANSCRICAO_BACKEND`, `CORS_ORIGINS` (o padrão no código já inclui `http://localhost:5183`).

**GitLab** (criar issue, comentar, anexar na descrição, wiki na toolbar): só no servidor, em `env.local` na raiz ou em `backend/.env`:

```env
GITLAB_BASE_URL=https://gitlab.defensoria.../
GITLAB_TOKEN=glpat-...
# Wiki (opcional):
# GITLAB_WIKI_PROJECT_PATH=portal-da-defensoria/documentacao
```

Reinicie o `uvicorn` após alterar qualquer `.env` ou `env.local`.

### Referência rápida de variáveis

- **`LITELLM_API_KEY`** / **`LITELLM_ENDPOINT`**: obrigatórios para transcrição e tutorial. Transcrição multimodal: `POST …/v1/chat/completions`. Whisper (`TRANSCRICAO_BACKEND=openai_whisper`): `POST …/v1/audio/transcriptions` no **mesmo** endpoint.
- **`LITELLM_HTTP_VERIFY_SSL`** (padrão `true`) / **`LITELLM_SSL_CA_BUNDLE`**: certificado interno no proxy — use o PEM da CA; em teste isolado pode usar `LITELLM_HTTP_VERIFY_SSL=false` (evite em produção exposta).
- **`TRANSCRICAO_BACKEND`**: `openai_whisper` ou `litellm_multimodal_audio` (chat com áudio inline; configure **`TRANSCRICAO_LITELLM_MODELO`** ou um `gemini/` em `LITELLM_MODELOS_PROVISIONADOS`).
- **`OPENAI_API_KEY`**: opcional; alias da mesma chave do proxy — prefira só `LITELLM_*`.
- **`LITELLM_MODEL`** / **`LITELLM_MODELOS_PROVISIONADOS`**: modelo padrão e whitelist opcional na UI.
- **`REVISAO_PROFUNDA_MAX_TOPICOS`**: opcional (padrão **8**, clamp 1–32 no servidor).
- **Verificação de sustentação**: `VERIFICACAO_SUSTENTACAO_TUTORIAL_DESATIVADA=true` desliga; limites opcionais `VERIFICACAO_SUSTENTACAO_TUTORIAL_MAX_CHARS_*`.
- **`TRANSCRIBROTHERS_DATA_DIR`**: padrão `./data` relativo ao diretório de trabalho do `uvicorn` (em dev, com `cd backend`, vira `backend/data/`).
- Demais chaves: ver comentários em [.env.example](.env.example).

### ffmpeg no Windows

Se `GET /api/config/transcribrothers` retornar `ffmpeg_disponivel: false` mas o ffmpeg funciona no seu terminal, o processo do uvicorn pode não ver o mesmo `PATH`. Defina no `backend/.env`:

```env
FFMPEG_BIN_DIR=C:\caminho\para\pasta\bin
# ou
# FFMPEG_PATH=C:\...\ffmpeg.exe
# FFPROBE_PATH=C:\...\ffprobe.exe
```

Reinicie o backend.

## Executar em desenvolvimento (PowerShell)

### Terminal 1 — backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn transcribrothers_backend.main:app --reload --host 127.0.0.1 --port 8000
```

O carregamento de `backend/.env` e `env.local` (raiz) **não depende** do diretório atual após o pacote estar instalado — mas manter `cd backend` evita confusão com `TRANSCRIBROTHERS_DATA_DIR=./data`.

### Terminal 2 — frontend

```powershell
cd frontend
npm install
npm run dev
```

Abra **`http://localhost:5183`**. O Vite faz proxy de `/api` para `http://127.0.0.1:8000`.

### Smoke test (após subir)

1. **Health:** `http://127.0.0.1:8000/api/health` — deve retornar `status` e `pipeline_identificador`.
2. **Config:** `http://127.0.0.1:8000/api/config/transcribrothers` — confira `ffmpeg_disponivel` e `ffprobe_disponivel` em `true`; flags `gitlab_*_habilitado` só ficam úteis com token configurado.
3. Na UI: **Iniciar transcrição** → Vídeo, Áudio ou **Transcrição pronta** (colar/arquivo). Áudio e texto importado: «Só transcrição» ou notas (sem tutorial/bug nesta versão). Se faltar LiteLLM quando o destino gera documento, a API responde pedindo `LITELLM_API_KEY` e `LITELLM_ENDPOINT`.

Se um job falhar e `steps_json.pipeline_identificador` for diferente do health, o `uvicorn` em execução não é o código que você editou — reinicie o backend.

## Testes (backend)

Na primeira vez, crie o venv conforme o Terminal 1 acima. Depois:

```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest -q
```

O CI instala **ffmpeg** no runner; localmente os testes de mídia exigem ffmpeg no PATH.

## API (resumo)

- `GET /api/health` — diagnóstico e `pipeline_identificador`.
- `POST /api/jobs/upload` — `multipart/form-data`, campo `video` (vídeo ou áudio local); `destino_apos_transcricao` inclui `so_transcricao`; grava `steps_json.tipo_entrada_midia` (`video`|`audio`).
- `POST /api/jobs/importar-transcricao` — `multipart/form-data`: `texto` e/ou `arquivo` (`.txt`/`.md`/`.srt`/`.vtt`), `destino_apos_transcricao` (`so_transcricao` | `notas_proposta_funcionalidade`), opcional `pipeline_custom_id` (só molde notas). Sem STT; grava snapshot em disco.
- `GET /api/config/transcribrothers` — modelos, flags de verificação, disponibilidade ffmpeg/GitLab (sem expor segredos).
- `POST /api/jobs/{job_id}/regenerate-tutorial` — JSON opcional: `instrucoes_revisao_humana`, `litellm_model`, `revisao_profunda_multifase` (várias chamadas LiteLLM; teto `REVISAO_PROFUNDA_MAX_TOPICOS`).
- `POST /api/jobs/{job_id}/gerar-outro-formato` — JSON: `destino_apos_transcricao` (`gerar_tutorial` | `notas_proposta_funcionalidade` | `reproducao_bug`), opcional `pipeline_custom_id` e `litellm_model`. Job `completed` com snapshot; áudio-only ou transcrição importada sem mídia → só notas. Backup do markdown no histórico e reprocessa só o pós-transcrição.
- `PATCH /api/jobs/{job_id}/result-markdown` — edição manual + histórico de versões.
- `GET /api/jobs/{job_id}/tutorial-markdown/historico-versoes` e `…/historico-versoes/{historico_id}`.
- `GET /api/config/transcribrothers/prompts-fixos-revisao-profunda-e-verificacao-sustentacao-tutorial` — prompts fixos (somente leitura).
- **Catálogo e pipelines custom:**
  - `GET /api/pipelines/catalogo` — pipelines do sistema + custom (`origem`, `editavel`, `executavel`, `entradas_aceitas`, prompts com `chave`); inclui molde `pipeline_inicial_so_transcricao`.
  - `POST /api/pipelines/custom/duplicar` — body `{ "fonte_id": "…" }` (ID sistema ou custom; custom reutiliza os mesmos agentes; herda `entradas_aceitas`).
  - `POST /api/pipelines/custom/criar` — body `{ "fonte_id": "pipeline_inicial_…", "titulo"?, "descricao"? }` (moldes executáveis incl. só transcrição; agentes via biblioteca obter-ou-criar por handler).
  - `PATCH /api/pipelines/custom/{id}` — título, descrição e opcionalmente `entradas_aceitas` (`["video"]`, `["audio"]` ou ambos).
  - `PUT /api/pipelines/custom/ordem` — body `{ "pipeline_ids_ordenados": ["uuid", …] }` (lista completa de IDs custom na ordem desejada).
  - `PUT /api/pipelines/custom/{id}/passos/ordem` — body `{ "passo_ids_ordenados": ["preparacao", …] }` (todos os passos da pipeline custom).
  - `POST /api/pipelines/custom/{id}/passos` — body `{ "agente_fonte_id": "gerador_tutorial_markdown" | uuid custom, "rotulo"?, "descricao"? }` (referencia agente da biblioteca / obter-ou-criar; acrescenta ao fim).
  - `DELETE /api/pipelines/custom/{id}/passos/{passo_id}` — remove passo (mínimo 1); exclui agente custom só se nenhuma pipeline o referenciar.
  - `PATCH /api/pipelines/custom/{id}` / `DELETE /api/pipelines/custom/{id}` — só custom.
  - `POST /api/agentes/custom/duplicar` — body `{ "fonte_id": "…" }`.
  - `PATCH /api/agentes/custom/{id}` / `DELETE /api/agentes/custom/{id}` — prompts, modelo e metadados.
  - `POST /api/jobs/upload` — campo opcional `pipeline_custom_id` (somente fluxos iniciais executáveis); grava snapshot em `steps_json`.
- **GitLab** (requer `GITLAB_BASE_URL` + `GITLAB_TOKEN`):
  - `POST /api/gitlab/issues/create-in-project` — nova issue (`squad::bravo` por padrão).
  - `POST /api/gitlab/issues/comment-in-existing-issue` — comentário em issue existente.
  - `POST /api/gitlab/issues/append-to-existing-issue-description` — anexar Markdown à descrição da issue.
  - Rotas de wiki documentadas na UI; exigem `GITLAB_WIKI_PROJECT_PATH` (e prefixo `GITLAB_WIKI_SLUG_PREFIXO_PASTA`, padrão `workshop`).
  - `PATCH /api/config/transcribrothers/gitlab-wiki-pastas-runtime` — body `{ "pastas": ["workshop", …], "pasta_padrao"? }`; lista efetiva em `GET /api/config/transcribrothers` (`gitlab_wiki_pastas_disponiveis`).
  - `DELETE /api/config/transcribrothers/gitlab-wiki-pastas-runtime` — volta ao padrão do `.env`.
  - `GET /api/gitlab/wikis/validar-pasta-indice?pasta=workshop` — confere se a página índice existe no GitLab.

Com `job_id` e imagens, o servidor envia PNGs de `assets/` ao GitLab e reescreve `![](assets/…)` para `/uploads/…`.

### Job com erro — onde olhar

1. **`error_message`** do job (inclui traceback).
2. **`steps_json.pipeline_fase`** — última fase antes da falha.
3. **`steps_json.error_traceback`** — mesmo traceback (a UI pode exibir à parte).

## Push (!push)

1. `git status` / `git add` / `git commit`
2. `git push` para o remoto configurado (`git remote -v`).

Ajuste branch padrão e credenciais conforme a política da Defensoria.
