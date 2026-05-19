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
  IconeExcluirSelecaoAnotacaoImagemTutorialTranscribrothers,
  IconeFerramentaAnotacaoImagemTutorialTranscribrothers,
  obterRotuloAcessivelFerramentaAnotacaoImagemTutorialTranscribrothers,
} from "./componente_icones_ferramentas_anotacao_imagem_tutorial_transcribrothers.tsx";
import {
  aplicarModoZoomVisualizacaoCanvasFabricAnotacaoImagemTutorialTranscribrothers,
  exportarCanvasFabricAnotacaoComoPngDataUrlTranscribrothers,
  obterCoordenadasCanvasFabricAPartirDeEventoPonteiroAnotacaoImagemTutorialTranscribrothers,
} from "./modulo_util_zoom_visualizacao_canvas_fabric_anotacao_imagem_tutorial_transcribrothers.ts";
import type {
  FerramentaAnotacaoImagemTutorialTranscribrothers,
  ModoZoomVisualizacaoCanvasAnotacaoImagemTutorialTranscribrothers,
} from "./tipos_ferramenta_anotacao_imagem_tutorial_transcribrothers.ts";
import "./estilos_css_modal_editor_anotacao_imagem_tutorial_fabric_js_transcribrothers.css";

type ArrastoFormaAnotacaoTranscribrothers =
  | { tipo: "seta"; x1: number; y1: number; preview?: fabric.Line }
  | { tipo: "linha"; x1: number; y1: number; preview?: fabric.Line }
  | { tipo: "destaque"; x1: number; y1: number; preview?: fabric.Rect }
  | { tipo: "retangulo"; x1: number; y1: number; preview?: fabric.Rect }
  | { tipo: "elipse"; x1: number; y1: number; preview?: fabric.Ellipse };

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
  aoSalvarComSucesso: (job: JobStatus) => void;
  aoAlternarVersaoExibicaoNoTutorial?: (
    nomeArquivoOriginal: string,
    versao: "original" | "anotado",
  ) => void | Promise<void>;
  aoRemoverAnotacaoSalva?: (nomeArquivoOriginal: string) => void | Promise<void>;
  aoSincronizarMarkdownComVersaoAnotada?: (nomeArquivoOriginal: string) => void | Promise<void>;
  processandoGestaoVersoes?: boolean;
  aoSolicitarInserirImagemNoDocumentoMarkdown?: (nomeArquivoOriginal: string) => void | Promise<void>;
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
}: PropsModalEditorAnotacaoImagemTutorialTranscribrothers) {
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

  const [ferramenta, setFerramenta] = useState<FerramentaAnotacaoImagemTutorialTranscribrothers>("selecionar");
  const [corAnotacao, setCorAnotacao] = useState(COR_PADRAO_FERRAMENTAS_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS);
  const [salvando, setSalvando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [processandoGestaoLocal, setProcessandoGestaoLocal] = useState(false);
  const [versaoImagemExibidaNoModal, setVersaoImagemExibidaNoModal] =
    useState<VersaoImagemExibidaNoEditorAnotacaoModalTranscribrothers>(() =>
      resolverVersaoImagemInicialNoEditorAnotacaoModalTranscribrothers(registroAnotacao),
    );
  const [modoZoomVisualizacaoCanvas, setModoZoomVisualizacaoCanvas] =
    useState<ModoZoomVisualizacaoCanvasAnotacaoImagemTutorialTranscribrothers>("ajustarArea");

  useEffect(() => {
    setVersaoImagemExibidaNoModal(
      resolverVersaoImagemInicialNoEditorAnotacaoModalTranscribrothers(registroAnotacao),
    );
  }, [nomeArquivoOriginal]);

  useEffect(() => {
    if (!registroAnotacao?.tem_arquivo_anotado) {
      setVersaoImagemExibidaNoModal("original");
    }
  }, [registroAnotacao?.tem_arquivo_anotado]);

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

  const exibindoAnotadaNoModal = versaoImagemExibidaNoModal === "anotado";

  const processandoAlgumaAcao =
    salvando || processandoGestaoVersoes || processandoGestaoLocal;

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

  const carregarImagemFundoNoCanvasAnotacaoTranscribrothers = useCallback(
    (nomeArquivo: string) => {
      const canvas = fabricRef.current;
      if (!canvas) return;

      const geracao = ++geracaoCarregamentoImagemFundoCanvasRef.current;
      setCarregando(true);
      setErro(null);
      arrastoFormaRef.current = null;

      const url =
        urlAssetPngJobParaNomeArquivoTranscribrothers(jobId, nomeArquivo) +
        `?t=${geracao}-${encodeURIComponent(nomeArquivo)}`;

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
    [jobId, aplicarModoCanvas, sincronizarZoomVisualizacaoCanvasAnotacaoTranscribrothers],
  );

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
    carregarImagemFundoNoCanvasAnotacaoTranscribrothers(nomeArquivoBaseCanvasEdicao);
  }, [nomeArquivoBaseCanvasEdicao, carregarImagemFundoNoCanvasAnotacaoTranscribrothers]);

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
  }, [ferramenta, finalizarFerramentaDesenhoEVoltarSelecionar]);

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

  const salvar = useCallback(async () => {
    const canvas = fabricRef.current;
    if (!canvas) return;
    setSalvando(true);
    setErro(null);
    try {
      const dataUrl = exportarCanvasFabricAnotacaoComoPngDataUrlTranscribrothers(canvas);
      const resp = await fetch(dataUrl);
      const blob = await resp.blob();
      const job = await gravarPngAnotadoScreenshotTutorialJobApiTranscribrothers(
        jobId,
        nomeArquivoOriginal,
        blob,
      );
      aoSalvarComSucesso(job);
      aoFechar();
    } catch (e) {
      setErro(e instanceof Error ? e.message : String(e));
    } finally {
      setSalvando(false);
    }
  }, [aoFechar, aoSalvarComSucesso, jobId, nomeArquivoOriginal]);

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

  const alternarVersaoImagemExibidaNoModalETutorial = useCallback(
    async (versao: VersaoImagemExibidaNoEditorAnotacaoModalTranscribrothers) => {
      if (versao === "anotado" && !registroAnotacao?.tem_arquivo_anotado) {
        return;
      }
      setVersaoImagemExibidaNoModal(versao);
      if (aoAlternarVersaoExibicaoNoTutorial) {
        await executarAcaoGestaoVersao(() =>
          aoAlternarVersaoExibicaoNoTutorial(nomeArquivoOriginal, versao),
        );
      }
    },
    [
      aoAlternarVersaoExibicaoNoTutorial,
      executarAcaoGestaoVersao,
      nomeArquivoOriginal,
      registroAnotacao?.tem_arquivo_anotado,
    ],
  );

  const ferramentasBarra: FerramentaAnotacaoImagemTutorialTranscribrothers[] = [
    "selecionar",
    "destaque",
    "retangulo",
    "elipse",
    "linha",
    "seta",
    "texto",
  ];

  return (
    <div role="dialog" aria-modal="true" className="tb-anotacao-modal-overlay" onClick={aoFechar}>
      <div
        className="tb-anotacao-modal-painel"
        onClick={(e: React.MouseEvent) => e.stopPropagation()}
        role="document"
      >
        <header className="tb-anotacao-modal-cabecalho">
          <h2>Anotar screenshot</h2>
          <p className="tb-anotacao-modal-sub">
            A captura original é preservada; a versão anotada é salva em paralelo (
            <code>.anotado.png</code>). Destaque e formas vazadas: arraste para definir o tamanho.
          </p>
          <button type="button" className="tb-anotacao-modal-fechar" onClick={aoFechar} aria-label="Fechar">
            ×
          </button>
        </header>

        <div className="tb-anotacao-modal-ferramentas" role="toolbar" aria-label="Ferramentas de anotação">
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
          </div>
          <div className="tb-anotacao-ferramentas-direita tb-anotacao-ferramentas-acoes-direita">
            {aoSolicitarInserirImagemNoDocumentoMarkdown ? (
              <button
                type="button"
                className="tb-linkbtn tb-anotacao-modal-btn-inserir-documento"
                disabled={processandoAlgumaAcao || carregando}
                title="Copiar referência da imagem e escolher onde inserir no tutorial"
                onClick={() => void aoSolicitarInserirImagemNoDocumentoMarkdown(nomeArquivoOriginal)}
              >
                Inserir no documento
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
              carregando
                ? "tb-anotacao-canvas-carregando-overlay tb-anotacao-canvas-carregando-overlay--visivel"
                : "tb-anotacao-canvas-carregando-overlay"
            }
            aria-hidden={!carregando}
            aria-live="polite"
          >
            <p className="tb-anotacao-carregando">
              Carregando {exibindoAnotadaNoModal ? "versão anotada" : "captura original"}…
            </p>
          </div>
        </div>

        <div className="tb-anotacao-modal-gestao-versoes">
          <span className="tb-anotacao-modal-gestao-versoes-titulo">
            Visualização no editor e no preview do tutorial
          </span>
          <div className="tb-anotacao-modal-gestao-versoes-acoes">
            <span className="tb-badge-versao-imagem-tutorial">
              {exibindoAnotadaNoModal ? "Anotada no editor" : "Original no editor"}
            </span>
            {registroAnotacao?.tem_arquivo_anotado ? (
              <>
                <button
                  type="button"
                  className="tb-linkbtn"
                  disabled={processandoAlgumaAcao || !exibindoAnotadaNoModal}
                  onClick={() => void alternarVersaoImagemExibidaNoModalETutorial("original")}
                >
                  Ver original
                </button>
                <button
                  type="button"
                  className="tb-linkbtn"
                  disabled={processandoAlgumaAcao || exibindoAnotadaNoModal}
                  onClick={() => void alternarVersaoImagemExibidaNoModalETutorial("anotado")}
                >
                  Ver anotada
                </button>
                {aoRemoverAnotacaoSalva ? (
                  <button
                    type="button"
                    className="tb-linkbtn"
                    disabled={processandoAlgumaAcao}
                    onClick={() => {
                      if (
                        !window.confirm(
                          "Remover a versão anotada desta imagem? A captura original será mantida.",
                        )
                      ) {
                        return;
                      }
                      void executarAcaoGestaoVersao(() =>
                        aoRemoverAnotacaoSalva(nomeArquivoOriginal),
                      );
                    }}
                  >
                    Remover anotação
                  </button>
                ) : null}
                {aoSincronizarMarkdownComVersaoAnotada ? (
                  <button
                    type="button"
                    className="tb-linkbtn"
                    disabled={processandoAlgumaAcao}
                    onClick={() =>
                      void executarAcaoGestaoVersao(() =>
                        aoSincronizarMarkdownComVersaoAnotada(nomeArquivoOriginal),
                      )
                    }
                  >
                    Usar anotada no .md
                  </button>
                ) : null}
              </>
            ) : (
              <span className="tb-anotacao-modal-gestao-versoes-hint">
                Ainda não há versão anotada salva para esta imagem.
              </span>
            )}
          </div>
        </div>

        <footer className="tb-anotacao-modal-rodape">
          <div className="tb-anotacao-modal-rodape-acoes-principais">
            <button
              type="button"
              className="tb-linkbtn"
              disabled={processandoAlgumaAcao}
              onClick={aoFechar}
            >
              Cancelar
            </button>
            <button
              type="button"
              className="tb-primary"
              onClick={() => void salvar()}
              disabled={processandoAlgumaAcao || carregando}
            >
              {salvando ? "Salvando…" : "Salvar versão anotada"}
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
}
