/**
 * Barra horizontal de passos de pipeline (modal de status ou catálogo).
 * Reutiliza estilos `.tb-pipeline-status-*` da página principal.
 */

import type { ReactNode } from "react";
import type { EstadoPassoPipelineHorizontalModalStatusTranscribrothers } from "./modulo_util_obter_passos_pipeline_horizontal_hint_modal_status_job_transcribrothers.ts";

export type PassoBarraPipelineHorizontalVisualTranscribrothers = {
  id: string;
  rotuloCurto: string;
  estado: EstadoPassoPipelineHorizontalModalStatusTranscribrothers;
  duracaoRotulo?: string;
};

export type ComponenteBarraPassosPipelineHorizontalVisualComPainelDetalheTranscribrothersProps = {
  tituloFluxo: string;
  descricaoFluxo: string;
  passos: PassoBarraPipelineHorizontalVisualTranscribrothers[];
  passoComPainelAbertoId: string | null;
  onAlternarPainelPasso: (passoId: string) => void;
  onFecharPainelPasso?: () => void;
  idPainelDescricao?: string;
  ariaLabelGrupo?: string;
  legendaClique?: string;
  mensagemSemPassos?: string;
  renderPainelPasso?: (passoId: string) => ReactNode;
  onClickPasso?: (passo: PassoBarraPipelineHorizontalVisualTranscribrothers) => boolean | void;
};

export function ComponenteBarraPassosPipelineHorizontalVisualComPainelDetalheTranscribrothers({
  tituloFluxo,
  descricaoFluxo,
  passos,
  passoComPainelAbertoId,
  onAlternarPainelPasso,
  onFecharPainelPasso,
  idPainelDescricao = "tb-pipeline-hint-painel",
  ariaLabelGrupo,
  legendaClique = "Clique em um passo para abrir a descrição abaixo. Tab e Enter também funcionam.",
  mensagemSemPassos,
  renderPainelPasso,
  onClickPasso,
}: ComponenteBarraPassosPipelineHorizontalVisualComPainelDetalheTranscribrothersProps) {
  const passoSelecionado = passos.find((p) => p.id === passoComPainelAbertoId);

  return (
    <div
      className="tb-pipeline-status-horizontal"
      role="group"
      aria-label={ariaLabelGrupo ?? `${tituloFluxo}. Visão em passos da pipeline.`}
    >
      <p className="tb-pipeline-status-fluxo-titulo">{tituloFluxo}</p>
      <p className="tb-pipeline-status-fluxo-descricao tb-muted">{descricaoFluxo}</p>
      {passos.length > 0 ? (
        <>
          <p className="tb-pipeline-status-horizontal-legenda tb-muted">{legendaClique}</p>
          <div
            className={`tb-pipeline-status-horizontal-linha${passos.length > 6 ? " tb-pipeline-status-horizontal-linha--compacta" : ""}`}
          >
            {passos.map((p, indice) => {
              const aberto = passoComPainelAbertoId === p.id;
              return (
                <div key={p.id} className="tb-pipeline-status-segmento">
                  {indice > 0 ? <span className="tb-pipeline-status-connector" aria-hidden /> : null}
                  <button
                    type="button"
                    className={`tb-pipeline-status-step tb-pipeline-status-step--${p.estado}`}
                    aria-expanded={aberto}
                    aria-controls={idPainelDescricao}
                    aria-label={
                      aberto
                        ? `${p.rotuloCurto}${p.duracaoRotulo ? ` (${p.duracaoRotulo})` : ""}, descrição aberta abaixo`
                        : `${p.rotuloCurto}${p.duracaoRotulo ? ` (${p.duracaoRotulo})` : ""}, clique para ver a descrição completa`
                    }
                    onClick={() => {
                      if (onClickPasso) {
                        const consumiu = onClickPasso(p);
                        if (consumiu === true) return;
                      }
                      onAlternarPainelPasso(p.id);
                    }}
                  >
                    <span className="tb-pipeline-status-step-rotulo">{p.rotuloCurto}</span>
                    {p.duracaoRotulo ? (
                      <span className="tb-pipeline-status-step-duracao" aria-hidden>
                        {p.duracaoRotulo}
                      </span>
                    ) : null}
                  </button>
                </div>
              );
            })}
          </div>
          {passoSelecionado && renderPainelPasso ? (
            <div
              id={idPainelDescricao}
              className="tb-pipeline-status-hint-painel"
              role="region"
              aria-live="polite"
            >
              <div className="tb-pipeline-status-hint-painel-topo">
                <strong className="tb-pipeline-status-hint-painel-titulo">{passoSelecionado.rotuloCurto}</strong>
                <button
                  type="button"
                  className="tb-pipeline-status-hint-painel-fechar"
                  aria-label="Fechar descrição do passo"
                  onClick={() => onFecharPainelPasso?.()}
                >
                  ×
                </button>
              </div>
              <div className="tb-pipeline-status-hint-painel-corpo">{renderPainelPasso(passoSelecionado.id)}</div>
            </div>
          ) : null}
        </>
      ) : mensagemSemPassos ? (
        <p className="tb-pipeline-status-sem-passos-horizontais tb-muted">{mensagemSemPassos}</p>
      ) : null}
    </div>
  );
}
