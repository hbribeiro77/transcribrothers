import { useEffect, useId, useState } from "react";
import { createPortal } from "react-dom";

export type PropsComponenteModalConfirmarCriarIssueGitlabDocumentoMarkdownTranscribrothers = {
  aberto: boolean;
  tituloInicial: string;
  projetoGitlab: string;
  tamanhoDescricaoCaracteres: number;
  quantidadeReferenciasImagensAssetsPng: number;
  processando: boolean;
  onFechar: () => void;
  onConfirmar: (titulo: string, incluirImagensPngMarkdown: boolean) => void;
};

export function ComponenteModalConfirmarCriarIssueGitlabDocumentoMarkdownTranscribrothers({
  aberto,
  tituloInicial,
  projetoGitlab,
  tamanhoDescricaoCaracteres,
  quantidadeReferenciasImagensAssetsPng,
  processando,
  onFechar,
  onConfirmar,
}: PropsComponenteModalConfirmarCriarIssueGitlabDocumentoMarkdownTranscribrothers) {
  const tituloId = useId();
  const checkboxImagensId = useId();
  const [titulo, setTitulo] = useState(tituloInicial);
  const [incluirImagensPngMarkdown, setIncluirImagensPngMarkdown] = useState(true);

  useEffect(() => {
    if (!aberto) return;
    setTitulo(tituloInicial);
    setIncluirImagensPngMarkdown(quantidadeReferenciasImagensAssetsPng > 0);
  }, [aberto, tituloInicial, quantidadeReferenciasImagensAssetsPng]);

  useEffect(() => {
    if (!aberto) return;
    const aoTeclar = (evento: KeyboardEvent) => {
      if (evento.key === "Escape" && !processando) onFechar();
    };
    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
  }, [aberto, onFechar, processando]);

  if (!aberto) return null;

  const tituloTrim = titulo.trim();
  const podeConfirmar = tituloTrim.length > 0 && tituloTrim.length <= 255 && tamanhoDescricaoCaracteres > 0;

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
            Exportar como issue no GitLab
          </h2>
          <p className="tb-muted tb-modal-criar-issue-gitlab-lead">
            O Markdown completo do documento ({tamanhoDescricaoCaracteres.toLocaleString("pt-BR")}{" "}
            caracteres) será enviado como <strong>descrição</strong> da issue. Projeto:{" "}
            <code>{projetoGitlab || "portal-da-defensoria/portal-defensoria-gateway"}</code> — label{" "}
            <code>squad::bravo</code>.
          </p>
          <label className="tb-modal-criar-issue-gitlab-checkbox-imagens" htmlFor={checkboxImagensId}>
            <input
              id={checkboxImagensId}
              type="checkbox"
              checked={incluirImagensPngMarkdown}
              disabled={processando || quantidadeReferenciasImagensAssetsPng === 0}
              onChange={(e) => setIncluirImagensPngMarkdown(e.target.checked)}
            />
            <span>
              Enviar imagens referenciadas em <code>assets/</code> para o GitLab (
              {quantidadeReferenciasImagensAssetsPng} no documento)
              {quantidadeReferenciasImagensAssetsPng === 0
                ? " — nenhuma referência PNG encontrada."
                : " — cada PNG será enviada e o link no Markdown virará `/uploads/…`."}
            </span>
          </label>
          <label className="tb-modal-criar-issue-gitlab-campo">
            <span className="tb-modal-criar-issue-gitlab-rotulo">Título da issue</span>
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
              onClick={() => onConfirmar(tituloTrim, incluirImagensPngMarkdown)}
            >
              {processando ? "Exportando…" : "Exportar issue"}
            </button>
          </footer>
        </div>
      </div>
    </div>,
    document.body,
  );
}
