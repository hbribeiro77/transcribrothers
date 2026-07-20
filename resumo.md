# Resumo — Transcribrothers

## O que é

Ferramenta web para transformar **vídeo ou áudio** (arquivo no computador do usuário) em documento útil: **só transcrição**, **tutorial em Markdown** (com timestamps e capturas), **notas de proposta** ou **reprodução de bug**, via **proxy LiteLLM**.

Uso típico: documentar fluxos em gravações de tela (treinamentos, tutoriais de sistema) sem montar o Markdown manualmente; ou obter só o texto da fala a partir de áudio/vídeo.

## Como funciona (visão geral)

1. O usuário escolhe **tipo de entrada** (vídeo ou áudio) e envia o arquivo (`POST /api/jobs/upload`, campo form `video` por compatibilidade); o arquivo fica no diretório do job (`TRANSCRIBROTHERS_DATA_DIR`). Pipelines/destinos são filtrados por `entradas_aceitas` no catálogo.
2. Preparação para STT: com **vídeo**, o **ffmpeg** extrai WAV; com **áudio**, normaliza/copia para `audio_extraido_para_transcricao.wav`.
3. **Transcrição** com segmentos e tempos:
   - **`openai_whisper`** — `POST /v1/audio/transcriptions` no mesmo proxy;
   - **`litellm_multimodal_audio`** — áudio inline no chat (`POST /v1/chat/completions`), em janelas paralelas com **checkpoint** em JSON para retomar trechos.
   - Formato inline: **WAV**, **MP3**, **Opus** ou **AAC (M4A)** (`TRANSCRICAO_MULTIMODAL_FORMATO_AUDIO_INLINE`). Janela, paralelismo, bitrate e mono podem vir do `.env` e ser **sobrescritos na UI** (gaveta Configurações → persistidos no SQLite).
4. **Capturas de tela** (dois modos, `tutorial_captura_frames_sob_demanda`, padrão `true` no servidor):
   - **Sob demanda (padrão):** gera um **rascunho** do tutorial sem imagens → extrai candidatos a timestamps do Markdown → o LiteLLM **planeja** quais momentos capturar → ffmpeg grava PNGs em `assets/` → segunda passagem incorpora imagens no tutorial.
   - **Legado:** captura frames nos instantes derivados dos **segmentos** da transcrição (amostragem por `MAX_FRAMES_PER_MINUTE` e teto opcional `TUTORIAL_MAX_FRAMES_TOTAL`).
5. O **tutorial** é gerado/regenerado no **mesmo proxy** (`LITELLM_API_KEY`, `LITELLM_ENDPOINT`, modelo da UI / `LITELLM_MODEL`; whitelist opcional `LITELLM_MODELOS_PROVISIONADOS`).
6. **Pós-geração (opcional no pipeline):** verificação de **sustentação** (tutorial vs transcrição) e de **imagens duplicadas** (visão em lotes); resultados em `steps_json`.
7. A UI exibe **player** do vídeo e **preview** do Markdown; exportação em **ZIP** (`tutorial.md` + `assets/`), Markdown com imagens embutidas (data-URI), **PDF** no navegador e GitLab (criar issue, comentar, anexar à descrição da issue ou publicar na wiki).

## Entrada de mídia

| Origem | Situação |
|--------|----------|
| **Upload local (vídeo)** | Stepper → tipo Vídeo; destinos tutorial / notas / bug / só transcrição. |
| **Upload local (áudio)** | Stepper → tipo Áudio; nesta versão só o destino **Só transcrição** (e customs derivadas desse molde). Extensões: wav, mp3, m4a, ogg, flac, aac, opus. |
| **Transcrição pronta** | Stepper → colar texto ou `.txt`/`.md`/`.srt`/`.vtt`; sem STT; destinos: só texto ou notas. |
| **Google Drive** | Suporte **legado** no pipeline (download por `file_id` se o job tiver `source_kind=drive`). Não há rota pública atual para criar job só com link do Drive na UI. |

## Stack

- **Backend:** FastAPI, SQLAlchemy async + SQLite (jobs, runtime de transcrição, histórico de versões do tutorial), httpx, SDK openai (Whisper no proxy), ffmpeg/ffprobe (subprocess).
- **Frontend:** Vite, React, TypeScript, react-markdown, Fabric.js (anotação de imagens), jspdf / html2canvas (export PDF).
- **Processamento:** tasks **asyncio** no mesmo processo do uvicorn (sem Redis/Celery).
- **CI:** GitHub Actions roda os testes do backend com Python 3.12 e instala `ffmpeg` no runner para cobrir fluxos que manipulam mídia/imagens.

**Ambiente (dev):** `backend/.env` (LiteLLM e app; copiar de `.env.example`) + opcional `env.local` na raiz (GitLab; copiar de `env.local.example`). Ordem de carga: `backend/.env` → `env.local` (último vence). Execução e API: [repositorio.md](repositorio.md).

## Funcionalidades além do fluxo inicial

- **Edição manual** do Markdown (`PATCH /api/jobs/{id}/result-markdown`) com histórico de versões.
- **Regenerar** o documento inteiro ou uma **seção `##`** (preview aplicar/descartar; pedido em linguagem natural para escopo da seção).
- **Revisão profunda** multifase (`revisao_profunda_multifase`): analista (plano por tópicos) → um passe por tópico → consolidação final.
- **Anotação de imagens** (PNG original + `.anotado.png`) e sincronização das referências no Markdown.
- **Captura manual de frame**, colar imagem da área de transferência, galeria de assets.
- **Exportação GitLab**: criar issue, comentar, anexar Markdown à descrição de issue existente ou publicar na wiki; imagens `assets/*.png` são enviadas ao GitLab e os links são reescritos para `/uploads/...`. Segredos em `env.local` na raiz (modelo em `env.local.example`) ou em `backend/.env`. Pastas wiki (`workshop`, etc.) são cadastradas em **Configurações → Wiki GitLab**; a modal de export usa um select (sem texto livre).
- **Projeto em branco** (`POST /api/jobs/projeto-em-branco`) e **staging RecBrothers** (`/api/staging/*`) para fluxos sem upload direto na UI principal.
- **Cancelar / retry** do job (retry pode reutilizar vídeo/áudio já no servidor).
- **Configurações** na UI: modelos LiteLLM, transcrição multimodal, prompts fixos (somente leitura via API), redundância entre seções na edição por seção.
- **Catálogo de pipelines** (`/pipelines/catalogo`): documentação dos fluxos do sistema (tutorial, notas, bug, **só transcrição**, regeneração, etc.) com prompts por etapa e `entradas_aceitas` (`video` / `audio`).
- **Pipelines e agentes custom (Fase 1 + biblioteca):** pipelines do sistema permanecem somente leitura. Pipelines custom **referenciam** agentes da biblioteca (obter-ou-criar a partir do sistema por `handler_chave`; sem clonar a cada pipeline). Editar um agente custom afeta todas as pipelines que o usam; jobs já iniciados seguem o snapshot. **Duplicar agente** cria variante isolada. No upload, o job grava `steps_json.pipeline_custom_agentes` (e metadados da pipeline). Cópias de fluxos 2 são editáveis na UI mas ainda não executáveis no upload. Sem autenticação: custom é global no servidor.
- **Minhas pipelines (Fase 2a):** no catálogo `/pipelines/catalogo`, seção **Minhas pipelines** separada das pipelines do sistema; botão **Nova pipeline** (molde tutorial/notas/bug/**só transcrição** + título); **arrastar** para reordenar (ordem persistida no SQLite e refletida no stepper de novo projeto e em «Gerar outro formato»). Metadados custom podem editar `entradas_aceitas` (áudio editável sobretudo no molde só transcrição nesta versão).
- **Só transcrição:** destino `so_transcricao` — após STT, `result_markdown` = texto da transcrição; não gera tutorial/notas/bug. Aceita vídeo ou áudio. Exige credenciais de **transcrição**, não de geração de documento.
- **Importar transcrição pronta:** no stepper, tipo **Transcrição pronta** (colar texto ou `.txt`/`.md`/`.srt`/`.vtt`) via `POST /api/jobs/importar-transcricao`. Grava o snapshot sem STT; destinos nesta fatia: manter só o texto ou gerar **notas** (sem mídia). Tutorial/bug exigem vídeo (fatia futura).
- **Passos internos (Fase 2b):** em pipelines custom, botão **Editar passos** — adicionar passo (referencia agente da biblioteca), remover passo (exclui agente só se ficar órfão), **arrastar** para reordenar passos dentro da pipeline.
- **Pipeline custom no job (Fase 2c):** upload e «Gerar outro formato» gravam `pipeline_custom_titulo`, `pipeline_custom_passos` e `pipeline_custom_agentes` no `steps_json`; o modal **Processando** mostra título e passos da custom; passos opcionais removidos (ex.: auditor, imagens duplicadas) **não executam** quando ausentes do snapshot.
- **Gerar outro formato (pós-transcrição):** em job **concluído** com snapshot de transcrição no disco, `POST /api/jobs/{id}/gerar-outro-formato` troca o destino (tutorial, notas ou bug) **sem novo upload nem retranscrição**. O `result_markdown` anterior vai para o **histórico de versões**; o documento ativo é substituído pelo novo pipeline. Na UI: botão «Gerar outro formato» na barra do documento quando elegível (`steps_json.pode_gerar_outro_formato` no `GET` do job). Jobs iniciados só com **áudio** só podem gerar **notas** nesta versão (tutorial/bug ainda exigem vídeo).

## Jornada do usuário (resumo)

1. Abrir a SPA (dev: `http://localhost:5183`).
2. Escolher modelo e, se necessário, ajustar Configurações.
3. **Iniciar transcrição** → vídeo, áudio ou **transcrição pronta** → destino filtrado → confirmar.
4. Acompanhar status (fases do pipeline, log de decisões da IA).
5. Revisar player + preview; editar, regenerar, anotar imagens, exportar.

Não há camada de **login/autenticação** implementada no repositório — tratar como ferramenta de rede/confiança interna até haver requisito explícito.

## Limitações e escopo atual

- Limite de tamanho do upload (`MAX_VIDEO_BYTES`) e extensões de vídeo/áudio permitidas; tutorial/notas/bug ainda exigem vídeo no upload (áudio só em «Só transcrição»).
- Requer **ffmpeg/ffprobe** no `PATH` do servidor.
- Dependência de **proxy LiteLLM** configurado (transcrição + tutorial + verificações).
- Jobs e arquivos ficam no disco local do servidor (`TRANSCRIBROTHERS_DATA_DIR`); não é um SaaS multi-tenant.

## Documentação relacionada

- [repositorio.md](repositorio.md) — checklist de primeira vez, `backend/.env`, `env.local`, comandos PowerShell, smoke test, testes, push.
- [README.md](README.md) — entrada rápida do repositório.
- [.env.example](.env.example) — referência de todas as variáveis do backend.
- [env.local.example](env.local.example) — template mínimo GitLab na raiz.
