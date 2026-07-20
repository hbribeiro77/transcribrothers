import { useCallback, useEffect, useId, useState } from "react";
import { createPortal } from "react-dom";

import { atualizarPipelineCustomApiTranscribrothers } from "./modulo_api_crud_pipelines_e_agentes_custom_transcribrothers.ts";
import type {
  PipelineCatalogoApiTranscribrothers,
  RespostaCatalogoPipelinesApiTranscribrothers,
} from "./tipos_catalogo_pipelines_api_transcribrothers.ts";
import { usarToastFeedbackAcoesUiTranscribrothers } from "./provedor_contexto_e_hook_uso_toasts_feedback_acoes_ui_transcribrothers.tsx";

export type ComponenteModalEditorPipelineCustomMetadadosTranscribrothersProps = {
  aberto: boolean;
  pipeline: PipelineCatalogoApiTranscribrothers | null;
  onFechar: () => void;
  onSalvo: (catalogo: RespostaCatalogoPipelinesApiTranscribrothers) => void;
};

export function ComponenteModalEditorPipelineCustomMetadadosTranscribrothers({
  aberto,
  pipeline,
  onFechar,
  onSalvo,
}: ComponenteModalEditorPipelineCustomMetadadosTranscribrothersProps) {
  const tituloId = useId();
  const { pushToast } = usarToastFeedbackAcoesUiTranscribrothers();
  const [titulo, setTitulo] = useState("");
  const [descricao, setDescricao] = useState("");
  const [aceitaVideo, setAceitaVideo] = useState(true);
  const [aceitaAudio, setAceitaAudio] = useState(false);
  const [salvando, setSalvando] = useState(false);

  const moldeSoTranscricao = pipeline?.copiado_de === "pipeline_inicial_so_transcricao";

  useEffect(() => {
    if (!aberto || !pipeline) return;
    setTitulo(pipeline.titulo);
    setDescricao(pipeline.descricao);
    const entradas = pipeline.entradas_aceitas?.length ? pipeline.entradas_aceitas : ["video"];
    setAceitaVideo(entradas.includes("video"));
    setAceitaAudio(entradas.includes("audio"));
  }, [aberto, pipeline]);

  useEffect(() => {
    if (!aberto) return;
    const aoTeclar = (evento: KeyboardEvent) => {
      if (evento.key === "Escape" && !salvando) onFechar();
    };
    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
  }, [aberto, onFechar, salvando]);

  const salvar = useCallback(async () => {
    if (!pipeline) return;
    const entradas: string[] = [];
    if (aceitaVideo) entradas.push("video");
    if (aceitaAudio) entradas.push("audio");
    if (entradas.length === 0) {
      pushToast("Selecione ao menos um tipo de entrada (vídeo ou áudio).", "error");
      return;
    }
    setSalvando(true);
    try {
      const catalogo = await atualizarPipelineCustomApiTranscribrothers(pipeline.id, {
        titulo: titulo.trim(),
        descricao,
        entradas_aceitas: entradas,
      });
      pushToast("Pipeline atualizada.", "success");
      onSalvo(catalogo);
      onFechar();
    } catch (e: unknown) {
      pushToast(e instanceof Error ? e.message : "Falha ao salvar pipeline.", "error");
    } finally {
      setSalvando(false);
    }
  }, [aceitaAudio, aceitaVideo, descricao, onFechar, onSalvo, pipeline, pushToast, titulo]);

  if (!aberto || !pipeline) return null;

  return createPortal(
    <div className="tb-modal-job-root" role="presentation">
      <button type="button" className="tb-modal-job-backdrop" aria-label="Fechar" onClick={onFechar} disabled={salvando} />
      <div className="tb-modal-job-shell tb-modal-job-shell-catalogo-editor-pipeline">
        <div
          className="tb-modal-job tb-catalogo-modal-editor-pipeline"
          role="dialog"
          aria-modal="true"
          aria-labelledby={tituloId}
        >
          <h2 id={tituloId} className="tb-modal-job-titulo">
            Editar pipeline
          </h2>
          {pipeline.executavel === false ? (
            <p className="tb-catalogo-pipelines-aviso-nao-executavel">
              Esta pipeline é somente documentação (fluxo 2). Ainda não pode ser usada no upload.
            </p>
          ) : null}
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
          <fieldset className="tb-field">
            <legend className="tb-field-label">Entradas aceitas no upload</legend>
            <label className="tb-catalogo-checkbox-entrada-midia">
              <input
                type="checkbox"
                checked={aceitaVideo}
                disabled={salvando}
                onChange={(e) => setAceitaVideo(e.target.checked)}
              />
              Vídeo
            </label>
            <label className="tb-catalogo-checkbox-entrada-midia">
              <input
                type="checkbox"
                checked={aceitaAudio}
                disabled={salvando || !moldeSoTranscricao}
                onChange={(e) => setAceitaAudio(e.target.checked)}
              />
              Áudio
              {!moldeSoTranscricao ? (
                <span className="tb-muted"> (só no molde «Só transcrição» nesta versão)</span>
              ) : null}
            </label>
          </fieldset>
          <p className="tb-muted tb-catalogo-modal-pipeline-dica-agentes">
            Para editar prompts e modelo dos agentes, clique nos passos da pipeline no catálogo.
          </p>
          <div className="tb-modal-job-acoes-finais">
            <button type="button" className="tb-linkbtn" onClick={onFechar} disabled={salvando}>
              Cancelar
            </button>
            <button type="button" className="tb-primary" onClick={() => void salvar()} disabled={salvando}>
              {salvando ? "Salvando…" : "Salvar"}
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body,
  );
}
