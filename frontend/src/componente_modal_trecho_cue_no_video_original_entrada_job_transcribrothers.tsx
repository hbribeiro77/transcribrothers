import { useCallback, useEffect, useId, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";

import {
  deslizarJanelaVideoCuePeloPontoUiTranscribrothers,
  marcarExtremoJanelaVideoCuePeloPontoUiTranscribrothers,
  type JanelaVideoCueLocalUiTranscribrothers,
} from "./modulo_api_janelas_video_e_wavs_por_cue_narracao_job_transcribrothers.ts";
import {
  ComponentePlayerVideoJobControlesCustomizadosEModalAmpliarTelaMaiorTranscribrothers,
  type SegmentoFaixaCuesTimelinePlayerVideoTranscribrothers,
} from "./componente_player_video_job_controles_customizados_e_modal_ampliar_tela_maior_transcribrothers.tsx";
import { formatarDuracaoSegundosCurtaPortuguesUiTranscribrothers } from "./modulo_util_formatar_duracao_segundos_curta_portugues_ui_transcribrothers.ts";
import { formatarSegundosComoTimestampVttCurtoUiTranscribrothers } from "./modulo_util_parsear_webvtt_em_cues_para_lista_ui_transcribrothers.ts";
import {
  montarSrcAudioNarracaoComBustCacheSeHttpUiTranscribrothers,
  resolverUrlAudioNarracaoCueTrechoOriginalUiTranscribrothers,
} from "./modulo_util_resolver_url_audio_narracao_cue_trecho_original_ui_transcribrothers.ts";
import { normalizarIdFonteVideoUiTranscribrothers } from "./modulo_api_biblioteca_midias_tela_job_transcribrothers.ts";
import "./estilos_css_player_video_job_controles_customizados_e_modal_ampliar_tela_maior_transcribrothers.css";
import "./estilos_css_modal_trecho_cue_no_video_original_entrada_job_transcribrothers.css";
import { usarDialogoConfirmacaoAcaoUiSubstituindoWindowConfirmTranscribrothers } from "./hook_usar_dialogo_confirmacao_acao_ui_substituindo_window_confirm_transcribrothers.tsx";


export type PropsComponenteModalTrechoCueNoVideoOriginalEntradaJobTranscribrothers = {
  aberto: boolean;
  jobId: string;
  /** Índice da cue aberta (0-based). */
  indiceCueInicial: number;
  janelas: JanelaVideoCueLocalUiTranscribrothers[];
  /** Textos das legendas (paralelo a `janelas`) para rótulos na faixa. */
  textosCues: string[];
  /**
   * URLs de áudio TTS por índice (WAV gravado ou blob de prévia/Regenerar do editor).
   * Quando informado, habilita «Narração» mesmo sem `temWav` no manifesto.
   */
  urlsAudioNarracaoPorIndice?: Record<number, string>;
  /** Override do src do player (mídia de tela da biblioteca). Default: vídeo de entrada. */
  urlVideoSrc?: string;
  /** Título do diálogo (ex.: quando a fonte não é a entrada). */
  tituloModal?: string;
  onFechar: () => void;
  /**
   * Aplica o rascunho de janelas no editor narrado (sem remux automático).
   * Retorna motivo de erro se o pai rejeitar.
   */
  onAplicarJanelas?: (
    janelas: JanelaVideoCueLocalUiTranscribrothers[],
  ) => { ok: true; aviso?: string | null } | { ok: false; motivo: string };
};

type ModoPlayTrechoOriginalUiTranscribrothers = "video" | "narracao";

const MARGEM_FIM_TRECHO_SEGUNDOS = 0.05;

function clampIndiceCueTranscribrothers(indice: number, total: number): number {
  if (total <= 0) return 0;
  return Math.max(0, Math.min(indice, total - 1));
}

function clonarJanelasTranscribrothers(
  lista: JanelaVideoCueLocalUiTranscribrothers[],
): JanelaVideoCueLocalUiTranscribrothers[] {
  return lista.map((j) => ({ ...j }));
}

function janelasTempoDiferemTranscribrothers(
  a: JanelaVideoCueLocalUiTranscribrothers[],
  b: JanelaVideoCueLocalUiTranscribrothers[],
): boolean {
  if (a.length !== b.length) return true;
  for (let i = 0; i < a.length; i++) {
    if (
      Math.abs(a[i].inicioVideoSegundos - b[i].inicioVideoSegundos) > 1e-6 ||
      Math.abs(a[i].fimVideoSegundos - b[i].fimVideoSegundos) > 1e-6
    ) {
      return true;
    }
  }
  return false;
}

function IconeMaximizarModalTrechoVideoOriginalTranscribrothers() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path
        d="M3 6V3h3M10 3h3v3M13 10v3h-3M6 13H3v-3"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function IconeRestaurarModalTrechoVideoOriginalTranscribrothers() {
  return (
    <svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path
        d="M6 3H3v3M10 3h3v3M13 10v3h-3M6 13H3v-3"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <rect x="5" y="5" width="6" height="6" rx="0.5" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

export function ComponenteModalTrechoCueNoVideoOriginalEntradaJobTranscribrothers({
  aberto,
  jobId,
  indiceCueInicial,
  janelas,
  textosCues,
  urlsAudioNarracaoPorIndice,
  urlVideoSrc,
  tituloModal,
  onFechar,
  onAplicarJanelas,
}: PropsComponenteModalTrechoCueNoVideoOriginalEntradaJobTranscribrothers) {
  const tituloId = useId();
  const { pedirConfirmacao, elementoDialogoConfirmacao } =
    usarDialogoConfirmacaoAcaoUiSubstituindoWindowConfirmTranscribrothers();
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const audioNarracaoRef = useRef<HTMLAudioElement | null>(null);
  const listaTrechosRef = useRef<HTMLUListElement | null>(null);
  const cardAtivoRef = useRef<HTMLLIElement | null>(null);
  const indiceAtivoRef = useRef(0);
  const limitarReproducaoAoTrechoRef = useRef(false);
  const modoPlayRef = useRef<ModoPlayTrechoOriginalUiTranscribrothers | null>(null);
  const ignorarProximoPauseUiRef = useRef(false);
  /** Janela de tela acabou; o WAV da narração segue até o fim (como no MP4 gerado). */
  const narracaoSegueAposVideoRef = useRef(false);
  const janelasRascunhoRef = useRef<JanelaVideoCueLocalUiTranscribrothers[]>([]);
  const urlsAudioNarracaoPorIndiceRef = useRef<Record<number, string> | undefined>(
    urlsAudioNarracaoPorIndice,
  );
  urlsAudioNarracaoPorIndiceRef.current = urlsAudioNarracaoPorIndice;

  const [indiceAtivo, setIndiceAtivo] = useState(0);
  const [painelMaximizado, setPainelMaximizado] = useState(false);
  /** Padrão: sem áudio do vídeo de entrada (foco na tela / narração). */
  const [audioOriginalAtivo, setAudioOriginalAtivo] = useState(false);
  /** Início/Fim marcam extremos (duração muda); padrão ligado em janela provisória. */
  const [marcarExtremosDuracaoLivre, setMarcarExtremosDuracaoLivre] = useState(false);
  const marcarExtremosDuracaoLivreRef = useRef(false);
  const [indiceTrechoTocando, setIndiceTrechoTocando] = useState<number | null>(null);
  const [modoPlayAtivo, setModoPlayAtivo] = useState<ModoPlayTrechoOriginalUiTranscribrothers | null>(
    null,
  );
  const [janelasRascunho, setJanelasRascunho] = useState<JanelaVideoCueLocalUiTranscribrothers[]>(
    [],
  );
  const [erroRecorte, setErroRecorte] = useState<string | null>(null);
  const [avisoRecorte, setAvisoRecorte] = useState<string | null>(null);
  const [avisoAplicado, setAvisoAplicado] = useState<string | null>(null);
  /** Fonte de tela desta sessão (só lista/edita cues com o mesmo id). */
  const [idFonteEscopo, setIdFonteEscopo] = useState("");

  janelasRascunhoRef.current = janelasRascunho;
  marcarExtremosDuracaoLivreRef.current = marcarExtremosDuracaoLivre;

  const pararAudioNarracao = useCallback(() => {
    const audio = audioNarracaoRef.current;
    if (!audio) return;
    audio.pause();
    audio.removeAttribute("src");
    try {
      audio.load();
    } catch {
      /* ignore */
    }
  }, []);

  const aplicarMuteVideoConformeEstado = useCallback(
    (modo: ModoPlayTrechoOriginalUiTranscribrothers | null) => {
      const video = videoRef.current;
      if (!video) return;
      if (modo === "narracao") {
        video.muted = true;
      } else {
        video.muted = !audioOriginalAtivo;
      }
    },
    [audioOriginalAtivo],
  );

  useEffect(() => {
    if (!aberto) {
      setPainelMaximizado(false);
      setIndiceTrechoTocando(null);
      setModoPlayAtivo(null);
      modoPlayRef.current = null;
      limitarReproducaoAoTrechoRef.current = false;
      narracaoSegueAposVideoRef.current = false;
      setJanelasRascunho([]);
      setErroRecorte(null);
      setAvisoRecorte(null);
      setAvisoAplicado(null);
      setMarcarExtremosDuracaoLivre(false);
      setIdFonteEscopo("");
      pararAudioNarracao();
      return;
    }
    const i = clampIndiceCueTranscribrothers(indiceCueInicial, janelas.length);
    const idFonte = normalizarIdFonteVideoUiTranscribrothers(janelas[i]?.idFonteVideo);
    setIndiceAtivo(i);
    indiceAtivoRef.current = i;
    setIdFonteEscopo(idFonte);
    setMarcarExtremosDuracaoLivre(Boolean(janelas[i]?.janelaProvisoria));
    setErroRecorte(null);
    setAvisoRecorte(null);
    setAvisoAplicado(null);
  }, [
    aberto,
    indiceCueInicial,
    janelas.length,
    // Garante escopo certo ao abrir logo após «Fonte» (mesmo length, id novo).
    janelas[indiceCueInicial]?.idFonteVideo,
    pararAudioNarracao,
  ]);

  // Espelha janelas do editor no rascunho (abre modal / após «Aplicar janela»).
  useEffect(() => {
    if (!aberto) return;
    setJanelasRascunho(clonarJanelasTranscribrothers(janelas));
  }, [aberto, janelas]);

  useEffect(() => {
    if (!aberto) return;
    cardAtivoRef.current?.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }, [aberto, indiceAtivo]);

  useEffect(() => {
    if (!aberto) return;
    aplicarMuteVideoConformeEstado(modoPlayRef.current);
  }, [aberto, audioOriginalAtivo, aplicarMuteVideoConformeEstado]);

  useEffect(() => {
    if (!aberto) return;
    let cancelado = false;
    let videoAnexado: HTMLVideoElement | null = null;
    const aoVolume = () => {
      const video = videoAnexado;
      if (!video) return;
      if (modoPlayRef.current === "narracao" || !audioOriginalAtivo) {
        if (!video.muted) video.muted = true;
      }
    };
    let idRaf = 0;
    const anexar = () => {
      if (cancelado) return;
      const video = videoRef.current;
      if (!video) {
        idRaf = window.requestAnimationFrame(anexar);
        return;
      }
      videoAnexado = video;
      video.addEventListener("volumechange", aoVolume);
    };
    anexar();
    return () => {
      cancelado = true;
      window.cancelAnimationFrame(idRaf);
      if (videoAnexado) videoAnexado.removeEventListener("volumechange", aoVolume);
    };
  }, [aberto, audioOriginalAtivo]);

  const indicesMesmaOrigem = useMemo(() => {
    if (!idFonteEscopo) return janelasRascunho.map((_, i) => i);
    return janelasRascunho
      .map((_, i) => i)
      .filter(
        (i) =>
          normalizarIdFonteVideoUiTranscribrothers(janelasRascunho[i]?.idFonteVideo) ===
          idFonteEscopo,
      );
  }, [janelasRascunho, idFonteEscopo]);

  const indicesMesmaOrigemRef = useRef(indicesMesmaOrigem);
  indicesMesmaOrigemRef.current = indicesMesmaOrigem;

  const faixaJanelasTimeline = useMemo<SegmentoFaixaCuesTimelinePlayerVideoTranscribrothers[]>(
    () =>
      indicesMesmaOrigem.map((indice) => {
        const j = janelasRascunho[indice];
        const texto = (textosCues[indice] || "").trim();
        const semNarracao = Boolean(j?.semNarracao);
        return {
          inicioSegundos: Math.max(0, j?.inicioVideoSegundos ?? 0),
          fimSegundos: Math.max(
            (j?.inicioVideoSegundos ?? 0) + 0.05,
            j?.fimVideoSegundos ?? 0.05,
          ),
          rotulo: semNarracao
            ? `#${indice + 1} — Sem narração`
            : `#${indice + 1} — ${texto.slice(0, 100) || "Cue"}`,
          semNarracao,
        };
      }),
    [janelasRascunho, textosCues, indicesMesmaOrigem],
  );

  const indiceAtivoNaFaixaOrigem = useMemo(() => {
    const pos = indicesMesmaOrigem.indexOf(indiceAtivo);
    return pos >= 0 ? pos : -1;
  }, [indicesMesmaOrigem, indiceAtivo]);

  const janelaAtiva = janelasRascunho[indiceAtivo] ?? null;
  const rascunhoSujo = useMemo(
    () => janelasTempoDiferemTranscribrothers(janelasRascunho, janelas),
    [janelasRascunho, janelas],
  );
  const cueAtivaSuja = useMemo(() => {
    const a = janelasRascunho[indiceAtivo];
    const b = janelas[indiceAtivo];
    if (!a || !b) return false;
    return (
      Math.abs(a.inicioVideoSegundos - b.inicioVideoSegundos) > 1e-6 ||
      Math.abs(a.fimVideoSegundos - b.fimVideoSegundos) > 1e-6
    );
  }, [janelasRascunho, janelas, indiceAtivo]);

  const selecionarCueSemPlay = useCallback(
    (indice: number) => {
      if (!janelasRascunhoRef.current[indice]) return;
      if (indiceAtivoRef.current !== indice) {
        setMarcarExtremosDuracaoLivre(
          Boolean(janelasRascunhoRef.current[indice]?.janelaProvisoria),
        );
      }
      indiceAtivoRef.current = indice;
      setIndiceAtivo(indice);
      setErroRecorte(null);
      setAvisoRecorte(null);
      setAvisoAplicado(null);
    },
    [],
  );

  const encerrarEstadoPlayUi = useCallback(() => {
    narracaoSegueAposVideoRef.current = false;
    limitarReproducaoAoTrechoRef.current = false;
    modoPlayRef.current = null;
    setModoPlayAtivo(null);
    setIndiceTrechoTocando(null);
    aplicarMuteVideoConformeEstado(null);
  }, [aplicarMuteVideoConformeEstado]);

  const pausarTrechoAtual = useCallback(() => {
    const video = videoRef.current;
    if (video && !video.paused) {
      ignorarProximoPauseUiRef.current = true;
      video.pause();
    }
    pararAudioNarracao();
    encerrarEstadoPlayUi();
  }, [pararAudioNarracao, encerrarEstadoPlayUi]);

  const iniciarTrechoDaCueNaPosicao = useCallback(
    (indice: number, modo: ModoPlayTrechoOriginalUiTranscribrothers) => {
      const j = janelasRascunhoRef.current[indice];
      const video = videoRef.current;
      if (!j || !video) return;

      if (modo === "narracao") {
        const urlNarracao = resolverUrlAudioNarracaoCueTrechoOriginalUiTranscribrothers(
          j,
          indice,
          urlsAudioNarracaoPorIndiceRef.current,
        );
        if (!urlNarracao) return;
      }

      const ini = Math.max(0, j.inicioVideoSegundos);
      if (indiceAtivoRef.current !== indice) {
        setMarcarExtremosDuracaoLivre(Boolean(j.janelaProvisoria));
      }
      indiceAtivoRef.current = indice;
      setIndiceAtivo(indice);
      narracaoSegueAposVideoRef.current = false;
      limitarReproducaoAoTrechoRef.current = true;
      modoPlayRef.current = modo;
      setModoPlayAtivo(modo);
      setIndiceTrechoTocando(indice);

      pararAudioNarracao();
      aplicarMuteVideoConformeEstado(modo);

      try {
        video.currentTime = ini;
      } catch {
        /* ignore seek prematuro */
      }

      const tentarPlayVideo = () => {
        void video.play().catch(() => undefined);
      };

      if (modo === "narracao") {
        const urlNarracao = resolverUrlAudioNarracaoCueTrechoOriginalUiTranscribrothers(
          j,
          indice,
          urlsAudioNarracaoPorIndiceRef.current,
        );
        const audio = audioNarracaoRef.current;
        if (audio && urlNarracao) {
          audio.src = montarSrcAudioNarracaoComBustCacheSeHttpUiTranscribrothers(urlNarracao);
          audio.currentTime = 0;
          void audio.play().catch(() => undefined);
        }
      }

      if (video.readyState >= 1) {
        tentarPlayVideo();
      } else {
        const aoMeta = () => {
          video.removeEventListener("loadedmetadata", aoMeta);
          try {
            video.currentTime = ini;
          } catch {
            /* ignore */
          }
          aplicarMuteVideoConformeEstado(modo);
          tentarPlayVideo();
        };
        video.addEventListener("loadedmetadata", aoMeta);
      }
    },
    [pararAudioNarracao, aplicarMuteVideoConformeEstado],
  );

  const alternarPlayTrecho = useCallback(
    (indice: number, modo: ModoPlayTrechoOriginalUiTranscribrothers) => {
      const video = videoRef.current;
      const audio = audioNarracaoRef.current;
      if (!janelasRascunhoRef.current[indice]) return;
      const videoSoloTocando =
        indiceTrechoTocando === indice &&
        modoPlayAtivo === modo &&
        modo === "video" &&
        video &&
        !video.paused &&
        limitarReproducaoAoTrechoRef.current;
      const narracaoAindaTocando =
        indiceTrechoTocando === indice &&
        modoPlayAtivo === "narracao" &&
        modo === "narracao" &&
        Boolean(
          (video && !video.paused && limitarReproducaoAoTrechoRef.current) ||
            narracaoSegueAposVideoRef.current ||
            (audio && !audio.paused),
        );
      if (videoSoloTocando || narracaoAindaTocando) {
        pausarTrechoAtual();
        return;
      }
      iniciarTrechoDaCueNaPosicao(indice, modo);
    },
    [indiceTrechoTocando, modoPlayAtivo, iniciarTrechoDaCueNaPosicao, pausarTrechoAtual],
  );

  const marcarPontoRecorte = useCallback((campo: "inicio" | "fim") => {
    const video = videoRef.current;
    const indice = indiceAtivoRef.current;
    const atual = janelasRascunhoRef.current[indice];
    if (!video || !atual) return;
    const t = Math.max(0, video.currentTime || 0);
    const r = marcarExtremosDuracaoLivreRef.current
      ? marcarExtremoJanelaVideoCuePeloPontoUiTranscribrothers(
          janelasRascunhoRef.current,
          indice,
          campo,
          t,
        )
      : deslizarJanelaVideoCuePeloPontoUiTranscribrothers(
          janelasRascunhoRef.current,
          indice,
          campo,
          t,
        );
    if (!r.ok) {
      setErroRecorte(r.motivo);
      setAvisoRecorte(null);
      setAvisoAplicado(null);
      return;
    }
    setJanelasRascunho(r.janelas);
    setErroRecorte(null);
    setAvisoRecorte(r.avisoSobreposicao);
    setAvisoAplicado(null);
  }, []);

  const descartarRecorteRascunho = useCallback(() => {
    setJanelasRascunho(clonarJanelasTranscribrothers(janelas));
    setErroRecorte(null);
    setAvisoRecorte(null);
    setAvisoAplicado(null);
  }, [janelas]);

  const usarRecortesNoEditorEFechar = useCallback(() => {
    if (!onAplicarJanelas) {
      onFechar();
      return;
    }
    if (!rascunhoSujo) {
      onFechar();
      return;
    }
    const r = onAplicarJanelas(clonarJanelasTranscribrothers(janelasRascunho));
    if (!r.ok) {
      setErroRecorte(r.motivo);
      setAvisoRecorte(null);
      setAvisoAplicado(null);
      return;
    }
    // Fecha na hora: o editor já recebeu as janelas; o remux fica para o rodapé.
    onFechar();
  }, [onAplicarJanelas, onFechar, rascunhoSujo, janelasRascunho]);

  const tentarFechar = useCallback(() => {
    void (async () => {
      if (rascunhoSujo) {
        const ok = await pedirConfirmacao({
          titulo: "Descartar recortes?",
          mensagem: "Há recortes de tela não aplicados nesta modal. Fechar e descartar?",
          rotuloConfirmar: "Descartar e fechar",
          varianteConfirmar: "destrutiva",
        });
        if (!ok) return;
      }
      onFechar();
    })();
  }, [rascunhoSujo, onFechar, pedirConfirmacao]);

  useEffect(() => {
    if (!aberto) {
      limitarReproducaoAoTrechoRef.current = false;
      const video = videoRef.current;
      if (video) video.pause();
      pararAudioNarracao();
      return;
    }
    let cancelado = false;
    let tentativas = 0;
    const posicionarPausadoNaCue = () => {
      if (cancelado) return;
      const video = videoRef.current;
      const indice = clampIndiceCueTranscribrothers(
        indiceCueInicial,
        janelasRascunhoRef.current.length,
      );
      const j = janelasRascunhoRef.current[indice];
      if (video && j) {
        limitarReproducaoAoTrechoRef.current = false;
        narracaoSegueAposVideoRef.current = false;
        modoPlayRef.current = null;
        setModoPlayAtivo(null);
        setIndiceTrechoTocando(null);
        pararAudioNarracao();
        aplicarMuteVideoConformeEstado(null);
        video.pause();
        const ini = Math.max(0, j.inicioVideoSegundos);
        const aplicarSeek = () => {
          try {
            video.currentTime = ini;
          } catch {
            /* ignore seek prematuro */
          }
          video.pause();
        };
        if (video.readyState >= 1) {
          aplicarSeek();
        } else {
          const aoMeta = () => {
            video.removeEventListener("loadedmetadata", aoMeta);
            if (!cancelado) aplicarSeek();
          };
          video.addEventListener("loadedmetadata", aoMeta);
        }
        return;
      }
      tentativas += 1;
      if (tentativas < 40) {
        window.setTimeout(posicionarPausadoNaCue, 50);
      }
    };
    const id = window.setTimeout(posicionarPausadoNaCue, 50);
    return () => {
      cancelado = true;
      window.clearTimeout(id);
    };
  }, [aberto, indiceCueInicial, pararAudioNarracao, aplicarMuteVideoConformeEstado]);

  useEffect(() => {
    if (!aberto) return;
    let cancelado = false;
    let videoAnexado: HTMLVideoElement | null = null;

    const aoTempo = () => {
      const video = videoAnexado;
      if (!video || !limitarReproducaoAoTrechoRef.current || video.paused) return;
      const indice = indiceAtivoRef.current;
      const j = janelasRascunhoRef.current[indice];
      if (!j) return;
      const ini = Math.max(0, j.inicioVideoSegundos);
      const fim = Math.max(ini + 0.05, j.fimVideoSegundos);
      const t = video.currentTime || 0;
      if (t >= fim - MARGEM_FIM_TRECHO_SEGUNDOS) {
        const estacionarEm = Math.max(ini, fim - MARGEM_FIM_TRECHO_SEGUNDOS);
        const modo = modoPlayRef.current;
        limitarReproducaoAoTrechoRef.current = false;
        ignorarProximoPauseUiRef.current = true;
        video.pause();
        video.currentTime = estacionarEm;
        if (modo === "narracao") {
          // Vídeo para no fim da janela; a narração TTS continua (slot narrado costuma ser maior).
          narracaoSegueAposVideoRef.current = true;
          aplicarMuteVideoConformeEstado("narracao");
        } else {
          pararAudioNarracao();
          modoPlayRef.current = null;
          setModoPlayAtivo(null);
          setIndiceTrechoTocando(null);
          aplicarMuteVideoConformeEstado(null);
        }
      }
    };

    const aoPlay = () => {
      if (limitarReproducaoAoTrechoRef.current) {
        narracaoSegueAposVideoRef.current = false;
        setIndiceTrechoTocando(indiceAtivoRef.current);
        setModoPlayAtivo(modoPlayRef.current);
      }
    };

    const aoPause = () => {
      if (ignorarProximoPauseUiRef.current) {
        ignorarProximoPauseUiRef.current = false;
        return;
      }
      // Narração ainda tocando após o fim da janela: não corta o WAV.
      if (narracaoSegueAposVideoRef.current) return;
      if (!limitarReproducaoAoTrechoRef.current) {
        pararAudioNarracao();
        modoPlayRef.current = null;
        setModoPlayAtivo(null);
        setIndiceTrechoTocando(null);
      }
    };

    let idRaf = 0;
    const anexarQuandoPronto = () => {
      if (cancelado) return;
      const video = videoRef.current;
      if (!video) {
        idRaf = window.requestAnimationFrame(anexarQuandoPronto);
        return;
      }
      videoAnexado = video;
      aplicarMuteVideoConformeEstado(modoPlayRef.current);
      video.addEventListener("timeupdate", aoTempo);
      video.addEventListener("seeked", aoTempo);
      video.addEventListener("play", aoPlay);
      video.addEventListener("pause", aoPause);
    };
    anexarQuandoPronto();

    return () => {
      cancelado = true;
      window.cancelAnimationFrame(idRaf);
      if (videoAnexado) {
        videoAnexado.removeEventListener("timeupdate", aoTempo);
        videoAnexado.removeEventListener("seeked", aoTempo);
        videoAnexado.removeEventListener("play", aoPlay);
        videoAnexado.removeEventListener("pause", aoPause);
      }
    };
  }, [aberto, pararAudioNarracao, aplicarMuteVideoConformeEstado]);

  useEffect(() => {
    if (!aberto) return;
    const aoTeclar = (evento: KeyboardEvent) => {
      if (evento.key === "Escape") {
        evento.preventDefault();
        evento.stopPropagation();
        if (painelMaximizado) {
          setPainelMaximizado(false);
          return;
        }
        tentarFechar();
      }
    };
    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
  }, [aberto, painelMaximizado, tentarFechar]);

  const aoClicarSegmentoFaixa = useCallback(
    (indiceNaFaixa: number) => {
      const indiceGlobal = indicesMesmaOrigemRef.current[indiceNaFaixa];
      if (indiceGlobal == null || !janelasRascunhoRef.current[indiceGlobal]) return;
      iniciarTrechoDaCueNaPosicao(indiceGlobal, "video");
    },
    [iniciarTrechoDaCueNaPosicao],
  );

  if (!aberto || !jobId) return null;

  const conteudoRecorteNosControles =
    janelaAtiva && onAplicarJanelas ? (
      <div className="tb-modal-trecho-video-original-recorte-barra">
        <span className="tb-modal-trecho-video-original-recorte-divisor" aria-hidden="true" />
        <div className="tb-modal-trecho-video-original-recorte-grupo-janela">
          <p className="tb-modal-trecho-video-original-recorte-tempos">
            {formatarSegundosComoTimestampVttCurtoUiTranscribrothers(janelaAtiva.inicioVideoSegundos)}
            {" – "}
            {formatarSegundosComoTimestampVttCurtoUiTranscribrothers(janelaAtiva.fimVideoSegundos)}
            {" · "}
            {formatarDuracaoSegundosCurtaPortuguesUiTranscribrothers(
              Math.max(0, janelaAtiva.fimVideoSegundos - janelaAtiva.inicioVideoSegundos),
            ) || "—"}
            {cueAtivaSuja ? " · rascunho" : ""}
          </p>
          <button
            type="button"
            className="tb-modal-trecho-video-original-recorte-btn"
            title={
              marcarExtremosDuracaoLivre
                ? "Início = tempo atual; o fim permanece (a duração da tela muda)"
                : "Início = tempo atual; fim = início + duração da janela"
            }
            onClick={() => marcarPontoRecorte("inicio")}
          >
            Início
          </button>
          <button
            type="button"
            className="tb-modal-trecho-video-original-recorte-btn"
            title={
              marcarExtremosDuracaoLivre
                ? "Fim = tempo atual; o início permanece (a duração da tela muda)"
                : "Fim = tempo atual; início = fim − duração da janela"
            }
            onClick={() => marcarPontoRecorte("fim")}
          >
            Fim
          </button>
          <label
            className="tb-modal-trecho-video-original-recorte-audio"
            title="Se marcado, Início e Fim fixam extremos de forma independente (a duração da tela muda)"
          >
            <input
              type="checkbox"
              checked={marcarExtremosDuracaoLivre}
              onChange={(e) => setMarcarExtremosDuracaoLivre(e.target.checked)}
            />
            <span>Marcar extremos</span>
          </label>
          <details className="tb-modal-trecho-video-original-recorte-ajuda-details">
            <summary
              className="tb-modal-trecho-video-original-recorte-ajuda-resumo"
              aria-label="Como marcar o recorte"
              title="Como marcar o recorte"
            >
              ?
            </summary>
            <p className="tb-modal-trecho-video-original-recorte-ajuda">
              {marcarExtremosDuracaoLivre
                ? "Marcar extremos: início e fim no tempo atual de forma independente — a duração da tela muda e a faixa sob o progresso acompanha. Sobreposição com vizinhas só avisa. Não altera a duração da cue na timeline narrada."
                : "Duração fixa: marque início ou fim no tempo atual — o outro extremo acompanha mantendo a duração desta janela. Sobreposição com vizinhas só avisa — não bloqueia. Não altera a duração da cue na timeline narrada."}
            </p>
          </details>
        </div>
        <label className="tb-modal-trecho-video-original-recorte-audio tb-modal-trecho-video-original-recorte-audio--direita">
          <span className="tb-modal-trecho-video-original-recorte-divisor" aria-hidden="true" />
          <input
            type="checkbox"
            checked={audioOriginalAtivo}
            onChange={(e) => setAudioOriginalAtivo(e.target.checked)}
          />
          <span>Áudio da origem</span>
          <span className="tb-modal-trecho-video-original-recorte-divisor" aria-hidden="true" />
        </label>
      </div>
    ) : (
      <div className="tb-modal-trecho-video-original-recorte-barra">
        <label className="tb-modal-trecho-video-original-recorte-audio tb-modal-trecho-video-original-recorte-audio--direita">
          <span className="tb-modal-trecho-video-original-recorte-divisor" aria-hidden="true" />
          <input
            type="checkbox"
            checked={audioOriginalAtivo}
            onChange={(e) => setAudioOriginalAtivo(e.target.checked)}
          />
          <span>Áudio da origem</span>
          <span className="tb-modal-trecho-video-original-recorte-divisor" aria-hidden="true" />
        </label>
      </div>
    );

  return createPortal(
    <>
    <div
      className={
        "tb-modal-trecho-video-original-root" +
        (painelMaximizado ? " tb-modal-trecho-video-original-root--maximizado" : "")
      }
      role="presentation"
    >
      <audio
        ref={audioNarracaoRef}
        preload="none"
        onEnded={() => {
          narracaoSegueAposVideoRef.current = false;
          modoPlayRef.current = null;
          setModoPlayAtivo(null);
          setIndiceTrechoTocando(null);
          aplicarMuteVideoConformeEstado(null);
        }}
      />
      {!painelMaximizado ? (
        <button
          type="button"
          className="tb-modal-trecho-video-original-backdrop"
          aria-label="Fechar"
          onClick={tentarFechar}
        />
      ) : null}
      <div
        className={
          "tb-modal-trecho-video-original-painel" +
          (painelMaximizado ? " tb-modal-trecho-video-original-painel--maximizado" : "")
        }
        role="dialog"
        aria-modal="true"
        aria-labelledby={tituloId}
      >
        <header className="tb-modal-trecho-video-original-cabecalho">
          <div className="tb-modal-trecho-video-original-cabecalho-texto">
            <h2 id={tituloId} className="tb-modal-trecho-video-original-titulo">
              {tituloModal?.trim() ||
                `Trecho na origem — cue #${indiceAtivo + 1}`}
            </h2>
          </div>
          <div className="tb-modal-trecho-video-original-cabecalho-acoes">
            <button
              type="button"
              className="tb-modal-trecho-video-original-btn-icone"
              aria-label={painelMaximizado ? "Restaurar tamanho da janela" : "Maximizar janela"}
              title={painelMaximizado ? "Restaurar" : "Maximizar"}
              onClick={() => setPainelMaximizado((v) => !v)}
            >
              {painelMaximizado ? (
                <IconeRestaurarModalTrechoVideoOriginalTranscribrothers />
              ) : (
                <IconeMaximizarModalTrechoVideoOriginalTranscribrothers />
              )}
            </button>
            <button
              type="button"
              className="tb-modal-trecho-video-original-btn-icone"
              aria-label="Fechar"
              title="Fechar"
              onClick={tentarFechar}
            >
              ×
            </button>
          </div>
        </header>

        <div className="tb-modal-trecho-video-original-corpo">
          <div className="tb-modal-trecho-video-original-col-player">
            <div className="tb-modal-trecho-video-original-player-wrap">
              <ComponentePlayerVideoJobControlesCustomizadosEModalAmpliarTelaMaiorTranscribrothers
                jobId={jobId}
                videoRef={videoRef}
                urlVideoSrc={urlVideoSrc}
                keyVideo={urlVideoSrc || `entrada-${jobId}`}
                classNameVideo="tb-video tb-modal-trecho-video-original-video"
                classNameEnvoltorio="tb-modal-trecho-video-original-player-envoltorio"
                preloadVideo="metadata"
                exibirBotaoTelaMaior={false}
                exibirBotaoCapturarFrame={false}
                faixaCuesTimeline={faixaJanelasTimeline}
                indiceCueAtivaFaixaTimeline={indiceAtivoNaFaixaOrigem}
                aoClicarSegmentoFaixaCuesTimeline={aoClicarSegmentoFaixa}
                forcarUiComoTocando={indiceTrechoTocando !== null}
                conteudoExtraNaLinhaAcoesControles={conteudoRecorteNosControles}
              />
            </div>
            {erroRecorte || avisoRecorte || avisoAplicado ? (
              <div className="tb-modal-trecho-video-original-recorte-mensagens">
                {erroRecorte ? (
                  <p className="tb-modal-trecho-video-original-recorte-erro" role="alert">
                    {erroRecorte}
                  </p>
                ) : null}
                {avisoRecorte ? (
                  <p className="tb-modal-trecho-video-original-recorte-aviso" role="status">
                    {avisoRecorte}
                  </p>
                ) : null}
                {avisoAplicado ? (
                  <p className="tb-modal-trecho-video-original-recorte-ok" role="status">
                    {avisoAplicado}
                  </p>
                ) : null}
              </div>
            ) : null}
          </div>

          <aside
            className="tb-modal-trecho-video-original-col-trechos"
            aria-label="Trechos nesta origem de tela"
          >
            <p className="tb-modal-trecho-video-original-col-trechos-titulo">
              Nesta origem ({indicesMesmaOrigem.length}
              {janelasRascunho.length !== indicesMesmaOrigem.length
                ? ` de ${janelasRascunho.length}`
                : ""}
              )
            </p>
            <ul ref={listaTrechosRef} className="tb-modal-trecho-video-original-trechos-lista">
              {indicesMesmaOrigem.map((i) => {
                const j = janelasRascunho[i];
                if (!j) return null;
                const ativa = i === indiceAtivo;
                const tocandoVideo =
                  indiceTrechoTocando === i && modoPlayAtivo === "video";
                const tocandoNarracao =
                  indiceTrechoTocando === i && modoPlayAtivo === "narracao";
                const podeNarracao = Boolean(
                  resolverUrlAudioNarracaoCueTrechoOriginalUiTranscribrothers(
                    j,
                    i,
                    urlsAudioNarracaoPorIndice,
                  ),
                );
                const ini = Math.max(0, j.inicioVideoSegundos);
                const fim = Math.max(ini + 0.05, j.fimVideoSegundos);
                const duracao = fim - ini;
                const texto = (textosCues[i] || "").trim();
                const jBase = janelas[i];
                const cardSujo =
                  !!jBase &&
                  (Math.abs(j.inicioVideoSegundos - jBase.inicioVideoSegundos) > 1e-6 ||
                    Math.abs(j.fimVideoSegundos - jBase.fimVideoSegundos) > 1e-6);
                return (
                  <li
                    key={`trecho-original-${i}-${ini}-${fim}`}
                    ref={ativa ? cardAtivoRef : undefined}
                    className={
                      "tb-modal-trecho-video-original-trecho-card" +
                      (ativa ? " tb-modal-trecho-video-original-trecho-card--ativo" : "")
                    }
                    aria-current={ativa ? "true" : undefined}
                    onClick={() => selecionarCueSemPlay(i)}
                  >
                    <div className="tb-modal-trecho-video-original-trecho-topo">
                      <span className="tb-modal-trecho-video-original-trecho-numero">
                        #{i + 1}
                        {cardSujo ? " ·" : ""}
                      </span>
                      <span className="tb-modal-trecho-video-original-trecho-duracao">
                        {formatarDuracaoSegundosCurtaPortuguesUiTranscribrothers(duracao) || "—"}
                      </span>
                    </div>
                    <p className="tb-modal-trecho-video-original-trecho-tempos">
                      {formatarSegundosComoTimestampVttCurtoUiTranscribrothers(ini)}
                      {" – "}
                      {formatarSegundosComoTimestampVttCurtoUiTranscribrothers(fim)}
                    </p>
                    {texto || j.semNarracao ? (
                      <p className="tb-modal-trecho-video-original-trecho-texto">
                        {j.semNarracao ? "Sem narração" : texto}
                      </p>
                    ) : null}
                    <div className="tb-modal-trecho-video-original-trecho-acoes">
                      <button
                        type="button"
                        className={
                          "tb-modal-trecho-video-original-trecho-play" +
                          (tocandoVideo
                            ? " tb-modal-trecho-video-original-trecho-play--tocando"
                            : "")
                        }
                        title={
                          tocandoVideo
                            ? "Pausar este trecho"
                            : audioOriginalAtivo
                              ? "Reproduzir trecho (com áudio da origem)"
                              : "Reproduzir trecho (vídeo sem áudio da origem)"
                        }
                        onClick={(e) => {
                          e.stopPropagation();
                          alternarPlayTrecho(i, "video");
                        }}
                      >
                        {tocandoVideo ? "Pausar" : "Play"}
                      </button>
                      <button
                        type="button"
                        className={
                          "tb-modal-trecho-video-original-trecho-play tb-modal-trecho-video-original-trecho-play--narracao" +
                          (tocandoNarracao
                            ? " tb-modal-trecho-video-original-trecho-play--tocando"
                            : "")
                        }
                        disabled={!podeNarracao}
                        title={
                          !podeNarracao
                            ? j.semNarracao
                              ? "Cue sem narração"
                              : "Gere a prévia/Regenerar no editor ou aguarde o WAV gravado"
                            : tocandoNarracao
                              ? "Pausar trecho com narração"
                              : "Tocar trecho de tela com a narração TTS (vídeo mudo)"
                        }
                        onClick={(e) => {
                          e.stopPropagation();
                          if (!podeNarracao) return;
                          alternarPlayTrecho(i, "narracao");
                        }}
                      >
                        {tocandoNarracao ? "Pausar" : "Narração"}
                      </button>
                    </div>
                  </li>
                );
              })}
            </ul>
          </aside>
        </div>

        <footer className="tb-modal-trecho-video-original-rodape">
          {onAplicarJanelas ? (
            <>
              <button
                type="button"
                className="tb-modal-trecho-video-original-trecho-play"
                disabled={!rascunhoSujo}
                title="Descarta o rascunho e volta às janelas do editor"
                onClick={descartarRecorteRascunho}
              >
                Descartar
              </button>
              <button
                type="button"
                className="tb-primary"
                title={
                  rascunhoSujo
                    ? "Leva os recortes para o editor e fecha esta modal (sem remontar o MP4)"
                    : "Volta ao editor — nada mudou no rascunho"
                }
                onClick={usarRecortesNoEditorEFechar}
              >
                Usar no editor
              </button>
            </>
          ) : null}
          <button type="button" className="tb-modal-trecho-video-original-trecho-play" onClick={tentarFechar}>
            Fechar
          </button>
        </footer>
      </div>
    </div>
    {elementoDialogoConfirmacao}
    </>,
    document.body,
  );
}
