# Design: modelo do chat Ask/Agente independente da pipeline

Data: 2026-10-04  
Status: aprovado  
Complementa: `docs/superpowers/specs/2026-10-03-chat-ask-e-agente-documento-job-transcribrothers-design.md`

## Problema

Ask usa o `litellm_model` congelado no job; Agente usa o select de Configurações (o mesmo das pipelines). A gaveta não mostra quem responde.

## Decisões

- Ask e Agente compartilham **um** modelo do chat.
- Esse modelo é **independente** do select «Modelo (LiteLLM)» das pipelines.
- Escolha na própria gaveta: botão com o slug curto ao lado de Ask | Agente; clique abre menu; o escolhido fica visível.
- Persistência: `localStorage` do navegador (todos os jobs). Primeira vez: primeiro modelo de chat da lista (sem slug TTS).
- Lista do menu: só modelos de chat (exclui `-tts` / ElevenLabs TTS).
- `POST /chat-ask` aceita `litellm_model` opcional; se vier, prevalece sobre o do job.
- Pedidos de Agente nascidos no chat enviam esse modelo (não o das Configurações).
- Pipelines disparadas fora do chat não mudam.

## Fora de escopo

- Mostrar o modelo em cada bolha do histórico.
- Dois modelos dentro do Agente (planejador vs escritor).
- Sync do select de Configurações com o do chat.
