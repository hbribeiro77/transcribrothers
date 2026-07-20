import { useCallback, useEffect, useId, useMemo, useState } from "react";
import { createPortal } from "react-dom";
import {
  DndContext,
  KeyboardSensor,
  PointerSensor,
  closestCenter,
  type DragEndEvent,
  useSensor,
  useSensors,
} from "@dnd-kit/core";
import {
  SortableContext,
  arrayMove,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

import {
  adicionarPassoPipelineCustomApiTranscribrothers,
  reordenarPassosPipelineCustomApiTranscribrothers,
  removerPassoPipelineCustomApiTranscribrothers,
} from "./modulo_api_crud_pipelines_e_agentes_custom_transcribrothers.ts";
import type {
  AgenteCatalogoApiTranscribrothers,
  PipelineCatalogoApiTranscribrothers,
  PassoCatalogoPipelineApiTranscribrothers,
  RespostaCatalogoPipelinesApiTranscribrothers,
} from "./tipos_catalogo_pipelines_api_transcribrothers.ts";
import { usarToastFeedbackAcoesUiTranscribrothers } from "./provedor_contexto_e_hook_uso_toasts_feedback_acoes_ui_transcribrothers.tsx";

export type ComponenteModalEditarPassosPipelineCustomAdicionarRemoverReordenarTranscribrothersProps = {
  aberto: boolean;
  pipeline: PipelineCatalogoApiTranscribrothers | null;
  agentes: AgenteCatalogoApiTranscribrothers[];
  onFechar: () => void;
  onAtualizado: (catalogo: RespostaCatalogoPipelinesApiTranscribrothers) => void;
};

function LinhaPassoOrdenavelEditarPassosPipelineCustomTranscribrothers({
  passo,
  agenteRotulo,
  desabilitado,
  onRemover,
}: {
  passo: PassoCatalogoPipelineApiTranscribrothers;
  agenteRotulo: string;
  desabilitado: boolean;
  onRemover: (passoId: string) => void;
}) {
  const { attributes, listeners, setNodeRef, setActivatorNodeRef, transform, transition, isDragging } = useSortable({
    id: passo.id,
    disabled: desabilitado,
  });
  const estilo = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.55 : 1,
  };

  return (
    <li ref={setNodeRef} style={estilo} className="tb-catalogo-passos-editor-item">
      <button
        type="button"
        ref={setActivatorNodeRef}
        className="tb-catalogo-pipeline-drag-handle tb-catalogo-passos-editor-drag"
        aria-label={`Arrastar passo ${passo.rotulo}`}
        disabled={desabilitado}
        {...attributes}
        {...listeners}
      >
        <span aria-hidden="true">⋮⋮</span>
      </button>
      <div className="tb-catalogo-passos-editor-conteudo">
        <strong>{passo.rotulo}</strong>
        <span className="tb-muted tb-catalogo-passos-editor-agente">{agenteRotulo}</span>
        {passo.descricao ? <p className="tb-muted tb-catalogo-passos-editor-descricao">{passo.descricao}</p> : null}
      </div>
      <button
        type="button"
        className="tb-linkbtn tb-catalogo-btn-excluir"
        disabled={desabilitado}
        onClick={() => onRemover(passo.id)}
        aria-label={`Remover passo ${passo.rotulo}`}
      >
        Remover
      </button>
    </li>
  );
}

export function ComponenteModalEditarPassosPipelineCustomAdicionarRemoverReordenarTranscribrothers({
  aberto,
  pipeline,
  agentes,
  onFechar,
  onAtualizado,
}: ComponenteModalEditarPassosPipelineCustomAdicionarRemoverReordenarTranscribrothersProps) {
  const tituloId = useId();
  const { pushToast } = usarToastFeedbackAcoesUiTranscribrothers();
  const [passosLocais, setPassosLocais] = useState<PassoCatalogoPipelineApiTranscribrothers[]>([]);
  const [agenteFonteId, setAgenteFonteId] = useState("");
  const [acaoEmAndamento, setAcaoEmAndamento] = useState(false);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 6 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  const agentesPorId = useMemo(() => {
    const mapa = new Map<string, AgenteCatalogoApiTranscribrothers>();
    for (const agente of agentes) mapa.set(agente.id, agente);
    return mapa;
  }, [agentes]);

  const agentesDisponiveisAdicionar = useMemo(() => {
    return [...agentes].sort((a, b) => a.rotulo.localeCompare(b.rotulo, "pt-BR"));
  }, [agentes]);

  useEffect(() => {
    if (!aberto || !pipeline) return;
    setPassosLocais([...pipeline.passos]);
    setAgenteFonteId(agentesDisponiveisAdicionar[0]?.id ?? "");
  }, [aberto, agentesDisponiveisAdicionar, pipeline]);

  useEffect(() => {
    if (!aberto) return;
    const aoTeclar = (evento: KeyboardEvent) => {
      if (evento.key === "Escape" && !acaoEmAndamento) onFechar();
    };
    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
  }, [aberto, acaoEmAndamento, onFechar]);

  const aoFinalizarArraste = useCallback(
    async (evento: DragEndEvent) => {
      if (!pipeline) return;
      const { active, over } = evento;
      if (!over || active.id === over.id) return;
      const indiceAntigo = passosLocais.findIndex((p) => p.id === active.id);
      const indiceNovo = passosLocais.findIndex((p) => p.id === over.id);
      if (indiceAntigo < 0 || indiceNovo < 0) return;
      const reordenados = arrayMove(passosLocais, indiceAntigo, indiceNovo);
      const idsOrdenados = reordenados.map((p) => p.id);
      setPassosLocais(reordenados);
      setAcaoEmAndamento(true);
      try {
        const catalogo = await reordenarPassosPipelineCustomApiTranscribrothers(pipeline.id, idsOrdenados);
        onAtualizado(catalogo);
        const atualizada = catalogo.pipelines.find((p) => p.id === pipeline.id);
        if (atualizada) setPassosLocais([...atualizada.passos]);
        pushToast("Ordem dos passos atualizada.", "success");
      } catch (e: unknown) {
        pushToast(e instanceof Error ? e.message : "Falha ao reordenar passos.", "error");
        setPassosLocais([...pipeline.passos]);
      } finally {
        setAcaoEmAndamento(false);
      }
    },
    [onAtualizado, passosLocais, pipeline, pushToast],
  );

  const adicionarPasso = useCallback(async () => {
    if (!pipeline || !agenteFonteId) return;
    setAcaoEmAndamento(true);
    try {
      const catalogo = await adicionarPassoPipelineCustomApiTranscribrothers(pipeline.id, {
        agente_fonte_id: agenteFonteId,
      });
      onAtualizado(catalogo);
      const atualizada = catalogo.pipelines.find((p) => p.id === pipeline.id);
      if (atualizada) setPassosLocais([...atualizada.passos]);
      pushToast("Passo adicionado (agente da biblioteca referenciado).", "success");
    } catch (e: unknown) {
      pushToast(e instanceof Error ? e.message : "Falha ao adicionar passo.", "error");
    } finally {
      setAcaoEmAndamento(false);
    }
  }, [agenteFonteId, onAtualizado, pipeline, pushToast]);

  const removerPasso = useCallback(
    async (passoId: string) => {
      if (!pipeline) return;
      if (
        !window.confirm(
          "Remover este passo? O agente só é excluído da biblioteca se nenhuma outra pipeline o usar.",
        )
      ) {
        return;
      }
      setAcaoEmAndamento(true);
      try {
        const catalogo = await removerPassoPipelineCustomApiTranscribrothers(pipeline.id, passoId);
        onAtualizado(catalogo);
        const atualizada = catalogo.pipelines.find((p) => p.id === pipeline.id);
        if (atualizada) setPassosLocais([...atualizada.passos]);
        pushToast("Passo removido.", "success");
      } catch (e: unknown) {
        pushToast(e instanceof Error ? e.message : "Falha ao remover passo.", "error");
      } finally {
        setAcaoEmAndamento(false);
      }
    },
    [onAtualizado, pipeline, pushToast],
  );

  if (!aberto || !pipeline) return null;

  return createPortal(
    <div className="tb-modal-job-root" role="presentation">
      <button
        type="button"
        className="tb-modal-job-backdrop"
        aria-label="Fechar"
        onClick={onFechar}
        disabled={acaoEmAndamento}
      />
      <div className="tb-modal-job-shell tb-modal-job-shell-catalogo-editor-pipeline">
        <div
          className="tb-modal-job tb-catalogo-modal-editor-passos-pipeline"
          role="dialog"
          aria-modal="true"
          aria-labelledby={tituloId}
        >
          <h2 id={tituloId} className="tb-modal-job-titulo">
            Editar passos — {pipeline.titulo}
          </h2>
          <p className="tb-muted tb-catalogo-modal-passos-dica">
            Arraste para reordenar. Ao adicionar, o agente escolhido é referenciado da biblioteca (sem criar cópia). A
            ordem dos passos atualiza o catálogo e o snapshot no upload; a execução do job ainda segue a lógica fixa do
            molde.
          </p>

          <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={(e) => void aoFinalizarArraste(e)}>
            <SortableContext items={passosLocais.map((p) => p.id)} strategy={verticalListSortingStrategy}>
              <ol className="tb-catalogo-passos-editor-lista">
                {passosLocais.map((passo) => {
                  const agente = agentesPorId.get(passo.agente_id);
                  return (
                    <LinhaPassoOrdenavelEditarPassosPipelineCustomTranscribrothers
                      key={passo.id}
                      passo={passo}
                      agenteRotulo={agente?.rotulo ?? passo.agente_id}
                      desabilitado={acaoEmAndamento}
                      onRemover={(id) => void removerPasso(id)}
                    />
                  );
                })}
              </ol>
            </SortableContext>
          </DndContext>

          <div className="tb-catalogo-passos-editor-adicionar">
            <label className="tb-field">
              <span className="tb-field-label">Adicionar passo (agente fonte)</span>
              <select
                className="tb-input"
                value={agenteFonteId}
                onChange={(e) => setAgenteFonteId(e.target.value)}
                disabled={acaoEmAndamento || agentesDisponiveisAdicionar.length === 0}
              >
                {agentesDisponiveisAdicionar.map((agente) => (
                  <option key={agente.id} value={agente.id}>
                    {agente.rotulo}
                    {agente.origem === "sistema" ? " (sistema)" : " (custom)"}
                  </option>
                ))}
              </select>
            </label>
            <button
              type="button"
              className="tb-secondary"
              disabled={acaoEmAndamento || !agenteFonteId}
              onClick={() => void adicionarPasso()}
            >
              Adicionar passo
            </button>
          </div>

          <div className="tb-modal-job-acoes-finais">
            <button type="button" className="tb-primary" onClick={onFechar} disabled={acaoEmAndamento}>
              Fechar
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body,
  );
}
