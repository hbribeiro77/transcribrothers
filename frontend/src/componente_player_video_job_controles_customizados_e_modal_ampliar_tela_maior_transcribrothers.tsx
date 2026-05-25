import type * as React from "react";
import { useCallback, useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
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
};

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
}: BarraControlesPlayerVideoTranscribrothersProps) {
  const duracaoValida = Number.isFinite(duracaoSegundos) && duracaoSegundos > 0;
  const maxBarra = duracaoValida ? duracaoSegundos : 0;
  const valorBarra = arrastandoBarraProgresso
    ? tempoAtualSegundos
    : Math.min(tempoAtualSegundos, maxBarra || tempoAtualSegundos);

  return (
    <div
      className={`tb-video-player-controles${compacto ? " tb-video-player-controles--compacto" : ""}`}
      onClick={(evento) => evento.stopPropagation()}
      onDoubleClick={(evento) => evento.stopPropagation()}
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

      <button
        type="button"
        className="tb-video-player-btn-icone"
        aria-label={mudo ? "Ativar som" : "Silenciar"}
        title={mudo ? "Ativar som" : "Silenciar"}
        disabled={!video}
        onClick={aoAlternarMudo}
      >
        {mudo || volume === 0 ? <IconeVolumeMudoVideoTranscribrothers /> : <IconeVolumeAltoVideoTranscribrothers />}
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
  const urlVideo = `/api/jobs/${encodeURIComponent(jobId)}/video`;
  const [duracaoSegundosApi, setDuracaoSegundosApi] = useState(0);

  const duracaoDoJob =
    typeof duracaoVideoSegundosDoJob === "number" &&
    Number.isFinite(duracaoVideoSegundosDoJob) &&
    duracaoVideoSegundosDoJob > 0
      ? duracaoVideoSegundosDoJob
      : 0;

  const duracaoConhecidaSegundos = duracaoDoJob > 0 ? duracaoDoJob : duracaoSegundosApi;

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
    if (duracaoDoJob > 0) return;
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
  }, [duracaoDoJob, jobId, registrarDuracaoConhecida]);

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

  const atribuirRefVideoInline = useCallback(
    (elemento: HTMLVideoElement | null) => {
      videoRef.current = elemento;
      setVideoElementoMontado(elemento);
    },
    [videoRef],
  );

  const alternarPlayPausePeloCliqueNoVideo = useCallback(() => {
    handlersInline.aoAlternarPlayPause();
  }, [handlersInline]);

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

  const propsBarraInline: BarraControlesPlayerVideoTranscribrothersProps = {
    video: videoElementoMontado,
    duracaoSegundos: estadoInline.duracaoSegundos,
    tempoAtualSegundos: estadoInline.tempoAtualSegundos,
    pausado: estadoInline.pausado,
    mudo: estadoInline.mudo,
    volume: estadoInline.volume,
    velocidadeReproducao: estadoInline.velocidadeReproducao,
    arrastandoBarraProgresso: estadoInline.arrastandoBarraProgresso,
    aoSolicitarTelaMaior: abrirModalTelaMaior,
    ...propsCapturaFrameCompartilhados,
    ...handlersInline,
  };

  const propsBarraModal: BarraControlesPlayerVideoTranscribrothersProps = {
    video: videoModalMontado,
    duracaoSegundos: estadoModal.duracaoSegundos,
    tempoAtualSegundos: estadoModal.tempoAtualSegundos,
    pausado: estadoModal.pausado,
    mudo: estadoModal.mudo,
    volume: estadoModal.volume,
    velocidadeReproducao: estadoModal.velocidadeReproducao,
    arrastandoBarraProgresso: estadoModal.arrastandoBarraProgresso,
    ...propsCapturaFrameCompartilhados,
    ...handlersModal,
  };

  return (
    <>
      <div className="tb-video-player-envoltorio">
        <div className="tb-video-player-area-midia">
          <video
            ref={atribuirRefVideoInline}
            className={classNameVideo}
            src={urlVideo}
            playsInline
            preload="auto"
            onLoadedMetadata={(evento) => {
              const alvo = evento.currentTarget;
              if (duracaoDoJob > 0) return;
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
          />
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
        </div>
        <BarraControlesPlayerVideoTranscribrothers {...propsBarraInline} />
      </div>

      {modalTelaMaiorAberto
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
