import { useEffect, useId, useState } from "react";
import { createPortal } from "react-dom";
import { previewUrlPaginaWikiGitlabDocumentacaoApiTranscribrothers } from "./modulo_api_preview_url_pagina_wiki_gitlab_documentacao_transcribrothers.ts";

export type PropsComponenteModalConfirmarCriarPaginaWikiGitlabDocumentoMarkdownTranscribrothers = {
  aberto: boolean;
  tituloInicial: string;
  jobId: string;
  projetoGitlab: string;
  prefixoPastaWikiPadrao: string;
  wikiHabilitadaNoServidor: boolean;
  tamanhoConteudoCaracteres: number;
  quantidadeReferenciasImagensAssetsPng: number;
  processando: boolean;
  onFechar: () => void;
  onConfirmar: (
    titulo: string,
    incluirImagensPngMarkdown: boolean,
    prefixoPastaWiki: string,
  ) => void;
};

export function ComponenteModalConfirmarCriarPaginaWikiGitlabDocumentoMarkdownTranscribrothers({
  aberto,
  tituloInicial,
  jobId,
  projetoGitlab,
  prefixoPastaWikiPadrao,
  wikiHabilitadaNoServidor,
  tamanhoConteudoCaracteres,
  quantidadeReferenciasImagensAssetsPng,
  processando,
  onFechar,
  onConfirmar,
}: PropsComponenteModalConfirmarCriarPaginaWikiGitlabDocumentoMarkdownTranscribrothers) {
  const tituloId = useId();
  const checkboxImagensId = useId();
  const urlPrevistaId = useId();
  const diretorioWikiId = useId();
  const [titulo, setTitulo] = useState(tituloInicial);
  const [nomeDiretorioWiki, setNomeDiretorioWiki] = useState(prefixoPastaWikiPadrao);
  const [incluirImagensPngMarkdown, setIncluirImagensPngMarkdown] = useState(true);
  const [urlPrevista, setUrlPrevista] = useState<string | null>(null);
  const [urlIndicePasta, setUrlIndicePasta] = useState<string | null>(null);
  const [paginaJaExiste, setPaginaJaExiste] = useState<boolean | null>(null);
  const [carregandoUrlPrevista, setCarregandoUrlPrevista] = useState(false);
  const [erroUrlPrevista, setErroUrlPrevista] = useState<string | null>(null);

  useEffect(() => {
    if (!aberto) return;
    setTitulo(tituloInicial);
    setNomeDiretorioWiki(prefixoPastaWikiPadrao);
    setIncluirImagensPngMarkdown(quantidadeReferenciasImagensAssetsPng > 0);
    setUrlPrevista(null);
    setUrlIndicePasta(null);
    setPaginaJaExiste(null);
    setErroUrlPrevista(null);
  }, [aberto, tituloInicial, prefixoPastaWikiPadrao, quantidadeReferenciasImagensAssetsPng]);

  useEffect(() => {
    if (!aberto) return;
    const aoTeclar = (evento: KeyboardEvent) => {
      if (evento.key === "Escape" && !processando) onFechar();
    };
    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
  }, [aberto, onFechar, processando]);

  useEffect(() => {
    if (!aberto || !wikiHabilitadaNoServidor || !jobId.trim()) {
      setUrlPrevista(null);
      setUrlIndicePasta(null);
      setPaginaJaExiste(null);
      setErroUrlPrevista(null);
      setCarregandoUrlPrevista(false);
      return;
    }

    const tituloTrim = titulo.trim();
    const pastaTrim = nomeDiretorioWiki.trim();
    if (!tituloTrim || !pastaTrim) {
      setUrlPrevista(null);
      setUrlIndicePasta(null);
      setPaginaJaExiste(null);
      return;
    }

    setUrlPrevista(null);
    setUrlIndicePasta(null);
    setPaginaJaExiste(null);
    setCarregandoUrlPrevista(true);
    setErroUrlPrevista(null);

    let cancelado = false;
    const timer = window.setTimeout(() => {
      void (async () => {
        try {
          const resp = await previewUrlPaginaWikiGitlabDocumentacaoApiTranscribrothers({
            titulo: tituloTrim,
            jobId,
            prefixoPastaWiki: pastaTrim,
          });
          if (cancelado) return;
          setUrlPrevista(resp.web_url);
          setUrlIndicePasta(resp.web_url_indice_workshop);
          setPaginaJaExiste(resp.pagina_destino_ja_existe_no_gitlab);
          if (resp.prefixo_pasta_wiki && resp.prefixo_pasta_wiki !== pastaTrim) {
            setNomeDiretorioWiki(resp.prefixo_pasta_wiki);
          }
          setErroUrlPrevista(null);
        } catch (e) {
          if (cancelado) return;
          setUrlPrevista(null);
          setUrlIndicePasta(null);
          setPaginaJaExiste(null);
          setErroUrlPrevista(e instanceof Error ? e.message : String(e));
        } finally {
          if (!cancelado) setCarregandoUrlPrevista(false);
        }
      })();
    }, 350);

    return () => {
      cancelado = true;
      window.clearTimeout(timer);
    };
  }, [aberto, wikiHabilitadaNoServidor, jobId, titulo, nomeDiretorioWiki]);

  if (!aberto) return null;

  const tituloTrim = titulo.trim();
  const pastaTrim = nomeDiretorioWiki.trim();
  const pasta = pastaTrim || "workshop";
  const podeConfirmar =
    tituloTrim.length > 0 &&
    tituloTrim.length <= 255 &&
    pastaTrim.length > 0 &&
    tamanhoConteudoCaracteres > 0 &&
    wikiHabilitadaNoServidor &&
    Boolean(jobId.trim()) &&
    Boolean(urlPrevista) &&
    urlPrevista.includes(`/-/wikis/${pasta}/`) &&
    !carregandoUrlPrevista &&
    !erroUrlPrevista;

  return createPortal(
    <div className="tb-modal-job-root" role="presentation">
      <button
        type="button"
        className="tb-modal-job-backdrop"
        aria-label="Fechar"
        disabled={processando}
        onClick={onFechar}
      />
      <div className="tb-modal-job-shell">
        <div
          className="tb-modal-job tb-modal-criar-issue-gitlab"
          role="dialog"
          aria-modal="true"
          aria-labelledby={tituloId}
        >
          <h2 id={tituloId} className="tb-modal-job-titulo">
            Exportar para wiki do GitLab ({pasta}/…)
          </h2>
          <p className="tb-muted tb-modal-criar-issue-gitlab-lead">
            Publica na subpágina abaixo em{" "}
            <code>{projetoGitlab || "portal-da-defensoria/documentacao"}</code>. A página índice{" "}
            <strong>{pasta}</strong> (que já existe) e as demais páginas da wiki{" "}
            <strong>não são alteradas</strong>. Se a subpágina ainda não existir, ela será criada em{" "}
            <strong>{pasta}/…</strong>, nunca na raiz da wiki.
          </p>
          <label className="tb-modal-criar-issue-gitlab-campo" htmlFor={diretorioWikiId}>
            <span className="tb-modal-criar-issue-gitlab-rotulo">Pasta wiki (diretório)</span>
            <input
              id={diretorioWikiId}
              type="text"
              className="tb-input"
              maxLength={64}
              value={nomeDiretorioWiki}
              disabled={processando}
              placeholder="workshop"
              onChange={(e) => setNomeDiretorioWiki(e.target.value)}
            />
            <span className="tb-muted tb-modal-criar-issue-gitlab-contador">
              Sugestão: <code>{prefixoPastaWikiPadrao || "workshop"}</code> — pode alterar para outra
              pasta existente na wiki.
            </span>
          </label>
          <div className="tb-modal-criar-wiki-gitlab-url-prevista" aria-live="polite">
            <span className="tb-modal-criar-issue-gitlab-rotulo" id={urlPrevistaId}>
              Subpágina de destino
            </span>
            {!wikiHabilitadaNoServidor ? (
              <p className="tb-muted tb-modal-criar-wiki-gitlab-url-prevista-texto">
                Configure o GitLab no servidor para ver a URL.
              </p>
            ) : carregandoUrlPrevista ? (
              <p className="tb-muted tb-modal-criar-wiki-gitlab-url-prevista-texto">
                Carregando URL…
              </p>
            ) : erroUrlPrevista ? (
              <p className="tb-modal-criar-wiki-gitlab-url-prevista-erro">{erroUrlPrevista}</p>
            ) : urlPrevista ? (
              <>
                <a
                  href={urlPrevista}
                  className="tb-modal-criar-wiki-gitlab-url-prevista-link"
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-describedby={urlPrevistaId}
                >
                  {urlPrevista}
                </a>
                {!urlPrevista.includes(`/-/wikis/${pasta}/`) ? (
                  <p className="tb-modal-criar-wiki-gitlab-url-prevista-erro" role="alert">
                    A URL não corresponde à pasta <strong>{pasta}</strong>. Aguarde o carregamento
                    ou confira o nome do diretório.
                  </p>
                ) : null}
                {paginaJaExiste === false ? (
                  <p className="tb-muted tb-modal-criar-wiki-gitlab-url-prevista-texto" role="status">
                    Subpágina nova — será criada em <strong>{pasta}/…</strong> (
                    {tamanhoConteudoCaracteres.toLocaleString("pt-BR")} caracteres). O índice{" "}
                    {pasta}{" "}
                    {urlIndicePasta ? (
                      <a href={urlIndicePasta} target="_blank" rel="noopener noreferrer">
                        continua igual
                      </a>
                    ) : (
                      "continua igual"
                    )}
                    .
                  </p>
                ) : paginaJaExiste === true ? (
                  <p className="tb-muted tb-modal-criar-wiki-gitlab-url-prevista-texto">
                    Subpágina já existe — a exportação atualiza o Markdown desta URL (
                    {tamanhoConteudoCaracteres.toLocaleString("pt-BR")} caracteres).
                  </p>
                ) : null}
              </>
            ) : null}
          </div>
          <label className="tb-modal-criar-issue-gitlab-checkbox-imagens" htmlFor={checkboxImagensId}>
            <input
              id={checkboxImagensId}
              type="checkbox"
              checked={incluirImagensPngMarkdown}
              disabled={processando || quantidadeReferenciasImagensAssetsPng === 0}
              onChange={(e) => setIncluirImagensPngMarkdown(e.target.checked)}
            />
            <span>
              Enviar imagens referenciadas em <code>assets/</code> para a wiki (
              {quantidadeReferenciasImagensAssetsPng} no documento)
              {quantidadeReferenciasImagensAssetsPng === 0
                ? " — nenhuma referência PNG encontrada."
                : " — cada PNG será anexada e o link no Markdown apontará para uploads/… na wiki."}
            </span>
          </label>
          <label className="tb-modal-criar-issue-gitlab-campo">
            <span className="tb-modal-criar-issue-gitlab-rotulo">Título exibido na página wiki</span>
            <input
              type="text"
              className="tb-input"
              maxLength={255}
              value={titulo}
              disabled={processando}
              onChange={(e) => setTitulo(e.target.value)}
            />
            <span className="tb-muted tb-modal-criar-issue-gitlab-contador">
              {titulo.trim().length}/255
            </span>
          </label>
          <footer className="tb-modal-job-rodape tb-modal-criar-issue-gitlab-rodape">
            <button type="button" className="tb-secondary" disabled={processando} onClick={onFechar}>
              Cancelar
            </button>
            <button
              type="button"
              className="tb-primary"
              disabled={!podeConfirmar || processando}
              aria-busy={processando}
              onClick={() => onConfirmar(tituloTrim, incluirImagensPngMarkdown, pastaTrim)}
            >
              {processando
                ? "Publicando…"
                : paginaJaExiste
                  ? "Atualizar subpágina"
                  : "Criar subpágina"}
            </button>
          </footer>
        </div>
      </div>
    </div>,
    document.body,
  );
}
