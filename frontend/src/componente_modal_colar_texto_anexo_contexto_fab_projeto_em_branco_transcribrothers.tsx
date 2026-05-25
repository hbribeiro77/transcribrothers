import { useCallback, useEffect, useState } from "react";
import { createPortal } from "react-dom";

type PropsComponenteModalColarTextoAnexoContextoFabProjetoEmBrancoTranscribrothers = {
  aberta: boolean;
  onFechar: () => void;
  onIncluir: (texto: string) => void;
  desabilitado?: boolean;
};

export function ComponenteModalColarTextoAnexoContextoFabProjetoEmBrancoTranscribrothers({
  aberta,
  onFechar,
  onIncluir,
  desabilitado = false,
}: PropsComponenteModalColarTextoAnexoContextoFabProjetoEmBrancoTranscribrothers) {
  const [texto, setTexto] = useState("");

  useEffect(() => {
    if (!aberta) {
      setTexto("");
    }
  }, [aberta]);

  useEffect(() => {
    if (!aberta) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onFechar();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [aberta, onFechar]);

  const confirmarInclusao = useCallback(() => {
    const t = texto.trim();
    if (!t) return;
    onIncluir(t);
    setTexto("");
    onFechar();
  }, [texto, onIncluir, onFechar]);

  if (!aberta) return null;

  return createPortal(
    <div className="tb-modal-job-root" role="presentation">
      <button
        type="button"
        className="tb-modal-job-backdrop"
        aria-label="Fechar"
        onClick={onFechar}
      />
      <div className="tb-modal-job-shell tb-modal-job-shell--compacto">
        <div
          className="tb-modal-job tb-modal-fab-texto-anexo"
          role="dialog"
          aria-modal="true"
          aria-labelledby="tb-modal-fab-texto-anexo-titulo"
        >
          <h2 id="tb-modal-fab-texto-anexo-titulo" className="tb-modal-job-titulo">
            Incluir texto de referência
          </h2>
          <p className="tb-muted tb-modal-fab-texto-anexo-hint">
            Cole notas, trechos ou contexto que o modelo deve considerar neste pedido. Não é preciso
            título — cada bloco será numerado automaticamente.
          </p>
          <textarea
            id="tb-modal-fab-texto-anexo-conteudo"
            className="tb-input tb-modal-fab-texto-anexo-textarea"
            rows={12}
            autoFocus
            placeholder="Cole ou digite o texto aqui…"
            value={texto}
            disabled={desabilitado}
            onChange={(e) => setTexto(e.target.value)}
          />
          <div className="tb-modal-job-acoes-finais">
            <button type="button" className="tb-linkbtn" onClick={onFechar} disabled={desabilitado}>
              Cancelar
            </button>
            <button
              type="button"
              className="tb-primary"
              disabled={desabilitado || !texto.trim()}
              onClick={confirmarInclusao}
            >
              Incluir no pedido
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body,
  );
}
