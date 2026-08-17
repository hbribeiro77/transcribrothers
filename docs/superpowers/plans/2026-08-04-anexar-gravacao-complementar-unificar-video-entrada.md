# Anexar gravação complementar — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Permitir anexar um vídeo complementar ao job, unificar num único `video_entrada` e reexecutar o pipeline completo (STT + tutorial).

**Architecture:** Novo módulo ffmpeg (normaliza + concat), orquestração que arquiva clips e invalida artefatos derivados, endpoint FastAPI e botão na coluna Vídeo do frontend.

**Tech Stack:** FastAPI, ffmpeg via helpers existentes, React/TS, pytest + TestClient, Vitest se houver teste FE mínimo.

## Global Constraints

- Nomes de arquivo descritivos longos (padrão Transcribrothers).
- UI e mensagens em pt-BR.
- Não commitar sem pedido explícito do usuário.
- Sempre reencode na unificação (codecs/resoluções heterogêneos).

---

### Task 1: Módulo ffmpeg concat + testes

**Files:**
- Create: `backend/transcribrothers_backend/modulo_ffmpeg_concatenar_dois_videos_entrada_normalizados_transcribrothers.py`
- Test: `backend/tests/test_modulo_ffmpeg_concatenar_dois_videos_entrada_normalizados_transcribrothers.py`

**Interfaces:**
- Produces: `async def concatenar_dois_videos_entrada_normalizados_via_ffmpeg_transcribrothers(*, caminho_video_a: Path, caminho_video_b: Path, caminho_saida: Path) -> Path`

- [x] Teste com mock de `executar_ffmpeg_com_argumentos` e assert args/saída
- [x] Implementar concat com filter_complex (1080p@30, H.264/AAC)
- [x] Rodar pytest do módulo

### Task 2: Orquestração no work do job + invalidação

**Files:**
- Create: `backend/transcribrothers_backend/modulo_anexar_gravacao_complementar_unificar_video_entrada_e_reprocessar_job_transcribrothers.py`
- Test: `backend/tests/test_modulo_anexar_gravacao_complementar_unificar_video_entrada_e_reprocessar_job_transcribrothers.py`

**Interfaces:**
- Consumes: concat ffmpeg, `limpar_cache_regeneravel_job_transcribrothers`, localizar vídeo
- Produces: `preparar_work_e_steps_apos_anexar_gravacao_complementar_transcribrothers(...)` e helpers de invalidação

- [x] Testes de arquivamento, remoção de WAV/snapshot, steps limpos
- [x] Implementar
- [x] Rodar pytest

### Task 3: Endpoint API

**Files:**
- Modify: `backend/transcribrothers_backend/main.py`
- Test: `backend/tests/test_api_anexar_gravacao_complementar_video_entrada_job_transcribrothers.py`

- [x] Teste 200 + agenda pipeline; 400 se job em execução / sem vídeo
- [x] Endpoint `POST .../anexar-gravacao-complementar-video-entrada`
- [x] Rodar pytest da API

### Task 4: Frontend

**Files:**
- Create: `frontend/src/modulo_api_anexar_gravacao_complementar_video_entrada_job_transcribrothers.ts`
- Modify: `frontend/src/componente_pagina_principal_formulario_drive_preview_tutorial.tsx`
- Modify: `frontend/src/componente_pagina_principal_formulario_drive_preview_tutorial.css`

- [x] API client multipart
- [x] Botão + file input na coluna Vídeo; abrir modal progresso; cache-bust player
