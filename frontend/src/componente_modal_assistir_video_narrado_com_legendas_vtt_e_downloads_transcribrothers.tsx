import { useCallback, useEffect, useId, useLayoutEffect, useMemo, useRef, useState } from "react";
import {
  cueTextoDifereDoNarradoTranscribrothers,
  cueVozDifereDaNarradaTranscribrothers,
  gerarPreviewTtsCueNarracaoTextoAtualJobApiTranscribrothers,
  listarJanelasVideoCuesNarracaoJobApiTranscribrothers,
  salvarJanelasVideoCuesNarracaoJobApiTranscribrothers,
  textoEfetivoParaTtsCueUiTranscribrothers,
  type JanelaVideoCueLocalUiTranscribrothers,
  avisarSobreposicaoSomenteCuesAlteradasUiTranscribrothers,
  validarJanelasVideoSemSobreposicaoNaUiTranscribrothers,
} from "./modulo_api_janelas_video_e_wavs_por_cue_narracao_job_transcribrothers.ts";
import { baixarVideoNarradoComLegendasQueimadasJobApiTranscribrothers } from "./modulo_api_baixar_video_narrado_com_legendas_queimadas_job_transcribrothers.ts";
import {
  listarVersoesVideoNarradoJobApiTranscribrothers,
  tornarVersaoVideoNarradoAtualJobApiTranscribrothers,
  type MetaVersaoVideoNarradoApiTranscribrothers,
} from "./modulo_api_listar_versoes_video_narrado_job_transcribrothers.ts";
import { obterUrlAssetLegendasVttAlinhadasDosStepsJsonJobTranscribrothers } from "./modulo_api_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers.ts";
import { salvarLegendasDocumentoAlinhadasVttEditadasJobApiTranscribrothers } from "./modulo_api_salvar_legendas_documento_alinhadas_vtt_editadas_job_transcribrothers.ts";
import type { JobStatus } from "./tipos_job_status_api_transcribrothers.ts";
import {
  carregarCuesWebVttDeUrlParaListaUiTranscribrothers,
  formatarSegundosComoTimestampVttCurtoUiTranscribrothers,
  type CueWebVttParaListaUiTranscribrothers,
} from "./modulo_util_parsear_webvtt_em_cues_para_lista_ui_transcribrothers.ts";
import { serializarCuesParaConteudoWebVttUiTranscribrothers } from "./modulo_util_serializar_cues_para_conteudo_webvtt_ui_transcribrothers.ts";
import {
  mapearTempoJanelaVideoOriginalParaTimelineCuePreviewUiTranscribrothers,
  mapearTempoTimelineCueParaJanelaVideoOriginalPreviewUiTranscribrothers,
  urlVideoEntradaJobParaPreviewUiTranscribrothers,
} from "./modulo_util_mapear_tempo_timeline_cue_para_janela_video_original_preview_ui_transcribrothers.ts";
import {
  ajustarFimCueTimelineAoAudioNarracaoUiTranscribrothers,
  cuePodeAjustarFimAoAudioNaTimelineUiTranscribrothers,
  cuePodeDeslocarNaTimelineUiTranscribrothers,
  DELTA_DESLOCAR_CUE_TIMELINE_NARRACAO_SEGUNDOS_TRANSCRIBROTHERS,
  deslocarCueTimelineNarracaoSemSobreporVizinhasUiTranscribrothers,
  posicionarInicioCueTimelineNarracaoSemSobreporVizinhasUiTranscribrothers,
} from "./modulo_util_ajustar_e_deslocar_cues_timeline_narracao_sem_sobreposicao_ui_transcribrothers.ts";
import {
  ComponenteMenuAcoesDropdownRodapeModalVideoNarradoTranscribrothers,
  resolverAcaoPrimariaContextualRodapeModalVideoNarradoTranscribrothers,
} from "./componente_menu_acoes_dropdown_rodape_modal_video_narrado_transcribrothers.tsx";
import {
  ComponentePlayerVideoJobControlesCustomizadosEModalAmpliarTelaMaiorTranscribrothers,
  type SegmentoFaixaCuesTimelinePlayerVideoTranscribrothers,
} from "./componente_player_video_job_controles_customizados_e_modal_ampliar_tela_maior_transcribrothers.tsx";
import { ComponenteModalTrechoCueNoVideoOriginalEntradaJobTranscribrothers } from "./componente_modal_trecho_cue_no_video_original_entrada_job_transcribrothers.tsx";
import { formatarDuracaoSegundosCurtaPortuguesUiTranscribrothers } from "./modulo_util_formatar_duracao_segundos_curta_portugues_ui_transcribrothers.ts";
import { obterDuracaoSegundosArquivoAudioPorUrlNavegadorTranscribrothers } from "./modulo_util_obter_duracao_segundos_arquivo_audio_por_url_navegador_transcribrothers.ts";
import { usarToastFeedbackAcoesUiTranscribrothers } from "./provedor_contexto_e_hook_uso_toasts_feedback_acoes_ui_transcribrothers.tsx";
import "./estilos_css_player_video_job_controles_customizados_e_modal_ampliar_tela_maior_transcribrothers.css";
import "./estilos_css_modal_assistir_video_narrado_com_legendas_vtt_e_downloads_transcribrothers.css";

type PreviewAudioCueFaixaTimelineUiTranscribrothers = {
  texto: string;
  /** Voz usada na prévia (precisa bater com a seleção atual para reaproveitar). */
  voz: string;
  duracaoSegundos: number;
  /** Object URL do blob TTS para reutilizar no play da cue / «Ouvir». */
  urlBlob: string;
};

function revogarUrlBlobPreviewCueTranscribrothers(url: string | null | undefined): void {
  if (typeof url === "string" && url.startsWith("blob:")) {
    URL.revokeObjectURL(url);
  }
}

function revogarTodosBlobsPreviewCuePorIndiceTranscribrothers(
  mapa: Record<number, PreviewAudioCueFaixaTimelineUiTranscribrothers>,
): void {
  for (const item of Object.values(mapa)) {
    revogarUrlBlobPreviewCueTranscribrothers(item.urlBlob);
  }
}

function previaAudioCueBateComTextoEVozUiTranscribrothers(
  preview: PreviewAudioCueFaixaTimelineUiTranscribrothers | undefined,
  texto: string,
  voz: string,
): boolean {
  if (!preview?.urlBlob) return false;
  if (preview.texto.trim() !== (texto || "").trim()) return false;
  return preview.voz.trim().toLowerCase() === (voz || "").trim().toLowerCase();
}

const CLASS_TEXTAREA_CUE_LEGENDA_VIDEO_NARRADO =
  "tb-modal-assistir-video-narrado-cue-textarea";

/** Altura mínima = CSS atual; cresce até caber o texto + 1 linha de folga (evita barra fantasma). */
function ajustarAlturaTextareaCueLegendaParaTextoCompletoTranscribrothers(
  el: HTMLTextAreaElement,
): void {
  const overflowYAnterior = el.style.overflowY;
  el.style.overflowY = "hidden";
  el.style.height = "auto";
  const estilos = window.getComputedStyle(el);
  const lineHeightPx = Number.parseFloat(estilos.lineHeight);
  const fontePx = Number.parseFloat(estilos.fontSize);
  const folgaUmaLinhaPx =
    Number.isFinite(lineHeightPx) && lineHeightPx > 0
      ? lineHeightPx
      : (Number.isFinite(fontePx) && fontePx > 0 ? fontePx * 1.4 : 16);
  el.style.height = `${el.scrollHeight + folgaUmaLinhaPx}px`;
  el.style.overflowY = overflowYAnterior;
}

function ajustarAlturasTodosTextareasCuesNaListaTranscribrothers(
  lista: HTMLUListElement | null,
): void {
  if (!lista) return;
  const textareas = lista.querySelectorAll<HTMLTextAreaElement>(
    `textarea.${CLASS_TEXTAREA_CUE_LEGENDA_VIDEO_NARRADO}`,
  );
  textareas.forEach((ta) => ajustarAlturaTextareaCueLegendaParaTextoCompletoTranscribrothers(ta));
}

export type PropsComponenteModalAssistirVideoNarradoComLegendasVttEDownloadsTranscribrothers = {
  aberto: boolean;
  jobId: string | null;
  urlVideoMp4: string;
  urlLegendasVtt: string | null;
  urlNarracaoWav: string | null;
  litellmModelTts?: string | null;
  regenerando: boolean;
  vozPadraoJob?: string | null;
  vozesDisponiveis?: Array<{ id: string; estilo: string }>;
  onFechar: () => void;
  onBaixarVideoMp4: () => void;
  onBaixarLegendasVtt: () => void;
  onBaixarNarracaoWav: () => void;
  onAtualizarNarracaoDasLegendas: () => void;
  onAplicarTemposJanelasAoVideo: () => void;
  onGerarNovaNarracao: () => void;
  /** Salva edições + TTS parcial se preciso + remonta MP4 na timeline atual. */
  onGerarVideoComEstasEdicoes: (payload: {
    cues: Array<{
      inicio_segundos: number;
      fim_segundos: number;
      texto: string;
      sem_narracao?: boolean;
      voz_tts?: string;
      texto_tts?: string;
      forcar_regenerar_tts?: boolean;
    }>;
    janelas: Array<{ inicio_video_segundos: number; fim_video_segundos: number }> | null;
  }) => void;
  onLegendasSalvas?: () => void | Promise<void>;
  /** Após «tornar atual» uma versão — atualiza URLs do job no pai. */
  onJobAtualizado?: (job: JobStatus) => void;
  /** Há vídeo de entrada no job (não é só-áudio) — habilita «Original» nas cues. */
  jobTemVideoEntrada?: boolean;
};

function rotuloOrigemVersaoVideoNarradoSelectUiTranscribrothers(origem: string): string {
  switch ((origem || "").trim()) {
    case "pipeline_completo":
      return "Do documento";
    case "edicoes_modal":
      return "Com edições";
    case "remux":
      return "Remux de janelas";
    case "atualizar_vtt":
      return "Legendas atualizadas";
    default:
      return origem.trim() || "Geração";
  }
}

function rotuloEscopoVersaoVideoNarradoSelectUiTranscribrothers(
  v: MetaVersaoVideoNarradoApiTranscribrothers,
): string {
  if (v.escopo_modo === "secoes" && Array.isArray(v.escopo_titulos) && v.escopo_titulos.length > 0) {
    const titulos = v.escopo_titulos.map((t) => String(t || "").trim()).filter(Boolean);
    if (titulos.length === 0) return "Seções selecionadas";
    const resumo =
      titulos.length <= 2
        ? titulos.join(", ")
        : `${titulos.slice(0, 2).join(", ")} (+${titulos.length - 2})`;
    const cortado = resumo.length > 48 ? `${resumo.slice(0, 45).trimEnd()}…` : resumo;
    return `Seções: ${cortado}`;
  }
  return "Documento completo";
}

function SkeletonCuesListaVideoNarradoUiTranscribrothers({ quantidade = 4 }: { quantidade?: number }) {
  return (
    <ul className="tb-modal-assistir-video-narrado-skeleton-cues" aria-busy="true" aria-label="Carregando legendas">
      {Array.from({ length: quantidade }, (_, i) => (
        <li key={i} className="tb-modal-assistir-video-narrado-skeleton-cue">
          <span className="tb-modal-assistir-video-narrado-skeleton-linha tb-modal-assistir-video-narrado-skeleton-linha--curta tb-modal-assistir-video-narrado-skeleton-pulse" />
          <span className="tb-modal-assistir-video-narrado-skeleton-linha tb-modal-assistir-video-narrado-skeleton-linha--longa tb-modal-assistir-video-narrado-skeleton-pulse" />
          <span className="tb-modal-assistir-video-narrado-skeleton-linha tb-modal-assistir-video-narrado-skeleton-linha--media tb-modal-assistir-video-narrado-skeleton-pulse" />
        </li>
      ))}
    </ul>
  );
}

function rotuloOpcaoVersaoVideoNarradoUiTranscribrothers(
  v: MetaVersaoVideoNarradoApiTranscribrothers,
  ehAtual: boolean,
): string {
  const data = v.criado_em
    ? new Date(v.criado_em).toLocaleString("pt-BR", {
        day: "2-digit",
        month: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
      })
    : "";
  const dur = Math.max(0, Math.round(Number(v.duracao_segundos) || 0));
  const mm = Math.floor(dur / 60);
  const ss = String(dur % 60).padStart(2, "0");
  const partes = [v.id];
  if (ehAtual) partes.push("Atual");
  partes.push(rotuloEscopoVersaoVideoNarradoSelectUiTranscribrothers(v));
  partes.push(rotuloOrigemVersaoVideoNarradoSelectUiTranscribrothers(v.origem));
  if (data) partes.push(data);
  partes.push(`${mm}:${ss}`);
  return partes.join(" · ");
}

function cuesEstaoSujasEmRelacaoAoOriginalTranscribrothers(
  atuais: CueWebVttParaListaUiTranscribrothers[],
  originais: CueWebVttParaListaUiTranscribrothers[],
): boolean {
  if (atuais.length !== originais.length) return true;
  for (let i = 0; i < atuais.length; i++) {
    if (
      atuais[i].texto !== originais[i].texto ||
      (atuais[i].textoTts || "") !== (originais[i].textoTts || "") ||
      atuais[i].inicioSegundos !== originais[i].inicioSegundos ||
      atuais[i].fimSegundos !== originais[i].fimSegundos
    ) {
      return true;
    }
  }
  return false;
}

/** Tempos da timeline diferem do VTT original (arraste/ajuste) — o áudio do MP4 não acompanha. */
function temposCuesDeslocadosEmRelacaoAoOriginalTranscribrothers(
  atuais: CueWebVttParaListaUiTranscribrothers[],
  originais: CueWebVttParaListaUiTranscribrothers[],
): boolean {
  if (atuais.length !== originais.length) return true;
  for (let i = 0; i < atuais.length; i++) {
    if (
      atuais[i].inicioSegundos !== originais[i].inicioSegundos ||
      atuais[i].fimSegundos !== originais[i].fimSegundos
    ) {
      return true;
    }
  }
  return false;
}

function indiceCueNoInstanteTimelineUiTranscribrothers(
  cuesLista: CueWebVttParaListaUiTranscribrothers[],
  tempoSegundos: number,
): number {
  for (let i = 0; i < cuesLista.length; i++) {
    const c = cuesLista[i];
    if (tempoSegundos >= c.inicioSegundos && tempoSegundos < c.fimSegundos) return i;
  }
  for (let i = 0; i < cuesLista.length; i++) {
    if (tempoSegundos < cuesLista[i].inicioSegundos) return i;
  }
  return cuesLista.length > 0 ? cuesLista.length - 1 : -1;
}

function janelasEstaoSujasTranscribrothers(
  atuais: JanelaVideoCueLocalUiTranscribrothers[],
  originais: JanelaVideoCueLocalUiTranscribrothers[],
): boolean {
  if (atuais.length !== originais.length) return true;
  for (let i = 0; i < atuais.length; i++) {
    if (
      atuais[i].inicioVideoSegundos !== originais[i].inicioVideoSegundos ||
      atuais[i].fimVideoSegundos !== originais[i].fimVideoSegundos ||
      Boolean(atuais[i].semNarracao) !== Boolean(originais[i].semNarracao)
    ) {
      return true;
    }
  }
  return false;
}

export function ComponenteModalAssistirVideoNarradoComLegendasVttEDownloadsTranscribrothers({
  aberto,
  jobId,
  urlVideoMp4,
  urlLegendasVtt,
  urlNarracaoWav,
  litellmModelTts,
  regenerando,
  vozPadraoJob = "Kore",
  vozesDisponiveis = [],
  onFechar,
  onBaixarVideoMp4,
  onBaixarLegendasVtt,
  onBaixarNarracaoWav,
  onAtualizarNarracaoDasLegendas,
  onAplicarTemposJanelasAoVideo,
  onGerarNovaNarracao,
  onGerarVideoComEstasEdicoes,
  onLegendasSalvas,
  onJobAtualizado,
  jobTemVideoEntrada = false,
}: PropsComponenteModalAssistirVideoNarradoComLegendasVttEDownloadsTranscribrothers) {
  const tituloId = useId();
  const { pushToast, pushToastProgresso, atualizarToastProgresso, removerToast } =
    usarToastFeedbackAcoesUiTranscribrothers();
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const audioCueRef = useRef<HTMLAudioElement | null>(null);
  const cueAtivaRef = useRef<HTMLLIElement | null>(null);
  const listaCuesRef = useRef<HTMLUListElement | null>(null);
  /** Enquanto definido, a reprodução solo/auxiliar está amarrada a esta cue. */
  const indiceCueReproducaoSoloRef = useRef<number | null>(null);
  /** Play contínuo com WAV nas posições atuais das cues (vídeo pausado; sem mutar volume). */
  const reproducaoContinuaPorWavRef = useRef(false);
  const cuesRef = useRef<CueWebVttParaListaUiTranscribrothers[]>([]);
  const janelasRef = useRef<JanelaVideoCueLocalUiTranscribrothers[]>([]);
  const cuesOriginaisRef = useRef<CueWebVttParaListaUiTranscribrothers[]>([]);
  const tocarNarracaoWavDaCueRef = useRef<
    (
      indice: number,
      opcoes?: {
        continuo?: boolean;
        retomarSePossivel?: boolean;
        partirDoTempoTimelineSegundos?: number;
      },
    ) => boolean
  >(() => false);
  /**
   * Solo da cue no vídeo de entrada (janela de tela + WAV), sem remux.
   * Quando ativo, o player troca o src para `/video` do job.
   */
  const previewRecorteTelaAtivoRef = useRef(false);
  const [previewRecorteTelaAtivo, setPreviewRecorteTelaAtivo] = useState(false);
  /** Duração do MP4 narrado (cache) — a barra virtual usa isso no preview de recorte. */
  const [duracaoMp4NarradoSegundos, setDuracaoMp4NarradoSegundos] = useState(0);
  /** Após pausar o vídeo no fim da janela, o WAV ainda pode continuar. */
  const narracaoSegueAposJanelaPreviewRef = useRef(false);
  const pedidoPlayAposTrocaSrcPreviewRef = useRef<{
    indice: number;
    continuo: boolean;
    offsetAudio: number;
    tempoJanelaSegundos: number;
    urlAudio: string | null;
    semNarracao: boolean;
  } | null>(null);
  const pedidoSeekNarradoAposSairPreviewRef = useRef<number | null>(null);
  /** Cue escolhida no clique (destaque estável; evita “pular” para a próxima no limite fim==próximo início). */
  const [indiceCueSelecionadaSolo, setIndiceCueSelecionadaSolo] = useState<number | null>(null);
  /** Modal «trecho no vídeo original» aberta nesta cue (índice 0-based). */
  const [indiceCueModalVideoOriginal, setIndiceCueModalVideoOriginal] = useState<number | null>(
    null,
  );
  const [versoesVideoNarrado, setVersoesVideoNarrado] = useState<
    MetaVersaoVideoNarradoApiTranscribrothers[]
  >([]);
  const [versaoAtualVideoNarradoId, setVersaoAtualVideoNarradoId] = useState<string | null>(null);
  const [trocandoVersaoVideoNarrado, setTrocandoVersaoVideoNarrado] = useState(false);
  const [cues, setCues] = useState<CueWebVttParaListaUiTranscribrothers[]>([]);
  cuesRef.current = cues;
  const [cuesOriginais, setCuesOriginais] = useState<CueWebVttParaListaUiTranscribrothers[]>([]);
  cuesOriginaisRef.current = cuesOriginais;
  const [janelas, setJanelas] = useState<JanelaVideoCueLocalUiTranscribrothers[]>([]);
  janelasRef.current = janelas;
  const [janelasOriginais, setJanelasOriginais] = useState<JanelaVideoCueLocalUiTranscribrothers[]>(
    [],
  );
  const [carregandoCues, setCarregandoCues] = useState(false);
  const [erroCues, setErroCues] = useState<string | null>(null);
  const [tempoAtualSegundos, setTempoAtualSegundos] = useState(0);
  const [legendasNoVideo, setLegendasNoVideo] = useState(true);
  const [salvandoLegendas, setSalvandoLegendas] = useState(false);
  const [salvandoJanelas, setSalvandoJanelas] = useState(false);
  const [baixandoVideoComLegendasQueimadas, setBaixandoVideoComLegendasQueimadas] = useState(false);
  const [versaoCacheTrackVtt, setVersaoCacheTrackVtt] = useState(0);
  const [indiceAudioTocando, setIndiceAudioTocando] = useState<number | null>(null);
  const [indiceAudioGerandoPreview, setIndiceAudioGerandoPreview] = useState<number | null>(null);
  const [menuRodapeAbertoId, setMenuRodapeAbertoId] = useState<string | null>(null);
  /** Índices com o campo «Fala (TTS)» expandido manualmente (por padrão fica colapsado). */
  const [indicesFalaTtsExpandidos, setIndicesFalaTtsExpandidos] = useState<Record<number, true>>(
    {},
  );
  /** Durações dos WAVs gravados por índice de cue (slot do vídeo narrado). */
  const [duracoesWavPorIndice, setDuracoesWavPorIndice] = useState<Record<number, number>>({});
  /** Prévia TTS medida para o texto atual (ainda não aplicada ao vídeo). */
  const [previewAudioPorIndice, setPreviewAudioPorIndice] = useState<
    Record<number, PreviewAudioCueFaixaTimelineUiTranscribrothers>
  >({});
  const previewAudioPorIndiceRef = useRef(previewAudioPorIndice);
  previewAudioPorIndiceRef.current = previewAudioPorIndice;

  const urlTrackVttComCacheBust = useMemo(() => {
    if (!urlLegendasVtt) return null;
    const sep = urlLegendasVtt.includes("?") ? "&" : "?";
    return `${urlLegendasVtt}${sep}v=${versaoCacheTrackVtt || "0"}`;
  }, [urlLegendasVtt, versaoCacheTrackVtt]);

  /** VTT ao vivo a partir dos cues editados — a legenda no vídeo acompanha o texto sem precisar salvar. */
  const [urlTrackVttAoVivoBlob, setUrlTrackVttAoVivoBlob] = useState<string | null>(null);
  const urlTrackVttAoVivoBlobRef = useRef<string | null>(null);

  useEffect(() => {
    if (urlTrackVttAoVivoBlobRef.current) {
      URL.revokeObjectURL(urlTrackVttAoVivoBlobRef.current);
      urlTrackVttAoVivoBlobRef.current = null;
    }
    if (!aberto || cues.length === 0) {
      setUrlTrackVttAoVivoBlob(null);
      return;
    }
    const conteudo = serializarCuesParaConteudoWebVttUiTranscribrothers(cues);
    const url = URL.createObjectURL(new Blob([conteudo], { type: "text/vtt" }));
    urlTrackVttAoVivoBlobRef.current = url;
    setUrlTrackVttAoVivoBlob(url);
    return () => {
      if (urlTrackVttAoVivoBlobRef.current === url) {
        URL.revokeObjectURL(url);
        urlTrackVttAoVivoBlobRef.current = null;
      }
    };
  }, [aberto, cues]);

  const urlTrackVttParaVideo =
    urlTrackVttAoVivoBlob || urlTrackVttComCacheBust;

  const sujas = useMemo(
    () => cuesEstaoSujasEmRelacaoAoOriginalTranscribrothers(cues, cuesOriginais),
    [cues, cuesOriginais],
  );
  const temposCuesDeslocados = useMemo(
    () => temposCuesDeslocadosEmRelacaoAoOriginalTranscribrothers(cues, cuesOriginais),
    [cues, cuesOriginais],
  );
  const janelasSujas = useMemo(
    () => janelasEstaoSujasTranscribrothers(janelas, janelasOriginais),
    [janelas, janelasOriginais],
  );
  /** Exclusão, «sem narração», texto ou tempos: o áudio embutido do MP4 não vale mais no preview. */
  const audioDoMp4NaoRefleteEdicoesLocais = sujas || temposCuesDeslocados || janelasSujas;

  const urlVideoEntradaJob = jobId
    ? urlVideoEntradaJobParaPreviewUiTranscribrothers(jobId)
    : "";
  const urlVideoPlayerEfetivo =
    previewRecorteTelaAtivo && jobTemVideoEntrada && urlVideoEntradaJob
      ? urlVideoEntradaJob
      : urlVideoMp4;

  const duracaoTimelineNarradaParaBarraUi = useMemo(() => {
    let maxCue = 0;
    for (const c of cues) {
      if (c.fimSegundos > maxCue) maxCue = c.fimSegundos;
    }
    return Math.max(duracaoMp4NarradoSegundos, maxCue, 0.1);
  }, [cues, duracaoMp4NarradoSegundos]);

  const definirPreviewRecorteTelaAtivoUi = useCallback((ativo: boolean) => {
    previewRecorteTelaAtivoRef.current = ativo;
    setPreviewRecorteTelaAtivo(ativo);
    if (!ativo) {
      narracaoSegueAposJanelaPreviewRef.current = false;
      pedidoPlayAposTrocaSrcPreviewRef.current = null;
    }
  }, []);

  /** Tempo da barra/cues durante preview: timeline narrada, não o relógio do vídeo original. */
  const lerTempoVirtualTimelinePreviewRecorteUi = useCallback((indiceSolo: number): number | null => {
    const cue = cuesRef.current[indiceSolo];
    const j = janelasRef.current[indiceSolo];
    if (!cue || !j) return null;
    const audio = audioCueRef.current;
    if (audio && !audio.paused && !j.semNarracao) {
      return Math.min(
        Math.max(cue.inicioSegundos + (audio.currentTime || 0), cue.inicioSegundos),
        Math.max(cue.inicioSegundos, cue.fimSegundos - 0.05),
      );
    }
    const video = videoRef.current;
    const tJanela = video?.currentTime ?? j.inicioVideoSegundos;
    return mapearTempoJanelaVideoOriginalParaTimelineCuePreviewUiTranscribrothers(
      tJanela,
      cue.inicioSegundos,
      cue.fimSegundos,
      j.inicioVideoSegundos,
      j.fimVideoSegundos,
    );
  }, []);

  const limparTodosPreviewsAudioCue = useCallback(() => {
    revogarTodosBlobsPreviewCuePorIndiceTranscribrothers(previewAudioPorIndiceRef.current);
    setPreviewAudioPorIndice({});
  }, []);

  /** Cacheia a duração do MP4 narrado enquanto ele está no player (fora do preview de recorte). */
  useEffect(() => {
    if (!aberto || previewRecorteTelaAtivo) return;
    const video = videoRef.current;
    if (!video) return;
    const ler = () => {
      const d = video.duration;
      if (Number.isFinite(d) && d > 0) setDuracaoMp4NarradoSegundos(d);
    };
    ler();
    video.addEventListener("loadedmetadata", ler);
    video.addEventListener("durationchange", ler);
    return () => {
      video.removeEventListener("loadedmetadata", ler);
      video.removeEventListener("durationchange", ler);
    };
  }, [aberto, previewRecorteTelaAtivo, urlVideoMp4]);

  const resolverUrlAudioNarracaoDaCueParaPlaybackUi = useCallback((indice: number): string | null => {
    const cue = cuesRef.current[indice];
    const j = janelasRef.current[indice];
    if (!cue) return null;
    const textoFala = textoEfetivoParaTtsCueUiTranscribrothers(cue.texto, cue.textoTts);
    const textoDifere =
      !!j && cueTextoDifereDoNarradoTranscribrothers(textoFala, j.textoNarrado || "");
    const vozDifere =
      !!j && cueVozDifereDaNarradaTranscribrothers(j.vozTts || "", j.vozNarrada || "");
    const audioDifere = textoDifere || vozDifere;
    const preview = previewAudioPorIndiceRef.current[indice];
    const previewBate = previaAudioCueBateComTextoEVozUiTranscribrothers(
      preview,
      textoFala,
      j?.vozTts || "",
    );
    if (audioDifere) {
      return previewBate && preview ? preview.urlBlob : null;
    }
    if (j?.temWav && j.urlWav) return j.urlWav;
    if (previewBate && preview) return preview.urlBlob;
    return null;
  }, []);

  const pararAudioCue = useCallback(() => {
    const a = audioCueRef.current;
    if (a) {
      a.pause();
      a.removeAttribute("src");
      a.load();
    }
    setIndiceAudioTocando(null);
    indiceCueReproducaoSoloRef.current = null;
    reproducaoContinuaPorWavRef.current = false;
  }, []);

  useEffect(() => {
    if (!aberto) {
      pararAudioCue();
      limparTodosPreviewsAudioCue();
      setMenuRodapeAbertoId(null);
      setVersoesVideoNarrado([]);
      setVersaoAtualVideoNarradoId(null);
      setTrocandoVersaoVideoNarrado(false);
      setIndiceCueModalVideoOriginal(null);
    }
  }, [aberto, limparTodosPreviewsAudioCue, pararAudioCue]);

  const carregarVersoesVideoNarradoUi = useCallback(async () => {
    if (!jobId) {
      setVersoesVideoNarrado([]);
      setVersaoAtualVideoNarradoId(null);
      return;
    }
    try {
      const resp = await listarVersoesVideoNarradoJobApiTranscribrothers(jobId);
      setVersoesVideoNarrado(resp.versoes ?? []);
      setVersaoAtualVideoNarradoId(resp.versao_atual_id ?? null);
    } catch {
      setVersoesVideoNarrado([]);
      setVersaoAtualVideoNarradoId(null);
    }
  }, [jobId]);

  useEffect(() => {
    if (!aberto || !jobId) return;
    void carregarVersoesVideoNarradoUi();
  }, [aberto, jobId, urlVideoMp4, carregarVersoesVideoNarradoUi]);

  const trocarVersaoVideoNarradoUi = useCallback(
    async (versaoId: string) => {
      if (!jobId || !versaoId || versaoId === versaoAtualVideoNarradoId || trocandoVersaoVideoNarrado) {
        return;
      }
      const temEdicoesLocais =
        cuesEstaoSujasEmRelacaoAoOriginalTranscribrothers(cuesRef.current, cuesOriginaisRef.current) ||
        janelasEstaoSujasTranscribrothers(janelasRef.current, janelasOriginais);
      if (temEdicoesLocais) {
        const ok = window.confirm(
          "Há edições locais não salvas nesta versão. Trocar de versão descarta essas alterações. Continuar?",
        );
        if (!ok) return;
      }
      setTrocandoVersaoVideoNarrado(true);
      try {
        pararAudioCue();
        limparTodosPreviewsAudioCue();
        const j = await tornarVersaoVideoNarradoAtualJobApiTranscribrothers(jobId, versaoId);
        setVersaoAtualVideoNarradoId(versaoId);
        setVersaoCacheTrackVtt(Date.now());
        onJobAtualizado?.(j);

        // Recarrega cues com a URL fresca do job (não depende do effect de props, que podia
        // ficar preso em pipeline.url_asset_vtt obsoleto e deixar o skeleton infinito).
        const urlVttFresca = obterUrlAssetLegendasVttAlinhadasDosStepsJsonJobTranscribrothers(
          j.steps_json as Record<string, unknown> | null | undefined,
        );
        if (urlVttFresca) {
          setCarregandoCues(true);
          setErroCues(null);
          try {
            const lista = await carregarCuesWebVttDeUrlParaListaUiTranscribrothers(urlVttFresca);
            setCues(lista);
            setCuesOriginais(lista.map((c) => ({ ...c })));
          } catch (e: unknown) {
            setCues([]);
            setCuesOriginais([]);
            setErroCues(e instanceof Error ? e.message : String(e));
          } finally {
            setCarregandoCues(false);
          }
        }

        await carregarVersoesVideoNarradoUi();
        pushToast(`Versão ${versaoId} definida como atual.`, "success");
      } catch (e) {
        pushToast(e instanceof Error ? e.message : String(e), "error");
      } finally {
        setTrocandoVersaoVideoNarrado(false);
      }
    },
    [
      jobId,
      versaoAtualVideoNarradoId,
      trocandoVersaoVideoNarrado,
      janelasOriginais,
      pararAudioCue,
      limparTodosPreviewsAudioCue,
      onJobAtualizado,
      carregarVersoesVideoNarradoUi,
      pushToast,
    ],
  );

  // Trava a barra de rolagem da página de baixo enquanto a edição está aberta.
  useEffect(() => {
    if (!aberto) return;
    const html = document.documentElement;
    const body = document.body;
    const scrollY = window.scrollY;
    html.setAttribute("data-tb-pagina-video-narrado-aberta", "");
    body.setAttribute("data-tb-pagina-video-narrado-aberta", "");
    body.style.top = `-${scrollY}px`;
    return () => {
      html.removeAttribute("data-tb-pagina-video-narrado-aberta");
      body.removeAttribute("data-tb-pagina-video-narrado-aberta");
      body.style.top = "";
      window.scrollTo(0, scrollY);
    };
  }, [aberto]);

  useEffect(() => {
    if (regenerando || salvandoLegendas || salvandoJanelas) {
      setMenuRodapeAbertoId(null);
    }
  }, [regenerando, salvandoLegendas, salvandoJanelas]);

  useEffect(() => {
    if (!aberto) return;
    const aoTeclar = (evento: KeyboardEvent) => {
      if (evento.key !== "Escape") return;
      // Modal do trecho original trata o Escape sozinha.
      if (indiceCueModalVideoOriginal !== null) return;
      if (!regenerando && !salvandoLegendas && !salvandoJanelas) {
        onFechar();
      }
    };
    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
  }, [
    aberto,
    onFechar,
    regenerando,
    salvandoLegendas,
    salvandoJanelas,
    indiceCueModalVideoOriginal,
  ]);

  useEffect(() => {
    if (!aberto) {
      setCues([]);
      setCuesOriginais([]);
      setJanelas([]);
      setJanelasOriginais([]);
      setErroCues(null);
      setCarregandoCues(false);
      setTempoAtualSegundos(0);
      setSalvandoLegendas(false);
      setSalvandoJanelas(false);
      setIndicesFalaTtsExpandidos({});
      return;
    }
    if (!urlLegendasVtt) {
      setCues([]);
      setCuesOriginais([]);
      setErroCues(null);
      setCarregandoCues(false);
      return;
    }
    let cancelado = false;
    setCarregandoCues(true);
    setErroCues(null);
    void carregarCuesWebVttDeUrlParaListaUiTranscribrothers(urlLegendasVtt)
      .then((lista) => {
        if (!cancelado) {
          setCues(lista);
          setCuesOriginais(lista.map((c) => ({ ...c })));
          setCarregandoCues(false);
        }
      })
      .catch((e: unknown) => {
        if (!cancelado) {
          setCues([]);
          setCuesOriginais([]);
          setCarregandoCues(false);
          setErroCues(e instanceof Error ? e.message : String(e));
        }
      });
    return () => {
      cancelado = true;
    };
  }, [aberto, urlLegendasVtt]);

  useEffect(() => {
    if (!aberto || !jobId) {
      setJanelas([]);
      setJanelasOriginais([]);
      setDuracoesWavPorIndice({});
      limparTodosPreviewsAudioCue();
      return;
    }
    let cancelado = false;
    void listarJanelasVideoCuesNarracaoJobApiTranscribrothers(jobId)
      .then((resp) => {
        if (cancelado) return;
        const padrao =
          String(resp.voz_tts_padrao_job || vozPadraoJob || "Kore").trim() || "Kore";
        const lista: JanelaVideoCueLocalUiTranscribrothers[] = resp.cues.map((c) => {
          const voz = String(c.voz_tts || "").trim() || padrao;
          const textoTts = String(c.texto_tts || "").trim();
          return {
            inicioVideoSegundos: c.inicio_video_segundos,
            fimVideoSegundos: c.fim_video_segundos,
            temWav: c.tem_wav,
            urlWav: c.url_wav,
            textoNarrado: textoEfetivoParaTtsCueUiTranscribrothers(c.texto || "", textoTts),
            textoTtsNarrado: textoTts,
            semNarracao: Boolean(c.sem_narracao),
            vozTts: voz,
            vozNarrada: voz,
          };
        });
        setJanelas(lista);
        setJanelasOriginais(lista.map((j) => ({ ...j })));
        const aplicarTextoTtsDoManifesto = (
          prev: CueWebVttParaListaUiTranscribrothers[],
        ): CueWebVttParaListaUiTranscribrothers[] =>
          prev.map((cue, i) => {
            const tts = String(resp.cues[i]?.texto_tts || "").trim();
            if ((cue.textoTts || "") === tts) return cue;
            return { ...cue, textoTts: tts };
          });
        setCues(aplicarTextoTtsDoManifesto);
        setCuesOriginais(aplicarTextoTtsDoManifesto);
        limparTodosPreviewsAudioCue();
      })
      .catch(() => {
        if (!cancelado) {
          setJanelas([]);
          setJanelasOriginais([]);
          setDuracoesWavPorIndice({});
          limparTodosPreviewsAudioCue();
        }
      });
    return () => {
      cancelado = true;
    };
  }, [aberto, jobId, urlVideoMp4, limparTodosPreviewsAudioCue, vozPadraoJob]);

  useEffect(() => {
    if (!aberto || janelas.length === 0) {
      setDuracoesWavPorIndice({});
      return;
    }
    let cancelado = false;
    const stamp = Date.now();
    void (async () => {
      const entradas = await Promise.all(
        janelas.map(async (j, indice) => {
          if (!j.temWav || !j.urlWav) return [indice, null] as const;
          try {
            const dur = await obterDuracaoSegundosArquivoAudioPorUrlNavegadorTranscribrothers(
              `${j.urlWav}?v=${stamp}`,
            );
            return [indice, dur] as const;
          } catch {
            return [indice, null] as const;
          }
        }),
      );
      if (cancelado) return;
      const mapa: Record<number, number> = {};
      for (const [indice, dur] of entradas) {
        if (typeof dur === "number" && dur > 0) mapa[indice] = dur;
      }
      setDuracoesWavPorIndice(mapa);
    })();
    return () => {
      cancelado = true;
    };
  }, [aberto, janelas]);

  useEffect(() => {
    if (!aberto) {
      indiceCueReproducaoSoloRef.current = null;
      setIndiceCueSelecionadaSolo(null);
      previewRecorteTelaAtivoRef.current = false;
      setPreviewRecorteTelaAtivo(false);
      narracaoSegueAposJanelaPreviewRef.current = false;
      pedidoPlayAposTrocaSrcPreviewRef.current = null;
      pedidoSeekNarradoAposSairPreviewRef.current = null;
      return;
    }
    const video = videoRef.current;
    if (!video) return;
    const aoTempo = () => {
      const t = video.currentTime || 0;
      const indiceSolo = indiceCueReproducaoSoloRef.current;
      const previewAtivo = previewRecorteTelaAtivoRef.current;
      if (previewAtivo && indiceSolo !== null) {
        const tVirtual = lerTempoVirtualTimelinePreviewRecorteUi(indiceSolo);
        setTempoAtualSegundos(tVirtual ?? t);
      } else {
        setTempoAtualSegundos(t);
      }
      if (indiceSolo === null || video.paused) return;
      const cueSolo = cuesRef.current[indiceSolo];
      if (!cueSolo) return;
      const jSolo = janelasRef.current[indiceSolo];
      const previewJanela = previewAtivo && Boolean(jSolo);
      // Preview de recorte / cue sem narração: limites na janela de tela (vídeo original ou MP4).
      const inicioLimite =
        previewJanela || jSolo?.semNarracao
          ? (jSolo?.inicioVideoSegundos ?? cueSolo.inicioSegundos)
          : cueSolo.inicioSegundos;
      const fimLimite =
        previewJanela || jSolo?.semNarracao
          ? (jSolo?.fimVideoSegundos ?? cueSolo.fimSegundos)
          : cueSolo.fimSegundos;
      // Para um pouco antes do fim: em cues contíguas, t === fim cai no início da próxima.
      const margemFimSegundos = 0.05;
      if (t >= fimLimite - margemFimSegundos) {
        const estacionarEm = Math.max(inicioLimite, fimLimite - margemFimSegundos);
        video.pause();
        video.currentTime = estacionarEm;
        if (previewJanela) {
          const tVirtual = lerTempoVirtualTimelinePreviewRecorteUi(indiceSolo);
          setTempoAtualSegundos(
            tVirtual ??
              Math.max(cueSolo.inicioSegundos, cueSolo.fimSegundos - margemFimSegundos),
          );
        } else {
          setTempoAtualSegundos(estacionarEm);
        }
        const audio = audioCueRef.current;
        const audioAindaToca = Boolean(audio && !audio.paused);
        // Preview com narração: vídeo para no fim da janela; WAV pode seguir.
        if (previewJanela && !jSolo?.semNarracao && audioAindaToca) {
          narracaoSegueAposJanelaPreviewRef.current = true;
          return;
        }
        if (jSolo?.semNarracao && !previewJanela) video.muted = false;
        if (audio && !audio.paused) audio.pause();
        setIndiceAudioTocando(null);
        const continuo = reproducaoContinuaPorWavRef.current;
        // Cue sem narração (só vídeo) ou preview mudo: avança a cadeia no fim da janela.
        if (continuo && (jSolo?.semNarracao || (previewJanela && !audioAindaToca))) {
          const proximo = indiceSolo + 1;
          if (proximo < cuesRef.current.length) {
            tocarNarracaoWavDaCueRef.current(proximo, { continuo: true });
            return;
          }
          reproducaoContinuaPorWavRef.current = false;
          indiceCueReproducaoSoloRef.current = null;
          if (previewJanela) {
            pedidoSeekNarradoAposSairPreviewRef.current = Math.max(
              0,
              cueSolo.inicioSegundos,
            );
            definirPreviewRecorteTelaAtivoUi(false);
          }
          return;
        }
        if (previewJanela && audioAindaToca) {
          /* WAV ainda toca — solo permanece até onEnded do áudio */
          return;
        }
        if (previewJanela) {
          indiceCueReproducaoSoloRef.current = null;
          pedidoSeekNarradoAposSairPreviewRef.current = Math.max(0, cueSolo.inicioSegundos);
          definirPreviewRecorteTelaAtivoUi(false);
          return;
        }
        if (!continuo) {
          /* solo no MP4 narrado: mantém destaque */
        } else {
          /* contínuo com WAV: o onEnded do áudio avança a cadeia */
          reproducaoContinuaPorWavRef.current = false;
        }
        indiceCueReproducaoSoloRef.current = null;
      }
    };
    video.addEventListener("timeupdate", aoTempo);
    video.addEventListener("seeked", aoTempo);
    return () => {
      video.removeEventListener("timeupdate", aoTempo);
      video.removeEventListener("seeked", aoTempo);
    };
  }, [
    aberto,
    urlVideoPlayerEfetivo,
    definirPreviewRecorteTelaAtivoUi,
    lerTempoVirtualTimelinePreviewRecorteUi,
  ]);

  /** Com WAV seguindo após o fim da janela, a barra virtual avança pelo áudio. */
  useEffect(() => {
    if (!aberto || !previewRecorteTelaAtivo) return;
    const audio = audioCueRef.current;
    if (!audio) return;
    const aoAudio = () => {
      const indiceSolo = indiceCueReproducaoSoloRef.current;
      if (indiceSolo === null || !previewRecorteTelaAtivoRef.current) return;
      const tVirtual = lerTempoVirtualTimelinePreviewRecorteUi(indiceSolo);
      if (tVirtual !== null) setTempoAtualSegundos(tVirtual);
    };
    audio.addEventListener("timeupdate", aoAudio);
    return () => audio.removeEventListener("timeupdate", aoAudio);
  }, [aberto, previewRecorteTelaAtivo, lerTempoVirtualTimelinePreviewRecorteUi]);

  /** No solo da cue (WAV/prévia), o vídeo fica pausado e o frame/barra acompanham o áudio. */
  useEffect(() => {
    if (!aberto) return;
    const audio = audioCueRef.current;
    const video = videoRef.current;
    if (!audio || !video) return;

    let rafId = 0;
    const aplicarSyncFrameComAudioSolo = () => {
      // Preview de recorte: o vídeo original corre em 1×; não scrubar pelo WAV.
      if (previewRecorteTelaAtivoRef.current) return false;
      const indiceSolo = indiceCueReproducaoSoloRef.current;
      if (indiceSolo === null || audio.paused) return false;
      const cue = cuesRef.current[indiceSolo];
      if (!cue) return false;
      const t = cue.inicioSegundos + (audio.currentTime || 0);
      const tClamp = Math.min(
        Math.max(cue.inicioSegundos, t),
        Math.max(cue.inicioSegundos, cue.fimSegundos - 0.05),
      );
      try {
        if (Math.abs((video.currentTime || 0) - tClamp) > 0.04) {
          video.currentTime = tClamp;
        }
      } catch {
        /* ignore */
      }
      setTempoAtualSegundos(tClamp);
      return true;
    };

    const loopRaf = () => {
      if (!aplicarSyncFrameComAudioSolo()) {
        rafId = 0;
        return;
      }
      rafId = window.requestAnimationFrame(loopRaf);
    };

    const aoPlayAudio = () => {
      if (!rafId) rafId = window.requestAnimationFrame(loopRaf);
    };
    const aoPauseOuFim = () => {
      if (rafId) {
        window.cancelAnimationFrame(rafId);
        rafId = 0;
      }
    };

    audio.addEventListener("play", aoPlayAudio);
    audio.addEventListener("playing", aoPlayAudio);
    audio.addEventListener("pause", aoPauseOuFim);
    audio.addEventListener("ended", aoPauseOuFim);
    return () => {
      aoPauseOuFim();
      audio.removeEventListener("play", aoPlayAudio);
      audio.removeEventListener("playing", aoPlayAudio);
      audio.removeEventListener("pause", aoPauseOuFim);
      audio.removeEventListener("ended", aoPauseOuFim);
    };
  }, [aberto, urlVideoPlayerEfetivo]);

  const executarPedidoPlayPreviewRecorteTelaUi = useCallback(() => {
    const pedido = pedidoPlayAposTrocaSrcPreviewRef.current;
    const video = videoRef.current;
    const audio = audioCueRef.current;
    if (!pedido || !video) return;
    pedidoPlayAposTrocaSrcPreviewRef.current = null;

    const {
      indice,
      continuo,
      offsetAudio,
      tempoJanelaSegundos,
      urlAudio,
      semNarracao,
    } = pedido;

    narracaoSegueAposJanelaPreviewRef.current = false;
    reproducaoContinuaPorWavRef.current = continuo;
    indiceCueReproducaoSoloRef.current = indice;
    setIndiceCueSelecionadaSolo(indice);

    const j = janelasRef.current[indice];
    const iniTela = Math.max(0, j?.inicioVideoSegundos ?? 0);
    const fimTela = Math.max(iniTela + 0.05, j?.fimVideoSegundos ?? iniTela + 0.05);
    const t0 = Math.min(Math.max(tempoJanelaSegundos, iniTela), fimTela - 0.05);

    try {
      video.currentTime = t0;
    } catch {
      /* seek prematuro */
    }
    const cuePlay = cuesRef.current[indice];
    const tempoVirtualInicial = cuePlay
      ? Math.min(
          Math.max(cuePlay.inicioSegundos + offsetAudio, cuePlay.inicioSegundos),
          Math.max(cuePlay.inicioSegundos, cuePlay.fimSegundos - 0.05),
        )
      : t0;
    setTempoAtualSegundos(tempoVirtualInicial);
    video.muted = true;

    if (semNarracao || !urlAudio || !audio) {
      setIndiceAudioTocando(indice);
      void video.play().then(
        () => undefined,
        (e: unknown) => {
          video.muted = false;
          setIndiceAudioTocando(null);
          indiceCueReproducaoSoloRef.current = null;
          definirPreviewRecorteTelaAtivoUi(false);
          pushToast(
            e instanceof Error ? e.message : "Não foi possível tocar o preview do recorte.",
            "error",
          );
        },
      );
      return;
    }

    try {
      const absAtual = audio.currentSrc || audio.src || "";
      const absNova = new URL(urlAudio, window.location.href).href;
      if (absAtual !== absNova) audio.src = urlAudio;
    } catch {
      audio.src = urlAudio;
    }

    const aplicarOffsetAudio = () => {
      if (indiceCueReproducaoSoloRef.current !== indice) return;
      try {
        if (offsetAudio > 0 && Number.isFinite(audio.duration) && audio.duration > 0) {
          audio.currentTime = Math.min(offsetAudio, Math.max(0, audio.duration - 0.05));
        } else {
          audio.currentTime = 0;
        }
      } catch {
        /* ignore */
      }
    };
    if (audio.readyState >= 1) aplicarOffsetAudio();
    else audio.addEventListener("loadedmetadata", aplicarOffsetAudio, { once: true });

    setIndiceAudioTocando(indice);
    void video.play().catch(() => undefined);
    void audio.play().then(
      () => {
        if (indiceCueReproducaoSoloRef.current !== indice) return;
        aplicarOffsetAudio();
      },
      (e: unknown) => {
        setIndiceAudioTocando(null);
        indiceCueReproducaoSoloRef.current = null;
        reproducaoContinuaPorWavRef.current = false;
        definirPreviewRecorteTelaAtivoUi(false);
        pushToast(
          e instanceof Error ? e.message : "Não foi possível tocar a narração da cue.",
          "error",
        );
      },
    );
  }, [definirPreviewRecorteTelaAtivoUi, pushToast]);

  /** Após trocar o src para o vídeo de entrada, dispara o play do preview. */
  useEffect(() => {
    if (!aberto || !previewRecorteTelaAtivo) return;
    if (!pedidoPlayAposTrocaSrcPreviewRef.current) return;
    const video = videoRef.current;
    if (!video) return;

    const rodar = () => {
      if (!pedidoPlayAposTrocaSrcPreviewRef.current) return;
      executarPedidoPlayPreviewRecorteTelaUi();
    };

    if (video.readyState >= 1) {
      rodar();
      return;
    }
    video.addEventListener("loadedmetadata", rodar, { once: true });
    return () => video.removeEventListener("loadedmetadata", rodar);
  }, [aberto, previewRecorteTelaAtivo, urlVideoPlayerEfetivo, executarPedidoPlayPreviewRecorteTelaUi]);

  /** Ao sair do preview, reposiciona o MP4 narrado se houver seek pendente. */
  useEffect(() => {
    if (!aberto || previewRecorteTelaAtivo) return;
    const t = pedidoSeekNarradoAposSairPreviewRef.current;
    if (t === null) return;
    const video = videoRef.current;
    if (!video) return;

    const aplicar = () => {
      const tt = pedidoSeekNarradoAposSairPreviewRef.current;
      if (tt === null) return;
      pedidoSeekNarradoAposSairPreviewRef.current = null;
      try {
        video.currentTime = tt;
      } catch {
        /* ignore */
      }
      setTempoAtualSegundos(tt);
      video.muted = false;
    };

    if (video.readyState >= 1) {
      aplicar();
      return;
    }
    video.addEventListener("loadedmetadata", aplicar, { once: true });
    return () => video.removeEventListener("loadedmetadata", aplicar);
  }, [aberto, previewRecorteTelaAtivo, urlVideoPlayerEfetivo]);

  useEffect(() => {
    if (!aberto) return;
    const video = videoRef.current;
    if (!video) return;
    const tracks = video.textTracks;
    for (let i = 0; i < tracks.length; i++) {
      const track = tracks[i];
      if (track.kind === "subtitles" || track.kind === "captions") {
        track.mode = legendasNoVideo ? "showing" : "hidden";
      }
    }
  }, [aberto, legendasNoVideo, urlTrackVttParaVideo, urlVideoPlayerEfetivo]);

  const indiceCueAtivaPorTempo = (() => {
    const t = tempoAtualSegundos;
    for (let i = 0; i < cues.length; i++) {
      const c = cues[i];
      if (t >= c.inicioSegundos && t < c.fimSegundos) return i;
    }
    if (cues.length > 0) {
      const ultima = cues[cues.length - 1];
      if (t >= ultima.inicioSegundos && t <= ultima.fimSegundos + 0.05) return cues.length - 1;
    }
    return -1;
  })();

  /** Preferir a cue clicada (solo) para não “passar” o destaque à seguinte no limite. */
  const indiceCueAtiva =
    indiceCueSelecionadaSolo !== null &&
    indiceCueSelecionadaSolo >= 0 &&
    indiceCueSelecionadaSolo < cues.length
      ? indiceCueSelecionadaSolo
      : indiceCueAtivaPorTempo;

  /**
   * No preview de recorte o `<track>` VTT segue o currentTime do original (errado).
   * Overlay usa a cue da timeline virtual (tempo narrado).
   */
  const textoLegendaOverlayPreviewRecorte = useMemo(() => {
    if (!previewRecorteTelaAtivo || !legendasNoVideo) return "";
    const indice =
      indiceCueAtivaPorTempo >= 0
        ? indiceCueAtivaPorTempo
        : indiceCueAtiva >= 0
          ? indiceCueAtiva
          : -1;
    if (indice < 0) return "";
    return String(cues[indice]?.texto || "").trim();
  }, [
    previewRecorteTelaAtivo,
    legendasNoVideo,
    indiceCueAtivaPorTempo,
    indiceCueAtiva,
    cues,
  ]);

  const faixaCuesTimeline = useMemo<SegmentoFaixaCuesTimelinePlayerVideoTranscribrothers[]>(
    () =>
      cues.map((c, indice) => {
        const j = janelas[indice];
        const semNarracao = Boolean(j?.semNarracao);
        const textoFala = textoEfetivoParaTtsCueUiTranscribrothers(c.texto, c.textoTts);
        const textoDifere =
          !!j && cueTextoDifereDoNarradoTranscribrothers(textoFala, j.textoNarrado || "");
        const vozDifere =
          !!j && cueVozDifereDaNarradaTranscribrothers(j.vozTts || "", j.vozNarrada || "");
        const audioDifere = textoDifere || vozDifere;
        const preview = previewAudioPorIndice[indice];
        const previewBateComTextoEVoz = previaAudioCueBateComTextoEVozUiTranscribrothers(
          preview,
          textoFala,
          j?.vozTts || "",
        );

        let duracaoAudioSegundos: number | null = null;
        let audioEhPreview = false;
        let aguardandoAudioAtual = false;

        if (semNarracao) {
          // Preview visual: ocupa o slot com a janela de tela (sem fala).
          const durJanela = j
            ? Math.max(0.05, j.fimVideoSegundos - j.inicioVideoSegundos)
            : Math.max(0.05, c.fimSegundos - c.inicioSegundos);
          duracaoAudioSegundos = durJanela;
        } else if (audioDifere) {
          if (previewBateComTextoEVoz && preview) {
            duracaoAudioSegundos = preview.duracaoSegundos;
            audioEhPreview = true;
          } else {
            aguardandoAudioAtual = true;
          }
        } else if (typeof duracoesWavPorIndice[indice] === "number") {
          duracaoAudioSegundos = duracoesWavPorIndice[indice];
        }

        return {
          inicioSegundos: c.inicioSegundos,
          fimSegundos: c.fimSegundos,
          rotulo: semNarracao
            ? `#${indice + 1} — Sem narração`
            : `#${indice + 1} — ${c.texto.trim().slice(0, 100) || "Cue"}`,
          duracaoAudioSegundos,
          audioEhPreview,
          aguardandoAudioAtual,
          semNarracao,
        };
      }),
    [cues, janelas, duracoesWavPorIndice, previewAudioPorIndice],
  );

  useEffect(() => {
    if (indiceCueAtiva < 0) return;
    cueAtivaRef.current?.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }, [indiceCueAtiva]);

  const tocarNarracaoWavDaCueNaPosicaoTimelineUi = useCallback(
    (
      indice: number,
      opcoes?: {
        continuo?: boolean;
        retomarSePossivel?: boolean;
        /** Se definido, continua daqui (barra) em vez de pular ao início da cue. */
        partirDoTempoTimelineSegundos?: number;
      },
    ) => {
      const video = videoRef.current;
      const audio = audioCueRef.current;
      const cue = cuesRef.current[indice];
      if (!video || !audio || !cue) return false;

      const continuo = Boolean(opcoes?.continuo);
      const retomarSePossivel = Boolean(opcoes?.retomarSePossivel);
      const partirDoTempoTimeline =
        typeof opcoes?.partirDoTempoTimelineSegundos === "number" &&
        Number.isFinite(opcoes.partirDoTempoTimelineSegundos)
          ? opcoes.partirDoTempoTimelineSegundos
          : null;
      const j = janelasRef.current[indice];
      const textoDifere =
        !!j &&
        cueTextoDifereDoNarradoTranscribrothers(
          textoEfetivoParaTtsCueUiTranscribrothers(cue.texto, cue.textoTts),
          j.textoNarrado || "",
        );
      const urlAudio = resolverUrlAudioNarracaoDaCueParaPlaybackUi(indice);
      const originais = cuesOriginaisRef.current;
      const temposDeslocadosNestaCue =
        !originais[indice] ||
        cue.inicioSegundos !== originais[indice].inicioSegundos ||
        cue.fimSegundos !== originais[indice].fimSegundos;

      setIndiceCueSelecionadaSolo(indice);
      reproducaoContinuaPorWavRef.current = continuo;

      const soloAtual = indiceCueReproducaoSoloRef.current;
      const offsetAudioAtual =
        retomarSePossivel && soloAtual === indice ? Math.max(0, audio.currentTime || 0) : 0;
      const podeRetomar =
        partirDoTempoTimeline === null &&
        retomarSePossivel &&
        soloAtual === indice &&
        audio.paused &&
        offsetAudioAtual > 0.05 &&
        Number.isFinite(audio.duration) &&
        offsetAudioAtual < audio.duration - 0.08;

      const tempoNaCueClamp =
        partirDoTempoTimeline !== null
          ? Math.min(
              Math.max(cue.inicioSegundos, partirDoTempoTimeline),
              Math.max(cue.inicioSegundos, cue.fimSegundos - 0.05),
            )
          : null;
      const offsetPelaBarra =
        tempoNaCueClamp !== null ? Math.max(0, tempoNaCueClamp - cue.inicioSegundos) : 0;

      audio.pause();
      video.pause();
      setIndiceAudioTocando(null);

      // Preview do recorte no vídeo de entrada (reflete janelas editadas sem remux).
      if (jobTemVideoEntrada && j) {
        const iniTela = Math.max(0, j.inicioVideoSegundos);
        const fimTela = Math.max(iniTela + 0.05, j.fimVideoSegundos);
        let tempoJanela = iniTela;
        if (tempoNaCueClamp !== null) {
          tempoJanela = mapearTempoTimelineCueParaJanelaVideoOriginalPreviewUiTranscribrothers(
            tempoNaCueClamp,
            cue.inicioSegundos,
            cue.fimSegundos,
            iniTela,
            fimTela,
          );
        } else if (
          podeRetomar &&
          previewRecorteTelaAtivoRef.current &&
          soloAtual === indice
        ) {
          tempoJanela = Math.min(
            Math.max(video.currentTime || iniTela, iniTela),
            fimTela - 0.05,
          );
        }

        const offsetAudio = podeRetomar
          ? offsetAudioAtual
          : tempoNaCueClamp !== null
            ? offsetPelaBarra
            : 0;

        if (!j.semNarracao && !urlAudio) {
          if (textoDifere) {
            pushToast(
              "Gere a «Prévia» desta cue para ouvir a narração do texto editado com o recorte de tela.",
              "info",
            );
          } else if (!j.temWav) {
            pushToast("Áudio desta cue ainda não está disponível.", "info");
          }
        }

        pedidoPlayAposTrocaSrcPreviewRef.current = {
          indice,
          continuo,
          offsetAudio: j.semNarracao || !urlAudio ? 0 : offsetAudio,
          tempoJanelaSegundos: tempoJanela,
          urlAudio: j.semNarracao ? null : urlAudio,
          semNarracao: Boolean(j.semNarracao) || !urlAudio,
        };

        if (previewRecorteTelaAtivoRef.current) {
          executarPedidoPlayPreviewRecorteTelaUi();
        } else {
          definirPreviewRecorteTelaAtivoUi(true);
        }
        return true;
      }

      if (previewRecorteTelaAtivoRef.current) {
        pedidoSeekNarradoAposSairPreviewRef.current = Math.max(0, cue.inicioSegundos);
        definirPreviewRecorteTelaAtivoUi(false);
      }

      // Trecho só com vídeo: play 1× na janela de tela, sem TTS (muta o MP4 — ainda tem fala antiga).
      if (j?.semNarracao) {
        const iniTela = Math.max(0, j.inicioVideoSegundos);
        const fimTela = Math.max(iniTela + 0.05, j.fimVideoSegundos);
        const t0 =
          tempoNaCueClamp !== null
            ? Math.min(Math.max(iniTela, tempoNaCueClamp), fimTela - 0.05)
            : iniTela;
        indiceCueReproducaoSoloRef.current = indice;
        video.muted = true;
        video.currentTime = t0;
        setTempoAtualSegundos(t0);
        setIndiceAudioTocando(indice);
        void video.play().then(
          () => undefined,
          (e: unknown) => {
            video.muted = false;
            setIndiceAudioTocando(null);
            indiceCueReproducaoSoloRef.current = null;
            pushToast(
              e instanceof Error ? e.message : "Não foi possível tocar o trecho sem narração.",
              "error",
            );
          },
        );
        return true;
      }

      video.muted = false;

      indiceCueReproducaoSoloRef.current = indice;
      if (tempoNaCueClamp !== null) {
        video.currentTime = tempoNaCueClamp;
        setTempoAtualSegundos(tempoNaCueClamp);
      } else if (!podeRetomar) {
        const t0 = Math.max(0, cue.inicioSegundos);
        video.currentTime = t0;
        setTempoAtualSegundos(t0);
      }

      if (urlAudio) {
        // Vídeo pausado (sem mutar volume/muted): WAV/prévia na posição atual da cue.
        // play() precisa rodar no mesmo gesto do clique — não esperar loadedmetadata.
        const offsetAudio = podeRetomar
          ? offsetAudioAtual
          : tempoNaCueClamp !== null
            ? offsetPelaBarra
            : 0;
        try {
          const absAtual = audio.currentSrc || audio.src || "";
          const absNova = new URL(urlAudio, window.location.href).href;
          if (absAtual !== absNova) audio.src = urlAudio;
        } catch {
          audio.src = urlAudio;
        }

        const aplicarOffsetAudio = () => {
          if (indiceCueReproducaoSoloRef.current !== indice) return;
          try {
            if (offsetAudio > 0 && Number.isFinite(audio.duration) && audio.duration > 0) {
              audio.currentTime = Math.min(offsetAudio, Math.max(0, audio.duration - 0.05));
            } else if (!podeRetomar && tempoNaCueClamp === null) {
              audio.currentTime = 0;
            } else if (tempoNaCueClamp !== null && offsetAudio <= 0) {
              audio.currentTime = 0;
            }
          } catch {
            /* ignore seek prematuro */
          }
        };

        if (audio.readyState >= 1) aplicarOffsetAudio();
        else audio.addEventListener("loadedmetadata", aplicarOffsetAudio, { once: true });

        setIndiceAudioTocando(indice);
        void audio.play().then(
          () => {
            if (indiceCueReproducaoSoloRef.current !== indice) return;
            aplicarOffsetAudio();
          },
          (e: unknown) => {
            setIndiceAudioTocando(null);
            indiceCueReproducaoSoloRef.current = null;
            reproducaoContinuaPorWavRef.current = false;
            pushToast(
              e instanceof Error ? e.message : "Não foi possível tocar a narração da cue.",
              "error",
            );
          },
        );
        return true;
      }

      if (textoDifere) {
        pushToast(
          "Gere a «Prévia» desta cue para ouvir a narração do texto editado neste ponto da timeline.",
          "info",
        );
        return false;
      }
      if (!j?.temWav) {
        pushToast("Áudio desta cue ainda não está disponível.", "info");
        return false;
      }
      if (temposDeslocadosNestaCue) {
        pushToast(
          "A narração do MP4 ainda está na posição antiga. Use a prévia da cue ou «Atualizar narração».",
          "info",
        );
        return false;
      }

      // Tempos originais e sem WAV auxiliar: cai no áudio do próprio MP4.
      void video.play().catch(() => undefined);
      return true;
    },
    [
      definirPreviewRecorteTelaAtivoUi,
      executarPedidoPlayPreviewRecorteTelaUi,
      jobTemVideoEntrada,
      pushToast,
      resolverUrlAudioNarracaoDaCueParaPlaybackUi,
    ],
  );
  tocarNarracaoWavDaCueRef.current = tocarNarracaoWavDaCueNaPosicaoTimelineUi;

  const alternarReproducaoSoloCueNoVideoNarrado = useCallback(
    (indice: number) => {
      const video = videoRef.current;
      const audio = audioCueRef.current;
      const cue = cues[indice];
      if (!video || !cue) return;

      const soloAtual = indiceCueReproducaoSoloRef.current;
      const audioSoloTocando =
        soloAtual === indice && indiceAudioTocando === indice && !!audio && !audio.paused;
      const videoSoloTocando = soloAtual === indice && !video.paused;
      const previewNarracaoSeguindo =
        soloAtual === indice &&
        previewRecorteTelaAtivoRef.current &&
        narracaoSegueAposJanelaPreviewRef.current &&
        Boolean(audio && !audio.paused);

      if (audioSoloTocando || videoSoloTocando || previewNarracaoSeguindo) {
        video.pause();
        if (audio && !audio.paused) audio.pause();
        setIndiceAudioTocando(null);
        reproducaoContinuaPorWavRef.current = false;
        narracaoSegueAposJanelaPreviewRef.current = false;
        setIndiceCueSelecionadaSolo(indice);
        // Preview de recorte: pausa sem sair do modo (mantém overlay + vídeo original).
        if (previewRecorteTelaAtivoRef.current) {
          indiceCueReproducaoSoloRef.current = indice;
        } else {
          indiceCueReproducaoSoloRef.current = null;
          video.muted = false;
        }
        return;
      }

      tocarNarracaoWavDaCueNaPosicaoTimelineUi(indice, {
        continuo: false,
        retomarSePossivel: soloAtual === indice,
      });
    },
    [cues, indiceAudioTocando, tocarNarracaoWavDaCueNaPosicaoTimelineUi],
  );

  /** 1º clique: só seleciona; 2º clique na mesma cue: play/pause. (Faixa da timeline.) */
  const selecionarOuAlternarReproducaoCueNaTimelineUi = useCallback(
    (indice: number) => {
      const video = videoRef.current;
      const cue = cues[indice];
      if (!cue) return;

      if (indiceCueSelecionadaSolo !== indice) {
        const audio = audioCueRef.current;
        if (audio && !audio.paused) audio.pause();
        setIndiceAudioTocando(null);
        indiceCueReproducaoSoloRef.current = null;
        reproducaoContinuaPorWavRef.current = false;
        narracaoSegueAposJanelaPreviewRef.current = false;
        video?.pause();
        setIndiceCueSelecionadaSolo(indice);
        const t0 = Math.max(0, cue.inicioSegundos);
        if (previewRecorteTelaAtivoRef.current) {
          pedidoSeekNarradoAposSairPreviewRef.current = t0;
          definirPreviewRecorteTelaAtivoUi(false);
          return;
        }
        if (video) {
          video.currentTime = t0;
          setTempoAtualSegundos(t0);
          video.muted = false;
        }
        return;
      }

      alternarReproducaoSoloCueNoVideoNarrado(indice);
    },
    [
      alternarReproducaoSoloCueNoVideoNarrado,
      cues,
      definirPreviewRecorteTelaAtivoUi,
      indiceCueSelecionadaSolo,
    ],
  );

  /** Clique no card da lista: só destaca a cue — sem play/pause (use «Ir»). */
  const selecionarCueNaListaSemAlterarPlaybackUi = useCallback((indice: number) => {
    if (!cues[indice]) return;
    setIndiceCueSelecionadaSolo(indice);
  }, [cues]);

  /**
   * Seek na barra durante preview: tempo é da timeline narrada; por baixo mapeia
   * para a janela no vídeo original (+ offset do WAV).
   */
  const aoAlterarTempoPelaBarraDurantePreviewRecorteUi = useCallback(
    (tempoTimelineSegundos: number) => {
      if (!previewRecorteTelaAtivoRef.current) return;
      const t = Math.max(0, tempoTimelineSegundos);
      setTempoAtualSegundos(t);
      const indiceAlvo = indiceCueNoInstanteTimelineUiTranscribrothers(cuesRef.current, t);
      if (indiceAlvo < 0) return;

      const soloAtual = indiceCueReproducaoSoloRef.current;
      const cue = cuesRef.current[indiceAlvo];
      const j = janelasRef.current[indiceAlvo];
      const video = videoRef.current;
      const audio = audioCueRef.current;
      if (!cue || !j || !video) return;

      const mesmoSoloTocando =
        soloAtual === indiceAlvo &&
        (Boolean(audio && !audio.paused) || !video.paused || narracaoSegueAposJanelaPreviewRef.current);

      if (!mesmoSoloTocando) {
        tocarNarracaoWavDaCueNaPosicaoTimelineUi(indiceAlvo, {
          continuo: false,
          partirDoTempoTimelineSegundos: t,
        });
        return;
      }

      const tJanela = mapearTempoTimelineCueParaJanelaVideoOriginalPreviewUiTranscribrothers(
        t,
        cue.inicioSegundos,
        cue.fimSegundos,
        j.inicioVideoSegundos,
        j.fimVideoSegundos,
      );
      try {
        video.currentTime = tJanela;
      } catch {
        /* ignore */
      }
      if (audio && !j.semNarracao && audio.src) {
        const offsetAudio = Math.max(0, t - cue.inicioSegundos);
        try {
          if (Number.isFinite(audio.duration) && audio.duration > 0) {
            audio.currentTime = Math.min(offsetAudio, Math.max(0, audio.duration - 0.05));
          } else {
            audio.currentTime = offsetAudio;
          }
        } catch {
          /* ignore */
        }
      }
    },
    [tocarNarracaoWavDaCueNaPosicaoTimelineUi],
  );

  const aoAlternarPlayPausePlayerComNarracaoAuxiliarUi = useCallback(() => {
    const video = videoRef.current;
    const audio = audioCueRef.current;
    if (!video) return;

    const wavTocando = Boolean(audio && !audio.paused && indiceAudioTocando !== null);
    const videoSemNarracaoTocando =
      !video.paused &&
      indiceCueReproducaoSoloRef.current !== null &&
      Boolean(janelasRef.current[indiceCueReproducaoSoloRef.current]?.semNarracao);

    // Preview de recorte: play/pause só congela mídia — não volta pro MP4 (evita legenda nativa “estranha”).
    if (previewRecorteTelaAtivoRef.current) {
      const indiceSolo =
        indiceCueReproducaoSoloRef.current ??
        indiceCueSelecionadaSolo ??
        indiceCueNoInstanteTimelineUiTranscribrothers(cuesRef.current, tempoAtualSegundos);
      const previewTocando =
        !video.paused || wavTocando || narracaoSegueAposJanelaPreviewRef.current;
      if (previewTocando) {
        video.pause();
        if (audio && !audio.paused) audio.pause();
        setIndiceAudioTocando(null);
        reproducaoContinuaPorWavRef.current = false;
        narracaoSegueAposJanelaPreviewRef.current = false;
        if (indiceSolo !== null && indiceSolo >= 0) {
          indiceCueReproducaoSoloRef.current = indiceSolo;
          setIndiceCueSelecionadaSolo(indiceSolo);
        }
        return;
      }
      if (indiceSolo !== null && indiceSolo >= 0) {
        tocarNarracaoWavDaCueNaPosicaoTimelineUi(indiceSolo, {
          continuo: false,
          retomarSePossivel: true,
          partirDoTempoTimelineSegundos: tempoAtualSegundos,
        });
      }
      return;
    }

    if (wavTocando && audio) {
      audio.pause();
      video.muted = false;
      setIndiceAudioTocando(null);
      indiceCueReproducaoSoloRef.current = null;
      reproducaoContinuaPorWavRef.current = false;
      return;
    }
    if (videoSemNarracaoTocando) {
      video.pause();
      video.muted = false;
      setIndiceAudioTocando(null);
      indiceCueReproducaoSoloRef.current = null;
      reproducaoContinuaPorWavRef.current = false;
      return;
    }

    if (audioDoMp4NaoRefleteEdicoesLocais) {
      // Play da barra: cadeia WAV / trechos mudos — o áudio do MP4 ainda tem cues excluídas.
      const tempoBarra = video.currentTime || 0;
      const indice = indiceCueNoInstanteTimelineUiTranscribrothers(cues, tempoBarra);
      if (indice < 0) return;
      tocarNarracaoWavDaCueNaPosicaoTimelineUi(indice, {
        continuo: true,
        partirDoTempoTimelineSegundos: tempoBarra,
      });
      return;
    }

    video.muted = false;
    if (video.paused) void video.play().catch(() => undefined);
    else video.pause();
  }, [
    audioDoMp4NaoRefleteEdicoesLocais,
    cues,
    indiceAudioTocando,
    indiceCueSelecionadaSolo,
    tempoAtualSegundos,
    tocarNarracaoWavDaCueNaPosicaoTimelineUi,
  ]);

  const gerarPreviewTtsCueForcandoNovaChamadaUi = useCallback(
    async (indice: number, opts?: { marcarForcarExport?: boolean }) => {
      const cue = cuesRef.current[indice] ?? cues[indice];
      if (!cue) return;
      if (!jobId) {
        pushToast("Job não disponível para gerar prévia de áudio.", "error");
        return;
      }
      const audio = audioCueRef.current;
      if (!audio) return;

      audio.pause();
      audio.removeAttribute("src");
      audio.load();
      setIndiceAudioTocando(null);
      videoRef.current?.pause();
      indiceCueReproducaoSoloRef.current = null;

      setPreviewAudioPorIndice((prev) => {
        const antigo = prev[indice];
        if (!antigo) return prev;
        revogarUrlBlobPreviewCueTranscribrothers(antigo.urlBlob);
        const proximo = { ...prev };
        delete proximo[indice];
        return proximo;
      });

      const textoAtual = textoEfetivoParaTtsCueUiTranscribrothers(cue.texto, cue.textoTts);
      setIndiceAudioGerandoPreview(indice);
      try {
        const vozUsada = janelasRef.current[indice]?.vozTts || vozPadraoJob || "Kore";
        const blob = await gerarPreviewTtsCueNarracaoTextoAtualJobApiTranscribrothers(jobId, {
          indice,
          texto: textoAtual,
          litellmModel: litellmModelTts,
          voz: vozUsada,
        });
        const url = URL.createObjectURL(blob);
        let durPreview = 0;
        try {
          durPreview = await obterDuracaoSegundosArquivoAudioPorUrlNavegadorTranscribrothers(url);
        } catch {
          /* prévia ainda toca */
        }
        setPreviewAudioPorIndice((prev) => {
          const antigo = prev[indice];
          if (antigo?.urlBlob && antigo.urlBlob !== url) {
            revogarUrlBlobPreviewCueTranscribrothers(antigo.urlBlob);
          }
          return {
            ...prev,
            [indice]: {
              texto: textoAtual,
              voz: vozUsada,
              duracaoSegundos: durPreview > 0 ? durPreview : antigo?.duracaoSegundos || 0,
              urlBlob: url,
            },
          };
        });
        if (opts?.marcarForcarExport) {
          setJanelas((prev) => {
            if (!prev[indice]) return prev;
            const copia = prev.map((j) => ({ ...j }));
            copia[indice] = { ...copia[indice], forcarRegenerarTts: true };
            return copia;
          });
        }
        audio.src = url;
        setIndiceAudioTocando(indice);
        await audio.play();
        pushToast(
          opts?.marcarForcarExport
            ? "Nova narração gerada. Ao gerar o vídeo, este áudio substitui o anterior desta cue."
            : "Prévia validada nesta cue. Ao gerar o vídeo, este áudio será reaproveitado (sem narrar de novo).",
          "success",
        );
      } catch (e: unknown) {
        setIndiceAudioTocando(null);
        pushToast(e instanceof Error ? e.message : "Falha na prévia TTS.", "error");
      } finally {
        setIndiceAudioGerandoPreview(null);
      }
    },
    [cues, jobId, litellmModelTts, vozPadraoJob, pushToast],
  );

  const ouvirOuPararAudioCue = useCallback(
    (indice: number) => {
      if (indiceAudioGerandoPreview !== null) return;
      if (indiceAudioTocando === indice) {
        pararAudioCue();
        return;
      }
      const cue = cues[indice];
      const j = janelas[indice];
      if (!cue) return;
      const audio = audioCueRef.current;
      if (!audio) return;

      const textoAtual = textoEfetivoParaTtsCueUiTranscribrothers(cue.texto, cue.textoTts);
      const precisaPreview =
        !j ||
        !j.temWav ||
        !j.urlWav ||
        cueTextoDifereDoNarradoTranscribrothers(textoAtual, j.textoNarrado || "") ||
        cueVozDifereDaNarradaTranscribrothers(j.vozTts || "", j.vozNarrada || "") ||
        Boolean(j.forcarRegenerarTts);

      // Para só o áudio auxiliar; mantém blobs de prévia para reuso.
      audio.pause();
      audio.removeAttribute("src");
      audio.load();
      setIndiceAudioTocando(null);
      videoRef.current?.pause();
      indiceCueReproducaoSoloRef.current = null;

      if (!precisaPreview && j?.urlWav) {
        audio.src = `${j.urlWav}?v=${Date.now()}`;
        setIndiceAudioTocando(indice);
        void audio.play().catch((e: unknown) => {
          setIndiceAudioTocando(null);
          pushToast(e instanceof Error ? e.message : "Não foi possível tocar o áudio.", "error");
        });
        return;
      }

      const previewExistente = previewAudioPorIndice[indice];
      const vozCue = j?.vozTts || vozPadraoJob || "Kore";
      if (previaAudioCueBateComTextoEVozUiTranscribrothers(previewExistente, textoAtual, vozCue)) {
        audio.src = previewExistente.urlBlob;
        setIndiceAudioTocando(indice);
        void audio.play().catch((e: unknown) => {
          setIndiceAudioTocando(null);
          pushToast(e instanceof Error ? e.message : "Não foi possível tocar a prévia.", "error");
        });
        return;
      }

      void gerarPreviewTtsCueForcandoNovaChamadaUi(indice);
    },
    [
      cues,
      janelas,
      vozPadraoJob,
      indiceAudioTocando,
      indiceAudioGerandoPreview,
      previewAudioPorIndice,
      pararAudioCue,
      pushToast,
      gerarPreviewTtsCueForcandoNovaChamadaUi,
    ],
  );

  const regenerarNarracaoTtsCueForcandoNovaChamadaUi = useCallback(
    (indice: number) => {
      if (indiceAudioGerandoPreview !== null) return;
      const j = janelas[indice];
      if (!cues[indice] || j?.semNarracao) return;
      void gerarPreviewTtsCueForcandoNovaChamadaUi(indice, { marcarForcarExport: true });
    },
    [cues, janelas, indiceAudioGerandoPreview, gerarPreviewTtsCueForcandoNovaChamadaUi],
  );

  const atualizarTextoCue = useCallback((indice: number, texto: string) => {
    const anterior = cuesRef.current[indice];
    const falaAntes = anterior
      ? textoEfetivoParaTtsCueUiTranscribrothers(anterior.texto, anterior.textoTts)
      : "";
    const falaDepois = textoEfetivoParaTtsCueUiTranscribrothers(texto, anterior?.textoTts);
    setCues((prev) => prev.map((c, i) => (i === indice ? { ...c, texto } : c)));
    if (falaAntes === falaDepois) return;
    setPreviewAudioPorIndice((prev) => {
      const atual = prev[indice];
      if (!atual || atual.texto.trim() === falaDepois) return prev;
      revogarUrlBlobPreviewCueTranscribrothers(atual.urlBlob);
      const proximo = { ...prev };
      delete proximo[indice];
      return proximo;
    });
  }, []);

  const atualizarTextoTtsCue = useCallback((indice: number, textoTts: string) => {
    const anterior = cuesRef.current[indice];
    const falaAntes = anterior
      ? textoEfetivoParaTtsCueUiTranscribrothers(anterior.texto, anterior.textoTts)
      : "";
    const falaDepois = textoEfetivoParaTtsCueUiTranscribrothers(
      anterior?.texto || "",
      textoTts,
    );
    setCues((prev) => prev.map((c, i) => (i === indice ? { ...c, textoTts } : c)));
    if (falaAntes === falaDepois) return;
    setPreviewAudioPorIndice((prev) => {
      const atual = prev[indice];
      if (!atual || atual.texto.trim() === falaDepois) return prev;
      revogarUrlBlobPreviewCueTranscribrothers(atual.urlBlob);
      const proximo = { ...prev };
      delete proximo[indice];
      return proximo;
    });
  }, []);

  const resolverDuracaoAudioAtualDaCueParaAjusteUi = useCallback(
    (indice: number): number | null => {
      const cue = cues[indice];
      const j = janelas[indice];
      if (!cue) return null;
      const textoFala = textoEfetivoParaTtsCueUiTranscribrothers(cue.texto, cue.textoTts);
      const textoDifere =
        !!j && cueTextoDifereDoNarradoTranscribrothers(textoFala, j.textoNarrado || "");
      const vozDifere =
        !!j && cueVozDifereDaNarradaTranscribrothers(j.vozTts || "", j.vozNarrada || "");
      const audioDifere = textoDifere || vozDifere;
      const preview = previewAudioPorIndice[indice];
      if (audioDifere) {
        if (
          previaAudioCueBateComTextoEVozUiTranscribrothers(preview, textoFala, j?.vozTts || "") &&
          preview &&
          preview.duracaoSegundos > 0
        ) {
          return preview.duracaoSegundos;
        }
        return null;
      }
      const durWav = duracoesWavPorIndice[indice];
      return typeof durWav === "number" && durWav > 0 ? durWav : null;
    },
    [cues, janelas, previewAudioPorIndice, duracoesWavPorIndice],
  );

  const ajustarCueAoAudioAtual = useCallback(
    (indice: number) => {
      const durAudio = resolverDuracaoAudioAtualDaCueParaAjusteUi(indice);
      if (durAudio === null) {
        pushToast(
          "Gere a prévia («Ouvir»/«Prévia») ou aguarde o áudio gravado para ajustar a cue.",
          "info",
        );
        return;
      }
      const r = ajustarFimCueTimelineAoAudioNarracaoUiTranscribrothers(cues, indice, durAudio);
      if (!r.ok) {
        pushToast(r.motivo, "info");
        return;
      }
      setCues(r.cues);
      setIndiceCueSelecionadaSolo(indice);
      pushToast("Cue ajustada ao áudio — ficou folga na timeline para deslocar.", "success");
    },
    [cues, pushToast, resolverDuracaoAudioAtualDaCueParaAjusteUi],
  );

  const deslocarCueNaTimeline = useCallback(
    (indice: number, sentido: "esquerda" | "direita") => {
      const delta =
        sentido === "esquerda"
          ? -DELTA_DESLOCAR_CUE_TIMELINE_NARRACAO_SEGUNDOS_TRANSCRIBROTHERS
          : DELTA_DESLOCAR_CUE_TIMELINE_NARRACAO_SEGUNDOS_TRANSCRIBROTHERS;
      const r = deslocarCueTimelineNarracaoSemSobreporVizinhasUiTranscribrothers(
        cues,
        indice,
        delta,
      );
      if (!r.ok) {
        pushToast(r.motivo, "info");
        return;
      }
      setCues(r.cues);
      setIndiceCueSelecionadaSolo(indice);
    },
    [cues, pushToast],
  );

  const arrastarCueNaTimelineParaInicio = useCallback(
    (indice: number, novoInicioSegundos: number) => {
      const duracaoVideo =
        videoRef.current &&
        Number.isFinite(videoRef.current.duration) &&
        videoRef.current.duration > 0
          ? videoRef.current.duration
          : null;
      const r = posicionarInicioCueTimelineNarracaoSemSobreporVizinhasUiTranscribrothers(
        cues,
        indice,
        novoInicioSegundos,
        duracaoVideo,
      );
      if (!r.ok) return;
      if (Math.abs(r.deslocouSegundos) < 1e-9) return;
      setCues(r.cues);
      setIndiceCueSelecionadaSolo(indice);
    },
    [cues],
  );

  useLayoutEffect(() => {
    if (!aberto || carregandoCues) return;
    ajustarAlturasTodosTextareasCuesNaListaTranscribrothers(listaCuesRef.current);
  }, [aberto, carregandoCues, cues]);

  const salvarLegendas = useCallback(async () => {
    if (!jobId || !urlLegendasVtt || salvandoLegendas || regenerando) return;
    const payload = cues.map((c) => ({
      inicio_segundos: c.inicioSegundos,
      fim_segundos: c.fimSegundos,
      texto: c.texto,
    }));
    setSalvandoLegendas(true);
    try {
      await salvarLegendasDocumentoAlinhadasVttEditadasJobApiTranscribrothers(jobId, payload);
      setCuesOriginais(cues.map((c) => ({ ...c })));
      setVersaoCacheTrackVtt(Date.now());
      pushToast("Legendas salvas. O áudio e o vídeo narrado não foram alterados.", "success");
      if (onLegendasSalvas) await onLegendasSalvas();
    } catch (e: unknown) {
      pushToast(e instanceof Error ? e.message : String(e), "error");
    } finally {
      setSalvandoLegendas(false);
    }
  }, [
    jobId,
    urlLegendasVtt,
    salvandoLegendas,
    regenerando,
    cues,
    pushToast,
    onLegendasSalvas,
  ]);

  const salvarJanelas = useCallback(async () => {
    if (!jobId || salvandoJanelas || regenerando || janelas.length === 0) return;
    const payload = janelas.map((j) => ({
      inicio_video_segundos: j.inicioVideoSegundos,
      fim_video_segundos: j.fimVideoSegundos,
    }));
    const erroLocal = validarJanelasVideoSemSobreposicaoNaUiTranscribrothers(payload);
    if (erroLocal) {
      pushToast(erroLocal, "error");
      return;
    }
    setSalvandoJanelas(true);
    try {
      const resp = await salvarJanelasVideoCuesNarracaoJobApiTranscribrothers(jobId, payload);
      setJanelas((prev) => {
        const padrao =
          String(resp.voz_tts_padrao_job || vozPadraoJob || "Kore").trim() || "Kore";
        const lista: JanelaVideoCueLocalUiTranscribrothers[] = resp.cues.map((c, i) => {
          const vozApi = String(c.voz_tts || "").trim() || padrao;
          const textoTts = String(c.texto_tts || "").trim();
          return {
            inicioVideoSegundos: c.inicio_video_segundos,
            fimVideoSegundos: c.fim_video_segundos,
            temWav: c.tem_wav,
            urlWav: c.url_wav,
            textoNarrado: textoEfetivoParaTtsCueUiTranscribrothers(c.texto || "", textoTts),
            textoTtsNarrado: textoTts,
            // Toggle/voz locais até o «Gerar vídeo» persistir no manifesto.
            semNarracao: prev[i]?.semNarracao ?? Boolean(c.sem_narracao),
            vozTts: prev[i]?.vozTts || vozApi,
            vozNarrada: prev[i]?.vozNarrada || vozApi,
          };
        });
        setJanelasOriginais((orig) =>
          lista.map((j, i) => ({
            ...j,
            semNarracao: orig[i]?.semNarracao ?? Boolean(resp.cues[i]?.sem_narracao),
            vozTts: orig[i]?.vozTts || j.vozTts,
            vozNarrada: orig[i]?.vozNarrada || j.vozNarrada,
          })),
        );
        return lista;
      });
      pushToast(
        "Tempos de tela salvos. Use «Aplicar tempos ao vídeo» para remontar o MP4 (sem novo TTS).",
        "success",
      );
    } catch (e: unknown) {
      pushToast(e instanceof Error ? e.message : String(e), "error");
    } finally {
      setSalvandoJanelas(false);
    }
  }, [jobId, salvandoJanelas, regenerando, janelas, pushToast, vozPadraoJob]);

  const aoBaixarVideoComLegendasQueimadas = useCallback(async () => {
    if (!jobId || baixandoVideoComLegendasQueimadas) return;
    if (!urlVideoMp4) {
      pushToast("Ainda não há vídeo com narração gerado.", "info");
      return;
    }
    if (!urlLegendasVtt) {
      pushToast("Ainda não há legendas VTT para embutir no vídeo.", "info");
      return;
    }
    setBaixandoVideoComLegendasQueimadas(true);
    setMenuRodapeAbertoId(null);
    let idToastProgresso: string | null = null;
    try {
      const resultado = await baixarVideoNarradoComLegendasQueimadasJobApiTranscribrothers(jobId, {
        onStatus: (s) => {
          if (s.status !== "gerando" && s.status !== "pendente") return;
          const pct =
            typeof s.progresso_percentual === "number" && Number.isFinite(s.progresso_percentual)
              ? s.progresso_percentual
              : null;
          const decorrido =
            typeof s.tempo_decorrido_segundos === "number" &&
            Number.isFinite(s.tempo_decorrido_segundos)
              ? Math.round(s.tempo_decorrido_segundos)
              : null;
          const msgBase =
            pct != null
              ? `Gerando vídeo com legendas embutidas… ${Math.round(pct)}%`
              : "Gerando vídeo com legendas embutidas… Em alta resolução pode levar alguns minutos na 1ª vez.";
          const msg =
            decorrido != null && decorrido >= 5 ? `${msgBase} (${decorrido}s)` : msgBase;
          if (!idToastProgresso) {
            idToastProgresso = pushToastProgresso({
              message: msg,
              percentual: pct,
              indeterminado: pct == null,
            });
          } else {
            atualizarToastProgresso(idToastProgresso, {
              message: msg,
              percentual: pct,
              indeterminado: pct == null,
            });
          }
        },
      });
      if (idToastProgresso) removerToast(idToastProgresso);
      pushToast(
        resultado.precisouGerar
          ? "Vídeo com legendas embutidas pronto — download iniciado."
          : "Download do vídeo com legendas embutidas iniciado.",
        "success",
      );
    } catch (e: unknown) {
      if (idToastProgresso) removerToast(idToastProgresso);
      pushToast(
        e instanceof Error ? e.message : "Falha ao gerar o vídeo com legendas embutidas.",
        "error",
      );
    } finally {
      setBaixandoVideoComLegendasQueimadas(false);
    }
  }, [
    atualizarToastProgresso,
    baixandoVideoComLegendasQueimadas,
    jobId,
    pushToast,
    pushToastProgresso,
    removerToast,
    urlLegendasVtt,
    urlVideoMp4,
  ]);

  if (!aberto) return null;

  const ocupado =
    regenerando ||
    salvandoLegendas ||
    salvandoJanelas ||
    baixandoVideoComLegendasQueimadas ||
    trocandoVersaoVideoNarrado;
  const podeSalvar =
    Boolean(jobId) &&
    Boolean(urlLegendasVtt) &&
    sujas &&
    !ocupado &&
    !carregandoCues &&
    cues.length > 0;
  const podeSalvarJanelas =
    Boolean(jobId) && janelas.length > 0 && janelasSujas && !ocupado;
  const podeAplicarTempos =
    Boolean(jobId) && janelas.length > 0 && !janelasSujas && !ocupado;
  const podeAtualizarNarracao =
    Boolean(jobId) && Boolean(urlLegendasVtt) && !ocupado && !sujas;
  const podeGerarVideoComEstasEdicoes =
    Boolean(jobId) && cues.length > 0 && !ocupado && !carregandoCues && !erroCues;
  const acaoSalvarContextual = resolverAcaoPrimariaContextualRodapeModalVideoNarradoTranscribrothers({
    podeSalvarLegendas: podeSalvar,
    podeSalvarTempos: podeSalvarJanelas,
    salvandoLegendas,
    salvandoJanelas,
    onSalvarLegendas: () => {
      void salvarLegendas();
    },
    onSalvarTempos: () => {
      void salvarJanelas();
    },
  });
  const dispararGerarVideoComEstasEdicoes = () => {
    onGerarVideoComEstasEdicoes({
      cues: cues.map((c, i) => ({
        inicio_segundos: c.inicioSegundos,
        fim_segundos: c.fimSegundos,
        texto: c.texto,
        texto_tts: (c.textoTts || "").trim() || undefined,
        sem_narracao: Boolean(janelas[i]?.semNarracao),
        voz_tts: janelas[i]?.vozTts || vozPadraoJob || "Kore",
        forcar_regenerar_tts: Boolean(janelas[i]?.forcarRegenerarTts),
      })),
      janelas:
        janelas.length === cues.length
          ? janelas.map((j) => ({
              inicio_video_segundos: j.inicioVideoSegundos,
              fim_video_segundos: j.fimVideoSegundos,
            }))
          : null,
    });
  };

  const alternarSemNarracaoDaCue = (indice: number) => {
    setJanelas((prev) => {
      if (!prev[indice]) return prev;
      const copia = prev.map((j) => ({ ...j }));
      copia[indice] = { ...copia[indice], semNarracao: !copia[indice].semNarracao };
      return copia;
    });
  };

  const alterarVozTtsDaCue = (indice: number, novaVoz: string) => {
    const voz = (novaVoz || "").trim() || vozPadraoJob || "Kore";
    setJanelas((prev) => {
      if (!prev[indice]) return prev;
      const copia = prev.map((j) => ({ ...j }));
      copia[indice] = { ...copia[indice], vozTts: voz };
      return copia;
    });
    setPreviewAudioPorIndice((prev) => {
      const antigo = prev[indice];
      if (!antigo) return prev;
      revogarUrlBlobPreviewCueTranscribrothers(antigo.urlBlob);
      const proximo = { ...prev };
      delete proximo[indice];
      return proximo;
    });
  };

  const excluirCueDaListaLocalUi = (indice: number) => {
    if (indice < 0 || indice >= cues.length) return;
    if (cues.length <= 1) {
      pushToast("É preciso manter ao menos uma cue.", "info");
      return;
    }
    const ok = window.confirm(
      `Excluir a cue ${indice + 1}? Esse trecho deixa de entrar no vídeo narrado ao gerar de novo.`,
    );
    if (!ok) return;

    const video = videoRef.current;
    if (video) {
      video.pause();
      video.muted = false;
    }
    audioCueRef.current?.pause();
    setIndiceAudioTocando(null);
    indiceCueReproducaoSoloRef.current = null;
    reproducaoContinuaPorWavRef.current = false;
    setIndiceCueSelecionadaSolo(null);

    // Mantém cuesOriginais/janelasOriginais: o MP4 ainda tem o trecho; o preview precisa da cadeia WAV.
    setCues((prev) => prev.filter((_, i) => i !== indice));
    setJanelas((prev) => prev.filter((_, i) => i !== indice));
    setDuracoesWavPorIndice((prev) => {
      const proximo: Record<number, number> = {};
      Object.entries(prev).forEach(([k, v]) => {
        const i = Number(k);
        if (i < indice) proximo[i] = v;
        else if (i > indice) proximo[i - 1] = v;
      });
      return proximo;
    });
    setPreviewAudioPorIndice((prev) => {
      const proximo: Record<number, PreviewAudioCueFaixaTimelineUiTranscribrothers> = {};
      Object.entries(prev).forEach(([k, v]) => {
        const i = Number(k);
        if (i === indice) {
          if (v.urlBlob) URL.revokeObjectURL(v.urlBlob);
          return;
        }
        if (i < indice) proximo[i] = v;
        else proximo[i - 1] = v;
      });
      return proximo;
    });
    pushToast("Cue excluída da lista. Gere o vídeo para aplicar no MP4.", "info");
  };

  if (!aberto) return null;

  const textosCuesParaModalOriginal = cues.map((c) => c.texto);

  return (
    <>
    <div
      className="tb-pagina-assistir-video-narrado"
      role="main"
      aria-labelledby={tituloId}
    >
      <div className="tb-pagina-assistir-video-narrado-painel">
        <audio
          ref={audioCueRef}
          preload="none"
          onEnded={() => {
            setIndiceAudioTocando(null);
            const video = videoRef.current;
            const indiceSolo = indiceCueReproducaoSoloRef.current;
            const continuo = reproducaoContinuaPorWavRef.current;
            const emPreview = previewRecorteTelaAtivoRef.current;
            narracaoSegueAposJanelaPreviewRef.current = false;
            if (video && indiceSolo !== null) {
              video.pause();
              const cueSolo = cuesRef.current[indiceSolo];
              const jSolo = janelasRef.current[indiceSolo];
              if (emPreview && jSolo && cueSolo) {
                const estacionarEm = Math.max(
                  jSolo.inicioVideoSegundos,
                  Math.min(video.currentTime || 0, jSolo.fimVideoSegundos - 0.05),
                );
                try {
                  video.currentTime = estacionarEm;
                } catch {
                  /* ignore */
                }
                setTempoAtualSegundos(
                  Math.max(cueSolo.inicioSegundos, cueSolo.fimSegundos - 0.05),
                );
              } else if (cueSolo) {
                const estacionarEm = Math.max(
                  cueSolo.inicioSegundos,
                  Math.min(video.currentTime || 0, cueSolo.fimSegundos - 0.05),
                );
                video.currentTime = estacionarEm;
                setTempoAtualSegundos(estacionarEm);
              }
              if (continuo) {
                const proximo = indiceSolo + 1;
                if (proximo < cuesRef.current.length) {
                  tocarNarracaoWavDaCueNaPosicaoTimelineUi(proximo, { continuo: true });
                  return;
                }
                reproducaoContinuaPorWavRef.current = false;
              }
              indiceCueReproducaoSoloRef.current = null;
              if (emPreview && cueSolo) {
                pedidoSeekNarradoAposSairPreviewRef.current = Math.max(
                  0,
                  cueSolo.inicioSegundos,
                );
                definirPreviewRecorteTelaAtivoUi(false);
              }
            }
          }}
          onError={() => {
            setIndiceAudioTocando(null);
            indiceCueReproducaoSoloRef.current = null;
            reproducaoContinuaPorWavRef.current = false;
          }}
        />
        <header className="tb-modal-assistir-video-narrado-cabecalho">
          <div className="tb-modal-assistir-video-narrado-cabecalho-topo">
            <h2 id={tituloId}>Editar vídeo narrado</h2>
            {versoesVideoNarrado.length > 0 ? (
              <label className="tb-modal-assistir-video-narrado-seletor-versao">
                <span className="tb-modal-assistir-video-narrado-seletor-versao-rotulo">Versão</span>
                <select
                  className="tb-modal-assistir-video-narrado-seletor-versao-select"
                  value={versaoAtualVideoNarradoId ?? ""}
                  disabled={ocupado || versoesVideoNarrado.length < 1}
                  aria-label="Versão do vídeo narrado"
                  onChange={(e) => {
                    const id = e.target.value;
                    if (!id || id === versaoAtualVideoNarradoId) return;
                    void trocarVersaoVideoNarradoUi(id);
                  }}
                >
                  {versoesVideoNarrado.map((v) => {
                    const ehAtual = v.id === versaoAtualVideoNarradoId;
                    return (
                      <option key={v.id} value={v.id}>
                        {rotuloOpcaoVersaoVideoNarradoUiTranscribrothers(v, ehAtual)}
                      </option>
                    );
                  })}
                </select>
              </label>
            ) : null}
          </div>
          <p className="tb-modal-assistir-video-narrado-sub">
            «Atualizar narração» usa as legendas editadas aqui. «Gerar nova narração» / toolbar partem do
            Markdown com limpeza IA (não reaproveitam este VTT).
          </p>
          <button
            type="button"
            className="tb-modal-assistir-video-narrado-fechar"
            aria-label="Voltar ao tutorial"
            disabled={ocupado}
            onClick={onFechar}
          >
            ×
          </button>
        </header>

        <div className="tb-modal-assistir-video-narrado-corpo">
          <div className="tb-modal-assistir-video-narrado-col tb-modal-assistir-video-narrado-col--player">
            <div className="tb-modal-assistir-video-narrado-col-titulo-linha">
              <p className="tb-modal-assistir-video-narrado-col-titulo">
                Vídeo
                {previewRecorteTelaAtivo ? (
                  <span
                    className="tb-modal-assistir-video-narrado-preview-recorte-rotulo"
                    title="A barra e as cues seguem a timeline do narrado; a imagem é o recorte no original. O MP4 só muda após remux."
                  >
                    {" "}
                    · preview do recorte
                  </span>
                ) : null}
              </p>
              <label className="tb-modal-assistir-video-narrado-toggle-legendas">
                <input
                  type="checkbox"
                  checked={legendasNoVideo}
                  disabled={!urlTrackVttParaVideo}
                  onChange={(e) => setLegendasNoVideo(e.target.checked)}
                />
                Legendas no vídeo
              </label>
            </div>
            <div className="tb-modal-assistir-video-narrado-player-area">
              {jobId ? (
                <ComponentePlayerVideoJobControlesCustomizadosEModalAmpliarTelaMaiorTranscribrothers
                  jobId={jobId}
                  videoRef={videoRef}
                  urlVideoSrc={urlVideoPlayerEfetivo}
                  keyVideo={urlVideoPlayerEfetivo}
                  classNameVideo="tb-video tb-modal-assistir-video-narrado-video"
                  classNameEnvoltorio="tb-modal-assistir-video-narrado-player-envoltorio"
                  preloadVideo="metadata"
                  exibirBotaoTelaMaior={false}
                  exibirBotaoCapturarFrame={false}
                  faixaCuesTimeline={faixaCuesTimeline}
                  indiceCueAtivaFaixaTimeline={indiceCueAtiva}
                  aoClicarSegmentoFaixaCuesTimeline={selecionarOuAlternarReproducaoCueNaTimelineUi}
                  aoArrastarSegmentoFaixaCuesTimeline={
                    previewRecorteTelaAtivo ? undefined : arrastarCueNaTimelineParaInicio
                  }
                  forcarUiComoTocando={indiceAudioTocando !== null}
                  aoAlternarPlayPauseCustomizado={aoAlternarPlayPausePlayerComNarracaoAuxiliarUi}
                  timelineVirtualUi={
                    previewRecorteTelaAtivo
                      ? {
                          tempoAtualSegundos,
                          duracaoSegundos: duracaoTimelineNarradaParaBarraUi,
                          aoAlterarTempoPelaBarra: aoAlterarTempoPelaBarraDurantePreviewRecorteUi,
                        }
                      : null
                  }
                  overlaySobreVideo={
                    previewRecorteTelaAtivo && textoLegendaOverlayPreviewRecorte ? (
                      <p
                        className="tb-modal-assistir-video-narrado-legenda-overlay-preview"
                        role="status"
                        aria-live="polite"
                      >
                        {textoLegendaOverlayPreviewRecorte}
                      </p>
                    ) : null
                  }
                  faixaLegendas={
                    !previewRecorteTelaAtivo && urlTrackVttParaVideo ? (
                      <track
                        key={urlTrackVttParaVideo}
                        kind="subtitles"
                        src={urlTrackVttParaVideo}
                        srcLang="pt"
                        label="Português"
                        default
                      />
                    ) : null
                  }
                />
              ) : null}
              {trocandoVersaoVideoNarrado ? (
                <div
                  className="tb-modal-assistir-video-narrado-skeleton-player"
                  aria-busy="true"
                  aria-label="Carregando nova versão do vídeo"
                >
                  <div className="tb-modal-assistir-video-narrado-skeleton-player-tela tb-modal-assistir-video-narrado-skeleton-pulse" />
                  <div className="tb-modal-assistir-video-narrado-skeleton-player-barra tb-modal-assistir-video-narrado-skeleton-pulse" />
                </div>
              ) : null}
            </div>
          </div>

          <div className="tb-modal-assistir-video-narrado-col tb-modal-assistir-video-narrado-col--cues">
            <div className="tb-modal-assistir-video-narrado-col-titulo-linha">
              <p className="tb-modal-assistir-video-narrado-col-titulo">
                Legendas
                {cues.length > 0 ? ` (${cues.length})` : ""}
                {sujas ? " · editado" : ""}
                {janelasSujas ? " · tela" : ""}
              </p>
              <details className="tb-modal-assistir-video-narrado-ajuda-legendas">
                <summary
                  className="tb-modal-assistir-video-narrado-ajuda-legendas-resumo"
                  aria-label="Ajuda sobre edição das legendas"
                  title="Como editar as legendas"
                >
                  <svg
                    className="tb-modal-assistir-video-narrado-ajuda-legendas-icone"
                    width="16"
                    height="16"
                    viewBox="0 0 16 16"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                    aria-hidden="true"
                  >
                    <circle cx="8" cy="8" r="6.25" stroke="currentColor" strokeWidth="1.5" />
                    <path
                      d="M8 7.25v4"
                      stroke="currentColor"
                      strokeWidth="1.5"
                      strokeLinecap="round"
                    />
                    <circle cx="8" cy="5.1" r="0.9" fill="currentColor" />
                  </svg>
                </summary>
                <div className="tb-modal-assistir-video-narrado-ajuda-legendas-popover" role="note">
                  <p>
                    «Ajustar ao áudio» encolhe a cue quando a fala é menor que o slot.
                  </p>
                  <p>
                    «← →» ou arraste na faixa sob o progresso deslocam a cue sem sobrepor.
                  </p>
                  <p>
                    «Ouvir»/«Prévia» gera o áudio TTS; se o badge «prévia ok» aparecer, esse áudio
                    será reaproveitado ao gerar o vídeo (sem narrar de novo).
                  </p>
                  <p>
                    O número (#1, #2…) identifica a cue na lista e no tooltip da timeline.
                  </p>
                </div>
              </details>
            </div>
            {!urlLegendasVtt ? (
              <p className="tb-modal-assistir-video-narrado-aviso">
                Legendas ainda não geradas. Use «Gerar nova narração» ou «Gerar vídeo narrado» na barra do documento.
              </p>
            ) : trocandoVersaoVideoNarrado || carregandoCues ? (
              <SkeletonCuesListaVideoNarradoUiTranscribrothers
                quantidade={trocandoVersaoVideoNarrado ? 5 : 4}
              />
            ) : erroCues ? (
              <p className="tb-modal-assistir-video-narrado-aviso" role="alert">
                {erroCues}
              </p>
            ) : cues.length === 0 ? (
              <p className="tb-modal-assistir-video-narrado-aviso">Arquivo VTT sem cues utilizáveis.</p>
            ) : (
              <ul
                ref={listaCuesRef}
                className="tb-modal-assistir-video-narrado-cues-lista"
              >
                {cues.map((cue, i) => {
                  const ativa = i === indiceCueAtiva;
                  const janela = janelas[i];
                  const tocando = indiceAudioTocando === i;
                  const gerandoPreview = indiceAudioGerandoPreview === i;
                  const vozAtual = janela?.vozTts || vozPadraoJob || "Kore";
                  const vozNarrada = janela?.vozNarrada || vozPadraoJob || "Kore";
                  const vozDesatualizada = Boolean(
                    janela && cueVozDifereDaNarradaTranscribrothers(vozAtual, vozNarrada),
                  );
                  const vozDiferenteDoPadrao =
                    vozAtual.trim().toLowerCase() !==
                    String(vozPadraoJob || "Kore").trim().toLowerCase();
                  const listaVozesBase =
                    vozesDisponiveis.length > 0
                      ? vozesDisponiveis
                      : [{ id: vozAtual, estilo: "" }];
                  const listaVozesCue = listaVozesBase.some((op) => op.id === vozAtual)
                    ? listaVozesBase
                    : [{ id: vozAtual, estilo: "" }, ...listaVozesBase];
                  const textoFala = textoEfetivoParaTtsCueUiTranscribrothers(
                    cue.texto,
                    cue.textoTts,
                  );
                  const textoDesatualizado =
                    !!janela &&
                    cueTextoDifereDoNarradoTranscribrothers(
                      textoFala,
                      janela.textoNarrado || "",
                    );
                  const audioDesatualizado = textoDesatualizado || vozDesatualizada;
                  const previaAprovada = previaAudioCueBateComTextoEVozUiTranscribrothers(
                    previewAudioPorIndice[i],
                    textoFala,
                    vozAtual,
                  );
                  const falaDiferenteDaLegenda =
                    Boolean((cue.textoTts || "").trim()) &&
                    textoEfetivoParaTtsCueUiTranscribrothers(cue.texto, cue.textoTts) !==
                      textoEfetivoParaTtsCueUiTranscribrothers(cue.texto, "");
                  const falaTtsExpandida =
                    falaDiferenteDaLegenda || Boolean(indicesFalaTtsExpandidos[i]);
                  const regeneracaoForcada = Boolean(janela?.forcarRegenerarTts);
                  const duracaoAudioAjuste = resolverDuracaoAudioAtualDaCueParaAjusteUi(i);
                  const duracaoCueSlot = cue.fimSegundos - cue.inicioSegundos;
                  const podeAjustarAoAudio = cuePodeAjustarFimAoAudioNaTimelineUiTranscribrothers(
                    duracaoCueSlot,
                    duracaoAudioAjuste,
                  );
                  const podeDeslocarEsq = cuePodeDeslocarNaTimelineUiTranscribrothers(
                    cues,
                    i,
                    "esquerda",
                  );
                  const podeDeslocarDir = cuePodeDeslocarNaTimelineUiTranscribrothers(
                    cues,
                    i,
                    "direita",
                  );
                  const semNarracao = Boolean(janela?.semNarracao);
                  const duracaoJanelaTela = janela
                    ? Math.max(0, janela.fimVideoSegundos - janela.inicioVideoSegundos)
                    : 0;
                  return (
                    <li
                      key={`${cue.inicioSegundos}-${i}`}
                      ref={ativa ? cueAtivaRef : undefined}
                      className={
                        "tb-modal-assistir-video-narrado-cue-item" +
                        (ativa ? " tb-modal-assistir-video-narrado-cue-item--ativa" : "") +
                        (semNarracao ? " tb-modal-assistir-video-narrado-cue-item--sem-narracao" : "")
                      }
                      aria-current={ativa ? "true" : undefined}
                      onClick={() => selecionarCueNaListaSemAlterarPlaybackUi(i)}
                    >
                      <div className="tb-modal-assistir-video-narrado-cue-cabecalho">
                        <span
                          className="tb-modal-assistir-video-narrado-cue-numero"
                          title={`Cue ${i + 1} de ${cues.length}`}
                        >
                          #{i + 1}
                        </span>
                        <button
                          type="button"
                          className="tb-modal-assistir-video-narrado-cue-tempo"
                          title="Selecionar esta legenda (sem play/pause — use «Ir»)"
                          onClick={(e) => {
                            e.stopPropagation();
                            selecionarCueNaListaSemAlterarPlaybackUi(i);
                          }}
                        >
                          {formatarSegundosComoTimestampVttCurtoUiTranscribrothers(cue.inicioSegundos)}
                          {" – "}
                          {formatarSegundosComoTimestampVttCurtoUiTranscribrothers(cue.fimSegundos)}
                        </button>
                        <span
                          className="tb-modal-assistir-video-narrado-cue-duracao"
                          title="Duração desta cue na timeline do vídeo narrado"
                        >
                          {formatarDuracaoSegundosCurtaPortuguesUiTranscribrothers(
                            Math.max(0, duracaoCueSlot),
                          ) || "—"}
                        </span>
                        <button
                          type="button"
                          className="tb-modal-assistir-video-narrado-cue-ir"
                          title="Reproduzir só esta legenda (clique de novo para pausar)"
                          onClick={(e) => {
                            e.stopPropagation();
                            setIndiceCueSelecionadaSolo(i);
                            alternarReproducaoSoloCueNoVideoNarrado(i);
                          }}
                        >
                          Ir
                        </button>
                        <button
                          type="button"
                          className="tb-modal-assistir-video-narrado-cue-original"
                          disabled={
                            !jobId || !jobTemVideoEntrada || !janela || ocupado
                          }
                          title={
                            !jobTemVideoEntrada
                              ? "Este projeto não tem vídeo de entrada"
                              : !janela
                                ? "Janela de tela ainda não disponível para esta cue"
                                : "Ver este trecho no vídeo original"
                          }
                          onClick={(e) => {
                            e.stopPropagation();
                            setIndiceCueSelecionadaSolo(i);
                            setIndiceCueModalVideoOriginal(i);
                          }}
                        >
                          Original
                        </button>
                        <button
                          type="button"
                          className={
                            "tb-modal-assistir-video-narrado-cue-ouvir" +
                            (tocando ? " tb-modal-assistir-video-narrado-cue-ouvir--ativo" : "") +
                            (audioDesatualizado || regeneracaoForcada
                              ? " tb-modal-assistir-video-narrado-cue-ouvir--preview"
                              : "")
                          }
                          disabled={
                            ocupado ||
                            semNarracao ||
                            gerandoPreview ||
                            indiceAudioGerandoPreview !== null
                          }
                          title={
                            semNarracao
                              ? "Cue sem narração — use Ir para ver só o trecho de tela"
                              : gerandoPreview
                                ? "Gerando prévia TTS…"
                                : tocando
                                  ? "Parar áudio"
                                  : audioDesatualizado || !janela?.temWav || regeneracaoForcada
                                    ? "Ouvir a prévia TTS do texto/voz atuais"
                                    : "Ouvir o áudio TTS gravado desta cue"
                          }
                          onClick={(e) => {
                            e.stopPropagation();
                            setIndiceCueSelecionadaSolo(i);
                            ouvirOuPararAudioCue(i);
                          }}
                        >
                          {gerandoPreview
                            ? "Gerando…"
                            : tocando
                              ? "Parar"
                              : audioDesatualizado || !janela?.temWav || regeneracaoForcada
                                ? "Prévia"
                                : "Ouvir"}
                        </button>
                        <button
                          type="button"
                          className="tb-modal-assistir-video-narrado-cue-regenerar"
                          disabled={
                            ocupado ||
                            semNarracao ||
                            gerandoPreview ||
                            indiceAudioGerandoPreview !== null
                          }
                          title="Gerar nova narração TTS nesta cue (chama a LLM de novo)"
                          onClick={(e) => {
                            e.stopPropagation();
                            setIndiceCueSelecionadaSolo(i);
                            regenerarNarracaoTtsCueForcandoNovaChamadaUi(i);
                          }}
                        >
                          Regenerar
                        </button>
                      </div>
                      <div className="tb-modal-assistir-video-narrado-cue-acoes-extras">
                        {janela ? (
                          <label
                            className="tb-modal-assistir-video-narrado-cue-voz"
                            htmlFor={`tb-cue-voz-${i}`}
                            title="Voz Gemini TTS desta cue"
                          >
                            <span className="tb-modal-assistir-video-narrado-cue-voz-rotulo">
                              Voz
                              {vozDiferenteDoPadrao ? (
                                <span className="tb-modal-assistir-video-narrado-cue-voz-badge">
                                  override
                                </span>
                              ) : null}
                              {vozDesatualizada ? (
                                <span className="tb-modal-assistir-video-narrado-cue-voz-badge tb-modal-assistir-video-narrado-cue-voz-badge--suja">
                                  regenerar
                                </span>
                              ) : null}
                              {previaAprovada && (audioDesatualizado || regeneracaoForcada) ? (
                                <span
                                  className="tb-modal-assistir-video-narrado-cue-voz-badge tb-modal-assistir-video-narrado-cue-voz-badge--previa"
                                  title="Prévia ouvida e validada: será reaproveitada ao gerar o vídeo"
                                >
                                  prévia ok
                                </span>
                              ) : null}
                              {falaDiferenteDaLegenda ? (
                                <span
                                  className="tb-modal-assistir-video-narrado-cue-voz-badge"
                                  title="A fala (TTS) difere da legenda exibida no vídeo"
                                >
                                  fala ≠ legenda
                                </span>
                              ) : null}
                            </span>
                            <select
                              id={`tb-cue-voz-${i}`}
                              className="tb-modal-assistir-video-narrado-cue-voz-select"
                              value={vozAtual}
                              disabled={ocupado || semNarracao}
                              onChange={(e) => alterarVozTtsDaCue(i, e.target.value)}
                            >
                              {listaVozesCue.map((op) => (
                                <option key={op.id} value={op.id}>
                                  {op.estilo ? `${op.id} — ${op.estilo}` : op.id}
                                </option>
                              ))}
                            </select>
                          </label>
                        ) : null}
                        {janela ? (
                          <label
                            className="tb-modal-assistir-video-narrado-cue-sem-narracao"
                            title={
                              duracaoJanelaTela >= 60
                                ? `Atenção: este trecho tem ${Math.round(duracaoJanelaTela)}s de tela no export.`
                                : "Mantém o trecho de tela no vídeo, sem fala TTS"
                            }
                          >
                            <input
                              type="checkbox"
                              checked={semNarracao}
                              disabled={ocupado}
                              onChange={() => alternarSemNarracaoDaCue(i)}
                            />
                            <span>Sem narração</span>
                            {semNarracao && duracaoJanelaTela >= 60 ? (
                              <span className="tb-modal-assistir-video-narrado-cue-sem-narracao-aviso">
                                {Math.round(duracaoJanelaTela)}s de tela
                              </span>
                            ) : null}
                          </label>
                        ) : null}
                        <button
                          type="button"
                          className="tb-modal-assistir-video-narrado-cue-excluir"
                          disabled={ocupado || cues.length <= 1}
                          title="Remove esta cue da lista (não entra no MP4 ao gerar)"
                          onClick={() => excluirCueDaListaLocalUi(i)}
                        >
                          Excluir
                        </button>
                      </div>
                      <div className="tb-modal-assistir-video-narrado-cue-timeline-acoes">
                        <span className="tb-modal-assistir-video-narrado-cue-timeline-rotulo">
                          Cue
                        </span>
                        <div className="tb-modal-assistir-video-narrado-cue-janela-grupo">
                          <button
                            type="button"
                            className="tb-modal-assistir-video-narrado-cue-nudge"
                            disabled={ocupado || !podeDeslocarEsq}
                            title="Deslocar cue −0,25s (sem sobrepor)"
                            onClick={() => deslocarCueNaTimeline(i, "esquerda")}
                          >
                            ←
                          </button>
                          <button
                            type="button"
                            className="tb-modal-assistir-video-narrado-cue-nudge"
                            disabled={ocupado || !podeDeslocarDir}
                            title="Deslocar cue +0,25s (sem sobrepor)"
                            onClick={() => deslocarCueNaTimeline(i, "direita")}
                          >
                            →
                          </button>
                        </div>
                        {podeAjustarAoAudio ? (
                          <button
                            type="button"
                            className="tb-modal-assistir-video-narrado-cue-ajustar-audio"
                            disabled={ocupado}
                            title="Encolher o fim da cue até a duração do áudio atual (abre folga na timeline)"
                            onClick={() => ajustarCueAoAudioAtual(i)}
                          >
                            Ajustar ao áudio
                          </button>
                        ) : null}
                      </div>
                      <div className="tb-modal-assistir-video-narrado-cue-textos">
                        <label className="tb-modal-assistir-video-narrado-cue-texto-campo">
                          <span className="tb-modal-assistir-video-narrado-cue-texto-rotulo">
                            Legenda
                          </span>
                          <textarea
                            className={CLASS_TEXTAREA_CUE_LEGENDA_VIDEO_NARRADO}
                            value={cue.texto}
                            rows={2}
                            disabled={ocupado || semNarracao}
                            placeholder={semNarracao ? "Trecho só com vídeo (sem fala)" : undefined}
                            aria-label={`Texto da legenda ${i + 1}`}
                            onChange={(e) => {
                              atualizarTextoCue(i, e.target.value);
                              ajustarAlturaTextareaCueLegendaParaTextoCompletoTranscribrothers(
                                e.currentTarget,
                              );
                            }}
                          />
                        </label>
                        {!semNarracao ? (
                          falaTtsExpandida ? (
                            <div className="tb-modal-assistir-video-narrado-cue-texto-campo">
                              <div className="tb-modal-assistir-video-narrado-cue-texto-rotulo-linha">
                                <span className="tb-modal-assistir-video-narrado-cue-texto-rotulo">
                                  Fala (TTS)
                                  {falaDiferenteDaLegenda ? (
                                    <span className="tb-modal-assistir-video-narrado-cue-voz-badge">
                                      ativa
                                    </span>
                                  ) : null}
                                </span>
                                {!falaDiferenteDaLegenda ? (
                                  <button
                                    type="button"
                                    className="tb-modal-assistir-video-narrado-cue-fala-toggle"
                                    disabled={ocupado}
                                    onClick={() =>
                                      setIndicesFalaTtsExpandidos((prev) => {
                                        const proximo = { ...prev };
                                        delete proximo[i];
                                        return proximo;
                                      })
                                    }
                                  >
                                    Recolher
                                  </button>
                                ) : null}
                              </div>
                              <textarea
                                className={CLASS_TEXTAREA_CUE_LEGENDA_VIDEO_NARRADO}
                                value={cue.textoTts || ""}
                                rows={2}
                                disabled={ocupado}
                                placeholder="Opcional — deixe vazio para narrar igual à legenda"
                                aria-label={`Texto de fala TTS da cue ${i + 1}`}
                                title="Ajuste só a pronúncia. A legenda no vídeo continua com o texto de cima."
                                onChange={(e) => {
                                  atualizarTextoTtsCue(i, e.target.value);
                                  ajustarAlturaTextareaCueLegendaParaTextoCompletoTranscribrothers(
                                    e.currentTarget,
                                  );
                                }}
                              />
                            </div>
                          ) : (
                            <button
                              type="button"
                              className="tb-modal-assistir-video-narrado-cue-fala-toggle tb-modal-assistir-video-narrado-cue-fala-toggle--abrir"
                              disabled={ocupado}
                              title="Abre um campo só para ajustar a pronúncia (a legenda não muda)"
                              onClick={() =>
                                setIndicesFalaTtsExpandidos((prev) => ({ ...prev, [i]: true }))
                              }
                            >
                              Ajustar fala (TTS)
                            </button>
                          )
                        ) : null}
                      </div>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>
        </div>

        <footer className="tb-modal-assistir-video-narrado-rodape">
          <div className="tb-modal-assistir-video-narrado-rodape-grupos">
            <ComponenteMenuAcoesDropdownRodapeModalVideoNarradoTranscribrothers
              idMenu="baixar"
              rotulo="Baixar"
              ariaLabel="Baixar arquivos do vídeo narrado"
              desabilitado={ocupado}
              menuAbertoId={menuRodapeAbertoId}
              onMenuAbertoIdChange={setMenuRodapeAbertoId}
              itens={[
                {
                  id: "video",
                  rotulo: "Vídeo (MP4)",
                  onClick: onBaixarVideoMp4,
                },
                {
                  id: "video-legendas-queimadas",
                  rotulo: baixandoVideoComLegendasQueimadas
                    ? "Gerando vídeo com legendas…"
                    : "Vídeo com legendas embutidas (MP4)",
                  desabilitado: !urlVideoMp4 || !urlLegendasVtt || baixandoVideoComLegendasQueimadas,
                  onClick: () => void aoBaixarVideoComLegendasQueimadas(),
                },
                {
                  id: "legendas",
                  rotulo: "Legendas (VTT)",
                  desabilitado: !urlLegendasVtt,
                  onClick: onBaixarLegendasVtt,
                },
                {
                  id: "narracao",
                  rotulo: "Narração (WAV)",
                  desabilitado: !urlNarracaoWav,
                  onClick: onBaixarNarracaoWav,
                },
              ]}
            />
            <ComponenteMenuAcoesDropdownRodapeModalVideoNarradoTranscribrothers
              idMenu="salvar"
              rotulo="Salvar"
              ariaLabel="Salvar legendas ou tempos de tela"
              desabilitado={ocupado}
              badge={sujas || janelasSujas}
              menuAbertoId={menuRodapeAbertoId}
              onMenuAbertoIdChange={setMenuRodapeAbertoId}
              itens={[
                {
                  id: "legendas",
                  rotulo: salvandoLegendas ? "Salvando legendas…" : "Legendas (texto)",
                  desabilitado: !podeSalvar,
                  titulo: sujas
                    ? "Grava o texto das legendas no VTT."
                    : "Nenhuma alteração de texto para salvar.",
                  onClick: () => {
                    void salvarLegendas();
                  },
                },
                {
                  id: "tempos",
                  rotulo: salvandoJanelas ? "Salvando tempos…" : "Tempos de tela",
                  desabilitado: !podeSalvarJanelas,
                  titulo: janelasSujas
                    ? "Grava os tempos de tela no manifesto (sem remux)."
                    : "Nenhuma alteração de tempos para salvar.",
                  onClick: () => {
                    void salvarJanelas();
                  },
                },
              ]}
            />
            <ComponenteMenuAcoesDropdownRodapeModalVideoNarradoTranscribrothers
              idMenu="aplicar"
              rotulo="Aplicar"
              ariaLabel="Aplicar tempos ou regenerar narração"
              desabilitado={ocupado}
              menuAbertoId={menuRodapeAbertoId}
              onMenuAbertoIdChange={setMenuRodapeAbertoId}
              itens={[
                {
                  id: "tempos-video",
                  rotulo: regenerando ? "Aplicando tempos…" : "Tempos ao vídeo",
                  desabilitado: !podeAplicarTempos,
                  titulo: janelasSujas
                    ? "Salve os tempos antes de aplicar ao vídeo."
                    : "Remonta o MP4 com as janelas salvas (reutiliza o áudio TTS).",
                  onClick: onAplicarTemposJanelasAoVideo,
                },
                {
                  id: "atualizar-narracao",
                  rotulo: "Atualizar narração",
                  desabilitado: !podeAtualizarNarracao,
                  titulo: sujas
                    ? "Salve as legendas antes de atualizar a narração."
                    : "Regenera TTS só nas cues cujo texto mudou e remonta o MP4.",
                  onClick: onAtualizarNarracaoDasLegendas,
                },
                {
                  id: "gerar-edicoes",
                  rotulo: "Gerar vídeo com estas edições",
                  desabilitado: !podeGerarVideoComEstasEdicoes,
                  titulo:
                    "Salva edições, regenera TTS se o texto mudou (pula cues «Sem narração») e monta um MP4 só com as cues, como no play do modal.",
                  onClick: dispararGerarVideoComEstasEdicoes,
                },
                {
                  id: "gerar-nova",
                  rotulo: "Gerar nova narração",
                  desabilitado: ocupado,
                  titulo:
                    "Parte do Markdown com limpeza IA e gera TTS de todas as cues (não reusa este VTT).",
                  onClick: onGerarNovaNarracao,
                },
              ]}
            />
          </div>
          <div className="tb-modal-assistir-video-narrado-rodape-direita">
            <button
              type="button"
              className="tb-primary"
              disabled={!podeGerarVideoComEstasEdicoes}
              title="Salva as edições e gera um MP4 só com os trechos que têm cue (sem gaps), como no play do modal."
              onClick={dispararGerarVideoComEstasEdicoes}
            >
              {regenerando ? "Gerando…" : "Gerar vídeo com estas edições"}
            </button>
            {acaoSalvarContextual ? (
              <button
                type="button"
                className="tb-linkbtn"
                disabled={acaoSalvarContextual.desabilitado}
                title={acaoSalvarContextual.titulo}
                onClick={acaoSalvarContextual.onClick}
              >
                {acaoSalvarContextual.rotulo}
              </button>
            ) : null}
            <button
              type="button"
              className="tb-linkbtn"
              disabled={ocupado}
              onClick={onFechar}
            >
              Voltar ao tutorial
            </button>
          </div>
        </footer>
      </div>
    </div>
    {jobId &&
    indiceCueModalVideoOriginal !== null &&
    janelas[indiceCueModalVideoOriginal] ? (
      <ComponenteModalTrechoCueNoVideoOriginalEntradaJobTranscribrothers
        aberto
        jobId={jobId}
        indiceCueInicial={indiceCueModalVideoOriginal}
        janelas={janelas}
        textosCues={textosCuesParaModalOriginal}
        onFechar={() => setIndiceCueModalVideoOriginal(null)}
        onAplicarJanelas={(janelasNovas) => {
          const avisoSobreposicao = avisarSobreposicaoSomenteCuesAlteradasUiTranscribrothers(
            janelas,
            janelasNovas,
          );
          setJanelas(janelasNovas.map((j) => ({ ...j })));
          if (avisoSobreposicao) {
            pushToast(
              `${avisoSobreposicao} Janela aplicada mesmo assim. Ao salvar/remux o backend ainda pode recusar.`,
              "info",
            );
            return { ok: true as const, aviso: avisoSobreposicao };
          }
          pushToast(
            "Recortes de tela no editor. Toque a cue para pré-visualizar no vídeo original; salve os tempos e remuxe quando quiser.",
            "info",
          );
          return { ok: true as const };
        }}
      />
    ) : null}
    </>
  );
}
