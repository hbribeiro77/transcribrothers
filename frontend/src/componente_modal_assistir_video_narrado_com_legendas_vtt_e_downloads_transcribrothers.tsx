import { useCallback, useEffect, useId, useLayoutEffect, useMemo, useRef, useState } from "react";
import {
  cueTextoDifereDoNarradoTranscribrothers,
  cueVozDifereDaNarradaTranscribrothers,
  gerarPreviewTtsCueNarracaoTextoAtualJobApiTranscribrothers,
  listarJanelasVideoCuesNarracaoJobApiTranscribrothers,
  textoEfetivoParaTtsCueUiTranscribrothers,
  urlWavNarracaoPorCueJobTranscribrothers,
  type JanelaVideoCueLocalUiTranscribrothers,
  avisarSobreposicaoSomenteCuesAlteradasUiTranscribrothers,
  validarEstruturaBasicaJanelasVideoNaUiTranscribrothers,
} from "./modulo_api_janelas_video_e_wavs_por_cue_narracao_job_transcribrothers.ts";
import { baixarVideoNarradoComLegendasQueimadasJobApiTranscribrothers } from "./modulo_api_baixar_video_narrado_com_legendas_queimadas_job_transcribrothers.ts";
import {
  escolherModeloTtsDaListaDisponivelTranscribrothers,
  listarModelosTtsDaListaDisponivelTranscribrothers,
  rotuloCurtoModeloTtsParaUiTranscribrothers,
} from "./modulo_api_gerar_narracao_tts_markdown_job_transcribrothers.ts";
import {
  listarVersoesVideoNarradoJobApiTranscribrothers,
  tornarVersaoVideoNarradoAtualJobApiTranscribrothers,
  type MetaVersaoVideoNarradoApiTranscribrothers,
} from "./modulo_api_listar_versoes_video_narrado_job_transcribrothers.ts";
import { obterUrlAssetLegendasVttAlinhadasDosStepsJsonJobTranscribrothers } from "./modulo_api_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers.ts";
import { salvarModeloTtsNarracaoPreferidoNoNavegadorTranscribrothers } from "./modulo_armazenamento_local_modelo_tts_narracao_preferido_navegador_transcribrothers.ts";
import {
  carregarTemperaturaTtsNarracaoPreferidaSalvaNoNavegadorTranscribrothers,
  salvarTemperaturaTtsNarracaoPreferidaNoNavegadorTranscribrothers,
} from "./modulo_armazenamento_local_temperatura_tts_narracao_preferido_navegador_transcribrothers.ts";
import {
  carregarRitmoTtsNarracaoPreferidoSalvoNoNavegadorTranscribrothers,
  salvarRitmoTtsNarracaoPreferidoNoNavegadorTranscribrothers,
} from "./modulo_armazenamento_local_ritmo_tts_narracao_preferido_navegador_transcribrothers.ts";
import { ComponenteControleSliderTemperaturaTtsNarracaoComAjudaTranscribrothers } from "./componente_controle_slider_temperatura_tts_narracao_com_ajuda_transcribrothers.tsx";
import { ComponentePainelSugestaoReescritaTextoCueIaUsarOuDescartarTranscribrothers } from "./componente_painel_sugestao_reescrita_texto_cue_ia_usar_ou_descartar_transcribrothers.tsx";
import { sugerirReescritaTextoCueNarracaoJobApiTranscribrothers } from "./modulo_api_sugerir_reescrita_texto_cue_narracao_job_transcribrothers.ts";
import {
  RITMO_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
  TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
  listarOpcoesRitmoTtsNarracaoParaUiTranscribrothers,
  normalizarRitmoTtsNarracaoTranscribrothers,
  normalizarTemperaturaTtsNarracaoTranscribrothers,
  type RitmoTtsNarracaoTranscribrothers,
} from "./modulo_perfil_motor_sintese_tts_narracao_transcribrothers.ts";
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
  urlVideoFonteTelaCueParaPreviewUiTranscribrothers,
} from "./modulo_util_mapear_tempo_timeline_cue_para_janela_video_original_preview_ui_transcribrothers.ts";
import {
  ajustarFimCueTimelineAJanelaTelaUiTranscribrothers,
  ajustarFimCueTimelineAoAudioNarracaoUiTranscribrothers,
  cuePodeAjustarFimAJanelaTelaNaTimelineUiTranscribrothers,
  cuePodeAjustarFimAoAudioNaTimelineUiTranscribrothers,
  cuePodeDeslocarNaTimelineUiTranscribrothers,
  DELTA_DESLOCAR_CUE_TIMELINE_NARRACAO_SEGUNDOS_TRANSCRIBROTHERS,
  deslocarCueTimelineNarracaoSemSobreporVizinhasUiTranscribrothers,
  posicionarInicioCueTimelineNarracaoSemSobreporVizinhasUiTranscribrothers,
  resolverDuracaoAudioAtualDaCueParaAjusteTimelineUiTranscribrothers,
} from "./modulo_util_ajustar_e_deslocar_cues_timeline_narracao_sem_sobreposicao_ui_transcribrothers.ts";
import {
  garantirIdsClienteNasCuesTimelineNarracaoUiTranscribrothers,
  DURACAO_SEPARADOR_SECAO_SEGUNDOS_TRANSCRIBROTHERS,
  TEXTO_PADRAO_SEPARADOR_SECAO_TRANSCRIBROTHERS,
  inserirCueDepoisDoIndiceNaTimelineUiTranscribrothers,
  inserirSeparadorSecaoDepoisDoIndiceNaTimelineUiTranscribrothers,
  remaparRecordPorIndiceAposInserirUiTranscribrothers,
  remaparRecordPorIndiceAposReordenarUiTranscribrothers,
  resolverIndiceBaseParaInserirCueDepoisDoDestaqueUiTranscribrothers,
  reordenarCuesEmpacotandoTimelineNarracaoUiTranscribrothers,
  alinharJanelasAoNumeroDeCuesTimelineNarracaoUiTranscribrothers,
  type CueTimelineComIdClienteUiTranscribrothers,
} from "./modulo_util_inserir_e_reordenar_cues_timeline_narracao_video_narrado_ui_transcribrothers.ts";
import {
  DndContext,
  DragOverlay,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  type DragEndEvent,
  type DragOverEvent,
  type DragStartEvent,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import {
  SortableContext,
  sortableKeyboardCoordinates,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { ComponenteMenuAcoesDropdownRodapeModalVideoNarradoTranscribrothers } from "./componente_menu_acoes_dropdown_rodape_modal_video_narrado_transcribrothers.tsx";
import { salvarProjetoEditorVideoNarradoEdicoesModalJobApiTranscribrothers } from "./modulo_api_salvar_projeto_editor_video_narrado_edicoes_modal_job_transcribrothers.ts";
import {
  ComponentePlayerVideoJobControlesCustomizadosEModalAmpliarTelaMaiorTranscribrothers,
  type SegmentoFaixaCuesTimelinePlayerVideoTranscribrothers,
} from "./componente_player_video_job_controles_customizados_e_modal_ampliar_tela_maior_transcribrothers.tsx";
import { ComponenteModalTrechoCueNoVideoOriginalEntradaJobTranscribrothers } from "./componente_modal_trecho_cue_no_video_original_entrada_job_transcribrothers.tsx";
import { ComponenteModalEscolherFonteMidiaTelaCueBibliotecaTranscribrothers } from "./componente_modal_escolher_fonte_midia_tela_cue_biblioteca_transcribrothers.tsx";
import {
  ID_FONTE_VIDEO_ENTRADA_UI_TRANSCRIBROTHERS,
  gerarCartaoSecaoBibliotecaMidiasTelaJobApiTranscribrothers,
  normalizarIdFonteVideoUiTranscribrothers,
} from "./modulo_api_biblioteca_midias_tela_job_transcribrothers.ts";
import { calcularJanelaVideoAposTrocaFonteMidiaTelaUiTranscribrothers } from "./modulo_util_calcular_janela_video_apos_troca_fonte_midia_tela_ui_transcribrothers.ts";
import { CartaoCueSortableListaVideoNarradoTranscribrothers } from "./componente_cartao_cue_sortable_lista_video_narrado_transcribrothers.tsx";
import { ComponentePainelDebugCacheSegmentosVideoNarradoModalTranscribrothers } from "./componente_painel_debug_cache_segmentos_video_narrado_modal_transcribrothers.tsx";
import { formatarDuracaoSegundosCurtaPortuguesUiTranscribrothers } from "./modulo_util_formatar_duracao_segundos_curta_portugues_ui_transcribrothers.ts";
import { obterDuracaoSegundosArquivoAudioPorUrlNavegadorTranscribrothers } from "./modulo_util_obter_duracao_segundos_arquivo_audio_por_url_navegador_transcribrothers.ts";
import { usarToastFeedbackAcoesUiTranscribrothers } from "./provedor_contexto_e_hook_uso_toasts_feedback_acoes_ui_transcribrothers.tsx";
import { usarDialogoConfirmacaoAcaoUiSubstituindoWindowConfirmTranscribrothers } from "./hook_usar_dialogo_confirmacao_acao_ui_substituindo_window_confirm_transcribrothers.tsx";
import { audioMp4NarradoDesatualizadoEmRelacaoAoProjetoEditorDosStepsJsonTranscribrothers } from "./modulo_util_audio_mp4_narrado_desatualizado_em_relacao_ao_projeto_editor_steps_json_transcribrothers.ts";
import { erroPlayMidiaFoiInterrompidoPorPauseOuAbortUiTranscribrothers } from "./modulo_util_erro_play_midia_foi_interrompido_por_pause_ou_abort_ui_transcribrothers.ts";
import { previewRecortePrecisaAguardarTrocaSrcAntesDoPlayUiTranscribrothers } from "./modulo_util_preview_recorte_aguardar_troca_src_fonte_cue_antes_do_play_ui_transcribrothers.ts";
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
  /** Steps do job — detecta MP4 com áudio atrás dos WAVs após Salvar projeto. */
  stepsJsonJob?: Record<string, unknown> | null;
  litellmModelTts?: string | null;
  /** Lista completa (chat + TTS); o select filtra só slugs com -tts. */
  modelosLitellmDisponiveis?: string[] | null;
  /** Notifica o pai quando o usuário troca o modelo TTS (prévia/regenerar). */
  onModeloTtsPreferidoAlterado?: (modeloTts: string) => void;
  /** Temperatura TTS do job/steps ou preferência. */
  temperaturaTtsInicial?: number | null;
  onTemperaturaTtsPreferidaAlterada?: (temperatura: number) => void;
  /** Ritmo TTS do job/steps ou preferência. */
  ritmoTtsInicial?: string | null;
  onRitmoTtsPreferidoAlterado?: (ritmo: RitmoTtsNarracaoTranscribrothers) => void;
  /** Modelo de chat para sugestão IA de legenda. */
  litellmModelChat?: string | null;
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
    temperaturaTts?: number;
    ritmoTts?: RitmoTtsNarracaoTranscribrothers;
  }) => void;
  onLegendasSalvas?: () => void | Promise<void>;
  /** Após «tornar atual» uma versão — atualiza URLs do job no pai. */
  onJobAtualizado?: (job: JobStatus) => void;
  /** Há vídeo de entrada no job (não é só-áudio) — habilita «Origem» nas cues. */
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
      Boolean(atuais[i].semNarracao) !== Boolean(originais[i].semNarracao) ||
      normalizarIdFonteVideoUiTranscribrothers(atuais[i].idFonteVideo) !==
        normalizarIdFonteVideoUiTranscribrothers(originais[i].idFonteVideo)
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
  stepsJsonJob = null,
  litellmModelTts,
  modelosLitellmDisponiveis,
  onModeloTtsPreferidoAlterado,
  temperaturaTtsInicial,
  onTemperaturaTtsPreferidaAlterada,
  ritmoTtsInicial,
  onRitmoTtsPreferidoAlterado,
  litellmModelChat,
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
  const { pedirConfirmacao, elementoDialogoConfirmacao } =
    usarDialogoConfirmacaoAcaoUiSubstituindoWindowConfirmTranscribrothers();
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const audioCueRef = useRef<HTMLAudioElement | null>(null);
  const cueAtivaRef = useRef<HTMLLIElement | null>(null);
  const listaCuesRef = useRef<HTMLUListElement | null>(null);
  /** Enquanto definido, a reprodução solo/auxiliar está amarrada a esta cue. */
  const indiceCueReproducaoSoloRef = useRef<number | null>(null);
  /** Play contínuo com WAV nas posições atuais das cues (vídeo pausado; sem mutar volume). */
  const reproducaoContinuaPorWavRef = useRef(false);
  const cuesRef = useRef<CueTimelineComIdClienteUiTranscribrothers[]>([]);
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
  /** Coalesce de seek na barra (evita tempestade play/pause no arraste). */
  const debounceScrubBarraTimeoutRef = useRef<number | null>(null);
  const debounceScrubBarraTempoPendenteRef = useRef<number | null>(null);
  /** Cue escolhida no clique (destaque estável; evita “pular” para a próxima no limite fim==próximo início). */
  const [indiceCueSelecionadaSolo, setIndiceCueSelecionadaSolo] = useState<number | null>(null);
  /** Modal «Origem» (recorte na fonte de tela da cue; índice 0-based). */
  const [indiceCueModalVideoOriginal, setIndiceCueModalVideoOriginal] = useState<number | null>(
    null,
  );
  const [indiceCueModalEscolherFonte, setIndiceCueModalEscolherFonte] = useState<number | null>(
    null,
  );
  const [versoesVideoNarrado, setVersoesVideoNarrado] = useState<
    MetaVersaoVideoNarradoApiTranscribrothers[]
  >([]);
  const [versaoAtualVideoNarradoId, setVersaoAtualVideoNarradoId] = useState<string | null>(null);
  const [trocandoVersaoVideoNarrado, setTrocandoVersaoVideoNarrado] = useState(false);
  const [cues, setCues] = useState<CueTimelineComIdClienteUiTranscribrothers[]>([]);
  cuesRef.current = cues;
  const [cuesOriginais, setCuesOriginais] = useState<CueWebVttParaListaUiTranscribrothers[]>([]);
  cuesOriginaisRef.current = cuesOriginais;
  const [janelas, setJanelas] = useState<JanelaVideoCueLocalUiTranscribrothers[]>([]);
  janelasRef.current = janelas;
  const [janelasOriginais, setJanelasOriginais] = useState<JanelaVideoCueLocalUiTranscribrothers[]>(
    [],
  );
  const [idCueArrastando, setIdCueArrastando] = useState<string | null>(null);
  const [idCueSobre, setIdCueSobre] = useState<string | null>(null);
  const sensorsOrdenacaoCues = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );
  const [carregandoCues, setCarregandoCues] = useState(false);
  const [erroCues, setErroCues] = useState<string | null>(null);
  const [tempoAtualSegundos, setTempoAtualSegundos] = useState(0);
  const [legendasNoVideo, setLegendasNoVideo] = useState(true);
  const opcoesModeloTts = useMemo(
    () => listarModelosTtsDaListaDisponivelTranscribrothers(modelosLitellmDisponiveis || []),
    [modelosLitellmDisponiveis],
  );
  const [modeloTtsUi, setModeloTtsUi] = useState(() => {
    const opcoes = listarModelosTtsDaListaDisponivelTranscribrothers(
      modelosLitellmDisponiveis || [],
    );
    const escolhido = escolherModeloTtsDaListaDisponivelTranscribrothers(opcoes, litellmModelTts);
    return (escolhido && opcoes.includes(escolhido) ? escolhido : opcoes[0]) || "";
  });
  const modeloTtsEfetivo =
    (modeloTtsUi && opcoesModeloTts.includes(modeloTtsUi) ? modeloTtsUi : null) ||
    escolherModeloTtsDaListaDisponivelTranscribrothers(opcoesModeloTts, litellmModelTts) ||
    (litellmModelTts || "").trim() ||
    null;
  const [temperaturaTtsUi, setTemperaturaTtsUi] = useState(() =>
    normalizarTemperaturaTtsNarracaoTranscribrothers(
      temperaturaTtsInicial ??
        carregarTemperaturaTtsNarracaoPreferidaSalvaNoNavegadorTranscribrothers() ??
        TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
    ),
  );
  const temperaturaTtsEfetiva = normalizarTemperaturaTtsNarracaoTranscribrothers(temperaturaTtsUi);
  const opcoesRitmoTts = useMemo(() => listarOpcoesRitmoTtsNarracaoParaUiTranscribrothers(), []);
  const [ritmoTtsUi, setRitmoTtsUi] = useState<RitmoTtsNarracaoTranscribrothers>(() =>
    normalizarRitmoTtsNarracaoTranscribrothers(
      ritmoTtsInicial ??
        carregarRitmoTtsNarracaoPreferidoSalvoNoNavegadorTranscribrothers() ??
        RITMO_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
    ),
  );
  const ritmoTtsEfetivo = normalizarRitmoTtsNarracaoTranscribrothers(ritmoTtsUi);
  const [sugestoesReescritaLegendaPorIndice, setSugestoesReescritaLegendaPorIndice] = useState<
    Record<number, string>
  >({});
  const [indicesSugerindoReescritaLegenda, setIndicesSugerindoReescritaLegenda] = useState<
    Set<number>
  >(() => new Set());
  const [salvandoProjeto, setSalvandoProjeto] = useState(false);
  /** Após promover prévia no save, até o job/steps refletirem ou o MP4 ser regenerado. */
  const [audioMp4DesatualizadoLocal, setAudioMp4DesatualizadoLocal] = useState(false);
  const [baixandoVideoComLegendasQueimadas, setBaixandoVideoComLegendasQueimadas] = useState(false);
  const [versaoCacheTrackVtt, setVersaoCacheTrackVtt] = useState(0);
  const [indiceAudioTocando, setIndiceAudioTocando] = useState<number | null>(null);
  const [indiceAudioGerandoPreview, setIndiceAudioGerandoPreview] = useState<number | null>(null);
  const [menuRodapeAbertoId, setMenuRodapeAbertoId] = useState<string | null>(null);
  const [painelDebugCacheAberto, setPainelDebugCacheAberto] = useState(false);
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
  /** Exclusão, «sem narração», texto/tempos locais ou WAVs mais novos que o MP4. */
  const audioMp4DesatualizadoNoJob = useMemo(
    () =>
      audioMp4NarradoDesatualizadoEmRelacaoAoProjetoEditorDosStepsJsonTranscribrothers(
        stepsJsonJob,
      ),
    [stepsJsonJob],
  );
  useEffect(() => {
    // Job/steps já sincronizados (ex.: após Gerar vídeo) — limpa override local.
    if (
      stepsJsonJob &&
      stepsJsonJob.editor_video_narrado_audio_mp4_desatualizado === false
    ) {
      setAudioMp4DesatualizadoLocal(false);
    }
  }, [stepsJsonJob]);
  const audioDoMp4NaoRefleteEdicoesLocais =
    sujas ||
    temposCuesDeslocados ||
    janelasSujas ||
    audioMp4DesatualizadoNoJob ||
    audioMp4DesatualizadoLocal;

  const urlVideoEntradaJob = jobId
    ? urlVideoEntradaJobParaPreviewUiTranscribrothers(jobId)
    : "";
  const indiceCueParaFontePreview = indiceAudioTocando ?? indiceCueSelecionadaSolo ?? 0;
  const urlVideoFontePreviewAtiva =
    jobId && previewRecorteTelaAtivo
      ? urlVideoFonteTelaCueParaPreviewUiTranscribrothers(
          jobId,
          janelas[indiceCueParaFontePreview]?.idFonteVideo,
        )
      : "";
  const urlVideoPlayerEfetivo =
    previewRecorteTelaAtivo && (jobTemVideoEntrada || Boolean(urlVideoFontePreviewAtiva))
      ? urlVideoFontePreviewAtiva || urlVideoEntradaJob
      : urlVideoMp4;
  const urlVideoPlayerEfetivoRef = useRef(urlVideoPlayerEfetivo);
  urlVideoPlayerEfetivoRef.current = urlVideoPlayerEfetivo;

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

  useEffect(() => {
    if (!aberto) return;
    const escolhido = escolherModeloTtsDaListaDisponivelTranscribrothers(
      opcoesModeloTts,
      litellmModelTts,
    );
    setModeloTtsUi(
      (escolhido && opcoesModeloTts.includes(escolhido) ? escolhido : opcoesModeloTts[0]) || "",
    );
    setTemperaturaTtsUi(
      normalizarTemperaturaTtsNarracaoTranscribrothers(
        temperaturaTtsInicial ??
          carregarTemperaturaTtsNarracaoPreferidaSalvaNoNavegadorTranscribrothers() ??
          TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
      ),
    );
    setRitmoTtsUi(
      normalizarRitmoTtsNarracaoTranscribrothers(
        ritmoTtsInicial ??
          carregarRitmoTtsNarracaoPreferidoSalvoNoNavegadorTranscribrothers() ??
          RITMO_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
      ),
    );
    setSugestoesReescritaLegendaPorIndice({});
    setIndicesSugerindoReescritaLegenda(new Set());
  }, [aberto, litellmModelTts, opcoesModeloTts, temperaturaTtsInicial, ritmoTtsInicial]);

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
        const ok = await pedirConfirmacao({
          titulo: "Trocar de versão?",
          mensagem:
            "Há edições locais não salvas nesta versão. Trocar de versão descarta essas alterações. Continuar?",
          rotuloConfirmar: "Trocar versão",
          varianteConfirmar: "destrutiva",
        });
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
            setCues(garantirIdsClienteNasCuesTimelineNarracaoUiTranscribrothers(lista));
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
      pedirConfirmacao,
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
    if (regenerando || salvandoProjeto) {
      setMenuRodapeAbertoId(null);
    }
  }, [regenerando, salvandoProjeto]);

  useEffect(() => {
    if (!aberto) return;
    const aoTeclar = (evento: KeyboardEvent) => {
      if (evento.key !== "Escape") return;
      // Modal do trecho original trata o Escape sozinha.
      if (indiceCueModalVideoOriginal !== null) return;
      if (!regenerando && !salvandoProjeto) {
        onFechar();
      }
    };
    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
  }, [
    aberto,
    onFechar,
    regenerando,
    salvandoProjeto,
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
      setSalvandoProjeto(false);
      setAudioMp4DesatualizadoLocal(false);
      if (debounceScrubBarraTimeoutRef.current != null) {
        window.clearTimeout(debounceScrubBarraTimeoutRef.current);
        debounceScrubBarraTimeoutRef.current = null;
      }
      debounceScrubBarraTempoPendenteRef.current = null;
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
          setCues(garantirIdsClienteNasCuesTimelineNarracaoUiTranscribrothers(lista));
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
            idFonteVideo: normalizarIdFonteVideoUiTranscribrothers(c.id_fonte_video),
          };
        });
        setJanelas((prev) => {
          const cuesLen = cuesRef.current.length;
          // Edição local alinhada (inserir/excluir) não deve ser apagada pelo manifesto antigo.
          if (prev.length > 0 && prev.length === cuesLen && prev.length !== lista.length) {
            return prev;
          }
          if (cuesLen > lista.length && prev.length === cuesLen) {
            return prev;
          }
          return lista;
        });
        setJanelasOriginais(lista.map((j) => ({ ...j })));
        const aplicarTextoTtsDoManifesto = (
          prev: CueTimelineComIdClienteUiTranscribrothers[],
        ): CueTimelineComIdClienteUiTranscribrothers[] =>
          prev.map((cue, i) => {
            const tts = String(resp.cues[i]?.texto_tts || "").trim();
            if ((cue.textoTts || "") === tts) return cue;
            return { ...cue, textoTts: tts };
          });
        setCues(aplicarTextoTtsDoManifesto);
        setCuesOriginais((prev) =>
          prev.map((cue, i) => {
            const tts = String(resp.cues[i]?.texto_tts || "").trim();
            if ((cue.textoTts || "") === tts) return cue;
            return { ...cue, textoTts: tts };
          }),
        );
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

  // VTT e manifesto podem divergir (ex.: geração falhou após gravar legendas).
  useEffect(() => {
    if (!aberto || carregandoCues || cues.length === 0) return;
    if (janelas.length === 0 || janelas.length === cues.length) return;
    const alinhadas = alinharJanelasAoNumeroDeCuesTimelineNarracaoUiTranscribrothers({
      quantidadeCues: cues.length,
      janelas,
      vozPadrao: vozPadraoJob || "Kore",
    });
    if (alinhadas.length === cues.length && alinhadas.length !== janelas.length) {
      setJanelas(alinhadas);
    }
  }, [aberto, carregandoCues, cues.length, janelas, vozPadraoJob]);

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
          if (erroPlayMidiaFoiInterrompidoPorPauseOuAbortUiTranscribrothers(e)) return;
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
        if (erroPlayMidiaFoiInterrompidoPorPauseOuAbortUiTranscribrothers(e)) return;
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
   * Legenda no quadro via overlay (quebra de linha confiável).
   * Substitui o `<track>` nativo nesta modal — mesmo texto da cue ativa por tempo.
   */
  const textoLegendaOverlayNoVideo = useMemo(() => {
    if (!legendasNoVideo || indiceCueAtivaPorTempo < 0) return "";
    return String(cues[indiceCueAtivaPorTempo]?.texto || "").trim();
  }, [legendasNoVideo, indiceCueAtivaPorTempo, cues]);

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

      // Preview do recorte na fonte de tela da cue (entrada ou biblioteca), sem remux.
      if (
        j &&
        (jobTemVideoEntrada ||
          normalizarIdFonteVideoUiTranscribrothers(j.idFonteVideo) !==
            ID_FONTE_VIDEO_ENTRADA_UI_TRANSCRIBROTHERS)
      ) {
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

        if (!jobId) {
          definirPreviewRecorteTelaAtivoUi(true);
          return true;
        }
        const urlFonteAlvo = urlVideoFonteTelaCueParaPreviewUiTranscribrothers(
          jobId,
          j.idFonteVideo,
        );
        const aguardarTrocaSrc = previewRecortePrecisaAguardarTrocaSrcAntesDoPlayUiTranscribrothers({
          previewRecorteAtivo: previewRecorteTelaAtivoRef.current,
          urlVideoPlayerAtual: urlVideoPlayerEfetivoRef.current,
          urlVideoFonteAlvo: urlFonteAlvo,
        });
        if (previewRecorteTelaAtivoRef.current) {
          if (!aguardarTrocaSrc) {
            executarPedidoPlayPreviewRecorteTelaUi();
          }
          // Fonte diferente: mantém o pedido; o effect dispara após urlVideoPlayerEfetivo mudar.
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
            if (erroPlayMidiaFoiInterrompidoPorPauseOuAbortUiTranscribrothers(e)) return;
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
            if (erroPlayMidiaFoiInterrompidoPorPauseOuAbortUiTranscribrothers(e)) return;
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
      jobId,
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
   * Arraste contínuo só faz seek na cue atual; troca de cue / play é debounced.
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
        (Boolean(audio && !audio.paused) ||
          !video.paused ||
          narracaoSegueAposJanelaPreviewRef.current);

      if (mesmoSoloTocando) {
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
        return;
      }

      // Troca de cue no arraste: atualiza só o ponteiro visual e agenda um play no fim do gesto.
      setIndiceCueSelecionadaSolo(indiceAlvo);
      debounceScrubBarraTempoPendenteRef.current = t;
      if (debounceScrubBarraTimeoutRef.current != null) {
        window.clearTimeout(debounceScrubBarraTimeoutRef.current);
      }
      debounceScrubBarraTimeoutRef.current = window.setTimeout(() => {
        debounceScrubBarraTimeoutRef.current = null;
        const tFinal = debounceScrubBarraTempoPendenteRef.current;
        debounceScrubBarraTempoPendenteRef.current = null;
        if (tFinal == null) return;
        const idx = indiceCueNoInstanteTimelineUiTranscribrothers(cuesRef.current, tFinal);
        if (idx < 0) return;
        tocarNarracaoWavDaCueNaPosicaoTimelineUi(idx, {
          continuo: false,
          partirDoTempoTimelineSegundos: tFinal,
        });
      }, 140);
    },
    [tocarNarracaoWavDaCueNaPosicaoTimelineUi],
  );

  /**
   * Seek na barra fora do preview: timeline narrada pode ser mais longa que o MP4
   * (ex.: cue adicionada). Além do fim do arquivo / com edições locais → cadeia WAV/preview.
   */
  const aoAlterarTempoPelaBarraForaDoPreviewRecorteUi = useCallback(
    (tempoTimelineSegundos: number) => {
      if (previewRecorteTelaAtivoRef.current) {
        aoAlterarTempoPelaBarraDurantePreviewRecorteUi(tempoTimelineSegundos);
        return;
      }
      const video = videoRef.current;
      const t = Math.max(0, tempoTimelineSegundos);
      setTempoAtualSegundos(t);
      if (!video) return;

      const durMp4 =
        duracaoMp4NarradoSegundos > 0
          ? duracaoMp4NarradoSegundos
          : Number.isFinite(video.duration) && video.duration > 0
            ? video.duration
            : 0;
      const alemDoMp4 = durMp4 > 0 && t > durMp4 - 0.02;
      if (audioDoMp4NaoRefleteEdicoesLocais || alemDoMp4) {
        const indice = indiceCueNoInstanteTimelineUiTranscribrothers(cuesRef.current, t);
        if (indice < 0) return;
        debounceScrubBarraTempoPendenteRef.current = t;
        if (debounceScrubBarraTimeoutRef.current != null) {
          window.clearTimeout(debounceScrubBarraTimeoutRef.current);
        }
        debounceScrubBarraTimeoutRef.current = window.setTimeout(() => {
          debounceScrubBarraTimeoutRef.current = null;
          const tFinal = debounceScrubBarraTempoPendenteRef.current;
          debounceScrubBarraTempoPendenteRef.current = null;
          if (tFinal == null) return;
          const idx = indiceCueNoInstanteTimelineUiTranscribrothers(cuesRef.current, tFinal);
          if (idx < 0) return;
          tocarNarracaoWavDaCueNaPosicaoTimelineUi(idx, {
            continuo: false,
            partirDoTempoTimelineSegundos: tFinal,
          });
        }, 140);
        return;
      }

      try {
        const teto =
          Number.isFinite(video.duration) && video.duration > 0
            ? Math.max(0, video.duration - 0.05)
            : t;
        video.currentTime = Math.min(t, teto);
      } catch {
        /* ignore */
      }
    },
    [
      aoAlterarTempoPelaBarraDurantePreviewRecorteUi,
      audioDoMp4NaoRefleteEdicoesLocais,
      duracaoMp4NarradoSegundos,
      tocarNarracaoWavDaCueNaPosicaoTimelineUi,
    ],
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
          litellmModel: modeloTtsEfetivo,
          voz: vozUsada,
          temperaturaTts: temperaturaTtsEfetiva,
          ritmoTts: ritmoTtsEfetivo,
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
        if (erroPlayMidiaFoiInterrompidoPorPauseOuAbortUiTranscribrothers(e)) return;
        pushToast(e instanceof Error ? e.message : "Falha na prévia TTS.", "error");
      } finally {
        setIndiceAudioGerandoPreview(null);
      }
    },
    [cues, jobId, modeloTtsEfetivo, temperaturaTtsEfetiva, ritmoTtsEfetivo, vozPadraoJob, pushToast],
  );

  const sugerirReescritaLegendaCueUi = useCallback(
    async (indice: number) => {
      if (!jobId) return;
      const cue = cues[indice];
      if (!cue || !(cue.texto || "").trim()) {
        pushToast("Informe o texto da legenda para pedir sugestão.", "error");
        return;
      }
      setIndicesSugerindoReescritaLegenda((prev) => new Set(prev).add(indice));
      try {
        const res = await sugerirReescritaTextoCueNarracaoJobApiTranscribrothers(jobId, {
          indice,
          texto: cue.texto,
          litellmModelChat,
        });
        if (!res.ok || !(res.sugestao || "").trim()) {
          pushToast(res.mensagem || "A IA não devolveu uma sugestão utilizável.", "error");
          return;
        }
        setSugestoesReescritaLegendaPorIndice((prev) => ({
          ...prev,
          [indice]: res.sugestao.trim(),
        }));
        pushToast("Sugestão pronta — revise antes de usar.", "success");
      } catch (e: unknown) {
        pushToast(e instanceof Error ? e.message : "Falha ao sugerir reescrita.", "error");
      } finally {
        setIndicesSugerindoReescritaLegenda((prev) => {
          const next = new Set(prev);
          next.delete(indice);
          return next;
        });
      }
    },
    [jobId, cues, litellmModelChat, pushToast],
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
          if (erroPlayMidiaFoiInterrompidoPorPauseOuAbortUiTranscribrothers(e)) return;
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
          if (erroPlayMidiaFoiInterrompidoPorPauseOuAbortUiTranscribrothers(e)) return;
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
      const vozAtual = j?.vozTts || "";
      const audioNarradoDesatualizado =
        !!j &&
        (cueTextoDifereDoNarradoTranscribrothers(textoFala, j.textoNarrado || "") ||
          cueVozDifereDaNarradaTranscribrothers(vozAtual, j.vozNarrada || ""));
      const preview = previewAudioPorIndice[indice];
      return resolverDuracaoAudioAtualDaCueParaAjusteTimelineUiTranscribrothers({
        textoFalaAtual: textoFala,
        vozAtual,
        audioNarradoDesatualizado,
        preview: preview
          ? { texto: preview.texto, voz: preview.voz, duracaoSegundos: preview.duracaoSegundos }
          : undefined,
        duracaoWavGravadoSegundos: duracoesWavPorIndice[indice],
      });
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
      setCues(
        garantirIdsClienteNasCuesTimelineNarracaoUiTranscribrothers(
          r.cues.map((c, i) => ({ ...c, idCliente: cues[i]?.idCliente })),
        ),
      );
      setIndiceCueSelecionadaSolo(indice);
      const msg =
        r.deslocouSegundos > 0
          ? "Cue ajustada ao áudio — cues seguintes foram empurradas se necessário."
          : "Cue ajustada ao áudio — ficou folga na timeline para deslocar.";
      pushToast(msg, "success");
    },
    [cues, pushToast, resolverDuracaoAudioAtualDaCueParaAjusteUi],
  );

  const ajustarCueAJanelaTelaAtual = useCallback(
    (indice: number) => {
      void (async () => {
        const j = janelas[indice];
        if (!j) {
          pushToast("Janela de tela ainda não disponível para esta cue.", "info");
          return;
        }
        const durTela = Math.max(0, j.fimVideoSegundos - j.inicioVideoSegundos);
        const durAudio = resolverDuracaoAudioAtualDaCueParaAjusteUi(indice);
        if (
          typeof durAudio === "number" &&
          Number.isFinite(durAudio) &&
          durAudio > durTela + 0.05
        ) {
          const rotuloTela =
            formatarDuracaoSegundosCurtaPortuguesUiTranscribrothers(durTela) ||
            `${durTela.toFixed(1)}s`;
          const rotuloAudio =
            formatarDuracaoSegundosCurtaPortuguesUiTranscribrothers(durAudio) ||
            `${durAudio.toFixed(1)}s`;
          const ok = await pedirConfirmacao({
            titulo: "Ajustar à tela com áudio maior?",
            mensagem:
              `A janela de tela tem ${rotuloTela} e o áudio atual tem ${rotuloAudio}. ` +
              "O slot da cue ficará menor que a fala (estouro no vídeo narrado). Continuar mesmo assim?",
            rotuloConfirmar: "Ajustar à tela",
            varianteConfirmar: "neutra",
          });
          if (!ok) return;
        }
        const r = ajustarFimCueTimelineAJanelaTelaUiTranscribrothers(cues, indice, durTela);
        if (!r.ok) {
          pushToast(r.motivo, "info");
          return;
        }
        setCues(
          garantirIdsClienteNasCuesTimelineNarracaoUiTranscribrothers(
            r.cues.map((c, i) => ({ ...c, idCliente: cues[i]?.idCliente })),
          ),
        );
        setIndiceCueSelecionadaSolo(indice);
        const msg =
          r.deslocouSegundos > 0
            ? "Cue ajustada à tela — cues seguintes foram empurradas se necessário."
            : "Cue ajustada à tela — ficou folga na timeline para deslocar.";
        pushToast(msg, "success");
      })();
    },
    [
      cues,
      janelas,
      pedirConfirmacao,
      pushToast,
      resolverDuracaoAudioAtualDaCueParaAjusteUi,
    ],
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
      setCues(
        garantirIdsClienteNasCuesTimelineNarracaoUiTranscribrothers(
          r.cues.map((c, i) => ({ ...c, idCliente: cues[i]?.idCliente })),
        ),
      );
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
      setCues(
        garantirIdsClienteNasCuesTimelineNarracaoUiTranscribrothers(
          r.cues.map((c, i) => ({ ...c, idCliente: cues[i]?.idCliente })),
        ),
      );
      setIndiceCueSelecionadaSolo(indice);
    },
    [cues],
  );

  useLayoutEffect(() => {
    if (!aberto || carregandoCues) return;
    ajustarAlturasTodosTextareasCuesNaListaTranscribrothers(listaCuesRef.current);
  }, [aberto, carregandoCues, cues]);

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

  const urlsAudioNarracaoParaModalOriginal = useMemo(() => {
    const mapa: Record<number, string> = {};
    for (let i = 0; i < cues.length; i++) {
      const url = resolverUrlAudioNarracaoDaCueParaPlaybackUi(i);
      if (url) mapa[i] = url;
    }
    return mapa;
  }, [cues, janelas, previewAudioPorIndice, resolverUrlAudioNarracaoDaCueParaPlaybackUi]);

  useEffect(() => {
    if (!aberto) setPainelDebugCacheAberto(false);
  }, [aberto]);

  if (!aberto) return null;

  const ocupado =
    regenerando ||
    salvandoProjeto ||
    baixandoVideoComLegendasQueimadas ||
    trocandoVersaoVideoNarrado;
  const projetoSujo = sujas || janelasSujas;
  const podeSalvarProjeto =
    Boolean(jobId) &&
    Boolean(urlLegendasVtt) &&
    cues.length > 0 &&
    janelas.length === cues.length &&
    projetoSujo &&
    !ocupado &&
    !carregandoCues &&
    !erroCues;
  const podeGerarVideoComEstasEdicoes =
    Boolean(jobId) && cues.length > 0 && !ocupado && !carregandoCues && !erroCues;

  const salvarProjetoEditorUi = () => {
    void (async () => {
      if (!jobId || salvandoProjeto || regenerando) return;
      if (cues.length === 0 || janelas.length !== cues.length) {
        pushToast(
          "Não foi possível salvar: quantidade de cues e tempos de tela não batem.",
          "error",
        );
        return;
      }
      const erroLocal = validarEstruturaBasicaJanelasVideoNaUiTranscribrothers(
        janelas.map((j) => ({
          inicio_video_segundos: j.inicioVideoSegundos,
          fim_video_segundos: j.fimVideoSegundos,
        })),
      );
      if (erroLocal) {
        pushToast(erroLocal, "error");
        return;
      }
      setSalvandoProjeto(true);
      try {
        const resp = await salvarProjetoEditorVideoNarradoEdicoesModalJobApiTranscribrothers(
          jobId,
          {
            cues: cues.map((c, i) => ({
              inicio_segundos: c.inicioSegundos,
              fim_segundos: c.fimSegundos,
              texto: c.texto,
              texto_tts: (c.textoTts || "").trim() || undefined,
              sem_narracao: Boolean(janelas[i]?.semNarracao),
              voz_tts: janelas[i]?.vozTts || vozPadraoJob || "Kore",
              forcar_regenerar_tts: Boolean(janelas[i]?.forcarRegenerarTts),
            })),
            janelas: janelas.map((j) => ({
              inicio_video_segundos: j.inicioVideoSegundos,
              fim_video_segundos: j.fimVideoSegundos,
              id_fonte_video: normalizarIdFonteVideoUiTranscribrothers(j.idFonteVideo),
            })),
          },
        );
        const promovidos = new Set(resp.indices_previews_promovidas ?? []);
        const janelasAposSave = janelas.map((j, i) => {
          if (!promovidos.has(i)) {
            return { ...j, forcarRegenerarTts: false };
          }
          const cue = cues[i];
          const textoFala = textoEfetivoParaTtsCueUiTranscribrothers(
            cue?.texto || "",
            cue?.textoTts || "",
          );
          const voz = j.vozTts || vozPadraoJob || "Kore";
          return {
            ...j,
            temWav: true,
            urlWav: `${urlWavNarracaoPorCueJobTranscribrothers(jobId, i)}?v=${Date.now()}`,
            textoNarrado: textoFala,
            textoTtsNarrado: (cue?.textoTts || "").trim(),
            vozNarrada: voz,
            forcarRegenerarTts: false,
          };
        });
        setJanelas(janelasAposSave);
        setCuesOriginais(cues.map((c) => ({ ...c })));
        setJanelasOriginais(janelasAposSave.map((j) => ({ ...j })));
        setVersaoCacheTrackVtt(Date.now());
        const nPrev = resp.previews_promovidas ?? 0;
        // Checkpoint sem remux: player deve usar preview/WAV até gerar o MP4 de novo.
        setAudioMp4DesatualizadoLocal(true);
        pushToast(
          nPrev > 0
            ? `Projeto salvo (legendas, tempos e ${nPrev} áudio(s) da prévia). O MP4 só muda ao gerar o vídeo.`
            : "Projeto salvo (legendas e tempos). O MP4 só muda ao gerar o vídeo.",
          "success",
        );
        if (onLegendasSalvas) await onLegendasSalvas();
      } catch (e: unknown) {
        pushToast(e instanceof Error ? e.message : String(e), "error");
      } finally {
        setSalvandoProjeto(false);
      }
    })();
  };

  const dispararGerarVideoComEstasEdicoes = () => {
    void (async () => {
      const videoEl = videoRef.current;
      const durEntrada =
        videoEl && Number.isFinite(videoEl.duration) && videoEl.duration > 0
          ? videoEl.duration
          : null;
      const janelasAlinhadas = alinharJanelasAoNumeroDeCuesTimelineNarracaoUiTranscribrothers({
        quantidadeCues: cues.length,
        janelas,
        duracaoVideoEntradaSegundos: durEntrada,
        vozPadrao: vozPadraoJob || "Kore",
      });
      if (janelasAlinhadas.length !== cues.length) {
        pushToast(
          `Não foi possível alinhar tempos de tela (${janelas.length}) às cues (${cues.length}).`,
          "error",
        );
        return;
      }
      if (janelasAlinhadas.length !== janelas.length) {
        setJanelas(janelasAlinhadas);
      }
      if (janelasAlinhadas.some((j) => j.janelaProvisoria)) {
        const ok = await pedirConfirmacao({
          titulo: "Janelas provisórias",
          mensagem:
            "Há cue(s) com janela provisória (ainda não ajustada em «Origem»). Gerar o vídeo mesmo assim?",
          rotuloConfirmar: "Gerar mesmo assim",
          varianteConfirmar: "neutra",
        });
        if (!ok) return;
      }
      onGerarVideoComEstasEdicoes({
        cues: cues.map((c, i) => ({
          inicio_segundos: c.inicioSegundos,
          fim_segundos: c.fimSegundos,
          texto: c.texto,
          texto_tts: (c.textoTts || "").trim() || undefined,
          sem_narracao: Boolean(janelasAlinhadas[i]?.semNarracao),
          voz_tts: janelasAlinhadas[i]?.vozTts || vozPadraoJob || "Kore",
          forcar_regenerar_tts: Boolean(janelasAlinhadas[i]?.forcarRegenerarTts),
        })),
        janelas: janelasAlinhadas.map((j) => ({
          inicio_video_segundos: j.inicioVideoSegundos,
          fim_video_segundos: j.fimVideoSegundos,
          id_fonte_video: normalizarIdFonteVideoUiTranscribrothers(j.idFonteVideo),
        })),
        temperaturaTts: temperaturaTtsEfetiva,
        ritmoTts: ritmoTtsEfetivo,
      });
    })();
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

  const adicionarCueDepoisDoSelecionadoUi = () => {
    if (ocupado) return;
    // Destaque visual pode ser só por tempo do vídeo (entrada em 0:00), sem clique.
    const indiceBase = resolverIndiceBaseParaInserirCueDepoisDoDestaqueUiTranscribrothers({
      quantidadeCues: cues.length,
      indiceSelecionadoSolo: indiceCueSelecionadaSolo,
      indiceCueAtiva,
    });
    const videoEl = videoRef.current;
    const durEntrada =
      previewRecorteTelaAtivo && videoEl && Number.isFinite(videoEl.duration) && videoEl.duration > 0
        ? videoEl.duration
        : null;
    const r = inserirCueDepoisDoIndiceNaTimelineUiTranscribrothers({
      cues,
      janelas,
      indiceSelecionado: indiceBase,
      duracaoVideoEntradaSegundos: durEntrada,
      vozPadrao: vozPadraoJob || "Kore",
    });
    setCues(r.cues);
    setJanelas(r.janelas);
    setDuracoesWavPorIndice((prev) =>
      remaparRecordPorIndiceAposInserirUiTranscribrothers(prev, r.indiceInserido),
    );
    setPreviewAudioPorIndice((prev) =>
      remaparRecordPorIndiceAposInserirUiTranscribrothers(prev, r.indiceInserido),
    );
    setIndicesFalaTtsExpandidos((prev) =>
      remaparRecordPorIndiceAposInserirUiTranscribrothers(prev, r.indiceInserido),
    );
    setSugestoesReescritaLegendaPorIndice((prev) =>
      remaparRecordPorIndiceAposInserirUiTranscribrothers(prev, r.indiceInserido),
    );
    setIndiceCueSelecionadaSolo(r.indiceInserido);
    pushToast(
      "Cue adicionada (janela provisória). Ajuste o trecho em «Origem» e gere a prévia TTS.",
      "success",
    );
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        const ta = listaCuesRef.current?.querySelector(
          ".tb-modal-assistir-video-narrado-cue-item--ativa textarea",
        ) as HTMLTextAreaElement | null;
        ta?.focus();
      });
    });
  };

  const adicionarSeparadorSecaoDepoisDoSelecionadoUi = () => {
    if (ocupado || !jobId) return;
    void (async () => {
      const indiceBase = resolverIndiceBaseParaInserirCueDepoisDoDestaqueUiTranscribrothers({
        quantidadeCues: cues.length,
        indiceSelecionadoSolo: indiceCueSelecionadaSolo,
        indiceCueAtiva,
      });
      const videoEl = videoRef.current;
      const durEntrada =
        previewRecorteTelaAtivo &&
        videoEl &&
        Number.isFinite(videoEl.duration) &&
        videoEl.duration > 0
          ? videoEl.duration
          : null;
      const titulo = TEXTO_PADRAO_SEPARADOR_SECAO_TRANSCRIBROTHERS;
      const r = inserirSeparadorSecaoDepoisDoIndiceNaTimelineUiTranscribrothers({
        cues,
        janelas,
        indiceSelecionado: indiceBase,
        duracaoVideoEntradaSegundos: durEntrada,
        vozPadrao: vozPadraoJob || "Kore",
        tituloSecao: titulo,
      });
      setCues(r.cues);
      setJanelas(r.janelas);
      setDuracoesWavPorIndice((prev) =>
        remaparRecordPorIndiceAposInserirUiTranscribrothers(prev, r.indiceInserido),
      );
      setPreviewAudioPorIndice((prev) =>
        remaparRecordPorIndiceAposInserirUiTranscribrothers(prev, r.indiceInserido),
      );
      setIndicesFalaTtsExpandidos((prev) =>
        remaparRecordPorIndiceAposInserirUiTranscribrothers(prev, r.indiceInserido),
      );
      setSugestoesReescritaLegendaPorIndice((prev) =>
        remaparRecordPorIndiceAposInserirUiTranscribrothers(prev, r.indiceInserido),
      );
      setIndiceCueSelecionadaSolo(r.indiceInserido);

      const toastId = pushToastProgresso({
        message: "Gerando cartão de seção (vinheta)…",
        indeterminado: true,
      });
      try {
        const item = await gerarCartaoSecaoBibliotecaMidiasTelaJobApiTranscribrothers(jobId, {
          titulo,
          duracaoSegundos: DURACAO_SEPARADOR_SECAO_SEGUNDOS_TRANSCRIBROTHERS,
        });
        const durFonte =
          typeof item.duracao_segundos === "number" && item.duracao_segundos > 0
            ? item.duracao_segundos
            : DURACAO_SEPARADOR_SECAO_SEGUNDOS_TRANSCRIBROTHERS;
        setJanelas((prev) => {
          if (!prev[r.indiceInserido]) return prev;
          return prev.map((j, i) =>
            i === r.indiceInserido
              ? {
                  ...j,
                  idFonteVideo: normalizarIdFonteVideoUiTranscribrothers(item.id),
                  inicioVideoSegundos: 0,
                  fimVideoSegundos: Math.max(0.05, durFonte),
                  janelaProvisoria: false,
                  ehSeparadorSecao: true,
                  semNarracao: true,
                }
              : j,
          );
        });
        removerToast(toastId);
        pushToast(
          "Separador inserido com vinheta gerada (fade in/out). Edite o título na legenda se quiser — para outro texto no cartão, use «Fonte» ou reinseira.",
          "success",
        );
      } catch (e: unknown) {
        removerToast(toastId);
        pushToast(
          e instanceof Error
            ? `Separador criado, mas a vinheta falhou: ${e.message}. Use «Fonte» para escolher uma mídia.`
            : "Separador criado, mas a vinheta falhou. Use «Fonte» para escolher uma mídia.",
          "error",
        );
        setIndiceCueModalEscolherFonte(r.indiceInserido);
      }
    })();
  };

  const reordenarCueNaListaUi = (indiceDe: number, indicePara: number) => {
    if (ocupado || indiceDe === indicePara) return;
    const r = reordenarCuesEmpacotandoTimelineNarracaoUiTranscribrothers({
      cues,
      janelas,
      indiceDe,
      indicePara,
    });
    setCues(r.cues);
    setJanelas(r.janelas);
    setDuracoesWavPorIndice((prev) =>
      remaparRecordPorIndiceAposReordenarUiTranscribrothers(prev, indiceDe, indicePara),
    );
    setPreviewAudioPorIndice((prev) =>
      remaparRecordPorIndiceAposReordenarUiTranscribrothers(prev, indiceDe, indicePara),
    );
    setIndicesFalaTtsExpandidos((prev) =>
      remaparRecordPorIndiceAposReordenarUiTranscribrothers(prev, indiceDe, indicePara),
    );
    setSugestoesReescritaLegendaPorIndice((prev) =>
      remaparRecordPorIndiceAposReordenarUiTranscribrothers(prev, indiceDe, indicePara),
    );
    if (indiceCueSelecionadaSolo === indiceDe) {
      setIndiceCueSelecionadaSolo(indicePara);
    } else if (indiceCueSelecionadaSolo != null) {
      const ids = r.cues.map((c) => c.idCliente);
      const idSel = cues[indiceCueSelecionadaSolo]?.idCliente;
      if (idSel) {
        const novo = ids.indexOf(idSel);
        if (novo >= 0) setIndiceCueSelecionadaSolo(novo);
      }
    }
  };

  const aoIniciarArrasteCue = (e: DragStartEvent) => {
    setIdCueArrastando(String(e.active.id));
  };

  const aoSobreArrasteCue = (e: DragOverEvent) => {
    setIdCueSobre(e.over ? String(e.over.id) : null);
  };

  const aoFinalizarArrasteCue = (e: DragEndEvent) => {
    setIdCueArrastando(null);
    setIdCueSobre(null);
    const { active, over } = e;
    if (!over || active.id === over.id) return;
    const de = cues.findIndex((c) => c.idCliente === String(active.id));
    const para = cues.findIndex((c) => c.idCliente === String(over.id));
    if (de < 0 || para < 0) return;
    reordenarCueNaListaUi(de, para);
  };

  const excluirCueDaListaLocalUi = (indice: number) => {
    if (indice < 0 || indice >= cues.length) return;
    if (cues.length <= 1) {
      pushToast("É preciso manter ao menos uma cue.", "info");
      return;
    }
    void (async () => {
      const ok = await pedirConfirmacao({
        titulo: `Excluir cue ${indice + 1}?`,
        mensagem:
          "Esse trecho deixa de entrar no vídeo narrado ao gerar de novo.",
        rotuloConfirmar: "Excluir",
        varianteConfirmar: "destrutiva",
      });
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
    })();
  };

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
            <h2 id={tituloId} className="tb-modal-assistir-video-narrado-titulo">
              Editar vídeo narrado
            </h2>
            {versoesVideoNarrado.length > 0 ? (
              <label className="tb-modal-assistir-video-narrado-seletor-versao tb-modal-assistir-video-narrado-seletor-versao--compacto">
                <span className="tb-sr-only">Versão</span>
                <select
                  className="tb-modal-assistir-video-narrado-seletor-versao-select"
                  value={versaoAtualVideoNarradoId ?? ""}
                  disabled={ocupado || versoesVideoNarrado.length < 1}
                  aria-label="Versão do vídeo narrado"
                  title="Versão do vídeo narrado"
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
            <details className="tb-modal-assistir-video-narrado-config-tts">
              <summary
                className="tb-modal-assistir-video-narrado-config-tts-resumo"
                title="Modelo, temperatura e ritmo do TTS (prévia e regenerar)"
              >
                Config TTS
              </summary>
              <div
                className="tb-modal-assistir-video-narrado-config-tts-popover"
                role="group"
                aria-label="Configuração TTS"
              >
                <label className="tb-modal-assistir-video-narrado-config-tts-campo">
                  <span className="tb-modal-assistir-video-narrado-seletor-versao-rotulo">
                    Modelo
                  </span>
                  <select
                    className="tb-modal-assistir-video-narrado-seletor-versao-select"
                    value={modeloTtsUi}
                    disabled={ocupado || opcoesModeloTts.length === 0}
                    aria-label="Modelo TTS para prévia e regenerar"
                    title="Usado em «Ouvir»/«Prévia» e «Regenerar» desta página"
                    onChange={(e) => {
                      const m = e.target.value.trim();
                      if (!m) return;
                      setModeloTtsUi(m);
                      salvarModeloTtsNarracaoPreferidoNoNavegadorTranscribrothers(m);
                      onModeloTtsPreferidoAlterado?.(m);
                    }}
                  >
                    {opcoesModeloTts.length === 0 ? (
                      <option value="">Nenhum TTS na lista</option>
                    ) : (
                      opcoesModeloTts.map((m) => (
                        <option key={m} value={m}>
                          {rotuloCurtoModeloTtsParaUiTranscribrothers(m)}
                        </option>
                      ))
                    )}
                  </select>
                </label>
                <ComponenteControleSliderTemperaturaTtsNarracaoComAjudaTranscribrothers
                  variante="compacto"
                  valor={temperaturaTtsEfetiva}
                  desabilitado={ocupado}
                  onChange={(t) => {
                    setTemperaturaTtsUi(t);
                    salvarTemperaturaTtsNarracaoPreferidaNoNavegadorTranscribrothers(t);
                    onTemperaturaTtsPreferidaAlterada?.(t);
                  }}
                />
                <label className="tb-modal-assistir-video-narrado-config-tts-campo">
                  <span className="tb-modal-assistir-video-narrado-seletor-versao-rotulo">
                    Ritmo
                  </span>
                  <select
                    className="tb-modal-assistir-video-narrado-seletor-versao-select"
                    value={ritmoTtsEfetivo}
                    disabled={ocupado}
                    aria-label="Ritmo da fala para prévia e regenerar"
                    title="Ajusta o ritmo via prompt (sem atempo no áudio)."
                    onChange={(e) => {
                      const r = normalizarRitmoTtsNarracaoTranscribrothers(e.target.value);
                      setRitmoTtsUi(r);
                      salvarRitmoTtsNarracaoPreferidoNoNavegadorTranscribrothers(r);
                      onRitmoTtsPreferidoAlterado?.(r);
                    }}
                  >
                    {opcoesRitmoTts.map((op) => (
                      <option key={op.id} value={op.id} title={op.descricao}>
                        {op.rotulo}
                      </option>
                    ))}
                  </select>
                </label>
              </div>
            </details>
          </div>
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
                  timelineVirtualUi={{
                    tempoAtualSegundos,
                    duracaoSegundos: duracaoTimelineNarradaParaBarraUi,
                    aoAlterarTempoPelaBarra: previewRecorteTelaAtivo
                      ? aoAlterarTempoPelaBarraDurantePreviewRecorteUi
                      : aoAlterarTempoPelaBarraForaDoPreviewRecorteUi,
                  }}
                  overlaySobreVideo={
                    textoLegendaOverlayNoVideo ? (
                      <p
                        className="tb-modal-assistir-video-narrado-legenda-overlay-preview"
                        role="status"
                        aria-live="polite"
                      >
                        {textoLegendaOverlayNoVideo}
                      </p>
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
              <button
                type="button"
                className="tb-modal-assistir-video-narrado-adicionar-cue"
                disabled={ocupado || !urlLegendasVtt || carregandoCues || Boolean(erroCues)}
                title="Insere uma cue depois do cartão destacado (seleção ou instante do vídeo)"
                onClick={() => adicionarCueDepoisDoSelecionadoUi()}
              >
                Adicionar cue
              </button>
              <button
                type="button"
                className="tb-modal-assistir-video-narrado-adicionar-cue tb-modal-assistir-video-narrado-adicionar-separador"
                disabled={ocupado || !urlLegendasVtt || carregandoCues || Boolean(erroCues)}
                title="Insere intercalário com cartão de seção gerado (título + fade) e sem narração"
                onClick={() => adicionarSeparadorSecaoDepoisDoSelecionadoUi()}
              >
                Inserir separador
              </button>
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
                    «Ajustar ao áudio» alinha a duração da cue à fala (encolhe ou estica; ao
                    esticar, empurra as cues seguintes). Use após Prévia/Regenerar quando o áudio
                    for maior que o slot — senão o vídeo gerado corta a narração.
                  </p>
                  <p>
                    «Ajustar à tela» alinha a duração da cue à janela do vídeo original (encolhe ou
                    estica; ao esticar, empurra as cues seguintes).
                  </p>
                  <p>
                    «← →» ou arraste na faixa sob o progresso deslocam a cue sem sobrepor.
                  </p>
                  <p>
                    «Ouvir»/«Prévia» gera o áudio TTS; se o badge «prévia ok» aparecer, esse áudio
                    será reaproveitado ao gerar o vídeo (sem narrar de novo).
                  </p>
                  <p>
                    «Adicionar cue» insere depois do cartão destacado (clique ou cue do instante
                    atual do vídeo; janela provisória). «Inserir separador» gera um cartão de seção
                    (vinheta com título e fade) e coloca na timeline. Arraste pelo handle ou use as
                    setas para reordenar (estilo Trello).
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
              <div className="tb-modal-assistir-video-narrado-cues-vazia">
                <p className="tb-modal-assistir-video-narrado-aviso">
                  Nenhuma cue na lista. Use «Adicionar cue» para criar a primeira.
                </p>
              </div>
            ) : (
              <DndContext
                sensors={sensorsOrdenacaoCues}
                collisionDetection={closestCenter}
                onDragStart={aoIniciarArrasteCue}
                onDragOver={aoSobreArrasteCue}
                onDragEnd={aoFinalizarArrasteCue}
                onDragCancel={() => {
                  setIdCueArrastando(null);
                  setIdCueSobre(null);
                }}
              >
                <SortableContext
                  items={cues.map((c) => c.idCliente)}
                  strategy={verticalListSortingStrategy}
                >
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
                  const duracaoJanelaTela = janela
                    ? Math.max(0, janela.fimVideoSegundos - janela.inicioVideoSegundos)
                    : 0;
                  const podeAjustarAoAudio = cuePodeAjustarFimAoAudioNaTimelineUiTranscribrothers(
                    duracaoCueSlot,
                    duracaoAudioAjuste,
                  );
                  const podeAjustarATela = cuePodeAjustarFimAJanelaTelaNaTimelineUiTranscribrothers(
                    duracaoCueSlot,
                    duracaoJanelaTela > 0 ? duracaoJanelaTela : null,
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
                  const janelaProvisoria = Boolean(janela?.janelaProvisoria);
                  const mostrarGapAntes =
                    Boolean(idCueArrastando) &&
                    idCueSobre === cue.idCliente &&
                    idCueArrastando !== cue.idCliente;
                  return (
                    <CartaoCueSortableListaVideoNarradoTranscribrothers
                      key={cue.idCliente}
                      id={cue.idCliente}
                      desabilitado={ocupado}
                      mostrarGapAntes={mostrarGapAntes}
                      ariaCurrent={ativa ? "true" : undefined}
                      onClickLista={() => selecionarCueNaListaSemAlterarPlaybackUi(i)}
                      liRef={ativa ? (el) => { cueAtivaRef.current = el; } : undefined}
                      className={
                        "tb-modal-assistir-video-narrado-cue-item" +
                        (ativa ? " tb-modal-assistir-video-narrado-cue-item--ativa" : "") +
                        (semNarracao ? " tb-modal-assistir-video-narrado-cue-item--sem-narracao" : "") +
                        (janelaProvisoria
                          ? " tb-modal-assistir-video-narrado-cue-item--janela-provisoria"
                          : "")
                      }
                    >
                      {(handleArraste) => (
                      <>
                      <div className="tb-modal-assistir-video-narrado-cue-cabecalho">
                        <button
                          type="button"
                          ref={handleArraste.setActivatorNodeRef}
                          className="tb-modal-assistir-video-narrado-cue-drag"
                          aria-label={`Arrastar cue ${i + 1}`}
                          title="Arrastar para reordenar"
                          disabled={ocupado}
                          onClick={(e) => e.stopPropagation()}
                          {...handleArraste.attributes}
                          {...handleArraste.listeners}
                        >
                          <span aria-hidden="true">⋮⋮</span>
                        </button>
                        <span
                          className="tb-modal-assistir-video-narrado-cue-numero"
                          title={`Cue ${i + 1} de ${cues.length}`}
                        >
                          #{i + 1}
                        </span>
                        <button
                          type="button"
                          className="tb-modal-assistir-video-narrado-cue-nudge"
                          disabled={ocupado || i === 0}
                          title="Mover cue para cima"
                          aria-label={`Mover cue ${i + 1} para cima`}
                          onClick={(e) => {
                            e.stopPropagation();
                            reordenarCueNaListaUi(i, i - 1);
                          }}
                        >
                          ↑
                        </button>
                        <button
                          type="button"
                          className="tb-modal-assistir-video-narrado-cue-nudge"
                          disabled={ocupado || i >= cues.length - 1}
                          title="Mover cue para baixo"
                          aria-label={`Mover cue ${i + 1} para baixo`}
                          onClick={(e) => {
                            e.stopPropagation();
                            reordenarCueNaListaUi(i, i + 1);
                          }}
                        >
                          ↓
                        </button>
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
                        {podeAjustarATela ? (
                          <span
                            className="tb-modal-assistir-video-narrado-cue-duracao-tela"
                            title="Duração da janela de tela no vídeo original (difere do slot narrado)"
                          >
                            tela{" "}
                            {formatarDuracaoSegundosCurtaPortuguesUiTranscribrothers(
                              duracaoJanelaTela,
                            ) || "—"}
                          </span>
                        ) : null}
                        {janelaProvisoria ? (
                          <span
                            className="tb-modal-assistir-video-narrado-cue-badge-janela-provisoria"
                            title="Trecho de tela provisório — ajuste em «Origem»"
                          >
                            janela provisória
                          </span>
                        ) : null}
                        {janela?.ehSeparadorSecao ? (
                          <span
                            className="tb-modal-assistir-video-narrado-cue-badge-separador-secao"
                            title="Intercalário entre funcionalidades — escolha a vinheta em «Fonte»"
                          >
                            separador
                          </span>
                        ) : null}
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
                          disabled={!jobId || !janela || ocupado}
                          title={
                            !janela
                              ? "Janela de tela ainda não disponível para esta cue"
                              : "Trocar a origem (vídeo de tela) desta cue"
                          }
                          onClick={(e) => {
                            e.stopPropagation();
                            setIndiceCueSelecionadaSolo(i);
                            setIndiceCueModalEscolherFonte(i);
                          }}
                        >
                          Fonte
                        </button>
                        <button
                          type="button"
                          className="tb-modal-assistir-video-narrado-cue-original"
                          disabled={
                            !jobId ||
                            (!jobTemVideoEntrada &&
                              normalizarIdFonteVideoUiTranscribrothers(janela?.idFonteVideo) ===
                                ID_FONTE_VIDEO_ENTRADA_UI_TRANSCRIBROTHERS) ||
                            !janela ||
                            ocupado
                          }
                          title={
                            !janela
                              ? "Janela de tela ainda não disponível para esta cue"
                              : "Recortar trecho na origem desta cue (só cues com o mesmo vídeo)"
                          }
                          onClick={(e) => {
                            e.stopPropagation();
                            setIndiceCueSelecionadaSolo(i);
                            setIndiceCueModalVideoOriginal(i);
                          }}
                        >
                          Origem
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
                            title="Alinhar o fim da cue à duração do áudio atual (encolhe ou estica; ao esticar, empurra as seguintes)"
                            onClick={() => ajustarCueAoAudioAtual(i)}
                          >
                            Ajustar ao áudio
                          </button>
                        ) : null}
                        {podeAjustarATela ? (
                          <button
                            type="button"
                            className="tb-modal-assistir-video-narrado-cue-ajustar-audio"
                            disabled={ocupado}
                            title="Alinhar a duração da cue à janela de tela do vídeo original (ao esticar, empurra as seguintes)"
                            onClick={() => ajustarCueAJanelaTelaAtual(i)}
                          >
                            Ajustar à tela
                          </button>
                        ) : null}
                      </div>
                      <div className="tb-modal-assistir-video-narrado-cue-textos">
                        <div className="tb-modal-assistir-video-narrado-cue-texto-campo">
                          <div className="tb-modal-assistir-video-narrado-cue-texto-rotulo-linha">
                            <span className="tb-modal-assistir-video-narrado-cue-texto-rotulo">
                              Legenda
                            </span>
                            {!semNarracao ? (
                              <button
                                type="button"
                                className="tb-modal-assistir-video-narrado-cue-sugestao-ia"
                                disabled={
                                  ocupado || indicesSugerindoReescritaLegenda.has(i)
                                }
                                title="Sugerir reescrita da legenda (IA)"
                                aria-label={`Sugerir reescrita da legenda ${i + 1}`}
                                onClick={() => void sugerirReescritaLegendaCueUi(i)}
                              >
                                {indicesSugerindoReescritaLegenda.has(i) ? (
                                  "…"
                                ) : (
                                  <svg
                                    width="15"
                                    height="15"
                                    viewBox="0 0 16 16"
                                    fill="none"
                                    xmlns="http://www.w3.org/2000/svg"
                                    aria-hidden="true"
                                  >
                                    <path
                                      d="M8 1.5l.9 3.2L12 5.6l-3.1 1-.9 3.2-.9-3.2L4 5.6l3.1-.9L8 1.5z"
                                      stroke="currentColor"
                                      strokeWidth="1.2"
                                      strokeLinejoin="round"
                                    />
                                    <path
                                      d="M12.5 9.5l.45 1.6 1.55.45-1.55.45-.45 1.6-.45-1.6-1.55-.45 1.55-.45.45-1.6z"
                                      fill="currentColor"
                                    />
                                  </svg>
                                )}
                              </button>
                            ) : null}
                          </div>
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
                        </div>
                        <ComponentePainelSugestaoReescritaTextoCueIaUsarOuDescartarTranscribrothers
                          sugestao={sugestoesReescritaLegendaPorIndice[i] || ""}
                          desabilitado={ocupado}
                          onUsar={() => {
                            const s = sugestoesReescritaLegendaPorIndice[i];
                            if (!s) return;
                            atualizarTextoCue(i, s);
                            setSugestoesReescritaLegendaPorIndice((prev) => {
                              const next = { ...prev };
                              delete next[i];
                              return next;
                            });
                            pushToast(`Sugestão aplicada na legenda ${i + 1}.`, "success");
                          }}
                          onDescartar={() =>
                            setSugestoesReescritaLegendaPorIndice((prev) => {
                              const next = { ...prev };
                              delete next[i];
                              return next;
                            })
                          }
                        />
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
                      </>
                      )}
                    </CartaoCueSortableListaVideoNarradoTranscribrothers>
                  );
                })}
                  </ul>
                </SortableContext>
                <DragOverlay dropAnimation={null}>
                  {idCueArrastando ? (
                    <div className="tb-modal-assistir-video-narrado-cue-drag-overlay">
                      {(() => {
                        const idx = cues.findIndex((c) => c.idCliente === idCueArrastando);
                        if (idx < 0) return "Movendo cue…";
                        const c = cues[idx];
                        return (
                          <>
                            <strong>#{idx + 1}</strong>{" "}
                            {formatarSegundosComoTimestampVttCurtoUiTranscribrothers(c.inicioSegundos)}
                            {" – "}
                            {(c.texto || "").slice(0, 48)}
                            {(c.texto || "").length > 48 ? "…" : ""}
                          </>
                        );
                      })()}
                    </div>
                  ) : null}
                </DragOverlay>
              </DndContext>
            )}
          </div>
        </div>

        {jobId && painelDebugCacheAberto ? (
          <ComponentePainelDebugCacheSegmentosVideoNarradoModalTranscribrothers
            jobId={jobId}
            aberto={painelDebugCacheAberto}
            onFechar={() => setPainelDebugCacheAberto(false)}
          />
        ) : null}

        <footer className="tb-modal-assistir-video-narrado-rodape">
          <div className="tb-modal-assistir-video-narrado-rodape-grupos">
            {jobId ? (
              <button
                type="button"
                className={
                  painelDebugCacheAberto
                    ? "tb-modal-assistir-video-narrado-btn-debug tb-modal-assistir-video-narrado-btn-debug--ativo"
                    : "tb-modal-assistir-video-narrado-btn-debug"
                }
                aria-pressed={painelDebugCacheAberto}
                aria-label={
                  painelDebugCacheAberto
                    ? "Esconder painel de debug"
                    : "Mostrar painel de debug"
                }
                title="Mostrar ou esconder informações de debug (cache de segmentos)"
                onClick={() => setPainelDebugCacheAberto((v) => !v)}
              >
                debug
              </button>
            ) : null}
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
            <button
              type="button"
              className={
                "tb-linkbtn tb-modal-assistir-video-narrado-btn-salvar-projeto" +
                (projetoSujo ? " tb-modal-assistir-video-narrado-btn-salvar-projeto--sujo" : "")
              }
              disabled={!podeSalvarProjeto}
              title={
                projetoSujo
                  ? "Grava legendas e tempos de tela no projeto (sem gerar o MP4)."
                  : "Nenhuma alteração para salvar."
              }
              onClick={() => salvarProjetoEditorUi()}
            >
              {salvandoProjeto ? "Salvando…" : "Salvar projeto"}
              {projetoSujo && !ocupado ? (
                <span
                  className="tb-modal-video-narrado-menu-acoes-badge"
                  aria-hidden="true"
                />
              ) : null}
            </button>
            <ComponenteMenuAcoesDropdownRodapeModalVideoNarradoTranscribrothers
              idMenu="mais"
              rotulo="Mais"
              ariaLabel="Outras ações do vídeo narrado"
              desabilitado={ocupado}
              menuAbertoId={menuRodapeAbertoId}
              onMenuAbertoIdChange={setMenuRodapeAbertoId}
              itens={[
                {
                  id: "gerar-nova",
                  rotulo: "Gerar nova narração",
                  desabilitado: ocupado,
                  titulo:
                    "Parte do Markdown com preparação IA das legendas e gera TTS de todas as cues (não reusa este VTT).",
                  onClick: onGerarNovaNarracao,
                },
                {
                  id: "remux-tempos",
                  rotulo: "Remontar MP4 (só tempos)",
                  desabilitado: ocupado || !jobId || janelas.length === 0 || projetoSujo,
                  titulo: projetoSujo
                    ? "Salve o projeto antes de remontar só com os tempos."
                    : "Remonta o MP4 reutilizando o áudio TTS (sem regenerar fala).",
                  onClick: onAplicarTemposJanelasAoVideo,
                },
                {
                  id: "atualizar-narracao",
                  rotulo: "Atualizar narração (TTS parcial)",
                  desabilitado: ocupado || !jobId || !urlLegendasVtt || projetoSujo,
                  titulo: projetoSujo
                    ? "Salve o projeto antes de atualizar a narração."
                    : "Regenera TTS só nas cues cujo texto mudou e remonta o MP4.",
                  onClick: onAtualizarNarracaoDasLegendas,
                },
              ]}
            />
          </div>
          <div className="tb-modal-assistir-video-narrado-rodape-direita">
            <button
              type="button"
              className="tb-primary tb-modal-assistir-video-narrado-cta-principal"
              disabled={!podeGerarVideoComEstasEdicoes}
              title="Salva as edições e gera um MP4 só com os trechos que têm cue (sem gaps), como no play do modal."
              onClick={dispararGerarVideoComEstasEdicoes}
            >
              {regenerando ? "Gerando…" : "Gerar vídeo com estas edições"}
            </button>
            <button
              type="button"
              className="tb-linkbtn"
              disabled={ocupado}
              title="Voltar ao tutorial"
              onClick={onFechar}
            >
              Voltar
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
        urlsAudioNarracaoPorIndice={urlsAudioNarracaoParaModalOriginal}
        urlVideoSrc={urlVideoFonteTelaCueParaPreviewUiTranscribrothers(
          jobId,
          janelas[indiceCueModalVideoOriginal]?.idFonteVideo,
        )}
        tituloModal={`Origem — cue #${indiceCueModalVideoOriginal + 1}`}
        onFechar={() => setIndiceCueModalVideoOriginal(null)}
        onAplicarJanelas={(janelasNovas) => {
          const indiceAplicado = indiceCueModalVideoOriginal;
          const avisoSobreposicao = avisarSobreposicaoSomenteCuesAlteradasUiTranscribrothers(
            janelas,
            janelasNovas,
          );
          setJanelas(
            janelasNovas.map((j, i) => ({
              ...j,
              janelaProvisoria:
                i === indiceAplicado ? false : Boolean(janelas[i]?.janelaProvisoria),
            })),
          );
          // Se a duração da janela mudou, alinha o slot da timeline (preview = MP4 gerado).
          setCues((prev) => {
            let next = prev;
            let alinhouAlguma = false;
            for (let i = 0; i < janelasNovas.length; i++) {
              const ant = janelas[i];
              const nov = janelasNovas[i];
              if (!ant || !nov || !next[i]) continue;
              const durAnt = Math.max(0, ant.fimVideoSegundos - ant.inicioVideoSegundos);
              const durNov = Math.max(0, nov.fimVideoSegundos - nov.inicioVideoSegundos);
              if (Math.abs(durNov - durAnt) < 0.15) continue;
              const r = ajustarFimCueTimelineAJanelaTelaUiTranscribrothers(next, i, durNov);
              if (r.ok) {
                next = r.cues;
                alinhouAlguma = true;
              }
            }
            if (!alinhouAlguma) return prev;
            return garantirIdsClienteNasCuesTimelineNarracaoUiTranscribrothers(
              next.map((c, i) => ({ ...c, idCliente: prev[i]?.idCliente ?? c.idCliente })),
            );
          });
          if (avisoSobreposicao) {
            pushToast(
              `${avisoSobreposicao} Janela aplicada mesmo assim. Ao salvar/remux o backend ainda pode recusar.`,
              "info",
            );
            return { ok: true as const, aviso: avisoSobreposicao };
          }
          pushToast(
            "Recortes de tela no editor. Se a duração da origem mudou, o slot da cue foi alinhado à tela.",
            "info",
          );
          return { ok: true as const };
        }}
      />
    ) : null}
    {jobId && indiceCueModalEscolherFonte !== null && janelas[indiceCueModalEscolherFonte] ? (
      <ComponenteModalEscolherFonteMidiaTelaCueBibliotecaTranscribrothers
        aberto
        jobId={jobId}
        idFonteAtual={janelas[indiceCueModalEscolherFonte]?.idFonteVideo}
        onFechar={() => setIndiceCueModalEscolherFonte(null)}
        onEscolherFonte={(idFonte, _rotulo, opcoes) => {
          const indice = indiceCueModalEscolherFonte;
          const atual = janelas[indice];
          if (!atual) {
            setIndiceCueModalEscolherFonte(null);
            return;
          }
          const cue = cues[indice];
          const durCue = cue
            ? Math.max(0.05, cue.fimSegundos - cue.inicioSegundos)
            : 0.05;
          const recalc = calcularJanelaVideoAposTrocaFonteMidiaTelaUiTranscribrothers({
            idFonteAnterior: atual.idFonteVideo,
            idFonteNova: idFonte,
            inicioVideoSegundos: atual.inicioVideoSegundos,
            fimVideoSegundos: atual.fimVideoSegundos,
            duracaoCueTimelineSegundos: durCue,
            duracaoFonteNovaSegundos: opcoes?.duracaoSegundos,
          });
          const idNorm = normalizarIdFonteVideoUiTranscribrothers(idFonte);
          setJanelas((prev) => {
            if (!prev[indice]) return prev;
            if (!recalc.mudouFonte) {
              return prev.map((j, i) =>
                i === indice ? { ...j, idFonteVideo: idNorm } : j,
              );
            }
            return prev.map((j, i) =>
              i === indice
                ? {
                    ...j,
                    idFonteVideo: idNorm,
                    inicioVideoSegundos: recalc.inicioVideoSegundos,
                    fimVideoSegundos: recalc.fimVideoSegundos,
                    janelaProvisoria: true,
                  }
                : j,
            );
          });
          if (recalc.mudouFonte) {
            const durNova = Math.max(
              0.05,
              recalc.fimVideoSegundos - recalc.inicioVideoSegundos,
            );
            setCues((prev) => {
              if (!prev[indice]) return prev;
              const durAnt = Math.max(
                0,
                prev[indice].fimSegundos - prev[indice].inicioSegundos,
              );
              if (Math.abs(durNova - durAnt) < 0.15) return prev;
              const r = ajustarFimCueTimelineAJanelaTelaUiTranscribrothers(
                prev,
                indice,
                durNova,
              );
              if (!r.ok) return prev;
              return garantirIdsClienteNasCuesTimelineNarracaoUiTranscribrothers(
                r.cues.map((c, i) => ({
                  ...c,
                  idCliente: prev[i]?.idCliente ?? c.idCliente,
                })),
              );
            });
          }
          setIndiceCueModalEscolherFonte(null);
          setIndiceCueModalVideoOriginal(indice);
        }}
      />
    ) : null}
    {elementoDialogoConfirmacao}
    </>
  );
}
