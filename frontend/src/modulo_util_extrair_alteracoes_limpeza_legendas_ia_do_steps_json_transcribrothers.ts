/** Extrai o resumo e o antes/depois da limpeza IA de legendas em `steps_json`. */

import {
  normalizarDiretrizConteudoLegendasTranscribrothers,
  rotuloDiretrizConteudoLegendasParaUiTranscribrothers,
} from "./modulo_diretriz_conteudo_legendas_narracao_transcribrothers.ts";

export type AlteracaoLimpezaLegendaIaUiTranscribrothers = {
  indice: number;
  antes: string;
  depois: string;
};

export type ResumoLimpezaLegendasIaStepsJsonTranscribrothers = {
  ok: boolean | null;
  status: string;
  mensagem: string;
  modelo: string;
  modelosTentados: string[];
  quantidadeCues: number;
  quantidadeAlteradas: number;
  usouFallbackOriginais: boolean;
  diretrizConteudo: string;
  diretrizConteudoRotulo: string;
  alteracoes: AlteracaoLimpezaLegendaIaUiTranscribrothers[];
};

export function extrairResumoLimpezaLegendasIaDoStepsJsonTranscribrothers(
  steps: Record<string, unknown> | null | undefined,
): ResumoLimpezaLegendasIaStepsJsonTranscribrothers | null {
  // Corrida do modal «edições» não usa limpeza IA — não reexibir resumo antigo.
  if (steps?.pipeline_origem_corrida === "edicoes_modal") return null;
  if (steps?.pipeline_fase === "video_narrado_gerando_com_edicoes_modal") return null;
  const raw = steps?.limpeza_legendas_ia_antes_tts;
  if (!raw || typeof raw !== "object") return null;
  const o = raw as Record<string, unknown>;
  const alteracoes: AlteracaoLimpezaLegendaIaUiTranscribrothers[] = [];
  if (Array.isArray(o.alteracoes)) {
    for (const item of o.alteracoes) {
      if (!item || typeof item !== "object") continue;
      const a = item as Record<string, unknown>;
      const indice = typeof a.indice === "number" ? a.indice : Number(a.indice);
      if (!Number.isFinite(indice)) continue;
      const antes = typeof a.antes === "string" ? a.antes : "";
      const depois = typeof a.depois === "string" ? a.depois : "";
      alteracoes.push({ indice, antes, depois });
    }
  }
  alteracoes.sort((x, y) => x.indice - y.indice);
  const modelosTentados = Array.isArray(o.modelos_tentados)
    ? o.modelos_tentados.filter((m): m is string => typeof m === "string" && m.trim().length > 0)
    : [];
  const diretrizRaw =
    typeof o.diretriz_conteudo === "string"
      ? o.diretriz_conteudo
      : typeof steps?.pipeline_video_narrado_diretriz_conteudo_legendas === "string"
        ? steps.pipeline_video_narrado_diretriz_conteudo_legendas
        : "";
  const diretrizConteudo = normalizarDiretrizConteudoLegendasTranscribrothers(diretrizRaw);
  return {
    ok: typeof o.ok === "boolean" ? o.ok : null,
    status: typeof o.status === "string" ? o.status : "",
    mensagem: typeof o.mensagem === "string" ? o.mensagem : "",
    modelo: typeof o.modelo === "string" ? o.modelo : "",
    modelosTentados,
    quantidadeCues:
      typeof o.quantidade_cues === "number" && Number.isFinite(o.quantidade_cues)
        ? o.quantidade_cues
        : 0,
    quantidadeAlteradas:
      typeof o.quantidade_alteradas === "number" && Number.isFinite(o.quantidade_alteradas)
        ? o.quantidade_alteradas
        : alteracoes.length,
    usouFallbackOriginais: o.usou_fallback_originais === true,
    diretrizConteudo,
    diretrizConteudoRotulo: rotuloDiretrizConteudoLegendasParaUiTranscribrothers(diretrizConteudo),
    alteracoes,
  };
}
