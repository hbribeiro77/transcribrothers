import type * as React from "react";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { ComponenteDialogoConfirmacaoAcaoDestrutivaOverlayTranscribrothers } from "./componente_dialogo_confirmacao_acao_destrutiva_overlay_transcribrothers.tsx";

import ReactMarkdown from "react-markdown";

import remarkGfm from "remark-gfm";

import type { Components } from "react-markdown";

import {
  contarNumeroLinhaMarkdownAPartirOffsetCaracteresTranscribrothers,
  listarSecoesHeadingNivel2ComLinhaESlugMarkdownTutorialTranscribrothers,
  obterSecaoHeadingNivel2AtivaNaLinhaMarkdownTutorialTranscribrothers,
  type SecaoHeadingNivel2MarkdownTutorialTranscribrothers,
} from "./modulo_util_contexto_cursor_markdown_e_slug_secao_heading_nivel2_tutorial_transcribrothers.ts";

import {
  descreverTipoBlocoMarkdownNaLinhaTranscribrothers,
  obterElementoDomPreviewMarkdownParaNumeroLinhaTranscribrothers,
  obterFracaoVerticalLinhaNoViewportTextareaMarkdownTranscribrothers,
  obterLinhaTextoMarkdownTranscribrothers,
  listarAncorasBlocoMarkdownTutorialEmOrdemDocumentoTranscribrothers,
  obterNumeroLinhaBlocoAncoraAtivaNoCursorMarkdownTranscribrothers,
  obterRotuloPortuguesTipoBlocoMarkdownTranscribrothers,
  rolarContainerScrollAlinharElementoComFracaoVerticalTextareaTranscribrothers,
  rolarPreviewMarkdownProporcionalPorNumeroLinhaTranscribrothers,
  posicionarCursorTextareaNaLinhaMarkdownTranscribrothers,
  rolarTextareaMarkdownParaNumeroLinhaAproximadoTranscribrothers,
  rolarTextareaMarkdownParaNumeroLinhaComMedicaoEspelhoTranscribrothers,
  rolarTextareaMarkdownParaOffsetCaretComMedicaoEspelhoTranscribrothers,
  exibirMarcadorCaretColadoNoEspelhoTextareaMarkdownTranscribrothers,
  ocultarMarcadorCaretColadoNoEspelhoTextareaMarkdownTranscribrothers,
  type TipoBlocoMarkdownIndicadorContextoEdicaoTranscribrothers,
} from "./modulo_util_bloco_ancora_linha_markdown_sincronizacao_preview_editor_transcribrothers.ts";

import {
  extrairTextoBuscaPreviewAPartirLinhaMarkdownTranscribrothers,
  localizarTrechoPreviewMarkdownPorTextoLinhaTranscribrothers,
  obterNumeroLinhaMarkdownAPartirCliquePreviewTranscribrothers,
} from "./modulo_util_localizar_trecho_texto_linha_markdown_no_preview_sincronizacao_editor_transcribrothers.ts";

import { extrairTextoPlanoFilhosReactTranscribrothers } from "./modulo_util_extrair_texto_plano_filhos_react_para_slug_heading_transcribrothers.ts";

import {
  consumirProximaAncoraLinhaFonteMarkdownPreviewTranscribrothers,
  mesclarComponentsReactMarkdownComAncorasLinhaFonteDocumentoTranscribrothers,
} from "./modulo_util_mesclar_components_react_markdown_com_data_linha_inicio_ast_transcribrothers.tsx";

import {
  aplicarFormatacaoMarkdownNaSelecaoTextareaEdicaoTranscribrothers,
  type TipoAcaoFormatacaoMarkdownTextareaEdicaoTranscribrothers,
} from "./modulo_util_aplicar_formatacao_markdown_selecao_textarea_edicao_transcribrothers.ts";

import { ComponenteBarraFerramentasFormatacaoMarkdownEditorModalTranscribrothers } from "./componente_barra_ferramentas_formatacao_markdown_editor_modal_transcribrothers.tsx";

import { useHistoricoUndoRedoMarkdownEditorModalTranscribrothers } from "./modulo_hook_historico_undo_redo_markdown_editor_modal_transcribrothers.ts";

import { colarImagemClipboardMarkdownTutorialJobApiTranscribrothers } from "./modulo_api_colar_imagem_clipboard_markdown_tutorial_assets_job_transcribrothers.ts";

import { inserirTextoNaPosicaoCursorTextareaMarkdownTranscribrothers } from "./modulo_api_captura_frame_manual_video_tutorial_inserir_markdown_transcribrothers.ts";

import {
  eventoArrastarSoltarContemArquivoImagemEditorMarkdownTranscribrothers,
  extrairArquivoImagemDoEventoArrastarSoltarEditorMarkdownTranscribrothers,
  extrairArquivoImagemDoEventoPasteAreaTransferenciaNavegadorTranscribrothers,
  obterIndiceCaretTextareaMarkdownAPartirCoordenadasClienteTranscribrothers,
} from "./modulo_util_imagem_insercao_editor_markdown_arrastar_soltar_e_area_transferencia_transcribrothers.ts";

import type { JobStatus } from "./tipos_job_status_api_transcribrothers.ts";

import "./estilos_css_modal_edicao_markdown_tutorial_duas_colunas_preview_ao_vivo_transcribrothers.css";

const LARGURA_MAXIMA_BREAKPOINT_MOBILE_EDICAO_MARKDOWN_TUTORIAL_PX = 980;

const ATRASO_MS_DEBOUNCE_ALINHAR_PREVIEW_SECAO_CURSOR_MARKDOWN = 280;

const DURACAO_MS_PULSO_INDICADOR_BLOCO_ATIVO_PREVIEW_MARKDOWN_MODAL = 650;

const DURACAO_MS_MARCADOR_CARET_ESPELHO_APOS_CLIQUE_PREVIEW_MARKDOWN = 8000;

const DURACAO_MS_PULSO_MARCADOR_CARET_ESPELHO_PREVIEW_MARKDOWN = 2100;

/** Atalho do espelhamento manual (uma vez) editor → preview. */
const ATALHO_TECLADO_ESPELHAR_PREVIEW_UMA_VEZ_MARKDOWN_MODAL = "Ctrl+Shift+P";

const CHAVE_LOCAL_STORAGE_ESPELHAMENTO_EDITOR_PARA_PREVIEW_MARKDOWN_MODAL =
  "transcribrothers.modal-md-edit.espelhamento-editor-para-preview";

function lerPreferenciaEspelhamentoEditorParaPreviewMarkdownModalTranscribrothers(): boolean {
  try {
    return (
      localStorage.getItem(
        CHAVE_LOCAL_STORAGE_ESPELHAMENTO_EDITOR_PARA_PREVIEW_MARKDOWN_MODAL,
      ) !== "false"
    );
  } catch {
    return true;
  }
}

function persistirPreferenciaEspelhamentoEditorParaPreviewMarkdownModalTranscribrothers(
  habilitado: boolean,
): void {
  try {
    localStorage.setItem(
      CHAVE_LOCAL_STORAGE_ESPELHAMENTO_EDITOR_PARA_PREVIEW_MARKDOWN_MODAL,
      habilitado ? "true" : "false",
    );
  } catch {
    /* armazenamento indisponível */
  }
}

export type PropsComponenteModalEdicaoMarkdownTutorialDuasColunasPreviewAoVivoTranscribrothers =
  {
    valorMarkdown: string;

    aoAlterarValorMarkdown: (valor: string) => void;

    aoFechar: () => void;

    /** Markdown persistido no servidor ao abrir a modal (baseline para alterações não guardadas). */
    markdownSalvoNoServidorReferenciaParaDetectarAlteracoes: string;

    aoSalvar: () => void | Promise<void>;

    salvando: boolean;

    componentsMarkdown: Components;

    refTextareaEdicaoMarkdown: React.RefObject<HTMLTextAreaElement | null>;

    jobId: string;

    aoAtualizarJobAposInserirAssetImagemMarkdown?: (job: JobStatus) => void;

    aoNotificarToastMarkdown?: (
      mensagem: string,
      tipo: "success" | "error" | "info",
    ) => void;
  };

type ContextoPosicaoEditorMarkdownModalTranscribrothers = {
  numeroLinhaCursor: number;

  numeroLinhaBlocoAtivo: number;

  tipoBlocoAtivo: TipoBlocoMarkdownIndicadorContextoEdicaoTranscribrothers;

  secaoAtiva: SecaoHeadingNivel2MarkdownTutorialTranscribrothers | null;
};

export function ComponenteModalEdicaoMarkdownTutorialDuasColunasPreviewAoVivoTranscribrothers({
  valorMarkdown,

  aoAlterarValorMarkdown,

  aoFechar,

  markdownSalvoNoServidorReferenciaParaDetectarAlteracoes,

  aoSalvar,

  salvando,

  componentsMarkdown,

  refTextareaEdicaoMarkdown,

  jobId,

  aoAtualizarJobAposInserirAssetImagemMarkdown,

  aoNotificarToastMarkdown,
}: PropsComponenteModalEdicaoMarkdownTutorialDuasColunasPreviewAoVivoTranscribrothers) {
  const [confirmacaoDescartarAlteracoesMarkdownAberta, setConfirmacaoDescartarAlteracoesMarkdownAberta] =
    useState(false);

  const temAlteracoesMarkdownNaoSalvasNoServidor =
    valorMarkdown !== markdownSalvoNoServidorReferenciaParaDetectarAlteracoes;

  const solicitarFecharModalEdicaoMarkdownTutorialTranscribrothers = useCallback(() => {
    if (salvando) return;
    if (temAlteracoesMarkdownNaoSalvasNoServidor) {
      setConfirmacaoDescartarAlteracoesMarkdownAberta(true);
      return;
    }
    aoFechar();
  }, [aoFechar, salvando, temAlteracoesMarkdownNaoSalvasNoServidor]);

  const confirmarDescartarAlteracoesEFecharModalEdicaoMarkdownTranscribrothers = useCallback(() => {
    setConfirmacaoDescartarAlteracoesMarkdownAberta(false);
    aoFechar();
  }, [aoFechar]);

  const {
    alterarValorMarkdownComHistoricoUndoTranscribrothers,
    tratarAtalhoTecladoUndoRedoMarkdownNoTextareaTranscribrothers,
  } = useHistoricoUndoRedoMarkdownEditorModalTranscribrothers(
    valorMarkdown,
    aoAlterarValorMarkdown,
  );

  const refScrollPreviewMarkdown = useRef<HTMLDivElement | null>(null);
  const refEnvoltorioScrollPreviewMarkdown = useRef<HTMLDivElement | null>(null);
  const refEnvoltorioScrollEditorMarkdown = useRef<HTMLDivElement | null>(null);
  const marcadorCaretEspelhoPreviewAtivoRef = useRef(false);
  const timerOcultarMarcadorCaretEspelhoPreviewRef = useRef<number | null>(null);
  const timerPulsoMarcadorCaretEspelhoPreviewRef = useRef<number | null>(null);
  const refElementoBlocoAtivoDestaquePreviewMarkdown = useRef<HTMLElement | null>(null);
  const indiceHeadingN2RenderizadoPreviewRef = useRef(0);
  const indiceAncoraRenderizadoPreviewRef = useRef(0);
  const usuarioRolouPreviewManualmenteRef = useRef(false);
  const ignorarProximoScrollPreviewRef = useRef(false);
  const timerDebounceAlinharPreviewRef = useRef<number | null>(null);
  const timerPulsoIndicadorBlocoPreviewRef = useRef<number | null>(null);
  const colandoImagemClipboardMarkdownRef = useRef(false);
  const contadorArrastarImagemSobreEditorMarkdownRef = useRef(0);
  const [arrastarImagemSobreEditorMarkdown, setArrastarImagemSobreEditorMarkdown] =
    useState(false);
  /** Mantém o padding inferior de scroll extra após o primeiro alinhamento preview→editor (evita “pulo” ao sumir o marcador). */
  const [rolagemExtraInferiorEditorMarkdownPersistenteAtiva, setRolagemExtraInferiorEditorMarkdownPersistenteAtiva] =
    useState(false);
  const espelhamentoEditorParaPreviewHabilitadoRef = useRef(
    lerPreferenciaEspelhamentoEditorParaPreviewMarkdownModalTranscribrothers(),
  );

  const [
    espelhamentoEditorParaPreviewHabilitado,
    setEspelhamentoEditorParaPreviewHabilitado,
  ] = useState(() =>
    lerPreferenciaEspelhamentoEditorParaPreviewMarkdownModalTranscribrothers(),
  );

  const [painelMobileEdicaoMarkdownAtivo, setPainelMobileEdicaoMarkdownAtivo] =
    useState<"editor" | "preview">("editor");

  const [
    viewportEstreitoParaEdicaoMarkdown,
    setViewportEstreitoParaEdicaoMarkdown,
  ] = useState(
    () =>
      typeof window !== "undefined" &&
      window.innerWidth <=
        LARGURA_MAXIMA_BREAKPOINT_MOBILE_EDICAO_MARKDOWN_TUTORIAL_PX,
  );

  const [contextoPosicaoEditor, setContextoPosicaoEditor] =
    useState<ContextoPosicaoEditorMarkdownModalTranscribrothers>({
      numeroLinhaCursor: 1,

      numeroLinhaBlocoAtivo: 1,

      tipoBlocoAtivo: "paragrafo",

      secaoAtiva: null,
    });

  const secoesPreviewMarkdown = useMemo(
    () =>
      listarSecoesHeadingNivel2ComLinhaESlugMarkdownTutorialTranscribrothers(valorMarkdown),
    [valorMarkdown],
  );

  const totalLinhasMarkdownEdicao = useMemo(
    () => valorMarkdown.replace(/\r\n/g, "\n").split("\n").length,
    [valorMarkdown],
  );

  const ancorasFonteMarkdownPreview = useMemo(
    () =>
      listarAncorasBlocoMarkdownTutorialEmOrdemDocumentoTranscribrothers(valorMarkdown),
    [valorMarkdown],
  );

  const componentsMarkdownComLinhaInicioAst = useMemo(
    () =>
      mesclarComponentsReactMarkdownComAncorasLinhaFonteDocumentoTranscribrothers(
        componentsMarkdown,
        ancorasFonteMarkdownPreview,
        indiceAncoraRenderizadoPreviewRef,
      ),

    [componentsMarkdown, ancorasFonteMarkdownPreview],
  );

  useEffect(() => {
    const mediaQuery = window.matchMedia(
      `(max-width: ${LARGURA_MAXIMA_BREAKPOINT_MOBILE_EDICAO_MARKDOWN_TUTORIAL_PX}px)`,
    );

    const atualizar = () =>
      setViewportEstreitoParaEdicaoMarkdown(mediaQuery.matches);

    mediaQuery.addEventListener("change", atualizar);

    atualizar();

    return () => mediaQuery.removeEventListener("change", atualizar);
  }, []);

  const calcularContextoPosicaoEditorMarkdownTranscribrothers = useCallback(
    (
      textarea: HTMLTextAreaElement | null,
    ): ContextoPosicaoEditorMarkdownModalTranscribrothers => {
      const numeroLinhaCursor = textarea
        ? contarNumeroLinhaMarkdownAPartirOffsetCaracteresTranscribrothers(
            valorMarkdown,

            textarea.selectionStart,
          )
        : 1;

      const numeroLinhaBlocoAtivo =
        obterNumeroLinhaBlocoAncoraAtivaNoCursorMarkdownTranscribrothers(
          valorMarkdown,

          numeroLinhaCursor,
        );

      const linhaTextoBloco = obterLinhaTextoMarkdownTranscribrothers(
        valorMarkdown,

        numeroLinhaBlocoAtivo,
      );

      const tipoBlocoAtivo =
        descreverTipoBlocoMarkdownNaLinhaTranscribrothers(linhaTextoBloco);

      const secoesAtuais =
        listarSecoesHeadingNivel2ComLinhaESlugMarkdownTutorialTranscribrothers(
          valorMarkdown,
        );

      const secaoAtiva =
        obterSecaoHeadingNivel2AtivaNaLinhaMarkdownTutorialTranscribrothers(
          secoesAtuais,

          numeroLinhaCursor,
        );

      return {
        numeroLinhaCursor,

        numeroLinhaBlocoAtivo,

        tipoBlocoAtivo,

        secaoAtiva,
      };
    },

    [valorMarkdown],
  );

  const atualizarContextoAPartirTextarea = useCallback(
    (textarea: HTMLTextAreaElement | null) => {
      const proximo =
        calcularContextoPosicaoEditorMarkdownTranscribrothers(textarea);

      setContextoPosicaoEditor(proximo);

      return proximo;
    },

    [calcularContextoPosicaoEditorMarkdownTranscribrothers],
  );

  const ativarRolagemExtraInferiorPersistenteEditorMarkdownTranscribrothers = useCallback(() => {
    setRolagemExtraInferiorEditorMarkdownPersistenteAtiva(true);
  }, []);

  const ocultarMarcadorCaretEspelhoPreviewMarkdownTranscribrothers = useCallback(() => {
    marcadorCaretEspelhoPreviewAtivoRef.current = false;
    const envoltorio = refEnvoltorioScrollEditorMarkdown.current;
    const textarea = refTextareaEdicaoMarkdown.current;
    if (envoltorio) {
      envoltorio
        .querySelector<HTMLElement>("[data-tb-destaque-linha-horizontal-caret]")
        ?.remove();
      ocultarMarcadorCaretColadoNoEspelhoTextareaMarkdownTranscribrothers(
        envoltorio,
        textarea,
      );
    }
    /* Só remove o destaque visual do caret; a rolagem extra inferior permanece na sessão da modal. */
    textarea?.classList.remove("tb-modal-md-edit-textarea--caret-destaque-espelho-preview");
    if (timerOcultarMarcadorCaretEspelhoPreviewRef.current != null) {
      window.clearTimeout(timerOcultarMarcadorCaretEspelhoPreviewRef.current);
      timerOcultarMarcadorCaretEspelhoPreviewRef.current = null;
    }
    if (timerPulsoMarcadorCaretEspelhoPreviewRef.current != null) {
      window.clearTimeout(timerPulsoMarcadorCaretEspelhoPreviewRef.current);
      timerPulsoMarcadorCaretEspelhoPreviewRef.current = null;
    }
  }, []);

  const aplicarMarcadorCaretEspelhoPreviewMarkdownTranscribrothers = useCallback(() => {
    const envoltorio = refEnvoltorioScrollEditorMarkdown.current;
    const textarea = refTextareaEdicaoMarkdown.current;
    if (!envoltorio || !textarea) return;

    const offsetCaret = textarea.selectionStart;
    const exibiu = exibirMarcadorCaretColadoNoEspelhoTextareaMarkdownTranscribrothers(
      envoltorio,
      textarea,
      offsetCaret,
    );
    if (!exibiu) {
      ocultarMarcadorCaretEspelhoPreviewMarkdownTranscribrothers();
      return;
    }

    marcadorCaretEspelhoPreviewAtivoRef.current = true;
    textarea.classList.add("tb-modal-md-edit-textarea--caret-destaque-espelho-preview");

    const destaqueCaret = envoltorio.querySelector<HTMLElement>(
      "[data-tb-destaque-linha-horizontal-caret]",
    );
    destaqueCaret?.classList.add(
      "tb-modal-md-edit-espelho-caret-marcador-inline__destaque-linha-horizontal--pulso",
    );
    if (timerPulsoMarcadorCaretEspelhoPreviewRef.current != null) {
      window.clearTimeout(timerPulsoMarcadorCaretEspelhoPreviewRef.current);
    }
    timerPulsoMarcadorCaretEspelhoPreviewRef.current = window.setTimeout(() => {
      destaqueCaret?.classList.remove(
        "tb-modal-md-edit-espelho-caret-marcador-inline__destaque-linha-horizontal--pulso",
      );
    }, DURACAO_MS_PULSO_MARCADOR_CARET_ESPELHO_PREVIEW_MARKDOWN);

    if (timerOcultarMarcadorCaretEspelhoPreviewRef.current != null) {
      window.clearTimeout(timerOcultarMarcadorCaretEspelhoPreviewRef.current);
    }
    timerOcultarMarcadorCaretEspelhoPreviewRef.current = window.setTimeout(() => {
      ocultarMarcadorCaretEspelhoPreviewMarkdownTranscribrothers();
    }, DURACAO_MS_MARCADOR_CARET_ESPELHO_APOS_CLIQUE_PREVIEW_MARKDOWN);
  }, [ocultarMarcadorCaretEspelhoPreviewMarkdownTranscribrothers]);

  const aplicarIndicadorVisualBlocoAtivoPreviewMarkdownTranscribrothers = useCallback(
    (elemento: HTMLElement | null) => {
      const container = refScrollPreviewMarkdown.current;
      if (!container) return;

      container
        .querySelectorAll(".tb-modal-md-edit-bloco-ativo-cursor")
        .forEach((no) => {
          no.classList.remove(
            "tb-modal-md-edit-bloco-ativo-cursor",
            "tb-modal-md-edit-bloco-ativo-cursor--pulso",
          );
        });

      refElementoBlocoAtivoDestaquePreviewMarkdown.current = elemento;

      if (!elemento) return;

      elemento.classList.add("tb-modal-md-edit-bloco-ativo-cursor");
      elemento.classList.add("tb-modal-md-edit-bloco-ativo-cursor--pulso");

      if (timerPulsoIndicadorBlocoPreviewRef.current != null) {
        window.clearTimeout(timerPulsoIndicadorBlocoPreviewRef.current);
      }
      timerPulsoIndicadorBlocoPreviewRef.current = window.setTimeout(() => {
        elemento.classList.remove("tb-modal-md-edit-bloco-ativo-cursor--pulso");
      }, DURACAO_MS_PULSO_INDICADOR_BLOCO_ATIVO_PREVIEW_MARKDOWN_MODAL);
    },
    [],
  );

  const rolarPreviewParaContextoEditorMarkdownTranscribrothers = useCallback(
    (
      contexto: ContextoPosicaoEditorMarkdownModalTranscribrothers,

      destacar: boolean,
    ) => {
      const container = refScrollPreviewMarkdown.current;
      const envoltorio = refEnvoltorioScrollPreviewMarkdown.current;
      const textarea = refTextareaEdicaoMarkdown.current;

      if (!container) return;

      const fracaoVerticalCursorNoEditor =
        textarea != null
          ? obterFracaoVerticalLinhaNoViewportTextareaMarkdownTranscribrothers(
              textarea,
              contexto.numeroLinhaCursor,
            )
          : 0;

      ignorarProximoScrollPreviewRef.current = true;

      window.setTimeout(() => {
        ignorarProximoScrollPreviewRef.current = false;
      }, 500);

      const linhaTextoCursor = obterLinhaTextoMarkdownTranscribrothers(
        valorMarkdown,
        contexto.numeroLinhaCursor,
      );

      const textoBuscaNaLinha =
        extrairTextoBuscaPreviewAPartirLinhaMarkdownTranscribrothers(linhaTextoCursor);

      if (textoBuscaNaLinha && envoltorio) {
        const localizadoPorTexto = localizarTrechoPreviewMarkdownPorTextoLinhaTranscribrothers(
          container,
          envoltorio,
          textoBuscaNaLinha,
          {
            numeroLinhaReferencia: contexto.numeroLinhaCursor,
            totalLinhasDocumento: totalLinhasMarkdownEdicao,
          },
        );

        if (localizadoPorTexto) {
          rolarContainerScrollAlinharElementoComFracaoVerticalTextareaTranscribrothers(
            container,
            localizadoPorTexto.elemento,
            fracaoVerticalCursorNoEditor,
          );

          if (destacar) {
            aplicarIndicadorVisualBlocoAtivoPreviewMarkdownTranscribrothers(
              localizadoPorTexto.elemento,
            );
          }

          return;
        }
      }

      const elementoBloco =
        obterElementoDomPreviewMarkdownParaNumeroLinhaTranscribrothers(
          container,
          contexto.numeroLinhaBlocoAtivo,
        );

      if (elementoBloco) {
        rolarContainerScrollAlinharElementoComFracaoVerticalTextareaTranscribrothers(
          container,
          elementoBloco,
          fracaoVerticalCursorNoEditor,
        );

        if (destacar) {
          aplicarIndicadorVisualBlocoAtivoPreviewMarkdownTranscribrothers(elementoBloco);
        }

        return;
      }

      const slugSecao = contexto.secaoAtiva?.slugIdAncoraPreview;

      if (slugSecao) {
        const heading = container.querySelector<HTMLElement>(
          `#${CSS.escape(slugSecao)}`,
        );

        if (heading) {
          rolarContainerScrollAlinharElementoComFracaoVerticalTextareaTranscribrothers(
            container,
            heading,
            fracaoVerticalCursorNoEditor,
          );

          if (destacar) {
            aplicarIndicadorVisualBlocoAtivoPreviewMarkdownTranscribrothers(heading);
          }

          return;
        }
      }

      rolarPreviewMarkdownProporcionalPorNumeroLinhaTranscribrothers(
        container,
        contexto.numeroLinhaBlocoAtivo,
        totalLinhasMarkdownEdicao,
        fracaoVerticalCursorNoEditor,
      );

      if (destacar) {
        aplicarIndicadorVisualBlocoAtivoPreviewMarkdownTranscribrothers(null);
      }
    },

    [
      aplicarIndicadorVisualBlocoAtivoPreviewMarkdownTranscribrothers,
      refTextareaEdicaoMarkdown,
      totalLinhasMarkdownEdicao,
      valorMarkdown,
    ],
  );

  useEffect(() => {
    espelhamentoEditorParaPreviewHabilitadoRef.current =
      espelhamentoEditorParaPreviewHabilitado;
  }, [espelhamentoEditorParaPreviewHabilitado]);

  const sincronizarPreviewComCursorEditorMarkdownTranscribrothers = useCallback(
    (destacarBlocoNoPreview: boolean) => {
      if (!espelhamentoEditorParaPreviewHabilitadoRef.current) return;

      const textarea = refTextareaEdicaoMarkdown.current;
      const contexto = atualizarContextoAPartirTextarea(textarea);
      usuarioRolouPreviewManualmenteRef.current = false;
      rolarPreviewParaContextoEditorMarkdownTranscribrothers(contexto, destacarBlocoNoPreview);
    },
    [
      atualizarContextoAPartirTextarea,
      refTextareaEdicaoMarkdown,
      rolarPreviewParaContextoEditorMarkdownTranscribrothers,
    ],
  );

  const aoAlternarEspelhamentoEditorParaPreviewMarkdownTranscribrothers =
    useCallback(
      (habilitado: boolean) => {
        setEspelhamentoEditorParaPreviewHabilitado(habilitado);
        espelhamentoEditorParaPreviewHabilitadoRef.current = habilitado;
        persistirPreferenciaEspelhamentoEditorParaPreviewMarkdownModalTranscribrothers(
          habilitado,
        );

        if (!habilitado) {
          if (timerDebounceAlinharPreviewRef.current != null) {
            window.clearTimeout(timerDebounceAlinharPreviewRef.current);
            timerDebounceAlinharPreviewRef.current = null;
          }
          aplicarIndicadorVisualBlocoAtivoPreviewMarkdownTranscribrothers(null);
          return;
        }

        sincronizarPreviewComCursorEditorMarkdownTranscribrothers(true);
      },
      [
        aplicarIndicadorVisualBlocoAtivoPreviewMarkdownTranscribrothers,
        sincronizarPreviewComCursorEditorMarkdownTranscribrothers,
      ],
    );

  const sincronizarEditorComCliquePreviewMarkdownTranscribrothers = useCallback(
    (evento: React.MouseEvent<HTMLElement>) => {
      const alvo = evento.target;
      if (!(alvo instanceof HTMLElement)) return;

      if (
        alvo.closest("a[href]") ||
        alvo.closest("button") ||
        alvo.closest(".tb-imagem-tutorial-clicavel-anotacao") ||
        alvo.closest(".tb-imagem-tutorial-clicavel-btn-excluir")
      ) {
        return;
      }

      const container = refScrollPreviewMarkdown.current;
      const textarea = refTextareaEdicaoMarkdown.current;
      if (!container || !textarea) return;

      const numeroLinha = obterNumeroLinhaMarkdownAPartirCliquePreviewTranscribrothers(
        alvo,
        container,
        valorMarkdown,
        secoesPreviewMarkdown,
        { clientX: evento.clientX, clientY: evento.clientY },
      );

      if (numeroLinha == null) return;

      evento.preventDefault();
      usuarioRolouPreviewManualmenteRef.current = true;
      ativarRolagemExtraInferiorPersistenteEditorMarkdownTranscribrothers();

      posicionarCursorTextareaNaLinhaMarkdownTranscribrothers(
        textarea,
        valorMarkdown,
        numeroLinha,
      );

      textarea.classList.add("tb-modal-md-edit-textarea--caret-destaque-espelho-preview");

      const envoltorioEditor = refEnvoltorioScrollEditorMarkdown.current;
      if (envoltorioEditor) {
        rolarTextareaMarkdownParaOffsetCaretComMedicaoEspelhoTranscribrothers(
          envoltorioEditor,
          textarea,
          textarea.selectionStart,
        );
      } else {
        rolarTextareaMarkdownParaNumeroLinhaAproximadoTranscribrothers(textarea, numeroLinha, {
          animacaoSuave: false,
        });
      }

      const contexto = calcularContextoPosicaoEditorMarkdownTranscribrothers(textarea);
      setContextoPosicaoEditor(contexto);

      // Clique no preview: só espelha no editor (esquerda); não destacar bloco no preview.
      aplicarIndicadorVisualBlocoAtivoPreviewMarkdownTranscribrothers(null);

      window.requestAnimationFrame(() => {
        window.requestAnimationFrame(() => {
          aplicarMarcadorCaretEspelhoPreviewMarkdownTranscribrothers();
        });
      });
    },
    [
      aplicarIndicadorVisualBlocoAtivoPreviewMarkdownTranscribrothers,
      aplicarMarcadorCaretEspelhoPreviewMarkdownTranscribrothers,
      ativarRolagemExtraInferiorPersistenteEditorMarkdownTranscribrothers,
      calcularContextoPosicaoEditorMarkdownTranscribrothers,
      secoesPreviewMarkdown,
      valorMarkdown,
    ],
  );

  const alinharPreviewComCursorEditorMarkdownTranscribrothers = useCallback(
    (
      opcoes: {
        forcarMesmoSeUsuarioRolouPreview?: boolean;
        rolarEditorTambem?: boolean;
      } = {},
    ) => {
      const { forcarMesmoSeUsuarioRolouPreview = false, rolarEditorTambem = false } = opcoes;
      if (!forcarMesmoSeUsuarioRolouPreview && usuarioRolouPreviewManualmenteRef.current) {
        return;
      }
      const textarea = refTextareaEdicaoMarkdown.current;
      const contexto = atualizarContextoAPartirTextarea(textarea);
      usuarioRolouPreviewManualmenteRef.current = false;
      rolarPreviewParaContextoEditorMarkdownTranscribrothers(contexto, true);
      if (rolarEditorTambem && textarea) {
        rolarTextareaMarkdownParaNumeroLinhaAproximadoTranscribrothers(
          textarea,
          contexto.numeroLinhaCursor,
        );
      }
    },
    [
      atualizarContextoAPartirTextarea,
      refTextareaEdicaoMarkdown,
      rolarPreviewParaContextoEditorMarkdownTranscribrothers,
    ],
  );

  /** Espelha o preview no cursor atual uma única vez (não altera o switch contínuo). */
  const espelharPreviewUmaVezComCursorEditorMarkdownTranscribrothers = useCallback(
    () => {
      alinharPreviewComCursorEditorMarkdownTranscribrothers({
        forcarMesmoSeUsuarioRolouPreview: true,
        rolarEditorTambem: false,
      });
    },
    [alinharPreviewComCursorEditorMarkdownTranscribrothers],
  );

  const agendarAlinharPreviewComCursorDebouncedTranscribrothers =
    useCallback(() => {
      if (!espelhamentoEditorParaPreviewHabilitadoRef.current) return;

      if (timerDebounceAlinharPreviewRef.current != null) {
        window.clearTimeout(timerDebounceAlinharPreviewRef.current);
      }

      timerDebounceAlinharPreviewRef.current = window.setTimeout(() => {
        if (!espelhamentoEditorParaPreviewHabilitadoRef.current) return;
        alinharPreviewComCursorEditorMarkdownTranscribrothers({
          forcarMesmoSeUsuarioRolouPreview: false,
        });
      }, ATRASO_MS_DEBOUNCE_ALINHAR_PREVIEW_SECAO_CURSOR_MARKDOWN);
    }, [alinharPreviewComCursorEditorMarkdownTranscribrothers]);

  const aplicarFormatacaoMarkdownToolbarEditorTranscribrothers = useCallback(
    (acao: TipoAcaoFormatacaoMarkdownTextareaEdicaoTranscribrothers) => {
      const textarea = refTextareaEdicaoMarkdown.current;
      if (!textarea) return;

      const resultado = aplicarFormatacaoMarkdownNaSelecaoTextareaEdicaoTranscribrothers(
        valorMarkdown,
        textarea.selectionStart ?? 0,
        textarea.selectionEnd ?? 0,
        acao,
      );

      ocultarMarcadorCaretEspelhoPreviewMarkdownTranscribrothers();
      alterarValorMarkdownComHistoricoUndoTranscribrothers(resultado.novoValor);

      window.requestAnimationFrame(() => {
        textarea.focus();
        textarea.setSelectionRange(
          resultado.selectionStart,
          resultado.selectionEnd,
        );
        atualizarContextoAPartirTextarea(textarea);
        agendarAlinharPreviewComCursorDebouncedTranscribrothers();
      });
    },
    [
      agendarAlinharPreviewComCursorDebouncedTranscribrothers,
      alterarValorMarkdownComHistoricoUndoTranscribrothers,
      atualizarContextoAPartirTextarea,
      ocultarMarcadorCaretEspelhoPreviewMarkdownTranscribrothers,
      valorMarkdown,
    ],
  );

  const inserirArquivoImagemNoEditorMarkdownTranscribrothers = useCallback(
    async (
      arquivoImagem: File,
      opcoes?: { indiceCaret?: number; mensagemSucesso?: string },
    ) => {
      if (colandoImagemClipboardMarkdownRef.current) return;

      const textarea = refTextareaEdicaoMarkdown.current;
      if (!textarea) return;

      if (opcoes?.indiceCaret != null) {
        const indice = Math.max(
          0,
          Math.min(opcoes.indiceCaret, valorMarkdown.length),
        );
        textarea.focus();
        textarea.setSelectionRange(indice, indice);
      }

      colandoImagemClipboardMarkdownRef.current = true;
      try {
        const resposta = await colarImagemClipboardMarkdownTutorialJobApiTranscribrothers(
          jobId,
          arquivoImagem,
        );
        aoAtualizarJobAposInserirAssetImagemMarkdown?.(resposta.job);

        const { novoValor, novaPosicaoCursor } =
          inserirTextoNaPosicaoCursorTextareaMarkdownTranscribrothers(
            textarea,
            resposta.snippet_markdown,
            valorMarkdown,
          );
        ocultarMarcadorCaretEspelhoPreviewMarkdownTranscribrothers();
        alterarValorMarkdownComHistoricoUndoTranscribrothers(novoValor);

        window.requestAnimationFrame(() => {
          textarea.focus();
          textarea.setSelectionRange(novaPosicaoCursor, novaPosicaoCursor);
          atualizarContextoAPartirTextarea(textarea);
          if (espelhamentoEditorParaPreviewHabilitadoRef.current) {
            agendarAlinharPreviewComCursorDebouncedTranscribrothers();
          }
        });

        aoNotificarToastMarkdown?.(
          opcoes?.mensagemSucesso ?? "Imagem inserida no Markdown.",
          "success",
        );
      } catch (erro) {
        const mensagem = erro instanceof Error ? erro.message : String(erro);
        aoNotificarToastMarkdown?.(mensagem, "error");
      } finally {
        colandoImagemClipboardMarkdownRef.current = false;
      }
    },
    [
      agendarAlinharPreviewComCursorDebouncedTranscribrothers,
      alterarValorMarkdownComHistoricoUndoTranscribrothers,
      aoAtualizarJobAposInserirAssetImagemMarkdown,
      aoNotificarToastMarkdown,
      atualizarContextoAPartirTextarea,
      jobId,
      ocultarMarcadorCaretEspelhoPreviewMarkdownTranscribrothers,
      refTextareaEdicaoMarkdown,
      valorMarkdown,
    ],
  );

  const aoColarImagemClipboardNoTextareaMarkdownTranscribrothers = useCallback(
    async (evento: React.ClipboardEvent<HTMLTextAreaElement>) => {
      const arquivoImagem =
        extrairArquivoImagemDoEventoPasteAreaTransferenciaNavegadorTranscribrothers(
          evento.nativeEvent,
        );
      if (!arquivoImagem) return;

      evento.preventDefault();
      await inserirArquivoImagemNoEditorMarkdownTranscribrothers(arquivoImagem, {
        mensagemSucesso: "Imagem colada e inserida no Markdown.",
      });
    },
    [inserirArquivoImagemNoEditorMarkdownTranscribrothers],
  );

  const aoArrastarSobreEditorMarkdownTranscribrothers = useCallback(
    (evento: React.DragEvent<HTMLDivElement>) => {
      if (!eventoArrastarSoltarContemArquivoImagemEditorMarkdownTranscribrothers(evento.nativeEvent)) {
        return;
      }
      evento.preventDefault();
      evento.dataTransfer.dropEffect = "copy";
    },
    [],
  );

  const aoEntrarArrastarImagemEditorMarkdownTranscribrothers = useCallback(
    (evento: React.DragEvent<HTMLDivElement>) => {
      if (!eventoArrastarSoltarContemArquivoImagemEditorMarkdownTranscribrothers(evento.nativeEvent)) {
        return;
      }
      evento.preventDefault();
      contadorArrastarImagemSobreEditorMarkdownRef.current += 1;
      setArrastarImagemSobreEditorMarkdown(true);
    },
    [],
  );

  const aoSairArrastarImagemEditorMarkdownTranscribrothers = useCallback(
    (evento: React.DragEvent<HTMLDivElement>) => {
      if (!eventoArrastarSoltarContemArquivoImagemEditorMarkdownTranscribrothers(evento.nativeEvent)) {
        return;
      }
      contadorArrastarImagemSobreEditorMarkdownRef.current = Math.max(
        0,
        contadorArrastarImagemSobreEditorMarkdownRef.current - 1,
      );
      if (contadorArrastarImagemSobreEditorMarkdownRef.current === 0) {
        setArrastarImagemSobreEditorMarkdown(false);
      }
    },
    [],
  );

  const aoSoltarImagemNoEditorMarkdownTranscribrothers = useCallback(
    async (evento: React.DragEvent<HTMLDivElement>) => {
      const arquivoImagem = extrairArquivoImagemDoEventoArrastarSoltarEditorMarkdownTranscribrothers(
        evento.nativeEvent,
      );

      evento.preventDefault();
      contadorArrastarImagemSobreEditorMarkdownRef.current = 0;
      setArrastarImagemSobreEditorMarkdown(false);

      if (!arquivoImagem) return;

      const textarea = refTextareaEdicaoMarkdown.current;
      if (!textarea) return;

      const indiceCaret = obterIndiceCaretTextareaMarkdownAPartirCoordenadasClienteTranscribrothers(
        textarea,
        evento.clientX,
        evento.clientY,
      );

      await inserirArquivoImagemNoEditorMarkdownTranscribrothers(arquivoImagem, {
        indiceCaret,
        mensagemSucesso: "Imagem arrastada e inserida no Markdown.",
      });
    },
    [inserirArquivoImagemNoEditorMarkdownTranscribrothers, refTextareaEdicaoMarkdown],
  );

  const aoTeclarTextareaMarkdownEditorTranscribrothers = useCallback(
    (evento: React.KeyboardEvent<HTMLTextAreaElement>) => {
      ocultarMarcadorCaretEspelhoPreviewMarkdownTranscribrothers();

      if (!tratarAtalhoTecladoUndoRedoMarkdownNoTextareaTranscribrothers(evento)) {
        return;
      }

      window.requestAnimationFrame(() => {
        const textarea = refTextareaEdicaoMarkdown.current;
        if (!textarea) return;
        atualizarContextoAPartirTextarea(textarea);
        agendarAlinharPreviewComCursorDebouncedTranscribrothers();
      });
    },
    [
      agendarAlinharPreviewComCursorDebouncedTranscribrothers,
      atualizarContextoAPartirTextarea,
      ocultarMarcadorCaretEspelhoPreviewMarkdownTranscribrothers,
      refTextareaEdicaoMarkdown,
      tratarAtalhoTecladoUndoRedoMarkdownNoTextareaTranscribrothers,
    ],
  );

  useEffect(() => {
    const onKeyDown = (evento: KeyboardEvent) => {
      if (evento.key === "Escape") {
        if (confirmacaoDescartarAlteracoesMarkdownAberta) return;
        solicitarFecharModalEdicaoMarkdownTutorialTranscribrothers();
        return;
      }

      const teclaComando = evento.ctrlKey || evento.metaKey;
      if (teclaComando && evento.shiftKey) {
        const tecla = evento.key.toLowerCase();
        if (tecla === "p") {
          evento.preventDefault();
          espelharPreviewUmaVezComCursorEditorMarkdownTranscribrothers();
        }
      }
    };

    window.addEventListener("keydown", onKeyDown);

    return () => window.removeEventListener("keydown", onKeyDown);
  }, [
    confirmacaoDescartarAlteracoesMarkdownAberta,
    solicitarFecharModalEdicaoMarkdownTutorialTranscribrothers,
    espelharPreviewUmaVezComCursorEditorMarkdownTranscribrothers,
  ]);

  useEffect(() => {
    return () => {
      if (timerDebounceAlinharPreviewRef.current != null) {
        window.clearTimeout(timerDebounceAlinharPreviewRef.current);
      }

      if (timerPulsoIndicadorBlocoPreviewRef.current != null) {
        window.clearTimeout(timerPulsoIndicadorBlocoPreviewRef.current);
      }

      if (timerOcultarMarcadorCaretEspelhoPreviewRef.current != null) {
        window.clearTimeout(timerOcultarMarcadorCaretEspelhoPreviewRef.current);
      }

      if (timerPulsoMarcadorCaretEspelhoPreviewRef.current != null) {
        window.clearTimeout(timerPulsoMarcadorCaretEspelhoPreviewRef.current);
      }
    };
  }, []);

  useEffect(() => {
    const container = refScrollPreviewMarkdown.current;

    if (!container) return;

    const onScroll = () => {
      if (ignorarProximoScrollPreviewRef.current) return;
      usuarioRolouPreviewManualmenteRef.current = true;
    };

    container.addEventListener("scroll", onScroll, { passive: true });

    return () => container.removeEventListener("scroll", onScroll);
  }, [valorMarkdown]);

  useEffect(() => {
    const textarea = refTextareaEdicaoMarkdown.current;
    if (!textarea) return;

    const onScrollEditor = () => {
      if (!marcadorCaretEspelhoPreviewAtivoRef.current) return;
      aplicarMarcadorCaretEspelhoPreviewMarkdownTranscribrothers();
    };

    textarea.addEventListener("scroll", onScrollEditor, { passive: true });

    return () => textarea.removeEventListener("scroll", onScrollEditor);
  }, [aplicarMarcadorCaretEspelhoPreviewMarkdownTranscribrothers]);

  useEffect(() => {
    return () => {
      ocultarMarcadorCaretEspelhoPreviewMarkdownTranscribrothers();
    };
  }, [ocultarMarcadorCaretEspelhoPreviewMarkdownTranscribrothers]);

  useEffect(() => {
    atualizarContextoAPartirTextarea(refTextareaEdicaoMarkdown.current);
  }, [
    valorMarkdown,
    atualizarContextoAPartirTextarea,
    refTextareaEdicaoMarkdown,
  ]);

  const componentsMarkdownComAncorasSecao = useMemo((): Components => {
    const h2Original = componentsMarkdownComLinhaInicioAst.h2;

    return {
      ...componentsMarkdownComLinhaInicioAst,

      h2: (props) => {
        const indice = indiceHeadingN2RenderizadoPreviewRef.current;

        indiceHeadingN2RenderizadoPreviewRef.current += 1;

        const secao = secoesPreviewMarkdown[indice];

        const ancoraH2 = consumirProximaAncoraLinhaFonteMarkdownPreviewTranscribrothers(
          indiceAncoraRenderizadoPreviewRef,
          ancorasFonteMarkdownPreview,
        );

        const numeroLinhaAncora =
          ancoraH2?.numeroLinha ?? secao?.numeroLinha ?? null;

        const id =
          secao?.slugIdAncoraPreview ??
          (numeroLinhaAncora != null ? `tb-md-linha-${numeroLinhaAncora}` : undefined);

        const tituloExtraido = extrairTextoPlanoFilhosReactTranscribrothers(
          props.children,
        ).trim();

        const propsComAncoras = {
          ...props,

          id,

          className: [
            props.className,
            "tb-modal-md-edit-heading-ancora",
            "tb-modal-md-edit-bloco-ancora",
          ]

            .filter(Boolean)

            .join(" "),

          ...(numeroLinhaAncora != null
            ? {
                "data-tb-linha-inicio": String(numeroLinhaAncora),
                "data-tb-tipo-bloco": ancoraH2?.tipo ?? "secao-h2",
              }
            : {}),

          "data-tb-secao-titulo": tituloExtraido || secao?.titulo,
        };

        if (typeof h2Original === "function") {
          const Elemento = h2Original;

          return <Elemento {...propsComAncoras} />;
        }

        return <h2 {...propsComAncoras} />;
      },
    };
  }, [
    componentsMarkdownComLinhaInicioAst,
    secoesPreviewMarkdown,
    ancorasFonteMarkdownPreview,
  ]);

  indiceHeadingN2RenderizadoPreviewRef.current = 0;
  indiceAncoraRenderizadoPreviewRef.current = 0;

  const exibirSomentePreviewNoMobile =
    viewportEstreitoParaEdicaoMarkdown &&
    painelMobileEdicaoMarkdownAtivo === "preview";

  const exibirSomenteEditorNoMobile =
    viewportEstreitoParaEdicaoMarkdown &&
    painelMobileEdicaoMarkdownAtivo === "editor";

  const rotuloTipoBloco = obterRotuloPortuguesTipoBlocoMarkdownTranscribrothers(
    contextoPosicaoEditor.tipoBlocoAtivo,
  );

  const rotuloSecao = contextoPosicaoEditor.secaoAtiva
    ? `Seção «${contextoPosicaoEditor.secaoAtiva.titulo}»`
    : "Antes da primeira seção ##";

  const aoAbrirPreviewMobileTranscribrothers = () => {
    setPainelMobileEdicaoMarkdownAtivo("preview");

    window.requestAnimationFrame(() => {
      espelharPreviewUmaVezComCursorEditorMarkdownTranscribrothers();
    });
  };

  return (
    <>
    <div className="tb-modal-md-edit-overlay">
      <div
        className="tb-modal-md-edit-painel"
        role="dialog"
        aria-modal="true"
        aria-labelledby="tb-modal-md-edit-titulo"
        onClick={(evento) => evento.stopPropagation()}
      >
        <header className="tb-modal-md-edit-cabecalho">
          <div>
            <h2 id="tb-modal-md-edit-titulo">Editar Markdown do tutorial</h2>

            <p className="tb-modal-md-edit-sub">
              {viewportEstreitoParaEdicaoMarkdown
                ? `Edite o Markdown; «Espelhar agora» (${ATALHO_TECLADO_ESPELHAR_PREVIEW_UMA_VEZ_MARKDOWN_MODAL}) alinha o preview uma vez.`
                : `Espelhamento contínuo (switch). Espelhar agora (${ATALHO_TECLADO_ESPELHAR_PREVIEW_UMA_VEZ_MARKDOWN_MODAL}). Imagens: Ctrl+V ou arrastar para o editor.`}
            </p>
          </div>

          <button
            type="button"
            className="tb-modal-md-edit-fechar"
            aria-label="Fechar edição"
            disabled={salvando}
            onClick={solicitarFecharModalEdicaoMarkdownTutorialTranscribrothers}
          >
            ×
          </button>
        </header>

        {viewportEstreitoParaEdicaoMarkdown ? (
          <div className="tb-modal-md-edit-barra-mobile">
            {exibirSomenteEditorNoMobile ? (
              <button
                type="button"
                className="tb-linkbtn"
                onClick={aoAbrirPreviewMobileTranscribrothers}
              >
                Ver preview
              </button>
            ) : (
              <button
                type="button"
                className="tb-linkbtn"
                onClick={() => setPainelMobileEdicaoMarkdownAtivo("editor")}
              >
                Voltar ao editor
              </button>
            )}
          </div>
        ) : null}

        <div
          className={[
            "tb-modal-md-edit-corpo",

            exibirSomentePreviewNoMobile
              ? "tb-modal-md-edit-corpo--mobile-preview"
              : "",

            exibirSomenteEditorNoMobile
              ? "tb-modal-md-edit-corpo--mobile-editor"
              : "",
          ]

            .filter(Boolean)

            .join(" ")}
        >
          <div className="tb-modal-md-edit-col tb-modal-md-edit-col-editor">
            <div className="tb-modal-md-edit-col-titulo-linha tb-modal-md-edit-col-titulo-linha-editor">
              <div className="tb-modal-md-edit-col-titulo-linha-acoes-editor tb-modal-md-edit-col-titulo-linha-acoes-editor--sem-titulo-coluna">
                <ComponenteBarraFerramentasFormatacaoMarkdownEditorModalTranscribrothers
                  aoAcionarFormatacao={aplicarFormatacaoMarkdownToolbarEditorTranscribrothers}
                />

                <label
                  className="tb-modal-md-edit-switch-espelhamento-preview tb-modal-md-edit-switch-espelhamento-preview--compacto"
                  title="Espelhar preview automaticamente ao editar ou clicar no Markdown"
                  aria-label="Espelhar preview automaticamente ao editar"
                >
                  <input
                    type="checkbox"
                    role="switch"
                    className="tb-modal-md-edit-switch-espelhamento-preview-input"
                    checked={espelhamentoEditorParaPreviewHabilitado}
                    onChange={(evento) =>
                      aoAlternarEspelhamentoEditorParaPreviewMarkdownTranscribrothers(
                        evento.target.checked,
                      )
                    }
                  />
                  <span
                    className="tb-modal-md-edit-switch-espelhamento-preview-pista"
                    aria-hidden="true"
                  />
                </label>

                <button
                  type="button"
                  className="tb-modal-md-edit-barra-formatacao-btn tb-modal-md-edit-btn-espelhar-agora"
                  aria-label={`Espelhar agora — alinhar o preview ao cursor uma vez (${ATALHO_TECLADO_ESPELHAR_PREVIEW_UMA_VEZ_MARKDOWN_MODAL})`}
                  title={`Espelhar agora: alinhar o preview ao cursor uma vez (${ATALHO_TECLADO_ESPELHAR_PREVIEW_UMA_VEZ_MARKDOWN_MODAL})`}
                  onClick={espelharPreviewUmaVezComCursorEditorMarkdownTranscribrothers}
                >
                  <svg
                    className="tb-modal-md-edit-icone-espelhar-agora"
                    viewBox="0 0 16 16"
                    width="16"
                    height="16"
                    aria-hidden="true"
                    focusable="false"
                  >
                    <rect
                      x="1.5"
                      y="3"
                      width="5"
                      height="10"
                      rx="1"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.25"
                    />
                    <rect
                      x="9.5"
                      y="3"
                      width="5"
                      height="10"
                      rx="1"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.25"
                    />
                    <path
                      d="M7 8h1.2M8.1 7.1 9.2 8 8.1 8.9"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.25"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    />
                  </svg>
                </button>
              </div>
            </div>

            <p className="tb-modal-md-edit-contexto" aria-live="polite">
              <span className="tb-modal-md-edit-contexto-linha">
                Linha {contextoPosicaoEditor.numeroLinhaCursor}
              </span>

              <span
                className="tb-modal-md-edit-contexto-separador"
                aria-hidden="true"
              >
                ·
              </span>

              <span className="tb-modal-md-edit-contexto-bloco">
                {rotuloTipoBloco}
              </span>

              <span
                className="tb-modal-md-edit-contexto-separador"
                aria-hidden="true"
              >
                ·
              </span>

              <span className="tb-modal-md-edit-contexto-secao">
                {rotuloSecao}
              </span>
            </p>

            <div
              ref={refEnvoltorioScrollEditorMarkdown}
              className={[
                "tb-modal-md-edit-editor-envoltorio-scroll",
                arrastarImagemSobreEditorMarkdown
                  ? "tb-modal-md-edit-editor-envoltorio-scroll--arrastar-imagem"
                  : "",
              ]
                .filter(Boolean)
                .join(" ")}
              onDragEnter={aoEntrarArrastarImagemEditorMarkdownTranscribrothers}
              onDragLeave={aoSairArrastarImagemEditorMarkdownTranscribrothers}
              onDragOver={aoArrastarSobreEditorMarkdownTranscribrothers}
              onDrop={aoSoltarImagemNoEditorMarkdownTranscribrothers}
            >
              <textarea
                ref={refTextareaEdicaoMarkdown}
                className={[
                  "tb-input",
                  "tb-modal-md-edit-textarea",
                  rolagemExtraInferiorEditorMarkdownPersistenteAtiva
                    ? "tb-modal-md-edit-textarea--rolagem-extra-inferior-editor"
                    : "",
                ]
                  .filter(Boolean)
                  .join(" ")}
                aria-label="Editar Markdown do tutorial"
                spellCheck={false}
                value={valorMarkdown}
                onDragEnter={aoEntrarArrastarImagemEditorMarkdownTranscribrothers}
                onDragLeave={aoSairArrastarImagemEditorMarkdownTranscribrothers}
                onDragOver={aoArrastarSobreEditorMarkdownTranscribrothers}
                onDrop={aoSoltarImagemNoEditorMarkdownTranscribrothers}
                onPaste={aoColarImagemClipboardNoTextareaMarkdownTranscribrothers}
                onChange={(evento) => {
                  ocultarMarcadorCaretEspelhoPreviewMarkdownTranscribrothers();
                  alterarValorMarkdownComHistoricoUndoTranscribrothers(
                    evento.target.value,
                  );
                }}
                onClick={() => {
                  ocultarMarcadorCaretEspelhoPreviewMarkdownTranscribrothers();
                  atualizarContextoAPartirTextarea(refTextareaEdicaoMarkdown.current);
                  sincronizarPreviewComCursorEditorMarkdownTranscribrothers(true);
                }}
                onKeyDown={aoTeclarTextareaMarkdownEditorTranscribrothers}
                onKeyUp={() => {
                  atualizarContextoAPartirTextarea(refTextareaEdicaoMarkdown.current);
                  agendarAlinharPreviewComCursorDebouncedTranscribrothers();
                }}
                onSelect={() => {
                  ocultarMarcadorCaretEspelhoPreviewMarkdownTranscribrothers();
                  atualizarContextoAPartirTextarea(refTextareaEdicaoMarkdown.current);
                  agendarAlinharPreviewComCursorDebouncedTranscribrothers();
                }}
              />
            </div>
          </div>

          <div className="tb-modal-md-edit-col tb-modal-md-edit-col-preview">
            <div className="tb-modal-md-edit-col-titulo-linha tb-modal-md-edit-col-titulo-linha-preview">
              <h3 className="tb-modal-md-edit-col-titulo">Pré-visualização</h3>
              <span className="tb-modal-md-edit-preview-badge-cursor" aria-live="polite">
                Bloco · linha {contextoPosicaoEditor.numeroLinhaBlocoAtivo}
              </span>
              <span className="tb-modal-md-edit-preview-dica-clique">
                Clique em um trecho para ir à linha no Markdown
              </span>
            </div>

            <div
              ref={refEnvoltorioScrollPreviewMarkdown}
              className="tb-modal-md-edit-preview-envoltorio-scroll"
            >
              <div
                ref={refScrollPreviewMarkdown}
                className="tb-modal-md-edit-preview-scroll tb-mdwrap tb-modal-md-edit-preview-scroll--clicavel"
                role="presentation"
                onClick={sincronizarEditorComCliquePreviewMarkdownTranscribrothers}
              >
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={componentsMarkdownComAncorasSecao}
                >
                  {valorMarkdown}
                </ReactMarkdown>
              </div>
            </div>
          </div>
        </div>

        <footer className="tb-modal-md-edit-rodape">
          <button
            type="button"
            className="tb-linkbtn"
            disabled={salvando}
            onClick={solicitarFecharModalEdicaoMarkdownTutorialTranscribrothers}
          >
            Cancelar
          </button>

          <button
            type="button"
            className="tb-primary"
            disabled={salvando}
            aria-busy={salvando}
            onClick={() => void aoSalvar()}
          >
            {salvando ? "A guardar…" : "Guardar no servidor"}
          </button>
        </footer>
      </div>
    </div>

      {createPortal(
        <ComponenteDialogoConfirmacaoAcaoDestrutivaOverlayTranscribrothers
          aberto={confirmacaoDescartarAlteracoesMarkdownAberta}
          titulo="Descartar alterações?"
          mensagem="Há alterações no Markdown que ainda não foram guardadas no servidor. Se fechar agora, perderá essas mudanças."
          rotuloConfirmar="Descartar e fechar"
          rotuloCancelar="Continuar a editar"
          aoConfirmar={confirmarDescartarAlteracoesEFecharModalEdicaoMarkdownTranscribrothers}
          aoCancelar={() => setConfirmacaoDescartarAlteracoesMarkdownAberta(false)}
        />,
        document.body,
      )}
    </>
  );
}
