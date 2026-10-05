# Design: chat Ask e Agente no documento do job

Data: 2026-10-03  
Status: aprovado

## Problema

O painel FAB «Atualizar tutorial» só dispara pipelines que reescrevem Markdown. Depois de um vídeo virar transcrição + frames + documento, o usuário precisa **conversar** com essa fonte (o que foi dito, o que já está no Markdown, qual tela ilustra) e, só quando quiser, **alterar** o documento ou gerar outro do zero.

## Decisões confirmadas

- Dois modos no mesmo chat: **Ask** e **Agente**. Interruptor no topo. Sem modo híbrido automático.
- Ask nunca grava Markdown. Não há botão «Adicionar ao documento» na bolha; quem quiser gravar troca para Agente e escreve o pedido.
- Agente reusa as rotas de regeneração já existentes (documento inteiro, sem vídeo, revisão profunda, edição parcial, notas, bug). Continua com prévia aplicar/descartar.
- Enquanto o Agente roda, o chat **permanece aberto**. A bolha mostra andamento; no fim, cartão **Ver prévia** abre a modal atual. O painel não some.
- Imagem no Ask: galeria primeiro; se não houver frame a até **5,0 s** do instante pedido, extrai PNG do vídeo com a captura manual já existente. Não insere no Markdown.
- Contexto de primeira classe no Ask: **Markdown atual** + **snapshot da transcrição** (texto e segmentos com tempo) + catálogo de frames.
- Casco: o botão FAB só abre/fecha. Aberto, o chat **encaixa à direita** (~380–420 px), **sem backdrop**. O grid vídeo + Markdown encolhe. Em viewport estreita, o painel vira folha sobre o documento.
- Histórico por job, persistido no disco do job. Recarregar a página não apaga o fio. Ask e Agente compartilham o mesmo histórico.
- Primeiro corte do Ask é **request/response** (sem SSE). Indicador de «pensando…» no cliente.

## Fora de escopo (este spec)

- Streaming token a token.
- RAG vetorial; busca é recorte do snapshot + Markdown, não índice novo.
- Botão de atalho Ask → gravar.
- Reconstruir a modal de prévia dentro da bolha.
- Chat entre jobs; o fio é de um job só.
- Alterar o motor das pipelines de regeneração (prompts, fases, preview).
- Disparar **Gerar outro formato** pelo composer (continua na toolbar).

## Design

### Superfície

O compositor sai do overlay `tb-fab-regen-wrapper` (card 400×480 + backdrop) e vira coluna à direita da `section.tb-grid-preview`.

- Fechado: botão FAB no canto, como hoje. O botão aparece se o job tiver Markdown **ou** snapshot de transcrição (hoje o FAB exige snapshot de regeneração; o Ask precisa abrir também só com documento).
- Aberto: classe no wrapper da prévia; terceira coluna (ou a única extra) com o painel. Sem `tb-fab-regen-backdrop`.
- Topo: título + `Ask | Agente`.
- Corpo: lista de mensagens (usuário / assistente / status de Agente).
- Rodapé: composer. No **Agente**, os chips atuais (Regenerar / Sem vídeo / Revisão profunda / Edição parcial, conforme o tipo do job). No **Ask**, sem chips de pipeline.
- O painel **não some** quando abrem progresso do job ou prévia de regeneração. Some ou cede só em ocupação de página inteira já existente (vídeo narrado, editor Markdown duas colunas).

Extrair o painel para `frontend/src/componente_painel_chat_ask_agente_documento_job_transcribrothers.tsx`. A página principal só encaixa o dock e continua dona dos callbacks de regeneração / `setJob` / abrir modal de prévia.

### Ask — API e módulos

`GET /api/jobs/{job_id}/chat-historico` — devolve o JSON do disco (lista vazia se ainda não houver arquivo).

`POST /api/jobs/{job_id}/chat-ask`

Corpo: só `mensagem` (texto). O servidor relê o arquivo, anexa o turno do usuário, chama o modelo, anexa a resposta, persiste.

Resposta:

- `texto` da resposta
- `citacoes`: lista de `{ tipo: "transcricao" | "markdown", rotulo, instante_segundos | null, heading | null }`
- `imagens`: lista de `{ caminho_relativo, url, instante_segundos, origem: "galeria" | "captura_sob_demanda" }`
- `historico` atualizado (o cliente não precisa de um GET extra após o POST)

O handler não muda `result_markdown` nem agenda `generating_tutorial`.

Módulos novos (um propósito cada):

1. Persistência do histórico — ler/escrever `historico_chat_ask_agente_documento_job.json` no work do job; teto de 40 mensagens (descarta as mais antigas).
2. Montagem de contexto Ask — Markdown vigente + snapshot STT + catálogo de frames (ver abaixo). Se o Markdown passar de 95_000 caracteres, manda índice de `##` + os trechos que cruzam com a pergunta (e o início do doc). Se a transcrição passar de 8_000 caracteres de texto corrido, manda o texto recortado e os segmentos cujo texto cruza com a pergunta, mais âncoras de tempo.
3. Resolução de imagem Ask — dado um instante T: escolhe no catálogo o frame com `|t - T| <= 5,0`; senão chama `capturar_frame_manual_video_tutorial_para_assets_do_job_transcribrothers`, registra em `steps_json` com `origem=chat_ask`, **não** aplica snippet no Markdown.
4. Cliente LiteLLM Ask — uma chamada de chat. A resposta do modelo é JSON `{ texto, citacoes, instantes_imagem_segundos: number[] }`. O servidor, em seguida, resolve cada instante (galeria ou captura) e monta `imagens`. System prompt: responder só com o contexto; citar tempo e heading; listar instantes só se o usuário pediu tela. Ask não emite um documento Markdown novo.

Catálogo de frames (união, sem duplicar `caminho_relativo`):

- `caminhos_frames_rel_job` do snapshot (`[segundos, rel]`)
- frames manuais em `steps_json`
- `offset_ms` no nome do PNG, quando não houver instante explícito

Sem vídeo (áudio-only, projeto em branco, vídeo ainda não no disco): a resposta de texto segue; pedido de imagem vem sem `imagens` e o texto avisa que não há tela.

Sem snapshot e sem Markdown: `409` com mensagem clara. Com só um dos dois, o Ask usa o que existir.

### Agente — sem API nova de escrita

O Enviar no modo Agente continua chamando, conforme o tipo do job e o chip:

- `POST .../regenerate-tutorial` (inteiro / revisão profunda / anexos de projeto em branco)
- `POST .../regenerate-markdown-section`
- `POST .../regenerate-notas-proposta`
- `POST .../regenerate-reproducao-bug`

Diferença de UX: não fechar o painel; gravar no histórico um turno `agente` com `job_status` e, quando `regeneracao_*_preview` estiver pronta, o cartão **Ver prévia** (`setModalPreview…(true)`).

«Documento do zero» / outro formato permanece o fluxo **Gerar outro formato** da toolbar. O Agente pode **lembrar** isso no texto da UI (chip ou hint), mas não reimplementa essa rota no composer neste spec. Pedido livre no Agente mapeia só para as regenerações acima (inteiro vs parcial vs preset), como o FAB faz hoje.

### Dados no disco do job

```
data/jobs/{id}/historico_chat_ask_agente_documento_job.json
```

Cada item: `papel` (`usuario` | `assistente` | `agente`), `modo` (`ask` | `agente`), `texto`, `citacoes`, `imagens`, `criado_em`, e no turno agente `estado` (`pedido` | `gerando` | `preview_pronta` | `falhou`) + `tipo_pipeline`.

### Erros

- Job inexistente: 404.
- Ask sem fonte (nem Markdown nem snapshot): 409; bolha de erro, histórico do usuário permanece.
- Falha LiteLLM / timeout: 502 ou 500 com detalhe; bolha de erro; não apagar turnos anteriores.
- Pedido de imagem sem vídeo: 200 com texto + `imagens: []` e aviso no `texto`.
- Captura ffmpeg falhou: resposta de texto mesmo assim; aviso de que a tela não saiu.
- Agente já em `generating_tutorial` / regeneração de seção: Enviar desabilitado (igual hoje).
- Preview descartada ou aplicada: o cartão do turno reflete o estado do job; não apaga o fio.

### Testes

Backend (TDD nos módulos, depois API):

- Escolher frame da galeria quando `|Δt| <= 5`; extrair quando `> 5` ou catálogo vazio (mock da captura).
- Montar contexto: Markdown curto vai inteiro; Markdown longo inclui índice de `##`.
- Persistência: append + teto de 40.
- API Ask: não altera `result_markdown`; devolve `citacoes` / `imagens` no formato acima.
- API Ask sem snapshot nem Markdown: 409.

Frontend:

- Painel aberto: sem backdrop; grid ganha coluna/classe de dock.
- Ask: Enviar não chama `regenerate-*`.
- Agente: Enviar não fecha o painel; ao preview pronto, o cartão dispara a modal existente.

## Ordem de implementação

1. Casco (dock + Ask | Agente + lista + composer) com Agente ligado nas rotas atuais e histórico em memória, depois persistência.
2. `POST chat-ask` + contexto Markdown/transcrição + citações (sem imagem).
3. Resolução de imagem (galeria → captura).
4. Cartão **Ver prévia** e turno de Agente no histórico persistido.

Cada passo entrega UI usável; o passo 1 já substitui o FAB atual no Agente.
