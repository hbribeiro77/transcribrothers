import { useEffect, useId, useMemo, useState } from "react";
import { createPortal } from "react-dom";

import type { OcorrenciaRepeticaoSuspeitaTextoTranscricaoTranscribrothers } from "./modulo_util_detectar_e_colapsar_repeticoes_suspeitas_texto_transcricao_transcribrothers.ts";
import "./estilos_css_modal_revisar_repeticoes_suspeitas_transcricao_markdown_transcribrothers.css";

export type PropsComponenteModalRevisarRepeticoesSuspeitasTranscricaoMarkdownTranscribrothers = {
  aberto: boolean;
  ocorrencias: readonly OcorrenciaRepeticaoSuspeitaTextoTranscricaoTranscribrothers[];
  processando: boolean;
  onFechar: () => void;
  onAplicar: (idsSelecionados: string[]) => void;
};

function recortarContextoOcorrenciaTranscricaoTranscribrothers(
  textoOriginal: string,
  maxCaracteres: number,
): string {
  const t = textoOriginal.replace(/\s+/g, " ").trim();
  if (t.length <= maxCaracteres) return t;
  return `${t.slice(0, Math.max(12, maxCaracteres - 1))}…`;
}

export function ComponenteModalRevisarRepeticoesSuspeitasTranscricaoMarkdownTranscribrothers({
  aberto,
  ocorrencias,
  processando,
  onFechar,
  onAplicar,
}: PropsComponenteModalRevisarRepeticoesSuspeitasTranscricaoMarkdownTranscribrothers) {
  const tituloId = useId();
  const [idsMarcados, setIdsMarcados] = useState<string[]>([]);

  const idsPadrao = useMemo(
    () => ocorrencias.filter((o) => o.marcadaPorPadrao).map((o) => o.id),
    [ocorrencias],
  );

  useEffect(() => {
    if (!aberto) return;
    setIdsMarcados(idsPadrao);
  }, [aberto, idsPadrao]);

  useEffect(() => {
    if (!aberto) return;
    const aoTeclar = (evento: KeyboardEvent) => {
      if (evento.key === "Escape" && !processando) onFechar();
    };
    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
  }, [aberto, onFechar, processando]);

  if (!aberto) return null;

  const conjunto = new Set(idsMarcados);
  const podeAplicar = idsMarcados.length > 0 && !processando;

  return createPortal(
    <div className="tb-modal-job-root" role="presentation">
      <button
        type="button"
        className="tb-modal-job-backdrop"
        aria-label="Fechar revisão de repetições"
        disabled={processando}
        onClick={onFechar}
      />
      <div className="tb-modal-job-shell">
        <div
          className="tb-modal-job tb-modal-revisar-repeticoes-transcricao"
          role="dialog"
          aria-modal="true"
          aria-labelledby={tituloId}
        >
          <h2 id={tituloId} className="tb-modal-job-titulo">
            Repetições suspeitas na transcrição
          </h2>
          <p className="tb-muted tb-modal-revisar-repeticoes-transcricao-lead">
            Loops longos costumam ser alucinação do modelo. Confira cada trecho antes de colapsar — ênfase
            curta («não, não») não entra nesta lista. Os extremos já vêm marcados.
          </p>
          <div className="tb-modal-revisar-repeticoes-transcricao-acoes-lista">
            <button
              type="button"
              className="tb-linkbtn"
              disabled={processando}
              onClick={() => setIdsMarcados(ocorrencias.map((o) => o.id))}
            >
              Marcar todas
            </button>
            <button
              type="button"
              className="tb-linkbtn"
              disabled={processando}
              onClick={() => setIdsMarcados([])}
            >
              Desmarcar todas
            </button>
          </div>
          <ul className="tb-modal-revisar-repeticoes-transcricao-lista">
            {ocorrencias.map((o, indice) => {
              const idInput = `${tituloId}-occ-${o.id}`;
              return (
                <li key={o.id}>
                  <label className="tb-modal-revisar-repeticoes-transcricao-item" htmlFor={idInput}>
                    <input
                      id={idInput}
                      type="checkbox"
                      checked={conjunto.has(o.id)}
                      disabled={processando}
                      onChange={() => {
                        setIdsMarcados((atual) =>
                          atual.includes(o.id) ? atual.filter((id) => id !== o.id) : [...atual, o.id],
                        );
                      }}
                    />
                    <span>
                      <span className="tb-modal-revisar-repeticoes-transcricao-item-meta">
                        Trecho {indice + 1} · {o.repeticoes}× «{o.textoColapsado}»
                        {o.marcadaPorPadrao ? " · extremo" : ""}
                      </span>
                      <span className="tb-modal-revisar-repeticoes-transcricao-item-amostra">
                        {recortarContextoOcorrenciaTranscricaoTranscribrothers(o.textoOriginal, 140)}
                      </span>
                    </span>
                  </label>
                </li>
              );
            })}
          </ul>
          <div className="tb-modal-job-acoes-finais">
            <button type="button" className="tb-btn-drawer-secundario" disabled={processando} onClick={onFechar}>
              Cancelar
            </button>
            <button
              type="button"
              className="tb-primary"
              disabled={!podeAplicar}
              onClick={() => onAplicar(idsMarcados)}
            >
              {processando ? "Aplicando…" : `Colapsar ${idsMarcados.length} selecionada(s)`}
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body,
  );
}
