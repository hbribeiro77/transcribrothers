# Chat Ask e Agente no documento do job — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Trocar o FAB de regeneração por um chat dockado com modos Ask (conversa sobre Markdown + transcrição, sem gravar) e Agente (pipelines atuais + prévia).

**Architecture:** Módulos de histórico, contexto e imagem no backend; `GET/POST` no job; LiteLLM via `litellm_chat_completions_texto_simples_transcribrothers` com JSON parseado. O frontend extrai o painel, encaixa à direita do `tb-grid-preview` e só reusa os callbacks de `regenerate-*`.

**Tech Stack:** FastAPI, pytest, React/TypeScript, CSS do preview, Vitest nos helpers de UI, LiteLLM chat completions já existente.

**Spec:** `docs/superpowers/specs/2026-10-03-chat-ask-e-agente-documento-job-transcribrothers-design.md`

## Global Constraints

- Nomes de arquivo longos e descritivos (padrão Transcribrothers).
- UI, toasts e mensagens de erro em pt-BR.
- Não commitar a menos que o usuário peça explicitamente (ignorar passos de commit deste plano).
- Ask nunca altera `result_markdown` nem agenda `generating_tutorial`.
- Agente não fecha o painel; prévia continua na modal atual.
- Teto de 40 mensagens no JSON do job; frame da galeria se `|Δt| <= 5,0` s.
- Windows PowerShell: encadear com `;`, não `&&`.

## File map

**Create (backend):**
- `backend/transcribrothers_backend/modulo_persistencia_historico_chat_ask_agente_documento_job_transcribrothers.py`
- `backend/transcribrothers_backend/modulo_montar_contexto_chat_ask_markdown_transcricao_e_catalogo_frames_transcribrothers.py`
- `backend/transcribrothers_backend/modulo_parsear_resposta_json_chat_ask_litellm_transcribrothers.py`
- `backend/transcribrothers_backend/modulo_orquestrar_turno_chat_ask_job_transcribrothers.py`
- `backend/transcribrothers_backend/modulo_resolver_imagem_chat_ask_galeria_ou_captura_frame_transcribrothers.py`
- `backend/tests/test_modulo_persistencia_historico_chat_ask_agente_documento_job_transcribrothers.py`
- `backend/tests/test_modulo_montar_contexto_chat_ask_markdown_transcricao_e_catalogo_frames_transcribrothers.py`
- `backend/tests/test_modulo_parsear_resposta_json_chat_ask_litellm_transcribrothers.py`
- `backend/tests/test_modulo_resolver_imagem_chat_ask_galeria_ou_captura_frame_transcribrothers.py`
- `backend/tests/test_api_chat_ask_e_historico_documento_job_transcribrothers.py`

**Create (frontend):**
- `frontend/src/modulo_util_job_pode_abrir_chat_ask_agente_documento_transcribrothers.ts`
- `frontend/src/modulo_util_job_pode_abrir_chat_ask_agente_documento_transcribrothers.test.ts`
- `frontend/src/modulo_tipos_item_historico_chat_ask_agente_documento_job_transcribrothers.ts`
- `frontend/src/modulo_api_chat_ask_e_historico_documento_job_transcribrothers.ts`
- `frontend/src/componente_painel_chat_ask_agente_documento_job_transcribrothers.tsx`

**Modify:**
- `backend/transcribrothers_backend/main.py` — rotas GET/POST
- `frontend/src/componente_pagina_principal_formulario_drive_preview_tutorial.tsx` — dock, não fechar no Enviar, visibilidade
- `frontend/src/componente_pagina_principal_formulario_drive_preview_tutorial.css` — dock sem backdrop

**Reuse (não reescrever):**
- `litellm_chat_completions_texto_simples_transcribrothers`
- `extrair_primeiro_objeto_json_de_texto_llm_transcribrothers`
- `carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers`
- `capturar_frame_manual_video_tutorial_para_assets_do_job_transcribrothers` + `mesclar_registro_frame_manual_capturado_no_steps_json_transcribrothers`
- `listar_secoes_markdown_nivel2_tutorial_transcribrothers`
- rotas `regenerate-tutorial` / seção / notas / bug

---

### Task 1: Persistência do histórico no disco do job

**Files:**
- Create: `backend/transcribrothers_backend/modulo_persistencia_historico_chat_ask_agente_documento_job_transcribrothers.py`
- Test: `backend/tests/test_modulo_persistencia_historico_chat_ask_agente_documento_job_transcribrothers.py`

**Interfaces:**
- Consumes: `pathlib.Path`, `json`
- Produces:
  - `NOME_ARQUIVO_HISTORICO_CHAT_ASK_AGENTE_DOCUMENTO_JOB_TRANSCRIBROTHERS = "historico_chat_ask_agente_documento_job.json"`
  - `TETO_MENSAGENS_HISTORICO_CHAT_ASK_AGENTE_DOCUMENTO_JOB_TRANSCRIBROTHERS = 40`
  - `ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers` dataclass: `papel: str` (`usuario`|`assistente`|`agente`), `modo: str` (`ask`|`agente`), `texto: str`, `criado_em: str`, `citacoes: list[dict]`, `imagens: list[dict]`, `estado: str | None`, `tipo_pipeline: str | None`
  - `def caminho_historico_chat_ask_agente_no_work_transcribrothers(diretorio_trabalho_job: Path) -> Path`
  - `def carregar_historico_chat_ask_agente_do_work_transcribrothers(diretorio_trabalho_job: Path) -> list[ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers]`
  - `def gravar_historico_chat_ask_agente_no_work_transcribrothers(diretorio_trabalho_job: Path, itens: list[ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers]) -> None` — escreve tmp + replace; se `len > 40`, fica com os **40 mais novos**
  - `def anexar_item_historico_chat_ask_agente_no_work_transcribrothers(diretorio_trabalho_job: Path, item: ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers) -> list[ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers]`
  - `def item_historico_chat_ask_agente_para_dict_transcribrothers(item) -> dict`
  - `def dict_para_item_historico_chat_ask_agente_transcribrothers(raw: dict) -> ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers | None`

- [ ] **Step 1: Escrever o teste que falha**

```python
from pathlib import Path

from transcribrothers_backend.modulo_persistencia_historico_chat_ask_agente_documento_job_transcribrothers import (
    ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers,
    TETO_MENSAGENS_HISTORICO_CHAT_ASK_AGENTE_DOCUMENTO_JOB_TRANSCRIBROTHERS,
    anexar_item_historico_chat_ask_agente_no_work_transcribrothers,
    carregar_historico_chat_ask_agente_do_work_transcribrothers,
)


def _item(texto: str) -> ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers:
    return ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers(
        papel="usuario",
        modo="ask",
        texto=texto,
        criado_em="2026-10-03T12:00:00+00:00",
        citacoes=[],
        imagens=[],
        estado=None,
        tipo_pipeline=None,
    )


def test_carregar_historico_ausente_devolve_lista_vazia(tmp_path: Path) -> None:
    assert carregar_historico_chat_ask_agente_do_work_transcribrothers(tmp_path) == []


def test_anexar_item_persiste_e_rele(tmp_path: Path) -> None:
    saida = anexar_item_historico_chat_ask_agente_no_work_transcribrothers(tmp_path, _item("oi"))
    assert len(saida) == 1
    assert saida[0].texto == "oi"
    assert carregar_historico_chat_ask_agente_do_work_transcribrothers(tmp_path)[0].texto == "oi"


def test_anexar_acima_do_teto_descarta_os_mais_antigos(tmp_path: Path) -> None:
    for i in range(TETO_MENSAGENS_HISTORICO_CHAT_ASK_AGENTE_DOCUMENTO_JOB_TRANSCRIBROTHERS + 3):
        anexar_item_historico_chat_ask_agente_no_work_transcribrothers(tmp_path, _item(f"m{i}"))
    itens = carregar_historico_chat_ask_agente_do_work_transcribrothers(tmp_path)
    assert len(itens) == TETO_MENSAGENS_HISTORICO_CHAT_ASK_AGENTE_DOCUMENTO_JOB_TRANSCRIBROTHERS
    assert itens[0].texto == "m3"
    assert itens[-1].texto == "m42"
```

- [ ] **Step 2: Rodar o teste e confirmar que falha**

```powershell
cd d:\claude\defensoria\transcribrothers\backend; python -m pytest tests/test_modulo_persistencia_historico_chat_ask_agente_documento_job_transcribrothers.py -v
```

Expected: FAIL (módulo inexistente).

- [ ] **Step 3: Implementar o módulo** — dataclass + JSON `{ "versao": 1, "itens": [...] }` + tmp/replace + teto 40 no gravar.

- [ ] **Step 4: Rodar o teste e confirmar que passa**

```powershell
cd d:\claude\defensoria\transcribrothers\backend; python -m pytest tests/test_modulo_persistencia_historico_chat_ask_agente_documento_job_transcribrothers.py -v
```

Expected: PASS.

---

### Task 2: Helper de visibilidade do chat (Markdown ou snapshot)

**Files:**
- Create: `frontend/src/modulo_util_job_pode_abrir_chat_ask_agente_documento_transcribrothers.ts`
- Test: `frontend/src/modulo_util_job_pode_abrir_chat_ask_agente_documento_transcribrothers.test.ts`

**Interfaces:**
- Consumes: shape mínimo `{ result_markdown?: string | null, steps_json?: Record<string, unknown> | null }`
- Produces: `jobPodeAbrirChatAskAgenteDocumentoTranscribrothers(job: { result_markdown?: string | null; steps_json?: Record<string, unknown> | null } | null): boolean`

Regra: `true` se `result_markdown` trim não vazio **ou** `steps_json.regeneracao_tutorial_snapshot` é objeto não-nulo. `null`/job vazio → `false`.

- [ ] **Step 1: Teste que falha**

```typescript
import { describe, expect, it } from "vitest";
import { jobPodeAbrirChatAskAgenteDocumentoTranscribrothers } from "./modulo_util_job_pode_abrir_chat_ask_agente_documento_transcribrothers.ts";

describe("visibilidade do chat Ask/Agente", () => {
  it("abre só com Markdown", () => {
    expect(
      jobPodeAbrirChatAskAgenteDocumentoTranscribrothers({
        result_markdown: "# doc",
        steps_json: {},
      }),
    ).toBe(true);
  });
  it("abre só com snapshot de regeneração", () => {
    expect(
      jobPodeAbrirChatAskAgenteDocumentoTranscribrothers({
        result_markdown: "",
        steps_json: { regeneracao_tutorial_snapshot: { texto_completo: "fala" } },
      }),
    ).toBe(true);
  });
  it("fecha sem os dois", () => {
    expect(
      jobPodeAbrirChatAskAgenteDocumentoTranscribrothers({
        result_markdown: "  ",
        steps_json: {},
      }),
    ).toBe(false);
  });
});
```

- [ ] **Step 2: Rodar Vitest e confirmar falha**

```powershell
cd d:\claude\defensoria\transcribrothers\frontend; npx --yes vitest run src/modulo_util_job_pode_abrir_chat_ask_agente_documento_transcribrothers.test.ts
```

- [ ] **Step 3: Implementar o helper**
- [ ] **Step 4: Rodar Vitest e confirmar PASS**

Na Task 3, trocar `fabRegeneracaoTutorialVisivel` para usar este helper **e** manter o filtro de status (`completed` | `failed` | `generating_tutorial`).

---

### Task 3: Casco — dock à direita, Ask | Agente, Agente sem fechar o painel

**Files:**
- Create: `frontend/src/componente_painel_chat_ask_agente_documento_job_transcribrothers.tsx`
- Modify: `frontend/src/componente_pagina_principal_formulario_drive_preview_tutorial.tsx`
- Modify: `frontend/src/componente_pagina_principal_formulario_drive_preview_tutorial.css`

**Interfaces:**
- Consumes: callbacks atuais `enviarPedidoPainelFabAtualizarTutorialTranscribrothers`, estados de chips, `instrucoesRegeneracaoTutorialMarkdown`
- Produces: painel controlado por props. Novo estado `modoChatAskOuAgenteDocumento: "ask" | "agente"` (default `"agente"` para não mudar o hábito de quem só regenera). Ask: chips escondidos; Enviar desabilitado até a Task 7 (`askDisponivel={false}`).

- [ ] **Step 1: CSS do dock**

Envolver a `section.tb-grid-preview` e o painel:

```css
.tb-chat-ask-agente-dock-wrapper {
  display: flex;
  align-items: stretch;
  gap: 16px;
  margin-top: 16px;
}
.tb-chat-ask-agente-dock-wrapper .tb-grid-preview {
  flex: 1 1 auto;
  min-width: 0;
  margin-top: 0;
}
.tb-chat-ask-agente-painel {
  flex: 0 0 min(420px, 36vw);
  width: min(420px, 36vw);
  max-height: calc(100vh - 120px);
  position: sticky;
  top: 88px;
  display: flex;
  flex-direction: column;
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  box-shadow: 0 8px 28px rgba(15, 23, 42, 0.08);
}
@media (max-width: 980px) {
  .tb-chat-ask-agente-dock-wrapper {
    display: block;
  }
  .tb-chat-ask-agente-painel {
    position: fixed;
    inset: 72px 12px 88px 12px;
    width: auto;
    flex: none;
    z-index: 160;
    max-height: none;
  }
}
```

Não renderizar `tb-fab-regen-backdrop`. O FAB continua `position: fixed` no canto para abrir/fechar.

- [ ] **Step 2: Extrair o JSX do painel** (header + chips + composer) para `ComponentePainelChatAskAgenteDocumentoJobTranscribrothers`. Props mínimas: `modo`, `aoAlternarModo`, `askDisponivel`, `titulo`, `disabledEnviar`, `textoInstrucoes`, `aoMudarTexto`, `aoEnviar`, `childrenChips`, `mensagens` (array em memória, pode começar vazio), `aoFechar`.

Interruptor:

```tsx
<div role="tablist" aria-label="Modo do chat">
  <button type="button" aria-selected={modo === "ask"} onClick={() => aoAlternarModo("ask")}>Ask</button>
  <button type="button" aria-selected={modo === "agente"} onClick={() => aoAlternarModo("agente")}>Agente</button>
</div>
```

- [ ] **Step 3: Página principal**
  - Visibilidade: `jobPodeAbrirChatAskAgenteDocumentoTranscribrothers(job)` + status `completed|failed|generating_tutorial`.
  - **Remover** `setPainelRegeneracaoFabAberto(false)` em: `solicitarRegeneracaoTutorialMarkdownComTextoInstrucoesTranscribrothers` (~3591), bug (~3623), notas (~3652), seção (~3855). Manter fechar no Escape e no botão ×.
  - **Parar de esconder** o chat quando `modalProgressoJobAberto` ou `modalPreviewRegeneracao*`. Continuar escondendo em `paginaVideoNarradoAberta` e `modoEdicaoMarkdownTutorialAtivo`.
  - Se `painelRegeneracaoFabAberto`, renderizar o painel **ao lado** do grid (não no portal com overlay fullscreen). O botão FAB pode continuar no portal sem backdrop.
  - Grid: se o painel estiver aberto, o `section.tb-grid` fica dentro de `div.tb-chat-ask-agente-dock-wrapper`.

- [ ] **Step 4: Verificar no browser** (Vite :5183)
  - Abrir um job completed: FAB visível.
  - Abrir o painel: documento continua legível (sem escurecer); painel à direita.
  - Enviar no Agente: painel **não** some; modal de progresso pode abrir por cima.
  - Ask: chips sumidos; Enviar desabilitado.

---

### Task 4: Montagem do contexto Ask

**Files:**
- Create: `backend/transcribrothers_backend/modulo_montar_contexto_chat_ask_markdown_transcricao_e_catalogo_frames_transcribrothers.py`
- Test: `backend/tests/test_modulo_montar_contexto_chat_ask_markdown_transcricao_e_catalogo_frames_transcribrothers.py`

**Interfaces:**
- Consumes: `ResultadoTranscricaoComSegmentos`, `listar_secoes_markdown_nivel2_tutorial_transcribrothers`, `listar_registros_frames_manuais_capturados_do_steps_json_transcribrothers`
- Produces:
  - `LIMITE_CARACTERES_MARKDOWN_CONTEXTO_CHAT_ASK_TRANSCRIBROTHERS = 95_000`
  - `LIMITE_CARACTERES_TRANSCRICAO_CONTEXTO_CHAT_ASK_TRANSCRIBROTHERS = 8_000`
  - `@dataclass FrameCatalogoChatAskTranscribrothers`: `caminho_relativo: str`, `instante_segundos: float`
  - `@dataclass ContextoChatAskDocumentoJobTranscribrothers`: `markdown_para_prompt: str`, `transcricao_para_prompt: str`, `catalogo_frames: list[FrameCatalogoChatAskTranscribrothers]`, `tem_markdown: bool`, `tem_transcricao: bool`
  - `def montar_catalogo_frames_chat_ask_transcribrothers(*, caminhos_frames_rel_job: list[tuple[float, str]], steps_json: dict | None) -> list[FrameCatalogoChatAskTranscribrothers]` — une snapshot + frames manuais + `offset_ms_(\d+)` no nome do PNG; dedup por `caminho_relativo` (fica o menor `|t|` explícito)
  - `def montar_contexto_chat_ask_documento_job_transcribrothers(*, markdown: str, transcricao: ResultadoTranscricaoComSegmentos | None, pergunta: str, caminhos_frames_rel_job: list[tuple[float, str]], steps_json: dict | None) -> ContextoChatAskDocumentoJobTranscribrothers`
  - Markdown curto: vai inteiro. Longo: índice das linhas `##` + primeiros 4_000 chars + seções cujo título/corpo contém algum token da pergunta com `len >= 4` (casefold).
  - Transcrição curta: `texto_completo`. Longa: recorte de `texto_completo` + segmentos cujo `texto` contém token da pergunta.

- [ ] **Step 1: Testes**

```python
from transcribrothers_backend.modulo_montar_contexto_chat_ask_markdown_transcricao_e_catalogo_frames_transcribrothers import (
    LIMITE_CARACTERES_MARKDOWN_CONTEXTO_CHAT_ASK_TRANSCRIBROTHERS,
    montar_catalogo_frames_chat_ask_transcribrothers,
    montar_contexto_chat_ask_documento_job_transcribrothers,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
    SegmentoTranscricaoComTempo,
)


def test_markdown_curto_vai_inteiro() -> None:
    ctx = montar_contexto_chat_ask_documento_job_transcribrothers(
        markdown="# T\n\n## Fluxo\n\njornada",
        transcricao=None,
        pergunta="fluxo",
        caminhos_frames_rel_job=[],
        steps_json={},
    )
    assert ctx.tem_markdown is True
    assert "## Fluxo" in ctx.markdown_para_prompt
    assert ctx.tem_transcricao is False


def test_markdown_longo_inclui_indice_de_h2() -> None:
    corpo = "# T\n\n" + ("x" * (LIMITE_CARACTERES_MARKDOWN_CONTEXTO_CHAT_ASK_TRANSCRIBROTHERS + 10))
    corpo += "\n\n## Atendimento\n\nfluxo de fila"
    ctx = montar_contexto_chat_ask_documento_job_transcribrothers(
        markdown=corpo,
        transcricao=None,
        pergunta="atendimento fila",
        caminhos_frames_rel_job=[],
        steps_json={},
    )
    assert "## Atendimento" in ctx.markdown_para_prompt
    assert "indice" in ctx.markdown_para_prompt.lower() or "## Atendimento" in ctx.markdown_para_prompt


def test_catalogo_une_snapshot_e_offset_ms() -> None:
    frames = montar_catalogo_frames_chat_ask_transcribrothers(
        caminhos_frames_rel_job=[(12.4, "assets/a.png")],
        steps_json={},
    )
    assert frames[0].caminho_relativo == "assets/a.png"
    assert frames[0].instante_segundos == 12.4
    extra = montar_catalogo_frames_chat_ask_transcribrothers(
        caminhos_frames_rel_job=[],
        steps_json={},
    )
    from transcribrothers_backend.modulo_montar_contexto_chat_ask_markdown_transcricao_e_catalogo_frames_transcribrothers import (
        instante_segundos_de_offset_ms_no_nome_png_chat_ask_transcribrothers,
    )
    assert instante_segundos_de_offset_ms_no_nome_png_chat_ask_transcribrothers(
        "screenshot_offset_ms_0000015000_indice_0001.png"
    ) == 15.0
```

Incluir `instante_segundos_de_offset_ms_no_nome_png_chat_ask_transcribrothers(nome: str) -> float | None` no mesmo módulo.

- [ ] **Step 2: pytest — deve falhar**
- [ ] **Step 3: Implementar**
- [ ] **Step 4: pytest — PASS**

```powershell
cd d:\claude\defensoria\transcribrothers\backend; python -m pytest tests/test_modulo_montar_contexto_chat_ask_markdown_transcricao_e_catalogo_frames_transcribrothers.py -v
```

---

### Task 5: Parse da resposta JSON do Ask

**Files:**
- Create: `backend/transcribrothers_backend/modulo_parsear_resposta_json_chat_ask_litellm_transcribrothers.py`
- Test: `backend/tests/test_modulo_parsear_resposta_json_chat_ask_litellm_transcribrothers.py`

**Interfaces:**
- Consumes: `extrair_primeiro_objeto_json_de_texto_llm_transcribrothers`
- Produces:
  - `@dataclass CitacaoChatAskTranscribrothers`: `tipo: str` (`transcricao`|`markdown`), `rotulo: str`, `instante_segundos: float | None`, `heading: str | None`
  - `@dataclass RespostaModeloChatAskTranscribrothers`: `texto: str`, `citacoes: list[CitacaoChatAskTranscribrothers]`, `instantes_imagem_segundos: list[float]`
  - `def parsear_resposta_json_chat_ask_litellm_transcribrothers(texto_bruto: str) -> RespostaModeloChatAskTranscribrothers`
  - Se não houver JSON válido: `texto` = texto bruto strip (fallback), `citacoes=[]`, `instantes=[]`.
  - `tipo` inválido vira `"markdown"`. Instantes: só `int`/`float` finitos `>= 0`.

- [ ] **Step 1: Testes**

```python
from transcribrothers_backend.modulo_parsear_resposta_json_chat_ask_litellm_transcribrothers import (
    parsear_resposta_json_chat_ask_litellm_transcribrothers,
)


def test_parseia_json_puro() -> None:
    r = parsear_resposta_json_chat_ask_litellm_transcribrothers(
        '{"texto":"jornada","citacoes":[{"tipo":"transcricao","rotulo":"12:40","instante_segundos":760,"heading":null}],"instantes_imagem_segundos":[760]}'
    )
    assert r.texto == "jornada"
    assert r.citacoes[0].instante_segundos == 760
    assert r.instantes_imagem_segundos == [760.0]


def test_parseia_json_dentro_de_cerca_markdown() -> None:
    r = parsear_resposta_json_chat_ask_litellm_transcribrothers(
        'veja:\n```json\n{"texto":"ok","citacoes":[],"instantes_imagem_segundos":[]}\n```'
    )
    assert r.texto == "ok"


def test_sem_json_usa_texto_bruto() -> None:
    r = parsear_resposta_json_chat_ask_litellm_transcribrothers("resposta solta")
    assert r.texto == "resposta solta"
    assert r.citacoes == []
```

- [ ] **Step 2–4:** falha → implementar → PASS

```powershell
cd d:\claude\defensoria\transcribrothers\backend; python -m pytest tests/test_modulo_parsear_resposta_json_chat_ask_litellm_transcribrothers.py -v
```

---

### Task 6: GET histórico + POST chat-ask (ainda sem resolver imagem)

**Files:**
- Create: `backend/transcribrothers_backend/modulo_orquestrar_turno_chat_ask_job_transcribrothers.py`
- Test: `backend/tests/test_api_chat_ask_e_historico_documento_job_transcribrothers.py`
- Modify: `backend/transcribrothers_backend/main.py`

**Interfaces:**
- Consumes: persistência, contexto, parse, `litellm_chat_completions_texto_simples_transcribrothers`, `carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers`, `_diretorio_trabalho_job`
- Produces:
  - `async def orquestrar_turno_chat_ask_job_transcribrothers(*, diretorio_trabalho_job, markdown, steps_json, mensagem, modelo, api_key, api_base, httpx_verify, resolver_imagens: bool = False) -> tuple[str, list[dict], list[dict], list[ItemHistorico...], dict | None]`
    - `resolver_imagens=False` nesta task: `imagens` sempre `[]` (os instantes do modelo são ignorados).
    - Anexa turno usuário, chama LiteLLM, parseia, anexa turno assistente, devolve histórico.
    - Sem markdown e sem snapshot: raise `ChatAskSemFonteError` (classe no mesmo módulo) com mensagem pt-BR: `"Não há Markdown nem transcrição neste job para o Ask."`
  - Pydantic em `main.py`:
    - `CorpoChatAskDocumentoJobTranscribrothers`: `mensagem: str`
    - `RespostaChatAskDocumentoJobTranscribrothers`: `texto`, `citacoes`, `imagens`, `historico`
    - `RespostaHistoricoChatAskAgenteDocumentoJobTranscribrothers`: `historico: list[dict]`
  - `GET /api/jobs/{job_id}/chat-historico`
  - `POST /api/jobs/{job_id}/chat-ask` — 404 se job não existe; 409 se `ChatAskSemFonteError`; 502 se LiteLLM falhar; **não** muda `result_markdown`; **não** muda `status` para `generating_tutorial`.

System prompt (constante no orquestrador), em pt-BR: responder só com o contexto; JSON `{texto, citacoes, instantes_imagem_segundos}`; citar tempo e `##`; não gerar documento Markdown novo.

`caminhos_frames_rel_job`: ler do snapshot em disco se o JSON tiver essa chave; senão `[]`. O snapshot STT (`ResultadoTranscricaoComSegmentos`) vem de `carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers`. Se o snapshot raw for dict com `caminhos_frames_rel_job`, parsear pares `[float, str]`.

- [ ] **Step 1: Testes de API** (inserir job como em `test_api_listar_assets_imagens_tutorial_job_transcribrothers.py`)

```python
def test_chat_historico_job_inexistente_404() -> None:
    with TestClient(app) as client:
        r = client.get("/api/jobs/00000000-0000-4000-8000-000000000099/chat-historico")
        assert r.status_code == 404


def test_chat_historico_vazio_200() -> None:
    # inserir job completed com markdown
    r = client.get(f"/api/jobs/{jid}/chat-historico")
    assert r.status_code == 200
    assert r.json()["historico"] == []


def test_chat_ask_sem_fonte_409() -> None:
    # job sem markdown e sem arquivo de snapshot
    r = client.post(f"/api/jobs/{jid}/chat-ask", json={"mensagem": "oi"})
    assert r.status_code == 409


def test_chat_ask_nao_altera_markdown_e_devolve_texto() -> None:
    with patch(
        "transcribrothers_backend.modulo_orquestrar_turno_chat_ask_job_transcribrothers.litellm_chat_completions_texto_simples_transcribrothers",
        new=AsyncMock(return_value='{"texto":"jornada do usuario","citacoes":[],"instantes_imagem_segundos":[]}'),
    ):
        r = client.post(f"/api/jobs/{jid}/chat-ask", json={"mensagem": "qual a jornada?"})
    assert r.status_code == 200
    assert r.json()["texto"] == "jornada do usuario"
    assert client.get(f"/api/jobs/{jid}").json()["result_markdown"] == markdown_antes
    assert client.get(f"/api/jobs/{jid}").json()["status"] != "generating_tutorial" or status_era_completed
```

Patch no **orquestrador**, não em `main`, se o import for `from ...modulo_cliente... import litellm_...` dentro do orquestrador (patch o símbolo usado no módulo do orquestrador).

- [ ] **Step 2: pytest API — FAIL**
- [ ] **Step 3: Orquestrador + rotas**
- [ ] **Step 4: pytest API — PASS**

```powershell
cd d:\claude\defensoria\transcribrothers\backend; python -m pytest tests/test_api_chat_ask_e_historico_documento_job_transcribrothers.py -v
```

---

### Task 7: Cliente frontend + Enviar no Ask

**Files:**
- Create: `frontend/src/modulo_tipos_item_historico_chat_ask_agente_documento_job_transcribrothers.ts`
- Create: `frontend/src/modulo_api_chat_ask_e_historico_documento_job_transcribrothers.ts`
- Modify: `frontend/src/componente_painel_chat_ask_agente_documento_job_transcribrothers.tsx`
- Modify: `frontend/src/componente_pagina_principal_formulario_drive_preview_tutorial.tsx`

**Interfaces:**
- `ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers` (espelho do dataclass)
- `buscarHistoricoChatAskAgenteDocumentoJobApiTranscribrothers(jobId: string): Promise<Item...[]>`
- `enviarMensagemChatAskDocumentoJobApiTranscribrothers(jobId: string, mensagem: string): Promise<{ texto, citacoes, imagens, historico }>`

- [ ] **Step 1: API client** — `fetch` + throw se `!ok` com `await r.text()`.
- [ ] **Step 2: Ao abrir o painel**, `GET chat-historico` e guardar em estado `mensagensChatAskAgente`.
- [ ] **Step 3: Enviar no Ask** chama a API; `askDisponivel={true}`; mostra «pensando…»; em sucesso substitui a lista por `historico`; em erro toast + bolha de erro **sem** apagar o fio. **Não** chama `regenerate-*`.
- [ ] **Step 4: Render** — bolha assistente: `texto`; citações como chips (`12:40`, `## Fluxo`); imagens `<img src={url} alt="" />` (vazio até Task 8).
- [ ] **Step 5: Browser** — pergunta sobre o Markdown; resposta no chat; documento inalterado.

---

### Task 8: Imagem no Ask (galeria → captura)

**Files:**
- Create: `backend/transcribrothers_backend/modulo_resolver_imagem_chat_ask_galeria_ou_captura_frame_transcribrothers.py`
- Test: `backend/tests/test_modulo_resolver_imagem_chat_ask_galeria_ou_captura_frame_transcribrothers.py`
- Modify: `backend/transcribrothers_backend/modulo_orquestrar_turno_chat_ask_job_transcribrothers.py`
- Modify: `backend/tests/test_api_chat_ask_e_historico_documento_job_transcribrothers.py`

**Interfaces:**
- `DELTA_MAXIMO_SEGUNDOS_FRAME_GALERIA_CHAT_ASK_TRANSCRIBROTHERS = 5.0`
- `@dataclass ImagemResolvidaChatAskTranscribrothers`: `caminho_relativo: str`, `instante_segundos: float`, `origem: str` (`galeria`|`captura_sob_demanda`)
- `async def resolver_imagens_chat_ask_por_instantes_transcribrothers(*, instantes_segundos: list[float], catalogo: list[FrameCatalogoChatAskTranscribrothers], caminho_video: Path | None, diretorio_trabalho_job: Path, steps_json: dict, capturar_frame) -> tuple[list[ImagemResolvidaChatAskTranscribrothers], dict]`
  - Para cada T: se existir frame com `abs(t-T) <= 5`, usa o de menor delta (`origem=galeria`).
  - Senão, se `caminho_video` é arquivo: `capturar_frame(...)` (injetável; produção = `capturar_frame_manual_video_tutorial_para_assets_do_job_transcribrothers`); `mesclar_registro_frame_manual_capturado_no_steps_json_transcribrothers(..., origem="chat_ask")`; `origem=captura_sob_demanda`.
  - Sem vídeo ou captura falhou: não inclui essa imagem (orquestrador acrescenta aviso no `texto` se pediram instante e `imagens` ficou menor).
- URL na API: `f"/api/jobs/{job_id}/assets/{nome}"` onde `nome` é o basename de `caminho_relativo`.

- [ ] **Step 1: Testes do módulo** com `AsyncMock` de captura

```python
@pytest.mark.asyncio
async def test_escolhe_galeria_quando_delta_ate_5() -> None:
    capturar = AsyncMock()
    imagens, _steps = await resolver_imagens_chat_ask_por_instantes_transcribrothers(
        instantes_segundos=[10.0],
        catalogo=[FrameCatalogoChatAskTranscribrothers("assets/a.png", 12.0)],
        caminho_video=None,
        diretorio_trabalho_job=tmp_path,
        steps_json={},
        capturar_frame=capturar,
    )
    assert imagens[0].origem == "galeria"
    capturar.assert_not_called()


@pytest.mark.asyncio
async def test_captura_quando_delta_maior_que_5(tmp_path: Path) -> None:
    video = tmp_path / "video_entrada_arquivo_local.mp4"
    video.write_bytes(b"0")
    async def _cap(**kwargs):
        return (80.0, "frame_manual.png", "assets/frame_manual.png", "!")
    imagens, steps = await resolver_imagens_chat_ask_por_instantes_transcribrothers(
        instantes_segundos=[80.0],
        catalogo=[FrameCatalogoChatAskTranscribrothers("assets/a.png", 12.0)],
        caminho_video=video,
        diretorio_trabalho_job=tmp_path,
        steps_json={},
        capturar_frame=_cap,
    )
    assert imagens[0].origem == "captura_sob_demanda"
    assert imagens[0].caminho_relativo == "assets/frame_manual.png"
```

- [ ] **Step 2–4:** TDD do módulo
- [ ] **Step 5:** No orquestrador, `resolver_imagens=True` no POST. Persistir `steps_json` se a captura mesclou registro. Não aplicar snippet no Markdown.
- [ ] **Step 6:** Teste de API: mock do modelo devolve `instantes_imagem_segundos:[12]`; catálogo no snapshot; assert `imagens[0].origem == "galeria"` e markdown inalterado.

```powershell
cd d:\claude\defensoria\transcribrothers\backend; python -m pytest tests/test_modulo_resolver_imagem_chat_ask_galeria_ou_captura_frame_transcribrothers.py tests/test_api_chat_ask_e_historico_documento_job_transcribrothers.py -v
```

---

### Task 9: Turno de Agente persistido + cartão Ver prévia

**Files:**
- Modify: `backend/transcribrothers_backend/main.py` — `POST /api/jobs/{job_id}/chat-historico`
- Modify: `backend/tests/test_api_chat_ask_e_historico_documento_job_transcribrothers.py`
- Modify: `frontend/src/modulo_api_chat_ask_e_historico_documento_job_transcribrothers.ts`
- Modify: `frontend/src/componente_painel_chat_ask_agente_documento_job_transcribrothers.tsx`
- Modify: `frontend/src/componente_pagina_principal_formulario_drive_preview_tutorial.tsx`

**Interfaces:**
- `CorpoAnexarHistoricoChatAskAgenteDocumentoJobTranscribrothers`: mesmo shape do item (papel/modo/texto/estado/tipo_pipeline)
- `POST /api/jobs/{job_id}/chat-historico` → anexa via `anexar_item_historico_chat_ask_agente_no_work_transcribrothers`, devolve `{ historico }`
- Frontend: `anexarItemHistoricoChatAskAgenteDocumentoJobApiTranscribrothers(jobId, item)`

- [ ] **Step 1: Teste API** — POST item `papel=agente`, `estado=gerando`; GET devolve 1 item.
- [ ] **Step 2: Endpoint + pytest PASS**
- [ ] **Step 3: No Enviar Agente** (depois do `setJob` das funções `solicitarRegeneracao*`): anexar no histórico `{ papel: "agente", modo: "agente", texto: instruções, estado: "gerando", tipo_pipeline }` e o turno do usuário. Não fechar painel (já Task 3).
- [ ] **Step 4: Quando `previewRegeneracaoTutorialMarkdownDocumentoInteiro` ou preview de seção existir**, atualizar o último turno agente para `estado: "preview_pronta"` (POST ou PATCH local + persistir) e mostrar botão **Ver prévia** que chama `setModalPreviewRegeneracaoTutorialAberto(true)` ou o de seção.
- [ ] **Step 5: Browser** — Agente → progresso → cartão no chat abre a modal; Ask e Agente no mesmo fio após F5 (GET historico).

---

## Verificação final (depois da Task 9)

```powershell
cd d:\claude\defensoria\transcribrothers\backend; python -m pytest tests/test_modulo_persistencia_historico_chat_ask_agente_documento_job_transcribrothers.py tests/test_modulo_montar_contexto_chat_ask_markdown_transcricao_e_catalogo_frames_transcribrothers.py tests/test_modulo_parsear_resposta_json_chat_ask_litellm_transcribrothers.py tests/test_modulo_resolver_imagem_chat_ask_galeria_ou_captura_frame_transcribrothers.py tests/test_api_chat_ask_e_historico_documento_job_transcribrothers.py -v
```

```powershell
cd d:\claude\defensoria\transcribrothers\frontend; npx --yes vitest run src/modulo_util_job_pode_abrir_chat_ask_agente_documento_transcribrothers.test.ts
```

No browser, job com vídeo + Markdown:

1. Painel dockado, sem backdrop.
2. Ask: pergunta sobre a reunião / seção; citações; imagem só se pedir tela.
3. Markdown do job não muda no Ask.
4. Agente: Enviar mantém o chat; **Ver prévia** abre a modal antiga.
5. F5: histórico permanece.

---

## Cobertura do spec

| Spec | Task |
|---|---|
| Ask \| Agente, sem híbrido | 3 |
| Ask nunca grava | 6, 7 |
| Sem botão Ask → gravar | 3, 7 |
| Agente = regenerate-* + prévia | 3, 9 |
| Chat aberto durante o job | 3 |
| Imagem C (5 s → captura) | 8 |
| Contexto Markdown + transcrição | 4, 6 |
| Dock sem backdrop | 3 |
| Histórico no disco, teto 40 | 1, 6, 9 |
| GET/POST chat-ask | 6 |
| FAB se Markdown ou snapshot | 2, 3 |
| Sem SSE | 6, 7 |
| Fora: outro formato, streaming, RAG | — |
