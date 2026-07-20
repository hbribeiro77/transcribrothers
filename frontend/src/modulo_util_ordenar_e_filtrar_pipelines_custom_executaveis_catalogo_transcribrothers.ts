import type { PipelineCatalogoApiTranscribrothers } from "./tipos_catalogo_pipelines_api_transcribrothers.ts";

export function filtrarPipelinesCustomUsuarioCatalogoTranscribrothers(
  pipelines: PipelineCatalogoApiTranscribrothers[],
): PipelineCatalogoApiTranscribrothers[] {
  return pipelines.filter((p) => p.origem === "usuario");
}

export function filtrarPipelinesSistemaCatalogoTranscribrothers(
  pipelines: PipelineCatalogoApiTranscribrothers[],
): PipelineCatalogoApiTranscribrothers[] {
  return pipelines.filter((p) => p.origem !== "usuario");
}

export function ordenarPipelinesCustomPorOrdemExibicaoCatalogoTranscribrothers(
  pipelines: PipelineCatalogoApiTranscribrothers[],
): PipelineCatalogoApiTranscribrothers[] {
  return [...pipelines].sort((a, b) => {
    const ordemA = a.ordem ?? Number.MAX_SAFE_INTEGER;
    const ordemB = b.ordem ?? Number.MAX_SAFE_INTEGER;
    if (ordemA !== ordemB) return ordemA - ordemB;
    return a.titulo.localeCompare(b.titulo, "pt-BR");
  });
}

export function filtrarEOrdenarPipelinesCustomExecutaveisCatalogoTranscribrothers(
  pipelines: PipelineCatalogoApiTranscribrothers[],
): PipelineCatalogoApiTranscribrothers[] {
  return ordenarPipelinesCustomPorOrdemExibicaoCatalogoTranscribrothers(
    filtrarPipelinesCustomUsuarioCatalogoTranscribrothers(pipelines).filter((p) => p.executavel !== false),
  );
}

export function ordenarTodasPipelinesCustomUsuarioCatalogoTranscribrothers(
  pipelines: PipelineCatalogoApiTranscribrothers[],
): PipelineCatalogoApiTranscribrothers[] {
  return ordenarPipelinesCustomPorOrdemExibicaoCatalogoTranscribrothers(
    filtrarPipelinesCustomUsuarioCatalogoTranscribrothers(pipelines),
  );
}

const ROTULOS_MOLDE_PIPELINE_SISTEMA_TRANSCRIBROTHERS: Record<string, string> = {
  pipeline_inicial_tutorial: "Tutorial",
  pipeline_inicial_notas_proposta: "Notas de proposta",
  pipeline_inicial_reproducao_bug: "Reprodução de bug",
};

export function obterRotuloMoldePipelineCustomCatalogoTranscribrothers(
  copiadoDe: string | null | undefined,
): string {
  const chave = (copiadoDe || "").trim();
  return ROTULOS_MOLDE_PIPELINE_SISTEMA_TRANSCRIBROTHERS[chave] ?? (chave || "—");
}
