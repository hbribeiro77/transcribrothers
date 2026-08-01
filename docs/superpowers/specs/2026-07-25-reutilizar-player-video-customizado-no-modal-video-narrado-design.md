# Design: reutilizar player de vídeo customizado no modal de vídeo narrado

Data: 2026-07-25  
Status: aprovado e implementado

## Problema

O modal «Assistir vídeo narrado» usa `<video controls>` nativo. A página principal já tem um player customizado (`ComponentePlayerVideoJobControlesCustomizadosEModalAmpliarTelaMaiorTranscribrothers`) com barra de play/pause, progresso, volume e velocidade. Queremos a mesma UX de controles no modal narrado.

## Decisões confirmadas

- Abordagem **A**: estender o player existente com props opcionais (não extrair barra nem duplicar componente).
- No modal narrado: **só a barra de controles customizada**, **sem** overlay de «tela maior».
- Manter o toggle **«Legendas no vídeo»** (track VTT sobre o MP4 narrado).
- Sem capturar frame no modal narrado (`exibirBotaoCapturarFrame={false}`).

## Contexto técnico atual

| Superfície | Fonte do vídeo | Controles |
|---|---|---|
| Página principal | `/api/jobs/{id}/video` (vídeo fonte) | Player customizado + tela maior + capturar frame |
| Modal narrado | URL do MP4 narrado (`urlVideoMp4`) | `<video controls>` + track VTT |

O player customizado hoje **fixa** `src` a partir de `jobId` e sempre monta o fluxo de «tela maior». O modal narrado depende de `videoRef` para seek ao clicar na cue e para ligar/desligar `textTracks`.

## Design

### 1. Novas props no player (opcionais, retrocompatíveis)

Arquivo: `componente_player_video_job_controles_customizados_e_modal_ampliar_tela_maior_transcribrothers.tsx`

| Prop | Default | Comportamento |
|---|---|---|
| `urlVideoSrc?: string` | `/api/jobs/{jobId}/video` | Override do `src` do(s) `<video>` |
| `exibirBotaoTelaMaior?: boolean` | `true` | Se `false`: não renderiza botão flutuante, não passa `aoSolicitarTelaMaior` à barra, não monta portal de tela maior |
| `faixaLegendas?: React.ReactNode` | `undefined` | Conteúdo filho do `<video>` inline (ex.: `<track … />`) |
| `keyVideo?: string \| number` | `undefined` | Encaminhado como `key` do `<video>` para forçar remount (cache-bust VTT/MP4) |
| `classNameEnvoltorio?: string` | `undefined` | Classe extra no wrapper (layout do modal) |
| `preloadVideo?: string` | `"auto"` (inline atual) | Permite `"metadata"` no modal se útil |

Página principal **não muda** comportamento além de continuar nos defaults.

### 2. Integração no modal narrado

Arquivo: `componente_modal_assistir_video_narrado_com_legendas_vtt_e_downloads_transcribrothers.tsx`

- Substituir o bloco `<video controls>…</video>` pelo player customizado.
- Props relevantes:
  - `jobId` (já disponível; necessário pela API do componente; `urlVideoSrc` prevalece sobre a URL default).
  - `urlVideoSrc={urlVideoMp4}`
  - `videoRef={videoRef}` (mesmo ref; seek das cues e `textTracks` seguem iguais).
  - `exibirBotaoTelaMaior={false}`
  - `exibirBotaoCapturarFrame={false}`
  - `faixaLegendas` = `<track>` atual quando houver URL VTT.
  - `keyVideo` = combinação já usada (`urlVideoMp4` + versão de cache do VTT).
- Manter o toggle «Legendas no vídeo» e o `useEffect` que altera `textTracks[].mode`.
- Ajustar CSS do modal (`estilos_css_modal_assistir_video_narrado_…`) para o player ocupar a área (`tb-modal-assistir-video-narrado-player-area`) sem controles nativos; importar CSS do player se ainda não estiver global.

### 3. Fora de escopo

- Mudar UX do player na página principal.
- Extrair `BarraControles` para pacote separado.
- Capturar frame a partir do vídeo narrado.
- Overlay «tela maior» dentro do modal narrado.
- Alterações de backend.

### 4. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| `jobId` null no modal | Modal já exige job; só montar player quando `jobId` e `urlVideoMp4` existirem (como hoje o `<video>`). |
| Track VTT não aparece | `faixaLegendas` como filho do mesmo `<video>` ligado ao `videoRef`; manter cache-bust e effect de `mode`. |
| Seek da lista de cues quebra | Continuar usando o mesmo `videoRef` preenchido pelo callback `atribuirRefVideoInline` do player. |
| Metadata de duração do job (fonte) no narrado | Com `urlVideoSrc` override, duração vem do elemento/metadata do MP4 narrado; não depender de `duracao_video_segundos` do vídeo fonte (passar `null` / omitir no modal). |

### 5. Verificação manual

1. Página principal: player, tela maior e capturar frame inalterados.
2. Modal narrado: controles customizados (play, barra, volume, velocidade); sem botão/overlay de tela maior; sem capturar frame.
3. Toggle «Legendas no vídeo» liga/desliga a faixa.
4. Clique em cue / «Ir» faz seek no vídeo narrado.
5. Troca de VTT/MP4 (regeneração) remonta o vídeo e as legendas corretamente.

## Critério de pronto

Modal narrado usa o mesmo componente de player da página, com URL do MP4 narrado, barra customizada, legendas VTT via toggle, sem segundo overlay de tela maior, e a página principal permanece com o comportamento atual.
