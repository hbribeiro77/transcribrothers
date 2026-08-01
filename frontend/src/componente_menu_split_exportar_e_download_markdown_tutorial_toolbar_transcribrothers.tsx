import { useEffect, useId, useRef, useState, type ReactNode } from "react";

import "./estilos_css_menu_split_exportar_e_download_markdown_tutorial_toolbar_transcribrothers.css";

function IconeSvgToolbarMarkdownTranscribrothers({ children }: { children: ReactNode }) {
  return (
    <svg className="tb-icone-header-toolbar" viewBox="0 0 24 24" aria-hidden="true" width="16" height="16">
      {children}
    </svg>
  );
}

/** Mesmo traço do download: janela com seta para fora (exportar / abrir fora). */
function IconeExportarDocumentoMarkdownToolbarTranscribrothers() {
  return (
    <IconeSvgToolbarMarkdownTranscribrothers>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
      />
    </IconeSvgToolbarMarkdownTranscribrothers>
  );
}

function IconeDownloadDocumentoMarkdownToolbarTranscribrothers() {
  return (
    <IconeSvgToolbarMarkdownTranscribrothers>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
      />
    </IconeSvgToolbarMarkdownTranscribrothers>
  );
}

function IconeChevronBaixoMenuSplitToolbarMarkdownTranscribrothers() {
  return (
    <IconeSvgToolbarMarkdownTranscribrothers>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2.25"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M6 9l6 6 6-6"
      />
    </IconeSvgToolbarMarkdownTranscribrothers>
  );
}

function IconeAbrirNovaAbaMenuExportarToolbarTranscribrothers() {
  return (
    <IconeSvgToolbarMarkdownTranscribrothers>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
      />
    </IconeSvgToolbarMarkdownTranscribrothers>
  );
}

function IconeGitlabMenuExportarToolbarTranscribrothers() {
  return (
    <svg className="tb-icone-header-toolbar" viewBox="0 0 24 24" aria-hidden="true" width="16" height="16">
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
      />
      <text
        x="12"
        y="16.4"
        textAnchor="middle"
        fontSize="5.25"
        fontWeight="700"
        fill="currentColor"
        fontFamily="system-ui, -apple-system, Segoe UI, Roboto, sans-serif"
      >
        GL
      </text>
    </svg>
  );
}

export type PropsComponenteMenuSplitExportarEDownloadMarkdownTutorialToolbarTranscribrothers = {
  bloqueadoPorHistoricoVersao: boolean;
  abrindoNovaAba: boolean;
  criandoIssueGitlab: boolean;
  comentandoIssueGitlab: boolean;
  anexandoDescricaoIssueGitlab: boolean;
  criandoPaginaWikiGitlab: boolean;
  baixandoMarkdown: boolean;
  baixandoPdf: boolean;
  gerandoNarracaoTts: boolean;
  urlAssetNarracaoTts: string | null;
  gerandoVideoComNarracaoTts: boolean;
  urlDownloadVideoComNarracaoTts: string | null;
  urlAssetLegendasVttAlinhadas: string | null;
  jobTemVideoEntrada: boolean;
  gitlabCriarIssueHabilitadoNoServidor: boolean;
  gitlabCriarWikiHabilitadoNoServidor: boolean;
  onAbrirTutorialMarkdownEmNovaAba: () => void;
  onAbrirModalCriarIssueGitlab: () => void;
  onAbrirModalComentarIssueGitlab: () => void;
  onAbrirModalAnexarDescricaoIssueGitlab: () => void;
  onAbrirModalCriarPaginaWikiGitlab: () => void;
  onAvisoGitlabNaoConfigurado: () => void;
  onAvisoGitlabWikiNaoConfigurado: () => void;
  onBaixarMarkdown: () => void;
  onBaixarPdf: () => void;
  onGerarNarracaoTts: () => void;
  onOuvirNarracaoTts: () => void;
  onGerarVideoComNarracaoTts: () => void;
  onBaixarVideoComNarracaoTts: () => void;
  onBaixarVideoComLegendasQueimadas?: () => void;
  baixandoVideoComLegendasQueimadas?: boolean;
  onBaixarLegendasVttAlinhadas: () => void;
};

export function ComponenteMenuSplitExportarEDownloadMarkdownTutorialToolbarTranscribrothers({
  bloqueadoPorHistoricoVersao,
  abrindoNovaAba,
  criandoIssueGitlab,
  comentandoIssueGitlab,
  anexandoDescricaoIssueGitlab,
  criandoPaginaWikiGitlab,
  baixandoMarkdown,
  baixandoPdf,
  gerandoNarracaoTts,
  urlAssetNarracaoTts,
  gerandoVideoComNarracaoTts,
  urlDownloadVideoComNarracaoTts,
  urlAssetLegendasVttAlinhadas,
  jobTemVideoEntrada,
  gitlabCriarIssueHabilitadoNoServidor,
  gitlabCriarWikiHabilitadoNoServidor,
  onAbrirTutorialMarkdownEmNovaAba,
  onAbrirModalCriarIssueGitlab,
  onAbrirModalComentarIssueGitlab,
  onAbrirModalAnexarDescricaoIssueGitlab,
  onAbrirModalCriarPaginaWikiGitlab,
  onAvisoGitlabNaoConfigurado,
  onAvisoGitlabWikiNaoConfigurado,
  onBaixarMarkdown,
  onBaixarPdf,
  onGerarNarracaoTts,
  onOuvirNarracaoTts,
  onGerarVideoComNarracaoTts,
  onBaixarVideoComNarracaoTts,
  onBaixarVideoComLegendasQueimadas,
  baixandoVideoComLegendasQueimadas = false,
  onBaixarLegendasVttAlinhadas,
}: PropsComponenteMenuSplitExportarEDownloadMarkdownTutorialToolbarTranscribrothers) {
  const menuExportarId = useId();
  const menuDownloadId = useId();
  const refExportar = useRef<HTMLDivElement | null>(null);
  const refDownload = useRef<HTMLDivElement | null>(null);
  const [menuExportarAberto, setMenuExportarAberto] = useState(false);
  const [menuDownloadAberto, setMenuDownloadAberto] = useState(false);

  const exportarOcupado =
    abrindoNovaAba ||
    criandoIssueGitlab ||
    comentandoIssueGitlab ||
    anexandoDescricaoIssueGitlab ||
    criandoPaginaWikiGitlab;
  const downloadOcupado =
    baixandoMarkdown ||
    baixandoPdf ||
    gerandoNarracaoTts ||
    gerandoVideoComNarracaoTts ||
    baixandoVideoComLegendasQueimadas;
  const exportarDesabilitado = bloqueadoPorHistoricoVersao || exportarOcupado;
  const downloadDesabilitado = bloqueadoPorHistoricoVersao || downloadOcupado;

  const tituloBloqueioHistorico =
    "Volte à versão atual no cabeçalho do documento (▼) para exportar ou baixar a versão do servidor.";

  useEffect(() => {
    if (!menuExportarAberto && !menuDownloadAberto) return;
    const fecharMenus = () => {
      setMenuExportarAberto(false);
      setMenuDownloadAberto(false);
    };
    const fecharSeCliqueFora = (evento: MouseEvent) => {
      const alvo = evento.target;
      if (!(alvo instanceof Node)) return;
      if (refExportar.current?.contains(alvo) || refDownload.current?.contains(alvo)) return;
      fecharMenus();
    };
    const fecharSeEscape = (evento: KeyboardEvent) => {
      if (evento.key === "Escape") fecharMenus();
    };
    document.addEventListener("mousedown", fecharSeCliqueFora);
    window.addEventListener("keydown", fecharSeEscape);
    return () => {
      document.removeEventListener("mousedown", fecharSeCliqueFora);
      window.removeEventListener("keydown", fecharSeEscape);
    };
  }, [menuExportarAberto, menuDownloadAberto]);

  useEffect(() => {
    const fecharMenus = () => {
      setMenuExportarAberto(false);
      setMenuDownloadAberto(false);
    };
    if (exportarOcupado || downloadOcupado) fecharMenus();
  }, [exportarOcupado, downloadOcupado]);

  function alternarMenuExportar() {
    if (exportarDesabilitado) return;
    setMenuDownloadAberto(false);
    setMenuExportarAberto((v) => !v);
  }

  function alternarMenuDownload() {
    if (downloadDesabilitado) return;
    setMenuExportarAberto(false);
    setMenuDownloadAberto((v) => !v);
  }

  function executarExportarNovaAba() {
    setMenuExportarAberto(false);
    onAbrirTutorialMarkdownEmNovaAba();
  }

  function executarExportarGitlabIssue() {
    setMenuExportarAberto(false);
    if (!gitlabCriarIssueHabilitadoNoServidor) {
      onAvisoGitlabNaoConfigurado();
      return;
    }
    onAbrirModalCriarIssueGitlab();
  }

  function executarComentarGitlabIssue() {
    setMenuExportarAberto(false);
    if (!gitlabCriarIssueHabilitadoNoServidor) {
      onAvisoGitlabNaoConfigurado();
      return;
    }
    onAbrirModalComentarIssueGitlab();
  }

  function executarAnexarDescricaoGitlabIssue() {
    setMenuExportarAberto(false);
    if (!gitlabCriarIssueHabilitadoNoServidor) {
      onAvisoGitlabNaoConfigurado();
      return;
    }
    onAbrirModalAnexarDescricaoIssueGitlab();
  }

  function executarExportarGitlabWiki() {
    setMenuExportarAberto(false);
    if (!gitlabCriarWikiHabilitadoNoServidor) {
      onAvisoGitlabWikiNaoConfigurado();
      return;
    }
    onAbrirModalCriarPaginaWikiGitlab();
  }

  function executarDownloadMd() {
    setMenuDownloadAberto(false);
    onBaixarMarkdown();
  }

  function executarDownloadPdf() {
    setMenuDownloadAberto(false);
    onBaixarPdf();
  }

  function executarGerarNarracaoTts() {
    setMenuDownloadAberto(false);
    onGerarNarracaoTts();
  }

  function executarOuvirNarracaoTts() {
    setMenuDownloadAberto(false);
    onOuvirNarracaoTts();
  }

  function executarGerarVideoComNarracaoTts() {
    setMenuDownloadAberto(false);
    onGerarVideoComNarracaoTts();
  }

  function executarBaixarVideoComNarracaoTts() {
    setMenuDownloadAberto(false);
    onBaixarVideoComNarracaoTts();
  }

  function executarBaixarVideoComLegendasQueimadas() {
    setMenuDownloadAberto(false);
    onBaixarVideoComLegendasQueimadas?.();
  }

  function executarBaixarLegendasVttAlinhadas() {
    setMenuDownloadAberto(false);
    onBaixarLegendasVttAlinhadas();
  }

  return (
    <>
      <div
        ref={refDownload}
        className={`tb-toolbar-split tb-toolbar-split--download${menuDownloadAberto ? " tb-toolbar-split--aberto" : ""}`}
      >
        <div className="tb-toolbar-split-botoes">
          <button
            type="button"
            className="tb-toolbar-split-principal"
            disabled={downloadDesabilitado}
            title={
              bloqueadoPorHistoricoVersao
                ? tituloBloqueioHistorico
                : downloadOcupado
                  ? "Download em andamento…"
                  : "Baixar documento"
            }
            aria-label="Baixar documento"
            aria-haspopup="menu"
            aria-expanded={menuDownloadAberto}
            aria-controls={menuDownloadId}
            onClick={alternarMenuDownload}
          >
            <IconeDownloadDocumentoMarkdownToolbarTranscribrothers />
          </button>
          <button
            type="button"
            className="tb-toolbar-split-caret"
            disabled={downloadDesabilitado}
            title="Opções de download"
            aria-label="Abrir menu de download"
            aria-haspopup="menu"
            aria-expanded={menuDownloadAberto}
            aria-controls={menuDownloadId}
            onClick={alternarMenuDownload}
          >
            <IconeChevronBaixoMenuSplitToolbarMarkdownTranscribrothers />
          </button>
        </div>
        {menuDownloadAberto ? (
          <ul id={menuDownloadId} className="tb-toolbar-split-menu" role="menu">
            <li role="none">
              <button
                type="button"
                className="tb-toolbar-split-menu-item tb-toolbar-split-menu-item--com-detalhe"
                role="menuitem"
                disabled={downloadDesabilitado}
                aria-busy={baixandoMarkdown}
                onClick={() => void executarDownloadMd()}
              >
                <span className="tb-toolbar-split-menu-item-rotulo-principal">Arquivo Markdown</span>
                <span className="tb-muted tb-toolbar-split-menu-item-detalhe">.md com imagens embutidas</span>
              </button>
            </li>
            <li role="none">
              <button
                type="button"
                className="tb-toolbar-split-menu-item tb-toolbar-split-menu-item--com-detalhe tb-toolbar-split-menu-item--pdf"
                role="menuitem"
                disabled={downloadDesabilitado}
                aria-busy={baixandoPdf}
                onClick={() => void executarDownloadPdf()}
              >
                <span className="tb-toolbar-split-menu-item-rotulo-principal">PDF</span>
                <span className="tb-muted tb-toolbar-split-menu-item-detalhe">imagens incluídas</span>
              </button>
            </li>
            <li role="none">
              <button
                type="button"
                className="tb-toolbar-split-menu-item tb-toolbar-split-menu-item--com-detalhe"
                role="menuitem"
                disabled={downloadDesabilitado}
                aria-busy={gerandoNarracaoTts}
                onClick={() => void executarGerarNarracaoTts()}
              >
                <span className="tb-toolbar-split-menu-item-rotulo-principal">
                  {urlAssetNarracaoTts ? "Regenerar narração (áudio)" : "Gerar narração (áudio)"}
                </span>
                <span className="tb-muted tb-toolbar-split-menu-item-detalhe">
                  TTS do Markdown · modelo com -tts
                </span>
              </button>
            </li>
            {urlAssetNarracaoTts ? (
              <li role="none">
                <button
                  type="button"
                  className="tb-toolbar-split-menu-item tb-toolbar-split-menu-item--com-detalhe"
                  role="menuitem"
                  disabled={bloqueadoPorHistoricoVersao || gerandoNarracaoTts}
                  onClick={() => void executarOuvirNarracaoTts()}
                >
                  <span className="tb-toolbar-split-menu-item-rotulo-principal">Ouvir / baixar narração</span>
                  <span className="tb-muted tb-toolbar-split-menu-item-detalhe">WAV gerado no servidor</span>
                </button>
              </li>
            ) : null}
            {jobTemVideoEntrada ? (
              <li role="none">
                <button
                  type="button"
                  className="tb-toolbar-split-menu-item tb-toolbar-split-menu-item--com-detalhe"
                  role="menuitem"
                  disabled={downloadDesabilitado || !urlAssetNarracaoTts}
                  aria-busy={gerandoVideoComNarracaoTts}
                  title={
                    urlAssetNarracaoTts
                      ? "Cria uma cópia do vídeo com a narração TTS no lugar do áudio original"
                      : "Gere a narração de áudio antes"
                  }
                  onClick={() => void executarGerarVideoComNarracaoTts()}
                >
                  <span className="tb-toolbar-split-menu-item-rotulo-principal">
                    {urlDownloadVideoComNarracaoTts
                      ? "Regenerar vídeo com narração"
                      : "Gerar vídeo com narração"}
                  </span>
                  <span className="tb-muted tb-toolbar-split-menu-item-detalhe">
                    troca o áudio do vídeo pelo TTS
                  </span>
                </button>
              </li>
            ) : null}
            {urlDownloadVideoComNarracaoTts ? (
              <li role="none">
                <button
                  type="button"
                  className="tb-toolbar-split-menu-item tb-toolbar-split-menu-item--com-detalhe"
                  role="menuitem"
                  disabled={bloqueadoPorHistoricoVersao || gerandoVideoComNarracaoTts}
                  onClick={() => void executarBaixarVideoComNarracaoTts()}
                >
                  <span className="tb-toolbar-split-menu-item-rotulo-principal">Baixar vídeo com narração</span>
                  <span className="tb-muted tb-toolbar-split-menu-item-detalhe">MP4 gerado no servidor</span>
                </button>
              </li>
            ) : null}
            {urlDownloadVideoComNarracaoTts && urlAssetLegendasVttAlinhadas && onBaixarVideoComLegendasQueimadas ? (
              <li role="none">
                <button
                  type="button"
                  className="tb-toolbar-split-menu-item tb-toolbar-split-menu-item--com-detalhe"
                  role="menuitem"
                  disabled={
                    bloqueadoPorHistoricoVersao ||
                    gerandoVideoComNarracaoTts ||
                    baixandoVideoComLegendasQueimadas
                  }
                  aria-busy={baixandoVideoComLegendasQueimadas}
                  title="Reencode sob demanda: legendas desenhadas no vídeo (aparecem em qualquer player)"
                  onClick={() => void executarBaixarVideoComLegendasQueimadas()}
                >
                  <span className="tb-toolbar-split-menu-item-rotulo-principal">
                    {baixandoVideoComLegendasQueimadas
                      ? "Gerando vídeo com legendas…"
                      : "Baixar vídeo com legendas embutidas"}
                  </span>
                  <span className="tb-muted tb-toolbar-split-menu-item-detalhe">
                    MP4 com legendas queimadas na imagem
                  </span>
                </button>
              </li>
            ) : null}
            {urlAssetLegendasVttAlinhadas ? (
              <li role="none">
                <button
                  type="button"
                  className="tb-toolbar-split-menu-item tb-toolbar-split-menu-item--com-detalhe"
                  role="menuitem"
                  disabled={bloqueadoPorHistoricoVersao}
                  onClick={() => void executarBaixarLegendasVttAlinhadas()}
                >
                  <span className="tb-toolbar-split-menu-item-rotulo-principal">Baixar legendas (VTT)</span>
                  <span className="tb-muted tb-toolbar-split-menu-item-detalhe">
                    alinhadas ao documento e à transcrição
                  </span>
                </button>
              </li>
            ) : null}
          </ul>
        ) : null}
      </div>

      <div
        ref={refExportar}
        className={`tb-toolbar-split tb-toolbar-split--exportar${menuExportarAberto ? " tb-toolbar-split--aberto" : ""}`}
      >
        <div className="tb-toolbar-split-botoes">
          <button
            type="button"
            className="tb-toolbar-split-principal"
            disabled={exportarDesabilitado}
            title={
              bloqueadoPorHistoricoVersao
                ? tituloBloqueioHistorico
                : exportarOcupado
                  ? "Exportação em andamento…"
                  : "Exportar documento"
            }
            aria-label="Exportar documento"
            aria-haspopup="menu"
            aria-expanded={menuExportarAberto}
            aria-controls={menuExportarId}
            onClick={alternarMenuExportar}
          >
            <IconeExportarDocumentoMarkdownToolbarTranscribrothers />
          </button>
          <button
            type="button"
            className="tb-toolbar-split-caret"
            disabled={exportarDesabilitado}
            title="Opções de exportação"
            aria-label="Abrir menu de exportação"
            aria-haspopup="menu"
            aria-expanded={menuExportarAberto}
            aria-controls={menuExportarId}
            onClick={alternarMenuExportar}
          >
            <IconeChevronBaixoMenuSplitToolbarMarkdownTranscribrothers />
          </button>
        </div>
        {menuExportarAberto ? (
          <ul id={menuExportarId} className="tb-toolbar-split-menu" role="menu">
            <li role="none">
              <button
                type="button"
                className="tb-toolbar-split-menu-item"
                role="menuitem"
                disabled={exportarDesabilitado}
                onClick={() => void executarExportarNovaAba()}
              >
                <IconeAbrirNovaAbaMenuExportarToolbarTranscribrothers />
                <span>Abrir em nova aba</span>
              </button>
            </li>
            <li role="none">
              <button
                type="button"
                className="tb-toolbar-split-menu-item tb-toolbar-split-menu-item--gitlab"
                role="menuitem"
                disabled={exportarDesabilitado}
                onClick={() => executarExportarGitlabIssue()}
              >
                <IconeGitlabMenuExportarToolbarTranscribrothers />
                <span>Criar issue no GitLab</span>
              </button>
            </li>
            <li role="none">
              <button
                type="button"
                className="tb-toolbar-split-menu-item tb-toolbar-split-menu-item--gitlab"
                role="menuitem"
                disabled={exportarDesabilitado}
                onClick={() => executarComentarGitlabIssue()}
              >
                <IconeGitlabMenuExportarToolbarTranscribrothers />
                <span>Comentar em issue do GitLab</span>
              </button>
            </li>
            <li role="none">
              <button
                type="button"
                className="tb-toolbar-split-menu-item tb-toolbar-split-menu-item--gitlab"
                role="menuitem"
                disabled={exportarDesabilitado}
                onClick={() => executarAnexarDescricaoGitlabIssue()}
              >
                <IconeGitlabMenuExportarToolbarTranscribrothers />
                <span>Adicionar à descrição da issue</span>
              </button>
            </li>
            <li role="none">
              <button
                type="button"
                className="tb-toolbar-split-menu-item tb-toolbar-split-menu-item--gitlab"
                role="menuitem"
                disabled={exportarDesabilitado}
                onClick={() => executarExportarGitlabWiki()}
              >
                <IconeGitlabMenuExportarToolbarTranscribrothers />
                <span>Publicar na wiki (workshop/…)</span>
              </button>
            </li>
          </ul>
        ) : null}
      </div>
    </>
  );
}
