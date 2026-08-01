# Reutilizar player customizado no modal narrado — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modal de vídeo narrado usa o mesmo player customizado da página principal, com URL do MP4 narrado, track VTT e sem overlay de tela maior.

**Architecture:** Estender o player existente com props opcionais retrocompatíveis; plugar no modal narrado substituindo `<video controls>`.

**Tech Stack:** React + TypeScript (frontend Transcribrothers)

## Global Constraints

- pt-BR na UI e comunicação
- Não alterar comportamento default do player na página principal
- Spec: `docs/superpowers/specs/2026-07-25-reutilizar-player-video-customizado-no-modal-video-narrado-design.md`

---

## Task 1: Props no player

- [x] Adicionar `urlVideoSrc`, `exibirBotaoTelaMaior`, `faixaLegendas`, `keyVideo`, `classNameEnvoltorio`, `preloadVideo`
- [x] Condicionar botão flutuante, barra e portal de tela maior
- [x] Usar `urlVideoSrc` (fallback URL do job) nos dois `<video>`

## Task 2: Modal narrado

- [x] Importar player + CSS do player
- [x] Substituir `<video controls>` pelo componente com props da spec
- [x] Ajustar CSS da área do player para layout flex (vídeo + barra)

## Task 3: Verificação

- [x] Conferir tipos/lints nos arquivos tocados
- [x] Atualizar status da spec para aprovado/implementado
