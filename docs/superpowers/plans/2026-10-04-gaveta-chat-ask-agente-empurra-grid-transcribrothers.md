# Gaveta do chat Ask/Agente que empurra o grid — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Trocar o FAB + card flutuante por uma gaveta à direita que empurra o grid, com composer no visual Excalibrothers (Ask | Agente, Limpar, cápsula `+`).

**Architecture:** Só casco no passo 1. Passo 2 adiciona `DELETE /chat-historico` reusando `gravar_historico_chat_ask_agente_no_work_transcribrothers`. Passo 3 adiciona `POST /chat-ask-resolver-frame` e `instante_anexo_segundos` no Ask, reusando `resolver_imagens_chat_ask_por_instantes_transcribrothers`. Sem pixels no LiteLLM.

**Tech Stack:** FastAPI, pytest, React/TypeScript, CSS do preview, Vitest nos helpers/API client.

**Spec:** `docs/superpowers/specs/2026-10-04-gaveta-chat-ask-agente-empurra-grid-transcribrothers-design.md`

## Global Constraints

- Nomes de arquivo longos e descritivos (padrão Transcribrothers).
- UI, toasts e mensagens de erro em pt-BR.
- Não commitar a menos que o usuário peça explicitamente (ignorar passos de commit deste plano).
- Sem FAB residual, sem backdrop, sem overlay tipo Configurações.
- Ask nunca altera `result_markdown`. Resolver-frame e captura do `+` **não** usam `POST .../capturar-frame-manual-video-tutorial` (essa rota devolve snippet para o documento).
- `DELETE` limpa só o JSON do histórico; não apaga `steps_json` nem PNGs.
- Galeria se `|Δt| ≤ 5,0` s; senão captura com `origem=chat_ask`.
- Windows PowerShell: encadear com `;`, não `&&`.
- Trabalhar in-place neste checkout (árvore já suja; não criar worktree).

## File map

**Create:**
- `frontend/src/modulo_util_rotulo_botao_toolbar_e_limpar_chat_ask_agente_documento_transcribrothers.ts`
- `frontend/src/modulo_util_rotulo_botao_toolbar_e_limpar_chat_ask_agente_documento_transcribrothers.test.ts`
- `frontend/src/modulo_util_prefixo_frame_anexado_chat_ask_agente_documento_transcribrothers.ts`
- `frontend/src/modulo_util_prefixo_frame_anexado_chat_ask_agente_documento_transcribrothers.test.ts`

**Modify:**
- `frontend/src/componente_painel_chat_ask_agente_documento_job_transcribrothers.tsx`
- `frontend/src/componente_pagina_principal_formulario_drive_preview_tutorial.tsx`
- `frontend/src/componente_pagina_principal_formulario_drive_preview_tutorial.css`
- `frontend/src/modulo_api_chat_ask_e_historico_documento_job_transcribrothers.ts`
- `frontend/src/modulo_api_chat_ask_e_historico_documento_job_transcribrothers.test.ts`
- `backend/transcribrothers_backend/main.py`
- `backend/transcribrothers_backend/modulo_orquestrar_turno_chat_ask_job_transcribrothers.py`
- `backend/tests/test_api_chat_ask_e_historico_documento_job_transcribrothers.py`

**Reuse:**
- `gravar_historico_chat_ask_agente_no_work_transcribrothers`
- `resolver_imagens_chat_ask_por_instantes_transcribrothers`
- `formatar_timestamp_segundos_para_mmss`
- `mesclar_somente_frames_manuais_novos_no_steps_json_recente_transcribrothers`
- `ComponenteDialogoConfirmacaoAcaoDestrutivaOverlayTranscribrothers`

---

### Task 1: Casco da gaveta (toolbar, sem FAB, composer)

**Files:**
- Create: `frontend/src/modulo_util_rotulo_botao_toolbar_e_limpar_chat_ask_agente_documento_transcribrothers.ts`
- Test: `frontend/src/modulo_util_rotulo_botao_toolbar_e_limpar_chat_ask_agente_documento_transcribrothers.test.ts`
- Modify: `frontend/src/componente_painel_chat_ask_agente_documento_job_transcribrothers.tsx`
- Modify: `frontend/src/componente_pagina_principal_formulario_drive_preview_tutorial.tsx`
- Modify: `frontend/src/componente_pagina_principal_formulario_drive_preview_tutorial.css` (bloco `.tb-chat-ask-agente-*` e FAB)

**Interfaces:**
- Consumes: `painelRegeneracaoFabAberto`, `setPainelRegeneracaoFabAberto`, `chatAskAgenteDocumentoJobVisivel`, `ComponentePainelChatAskAgenteDocumentoJobTranscribrothers`
- Produces:
  - `rotuloBotaoToolbarChatAskAgenteDocumentoTranscribrothers(aberto: boolean): "Ocultar chat" | "Abrir chat"`
  - `limparChatAskAgenteDeveFicarDesabilitadoTranscribrothers(args: { historicoVazio: boolean; enviando: boolean }): boolean`
  - Painel: título fixo **Chat**; sem `(i)`; `Ask | Agente` na faixa do composer; **Limpar** à direita; cápsula `+` · campo · enviar em **todos** os modos
  - Props novas no painel: `aoPedirLimpar: () => void`, `limparDesabilitado: boolean`, `aoAnexarFrameDoPlayer?: () => void`, `anexarFrameDesabilitado?: boolean`, `tituloAnexarFrame?: string` (Task 3 preenche o `+` de vídeo; Task 1 deixa o `+` do job com vídeo chamando `aoAnexarFrameDoPlayer` se existir, senão desabilitado com title «Não há vídeo para anexar um frame.»)
  - Página: some o `createPortal` de `tb-fab-principal`; botão `tb-btn-md-toolbar-icone` na `tb-md-header-toolbar`

- [ ] **Step 1: Escrever o teste que falha**

```ts
import { describe, expect, it } from "vitest";
import {
  limparChatAskAgenteDeveFicarDesabilitadoTranscribrothers,
  rotuloBotaoToolbarChatAskAgenteDocumentoTranscribrothers,
} from "./modulo_util_rotulo_botao_toolbar_e_limpar_chat_ask_agente_documento_transcribrothers.ts";

describe("rótulos da gaveta do chat", () => {
  it("toolbar fechada é Abrir chat", () => {
    expect(rotuloBotaoToolbarChatAskAgenteDocumentoTranscribrothers(false)).toBe("Abrir chat");
  });
  it("toolbar aberta é Ocultar chat", () => {
    expect(rotuloBotaoToolbarChatAskAgenteDocumentoTranscribrothers(true)).toBe("Ocultar chat");
  });
  it("Limpar desabilita se vazio ou enviando", () => {
    expect(
      limparChatAskAgenteDeveFicarDesabilitadoTranscribrothers({
        historicoVazio: true,
        enviando: false,
      }),
    ).toBe(true);
    expect(
      limparChatAskAgenteDeveFicarDesabilitadoTranscribrothers({
        historicoVazio: false,
        enviando: true,
      }),
    ).toBe(true);
    expect(
      limparChatAskAgenteDeveFicarDesabilitadoTranscribrothers({
        historicoVazio: false,
        enviando: false,
      }),
    ).toBe(false);
  });
});
```

- [ ] **Step 2: Rodar e ver falhar**

Run (PowerShell, em `frontend`): `npx --yes vitest run src/modulo_util_rotulo_botao_toolbar_e_limpar_chat_ask_agente_documento_transcribrothers.test.ts`

Expected: FAIL (módulo inexistente).

- [ ] **Step 3: Implementar helper + casco**

Helper:

```ts
export function rotuloBotaoToolbarChatAskAgenteDocumentoTranscribrothers(
  aberto: boolean,
): "Ocultar chat" | "Abrir chat" {
  return aberto ? "Ocultar chat" : "Abrir chat";
}

export function limparChatAskAgenteDeveFicarDesabilitadoTranscribrothers(args: {
  historicoVazio: boolean;
  enviando: boolean;
}): boolean {
  return args.historicoVazio || args.enviando;
}
```

Painel (`componente_painel_chat_ask_agente_documento_job_transcribrothers.tsx`):

- `titulo` deixa de ser obrigatório para o texto visível: renderizar sempre `<span>Chat</span>` no header. Pode manter a prop `titulo` só para `aria-label` do aside **ou** trocar o `aria-label` para `"Chat"`. Remover o botão `(i)` e a prop `textoTooltipInfo` se ninguém mais precisar.
- Mover o `role="tablist"` Ask | Agente para **acima da cápsula**, numa faixa `tb-chat-ask-agente-composer-faixa` com Limpar à direita.
- Limpar: `type="button"`, texto **Limpar**, `disabled={limparDesabilitado}`, `onClick={aoPedirLimpar}`.
- Composer em cápsula **sempre** (não só `anexosProjetoEmBranco`): `+` | textarea | enviar. Se `anexosProjetoEmBranco` existir, o `+` abre o menu Texto/Imagem/Arquivo (igual hoje). Senão, o `+` chama `aoAnexarFrameDoPlayer` se definido; se não, `disabled` e `title={tituloAnexarFrame ?? "Não há vídeo para anexar um frame."}`.
- Chips do Agente (`childrenChips`) ficam **acima** da faixa Ask | Agente.
- Remover o textarea solto (`tb-fab-textarea`) do ramo sem anexos.
- Classe do aside: `tb-chat-ask-agente-painel` + `tb-chat-ask-agente-gaveta` (e as de arraste do projeto em branco, se existirem).

Página:

- Importar `rotuloBotaoToolbarChatAskAgenteDocumentoTranscribrothers` e `limparChatAskAgenteDeveFicarDesabilitadoTranscribrothers`.
- Na `tb-md-header-toolbar`, depois dos ícones existentes e **só se** `chatAskAgenteDocumentoJobVisivel`, botão:

```tsx
<button
  type="button"
  className={[
    "tb-btn-md-toolbar-icone",
    painelRegeneracaoFabAberto ? "tb-btn-md-toolbar-icone--ativo" : "",
  ].filter(Boolean).join(" ")}
  title={rotuloBotaoToolbarChatAskAgenteDocumentoTranscribrothers(painelRegeneracaoFabAberto)}
  aria-label={rotuloBotaoToolbarChatAskAgenteDocumentoTranscribrothers(painelRegeneracaoFabAberto)}
  aria-pressed={painelRegeneracaoFabAberto}
  onClick={() => setPainelRegeneracaoFabAberto((v) => !v)}
>
  <IconeChatAskAgenteDocumentoToolbarTranscribrothers />
</button>
```

- Ícone: SVG de balão (mesmo wrapper `IconeSvgHeaderToolbarTranscribrothers` dos outros). Paths simples de speech-bubble.
- **Apagar** o bloco `createPortal` de `tb-fab-principal` / `tb-fab-regen-wrapper` no final da página (hoje ~7966–8000). Não deixar FAB no `document.body`.
- Passar ao painel: `titulo="Chat"`, `aoPedirLimpar={() => { /* Task 2 liga o diálogo; neste passo no-op ou setEstadoConfirmacao se já criar o estado */ }}`, `limparDesabilitado={limparChatAskAgenteDeveFicarDesabilitadoTranscribrothers({ historicoVazio: mensagensChat.length === 0, enviando: enviandoMensagemChatAskDocumento || regenerandoTutorialMarkdown })}`.
- Neste passo o Limpar pode só abrir um estado local `confirmacaoLimparChatAberta` **sem** DELETE (botão + diálogo visual ok; confirmar no-op). Preferível: deixar `aoPedirLimpar` no-op e o diálogo na Task 2, para não mentir «limpo» sem persistir. **Escolha obrigatória:** Limpar no passo 1 só dispara `aoPedirLimpar`; a página passa função vazia `() => {}` — o botão existe, desabilitado quando o fio está vazio. Task 2 substitui o no-op.

CSS (substituir o card flutuante):

```css
.tb-chat-ask-agente-gaveta {
  border-radius: 0;
  box-shadow: none;
  border: 1px solid #e2e8f0;
  border-right: 0;
  padding: 12px 12px 16px;
  max-height: none;
  height: auto;
  align-self: stretch;
  position: sticky;
  top: 88px;
  min-height: calc(100vh - 88px);
}
.tb-chat-ask-agente-composer-faixa {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin: 0 0 8px;
}
.tb-chat-ask-agente-limpar {
  border: 0;
  background: transparent;
  color: #64748b;
  font: inherit;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
}
.tb-chat-ask-agente-limpar:disabled {
  opacity: 0.45;
  cursor: default;
}
@media (max-width: 900px) {
  .tb-chat-ask-agente-dock-wrapper { display: block; }
  .tb-chat-ask-agente-gaveta {
    position: fixed;
    inset: 72px 0 0 auto;
    width: min(400px, 100vw);
    height: auto;
    z-index: 160;
    border-right: 0;
    box-shadow: none;
  }
}
```

Remover `border-radius: 16px` e `box-shadow` de `.tb-chat-ask-agente-painel` (o card). Ajustar `max-height` antigo do painel para a gaveta esticar. Não criar backdrop.

Se existir classe `tb-btn-md-toolbar-icone--ativo`, usar; senão adicionar fundo `#e2e8f0` quando ativo.

- [ ] **Step 4: Rodar o teste**

Run: `npx --yes vitest run src/modulo_util_rotulo_botao_toolbar_e_limpar_chat_ask_agente_documento_transcribrothers.test.ts`

Expected: PASS.

- [ ] **Step 5: Não commitar**

---

### Task 2: DELETE histórico + Limpar com confirmação

**Files:**
- Modify: `backend/transcribrothers_backend/main.py`
- Modify: `backend/tests/test_api_chat_ask_e_historico_documento_job_transcribrothers.py`
- Modify: `frontend/src/modulo_api_chat_ask_e_historico_documento_job_transcribrothers.ts`
- Modify: `frontend/src/modulo_api_chat_ask_e_historico_documento_job_transcribrothers.test.ts`
- Modify: `frontend/src/componente_pagina_principal_formulario_drive_preview_tutorial.tsx`

**Interfaces:**
- Consumes: `gravar_historico_chat_ask_agente_no_work_transcribrothers`, `RespostaHistoricoChatAskAgenteDocumentoJobTranscribrothers`, `ComponenteDialogoConfirmacaoAcaoDestrutivaOverlayTranscribrothers`
- Produces:
  - `DELETE /api/jobs/{job_id}/chat-historico` → 200 `{ "historico": [] }` ou 404 `"Job não encontrado."`
  - `limparHistoricoChatAskAgenteDocumentoJobApiTranscribrothers(jobId: string): Promise<ItemHistorico...[]>`

- [ ] **Step 1: Teste API que falha**

Acrescentar em `backend/tests/test_api_chat_ask_e_historico_documento_job_transcribrothers.py`:

```python
def test_delete_chat_historico_esvazia_arquivo() -> None:
    jid = novo_id_job()
    with TestClient(app) as client:
        sf = app.state.session_factory
        data_dir: Path = app.state.data_dir
        try:
            asyncio.run(_inserir_job_chat_ask_transcribrothers(sf, jid, markdown="# Doc"))
            client.post(
                f"/api/jobs/{jid}/chat-historico",
                json={"papel": "usuario", "modo": "ask", "texto": "oi"},
            )
            r = client.delete(f"/api/jobs/{jid}/chat-historico")
            assert r.status_code == 200, r.text
            assert r.json()["historico"] == []
            hist = client.get(f"/api/jobs/{jid}/chat-historico")
            assert hist.json()["historico"] == []
        finally:
            _limpar_job_chat_ask_transcribrothers(sf, data_dir, jid)


def test_delete_chat_historico_job_inexistente_404() -> None:
    with TestClient(app) as client:
        r = client.delete(f"/api/jobs/{_JOB_INEXISTENTE}/chat-historico")
        assert r.status_code == 404
        assert r.json()["detail"] == _DETALHE_JOB_NAO_ENCONTRADO
```

- [ ] **Step 2: Rodar e ver falhar**

Run (em `backend`): `python -m pytest tests/test_api_chat_ask_e_historico_documento_job_transcribrothers.py::test_delete_chat_historico_esvazia_arquivo tests/test_api_chat_ask_e_historico_documento_job_transcribrothers.py::test_delete_chat_historico_job_inexistente_404 -v`

Expected: FAIL (rota inexistente / 405).

- [ ] **Step 3: Rota + cliente + diálogo**

`main.py` junto das outras rotas de histórico:

```python
@app.delete(
    "/api/jobs/{job_id}/chat-historico",
    response_model=RespostaHistoricoChatAskAgenteDocumentoJobTranscribrothers,
)
async def limpar_historico_chat_ask_agente_documento_job_transcribrothers(
    job_id: str,
    session_factory: SessionFactoryDep,
    data_dir: DataDirDep,
) -> RespostaHistoricoChatAskAgenteDocumentoJobTranscribrothers:
    from transcribrothers_backend.modulo_persistencia_historico_chat_ask_agente_documento_job_transcribrothers import (
        gravar_historico_chat_ask_agente_no_work_transcribrothers,
    )
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Job não encontrado.")
    work = _diretorio_trabalho_job(data_dir, job_id)
    gravar_historico_chat_ask_agente_no_work_transcribrothers(work, [])
    return RespostaHistoricoChatAskAgenteDocumentoJobTranscribrothers(historico=[])
```

Cliente:

```ts
export async function limparHistoricoChatAskAgenteDocumentoJobApiTranscribrothers(
  jobId: string,
): Promise<ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers[]> {
  const r = await fetch(`/api/jobs/${encodeURIComponent(jobId)}/chat-historico`, {
    method: "DELETE",
  });
  await garantirRespostaHttpOkChatAskTranscribrothers(r);
  const data = (await r.json()) as { historico?: unknown };
  return normalizarListaHistoricoChatAskAgenteDocumentoJobTranscribrothers(data.historico);
}
```

Vitest: `DELETE` é chamado; lista vazia não chama (teste do helper já cobre disabled — aqui teste o fetch).

Página: estado `confirmacaoLimparChatAskAberta`. `aoPedirLimpar` abre o diálogo. Instância extra (ou a mesma reusada com cuidado) de `ComponenteDialogoConfirmacaoAcaoDestrutivaOverlayTranscribrothers`:

- `titulo="Limpar o chat deste documento?"`
- `mensagem="O histórico Ask e Agente deste job some. Isso não altera o Markdown."`
- `rotuloConfirmar="Limpar"`
- `rotuloCancelar="Cancelar"`
- Confirmar: `await limparHistorico...`; se 200, `setMensagens([])` (o estado real do fio no page). Só aplica lista vazia se o DELETE for ok. Toast de erro se falhar.

Não apagar `steps_json` nem assets.

- [ ] **Step 4: Rodar testes**

Run: `python -m pytest tests/test_api_chat_ask_e_historico_documento_job_transcribrothers.py::test_delete_chat_historico_esvazia_arquivo tests/test_api_chat_ask_e_historico_documento_job_transcribrothers.py::test_delete_chat_historico_job_inexistente_404 -v`

Run (em `frontend`): `npx --yes vitest run src/modulo_api_chat_ask_e_historico_documento_job_transcribrothers.test.ts`

Expected: PASS.

- [ ] **Step 5: Não commitar**

---

### Task 3: `+` frame do player + `instante_anexo_segundos`

**Files:**
- Create: `frontend/src/modulo_util_prefixo_frame_anexado_chat_ask_agente_documento_transcribrothers.ts`
- Test: `frontend/src/modulo_util_prefixo_frame_anexado_chat_ask_agente_documento_transcribrothers.test.ts`
- Modify: `backend/transcribrothers_backend/main.py`
- Modify: `backend/transcribrothers_backend/modulo_orquestrar_turno_chat_ask_job_transcribrothers.py`
- Modify: `backend/tests/test_api_chat_ask_e_historico_documento_job_transcribrothers.py`
- Modify: `frontend/src/modulo_api_chat_ask_e_historico_documento_job_transcribrothers.ts`
- Modify: `frontend/src/modulo_api_chat_ask_e_historico_documento_job_transcribrothers.test.ts`
- Modify: `frontend/src/componente_painel_chat_ask_agente_documento_job_transcribrothers.tsx`
- Modify: `frontend/src/componente_pagina_principal_formulario_drive_preview_tutorial.tsx`

**Interfaces:**
- Consumes: `resolver_imagens_chat_ask_por_instantes_transcribrothers`, `formatar_timestamp_segundos_para_mmss`, `videoRef.current.currentTime`, mescla segura de `steps_json` do Ask
- Produces:
  - `POST /api/jobs/{job_id}/chat-ask-resolver-frame` body `{ instante_segundos: number }` → `{ caminho_relativo, url, instante_segundos, origem }` ; 404 job; 409 sem vídeo; 502 captura falhou
  - `CorpoChatAskDocumentoJobTranscribrothers.instante_anexo_segundos: float | None = None`
  - `orquestrar_turno_chat_ask_job_transcribrothers(..., instante_anexo_segundos: float | None = None)`: resolve o instante, grava `imagens` no turno do **usuário**, prefixa `Frame anexado em {MM:SS}.` no texto enviado ao modelo
  - `prefixoFrameAnexadoChatAskAgenteDocumentoTranscribrothers(instanteSegundos: number): string` → `"Frame anexado em 1:12."` (usar a mesma regra MM:SS do backend: `m:ss` sem hora se < 3600)
  - `resolverFrameChatAskDocumentoJobApiTranscribrothers(jobId, instanteSegundos)`
  - `enviarMensagemChatAskDocumentoJobApiTranscribrothers(jobId, mensagem, instanteAnexoSegundos?: number | null)`

- [ ] **Step 1: Testes que falham**

Helper frontend:

```ts
it("formata 72s como 1:12", () => {
  expect(prefixoFrameAnexadoChatAskAgenteDocumentoTranscribrothers(72)).toBe(
    "Frame anexado em 1:12.",
  );
});
```

API backend — galeria:

```python
def test_chat_ask_resolver_frame_galeria_nao_altera_markdown() -> None:
    # mesmo snapshot [[12.0, "assets/tela_jornada.png"]] do teste de galeria do Ask
    r = client.post(f"/api/jobs/{jid}/chat-ask-resolver-frame", json={"instante_segundos": 12.0})
    assert r.status_code == 200
    assert r.json()["origem"] == "galeria"
    assert r.json()["caminho_relativo"] == "assets/tela_jornada.png"
    assert "snippet_markdown" not in r.json()
    job = client.get(f"/api/jobs/{jid}").json()
    assert job["result_markdown"] == markdown
```

API — captura (mock de `capturar_frame_manual_video_tutorial_para_assets_do_job_transcribrothers` no resolver, igual ao teste Ask de captura): origem `captura_sob_demanda`; `result_markdown` intacto; `steps_json` só ganha o registro novo.

API — `POST chat-ask` com anexo:

```python
def test_chat_ask_instante_anexo_grava_imagem_no_turno_usuario() -> None:
    # snapshot frame em 12s; litellm devolve texto sem instantes_imagem
    r = client.post(
        f"/api/jobs/{jid}/chat-ask",
        json={"mensagem": "o que tem nessa tela?", "instante_anexo_segundos": 12.0},
    )
    assert r.status_code == 200
    usuario = next(i for i in r.json()["historico"] if i["papel"] == "usuario")
    assert usuario["imagens"][0]["instante_segundos"] == 12.0
    assert usuario["imagens"][0]["origem"] == "galeria"
```

- [ ] **Step 2: Rodar e ver falhar**

Run: `python -m pytest tests/test_api_chat_ask_e_historico_documento_job_transcribrothers.py::test_chat_ask_resolver_frame_galeria_nao_altera_markdown tests/test_api_chat_ask_e_historico_documento_job_transcribrothers.py::test_chat_ask_instante_anexo_grava_imagem_no_turno_usuario -v`

Expected: FAIL.

- [ ] **Step 3: Implementar**

Rota resolver-frame: montar catálogo como o Ask (snapshot + steps), chamar `resolver_imagens_chat_ask_por_instantes_transcribrothers` com um instante. Sem vídeo e sem galeria: 409 `"Não há vídeo para anexar um frame."`. Captura levanta e lista vazia: 502. Sucesso: primeiro item + url `/api/jobs/{id}/assets/{nome}`. Mesclar só frames novos no `steps_json` (mesmo helper do Ask). Não devolver snippet.

Orquestrador: se `instante_anexo_segundos is not None`, resolver **antes** do LiteLLM; imagens do usuário no `anexar` do turno usuario; `mensagem` para o modelo = `f"{mensagem.rstrip()}\n\nFrame anexado em {formatar_timestamp_segundos_para_mmss(instante)}."` (a linha no histórico do usuário pode ser a mensagem original ou a prefixada — **obrigatório:** histórico do usuário guarda o texto que a pessoa digitou; o prefixo vai só no `conteudo_usuario` do LiteLLM **e** as `imagens` no item). Bolha mostra miniatura pelas `imagens`.

Página:

- Estado `frameAnexoComposer: { instante_segundos, url, caminho_relativo, origem } | null`.
- `aoAnexarFrameDoPlayer`: lê `videoRef.current?.currentTime`; se não houver, não clica (botão já disabled). POST resolver-frame; toast no 409/502; sucesso substitui o chip (um por vez).
- `+` habilitado só com player + vídeo de entrada.
- Chip removível acima da cápsula (miniatura + ×).
- Ask enviar: passa `instante_anexo_segundos` e limpa o chip.
- Agente enviar: prefixa `prefixoFrameAnexado...` nas instruções; **não** grava PNG no turno agente; limpa o chip.

Painel: prop `chipFrameAnexo` + `aoRemoverChipFrameAnexo` para renderizar a miniatura.

- [ ] **Step 4: Rodar testes**

Run: `python -m pytest tests/test_api_chat_ask_e_historico_documento_job_transcribrothers.py -v`

Run: `npx --yes vitest run src/modulo_util_prefixo_frame_anexado_chat_ask_agente_documento_transcribrothers.test.ts src/modulo_api_chat_ask_e_historico_documento_job_transcribrothers.test.ts`

Expected: PASS (incluindo os testes antigos do Ask).

- [ ] **Step 5: Não commitar**
