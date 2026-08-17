import { forwardRef, useCallback, useEffect, useMemo, useState } from "react";
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
import { ComponenteBarraPassosPipelineHorizontalVisualComPainelDetalheTranscribrothers } from "./componente_barra_passos_pipeline_horizontal_visual_com_painel_detalhe_transcribrothers.tsx";
import { ComponenteModalCriarPipelineCustomEscolherMoldeEMetadadosTranscribrothers } from "./componente_modal_criar_pipeline_custom_escolher_molde_e_metadados_transcribrothers.tsx";
import { ComponenteModalEditarPassosPipelineCustomAdicionarRemoverReordenarTranscribrothers } from "./componente_modal_editar_passos_pipeline_custom_adicionar_remover_reordenar_transcribrothers.tsx";
import { ComponenteModalEditorPipelineCustomMetadadosTranscribrothers } from "./componente_modal_editor_pipeline_custom_metadados_transcribrothers.tsx";
import { ComponentePainelEdicaoInlineAgenteCustomCatalogoPipelinesTranscribrothers } from "./componente_painel_edicao_inline_agente_custom_catalogo_pipelines_transcribrothers.tsx";
import {
  duplicarAgenteCustomApiTranscribrothers,
  duplicarPipelineCustomApiTranscribrothers,
  excluirAgenteCustomApiTranscribrothers,
  excluirPipelineCustomApiTranscribrothers,
  reordenarPipelinesCustomApiTranscribrothers,
} from "./modulo_api_crud_pipelines_e_agentes_custom_transcribrothers.ts";
import {
  filtrarPipelinesSistemaCatalogoTranscribrothers,
  obterRotuloMoldePipelineCustomCatalogoTranscribrothers,
  ordenarTodasPipelinesCustomUsuarioCatalogoTranscribrothers,
} from "./modulo_util_ordenar_e_filtrar_pipelines_custom_executaveis_catalogo_transcribrothers.ts";
import { usarToastFeedbackAcoesUiTranscribrothers } from "./provedor_contexto_e_hook_uso_toasts_feedback_acoes_ui_transcribrothers.tsx";
import { usarDialogoConfirmacaoAcaoUiSubstituindoWindowConfirmTranscribrothers } from "./hook_usar_dialogo_confirmacao_acao_ui_substituindo_window_confirm_transcribrothers.tsx";
import type {
  AgenteCatalogoApiTranscribrothers,
  PipelineCatalogoApiTranscribrothers,
  RespostaCatalogoPipelinesApiTranscribrothers,
} from "./tipos_catalogo_pipelines_api_transcribrothers.ts";
import "./componente_pagina_principal_formulario_drive_preview_tutorial.css";
import "./estilos_css_pagina_catalogo_pipelines_disponiveis_transcribrothers.css";

export type ComponentePaginaCatalogoPipelinesDisponiveisComPromptsPorEtapaTranscribrothersProps = {
  onVoltarParaProjeto: () => void;
};

type AbaCatalogoTranscribrothers = "pipelines" | "agentes";

function BadgeOrigemCatalogoTranscribrothers({ origem, executavel }: { origem?: string; executavel?: boolean }) {
  if (origem === "usuario") {
    return (
      <>
        <span className="tb-catalogo-badge tb-catalogo-badge--custom">Custom</span>
        {executavel === false ? (
          <span className="tb-catalogo-badge tb-catalogo-badge--aviso">Somente documentação</span>
        ) : null}
      </>
    );
  }
  return <span className="tb-catalogo-badge tb-catalogo-badge--sistema">Sistema</span>;
}

function CardPipelineCatalogoTranscribrothers({
  pipeline,
  agentesPorId,
  modelosLitellm,
  modeloPadrao,
  onDuplicar,
  onEditar,
  onEditarPassos,
  onExcluir,
  onSalvoAgente,
  acaoEmAndamento,
  arrastavel = false,
  alcaArrastar,
}: {
  pipeline: PipelineCatalogoApiTranscribrothers;
  agentesPorId: Map<string, AgenteCatalogoApiTranscribrothers>;
  modelosLitellm: string[];
  modeloPadrao: string;
  onDuplicar: (id: string) => void;
  onEditar: (pipeline: PipelineCatalogoApiTranscribrothers) => void;
  onEditarPassos?: (pipeline: PipelineCatalogoApiTranscribrothers) => void;
  onExcluir: (id: string) => void;
  onSalvoAgente: (catalogo: RespostaCatalogoPipelinesApiTranscribrothers) => void;
  acaoEmAndamento: boolean;
  arrastavel?: boolean;
  alcaArrastar?: React.ReactNode;
}) {
  const [passoAbertoId, setPassoAbertoId] = useState<string | null>(null);
  const passoAberto = pipeline.passos.find((p) => p.id === passoAbertoId) ?? null;
  const agenteAberto = passoAberto ? agentesPorId.get(passoAberto.agente_id) : null;

  return (
    <article className="tb-catalogo-pipelines-card" aria-labelledby={`tb-catalogo-pipeline-${pipeline.id}`}>
      <div className="tb-catalogo-card-acoes-cabecalho">
        <div className="tb-catalogo-card-acoes-cabecalho-esquerda">
          {arrastavel ? alcaArrastar : null}
          <BadgeOrigemCatalogoTranscribrothers origem={pipeline.origem} executavel={pipeline.executavel} />
          {pipeline.origem === "usuario" ? (
            <span className="tb-catalogo-badge tb-catalogo-badge--molde">
              Molde: {obterRotuloMoldePipelineCustomCatalogoTranscribrothers(pipeline.copiado_de)}
            </span>
          ) : null}
        </div>
        <div className="tb-catalogo-card-botoes">
          <button
            type="button"
            className="tb-linkbtn"
            disabled={acaoEmAndamento}
            onClick={() => onDuplicar(pipeline.id)}
          >
            Duplicar
          </button>
          {pipeline.editavel ? (
            <>
              <button
                type="button"
                className="tb-linkbtn"
                disabled={acaoEmAndamento}
                onClick={() => onEditar(pipeline)}
              >
                Editar
              </button>
              {onEditarPassos ? (
                <button
                  type="button"
                  className="tb-linkbtn"
                  disabled={acaoEmAndamento}
                  onClick={() => onEditarPassos(pipeline)}
                >
                  Editar passos
                </button>
              ) : null}
              <button
                type="button"
                className="tb-linkbtn tb-catalogo-btn-excluir"
                disabled={acaoEmAndamento}
                onClick={() => onExcluir(pipeline.id)}
              >
                Excluir
              </button>
            </>
          ) : null}
        </div>
      </div>
      <ComponenteBarraPassosPipelineHorizontalVisualComPainelDetalheTranscribrothers
        tituloFluxo={pipeline.titulo}
        descricaoFluxo={pipeline.descricao}
        passos={pipeline.passos.map((p) => ({
          id: p.id,
          rotuloCurto: p.rotulo,
          estado: "pending",
        }))}
        passoComPainelAbertoId={passoAbertoId}
        onAlternarPainelPasso={(id) => setPassoAbertoId((atual) => (atual === id ? null : id))}
        onFecharPainelPasso={() => setPassoAbertoId(null)}
        idPainelDescricao={`tb-catalogo-pipeline-painel-${pipeline.id}`}
        ariaLabelGrupo={`${pipeline.titulo}. Catálogo de passos.`}
        legendaClique={
          pipeline.editavel
            ? "Clique em um passo para ver ou editar o agente desta etapa (prompts e modelo)."
            : "Clique em um passo para ver o agente, a descrição e os prompts usados nessa etapa."
        }
        renderPainelPasso={() =>
          passoAberto && agenteAberto ? (
            <ComponentePainelEdicaoInlineAgenteCustomCatalogoPipelinesTranscribrothers
              key={`${passoAberto.id}-${agenteAberto.id}`}
              agente={agenteAberto}
              descricaoPasso={passoAberto.descricao}
              modelosLitellm={modelosLitellm}
              modeloPadrao={modeloPadrao}
              modoEdicao={agenteAberto.editavel === true}
              onSalvo={onSalvoAgente}
              desabilitado={acaoEmAndamento}
            />
          ) : null
        }
      />
    </article>
  );
}

const AlcaArrastarPipelineCustomCatalogoTranscribrothers = forwardRef<
  HTMLButtonElement,
  React.ButtonHTMLAttributes<HTMLButtonElement>
>(function AlcaArrastarPipelineCustomCatalogoTranscribrothers({ disabled, ...props }, ref) {
  return (
    <button
      ref={ref}
      type="button"
      className="tb-catalogo-pipeline-drag-handle"
      aria-label="Arrastar para reordenar"
      disabled={disabled}
      {...props}
    >
      <span aria-hidden="true">⋮⋮</span>
    </button>
  );
});

function CardPipelineCustomOrdenavelCatalogoTranscribrothers({
  pipeline,
  agentesPorId,
  modelosLitellm,
  modeloPadrao,
  onDuplicar,
  onEditar,
  onEditarPassos,
  onExcluir,
  onSalvoAgente,
  acaoEmAndamento,
}: {
  pipeline: PipelineCatalogoApiTranscribrothers;
  agentesPorId: Map<string, AgenteCatalogoApiTranscribrothers>;
  modelosLitellm: string[];
  modeloPadrao: string;
  onDuplicar: (id: string) => void;
  onEditar: (pipeline: PipelineCatalogoApiTranscribrothers) => void;
  onEditarPassos?: (pipeline: PipelineCatalogoApiTranscribrothers) => void;
  onExcluir: (id: string) => void;
  onSalvoAgente: (catalogo: RespostaCatalogoPipelinesApiTranscribrothers) => void;
  acaoEmAndamento: boolean;
}) {
  const { attributes, listeners, setNodeRef, setActivatorNodeRef, transform, transition, isDragging } = useSortable({
    id: pipeline.id,
    disabled: acaoEmAndamento,
  });
  const estilo = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.55 : 1,
  };

  return (
    <div ref={setNodeRef} style={estilo} className="tb-catalogo-pipeline-sortable-item">
      <CardPipelineCatalogoTranscribrothers
        pipeline={pipeline}
        agentesPorId={agentesPorId}
        modelosLitellm={modelosLitellm}
        modeloPadrao={modeloPadrao}
        onDuplicar={onDuplicar}
        onEditar={onEditar}
        onEditarPassos={onEditarPassos}
        onExcluir={onExcluir}
        onSalvoAgente={onSalvoAgente}
        acaoEmAndamento={acaoEmAndamento}
        arrastavel
        alcaArrastar={
          <AlcaArrastarPipelineCustomCatalogoTranscribrothers
            ref={setActivatorNodeRef}
            disabled={acaoEmAndamento}
            {...attributes}
            {...listeners}
          />
        }
      />
    </div>
  );
}

function obterBadgesCaracteristicasAgenteCatalogoTranscribrothers(agente: AgenteCatalogoApiTranscribrothers) {
  const promptsComTexto = agente.prompts.filter((p) => (p.texto || "").trim());
  const soObservacao = agente.prompts.length > 0 && promptsComTexto.length === 0;
  const tipos = new Set(agente.prompts.map((p) => p.tipo));

  const badges: { key: string; rotulo: string; variante: string }[] = [];

  if (soObservacao) {
    badges.push({ key: "sem-llm", rotulo: "Sem LiteLLM", variante: "neutro" });
  } else if (promptsComTexto.length > 0) {
    badges.push({ key: "llm", rotulo: "LiteLLM", variante: "primario" });
  }

  if (agente.prompts.length > 0) {
    badges.push({
      key: "qtd-prompts",
      rotulo: `${agente.prompts.length} prompt${agente.prompts.length === 1 ? "" : "s"}`,
      variante: "contagem",
    });
  }

  if (tipos.has("system")) {
    badges.push({ key: "tipo-system", rotulo: "system", variante: "tipo" });
  }
  if (tipos.has("instrucao") || tipos.has("user")) {
    badges.push({ key: "tipo-instrucao", rotulo: "instrução", variante: "tipo" });
  }

  if (agente.pipelines_ids.length > 1) {
    badges.push({
      key: "reuso",
      rotulo: `Reutilizado · ${agente.pipelines_ids.length} pipelines`,
      variante: "reuso",
    });
  }

  return badges;
}

function CardAgenteCatalogoTranscribrothers({
  agente,
  titulosPipelinePorId,
  modelosLitellm,
  modeloPadrao,
  onDuplicar,
  onExcluir,
  onSalvoAgente,
  acaoEmAndamento,
}: {
  agente: AgenteCatalogoApiTranscribrothers;
  titulosPipelinePorId: Map<string, string>;
  modelosLitellm: string[];
  modeloPadrao: string;
  onDuplicar: (id: string) => void;
  onExcluir: (id: string) => void;
  onSalvoAgente: (catalogo: RespostaCatalogoPipelinesApiTranscribrothers) => void;
  acaoEmAndamento: boolean;
}) {
  const [expandido, setExpandido] = useState(false);
  const [modoEdicao, setModoEdicao] = useState(false);
  const badges = obterBadgesCaracteristicasAgenteCatalogoTranscribrothers(agente);
  const pipelinesRotulos = agente.pipelines_ids
    .map((id) => titulosPipelinePorId.get(id) ?? id)
    .filter(Boolean);

  return (
    <article className="tb-catalogo-agente-card">
      <div className="tb-catalogo-card-acoes-cabecalho tb-catalogo-card-acoes-cabecalho--agente">
        <BadgeOrigemCatalogoTranscribrothers origem={agente.origem} />
        <div className="tb-catalogo-card-botoes">
          <button type="button" className="tb-linkbtn" disabled={acaoEmAndamento} onClick={() => onDuplicar(agente.id)}>
            Duplicar
          </button>
          {agente.editavel ? (
            <>
              <button
                type="button"
                className="tb-linkbtn"
                disabled={acaoEmAndamento}
                onClick={() => {
                  setExpandido(true);
                  setModoEdicao(true);
                }}
              >
                Editar
              </button>
              <button
                type="button"
                className="tb-linkbtn tb-catalogo-btn-excluir"
                disabled={acaoEmAndamento}
                onClick={() => onExcluir(agente.id)}
              >
                Excluir
              </button>
            </>
          ) : null}
        </div>
      </div>
      <button
        type="button"
        className="tb-catalogo-agente-card-cabecalho"
        aria-expanded={expandido}
        onClick={() => {
          setExpandido((v) => {
            const proximo = !v;
            if (!proximo) setModoEdicao(false);
            return proximo;
          });
        }}
      >
        <div className="tb-catalogo-agente-card-cabecalho-texto">
          <h3 className="tb-catalogo-agente-card-titulo">{agente.rotulo}</h3>
          <p className="tb-catalogo-agente-card-id">
            <code className="tb-code-inline">{agente.id}</code>
          </p>
        </div>
        <span className="tb-catalogo-agente-card-expandir" aria-hidden="true">
          {expandido ? "▾" : "▸"}
        </span>
      </button>

      {badges.length > 0 ? (
        <div className="tb-catalogo-agente-badges" aria-label="Características do agente">
          {badges.map((badge) => (
            <span
              key={badge.key}
              className={`tb-catalogo-agente-badge tb-catalogo-agente-badge--${badge.variante}`}
            >
              {badge.rotulo}
            </span>
          ))}
        </div>
      ) : null}

      <p className="tb-catalogo-agente-card-descricao">{agente.descricao}</p>

      {pipelinesRotulos.length > 0 ? (
        <div className="tb-catalogo-agente-badges tb-catalogo-agente-badges--pipelines">
          <span className="tb-catalogo-agente-badges-rotulo">Pipelines:</span>
          {pipelinesRotulos.map((rotulo) => (
            <span key={rotulo} className="tb-catalogo-agente-badge tb-catalogo-agente-badge--pipeline">
              {rotulo}
            </span>
          ))}
        </div>
      ) : null}

      {expandido ? (
        <div className="tb-catalogo-agente-card-detalhe">
          <ComponentePainelEdicaoInlineAgenteCustomCatalogoPipelinesTranscribrothers
            agente={agente}
            modelosLitellm={modelosLitellm}
            modeloPadrao={modeloPadrao}
            modoEdicao={modoEdicao}
            onSalvo={onSalvoAgente}
            onCancelarEdicao={() => setModoEdicao(false)}
            desabilitado={acaoEmAndamento}
          />
        </div>
      ) : null}
    </article>
  );
}

export function ComponentePaginaCatalogoPipelinesDisponiveisComPromptsPorEtapaTranscribrothers({
  onVoltarParaProjeto,
}: ComponentePaginaCatalogoPipelinesDisponiveisComPromptsPorEtapaTranscribrothersProps) {
  const { pushToast } = usarToastFeedbackAcoesUiTranscribrothers();
  const { pedirConfirmacao, elementoDialogoConfirmacao } =
    usarDialogoConfirmacaoAcaoUiSubstituindoWindowConfirmTranscribrothers();
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState<string | null>(null);
  const [catalogo, setCatalogo] = useState<RespostaCatalogoPipelinesApiTranscribrothers | null>(null);
  const [abaAtiva, setAbaAtiva] = useState<AbaCatalogoTranscribrothers>("pipelines");
  const [acaoEmAndamento, setAcaoEmAndamento] = useState(false);
  const [modelosLitellm, setModelosLitellm] = useState<string[]>([]);
  const [modeloPadrao, setModeloPadrao] = useState("");
  const [pipelineEditando, setPipelineEditando] = useState<PipelineCatalogoApiTranscribrothers | null>(null);
  const [pipelineEditandoPassos, setPipelineEditandoPassos] = useState<PipelineCatalogoApiTranscribrothers | null>(null);
  const [modalCriarPipelineAberto, setModalCriarPipelineAberto] = useState(false);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 6 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );

  const recarregarCatalogo = useCallback(async () => {
    setCarregando(true);
    setErro(null);
    try {
      const r = await fetch("/api/pipelines/catalogo");
      if (!r.ok) throw new Error(await r.text());
      setCatalogo((await r.json()) as RespostaCatalogoPipelinesApiTranscribrothers);
    } catch (e: unknown) {
      setCatalogo(null);
      setErro(e instanceof Error ? e.message : String(e));
    } finally {
      setCarregando(false);
    }
  }, []);

  useEffect(() => {
    void recarregarCatalogo();
    void fetch("/api/config/transcribrothers")
      .then((r) => r.json())
      .then((cfg: { litellm_models?: string[]; litellm_model_default?: string }) => {
        setModelosLitellm(cfg.litellm_models ?? []);
        setModeloPadrao(cfg.litellm_model_default ?? "");
      })
      .catch(() => undefined);
  }, [recarregarCatalogo]);

  const aplicarCatalogo = useCallback((d: RespostaCatalogoPipelinesApiTranscribrothers) => {
    setCatalogo(d);
  }, []);

  const duplicarPipeline = useCallback(
    async (id: string) => {
      setAcaoEmAndamento(true);
      try {
        const d = await duplicarPipelineCustomApiTranscribrothers(id);
        aplicarCatalogo(d);
        pushToast("Pipeline duplicada.", "success");
      } catch (e: unknown) {
        pushToast(e instanceof Error ? e.message : "Falha ao duplicar.", "error");
      } finally {
        setAcaoEmAndamento(false);
      }
    },
    [aplicarCatalogo, pushToast],
  );

  const excluirPipeline = useCallback(
    async (id: string) => {
      const ok = await pedirConfirmacao({
        titulo: "Excluir pipeline?",
        mensagem: "Excluir esta pipeline custom? Agentes órfãos também serão removidos.",
        rotuloConfirmar: "Excluir",
        varianteConfirmar: "destrutiva",
      });
      if (!ok) return;
      setAcaoEmAndamento(true);
      try {
        const d = await excluirPipelineCustomApiTranscribrothers(id);
        aplicarCatalogo(d);
        pushToast("Pipeline excluída.", "success");
      } catch (e: unknown) {
        pushToast(e instanceof Error ? e.message : "Falha ao excluir.", "error");
      } finally {
        setAcaoEmAndamento(false);
      }
    },
    [aplicarCatalogo, pushToast, pedirConfirmacao],
  );

  const duplicarAgente = useCallback(
    async (id: string) => {
      setAcaoEmAndamento(true);
      try {
        const d = await duplicarAgenteCustomApiTranscribrothers(id);
        aplicarCatalogo(d);
        pushToast("Variante do agente criada (cópia isolada).", "success");
      } catch (e: unknown) {
        pushToast(e instanceof Error ? e.message : "Falha ao duplicar.", "error");
      } finally {
        setAcaoEmAndamento(false);
      }
    },
    [aplicarCatalogo, pushToast],
  );

  const excluirAgente = useCallback(
    async (id: string) => {
      const ok = await pedirConfirmacao({
        titulo: "Excluir agente?",
        mensagem: "Excluir este agente custom?",
        rotuloConfirmar: "Excluir",
        varianteConfirmar: "destrutiva",
      });
      if (!ok) return;
      setAcaoEmAndamento(true);
      try {
        const d = await excluirAgenteCustomApiTranscribrothers(id);
        aplicarCatalogo(d);
        pushToast("Agente excluído.", "success");
      } catch (e: unknown) {
        pushToast(e instanceof Error ? e.message : "Falha ao excluir.", "error");
      } finally {
        setAcaoEmAndamento(false);
      }
    },
    [aplicarCatalogo, pushToast, pedirConfirmacao],
  );

  const agentesPorId = useMemo(() => {
    const mapa = new Map<string, AgenteCatalogoApiTranscribrothers>();
    for (const agente of catalogo?.agentes ?? []) {
      mapa.set(agente.id, agente);
    }
    return mapa;
  }, [catalogo]);

  const titulosPipelinePorId = useMemo(() => {
    const mapa = new Map<string, string>();
    for (const pipeline of catalogo?.pipelines ?? []) {
      mapa.set(pipeline.id, pipeline.titulo);
    }
    return mapa;
  }, [catalogo]);

  const pipelinesSistema = useMemo(
    () => filtrarPipelinesSistemaCatalogoTranscribrothers(catalogo?.pipelines ?? []),
    [catalogo],
  );

  const pipelinesCustom = useMemo(
    () => ordenarTodasPipelinesCustomUsuarioCatalogoTranscribrothers(catalogo?.pipelines ?? []),
    [catalogo],
  );

  const idsPipelinesCustom = useMemo(() => pipelinesCustom.map((p) => p.id), [pipelinesCustom]);

  const aoFinalizarArrastePipelineCustom = useCallback(
    async (evento: DragEndEvent) => {
      const { active, over } = evento;
      if (!over || active.id === over.id || !catalogo) return;
      const indiceAntigo = pipelinesCustom.findIndex((p) => p.id === active.id);
      const indiceNovo = pipelinesCustom.findIndex((p) => p.id === over.id);
      if (indiceAntigo < 0 || indiceNovo < 0) return;
      const reordenadas = arrayMove(pipelinesCustom, indiceAntigo, indiceNovo);
      const idsOrdenados = reordenadas.map((p) => p.id);
      const mapaOrdem = new Map(idsOrdenados.map((id, indice) => [id, indice]));
      setCatalogo({
        ...catalogo,
        pipelines: catalogo.pipelines.map((p) =>
          p.origem === "usuario" && mapaOrdem.has(p.id) ? { ...p, ordem: mapaOrdem.get(p.id)! } : p,
        ),
      });
      setAcaoEmAndamento(true);
      try {
        const d = await reordenarPipelinesCustomApiTranscribrothers(idsOrdenados);
        aplicarCatalogo(d);
        pushToast("Ordem das pipelines atualizada.", "success");
      } catch (e: unknown) {
        pushToast(e instanceof Error ? e.message : "Falha ao reordenar.", "error");
        void recarregarCatalogo();
      } finally {
        setAcaoEmAndamento(false);
      }
    },
    [aplicarCatalogo, catalogo, pipelinesCustom, pushToast, recarregarCatalogo],
  );

  return (
    <div className="tb-catalogo-pipelines-pagina">
      <header className="tb-catalogo-pipelines-header">
        <div className="tb-catalogo-pipelines-header-inner">
          <div>
            <h1 className="tb-catalogo-pipelines-titulo-pagina" id="tb-catalogo-pipelines-titulo">
              Pipelines e agentes
            </h1>
            <p className="tb-catalogo-pipelines-subtitulo-pagina">
              Fluxos do Transcribrothers: pipelines do sistema são somente leitura. Pipelines custom compartilham
              agentes da biblioteca; duplique um agente só quando quiser uma variante isolada.
            </p>
          </div>
          <div className="tb-catalogo-pipelines-header-acoes tb-modal-job-acoes-finais tb-catalogo-pipelines-header-acoes-modal">
            <button type="button" className="tb-linkbtn" onClick={onVoltarParaProjeto}>
              Voltar ao projeto
            </button>
          </div>
        </div>
      </header>
      <main className="tb-catalogo-pipelines-conteudo" aria-labelledby="tb-catalogo-pipelines-titulo">
        {carregando ? <p className="tb-muted">Carregando catálogo…</p> : null}
        {erro ? <p className="tb-catalogo-pipelines-erro">{erro}</p> : null}
        {catalogo ? (
          <>
            <p className="tb-catalogo-pipelines-build">
              Build do pipeline no servidor:{" "}
              <code className="tb-code-inline">{catalogo.pipeline_identificador || "—"}</code>
            </p>
            <div className="tb-tabs" role="tablist" aria-label="Visualização do catálogo">
              <button
                type="button"
                role="tab"
                className={`tb-tab${abaAtiva === "pipelines" ? " tb-tab-active" : ""}`}
                aria-selected={abaAtiva === "pipelines"}
                onClick={() => setAbaAtiva("pipelines")}
              >
                Pipelines ({catalogo.pipelines.length})
              </button>
              <button
                type="button"
                role="tab"
                className={`tb-tab${abaAtiva === "agentes" ? " tb-tab-active" : ""}`}
                aria-selected={abaAtiva === "agentes"}
                onClick={() => setAbaAtiva("agentes")}
              >
                Agentes ({catalogo.agentes.length})
              </button>
            </div>
            {abaAtiva === "pipelines" ? (
              <>
                <section className="tb-catalogo-secao-pipelines" aria-labelledby="tb-catalogo-secao-sistema">
                  <h2 id="tb-catalogo-secao-sistema" className="tb-catalogo-secao-pipelines-titulo">
                    Pipelines do sistema
                  </h2>
                  <p className="tb-muted tb-catalogo-secao-pipelines-lead">
                    Somente leitura. Use Duplicar para criar uma cópia editável em Minhas pipelines.
                  </p>
                  {pipelinesSistema.map((pipeline) => (
                    <CardPipelineCatalogoTranscribrothers
                      key={pipeline.id}
                      pipeline={pipeline}
                      agentesPorId={agentesPorId}
                      modelosLitellm={modelosLitellm}
                      modeloPadrao={modeloPadrao}
                      onDuplicar={(id) => void duplicarPipeline(id)}
                      onEditar={setPipelineEditando}
                      onExcluir={(id) => void excluirPipeline(id)}
                      onSalvoAgente={aplicarCatalogo}
                      acaoEmAndamento={acaoEmAndamento}
                    />
                  ))}
                </section>

                <section className="tb-catalogo-secao-pipelines" aria-labelledby="tb-catalogo-secao-minhas">
                  <div className="tb-catalogo-secao-pipelines-cabecalho">
                    <div>
                      <h2 id="tb-catalogo-secao-minhas" className="tb-catalogo-secao-pipelines-titulo">
                        Minhas pipelines
                      </h2>
                      <p className="tb-muted tb-catalogo-secao-pipelines-lead">
                        Arraste para definir a ordem exibida no upload e em «Gerar outro formato».
                      </p>
                    </div>
                    <button
                      type="button"
                      className="tb-primary"
                      disabled={acaoEmAndamento}
                      onClick={() => setModalCriarPipelineAberto(true)}
                    >
                      Nova pipeline
                    </button>
                  </div>
                  {pipelinesCustom.length === 0 ? (
                    <p className="tb-muted">Nenhuma pipeline custom ainda. Crie uma a partir de um molde.</p>
                  ) : (
                    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={(e) => void aoFinalizarArrastePipelineCustom(e)}>
                      <SortableContext items={idsPipelinesCustom} strategy={verticalListSortingStrategy}>
                        {pipelinesCustom.map((pipeline) => (
                          <CardPipelineCustomOrdenavelCatalogoTranscribrothers
                            key={pipeline.id}
                            pipeline={pipeline}
                            agentesPorId={agentesPorId}
                            modelosLitellm={modelosLitellm}
                            modeloPadrao={modeloPadrao}
                            onDuplicar={(id) => void duplicarPipeline(id)}
                            onEditar={setPipelineEditando}
                            onEditarPassos={setPipelineEditandoPassos}
                            onExcluir={(id) => void excluirPipeline(id)}
                            onSalvoAgente={aplicarCatalogo}
                            acaoEmAndamento={acaoEmAndamento}
                          />
                        ))}
                      </SortableContext>
                    </DndContext>
                  )}
                </section>
              </>
            ) : (
              <div className="tb-catalogo-agentes-grade">
                {catalogo.agentes.map((agente) => (
                  <CardAgenteCatalogoTranscribrothers
                    key={agente.id}
                    agente={agente}
                    titulosPipelinePorId={titulosPipelinePorId}
                    modelosLitellm={modelosLitellm}
                    modeloPadrao={modeloPadrao}
                    onDuplicar={(id) => void duplicarAgente(id)}
                    onExcluir={(id) => void excluirAgente(id)}
                    onSalvoAgente={aplicarCatalogo}
                    acaoEmAndamento={acaoEmAndamento}
                  />
                ))}
              </div>
            )}
            <ComponenteModalEditorPipelineCustomMetadadosTranscribrothers
              aberto={pipelineEditando !== null}
              pipeline={pipelineEditando}
              onFechar={() => setPipelineEditando(null)}
              onSalvo={aplicarCatalogo}
            />
            <ComponenteModalCriarPipelineCustomEscolherMoldeEMetadadosTranscribrothers
              aberto={modalCriarPipelineAberto}
              onFechar={() => setModalCriarPipelineAberto(false)}
              onCriada={aplicarCatalogo}
            />
            <ComponenteModalEditarPassosPipelineCustomAdicionarRemoverReordenarTranscribrothers
              aberto={pipelineEditandoPassos !== null}
              pipeline={
                pipelineEditandoPassos
                  ? (catalogo.pipelines.find((p) => p.id === pipelineEditandoPassos.id) ?? pipelineEditandoPassos)
                  : null
              }
              agentes={catalogo.agentes}
              onFechar={() => setPipelineEditandoPassos(null)}
              onAtualizado={aplicarCatalogo}
            />
          </>
        ) : null}
      </main>
      {elementoDialogoConfirmacao}
    </div>
  );
}
