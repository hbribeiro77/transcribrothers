/** Tipos da resposta de GET /api/pipelines/catalogo */

export type PromptCatalogoPassoPipelineApiTranscribrothers = {
  chave: string;
  tipo: "system" | "user" | "instrucao" | "observacao";
  rotulo: string;
  texto: string;
  observacao?: string | null;
  fonte_modulo?: string | null;
};

export type AgenteCatalogoApiTranscribrothers = {
  id: string;
  rotulo: string;
  descricao: string;
  handler_chave?: string | null;
  origem?: "sistema" | "usuario";
  editavel?: boolean;
  executavel?: boolean;
  copiado_de?: string | null;
  modelo_litellm?: string | null;
  prompts: PromptCatalogoPassoPipelineApiTranscribrothers[];
  pipelines_ids: string[];
};

export type PassoCatalogoPipelineApiTranscribrothers = {
  id: string;
  agente_id: string;
  rotulo: string;
  descricao: string;
};

export type TipoEntradaMidiaCatalogoApiTranscribrothers = "video" | "audio";

export type PipelineCatalogoApiTranscribrothers = {
  id: string;
  titulo: string;
  descricao: string;
  origem?: "sistema" | "usuario";
  editavel?: boolean;
  executavel?: boolean;
  copiado_de?: string | null;
  ordem?: number | null;
  entradas_aceitas?: TipoEntradaMidiaCatalogoApiTranscribrothers[];
  passos: PassoCatalogoPipelineApiTranscribrothers[];
};

export type RespostaCatalogoPipelinesApiTranscribrothers = {
  pipeline_identificador: string;
  agentes: AgenteCatalogoApiTranscribrothers[];
  pipelines: PipelineCatalogoApiTranscribrothers[];
};
