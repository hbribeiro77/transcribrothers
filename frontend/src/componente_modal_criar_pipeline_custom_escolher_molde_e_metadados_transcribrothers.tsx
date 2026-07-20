import { useCallback, useEffect, useId, useState } from "react";
import { createPortal } from "react-dom";

import { criarPipelineCustomApiTranscribrothers } from "./modulo_api_crud_pipelines_e_agentes_custom_transcribrothers.ts";
import type { RespostaCatalogoPipelinesApiTranscribrothers } from "./tipos_catalogo_pipelines_api_transcribrothers.ts";
import { usarToastFeedbackAcoesUiTranscribrothers } from "./provedor_contexto_e_hook_uso_toasts_feedback_acoes_ui_transcribrothers.tsx";

const MOLDES_PIPELINE_CUSTOM_CRIACAO_TRANSCRIBROTHERS = [
  {
    id: "pipeline_inicial_tutorial",
    rotulo: "Tutorial",
    descricao:
      "Transcreve o áudio, captura telas do vídeo e monta um tutorial em Markdown com imagens e links para o tempo no vídeo.",
  },
  {
    id: "pipeline_inicial_notas_proposta",
    rotulo: "Notas de proposta",
    descricao:
      "Transcreve reunião de discovery ou refinement e gera notas estruturadas com links para o vídeo e capturas de telas.",
  },
  {
    id: "pipeline_inicial_reproducao_bug",
    rotulo: "Reprodução de bug",
    descricao:
      "Monta passo a passo de reprodução do bug com capturas e IA, com ou sem JSON de cliques do RecBrothers.",
  },
  {
    id: "pipeline_inicial_so_transcricao",
    rotulo: "Só transcrição",
    descricao:
      "Aceita vídeo ou áudio, transcreve e publica o texto no job — sem capturas nem geração de tutorial/notas/bug.",
  },
] as const;

export type ComponenteModalCriarPipelineCustomEscolherMoldeEMetadadosTranscribrothersProps = {
  aberto: boolean;
  onFechar: () => void;
  onCriada: (catalogo: RespostaCatalogoPipelinesApiTranscribrothers) => void;
};

export function ComponenteModalCriarPipelineCustomEscolherMoldeEMetadadosTranscribrothers({
  aberto,
  onFechar,
  onCriada,
}: ComponenteModalCriarPipelineCustomEscolherMoldeEMetadadosTranscribrothersProps) {
  const tituloId = useId();
  const { pushToast } = usarToastFeedbackAcoesUiTranscribrothers();
  const [moldeId, setMoldeId] = useState<string>(MOLDES_PIPELINE_CUSTOM_CRIACAO_TRANSCRIBROTHERS[0].id);
  const [titulo, setTitulo] = useState("");
  const [descricao, setDescricao] = useState("");
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    if (!aberto) return;
    setMoldeId(MOLDES_PIPELINE_CUSTOM_CRIACAO_TRANSCRIBROTHERS[0].id);
    setTitulo("");
    setDescricao("");
  }, [aberto]);

  useEffect(() => {
    if (!aberto) return;
    const aoTeclar = (evento: KeyboardEvent) => {
      if (evento.key === "Escape" && !salvando) onFechar();
    };
    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
  }, [aberto, onFechar, salvando]);

  const confirmar = useCallback(async () => {
    const tituloNorm = titulo.trim();
    if (!tituloNorm) {
      pushToast("Informe um título para a pipeline.", "error");
      return;
    }
    setSalvando(true);
    try {
      const catalogo = await criarPipelineCustomApiTranscribrothers(moldeId, {
        titulo: tituloNorm,
        descricao: descricao.trim() || undefined,
      });
      pushToast("Pipeline criada.", "success");
      onCriada(catalogo);
      onFechar();
    } catch (e: unknown) {
      pushToast(e instanceof Error ? e.message : "Falha ao criar pipeline.", "error");
    } finally {
      setSalvando(false);
    }
  }, [descricao, moldeId, onCriada, onFechar, pushToast, titulo]);

  if (!aberto) return null;

  return createPortal(
    <div className="tb-modal-job-root" role="presentation">
      <button type="button" className="tb-modal-job-backdrop" aria-label="Fechar" disabled={salvando} onClick={onFechar} />
      <div className="tb-modal-job-shell tb-modal-job-shell-catalogo-editor-pipeline">
        <div className="tb-modal-job tb-catalogo-modal-editor-pipeline" role="dialog" aria-modal="true" aria-labelledby={tituloId}>
          <h2 id={tituloId} className="tb-modal-job-titulo">
            Nova pipeline
          </h2>
          <p className="tb-muted">
            Escolha um molde executável (tutorial, notas, bug ou só transcrição) e defina título e descrição.
          </p>
          <fieldset className="tb-catalogo-criar-pipeline-moldes">
            <legend className="tb-field-label">Molde</legend>
            <div className="tb-stepper-iniciar-transcricao-opcoes-destino" role="radiogroup" aria-label="Molde da pipeline">
              {MOLDES_PIPELINE_CUSTOM_CRIACAO_TRANSCRIBROTHERS.map((molde) => (
                <label
                  key={molde.id}
                  className={`tb-stepper-iniciar-transcricao-opcao-destino${moldeId === molde.id ? " tb-stepper-iniciar-transcricao-opcao-destino--selecionada" : ""}`}
                >
                  <input
                    type="radio"
                    name="molde-pipeline-custom"
                    value={molde.id}
                    checked={moldeId === molde.id}
                    onChange={() => setMoldeId(molde.id)}
                  />
                  <span className="tb-stepper-iniciar-transcricao-opcao-titulo">{molde.rotulo}</span>
                  <span className="tb-muted tb-stepper-iniciar-transcricao-opcao-desc">{molde.descricao}</span>
                </label>
              ))}
            </div>
          </fieldset>
          <label className="tb-field">
            <span className="tb-field-label">Título</span>
            <input className="tb-input" value={titulo} onChange={(e) => setTitulo(e.target.value)} disabled={salvando} />
          </label>
          <label className="tb-field">
            <span className="tb-field-label">Descrição</span>
            <textarea
              className="tb-input"
              rows={3}
              value={descricao}
              onChange={(e) => setDescricao(e.target.value)}
              disabled={salvando}
            />
          </label>
          <div className="tb-modal-job-acoes-finais">
            <button type="button" className="tb-linkbtn" onClick={onFechar} disabled={salvando}>
              Cancelar
            </button>
            <button type="button" className="tb-primary" onClick={() => void confirmar()} disabled={salvando}>
              {salvando ? "Criando…" : "Criar pipeline"}
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body,
  );
}
