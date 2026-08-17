import type * as React from "react";
import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { calcularRetanguloObjectFitContainVideoNoElementoUiTranscribrothers } from "./modulo_util_calcular_retangulo_object_fit_contain_video_no_elemento_ui_transcribrothers.ts";
import { formatarSegundosComoMmSsTranscribrothers } from "./modulo_util_rotulos_fase_pipeline_status_portugues_ui_transcribrothers.ts";
import { tentarDescobrirDuracaoVideoPorSeekAoFimNavegadorTranscribrothers } from "./modulo_util_tentar_descobrir_duracao_video_por_seek_ao_fim_navegador_transcribrothers.ts";

/** Lê duração do `<video>` (metadata ou intervalo seekable). */
function lerDuracaoSegundosElementoVideoPlayerTranscribrothers(video: HTMLVideoElement): number {
  if (Number.isFinite(video.duration) && video.duration > 0) return video.duration;
  const seekable = video.seekable;
  if (seekable.length > 0) {
    const fim = seekable.end(seekable.length - 1);
    if (Number.isFinite(fim) && fim > 0) return fim;
  }
  return 0;
}

type PropsComponentePlayerVideoJobControlesCustomizadosEModalAmpliarTelaMaiorTranscribrothers = {
  jobId: string;
  videoRef: React.RefObject<HTMLVideoElement | null>;
  /** Quando o job já tem `steps_json.duracao_video_segundos` (ffprobe no servidor). */
  duracaoVideoSegundosDoJob?: number | null;
  classNameVideo?: string;
  /** Override do `src` (ex.: MP4 narrado). Default: `/api/jobs/{jobId}/video`. */
  urlVideoSrc?: string;
  /** Se false, esconde botão flutuante, ação na barra e portal de tela maior. Default: true. */
  exibirBotaoTelaMaior?: boolean;
  /** Filhos do `<video>` inline (ex.: `<track>` VTT). */
  faixaLegendas?: React.ReactNode;
  /** `key` do `<video>` inline para forçar remount (cache-bust). */
  keyVideo?: string | number;
  /** Classe extra no wrapper `.tb-video-player-envoltorio`. */
  classNameEnvoltorio?: string;
  /** `preload` do `<video>` inline. Default: `"auto"`. */
  preloadVideo?: "none" | "metadata" | "auto";
  /** Segmentos de legenda sob a barra de progresso (modal narrado). */
  faixaCuesTimeline?: SegmentoFaixaCuesTimelinePlayerVideoTranscribrothers[];
  indiceCueAtivaFaixaTimeline?: number;
  aoClicarSegmentoFaixaCuesTimeline?: (indice: number) => void;
  aoArrastarSegmentoFaixaCuesTimeline?: (indice: number, novoInicioSegundos: number) => void;
  /**
   * Quando true, a barra mostra ícone de pausa mesmo com `video.paused`
   * (ex.: narração WAV auxiliar com o vídeo só no frame).
   */
  forcarUiComoTocando?: boolean;
  /** Substitui o play/pause nativo do `<video>` (modal narrado com áudio auxiliar). */
  aoAlternarPlayPauseCustomizado?: () => void;
  /**
   * Timeline virtual na barra (tempo/duração/seek) sem depender só do `currentTime`/`duration`
   * reais do `<video>`. Usado no preview de recorte e quando a timeline narrada (cues)
   * é mais longa que o MP4 ainda não remuxado.
   */
  timelineVirtualUi?: {
    tempoAtualSegundos: number;
    duracaoSegundos: number;
    aoAlterarTempoPelaBarra: (tempoSegundos: number) => void;
  } | null;
  /** Conteúdo sobreposto à área do vídeo (ex.: legenda por overlay no preview de recorte). */
  overlaySobreVideo?: React.ReactNode;
  /**
   * Conteúdo opcional na mesma linha do play/tempo/volume
   * (ex.: recorte início/fim na modal do vídeo original).
   */
  conteudoExtraNaLinhaAcoesControles?: React.ReactNode;
  exibirBotaoCapturarFrame?: boolean;
  capturandoFrame?: boolean;
  /** Recebe o instante atual do vídeo ativo (inline ou modal em tela maior). */
  aoCapturarFrameNoInstanteAtual?: (timestampSegundos: number) => void;
  aoVideoIndisponivelParaCapturaFrame?: () => void;
  /** Quando a duração é descoberta (API ou metadata do `<video>`), para atualizar o job na página. */
  onDuracaoVideoConhecidaSegundos?: (duracaoSegundos: number) => void;
};

const VELOCIDADES_REPRODUCAO_VIDEO_TRANSCRIBROTHERS = [0.75, 1, 1.25, 1.5, 2] as const;

function IconePlayVideoTranscribrothers() {
  return (
    <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden>
      <path fill="currentColor" d="M8 5v14l11-7z" />
    </svg>
  );
}

function IconePauseVideoTranscribrothers() {
  return (
    <svg viewBox="0 0 24 24" width="20" height="20" aria-hidden>
      <path fill="currentColor" d="M6 5h4v14H6V5zm8 0h4v14h-4V5z" />
    </svg>
  );
}

function IconeVolumeAltoVideoTranscribrothers() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden>
      <path
        fill="currentColor"
        d="M3 10v4h4l5 5V5L7 10H3zm13.5 2a4.5 4.5 0 00-2.54-4.06l-.91 1.41A2.96 2.96 0 0115.5 12c0 .96-.46 1.81-1.17 2.35l.91 1.41A4.5 4.5 0 0016.5 12zm2.82-6.36l-.9 1.41A6.96 6.96 0 0119.5 12a6.96 6.96 0 01-1.08 3.95l.9 1.41A8.46 8.46 0 0021.5 12a8.46 8.46 0 00-2.18-6.36z"
      />
    </svg>
  );
}

function IconeVolumeMudoVideoTranscribrothers() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden>
      <path
        fill="currentColor"
        d="M16.5 12a4.5 4.5 0 00-2.54-4.06l-.91 1.41A2.96 2.96 0 0115.5 12c0 .96-.46 1.81-1.17 2.35l.91 1.41A4.5 4.5 0 0016.5 12zM3 10v4h4l5 5V5L7 10H3zm14.07-1.36l-1.41-1.41L3 18.59 4.41 20 16.07 8.34z"
      />
    </svg>
  );
}

function IconeAmpliarVideoTelaMaiorTranscribrothers() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M8 3H5a2 2 0 00-2 2v3m18 0V5a2 2 0 00-2-2h-3m0 18h3a2 2 0 002-2v-3M3 16v3a2 2 0 002 2h3"
      />
    </svg>
  );
}

function IconeCapturarFrameVideoTranscribrothers() {
  return (
    <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M4 8h4l2-2h4l2 2h4v10H4V8z"
      />
      <circle cx="12" cy="13" r="3" fill="none" stroke="currentColor" strokeWidth="2" />
    </svg>
  );
}

export type SegmentoFaixaCuesTimelinePlayerVideoTranscribrothers = {
  inicioSegundos: number;
  fimSegundos: number;
  /** Texto curto para tooltip (ex.: início da legenda). */
  rotulo?: string;
  /**
   * Duração do áudio atual (WAV gravado ou prévia TTS) em segundos.
   * `null`/omitido = sem medida (ex.: texto editado ainda sem «Ouvir»).
   */
  duracaoAudioSegundos?: number | null;
  /** Preenchimento vem de prévia TTS do texto editado (ainda não aplicada ao vídeo). */
  audioEhPreview?: boolean;
  /** Texto difere do narrado e ainda não há áudio medido para o texto atual. */
  aguardandoAudioAtual?: boolean;
  /** Trecho só com vídeo — sem fala TTS no preview/export. */
  semNarracao?: boolean;
};

type BarraControlesPlayerVideoTranscribrothersProps = {
  video: HTMLVideoElement | null;
  duracaoSegundos: number;
  tempoAtualSegundos: number;
  pausado: boolean;
  mudo: boolean;
  volume: number;
  velocidadeReproducao: number;
  arrastandoBarraProgresso: boolean;
  aoAlternarPlayPause: () => void;
  aoAlternarMudo: () => void;
  aoAlterarVolume: (volume: number) => void;
  aoIniciarArrastarBarra: () => void;
  aoFinalizarArrastarBarra: () => void;
  aoAlterarTempoPelaBarra: (tempoSegundos: number) => void;
  aoAlternarVelocidade: () => void;
  aoSolicitarTelaMaior?: () => void;
  exibirBotaoCapturarFrame?: boolean;
  capturandoFrame?: boolean;
  aoCapturarFrame?: () => void;
  compacto?: boolean;
  /** Trechos de legenda sob a barra de progresso (ex.: modal de vídeo narrado). */
  faixaCuesTimeline?: SegmentoFaixaCuesTimelinePlayerVideoTranscribrothers[];
  indiceCueAtivaFaixaTimeline?: number;
  aoClicarSegmentoFaixaCuesTimeline?: (indice: number) => void;
  /** Arrastar segmento na faixa: novo início desejado em segundos (pai aplica limites). */
  aoArrastarSegmentoFaixaCuesTimeline?: (indice: number, novoInicioSegundos: number) => void;
  conteudoExtraNaLinhaAcoesControles?: React.ReactNode;
};

type ArrasteFaixaCueTimelineRefTranscribrothers = {
  indice: number;
  pointerId: number;
  clientXInicial: number;
  inicioCueSegundos: number;
  larguraFaixaPx: number;
  moveu: boolean;
};

function ComponenteFaixaCuesTimelineAbaixoBarraProgressoTranscribrothers({
  duracaoSegundos,
  segmentos,
  indiceAtiva,
  aoClicarSegmento,
  aoArrastarSegmento,
}: {
  duracaoSegundos: number;
  segmentos: SegmentoFaixaCuesTimelinePlayerVideoTranscribrothers[];
  indiceAtiva: number;
  aoClicarSegmento?: (indice: number) => void;
  aoArrastarSegmento?: (indice: number, novoInicioSegundos: number) => void;
}) {
  const faixaRef = useRef<HTMLDivElement | null>(null);
  const arrasteRef = useRef<ArrasteFaixaCueTimelineRefTranscribrothers | null>(null);
  const [indiceArrastando, setIndiceArrastando] = useState<number | null>(null);

  useEffect(() => {
    const aoPointerMove = (evento: PointerEvent) => {
      const arraste = arrasteRef.current;
      if (!arraste || evento.pointerId !== arraste.pointerId) return;
      if (!(arraste.larguraFaixaPx > 0) || !(duracaoSegundos > 0)) return;
      const deltaPx = evento.clientX - arraste.clientXInicial;
      if (Math.abs(deltaPx) > 3) arraste.moveu = true;
      const deltaSegundos = (deltaPx / arraste.larguraFaixaPx) * duracaoSegundos;
      aoArrastarSegmento?.(arraste.indice, arraste.inicioCueSegundos + deltaSegundos);
    };

    const aoPointerUp = (evento: PointerEvent) => {
      const arraste = arrasteRef.current;
      if (!arraste || evento.pointerId !== arraste.pointerId) return;
      const { indice, moveu } = arraste;
      arrasteRef.current = null;
      setIndiceArrastando(null);
      if (!moveu) {
        aoClicarSegmento?.(indice);
      }
    };

    window.addEventListener("pointermove", aoPointerMove);
    window.addEventListener("pointerup", aoPointerUp);
    window.addEventListener("pointercancel", aoPointerUp);
    return () => {
      window.removeEventListener("pointermove", aoPointerMove);
      window.removeEventListener("pointerup", aoPointerUp);
      window.removeEventListener("pointercancel", aoPointerUp);
    };
  }, [aoArrastarSegmento, aoClicarSegmento, duracaoSegundos]);

  if (!(duracaoSegundos > 0) || segmentos.length === 0) return null;

  return (
    <div
      ref={faixaRef}
      className="tb-video-player-faixa-cues"
      role="list"
      aria-label="Trechos das legendas no tempo do vídeo — arraste para deslocar"
    >
      {segmentos.map((seg, indice) => {
        const inicio = Math.max(0, Math.min(seg.inicioSegundos, duracaoSegundos));
        const fim = Math.max(inicio, Math.min(seg.fimSegundos, duracaoSegundos));
        const duracaoCue = fim - inicio;
        const larguraPct = (duracaoCue / duracaoSegundos) * 100;
        const esquerdaPct = (inicio / duracaoSegundos) * 100;
        if (!(larguraPct > 0)) return null;
        const ativa = indice === indiceAtiva;
        const arrastando = indiceArrastando === indice;
        const durAudio =
          typeof seg.duracaoAudioSegundos === "number" &&
          Number.isFinite(seg.duracaoAudioSegundos) &&
          seg.duracaoAudioSegundos >= 0
            ? seg.duracaoAudioSegundos
            : null;
        const ocupacaoPct =
          durAudio !== null && duracaoCue > 0 ? (durAudio / duracaoCue) * 100 : null;
        const fillPct =
          ocupacaoPct === null ? 0 : Math.max(0, Math.min(100, ocupacaoPct));
        const estourou = ocupacaoPct !== null && ocupacaoPct > 100.5;
        const aguardando = Boolean(seg.aguardandoAudioAtual) && ocupacaoPct === null;

        const semNarracao = Boolean(seg.semNarracao);
        let title = seg.rotulo?.trim() || `Legenda ${indice + 1}`;
        title = `${title}\nArraste para deslocar · clique para reproduzir`;
        if (semNarracao) {
          title = `${title}\nSem narração — só o trecho de tela (sem fala)`;
        } else if (aguardando) {
          title = `${title}\nTexto editado — use «Ouvir» para medir a nova fala neste slot.`;
        } else if (ocupacaoPct !== null && durAudio !== null) {
          const origem = seg.audioEhPreview ? "prévia TTS" : "áudio gravado";
          title =
            `${title}\n${origem}: ${durAudio.toFixed(1)}s / cue ${duracaoCue.toFixed(1)}s` +
            ` (${Math.round(ocupacaoPct)}%)` +
            (estourou ? " — fala maior que o slot" : "");
        }

        return (
          <button
            key={`faixa-cue-${indice}`}
            type="button"
            role="listitem"
            className={
              "tb-video-player-faixa-cues-segmento" +
              (ativa ? " tb-video-player-faixa-cues-segmento--ativa" : "") +
              (arrastando ? " tb-video-player-faixa-cues-segmento--arrastando" : "") +
              (semNarracao ? " tb-video-player-faixa-cues-segmento--sem-narracao" : "") +
              (seg.audioEhPreview && !semNarracao
                ? " tb-video-player-faixa-cues-segmento--preview"
                : "") +
              (aguardando && !semNarracao
                ? " tb-video-player-faixa-cues-segmento--aguardando"
                : "") +
              (estourou && !semNarracao ? " tb-video-player-faixa-cues-segmento--estouro" : "")
            }
            style={{ left: `${esquerdaPct}%`, width: `${larguraPct}%` }}
            title={title}
            aria-label={
              ativa
                ? `Legenda ${indice + 1} (selecionada) — clique de novo para reproduzir ou pausar; arraste para deslocar`
                : `Legenda ${indice + 1} — clique para selecionar; arraste para deslocar`
            }
            aria-current={ativa ? "true" : undefined}
            onPointerDown={(evento) => {
              if (evento.button !== 0) return;
              const faixa = faixaRef.current;
              if (!faixa || !aoArrastarSegmento) {
                return;
              }
              evento.preventDefault();
              evento.stopPropagation();
              const largura = faixa.getBoundingClientRect().width;
              arrasteRef.current = {
                indice,
                pointerId: evento.pointerId,
                clientXInicial: evento.clientX,
                inicioCueSegundos: seg.inicioSegundos,
                larguraFaixaPx: largura,
                moveu: false,
              };
              setIndiceArrastando(indice);
              try {
                evento.currentTarget.setPointerCapture(evento.pointerId);
              } catch {
                /* alguns navegadores falham se o alvo sumir */
              }
            }}
            onClick={(evento) => {
              // Clique sem drag é tratado no pointerup (evita play ao soltar o arraste).
              if (aoArrastarSegmento) {
                evento.preventDefault();
                return;
              }
              aoClicarSegmento?.(indice);
            }}
          >
            {ocupacaoPct !== null ? (
              <span
                className="tb-video-player-faixa-cues-ocupacao"
                style={{ width: `${fillPct}%` }}
                aria-hidden
              />
            ) : null}
            <span className="tb-video-player-faixa-cues-numero" aria-hidden>
              {indice + 1}
            </span>
          </button>
        );
      })}
    </div>
  );
}

function BarraControlesPlayerVideoTranscribrothers({
  video,
  duracaoSegundos,
  tempoAtualSegundos,
  pausado,
  mudo,
  volume,
  velocidadeReproducao,
  arrastandoBarraProgresso,
  aoAlternarPlayPause,
  aoAlternarMudo,
  aoAlterarVolume,
  aoIniciarArrastarBarra,
  aoFinalizarArrastarBarra,
  aoAlterarTempoPelaBarra,
  aoAlternarVelocidade,
  aoSolicitarTelaMaior,
  exibirBotaoCapturarFrame = false,
  capturandoFrame = false,
  aoCapturarFrame,
  compacto = false,
  faixaCuesTimeline,
  indiceCueAtivaFaixaTimeline = -1,
  aoClicarSegmentoFaixaCuesTimeline,
  aoArrastarSegmentoFaixaCuesTimeline,
  conteudoExtraNaLinhaAcoesControles = null,
}: BarraControlesPlayerVideoTranscribrothersProps) {
  const duracaoValida = Number.isFinite(duracaoSegundos) && duracaoSegundos > 0;
  const maxBarra = duracaoValida ? duracaoSegundos : 0;
  const valorBarra = arrastandoBarraProgresso
    ? tempoAtualSegundos
    : Math.min(tempoAtualSegundos, maxBarra || tempoAtualSegundos);
  const temFaixaCues = Boolean(faixaCuesTimeline && faixaCuesTimeline.length > 0);

  return (
    <div
      className={`tb-video-player-controles${compacto ? " tb-video-player-controles--compacto" : ""}${
        temFaixaCues ? " tb-video-player-controles--com-faixa-cues" : ""
      }`}
      onClick={(evento) => evento.stopPropagation()}
      onDoubleClick={(evento) => evento.stopPropagation()}
    >
      <div
        className={
          "tb-video-player-controles-linha-acoes" +
          (conteudoExtraNaLinhaAcoesControles
            ? " tb-video-player-controles-linha-acoes--com-extra"
            : "")
        }
      >
        <button
          type="button"
          className="tb-video-player-btn-icone"
          aria-label={pausado ? "Reproduzir" : "Pausar"}
          title={pausado ? "Reproduzir" : "Pausar"}
          disabled={!video}
          onClick={aoAlternarPlayPause}
        >
          {pausado ? <IconePlayVideoTranscribrothers /> : <IconePauseVideoTranscribrothers />}
        </button>

        <span className="tb-video-player-tempo" aria-live="off">
          {formatarSegundosComoMmSsTranscribrothers(tempoAtualSegundos)}
          <span className="tb-video-player-tempo-separador">/</span>
          {duracaoValida
            ? formatarSegundosComoMmSsTranscribrothers(duracaoSegundos)
            : video
              ? "…"
              : "0:00"}
        </span>

        {conteudoExtraNaLinhaAcoesControles ? (
          <div className="tb-video-player-controles-extra">{conteudoExtraNaLinhaAcoesControles}</div>
        ) : null}

        <div className="tb-video-player-controles-grupo-direita">
          <button
            type="button"
            className="tb-video-player-btn-icone"
            aria-label={mudo ? "Ativar som" : "Silenciar"}
            title={mudo ? "Ativar som" : "Silenciar"}
            disabled={!video}
            onClick={aoAlternarMudo}
          >
            {mudo || volume === 0 ? (
              <IconeVolumeMudoVideoTranscribrothers />
            ) : (
              <IconeVolumeAltoVideoTranscribrothers />
            )}
          </button>

          <input
            type="range"
            className="tb-video-player-barra-volume"
            min={0}
            max={1}
            step={0.05}
            value={mudo ? 0 : volume}
            disabled={!video}
            aria-label="Volume"
            onChange={(evento) => aoAlterarVolume(Number(evento.target.value))}
          />

          <button
            type="button"
            className="tb-video-player-btn-velocidade"
            aria-label={`Velocidade de reprodução: ${velocidadeReproducao}x`}
            title="Alterar velocidade"
            disabled={!video}
            onClick={aoAlternarVelocidade}
          >
            {velocidadeReproducao}x
          </button>

          {exibirBotaoCapturarFrame && aoCapturarFrame ? (
            <button
              type="button"
              className="tb-video-player-btn-capturar-frame"
              aria-label={capturandoFrame ? "Capturando frame…" : "Capturar frame e abrir imagem"}
              title={
                capturandoFrame
                  ? "Capturando frame do vídeo…"
                  : "Capturar frame neste instante e abrir na visualização de imagem"
              }
              aria-busy={capturandoFrame}
              disabled={!video || capturandoFrame}
              onClick={aoCapturarFrame}
            >
              <IconeCapturarFrameVideoTranscribrothers />
            </button>
          ) : null}

          {aoSolicitarTelaMaior ? (
            <button
              type="button"
              className="tb-video-player-btn-icone"
              aria-label="Abrir vídeo em tela maior"
              title="Tela maior"
              disabled={!video}
              onClick={aoSolicitarTelaMaior}
            >
              <IconeAmpliarVideoTelaMaiorTranscribrothers />
            </button>
          ) : null}
        </div>
      </div>

      <div className="tb-video-player-coluna-progresso-e-faixa-cues">
        <input
          type="range"
          className="tb-video-player-barra-progresso"
          min={0}
          max={maxBarra || 100}
          step={0.1}
          value={valorBarra}
          disabled={!video}
          aria-label="Posição no vídeo"
          aria-valuemin={0}
          aria-valuemax={maxBarra}
          aria-valuenow={valorBarra}
          aria-valuetext={formatarSegundosComoMmSsTranscribrothers(tempoAtualSegundos)}
          onMouseDown={aoIniciarArrastarBarra}
          onTouchStart={aoIniciarArrastarBarra}
          onChange={(evento) => aoAlterarTempoPelaBarra(Number(evento.target.value))}
        />
        {temFaixaCues ? (
          <ComponenteFaixaCuesTimelineAbaixoBarraProgressoTranscribrothers
            duracaoSegundos={maxBarra}
            segmentos={faixaCuesTimeline!}
            indiceAtiva={indiceCueAtivaFaixaTimeline}
            aoClicarSegmento={aoClicarSegmentoFaixaCuesTimeline}
            aoArrastarSegmento={aoArrastarSegmentoFaixaCuesTimeline}
          />
        ) : null}
      </div>
    </div>
  );
}

function useEstadoUiPlayerVideoTranscribrothers(
  video: HTMLVideoElement | null,
  duracaoConhecidaSegundos: number,
) {
  const [duracaoSegundosNoElemento, setDuracaoSegundosNoElemento] = useState(0);
  const duracaoConhecidaRef = useRef(duracaoConhecidaSegundos);
  duracaoConhecidaRef.current = duracaoConhecidaSegundos;
  const duracaoSegundos =
    duracaoConhecidaSegundos > 0 ? duracaoConhecidaSegundos : duracaoSegundosNoElemento;
  const [tempoAtualSegundos, setTempoAtualSegundos] = useState(0);
  const [pausado, setPausado] = useState(true);
  const [mudo, setMudo] = useState(false);
  const [volume, setVolume] = useState(1);
  const [velocidadeReproducao, setVelocidadeReproducao] = useState(1);
  const [arrastandoBarraProgresso, setArrastandoBarraProgresso] = useState(false);
  const arrastandoBarraProgressoRef = useRef(false);
  const seekAoFimParaDuracaoTentadoRef = useRef(false);

  useEffect(() => {
    setDuracaoSegundosNoElemento(0);
    setTempoAtualSegundos(0);
    seekAoFimParaDuracaoTentadoRef.current = false;
  }, [video]);

  useEffect(() => {
    if (!video) return;

    const registrarDuracaoDoElementoSeNecessario = (dur: number) => {
      if (duracaoConhecidaRef.current > 0) return;
      if (dur > 0) setDuracaoSegundosNoElemento(dur);
    };

    const atualizarDuracaoDoElemento = () => {
      const dur = lerDuracaoSegundosElementoVideoPlayerTranscribrothers(video);
      registrarDuracaoDoElementoSeNecessario(dur);
    };
    const atualizarTempo = () => {
      if (!arrastandoBarraProgressoRef.current) {
        setTempoAtualSegundos(video.currentTime);
      }
      atualizarDuracaoDoElemento();
    };
    const aoPlay = () => setPausado(false);
    const aoPause = () => setPausado(true);
    const aoVolume = () => {
      setMudo(video.muted);
      setVolume(video.volume);
    };

    atualizarDuracaoDoElemento();
    atualizarTempo();
    setPausado(video.paused);
    setMudo(video.muted);
    setVolume(video.volume);
    setVelocidadeReproducao(video.playbackRate);

    const eventosDuracao: Array<keyof HTMLVideoElementEventMap> = [
      "loadedmetadata",
      "durationchange",
      "loadeddata",
      "canplay",
      "progress",
    ];
    let cancelarSeekAoFim: (() => void) | undefined;
    const tentarSeekAoFimSeAindaSemDuracao = () => {
      if (duracaoConhecidaRef.current > 0 || seekAoFimParaDuracaoTentadoRef.current) return;
      const dur = lerDuracaoSegundosElementoVideoPlayerTranscribrothers(video);
      if (dur > 0) {
        registrarDuracaoDoElementoSeNecessario(dur);
        return;
      }
      seekAoFimParaDuracaoTentadoRef.current = true;
      cancelarSeekAoFim?.();
      cancelarSeekAoFim = tentarDescobrirDuracaoVideoPorSeekAoFimNavegadorTranscribrothers(
        video,
        registrarDuracaoDoElementoSeNecessario,
      );
    };

    for (const nome of eventosDuracao) {
      video.addEventListener(nome, atualizarDuracaoDoElemento);
      video.addEventListener(nome, tentarSeekAoFimSeAindaSemDuracao);
    }
    video.addEventListener("timeupdate", atualizarTempo);
    video.addEventListener("seeked", atualizarTempo);
    video.addEventListener("play", aoPlay);
    video.addEventListener("pause", aoPause);
    video.addEventListener("volumechange", aoVolume);
    tentarSeekAoFimSeAindaSemDuracao();

    return () => {
      cancelarSeekAoFim?.();
      for (const nome of eventosDuracao) {
        video.removeEventListener(nome, atualizarDuracaoDoElemento);
        video.removeEventListener(nome, tentarSeekAoFimSeAindaSemDuracao);
      }
      video.removeEventListener("timeupdate", atualizarTempo);
      video.removeEventListener("seeked", atualizarTempo);
      video.removeEventListener("play", aoPlay);
      video.removeEventListener("pause", aoPause);
      video.removeEventListener("volumechange", aoVolume);
    };
  }, [video]);

  useEffect(() => {
    if (!arrastandoBarraProgresso) return;
    const aoSoltarPonteiro = () => {
      window.setTimeout(() => {
        arrastandoBarraProgressoRef.current = false;
        setArrastandoBarraProgresso(false);
        if (video) setTempoAtualSegundos(video.currentTime);
      }, 0);
    };
    window.addEventListener("mouseup", aoSoltarPonteiro);
    window.addEventListener("touchend", aoSoltarPonteiro);
    return () => {
      window.removeEventListener("mouseup", aoSoltarPonteiro);
      window.removeEventListener("touchend", aoSoltarPonteiro);
    };
  }, [arrastandoBarraProgresso, video]);

  return {
    duracaoSegundos,
    tempoAtualSegundos,
    pausado,
    mudo,
    volume,
    velocidadeReproducao,
    arrastandoBarraProgresso,
    arrastandoBarraProgressoRef,
    setTempoAtualSegundos,
    setArrastandoBarraProgresso,
    setVelocidadeReproducao,
  };
}

function criarHandlersControlesVideoTranscribrothers(
  video: HTMLVideoElement | null,
  estado: ReturnType<typeof useEstadoUiPlayerVideoTranscribrothers>,
) {
  return {
    aoAlternarPlayPause: () => {
      if (!video) return;
      if (video.paused) void video.play().catch(() => undefined);
      else video.pause();
    },
    aoAlternarMudo: () => {
      if (!video) return;
      video.muted = !video.muted;
    },
    aoAlterarVolume: (novoVolume: number) => {
      if (!video) return;
      video.volume = Math.max(0, Math.min(1, novoVolume));
      if (novoVolume > 0) video.muted = false;
    },
    aoIniciarArrastarBarra: () => {
      estado.arrastandoBarraProgressoRef.current = true;
      estado.setArrastandoBarraProgresso(true);
    },
    aoFinalizarArrastarBarra: () => {
      estado.arrastandoBarraProgressoRef.current = false;
      estado.setArrastandoBarraProgresso(false);
    },
    aoAlterarTempoPelaBarra: (tempoSegundos: number) => {
      if (!video) return;
      const duracao =
        Number.isFinite(video.duration) && video.duration > 0 ? video.duration : Number.POSITIVE_INFINITY;
      const t = Math.max(0, Math.min(tempoSegundos, duracao));
      estado.arrastandoBarraProgressoRef.current = true;
      video.currentTime = t;
      estado.setTempoAtualSegundos(t);
    },
    aoAlternarVelocidade: () => {
      if (!video) return;
      const lista = VELOCIDADES_REPRODUCAO_VIDEO_TRANSCRIBROTHERS;
      const indiceAtual = lista.findIndex((v) => Math.abs(v - video.playbackRate) < 0.01);
      const proximo = lista[(indiceAtual + 1) % lista.length] ?? 1;
      video.playbackRate = proximo;
      estado.setVelocidadeReproducao(proximo);
    },
  };
}

export function ComponentePlayerVideoJobControlesCustomizadosEModalAmpliarTelaMaiorTranscribrothers({
  jobId,
  videoRef,
  duracaoVideoSegundosDoJob = null,
  classNameVideo = "tb-video",
  urlVideoSrc,
  exibirBotaoTelaMaior = true,
  faixaLegendas,
  keyVideo,
  classNameEnvoltorio,
  preloadVideo = "auto",
  faixaCuesTimeline,
  indiceCueAtivaFaixaTimeline = -1,
  aoClicarSegmentoFaixaCuesTimeline,
  aoArrastarSegmentoFaixaCuesTimeline,
  forcarUiComoTocando = false,
  aoAlternarPlayPauseCustomizado,
  timelineVirtualUi = null,
  overlaySobreVideo = null,
  conteudoExtraNaLinhaAcoesControles = null,
  exibirBotaoCapturarFrame = false,
  capturandoFrame = false,
  aoCapturarFrameNoInstanteAtual,
  aoVideoIndisponivelParaCapturaFrame,
  onDuracaoVideoConhecidaSegundos,
}: PropsComponentePlayerVideoJobControlesCustomizadosEModalAmpliarTelaMaiorTranscribrothers) {
  const [modalTelaMaiorAberto, setModalTelaMaiorAberto] = useState(false);
  const [videoElementoMontado, setVideoElementoMontado] = useState<HTMLVideoElement | null>(null);
  const [videoModalMontado, setVideoModalMontado] = useState<HTMLVideoElement | null>(null);
  const videoModalRef = useRef<HTMLVideoElement | null>(null);
  /** Alinha overlay (ex.: legenda) ao quadro da imagem com object-fit: contain. */
  const [retanguloOverlaySobreVideo, setRetanguloOverlaySobreVideo] = useState<{
    left: number;
    top: number;
    width: number;
    height: number;
  } | null>(null);
  const urlVideoPadraoJob = `/api/jobs/${encodeURIComponent(jobId)}/video`;
  const urlVideo =
    typeof urlVideoSrc === "string" && urlVideoSrc.trim()
      ? urlVideoSrc.trim()
      : urlVideoPadraoJob;
  const usaUrlVideoOverride = urlVideo !== urlVideoPadraoJob;
  const [duracaoSegundosApi, setDuracaoSegundosApi] = useState(0);

  const duracaoDoJob =
    typeof duracaoVideoSegundosDoJob === "number" &&
    Number.isFinite(duracaoVideoSegundosDoJob) &&
    duracaoVideoSegundosDoJob > 0
      ? duracaoVideoSegundosDoJob
      : 0;

  const duracaoConhecidaSegundos =
    !usaUrlVideoOverride && duracaoDoJob > 0 ? duracaoDoJob : duracaoSegundosApi;

  const registrarDuracaoConhecida = useCallback(
    (duracaoSegundos: number) => {
      if (!(duracaoSegundos > 0)) return;
      setDuracaoSegundosApi(duracaoSegundos);
      onDuracaoVideoConhecidaSegundos?.(duracaoSegundos);
    },
    [onDuracaoVideoConhecidaSegundos],
  );

  useEffect(() => {
    setDuracaoSegundosApi(0);
    // Com override (ex.: MP4 narrado), a duração vem do próprio `<video>`, não do metadata do vídeo fonte.
    if (usaUrlVideoOverride || duracaoDoJob > 0) return;
    let cancelado = false;
    void fetch(`/api/jobs/${encodeURIComponent(jobId)}/video/metadata`)
      .then(async (resposta) => {
        if (!resposta.ok) return null;
        return (await resposta.json()) as { duracao_segundos?: number };
      })
      .then((payload) => {
        if (cancelado || !payload) return;
        const dur = payload.duracao_segundos;
        if (typeof dur === "number" && Number.isFinite(dur) && dur > 0) {
          registrarDuracaoConhecida(dur);
        }
      })
      .catch(() => undefined);
    return () => {
      cancelado = true;
    };
  }, [duracaoDoJob, jobId, registrarDuracaoConhecida, usaUrlVideoOverride]);

  const estadoInline = useEstadoUiPlayerVideoTranscribrothers(
    videoElementoMontado,
    duracaoConhecidaSegundos,
  );
  const estadoModal = useEstadoUiPlayerVideoTranscribrothers(
    modalTelaMaiorAberto ? videoModalMontado : null,
    duracaoConhecidaSegundos,
  );

  const handlersInline = criarHandlersControlesVideoTranscribrothers(videoElementoMontado, estadoInline);
  const handlersModal = criarHandlersControlesVideoTranscribrothers(
    modalTelaMaiorAberto ? videoModalMontado : null,
    estadoModal,
  );
  const aoPlayPauseInline = aoAlternarPlayPauseCustomizado ?? handlersInline.aoAlternarPlayPause;
  const aoPlayPauseModal = aoAlternarPlayPauseCustomizado ?? handlersModal.aoAlternarPlayPause;

  const atribuirRefVideoInline = useCallback(
    (elemento: HTMLVideoElement | null) => {
      videoRef.current = elemento;
      setVideoElementoMontado(elemento);
    },
    [videoRef],
  );

  useEffect(() => {
    if (!overlaySobreVideo || !videoElementoMontado) {
      setRetanguloOverlaySobreVideo(null);
      return;
    }
    const video = videoElementoMontado;
    const atualizar = () => {
      const caixa = video.getBoundingClientRect();
      const r = calcularRetanguloObjectFitContainVideoNoElementoUiTranscribrothers(
        caixa.width,
        caixa.height,
        video.videoWidth || 0,
        video.videoHeight || 0,
      );
      setRetanguloOverlaySobreVideo(r);
    };
    atualizar();
    const ro = new ResizeObserver(atualizar);
    ro.observe(video);
    video.addEventListener("loadedmetadata", atualizar);
    video.addEventListener("resize", atualizar);
    return () => {
      ro.disconnect();
      video.removeEventListener("loadedmetadata", atualizar);
      video.removeEventListener("resize", atualizar);
    };
  }, [overlaySobreVideo, videoElementoMontado, urlVideo, keyVideo]);

  const alternarPlayPausePeloCliqueNoVideo = useCallback(() => {
    aoPlayPauseInline();
  }, [aoPlayPauseInline]);

  const abrirModalTelaMaior = useCallback(() => {
    const video = videoRef.current;
    if (!video) return;
    video.pause();
    setModalTelaMaiorAberto(true);
  }, [videoRef]);

  const fecharModalTelaMaior = useCallback(() => {
    const videoInline = videoRef.current;
    const videoModal = videoModalRef.current;
    if (videoInline && videoModal) {
      videoInline.currentTime = videoModal.currentTime;
      videoInline.volume = videoModal.volume;
      videoInline.muted = videoModal.muted;
      videoInline.playbackRate = videoModal.playbackRate;
      if (!videoModal.paused) {
        void videoInline.play().catch(() => undefined);
      }
    }
    if (videoModal) videoModal.pause();
    setVideoModalMontado(null);
    setModalTelaMaiorAberto(false);
  }, [videoRef]);

  useEffect(() => {
    if (!modalTelaMaiorAberto || !videoModalMontado) return;
    const videoInline = videoRef.current;
    const videoModal = videoModalMontado;
    if (!videoInline) return;

    const sincronizarModalComInline = () => {
      videoModal.currentTime = videoInline.currentTime;
      videoModal.volume = videoInline.volume;
      videoModal.muted = videoInline.muted;
      videoModal.playbackRate = videoInline.playbackRate;
    };

    if (videoModal.readyState >= 1) {
      sincronizarModalComInline();
    } else {
      videoModal.addEventListener("loadedmetadata", sincronizarModalComInline, { once: true });
    }
  }, [modalTelaMaiorAberto, videoModalMontado, videoRef]);

  useEffect(() => {
    if (!modalTelaMaiorAberto) return;
    const onKeyDown = (evento: KeyboardEvent) => {
      if (evento.key === "Escape") fecharModalTelaMaior();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [fecharModalTelaMaior, modalTelaMaiorAberto]);

  const solicitarCapturaFrameDoVideoAtivo = useCallback(() => {
    if (!aoCapturarFrameNoInstanteAtual) return;
    const videoAtivo =
      modalTelaMaiorAberto && videoModalMontado ? videoModalMontado : videoElementoMontado;
    if (!videoAtivo) return;
    if (Number.isNaN(videoAtivo.duration) && videoAtivo.readyState < 2) {
      aoVideoIndisponivelParaCapturaFrame?.();
      return;
    }
    const timestampSegundos = videoAtivo.currentTime;
    videoAtivo.pause();
    if (modalTelaMaiorAberto) {
      fecharModalTelaMaior();
    }
    aoCapturarFrameNoInstanteAtual(timestampSegundos);
  }, [
    aoCapturarFrameNoInstanteAtual,
    aoVideoIndisponivelParaCapturaFrame,
    fecharModalTelaMaior,
    modalTelaMaiorAberto,
    videoElementoMontado,
    videoModalMontado,
  ]);

  const propsCapturaFrameCompartilhados = {
    exibirBotaoCapturarFrame: exibirBotaoCapturarFrame && Boolean(aoCapturarFrameNoInstanteAtual),
    capturandoFrame,
    aoCapturarFrame: solicitarCapturaFrameDoVideoAtivo,
  };

  const propsFaixaCuesCompartilhados = {
    faixaCuesTimeline,
    indiceCueAtivaFaixaTimeline,
    aoClicarSegmentoFaixaCuesTimeline,
    aoArrastarSegmentoFaixaCuesTimeline,
  };

  const handlersInlineComTimelineVirtual = timelineVirtualUi
    ? {
        ...handlersInline,
        aoAlterarTempoPelaBarra: (tempoSegundos: number) => {
          const dur = Math.max(0, timelineVirtualUi.duracaoSegundos);
          const t = Math.max(0, dur > 0 ? Math.min(tempoSegundos, dur) : tempoSegundos);
          estadoInline.arrastandoBarraProgressoRef.current = true;
          estadoInline.setTempoAtualSegundos(t);
          timelineVirtualUi.aoAlterarTempoPelaBarra(t);
        },
      }
    : handlersInline;

  const handlersModalComTimelineVirtual = timelineVirtualUi
    ? {
        ...handlersModal,
        aoAlterarTempoPelaBarra: (tempoSegundos: number) => {
          const dur = Math.max(0, timelineVirtualUi.duracaoSegundos);
          const t = Math.max(0, dur > 0 ? Math.min(tempoSegundos, dur) : tempoSegundos);
          estadoModal.arrastandoBarraProgressoRef.current = true;
          estadoModal.setTempoAtualSegundos(t);
          timelineVirtualUi.aoAlterarTempoPelaBarra(t);
        },
      }
    : handlersModal;

  const propsBarraInline: BarraControlesPlayerVideoTranscribrothersProps = {
    video: videoElementoMontado,
    duracaoSegundos: timelineVirtualUi
      ? Math.max(0, timelineVirtualUi.duracaoSegundos)
      : estadoInline.duracaoSegundos,
    tempoAtualSegundos: timelineVirtualUi
      ? timelineVirtualUi.tempoAtualSegundos
      : estadoInline.tempoAtualSegundos,
    pausado: forcarUiComoTocando ? false : estadoInline.pausado,
    mudo: estadoInline.mudo,
    volume: estadoInline.volume,
    velocidadeReproducao: estadoInline.velocidadeReproducao,
    arrastandoBarraProgresso: estadoInline.arrastandoBarraProgresso,
    ...(exibirBotaoTelaMaior ? { aoSolicitarTelaMaior: abrirModalTelaMaior } : {}),
    ...propsFaixaCuesCompartilhados,
    ...propsCapturaFrameCompartilhados,
    conteudoExtraNaLinhaAcoesControles,
    ...handlersInlineComTimelineVirtual,
    aoAlternarPlayPause: aoPlayPauseInline,
  };

  const propsBarraModal: BarraControlesPlayerVideoTranscribrothersProps = {
    video: videoModalMontado,
    duracaoSegundos: timelineVirtualUi
      ? Math.max(0, timelineVirtualUi.duracaoSegundos)
      : estadoModal.duracaoSegundos,
    tempoAtualSegundos: timelineVirtualUi
      ? timelineVirtualUi.tempoAtualSegundos
      : estadoModal.tempoAtualSegundos,
    pausado: forcarUiComoTocando ? false : estadoModal.pausado,
    mudo: estadoModal.mudo,
    volume: estadoModal.volume,
    velocidadeReproducao: estadoModal.velocidadeReproducao,
    arrastandoBarraProgresso: estadoModal.arrastandoBarraProgresso,
    ...propsFaixaCuesCompartilhados,
    ...propsCapturaFrameCompartilhados,
    ...handlersModalComTimelineVirtual,
    aoAlternarPlayPause: aoPlayPauseModal,
  };

  const classeEnvoltorio = [
    "tb-video-player-envoltorio",
    classNameEnvoltorio?.trim() || "",
  ]
    .filter(Boolean)
    .join(" ");

  return (
    <>
      <div className={classeEnvoltorio}>
        <div className="tb-video-player-area-midia">
          <video
            key={keyVideo}
            ref={atribuirRefVideoInline}
            className={classNameVideo}
            src={urlVideo}
            playsInline
            preload={preloadVideo}
            onLoadedMetadata={(evento) => {
              const alvo = evento.currentTarget;
              // Duração do job (vídeo fonte) não se aplica quando há override de URL.
              if (!usaUrlVideoOverride && duracaoDoJob > 0) return;
              const dur = lerDuracaoSegundosElementoVideoPlayerTranscribrothers(alvo);
              if (dur > 0) {
                registrarDuracaoConhecida(dur);
                return;
              }
              tentarDescobrirDuracaoVideoPorSeekAoFimNavegadorTranscribrothers(alvo, (duracaoSegundos) => {
                registrarDuracaoConhecida(duracaoSegundos);
              });
            }}
            onClick={alternarPlayPausePeloCliqueNoVideo}
          >
            {faixaLegendas}
          </video>
          {overlaySobreVideo ? (
            <div
              className="tb-video-player-overlay-sobre-video"
              style={
                retanguloOverlaySobreVideo &&
                retanguloOverlaySobreVideo.width > 0 &&
                retanguloOverlaySobreVideo.height > 0
                  ? {
                      left: retanguloOverlaySobreVideo.left,
                      top: retanguloOverlaySobreVideo.top,
                      width: retanguloOverlaySobreVideo.width,
                      height: retanguloOverlaySobreVideo.height,
                      right: "auto",
                      bottom: "auto",
                    }
                  : undefined
              }
            >
              {overlaySobreVideo}
            </div>
          ) : null}
          {exibirBotaoTelaMaior ? (
            <button
              type="button"
              className="tb-video-player-btn-flutuante-ampliar"
              aria-label="Abrir vídeo em tela maior"
              title="Tela maior"
              onClick={(evento) => {
                evento.stopPropagation();
                abrirModalTelaMaior();
              }}
            >
              <IconeAmpliarVideoTelaMaiorTranscribrothers />
            </button>
          ) : null}
        </div>
        <BarraControlesPlayerVideoTranscribrothers {...propsBarraInline} />
      </div>

      {exibirBotaoTelaMaior && modalTelaMaiorAberto
        ? createPortal(
            <div
              className="tb-video-modal-tela-maior-overlay"
              role="dialog"
              aria-modal="true"
              aria-label="Vídeo em tela maior"
              onClick={fecharModalTelaMaior}
            >
              <div
                className="tb-video-modal-tela-maior-painel"
                onClick={(evento) => evento.stopPropagation()}
              >
                <header className="tb-video-modal-tela-maior-cabecalho">
                  <h3 className="tb-video-modal-tela-maior-titulo">Vídeo</h3>
                  <button
                    type="button"
                    className="tb-video-modal-tela-maior-fechar"
                    aria-label="Fechar tela maior"
                    onClick={fecharModalTelaMaior}
                  >
                    Fechar
                  </button>
                </header>
                <div className="tb-video-player-envoltorio tb-video-player-envoltorio--modal">
                  <div className="tb-video-player-area-midia tb-video-player-area-midia--modal">
                    <video
                      ref={(elemento) => {
                        videoModalRef.current = elemento;
                        setVideoModalMontado(elemento);
                      }}
                      className="tb-video tb-video--modal-tela-maior"
                      src={urlVideo}
                      playsInline
                      preload="metadata"
                      autoPlay
                      onClick={() => handlersModal.aoAlternarPlayPause()}
                    />
                  </div>
                  <BarraControlesPlayerVideoTranscribrothers {...propsBarraModal} compacto />
                </div>
              </div>
            </div>,
            document.body,
          )
        : null}
    </>
  );
}
