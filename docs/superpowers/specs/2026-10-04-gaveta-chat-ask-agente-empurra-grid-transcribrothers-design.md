# Design: gaveta do chat Ask/Agente que empurra o grid

Data: 2026-10-04  
Status: aprovado  
Complementa: `docs/superpowers/specs/2026-10-03-chat-ask-e-agente-documento-job-transcribrothers-design.md`

## Problema

O chat Ask/Agente já existe, mas o casco ainda é um FAB (`↻`) + card flutuante com título de regeneração. Isso serve para disparar pipeline, não para conversar. O alvo visual é a gaveta do Excalibrothers (Ask | Agente no composer, `+`, Ocultar chat), sem tapar o vídeo nem o Markdown.

## Decisões confirmadas

- **A — gaveta que empurra o grid.** Sem FAB. Sem backdrop. O grid vídeo + Markdown encolhe.
- Interruptor na **toolbar do Markdown** (`tb-md-header-toolbar`), família dos ícones já existentes.
- Título da gaveta: **Chat**. Some o «Atualizar tutorial» e o `(i)` de pixels.
- Ask | Agente sobe para a **faixa do composer** (esquerda). **Limpar** à direita, com confirmação; apaga o fio deste job no disco.
- Composer em cápsula: `+` · campo · enviar, nos dois modos (não só no projeto em branco).
- `+` em job com vídeo: anexa o **frame do instante do player**. Galeria se `|Δt| ≤ 5,0 s`; senão captura manual já usada pelo Ask. **Não** insere no Markdown. **Não** usa `POST .../capturar-frame-manual-video-tutorial` (essa rota devolve snippet para o documento).
- `+` no projeto em branco: menu atual Texto / Imagem / Arquivo.
- Ask, Agente, histórico, prévia e rotas `chat-ask` / `regenerate-*` permanecem. Este spec não mexe no motor das pipelines.
- Recarregar a página: fio permanece; gaveta **começa fechada**.
- Sem **Desfazer** (no Excalibrothers isso desfaz o desenho; aqui o equivalente do Agente já é descartar a prévia).

## Fora de escopo

- Enviar pixels do frame ao LiteLLM (Ask continua texto; o PNG aparece na bolha / chip).
- Streaming token a token.
- Chat entre jobs.
- Backdrop, overlay tipo Configurações, ou FAB residual.
- Botão Ask → gravar no Markdown.
- Reconstruir a modal de prévia dentro da bolha.
- `Gerar outro formato` pelo composer.

## Superfície

### Fechado

Some o `createPortal` de `tb-fab-principal`. No lugar, um botão `tb-btn-md-toolbar-icone` na toolbar do frame do documento:

- `aria-label` / `title`: **Abrir chat**
- Visível quando `job_pode_abrir_chat_ask_agente` (regra atual: Markdown ou snapshot)

### Aberto

O wrapper do preview continua flex (`tb-chat-ask-agente-dock-wrapper`):

- Coluna esquerda: `section.tb-grid-preview` (encolhe).
- Coluna direita: `<aside>` da gaveta, `flex-basis` ~400 px (`min(400px, 36vw)`).
- Gaveta com altura da faixa de preview, encostada na direita da página: borda reta no lado externo, sem `border-radius` de card nem sombra de FAB.
- Sem `tb-fab-regen-backdrop` e sem portal no `body`.
- Botão da toolbar: estado ativo + **Ocultar chat**.
- Cabeçalho da gaveta: **Chat** + fechar (mesmo efeito de ocultar).
- Em viewport estreita (`max-width` ≤ 900 px): a gaveta vira folha sobre o documento, ainda **sem** escurecer.

A gaveta **não some** quando abrem progresso do job ou a modal de prévia. Some ou cede só nas ocupações de página inteira já existentes (vídeo narrado, editor Markdown duas colunas).

### Composer

Faixa acima da cápsula:

- Esquerda: `Ask | Agente` (`role="tablist"`), visual em pílula já usado.
- Direita: **Limpar** (desabilitado se o fio estiver vazio ou se Ask/Agente estiver enviando).

Abaixo: cápsula `+` · textarea · enviar.

No **Agente**, os chips atuais (Regenerar / Sem vídeo / Revisão profunda / Edição parcial, conforme o tipo do job) ficam **acima** dessa faixa. Placeholder: Ask = «Pergunte sobre o documento…»; Agente = o texto atual do campo de instruções.

## Limpar

Diálogo de confirmação já usado no app (`ComponenteDialogoConfirmacaoAcaoDestrutivaOverlayTranscribrothers`):

- Título: **Limpar o chat deste documento?**
- Corpo: o histórico Ask e Agente deste job some. Isso não altera o Markdown.
- Confirmar: **Limpar** · Cancelar: **Cancelar**

`DELETE /api/jobs/{job_id}/chat-historico` grava lista vazia com `gravar_historico_chat_ask_agente_no_work_transcribrothers` (já existe). Job inexistente: 404. Sucesso: `{ "historico": [] }`. O cliente esvazia a lista na hora.

Limpar **não** apaga frames capturados pelo Ask em `steps_json` nem PNGs em `assets/`.

## `+` — frame do instante do player

O cliente lê `videoRef.current.currentTime`. Sem vídeo no disco / áudio-only / player ausente: o `+` fica desabilitado e o `title` é «Não há vídeo para anexar um frame.» (sem toast — o botão não dispara clique).

Fluxo:

1. `POST /api/jobs/{job_id}/chat-ask-resolver-frame` com `{ "instante_segundos": number }`.
2. Servidor chama `resolver_imagens_chat_ask_por_instantes_transcribrothers` (Δt ≤ 5,0 s → galeria; senão captura com `origem=chat_ask`). Mesma mescla segura de `steps_json` do `POST chat-ask` (só frames novos, sem reescrever o JSON inteiro).
3. Resposta: `{ caminho_relativo, url, instante_segundos, origem }` ou 409/502 com detalhe. **Não** devolve `snippet_markdown`. **Não** altera `result_markdown`.

O composer mostra um chip/miniatura removível (um frame por vez neste corte; novo `+` substitui o anterior).

No **Ask**, `POST chat-ask` ganha campo opcional `instante_anexo_segundos`. Se vier:

- o servidor resolve de novo (ou reusa o caminho já no catálogo) e grava `imagens` no turno do **usuário**;
- o texto enviado ao modelo inclui uma linha `Frame anexado em {MM:SS}.`;
- a bolha do usuário mostra a miniatura.

No **Agente**, o chip não chama `chat-ask`. Ao enviar, o cliente prefixa nas instruções `Frame anexado em {MM:SS}.` (o modelo da pipeline já vê o Markdown/catálogo). A miniatura pode ficar só no composer até o envio; o turno `agente` no histórico não precisa do PNG neste corte.

## Erros

- Job inexistente em DELETE ou resolver-frame: 404.
- Resolver-frame sem vídeo: 409; chip não entra; toast com o detalhe.
- Captura ffmpeg falhou: 502; toast; composer inalterado.
- DELETE com Ask/Agente em voo: o botão Limpar já está desabilitado; se a corrida acontecer, o DELETE vence no disco e o cliente aplica `{ historico: [] }` só se o DELETE tiver 200 — um Ask que grave depois reaparece no próximo GET (aceitável neste corte).
- Demais erros do Ask/Agente: iguais ao spec de 2026-10-03.

## Testes

Backend:

- `DELETE chat-historico` em job com itens → arquivo com `itens: []`; 404 se o job não existe.
- `POST chat-ask-resolver-frame` com catálogo a ≤ 5,0 s → origem `galeria`, `result_markdown` intacto.
- `POST chat-ask-resolver-frame` sem frame próximo → origem `captura_sob_demanda`; `steps_json` só ganha o registro novo (mesmo critério do Ask).
- `POST chat-ask` com `instante_anexo_segundos` → turno do usuário no JSON tem `imagens` com esse instante.

Frontend (Vitest no casco / helpers; sem E2E obrigatório):

- Aberto: sem FAB no documento; toolbar tem **Ocultar chat**; grid tem a classe de dock; sem backdrop.
- Fechado: toolbar tem **Abrir chat**; gaveta ausente.
- Ask | Agente na faixa do composer, não no cabeçalho.
- Limpar com lista vazia não chama DELETE.

## Ordem de implementação

1. Casco (toolbar, gaveta que empurra, composer cápsula, sumir FAB) com Ask/Agente já ligados.
2. `DELETE chat-historico` + Limpar com confirmação.
3. `POST chat-ask-resolver-frame` + chip do `+` + `instante_anexo_segundos` no Ask.

Cada passo deixa a UI usável. O passo 1 já substitui o FAB.
