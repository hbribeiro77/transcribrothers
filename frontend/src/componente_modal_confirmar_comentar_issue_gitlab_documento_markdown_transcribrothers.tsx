import { useEffect, useId, useState } from "react";
import { createPortal } from "react-dom";

export type PropsComponenteModalConfirmarComentarIssueGitlabDocumentoMarkdownTranscribrothers = {
  aberto: boolean;
  tamanhoComentarioCaracteres: number;
  quantidadeReferenciasImagensAssetsPng: number;
  processando: boolean;
  onFechar: () => void;
  onConfirmar: (issueUrl: string, incluirImagensPngMarkdown: boolean) => void;
};

export function ComponenteModalConfirmarComentarIssueGitlabDocumentoMarkdownTranscribrothers({
  aberto,
  tamanhoComentarioCaracteres,
  quantidadeReferenciasImagensAssetsPng,
  processando,
  onFechar,
  onConfirmar,
}: PropsComponenteModalConfirmarComentarIssueGitlabDocumentoMarkdownTranscribrothers) {
  const tituloId = useId();
  const issueUrlId = useId();
  const checkboxImagensId = useId();
  const [issueUrl, setIssueUrl] = useState("");
  const [incluirImagensPngMarkdown, setIncluirImagensPngMarkdown] = useState(true);

  useEffect(() => {
    if (!aberto) return;
    setIssueUrl("");
    setIncluirImagensPngMarkdown(quantidadeReferenciasImagensAssetsPng > 0);
  }, [aberto, quantidadeReferenciasImagensAssetsPng]);

  useEffect(() => {
    if (!aberto) return;
    const aoTeclar = (evento: KeyboardEvent) => {
      if (evento.key === "Escape" && !processando) onFechar();
    };
    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
  }, [aberto, onFechar, processando]);

  if (!aberto) return null;

  const issueUrlTrim = issueUrl.trim();
  const pareceUrlIssueGitlab = /^https?:\/\/.+\/-\/issues\/\d+(?:[/?#].*)?$/i.test(issueUrlTrim);
  const podeConfirmar = pareceUrlIssueGitlab && tamanhoComentarioCaracteres > 0;

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
            Comentar em issue do GitLab
          </h2>
          <p className="tb-muted tb-modal-criar-issue-gitlab-lead">
            O Markdown completo do documento ({tamanhoComentarioCaracteres.toLocaleString("pt-BR")}{" "}
            caracteres) será publicado como <strong>comentário</strong> na issue informada. A URL
            precisa pertencer ao GitLab configurado no servidor.
          </p>
          <label className="tb-modal-criar-issue-gitlab-campo" htmlFor={issueUrlId}>
            <span className="tb-modal-criar-issue-gitlab-rotulo">URL completa da issue</span>
            <input
              id={issueUrlId}
              type="url"
              className="tb-input"
              value={issueUrl}
              disabled={processando}
              placeholder="https://gitlab.defpub.local/grupo/projeto/-/issues/123"
              onChange={(e) => setIssueUrl(e.target.value)}
            />
            <span className="tb-muted tb-modal-criar-issue-gitlab-contador">
              Cole a URL da issue de destino. O servidor validará se ela pertence ao GitLab configurado.
            </span>
          </label>
          <label className="tb-modal-criar-issue-gitlab-checkbox-imagens" htmlFor={checkboxImagensId}>
            <input
              id={checkboxImagensId}
              type="checkbox"
              checked={incluirImagensPngMarkdown}
              disabled={processando || quantidadeReferenciasImagensAssetsPng === 0}
              onChange={(e) => setIncluirImagensPngMarkdown(e.target.checked)}
            />
            <span>
              Enviar imagens referenciadas em <code>assets/</code> para o projeto da issue (
              {quantidadeReferenciasImagensAssetsPng} no documento)
              {quantidadeReferenciasImagensAssetsPng === 0
                ? " — nenhuma referência PNG encontrada."
                : " — cada PNG será enviada e o link no Markdown virará `/uploads/…`."}
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
              onClick={() => onConfirmar(issueUrlTrim, incluirImagensPngMarkdown)}
            >
              {processando ? "Comentando…" : "Comentar na issue"}
            </button>
          </footer>
        </div>
      </div>
    </div>,
    document.body,
  );
}
