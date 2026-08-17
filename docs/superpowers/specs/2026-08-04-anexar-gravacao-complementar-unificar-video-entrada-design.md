# Design: anexar gravação complementar e unificar `video_entrada`

Data: 2026-08-04  
Status: aprovado

## Problema

O vídeo de reunião/gravação às vezes fica incompleto. Hoje o job tem um único `video_entrada`; tutorial (`?t=`), frames e vídeo narrado dependem dessa timeline. Precisamos anexar um clip complementar, juntar num vídeo só e reprocessar o pipeline completo.

## Decisões confirmadas

- Concatenar num único arquivo (não manter dois vídeos lógicos).
- Após unificar: **retranscrever e regenerar o tutorial** (pipeline completo).
- UI: botão na coluna «Vídeo» do job.
- Arquivar clips originais em `clips_entrada_originais/` no work do job.
- Fora de escopo: concatenar 3+ numa tacada (repetir a ação); só-áudio; Drive.

## Design

### Backend

`POST /api/jobs/{job_id}/anexar-gravacao-complementar-video-entrada`  
Multipart: `video` (gravação complementar).

Pré-condições:
- Job `completed`, `failed` ou `cancelled`
- `tipo_entrada_midia !== audio`
- Existe `video_entrada_*` no disco
- Credenciais LiteLLM como no upload

Fluxo:
1. Gravar complemento e arquivar entrada atual em `clips_entrada_originais/`
2. ffmpeg: normalizar + concat → `video_entrada_arquivo_local.mp4`
3. Invalidar WAV, snapshot STT, caches regeneráveis; limpar chaves de transcrição/tutorial em `steps_json`
4. Atualizar duração/`saved_as`/`bytes_written`; `status=pending`
5. `agendar_pipeline_job_em_task_assincrona` (mesmo `destino_apos_transcricao`)

### Frontend

- Botão «Anexar gravação complementar» + `input type=file accept=video/*`
- Após sucesso: `setJob` + abrir modal de progresso
- Cache-bust do player (`key` / query na URL do vídeo)

### Testes

- Módulo ffmpeg com mock de `executar_ffmpeg_com_argumentos`
- API: patch work dir + agendamento; assert substituição e invalidação de snapshot
