import type * as React from "react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { fabric } from "fabric";
import {
  derivarNomeArquivoPngAnotadoLocalTranscribrothers,
  gravarPngAnotadoScreenshotTutorialJobApiTranscribrothers,
  type RegistroAnotacaoImagemTutorialApiTranscribrothers,
} from "./modulo_api_anotacao_imagens_tutorial_assets_png_duas_versoes_transcribrothers.ts";
import { ComponenteSeletorCorAnotacaoPaletaPredefinidaEColorPickerTranscribrothers } from "./componente_seletor_cor_anotacao_paleta_predefinida_e_color_picker_transcribrothers.tsx";
import type { JobStatus } from "./tipos_job_status_api_transcribrothers.ts";
import { urlAssetPngJobParaNomeArquivoTranscribrothers } from "./modulo_util_resolver_nome_asset_png_para_exibicao_com_metadados_anotacao_tutorial_transcribrothers.ts";
import { usarDialogoConfirmacaoAcaoUiSubstituindoWindowConfirmTranscribrothers } from "./hook_usar_dialogo_confirmacao_acao_ui_substituindo_window_confirm_transcribrothers.tsx";
import {
  COR_PADRAO_FERRAMENTAS_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS,
  ESPESSURA_TRACO_PADRAO_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS,
  PROPRIEDADE_FABRIC_TIPO_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS,
  VALOR_TIPO_ANOTACAO_DESTAQUE_SEMITRANSPARENTE_TRANSCRIBROTHERS,
  obterEstiloContornoFormaVazadaAnotacaoImagemTutorialTranscribrothers,
  obterEstiloRetanguloDestaqueSemitransparenteSemBordaAnotacaoImagemTutorialTranscribrothers,
} from "./modulo_util_estilos_formas_anotacao_imagem_tutorial_fabric_js_transcribrothers.ts";
import {
  IconeAjustarAreaVisualizacaoCanvasAnotacaoImagemTutorialTranscribrothers,
  IconeCopiarImagemEditadaAnotacaoTutorialTranscribrothers,
  IconeExcluirSelecaoAnotacaoImagemTutorialTranscribrothers,
  IconeFerramentaAnotacaoImagemTutorialTranscribrothers,
  IconeInserirImagemNoDocumentoAnotacaoTutorialTranscribrothers,
  obterRotuloAcessivelFerramentaAnotacaoImagemTutorialTranscribrothers,
} from "./componente_icones_ferramentas_anotacao_imagem_tutorial_transcribrothers.tsx";
import {
  aplicarModoZoomVisualizacaoCanvasFabricAnotacaoImagemTutorialTranscribrothers,
  exportarCanvasFabricAnotacaoComoPngDataUrlTranscribrothers,
  obterCoordenadasCanvasFabricAPartirDeEventoPonteiroAnotacaoImagemTutorialTranscribrothers,
} from "./modulo_util_zoom_visualizacao_canvas_fabric_anotacao_imagem_tutorial_transcribrothers.ts";
import { calcularRetanguloRecorteNormalizadoCanvasAnotacaoImagemTutorialTranscribrothers } from "./modulo_util_calcular_retangulo_recorte_normalizado_canvas_anotacao_imagem_tutorial_transcribrothers.ts";
import {
  converterDataUrlPngParaBlobTranscribrothers,
  copiarBlobImagemPngParaAreaTransferenciaNavegadorTranscribrothers,
} from "./modulo_util_copiar_blob_imagem_png_para_area_transferencia_navegador_transcribrothers.ts";
import { usarToastFeedbackAcoesUiTranscribrothers } from "./provedor_contexto_e_hook_uso_toasts_feedback_acoes_ui_transcribrothers.tsx";
import type {
  FerramentaAnotacaoImagemTutorialTranscribrothers,
  ModoZoomVisualizacaoCanvasAnotacaoImagemTutorialTranscribrothers,
} from "./tipos_ferramenta_anotacao_imagem_tutorial_transcribrothers.ts";
import { resolverNomeArquivoESePrecisaPersistirAnotacaoParaInserirNoDocumentoTranscribrothers } from "./modulo_util_resolver_nome_arquivo_e_persistencia_anotacao_para_inserir_no_documento_tutorial_transcribrothers.ts";
import {
  ROTULO_BOTAO_COMMIT_USAR_NO_TUTORIAL_MODAL_ANOTACAO_TRANSCRIBROTHERS,
  ROTULO_BOTAO_COMMIT_USAR_NO_TUTORIAL_PROCESSANDO_MODAL_ANOTACAO_TRANSCRIBROTHERS,
  resolverAcaoCommitUsarNoTutorialModalAnotacaoTranscribrothers,
} from "./modulo_util_resolver_acao_commit_usar_no_tutorial_modal_anotacao_screenshot_transcribrothers.ts";
import {
  descartarPrevisualizacaoFramesNavegacaoVideoTutorialJobApiTranscribrothers,
  previsualizarFramesNavegacaoVideoTutorialJobApiTranscribrothers,
  promoverFramePrevisualizacaoParaAssetsVideoTutorialJobApiTranscribrothers,
} from "./modulo_api_previsualizar_promover_e_descartar_frames_navegacao_video_tutorial_transcribrothers.ts";
import { instanteAposPassoNavegacaoFrameVideoTutorialTranscribrothers } from "./modulo_util_passo_navegacao_instante_frame_video_tutorial_transcribrothers.ts";
import {
  chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers,
  devePedirConfirmacaoAnotacaoAoNavegarSetaFrameTutorialTranscribrothers,
  devePedirConfirmacaoAnotacaoAoUsarEsteFrameTutorialTranscribrothers,
  instanteEhSlotDocumentoFrameNavegacaoTutorialTranscribrothers,
  montarInstantesPrefetchJanelaNavegacaoFrameTutorialTranscribrothers,
  nomesArquivoPreviewParaDescartarNavegacaoFrameTutorialTranscribrothers,
  resolverNomeArquivoCandidatoPreviewFrameVisivelParaCommitTutorialTranscribrothers,
  type ItemCachePreviewFrameNavegacaoTutorialTranscribrothers,
} from "./modulo_util_cache_previsualizacao_frames_video_navegacao_modal_anotacao_tutorial_transcribrothers.ts";
import {
  montarTrilhaPassosNavegacaoFrameAncoradaNoDocumentoTutorialTranscribrothers,
  rotuloAcessivelTracoTrilhaNavegacaoFrameTutorialTranscribrothers,
} from "./modulo_util_trilha_passos_navegacao_frame_video_ancorada_no_documento_tutorial_transcribrothers.ts";
import {
  formatarSegundosParaRotuloMmSsMarkdownTutorialTranscribrothers,
  navegacaoFrameVideoDeveAparecerNaModalAnotacaoTutorialTranscribrothers,
  usarEsteFrameNoDocumentoDeveFicarHabilitadoTranscribrothers,
} from "./modulo_util_substituir_referencia_imagem_asset_e_link_temporal_markdown_tutorial_transcribrothers.ts";
import "./estilos_css_modal_editor_anotacao_imagem_tutorial_fabric_js_transcribrothers.css";

type ArrastoFormaAnotacaoTranscribrothers =
  | { tipo: "seta"; x1: number; y1: number; preview?: fabric.Line }
  | { tipo: "linha"; x1: number; y1: number; preview?: fabric.Line }
  | { tipo: "destaque"; x1: number; y1: number; preview?: fabric.Rect }
  | { tipo: "retangulo"; x1: number; y1: number; preview?: fabric.Rect }
  | { tipo: "elipse"; x1: number; y1: number; preview?: fabric.Ellipse }
  | { tipo: "recortar"; x1: number; y1: number; preview?: fabric.Rect };

const TAMANHO_MINIMO_FORMA_ARRASTE_PX_TRANSCRIBROTHERS = 6;

type VersaoImagemExibidaNoEditorAnotacaoModalTranscribrothers = "original" | "anotado";

function resolverVersaoImagemInicialNoEditorAnotacaoModalTranscribrothers(
  registro?: RegistroAnotacaoImagemTutorialApiTranscribrothers,
): VersaoImagemExibidaNoEditorAnotacaoModalTranscribrothers {
  if (registro?.tem_arquivo_anotado && registro.exibir_no_tutorial === "anotado") {
    return "anotado";
  }
  return "original";
}

type PropsModalEditorAnotacaoImagemTutorialTranscribrothers = {
  jobId: string;
  nomeArquivoOriginal: string;
  registroAnotacao?: RegistroAnotacaoImagemTutorialApiTranscribrothers;
  aoFechar: () => void;
  aoSalvarComSucesso: (job: JobStatus, origem?: "salvar_manual" | "inserir_documento" | "usar_no_tutorial") => void;
  aoAlternarVersaoExibicaoNoTutorial?: (
    nomeArquivoOriginal: string,
    versao: "original" | "anotado",
    opcoes?: { silencioso?: boolean },
  ) => void | Promise<void>;
  aoRemoverAnotacaoSalva?: (nomeArquivoOriginal: string) => void | Promise<void>;
  aoSincronizarMarkdownComVersaoAnotada?: (
    nomeArquivoOriginal: string,
    opcoes?: { silencioso?: boolean },
  ) => void | Promise<void>;
  processandoGestaoVersoes?: boolean;
  aoSolicitarInserirImagemNoDocumentoMarkdown?: (nomeArquivoParaSnippet: string) => void | Promise<void>;
  temVideoEntrada?: boolean;
  instanteSegundosInicial?: number | null;
  duracaoVideoSegundos?: number;
  aoAtualizarJobAposCapturaFramePreview?: (job: JobStatus) => void;
  aoUsarFrameCapturadoNoDocumentoMarkdown?: (args: {
    nomeArquivoAnterior: string;
    nomeArquivoNovo: string;
    instanteSegundos: number;
  }) => void | Promise<void>;
};

function marcarObjetoComoDestaqueSemitransparenteTranscribrothers(obj: fabric.Object): void {
  obj.set(
    PROPRIEDADE_FABRIC_TIPO_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS,
    VALOR_TIPO_ANOTACAO_DESTAQUE_SEMITRANSPARENTE_TRANSCRIBROTHERS,
  );
}

function criarRetanguloDestaqueSemitransparenteAnotacaoTranscribrothers(
  x1: number,
  y1: number,
  x2: number,
  y2: number,
): fabric.Rect | null {
  const left = Math.min(x1, x2);
  const top = Math.min(y1, y2);
  const width = Math.abs(x2 - x1);
  const height = Math.abs(y2 - y1);
  if (width < TAMANHO_MINIMO_FORMA_ARRASTE_PX_TRANSCRIBROTHERS || height < TAMANHO_MINIMO_FORMA_ARRASTE_PX_TRANSCRIBROTHERS) {
    return null;
  }
  const rect = new fabric.Rect({
    left,
    top,
    width,
    height,
    ...obterEstiloRetanguloDestaqueSemitransparenteSemBordaAnotacaoImagemTutorialTranscribrothers(),
  });
  marcarObjetoComoDestaqueSemitransparenteTranscribrothers(rect);
  return rect;
}

function criarRetanguloVazadoAnotacaoTranscribrothers(
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  cor: string,
): fabric.Rect | null {
  const left = Math.min(x1, x2);
  const top = Math.min(y1, y2);
  const width = Math.abs(x2 - x1);
  const height = Math.abs(y2 - y1);
  if (width < TAMANHO_MINIMO_FORMA_ARRASTE_PX_TRANSCRIBROTHERS || height < TAMANHO_MINIMO_FORMA_ARRASTE_PX_TRANSCRIBROTHERS) {
    return null;
  }
  return new fabric.Rect({
    left,
    top,
    width,
    height,
    ...obterEstiloContornoFormaVazadaAnotacaoImagemTutorialTranscribrothers(cor),
  });
}

function obterEstiloRetanguloPreviewRecorteAnotacaoImagemTutorialTranscribrothers(): fabric.IRectOptions {
  return {
    fill: "rgba(15, 23, 42, 0.12)",
    stroke: "#0f172a",
    strokeWidth: 1,
    strokeDashArray: [6, 4],
    opacity: 1,
  };
}

function criarElipseVazadaAnotacaoTranscribrothers(
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  cor: string,
): fabric.Ellipse | null {
  const left = Math.min(x1, x2);
  const top = Math.min(y1, y2);
  const width = Math.abs(x2 - x1);
  const height = Math.abs(y2 - y1);
  if (width < TAMANHO_MINIMO_FORMA_ARRASTE_PX_TRANSCRIBROTHERS || height < TAMANHO_MINIMO_FORMA_ARRASTE_PX_TRANSCRIBROTHERS) {
    return null;
  }
  return new fabric.Ellipse({
    left: left + width / 2,
    top: top + height / 2,
    originX: "center",
    originY: "center",
    rx: width / 2,
    ry: height / 2,
    ...obterEstiloContornoFormaVazadaAnotacaoImagemTutorialTranscribrothers(cor),
  });
}

function criarGrupoSetaAnotacaoTranscribrothers(
  x1: number,
  y1: number,
  x2: number,
  y2: number,
  cor: string,
): fabric.Group | null {
  const dist = Math.hypot(x2 - x1, y2 - y1);
  if (dist < TAMANHO_MINIMO_FORMA_ARRASTE_PX_TRANSCRIBROTHERS) return null;
  const angulo = (Math.atan2(y2 - y1, x2 - x1) * 180) / Math.PI;
  const linha = new fabric.Line([x1, y1, x2, y2], {
    stroke: cor,
    strokeWidth: ESPESSURA_TRACO_PADRAO_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS,
  });
  const ponta = new fabric.Triangle({
    left: x2,
    top: y2,
    width: 14,
    height: 18,
    fill: cor,
    stroke: cor,
    strokeWidth: 0,
    originX: "center",
    originY: "center",
    angle: angulo + 90,
  });
  return new fabric.Group([linha, ponta], {});
}

function aplicarCorAoObjetoFabricSelecionadoTranscribrothers(obj: fabric.Object, cor: string): void {
  if (obj.type === "i-text" || obj.type === "text") {
    obj.set("fill", cor);
    return;
  }
  const tipoAnotacao = obj.get(PROPRIEDADE_FABRIC_TIPO_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS) as
    | string
    | undefined;
  if (tipoAnotacao === VALOR_TIPO_ANOTACAO_DESTAQUE_SEMITRANSPARENTE_TRANSCRIBROTHERS) {
    return;
  }
  if (obj.type === "group") {
    (obj as fabric.Group).forEachObject((filho) => {
      if (filho.type === "line") {
        filho.set("stroke", cor);
      } else if (filho.type === "triangle") {
        filho.set({ fill: cor, stroke: cor });
      }
    });
    return;
  }
  obj.set("stroke", cor);
  if (obj.type === "rect" || obj.type === "ellipse") {
    obj.set("fill", "transparent");
  }
}

export function ComponenteModalEditorAnotacaoImagemTutorialFabricJsDuasVersoesTranscribrothers({
  jobId,
  nomeArquivoOriginal,
  registroAnotacao,
  aoFechar,
  aoSalvarComSucesso,
  aoAlternarVersaoExibicaoNoTutorial,
  aoRemoverAnotacaoSalva,
  aoSincronizarMarkdownComVersaoAnotada,
  processandoGestaoVersoes = false,
  aoSolicitarInserirImagemNoDocumentoMarkdown,
  temVideoEntrada = false,
  instanteSegundosInicial = null,
  duracaoVideoSegundos = 0,
  aoAtualizarJobAposCapturaFramePreview,
  aoUsarFrameCapturadoNoDocumentoMarkdown,
}: PropsModalEditorAnotacaoImagemTutorialTranscribrothers) {
  const { pedirConfirmacao, elementoDialogoConfirmacao } =
    usarDialogoConfirmacaoAcaoUiSubstituindoWindowConfirmTranscribrothers();
  const { pushToast } = usarToastFeedbackAcoesUiTranscribrothers();
  const fabricMountRef = useRef<HTMLDivElement | null>(null);
  const canvasHostRef = useRef<HTMLDivElement | null>(null);
  const canvasElRef = useRef<HTMLCanvasElement | null>(null);
  const fabricRef = useRef<fabric.Canvas | null>(null);
  const imagemFundoRef = useRef<fabric.Image | null>(null);
  const dimensoesImagemFundoCanvasRef = useRef<{ largura: number; altura: number } | null>(null);
  const modoZoomVisualizacaoCanvasRef = useRef<ModoZoomVisualizacaoCanvasAnotacaoImagemTutorialTranscribrothers>(
    "ajustarArea",
  );
  const arrastoFormaRef = useRef<ArrastoFormaAnotacaoTranscribrothers | null>(null);
  const corAnotacaoRef = useRef(COR_PADRAO_FERRAMENTAS_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS);
  const ferramentaRef = useRef<FerramentaAnotacaoImagemTutorialTranscribrothers>("selecionar");
  const geracaoCarregamentoImagemFundoCanvasRef = useRef(0);
  const recorteAplicadoNestaSessaoCanvasRef = useRef(false);
  const cachePreviewsNavegacaoRef = useRef<
    Record<string, ItemCachePreviewFrameNavegacaoTutorialTranscribrothers>
  >({});
  const timestampsPreviewInflightRef = useRef<Set<string>>(new Set());

  const [ferramenta, setFerramenta] = useState<FerramentaAnotacaoImagemTutorialTranscribrothers>("selecionar");
  const [corAnotacao, setCorAnotacao] = useState(COR_PADRAO_FERRAMENTAS_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS);
  const [salvando, setSalvando] = useState(false);
  const [inserindoNoDocumento, setInserindoNoDocumento] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [processandoGestaoLocal, setProcessandoGestaoLocal] = useState(false);
  const [versaoImagemExibidaNoModal, setVersaoImagemExibidaNoModal] =
    useState<VersaoImagemExibidaNoEditorAnotacaoModalTranscribrothers>(() =>
      resolverVersaoImagemInicialNoEditorAnotacaoModalTranscribrothers(registroAnotacao),
    );
  const [modoZoomVisualizacaoCanvas, setModoZoomVisualizacaoCanvas] =
    useState<ModoZoomVisualizacaoCanvasAnotacaoImagemTutorialTranscribrothers>("ajustarArea");
  const [cachePreviewsNavegacao, setCachePreviewsNavegacao] = useState<
    Record<string, ItemCachePreviewFrameNavegacaoTutorialTranscribrothers>
  >({});
  const [instanteExibidoSegundos, setInstanteExibidoSegundos] = useState<number | null>(
    typeof instanteSegundosInicial === "number" ? instanteSegundosInicial : null,
  );
  const [capturandoFrameNavegacao, setCapturandoFrameNavegacao] = useState(false);
  const [aplicandoFrameNoDocumento, setAplicandoFrameNoDocumento] = useState(false);

  useEffect(() => {
    cachePreviewsNavegacaoRef.current = cachePreviewsNavegacao;
  }, [cachePreviewsNavegacao]);

  useEffect(() => {
    setVersaoImagemExibidaNoModal(
      resolverVersaoImagemInicialNoEditorAnotacaoModalTranscribrothers(registroAnotacao),
    );
    setCachePreviewsNavegacao({});
    cachePreviewsNavegacaoRef.current = {};
    setInstanteExibidoSegundos(
      typeof instanteSegundosInicial === "number" ? instanteSegundosInicial : null,
    );
  }, [nomeArquivoOriginal]);

  useEffect(() => {
    if (!registroAnotacao?.tem_arquivo_anotado) {
      setVersaoImagemExibidaNoModal("original");
    }
  }, [registroAnotacao?.tem_arquivo_anotado]);

  const instanteFrameExibidoSegundos =
    instanteExibidoSegundos ??
    (typeof instanteSegundosInicial === "number" ? instanteSegundosInicial : null);
  const noSlotDocumentoNavegacao = instanteEhSlotDocumentoFrameNavegacaoTutorialTranscribrothers(
    instanteFrameExibidoSegundos ?? Number.NaN,
    typeof instanteSegundosInicial === "number" ? instanteSegundosInicial : null,
  );

  const nomeArquivoAnotadoDocumento =
    registroAnotacao?.nome_arquivo_anotado ??
    derivarNomeArquivoPngAnotadoLocalTranscribrothers(nomeArquivoOriginal);

  const nomeArquivoBaseCanvasEdicao = useMemo(() => {
    if (versaoImagemExibidaNoModal === "anotado" && registroAnotacao?.tem_arquivo_anotado) {
      return (
        registroAnotacao.nome_arquivo_anotado ??
        derivarNomeArquivoPngAnotadoLocalTranscribrothers(nomeArquivoOriginal)
      );
    }
    return nomeArquivoOriginal;
  }, [
    versaoImagemExibidaNoModal,
    nomeArquivoOriginal,
    registroAnotacao?.tem_arquivo_anotado,
    registroAnotacao?.nome_arquivo_anotado,
  ]);

  const urlImagemCanvasNavegacao = useMemo(() => {
    if (!noSlotDocumentoNavegacao && instanteFrameExibidoSegundos != null) {
      const preview =
        cachePreviewsNavegacao[
          chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers(instanteFrameExibidoSegundos)
        ];
      if (preview?.urlPreview) return preview.urlPreview;
      return null;
    }
    return urlAssetPngJobParaNomeArquivoTranscribrothers(jobId, nomeArquivoBaseCanvasEdicao);
  }, [
    noSlotDocumentoNavegacao,
    instanteFrameExibidoSegundos,
    cachePreviewsNavegacao,
    jobId,
    nomeArquivoBaseCanvasEdicao,
  ]);

  const exibindoAnotadaNoModal = versaoImagemExibidaNoModal === "anotado";

  const processandoAlgumaAcao =
    salvando ||
    inserindoNoDocumento ||
    processandoGestaoVersoes ||
    processandoGestaoLocal ||
    capturandoFrameNavegacao ||
    aplicandoFrameNoDocumento;

  const mostrarNavegacaoFrame = navegacaoFrameVideoDeveAparecerNaModalAnotacaoTutorialTranscribrothers({
    temVideoEntrada,
    instanteSegundos: instanteFrameExibidoSegundos,
  });
  const nomeArquivoCandidatoFrame =
    resolverNomeArquivoCandidatoPreviewFrameVisivelParaCommitTutorialTranscribrothers({
      noSlotDocumento: noSlotDocumentoNavegacao,
      instanteExibidoSegundos: instanteFrameExibidoSegundos,
      instanteDocumentoSegundos:
        typeof instanteSegundosInicial === "number" ? instanteSegundosInicial : null,
      cachePreviewsPorChave: cachePreviewsNavegacao,
    });
  const podeUsarEsteFrame = usarEsteFrameNoDocumentoDeveFicarHabilitadoTranscribrothers({
    nomeArquivoNoDocumento: nomeArquivoOriginal,
    nomeArquivoCandidato: nomeArquivoCandidatoFrame,
    capturando: capturandoFrameNavegacao || aplicandoFrameNoDocumento,
  });
  const candidatoFramePendente = Boolean(nomeArquivoCandidatoFrame) && !noSlotDocumentoNavegacao;
  const aguardandoPreviewAtual =
    !noSlotDocumentoNavegacao && urlImagemCanvasNavegacao == null;
  const mostrandoOverlayCanvas = carregando || capturandoFrameNavegacao || aguardandoPreviewAtual;
  const acoesDocumentoDesabilitadasEnquantoCandidato =
    processandoAlgumaAcao || carregando || candidatoFramePendente;

  useEffect(() => {
    corAnotacaoRef.current = corAnotacao;
  }, [corAnotacao]);

  useEffect(() => {
    ferramentaRef.current = ferramenta;
  }, [ferramenta]);

  useEffect(() => {
    modoZoomVisualizacaoCanvasRef.current = modoZoomVisualizacaoCanvas;
  }, [modoZoomVisualizacaoCanvas]);

  const sincronizarZoomVisualizacaoCanvasAnotacaoTranscribrothers = useCallback(() => {
    const canvas = fabricRef.current;
    const host = canvasHostRef.current;
    const mount = fabricMountRef.current;
    const dimensoes = dimensoesImagemFundoCanvasRef.current;
    if (!canvas || !host || !mount || !dimensoes) return;
    aplicarModoZoomVisualizacaoCanvasFabricAnotacaoImagemTutorialTranscribrothers(
      canvas,
      host,
      mount,
      modoZoomVisualizacaoCanvasRef.current,
      dimensoes.largura,
      dimensoes.altura,
    );
  }, []);

  const alternarModoZoomVisualizacaoCanvasAnotacaoTranscribrothers = useCallback(() => {
    setModoZoomVisualizacaoCanvas((modoAtual) =>
      modoAtual === "tamanhoReal" ? "ajustarArea" : "tamanhoReal",
    );
  }, []);

  const aplicarModoCanvas = useCallback((canvas: fabric.Canvas, modo: FerramentaAnotacaoImagemTutorialTranscribrothers) => {
    canvas.isDrawingMode = false;
    canvas.selection = modo === "selecionar";
    canvas.forEachObject((obj) => {
      if (obj === imagemFundoRef.current) {
        obj.selectable = false;
        obj.evented = false;
      } else {
        obj.selectable = modo === "selecionar";
        obj.evented = modo === "selecionar";
      }
    });
    canvas.requestRenderAll();
  }, []);

  const finalizarFerramentaDesenhoEVoltarSelecionar = useCallback(
    (canvas: fabric.Canvas) => {
      aplicarModoCanvas(canvas, "selecionar");
      setFerramenta("selecionar");
    },
    [aplicarModoCanvas],
  );

  const substituirCanvasPelaImagemDataUrlAposRecorteTranscribrothers = useCallback(
    (dataUrl: string) => {
      const canvas = fabricRef.current;
      if (!canvas) return;

      const geracao = ++geracaoCarregamentoImagemFundoCanvasRef.current;
      setCarregando(true);
      setErro(null);
      arrastoFormaRef.current = null;

      fabric.Image.fromURL(
        dataUrl,
        (img) => {
          if (geracao !== geracaoCarregamentoImagemFundoCanvasRef.current) return;
          const canvasAtual = fabricRef.current;
          if (!canvasAtual) return;

          if (!img.width || !img.height) {
            setErro("Não foi possível aplicar o recorte.");
            setCarregando(false);
            return;
          }

          canvasAtual.clear();
          canvasAtual.setWidth(img.width);
          canvasAtual.setHeight(img.height);
          img.set({
            left: 0,
            top: 0,
            selectable: false,
            evented: false,
          });
          imagemFundoRef.current = img;
          dimensoesImagemFundoCanvasRef.current = {
            largura: img.width ?? 0,
            altura: img.height ?? 0,
          };
          canvasAtual.add(img);
          canvasAtual.sendToBack(img);
          recorteAplicadoNestaSessaoCanvasRef.current = true;
          aplicarModoCanvas(canvasAtual, "selecionar");
          setFerramenta("selecionar");
          canvasAtual.requestRenderAll();
          setCarregando(false);
          requestAnimationFrame(() => {
            requestAnimationFrame(() => sincronizarZoomVisualizacaoCanvasAnotacaoTranscribrothers());
          });
        },
        { crossOrigin: "anonymous" },
      );
    },
    [aplicarModoCanvas, sincronizarZoomVisualizacaoCanvasAnotacaoTranscribrothers],
  );

  const carregarImagemFundoNoCanvasAnotacaoTranscribrothers = useCallback(
    (urlImagem: string) => {
      const canvas = fabricRef.current;
      if (!canvas || !urlImagem) return;

      const geracao = ++geracaoCarregamentoImagemFundoCanvasRef.current;
      setCarregando(true);
      setErro(null);
      arrastoFormaRef.current = null;
      recorteAplicadoNestaSessaoCanvasRef.current = false;

      const separador = urlImagem.includes("?") ? "&" : "?";
      const url = `${urlImagem}${separador}t=${geracao}`;

      fabric.Image.fromURL(
        url,
        (img) => {
          if (geracao !== geracaoCarregamentoImagemFundoCanvasRef.current) return;
          const canvasAtual = fabricRef.current;
          if (!canvasAtual) return;

          if (!img.width || !img.height) {
            setErro("Não foi possível carregar as dimensões da imagem.");
            setCarregando(false);
            return;
          }

          canvasAtual.clear();
          canvasAtual.setWidth(img.width);
          canvasAtual.setHeight(img.height);
          img.set({
            left: 0,
            top: 0,
            selectable: false,
            evented: false,
          });
          imagemFundoRef.current = img;
          dimensoesImagemFundoCanvasRef.current = {
            largura: img.width ?? 0,
            altura: img.height ?? 0,
          };
          canvasAtual.add(img);
          canvasAtual.sendToBack(img);
          aplicarModoCanvas(canvasAtual, ferramentaRef.current);
          canvasAtual.requestRenderAll();
          setCarregando(false);
          requestAnimationFrame(() => {
            requestAnimationFrame(() => sincronizarZoomVisualizacaoCanvasAnotacaoTranscribrothers());
          });
        },
        { crossOrigin: "anonymous" },
      );
    },
    [aplicarModoCanvas, sincronizarZoomVisualizacaoCanvasAnotacaoTranscribrothers],
  );

  const canvasTemAnotacoesAlemDoFundoTranscribrothers = useCallback((): boolean => {
    const canvas = fabricRef.current;
    if (!canvas) return false;
    return canvas.getObjects().some((obj) => obj !== imagemFundoRef.current);
  }, []);

  const nomesProtegidosDocumentoNavegacaoFrame = useMemo(() => {
    const nomes = [nomeArquivoOriginal];
    if (registroAnotacao?.tem_arquivo_anotado) nomes.push(nomeArquivoAnotadoDocumento);
    return nomes;
  }, [
    nomeArquivoOriginal,
    registroAnotacao?.tem_arquivo_anotado,
    nomeArquivoAnotadoDocumento,
  ]);

  const mesclarItensPreviewNoCacheNavegacaoTranscribrothers = useCallback(
    (
      itens: {
        timestamp_segundos_efetivo: number;
        timestamp_segundos_solicitado?: number;
        nome_arquivo: string;
        url_preview: string;
      }[],
    ) => {
      const aplicarNoCache = (
        prev: Record<string, ItemCachePreviewFrameNavegacaoTutorialTranscribrothers>,
      ) => {
        const next = { ...prev };
        for (const item of itens) {
          const entrada: ItemCachePreviewFrameNavegacaoTutorialTranscribrothers = {
            instanteSegundos: item.timestamp_segundos_efetivo,
            nomeArquivoPreview: item.nome_arquivo,
            urlPreview: item.url_preview,
          };
          next[chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers(item.timestamp_segundos_efetivo)] =
            entrada;
          if (typeof item.timestamp_segundos_solicitado === "number") {
            next[
              chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers(item.timestamp_segundos_solicitado)
            ] = entrada;
          }
        }
        return next;
      };
      cachePreviewsNavegacaoRef.current = aplicarNoCache(cachePreviewsNavegacaoRef.current);
      setCachePreviewsNavegacao((prev) => aplicarNoCache(prev));
    },
    [],
  );

  const buscarPreviewsNavegacaoFaltandoTranscribrothers = useCallback(
    async (timestamps: number[]) => {
      const instanteDocumento =
        typeof instanteSegundosInicial === "number" ? instanteSegundosInicial : null;
      const faltando = timestamps.filter((t) => {
        if (instanteEhSlotDocumentoFrameNavegacaoTutorialTranscribrothers(t, instanteDocumento)) {
          return false;
        }
        const chave = chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers(t);
        if (cachePreviewsNavegacaoRef.current[chave]) return false;
        if (timestampsPreviewInflightRef.current.has(chave)) return false;
        return true;
      });
      if (faltando.length === 0) return;
      const lote = faltando.slice(0, 12);
      for (const t of lote) {
        timestampsPreviewInflightRef.current.add(
          chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers(t),
        );
      }
      try {
        const itens = await previsualizarFramesNavegacaoVideoTutorialJobApiTranscribrothers(
          jobId,
          lote,
        );
        mesclarItensPreviewNoCacheNavegacaoTranscribrothers(itens);
      } finally {
        for (const t of lote) {
          timestampsPreviewInflightRef.current.delete(
            chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers(t),
          );
        }
      }
    },
    [jobId, instanteSegundosInicial, mesclarItensPreviewNoCacheNavegacaoTranscribrothers],
  );

  const prefetchJanelaNavegacaoFrameTranscribrothers = useCallback(
    async (centroSegundos: number) => {
      const lista = montarInstantesPrefetchJanelaNavegacaoFrameTutorialTranscribrothers({
        centroSegundos,
        instanteDocumentoSegundos:
          typeof instanteSegundosInicial === "number" ? instanteSegundosInicial : null,
        duracaoVideoSegundos,
      });
      try {
        await buscarPreviewsNavegacaoFaltandoTranscribrothers(lista);
      } catch {
        /* a prévia extra não bloqueia o frame já visível */
      }
    },
    [instanteSegundosInicial, duracaoVideoSegundos, buscarPreviewsNavegacaoFaltandoTranscribrothers],
  );

  const irParaInstanteSegundosNavegacaoFrameTranscribrothers = useCallback(
    async (proximo: number) => {
      if (!mostrarNavegacaoFrame || instanteFrameExibidoSegundos == null) return;
      if (Math.abs(proximo - instanteFrameExibidoSegundos) < 0.0005) return;
      if (
        devePedirConfirmacaoAnotacaoAoNavegarSetaFrameTutorialTranscribrothers({
          temMarcacoesNaoSalvasNoCanvas: canvasTemAnotacoesAlemDoFundoTranscribrothers(),
          temArquivoAnotadoSalvoNoDocumento: Boolean(registroAnotacao?.tem_arquivo_anotado),
          exibindoVersaoAnotada: exibindoAnotadaNoModal,
        })
      ) {
        const ok = await pedirConfirmacao({
          titulo: "Descartar marcações não salvas?",
          mensagem:
            "Há rabiscos nesta tela que ainda não foram salvos. Trocar o instante descarta só o que está no canvas agora; a versão anotada do documento permanece.",
          rotuloConfirmar: "Continuar",
          varianteConfirmar: "destrutiva",
        });
        if (!ok) return;
      }
      const instanteDocumento =
        typeof instanteSegundosInicial === "number" ? instanteSegundosInicial : null;
      const voltandoAoDocumento = instanteEhSlotDocumentoFrameNavegacaoTutorialTranscribrothers(
        proximo,
        instanteDocumento,
      );
      setErro(null);
      if (voltandoAoDocumento) {
        setInstanteExibidoSegundos(proximo);
        setVersaoImagemExibidaNoModal(
          resolverVersaoImagemInicialNoEditorAnotacaoModalTranscribrothers(registroAnotacao),
        );
        void prefetchJanelaNavegacaoFrameTranscribrothers(proximo);
        return;
      }
      const chaveProximo = chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers(proximo);
      const jaTem = cachePreviewsNavegacaoRef.current[chaveProximo];
      if (jaTem) {
        setInstanteExibidoSegundos(proximo);
        setVersaoImagemExibidaNoModal("original");
        void prefetchJanelaNavegacaoFrameTranscribrothers(proximo);
        return;
      }
      setCapturandoFrameNavegacao(true);
      try {
        await buscarPreviewsNavegacaoFaltandoTranscribrothers([proximo]);
        setInstanteExibidoSegundos(proximo);
        setVersaoImagemExibidaNoModal("original");
        void prefetchJanelaNavegacaoFrameTranscribrothers(proximo);
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        setErro(msg);
        pushToast(msg, "error");
      } finally {
        setCapturandoFrameNavegacao(false);
      }
    },
    [
      mostrarNavegacaoFrame,
      instanteFrameExibidoSegundos,
      canvasTemAnotacoesAlemDoFundoTranscribrothers,
      registroAnotacao,
      exibindoAnotadaNoModal,
      pedirConfirmacao,
      instanteSegundosInicial,
      prefetchJanelaNavegacaoFrameTranscribrothers,
      buscarPreviewsNavegacaoFaltandoTranscribrothers,
      pushToast,
    ],
  );

  const navegarFrameVideoNaModalAnotacaoTranscribrothers = useCallback(
    async (direcao: -1 | 1) => {
      if (instanteFrameExibidoSegundos == null) return;
      const proximo = instanteAposPassoNavegacaoFrameVideoTutorialTranscribrothers({
        instanteAtual: instanteFrameExibidoSegundos,
        direcao,
        duracaoVideoSegundos,
      });
      await irParaInstanteSegundosNavegacaoFrameTranscribrothers(proximo);
    },
    [instanteFrameExibidoSegundos, duracaoVideoSegundos, irParaInstanteSegundosNavegacaoFrameTranscribrothers],
  );

  const trilhaPassosNavegacaoFrame = useMemo(() => {
    if (
      !mostrarNavegacaoFrame ||
      instanteFrameExibidoSegundos == null ||
      typeof instanteSegundosInicial !== "number"
    ) {
      return null;
    }
    return montarTrilhaPassosNavegacaoFrameAncoradaNoDocumentoTutorialTranscribrothers({
      instanteAtualSegundos: instanteFrameExibidoSegundos,
      instanteDocumentoSegundos: instanteSegundosInicial,
      duracaoVideoSegundos,
    });
  }, [mostrarNavegacaoFrame, instanteFrameExibidoSegundos, instanteSegundosInicial, duracaoVideoSegundos]);

  const persistirCanvasComoPngAnotadoTranscribrothers = useCallback(
    async (nomeArquivoDestino: string = nomeArquivoOriginal): Promise<JobStatus> => {
      const canvas = fabricRef.current;
      if (!canvas) {
        throw new Error("Canvas de anotação indisponível.");
      }
      const dataUrl = exportarCanvasFabricAnotacaoComoPngDataUrlTranscribrothers(canvas);
      const blob = await converterDataUrlPngParaBlobTranscribrothers(dataUrl);
      return gravarPngAnotadoScreenshotTutorialJobApiTranscribrothers(jobId, nomeArquivoDestino, blob);
    },
    [jobId, nomeArquivoOriginal],
  );

  const usarEsteFrameNoDocumentoPelaModalAnotacaoTranscribrothers = useCallback(async (args?: {
    persistirAnotacaoDoCanvas?: boolean;
  }) => {
    if (
      !podeUsarEsteFrame ||
      !nomeArquivoCandidatoFrame ||
      instanteFrameExibidoSegundos == null ||
      noSlotDocumentoNavegacao
    ) {
      return;
    }
    if (
      devePedirConfirmacaoAnotacaoAoUsarEsteFrameTutorialTranscribrothers({
        temArquivoAnotadoSalvoNoDocumento: Boolean(registroAnotacao?.tem_arquivo_anotado),
        saindoDoSlotDocumento: true,
      })
    ) {
      const ok = await pedirConfirmacao({
        titulo: "Trocar o frame no documento?",
        mensagem:
          "O tutorial passa a usar este instante. A versão anotada da imagem anterior permanece nos assets, mas sai do documento.",
        rotuloConfirmar: ROTULO_BOTAO_COMMIT_USAR_NO_TUTORIAL_MODAL_ANOTACAO_TRANSCRIBROTHERS,
        varianteConfirmar: "destrutiva",
      });
      if (!ok) return;
    }
    setAplicandoFrameNoDocumento(true);
    setErro(null);
    try {
      const promovido = await promoverFramePrevisualizacaoParaAssetsVideoTutorialJobApiTranscribrothers(
        jobId,
        nomeArquivoCandidatoFrame,
        instanteFrameExibidoSegundos,
      );
      aoAtualizarJobAposCapturaFramePreview?.(promovido.job);
      if (args?.persistirAnotacaoDoCanvas) {
        const jobAnotado = await persistirCanvasComoPngAnotadoTranscribrothers(promovido.nome_arquivo);
        aoSalvarComSucesso(jobAnotado, "usar_no_tutorial");
        recorteAplicadoNestaSessaoCanvasRef.current = false;
      }
      const nomesDescartar = nomesArquivoPreviewParaDescartarNavegacaoFrameTutorialTranscribrothers({
        nomesPreviewEmCache: Object.values(cachePreviewsNavegacaoRef.current).map(
          (item) => item.nomeArquivoPreview,
        ),
        nomesProtegidosDocumento: nomesProtegidosDocumentoNavegacaoFrame,
        nomePreviewPromovido: nomeArquivoCandidatoFrame,
      });
      if (nomesDescartar.length > 0) {
        await descartarPrevisualizacaoFramesNavegacaoVideoTutorialJobApiTranscribrothers(
          jobId,
          nomesDescartar,
          nomesProtegidosDocumentoNavegacaoFrame,
        );
      }
      await aoUsarFrameCapturadoNoDocumentoMarkdown?.({
        nomeArquivoAnterior: nomeArquivoOriginal,
        nomeArquivoNovo: promovido.nome_arquivo,
        instanteSegundos: instanteFrameExibidoSegundos,
      });
      if (args?.persistirAnotacaoDoCanvas) {
        await aoSincronizarMarkdownComVersaoAnotada?.(promovido.nome_arquivo, { silencioso: true });
      }
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      setErro(msg);
      pushToast(msg, "error");
    } finally {
      setAplicandoFrameNoDocumento(false);
    }
  }, [
    podeUsarEsteFrame,
    nomeArquivoCandidatoFrame,
    instanteFrameExibidoSegundos,
    noSlotDocumentoNavegacao,
    registroAnotacao?.tem_arquivo_anotado,
    pedirConfirmacao,
    jobId,
    aoAtualizarJobAposCapturaFramePreview,
    nomesProtegidosDocumentoNavegacaoFrame,
    aoUsarFrameCapturadoNoDocumentoMarkdown,
    nomeArquivoOriginal,
    pushToast,
    persistirCanvasComoPngAnotadoTranscribrothers,
    aoSalvarComSucesso,
    aoSincronizarMarkdownComVersaoAnotada,
  ]);

  useEffect(() => {
    sincronizarZoomVisualizacaoCanvasAnotacaoTranscribrothers();
  }, [modoZoomVisualizacaoCanvas, sincronizarZoomVisualizacaoCanvasAnotacaoTranscribrothers]);

  useEffect(() => {
    const host = canvasHostRef.current;
    if (!host) return;
    const observador = new ResizeObserver(() => {
      if (modoZoomVisualizacaoCanvasRef.current === "ajustarArea") {
        sincronizarZoomVisualizacaoCanvasAnotacaoTranscribrothers();
      }
    });
    observador.observe(host);
    return () => observador.disconnect();
  }, [sincronizarZoomVisualizacaoCanvasAnotacaoTranscribrothers]);

  useEffect(() => {
    const mount = fabricMountRef.current;
    if (!mount) return;

    const el = document.createElement("canvas");
    mount.appendChild(el);
    canvasElRef.current = el;

    const canvas = new fabric.Canvas(el, {
      selection: true,
      preserveObjectStacking: true,
    });
    fabricRef.current = canvas;

    return () => {
      geracaoCarregamentoImagemFundoCanvasRef.current += 1;
      canvas.dispose();
      fabricRef.current = null;
      imagemFundoRef.current = null;
      canvasElRef.current = null;
      while (mount.firstChild) {
        mount.removeChild(mount.firstChild);
      }
    };
  }, [jobId, nomeArquivoOriginal]);

  useEffect(() => {
    if (!urlImagemCanvasNavegacao) return;
    carregarImagemFundoNoCanvasAnotacaoTranscribrothers(urlImagemCanvasNavegacao);
  }, [urlImagemCanvasNavegacao, carregarImagemFundoNoCanvasAnotacaoTranscribrothers]);

  useEffect(() => {
    const canvas = fabricRef.current;
    if (!canvas) return;
    aplicarModoCanvas(canvas, ferramenta);
  }, [ferramenta, aplicarModoCanvas]);

  useEffect(() => {
    const canvas = fabricRef.current;
    if (!canvas) return;
    const cor = corAnotacao;

    const onMouseDown = (opt: fabric.IEvent<Event>) => {
      if (ferramenta === "selecionar") return;
      const ponteiro = obterCoordenadasCanvasFabricAPartirDeEventoPonteiroAnotacaoImagemTutorialTranscribrothers(
        canvas,
        opt,
      );
      if (!ponteiro) return;
      const { x, y } = ponteiro;
      const corAtual = corAnotacaoRef.current;

      if (ferramenta === "texto") {
        const texto = new fabric.IText("Texto", {
          left: x,
          top: y,
          fill: corAtual,
          fontSize: 22,
          fontFamily: "system-ui, Segoe UI, sans-serif",
          fontWeight: "600",
        });
        canvas.add(texto);
        canvas.setActiveObject(texto);
        finalizarFerramentaDesenhoEVoltarSelecionar(canvas);
        return;
      }

      if (ferramenta === "recortar") {
        const preview = new fabric.Rect({
          left: x,
          top: y,
          width: 1,
          height: 1,
          ...obterEstiloRetanguloPreviewRecorteAnotacaoImagemTutorialTranscribrothers(),
          selectable: false,
          evented: false,
        });
        canvas.add(preview);
        arrastoFormaRef.current = { tipo: "recortar", x1: x, y1: y, preview };
        return;
      }

      if (ferramenta === "seta" || ferramenta === "linha") {
        const linha = new fabric.Line([x, y, x, y], {
          stroke: corAtual,
          strokeWidth: ESPESSURA_TRACO_PADRAO_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS,
          selectable: false,
          evented: false,
        });
        canvas.add(linha);
        arrastoFormaRef.current = {
          tipo: ferramenta === "seta" ? "seta" : "linha",
          x1: x,
          y1: y,
          preview: linha,
        };
        return;
      }

      if (ferramenta === "destaque") {
        const preview = new fabric.Rect({
          left: x,
          top: y,
          width: 1,
          height: 1,
          ...obterEstiloRetanguloDestaqueSemitransparenteSemBordaAnotacaoImagemTutorialTranscribrothers(),
          selectable: false,
          evented: false,
        });
        canvas.add(preview);
        arrastoFormaRef.current = { tipo: "destaque", x1: x, y1: y, preview };
        return;
      }

      if (ferramenta === "retangulo") {
        const preview = new fabric.Rect({
          left: x,
          top: y,
          width: 1,
          height: 1,
          ...obterEstiloContornoFormaVazadaAnotacaoImagemTutorialTranscribrothers(corAtual),
          selectable: false,
          evented: false,
        });
        canvas.add(preview);
        arrastoFormaRef.current = { tipo: "retangulo", x1: x, y1: y, preview };
        return;
      }

      if (ferramenta === "elipse") {
        const preview = new fabric.Ellipse({
          left: x,
          top: y,
          originX: "center",
          originY: "center",
          rx: 1,
          ry: 1,
          ...obterEstiloContornoFormaVazadaAnotacaoImagemTutorialTranscribrothers(corAtual),
          selectable: false,
          evented: false,
        });
        canvas.add(preview);
        arrastoFormaRef.current = { tipo: "elipse", x1: x, y1: y, preview };
      }
    };

    const onMouseMove = (opt: fabric.IEvent<Event>) => {
      const arrasto = arrastoFormaRef.current;
      if (!arrasto?.preview) return;
      const ponteiroMovimento =
        obterCoordenadasCanvasFabricAPartirDeEventoPonteiroAnotacaoImagemTutorialTranscribrothers(canvas, opt);
      if (!ponteiroMovimento) return;
      const { x, y } = ponteiroMovimento;
      const corAtual = corAnotacaoRef.current;

      if (arrasto.tipo === "seta" || arrasto.tipo === "linha") {
        arrasto.preview.set({ x2: x, y2: y });
        arrasto.preview.setCoords();
        canvas.requestRenderAll();
        return;
      }

      if (arrasto.tipo === "destaque") {
        const atualizado = criarRetanguloDestaqueSemitransparenteAnotacaoTranscribrothers(
          arrasto.x1,
          arrasto.y1,
          x,
          y,
        );
        if (!atualizado) return;
        arrasto.preview.set({
          left: atualizado.left,
          top: atualizado.top,
          width: atualizado.width,
          height: atualizado.height,
          fill: atualizado.fill,
          stroke: atualizado.stroke,
          strokeWidth: atualizado.strokeWidth,
        });
        arrasto.preview.setCoords();
        canvas.requestRenderAll();
        return;
      }

      if (arrasto.tipo === "recortar") {
        const left = Math.min(arrasto.x1, x);
        const top = Math.min(arrasto.y1, y);
        const width = Math.max(1, Math.abs(x - arrasto.x1));
        const height = Math.max(1, Math.abs(y - arrasto.y1));
        arrasto.preview.set({ left, top, width, height });
        arrasto.preview.setCoords();
        canvas.requestRenderAll();
        return;
      }

      if (arrasto.tipo === "retangulo") {
        const atualizado = criarRetanguloVazadoAnotacaoTranscribrothers(arrasto.x1, arrasto.y1, x, y, corAtual);
        if (!atualizado) return;
        arrasto.preview.set({
          left: atualizado.left,
          top: atualizado.top,
          width: atualizado.width,
          height: atualizado.height,
        });
        arrasto.preview.setCoords();
        canvas.requestRenderAll();
        return;
      }

      if (arrasto.tipo === "elipse") {
        const atualizado = criarElipseVazadaAnotacaoTranscribrothers(arrasto.x1, arrasto.y1, x, y, corAtual);
        if (!atualizado) return;
        arrasto.preview.set({
          left: atualizado.left,
          top: atualizado.top,
          rx: atualizado.rx,
          ry: atualizado.ry,
          originX: "center",
          originY: "center",
        });
        arrasto.preview.setCoords();
        canvas.requestRenderAll();
      }
    };

    const onMouseUp = (opt: fabric.IEvent<Event>) => {
      const arrasto = arrastoFormaRef.current;
      if (!arrasto) return;
      const ponteiroSoltar =
        obterCoordenadasCanvasFabricAPartirDeEventoPonteiroAnotacaoImagemTutorialTranscribrothers(canvas, opt);
      if (!ponteiroSoltar) return;
      const { x, y } = ponteiroSoltar;
      const corAtual = corAnotacaoRef.current;
      arrastoFormaRef.current = null;

      if (arrasto.tipo === "linha" && arrasto.preview) {
        const dist = Math.hypot(x - arrasto.x1, y - arrasto.y1);
        if (dist < TAMANHO_MINIMO_FORMA_ARRASTE_PX_TRANSCRIBROTHERS) {
          canvas.remove(arrasto.preview);
        } else {
          arrasto.preview.set({
            selectable: true,
            evented: true,
          });
          arrasto.preview.setCoords();
          canvas.setActiveObject(arrasto.preview);
        }
        finalizarFerramentaDesenhoEVoltarSelecionar(canvas);
        return;
      }

      if (arrasto.tipo === "recortar") {
        if (arrasto.preview) {
          canvas.remove(arrasto.preview);
        }
        const dimensoes = dimensoesImagemFundoCanvasRef.current;
        const regiao = calcularRetanguloRecorteNormalizadoCanvasAnotacaoImagemTutorialTranscribrothers(
          arrasto.x1,
          arrasto.y1,
          x,
          y,
          dimensoes?.largura ?? canvas.getWidth() ?? 0,
          dimensoes?.altura ?? canvas.getHeight() ?? 0,
        );
        if (!regiao) {
          finalizarFerramentaDesenhoEVoltarSelecionar(canvas);
          return;
        }
        canvas.discardActiveObject();
        canvas.requestRenderAll();
        try {
          const dataUrl = exportarCanvasFabricAnotacaoComoPngDataUrlTranscribrothers(canvas, regiao);
          substituirCanvasPelaImagemDataUrlAposRecorteTranscribrothers(dataUrl);
        } catch (e) {
          setErro(e instanceof Error ? e.message : "Não foi possível aplicar o recorte.");
          finalizarFerramentaDesenhoEVoltarSelecionar(canvas);
        }
        return;
      }

      if (arrasto.preview) {
        canvas.remove(arrasto.preview);
      }

      if (arrasto.tipo === "seta") {
        const grupo = criarGrupoSetaAnotacaoTranscribrothers(arrasto.x1, arrasto.y1, x, y, corAtual);
        if (grupo) {
          canvas.add(grupo);
          canvas.setActiveObject(grupo);
        }
        finalizarFerramentaDesenhoEVoltarSelecionar(canvas);
        return;
      }

      if (arrasto.tipo === "destaque") {
        const rect = criarRetanguloDestaqueSemitransparenteAnotacaoTranscribrothers(
          arrasto.x1,
          arrasto.y1,
          x,
          y,
        );
        if (rect) {
          canvas.add(rect);
          canvas.setActiveObject(rect);
        }
        finalizarFerramentaDesenhoEVoltarSelecionar(canvas);
        return;
      }

      if (arrasto.tipo === "retangulo") {
        const rect = criarRetanguloVazadoAnotacaoTranscribrothers(arrasto.x1, arrasto.y1, x, y, corAtual);
        if (rect) {
          canvas.add(rect);
          canvas.setActiveObject(rect);
        }
        finalizarFerramentaDesenhoEVoltarSelecionar(canvas);
        return;
      }

      if (arrasto.tipo === "elipse") {
        const elipse = criarElipseVazadaAnotacaoTranscribrothers(arrasto.x1, arrasto.y1, x, y, corAtual);
        if (elipse) {
          canvas.add(elipse);
          canvas.setActiveObject(elipse);
        }
        finalizarFerramentaDesenhoEVoltarSelecionar(canvas);
      }
    };

    canvas.on("mouse:down", onMouseDown);
    canvas.on("mouse:move", onMouseMove);
    canvas.on("mouse:up", onMouseUp);
    return () => {
      canvas.off("mouse:down", onMouseDown);
      canvas.off("mouse:move", onMouseMove);
      canvas.off("mouse:up", onMouseUp);
    };
  }, [ferramenta, finalizarFerramentaDesenhoEVoltarSelecionar, substituirCanvasPelaImagemDataUrlAposRecorteTranscribrothers]);

  const aoAlterarCorAnotacao = useCallback((novaCor: string) => {
    setCorAnotacao(novaCor);
    const canvas = fabricRef.current;
    if (!canvas) return;
    const ativos = canvas.getActiveObjects();
    for (const obj of ativos) {
      if (obj === imagemFundoRef.current) continue;
      aplicarCorAoObjetoFabricSelecionadoTranscribrothers(obj, novaCor);
    }
    canvas.requestRenderAll();
  }, []);

  const excluirSelecionados = useCallback(() => {
    const canvas = fabricRef.current;
    if (!canvas) return;
    const ativos = canvas.getActiveObjects();
    for (const obj of ativos) {
      if (obj !== imagemFundoRef.current) canvas.remove(obj);
    }
    canvas.discardActiveObject();
    canvas.requestRenderAll();
  }, []);

  const fecharModalDescartandoPreviewsNavegacaoTranscribrothers = useCallback(() => {
    const nomes = Object.values(cachePreviewsNavegacaoRef.current).map(
      (item) => item.nomeArquivoPreview,
    );
    if (nomes.length > 0) {
      void descartarPrevisualizacaoFramesNavegacaoVideoTutorialJobApiTranscribrothers(
        jobId,
        nomes,
        nomesProtegidosDocumentoNavegacaoFrame,
      ).catch(() => undefined);
    }
    aoFechar();
  }, [aoFechar, jobId, nomesProtegidosDocumentoNavegacaoFrame]);

  const usarNoTutorialOQueEstaNaTelaTranscribrothers = useCallback(async () => {
    const canvas = fabricRef.current;
    const decisao = resolverAcaoCommitUsarNoTutorialModalAnotacaoTranscribrothers({
      noSlotDocumento: noSlotDocumentoNavegacao,
      versaoExibidaNoEditor: versaoImagemExibidaNoModal,
      recorteFoiAplicado: recorteAplicadoNestaSessaoCanvasRef.current,
      totalObjetosCanvas: canvas?.getObjects().length ?? 1,
    });
    if (decisao.tipo === "promover_previsualizacao_frame") {
      await usarEsteFrameNoDocumentoPelaModalAnotacaoTranscribrothers({
        persistirAnotacaoDoCanvas: decisao.precisaPersistirAnotacao,
      });
      return;
    }
    setSalvando(true);
    setErro(null);
    try {
      if (decisao.precisaPersistirAnotacao) {
        const job = await persistirCanvasComoPngAnotadoTranscribrothers();
        aoSalvarComSucesso(job, "usar_no_tutorial");
        recorteAplicadoNestaSessaoCanvasRef.current = false;
      }
      if (decisao.versaoParaTutorial === "anotado") {
        if (aoSincronizarMarkdownComVersaoAnotada) {
          await aoSincronizarMarkdownComVersaoAnotada(nomeArquivoOriginal, { silencioso: true });
        } else if (aoAlternarVersaoExibicaoNoTutorial) {
          await aoAlternarVersaoExibicaoNoTutorial(nomeArquivoOriginal, "anotado", { silencioso: true });
        }
      } else if (decisao.versaoParaTutorial === "original" && aoAlternarVersaoExibicaoNoTutorial) {
        await aoAlternarVersaoExibicaoNoTutorial(nomeArquivoOriginal, "original", { silencioso: true });
      }
      pushToast("Tutorial atualizado.", "success");
      fecharModalDescartandoPreviewsNavegacaoTranscribrothers();
    } catch (e) {
      setErro(e instanceof Error ? e.message : String(e));
    } finally {
      setSalvando(false);
    }
  }, [
    noSlotDocumentoNavegacao,
    versaoImagemExibidaNoModal,
    usarEsteFrameNoDocumentoPelaModalAnotacaoTranscribrothers,
    persistirCanvasComoPngAnotadoTranscribrothers,
    aoSalvarComSucesso,
    aoSincronizarMarkdownComVersaoAnotada,
    aoAlternarVersaoExibicaoNoTutorial,
    nomeArquivoOriginal,
    pushToast,
    fecharModalDescartandoPreviewsNavegacaoTranscribrothers,
  ]);

  const inserirImagemCanvasNoDocumentoMarkdownTranscribrothers = useCallback(async () => {
    if (!aoSolicitarInserirImagemNoDocumentoMarkdown) return;
    const canvas = fabricRef.current;
    if (!canvas) return;
    const decisao = resolverNomeArquivoESePrecisaPersistirAnotacaoParaInserirNoDocumentoTranscribrothers({
      nomeArquivoOriginal,
      recorteFoiAplicado: recorteAplicadoNestaSessaoCanvasRef.current,
      totalObjetosCanvas: canvas.getObjects().length,
      jaExisteArquivoAnotado: Boolean(registroAnotacao?.tem_arquivo_anotado),
      exibindoVersaoAnotadaNoCanvas: versaoImagemExibidaNoModal === "anotado",
    });
    setErro(null);
    setInserindoNoDocumento(true);
    try {
      if (decisao.precisaPersistirAnotacao) {
        const job = await persistirCanvasComoPngAnotadoTranscribrothers();
        aoSalvarComSucesso(job, "inserir_documento");
        recorteAplicadoNestaSessaoCanvasRef.current = false;
      }
      await aoSolicitarInserirImagemNoDocumentoMarkdown(decisao.nomeArquivoParaSnippet);
    } catch (e) {
      setErro(e instanceof Error ? e.message : String(e));
    } finally {
      setInserindoNoDocumento(false);
    }
  }, [
    aoSalvarComSucesso,
    aoSolicitarInserirImagemNoDocumentoMarkdown,
    nomeArquivoOriginal,
    persistirCanvasComoPngAnotadoTranscribrothers,
    registroAnotacao?.tem_arquivo_anotado,
    versaoImagemExibidaNoModal,
  ]);

  const copiarImagemEditadaParaAreaTransferenciaTranscribrothers = useCallback(async () => {
    const canvas = fabricRef.current;
    if (!canvas) return;
    setErro(null);
    try {
      const dataUrl = exportarCanvasFabricAnotacaoComoPngDataUrlTranscribrothers(canvas);
      const blob = await converterDataUrlPngParaBlobTranscribrothers(dataUrl);
      await copiarBlobImagemPngParaAreaTransferenciaNavegadorTranscribrothers(blob);
      pushToast("Imagem editada copiada para a área de transferência.", "success");
    } catch (e) {
      const mensagem = e instanceof Error ? e.message : "Não foi possível copiar a imagem.";
      setErro(mensagem);
      pushToast(mensagem, "error");
    }
  }, [pushToast]);

  const executarAcaoGestaoVersao = useCallback(
    async (acao: () => void | Promise<void>) => {
      setProcessandoGestaoLocal(true);
      setErro(null);
      try {
        await acao();
      } catch (e) {
        setErro(e instanceof Error ? e.message : String(e));
      } finally {
        setProcessandoGestaoLocal(false);
      }
    },
    [],
  );

  const alternarVersaoImagemExibidaSoNoEditor = useCallback(
    (versao: VersaoImagemExibidaNoEditorAnotacaoModalTranscribrothers) => {
      if (versao === "anotado" && !registroAnotacao?.tem_arquivo_anotado) {
        return;
      }
      setVersaoImagemExibidaNoModal(versao);
    },
    [registroAnotacao?.tem_arquivo_anotado],
  );

  const ferramentasBarra: FerramentaAnotacaoImagemTutorialTranscribrothers[] = [
    "selecionar",
    "recortar",
    "destaque",
    "retangulo",
    "elipse",
    "linha",
    "seta",
    "texto",
  ];

  return (
    <>
    <div role="dialog" aria-modal="true" className="tb-anotacao-modal-overlay" onClick={fecharModalDescartandoPreviewsNavegacaoTranscribrothers}>
      <div
        className="tb-anotacao-modal-painel"
        onClick={(e: React.MouseEvent) => e.stopPropagation()}
        role="document"
      >
        <header className="tb-anotacao-modal-cabecalho">
          <h2 title="A captura original é preservada; a versão editada é salva em paralelo (.anotado.png).">
            Editar screenshot
          </h2>
          <button type="button" className="tb-anotacao-modal-fechar" onClick={fecharModalDescartandoPreviewsNavegacaoTranscribrothers} aria-label="Fechar">
            ×
          </button>
        </header>

        <div className="tb-anotacao-modal-ferramentas" role="toolbar" aria-label="Ferramentas de edição">
          <div className="tb-anotacao-ferramentas-esquerda">
            <div className="tb-anotacao-ferramentas-grupo-icone" role="group" aria-label="Formas e seleção">
            {ferramentasBarra.map((id) => {
              const rotulo = obterRotuloAcessivelFerramentaAnotacaoImagemTutorialTranscribrothers(id);
              return (
                <button
                  key={id}
                  type="button"
                  className={
                    ferramenta === id
                      ? "tb-anotacao-ferramenta-icone tb-anotacao-ferramenta-ativa"
                      : "tb-anotacao-ferramenta-icone"
                  }
                  aria-label={rotulo}
                  title={rotulo}
                  aria-pressed={ferramenta === id}
                  onClick={() => setFerramenta(id)}
                >
                  <IconeFerramentaAnotacaoImagemTutorialTranscribrothers ferramenta={id} />
                </button>
              );
            })}
            <button
              type="button"
              className="tb-anotacao-ferramenta-icone tb-anotacao-ferramenta-icone--excluir"
              aria-label="Excluir seleção"
              title="Excluir seleção"
              onClick={excluirSelecionados}
            >
              <IconeExcluirSelecaoAnotacaoImagemTutorialTranscribrothers />
            </button>
          </div>
            <ComponenteSeletorCorAnotacaoPaletaPredefinidaEColorPickerTranscribrothers
              corAtual={corAnotacao}
              aoSelecionarCor={aoAlterarCorAnotacao}
            />
            {mostrarNavegacaoFrame && instanteFrameExibidoSegundos != null ? (
              <div className="tb-anotacao-modal-navegacao-frame" role="group" aria-label="Trocar frame do vídeo">
                <button
                  type="button"
                  className="tb-anotacao-modal-navegacao-frame-seta"
                  aria-label="Frame anterior"
                  title="Frame anterior (0,4 s)"
                  disabled={processandoAlgumaAcao || carregando}
                  onClick={() => void navegarFrameVideoNaModalAnotacaoTranscribrothers(-1)}
                >
                  ‹
                </button>
                <span
                  className="tb-anotacao-modal-navegacao-frame-instante"
                  title={`${instanteFrameExibidoSegundos.toFixed(1)} s`}
                >
                  {formatarSegundosParaRotuloMmSsMarkdownTutorialTranscribrothers(instanteFrameExibidoSegundos)}
                </span>
                <button
                  type="button"
                  className="tb-anotacao-modal-navegacao-frame-seta"
                  aria-label="Próximo frame"
                  title="Próximo frame (0,4 s)"
                  disabled={processandoAlgumaAcao || carregando}
                  onClick={() => void navegarFrameVideoNaModalAnotacaoTranscribrothers(1)}
                >
                  ›
                </button>
                <span className="tb-anotacao-modal-navegacao-frame-hint">
                  {noSlotDocumentoNavegacao ? "No tutorial" : "Prévia"}
                </span>
              </div>
            ) : null}
          </div>
          <div className="tb-anotacao-ferramentas-direita tb-anotacao-ferramentas-acoes-direita">
            <button
              type="button"
              className="tb-anotacao-ferramenta-icone tb-anotacao-modal-btn-copiar-imagem"
              disabled={acoesDocumentoDesabilitadasEnquantoCandidato}
              title="Copiar a imagem editada para a área de transferência"
              aria-label="Copiar imagem editada"
              onClick={() => void copiarImagemEditadaParaAreaTransferenciaTranscribrothers()}
            >
              <IconeCopiarImagemEditadaAnotacaoTutorialTranscribrothers />
            </button>
            {aoSolicitarInserirImagemNoDocumentoMarkdown ? (
              <button
                type="button"
                className="tb-anotacao-ferramenta-icone tb-anotacao-modal-btn-inserir-documento"
                disabled={acoesDocumentoDesabilitadasEnquantoCandidato}
                title="Grava a edição (se houver), copia a referência e abre o Markdown para você colar no ponto certo"
                aria-label={inserindoNoDocumento ? "Inserindo no documento" : "Inserir no documento"}
                onClick={() => void inserirImagemCanvasNoDocumentoMarkdownTranscribrothers()}
              >
                <IconeInserirImagemNoDocumentoAnotacaoTutorialTranscribrothers />
              </button>
            ) : null}
            <button
              type="button"
              className={
                modoZoomVisualizacaoCanvas === "ajustarArea"
                  ? "tb-anotacao-ferramenta-icone tb-anotacao-ferramenta-ativa"
                  : "tb-anotacao-ferramenta-icone"
              }
              aria-label={
                modoZoomVisualizacaoCanvas === "ajustarArea" ? "Tamanho real" : "Ajustar à área"
              }
              title={modoZoomVisualizacaoCanvas === "ajustarArea" ? "Tamanho real" : "Ajustar à área"}
              aria-pressed={modoZoomVisualizacaoCanvas === "ajustarArea"}
              onClick={alternarModoZoomVisualizacaoCanvasAnotacaoTranscribrothers}
            >
              <IconeAjustarAreaVisualizacaoCanvasAnotacaoImagemTutorialTranscribrothers />
            </button>
          </div>
        </div>

        {erro ? <p className="tb-anotacao-erro">{erro}</p> : null}

        <div
          ref={canvasHostRef}
          className={
            modoZoomVisualizacaoCanvas === "ajustarArea"
              ? "tb-anotacao-canvas-host tb-anotacao-canvas-host--ajustar-area"
              : "tb-anotacao-canvas-host"
          }
        >
          {/* Fabric altera o DOM ao redor do canvas; não montar/desmontar irmãos via React aqui. */}
          <div ref={fabricMountRef} className="tb-anotacao-canvas-fabric-mount" />
          <div
            className={
              mostrandoOverlayCanvas
                ? "tb-anotacao-canvas-carregando-overlay tb-anotacao-canvas-carregando-overlay--visivel"
                : "tb-anotacao-canvas-carregando-overlay"
            }
            aria-hidden={!mostrandoOverlayCanvas}
            aria-live="polite"
          >
            <p className="tb-anotacao-carregando">
              {capturandoFrameNavegacao || aguardandoPreviewAtual
                ? "Buscando frame do vídeo…"
                : `Carregando ${exibindoAnotadaNoModal ? "versão anotada" : "captura original"}…`}
            </p>
          </div>
        </div>

        {trilhaPassosNavegacaoFrame ? (
          <div
            className="tb-anotacao-trilha-passos-navegacao-frame"
            role="group"
            aria-label="Passos em torno do frame do tutorial"
          >
            {trilhaPassosNavegacaoFrame.documentoForaDaJanelaNaPonta === "esquerda" ? (
              <button
                type="button"
                className="tb-anotacao-trilha-pino-documento"
                title="O frame do tutorial está à esquerda desta janela"
                aria-label="Ir para o frame do tutorial"
                disabled={processandoAlgumaAcao || carregando}
                onClick={() =>
                  void irParaInstanteSegundosNavegacaoFrameTranscribrothers(
                    instanteSegundosInicial as number,
                  )
                }
              >
                ◀
              </button>
            ) : null}
            {trilhaPassosNavegacaoFrame.tracos.map((traco, indiceTraco) => {
              const classes = ["tb-anotacao-trilha-traco"];
              if (traco.ehAtual) classes.push("tb-anotacao-trilha-traco--atual");
              if (traco.ehDocumento) classes.push("tb-anotacao-trilha-traco--documento");
              return (
                <button
                  key={`${indiceTraco}-${chaveInstanteCacheFrameNavegacaoTutorialTranscribrothers(traco.instanteSegundos)}`}
                  type="button"
                  className={classes.join(" ")}
                  aria-current={traco.ehAtual ? "true" : undefined}
                  aria-label={rotuloAcessivelTracoTrilhaNavegacaoFrameTutorialTranscribrothers(traco)}
                  title={rotuloAcessivelTracoTrilhaNavegacaoFrameTutorialTranscribrothers(traco)}
                  disabled={processandoAlgumaAcao || carregando}
                  onClick={() => void irParaInstanteSegundosNavegacaoFrameTranscribrothers(traco.instanteSegundos)}
                />
              );
            })}
            {trilhaPassosNavegacaoFrame.documentoForaDaJanelaNaPonta === "direita" ? (
              <button
                type="button"
                className="tb-anotacao-trilha-pino-documento"
                title="O frame do tutorial está à direita desta janela"
                aria-label="Ir para o frame do tutorial"
                disabled={processandoAlgumaAcao || carregando}
                onClick={() =>
                  void irParaInstanteSegundosNavegacaoFrameTranscribrothers(
                    instanteSegundosInicial as number,
                  )
                }
              >
                ▶
              </button>
            ) : null}
          </div>
        ) : null}

        <footer className="tb-anotacao-modal-rodape">
          {noSlotDocumentoNavegacao && registroAnotacao?.tem_arquivo_anotado ? (
            <div className="tb-anotacao-rodape-versao-casa">
              <div className="tb-anotacao-toggle-original-anotada" role="group" aria-label="Versão no editor">
                <button
                  type="button"
                  aria-pressed={!exibindoAnotadaNoModal}
                  disabled={acoesDocumentoDesabilitadasEnquantoCandidato}
                  onClick={() => alternarVersaoImagemExibidaSoNoEditor("original")}
                >
                  Original
                </button>
                <button
                  type="button"
                  aria-pressed={exibindoAnotadaNoModal}
                  disabled={acoesDocumentoDesabilitadasEnquantoCandidato}
                  onClick={() => alternarVersaoImagemExibidaSoNoEditor("anotado")}
                >
                  Anotada
                </button>
              </div>
              {aoRemoverAnotacaoSalva ? (
                <details className="tb-anotacao-menu-versao-casa">
                  <summary title="Mais ações da versão anotada" aria-label="Mais ações da versão anotada">
                    ⋯
                  </summary>
                  <div className="tb-anotacao-menu-versao-casa-painel">
                    {aoRemoverAnotacaoSalva ? (
                      <button
                        type="button"
                        disabled={acoesDocumentoDesabilitadasEnquantoCandidato}
                        onClick={() => {
                          void (async () => {
                            const ok = await pedirConfirmacao({
                              titulo: "Remover anotação?",
                              mensagem:
                                "Remover a versão anotada desta imagem? A captura original será mantida.",
                              rotuloConfirmar: "Remover",
                              varianteConfirmar: "destrutiva",
                            });
                            if (!ok) return;
                            void executarAcaoGestaoVersao(() =>
                              aoRemoverAnotacaoSalva(nomeArquivoOriginal),
                            );
                          })();
                        }}
                      >
                        Remover anotação
                      </button>
                    ) : null}
                  </div>
                </details>
              ) : null}
            </div>
          ) : null}
          <div className="tb-anotacao-modal-rodape-acoes-principais">
            <button
              type="button"
              className="tb-linkbtn"
              disabled={processandoAlgumaAcao}
              onClick={fecharModalDescartandoPreviewsNavegacaoTranscribrothers}
            >
              Cancelar
            </button>
            <button
              type="button"
              className="tb-primary"
              onClick={() => void usarNoTutorialOQueEstaNaTelaTranscribrothers()}
              disabled={
                processandoAlgumaAcao ||
                carregando ||
                (!noSlotDocumentoNavegacao && !podeUsarEsteFrame)
              }
              title={
                noSlotDocumentoNavegacao
                  ? "O tutorial passa a usar a versão que está na tela"
                  : "Prévia — ainda não está no documento. Grava este instante no tutorial."
              }
            >
              {salvando || aplicandoFrameNoDocumento
                ? ROTULO_BOTAO_COMMIT_USAR_NO_TUTORIAL_PROCESSANDO_MODAL_ANOTACAO_TRANSCRIBROTHERS
                : ROTULO_BOTAO_COMMIT_USAR_NO_TUTORIAL_MODAL_ANOTACAO_TRANSCRIBROTHERS}
            </button>
          </div>
        </footer>
      </div>
    </div>
    {elementoDialogoConfirmacao}
    </>
  );
}
