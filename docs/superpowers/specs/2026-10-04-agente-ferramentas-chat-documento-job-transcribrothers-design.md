# Design: Agente do chat com ferramentas (não dispara pipeline no Enviar)

Data: 2026-10-04  
Status: aprovado  
Complementa: `docs/superpowers/specs/2026-10-03-chat-ask-e-agente-documento-job-transcribrothers-design.md`

## Problema

No modo Agente, Enviar chama `regenerate-*` na hora e abre a modal **Processando**. Um pedido conversacional («bola um texto, pega o frame, onde encaixo?») vira revisão profunda ou regeneração inteira se o chip estiver ativo. Os chips Sem vídeo / Revisão profunda / Edição parcial são modos de envio, não ferramentas.

## Decisões

- Enviar no Agente **sem chip** vai para `POST /api/jobs/{id}/chat-agente`: uma chamada LiteLLM, mesmo contexto do Ask (Markdown + transcrição + frames).
- A resposta é JSON com `texto`, `citacoes`, `instantes_imagem_segundos` e `ferramentas`.
- **capturar_frame** (via instantes) executa no servidor, como no Ask. Não grava o Markdown.
- **edicao_parcial**, **revisao_profunda** e **sem_video** **não executam** no turno. Viram `proposta_ferramenta` no histórico. A bolha mostra um botão («Aplicar edição parcial», «Disparar revisão profunda», «Disparar sem vídeo»). Só o clique dispara a rota já existente. Continua com prévia aplicar/descartar.
- Chip selecionado envia `forcar_ferramenta`. O modelo deve propor essa tool. Se não propor, o backend injeta a proposta com a mensagem do usuário como `instrucoes`. Chip **não** dispara pipeline no Enviar.
- Clique no chip só marca a tool. Sem vídeo **não** preenche mais o textarea com o template longo.
- Pedido nascido no chat **não** abre a modal Processando. Progresso na bolha; **Ver prévia** no fim.
- Ask não muda: continua só leitura, sem `ferramentas`.
- Modelo do chat: o mesmo `litellm_model` da gaveta.

## Fora de escopo

- Tool calling nativo do LiteLLM (`tools` / `tool_calls`).
- Loop multi-turno de ferramentas no servidor.
- O modelo aplicar ou descartar a prévia.
- Gerar outro formato pelo composer.
- Novas pipelines.

## API

`POST /api/jobs/{id}/chat-agente`

Corpo: `mensagem`, `instante_anexo_segundos?`, `litellm_model?`, `forcar_ferramenta?` (`edicao_parcial` | `revisao_profunda` | `sem_video`).

Resposta: igual ao Ask + `proposta_ferramenta` (`nome`, `titulo_secao_heading`, `instrucoes`) no item do assistente/agente e no corpo.

Não altera `result_markdown`. Não agenda `generating_tutorial`.

Job sem Markdown e sem snapshot: `409`, igual ao Ask.

## Histórico

Campo opcional `proposta_ferramenta` no item JSON. Itens antigos sem o campo continuam válidos.

## Testes

- Parse das ferramentas; allowlist; injeção se `forcar_ferramenta` vier e o modelo omitir.
- API: 200, Markdown intacto, proposta persistida; 404/409.
- Frontend: Enviar no Agente sem chip chama `chat-agente`, não `regenerate-*`.
