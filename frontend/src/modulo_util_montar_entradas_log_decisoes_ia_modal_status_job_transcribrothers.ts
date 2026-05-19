/** Entradas do log de decisões/respostas da IA exibidas na modal de status do job. */

export type EntradaLogDecisaoIaModalStatusJobTranscribrothers = {
  em: string;
  etapa: string;
  resumo: string;
  sucesso: boolean;
  modelo?: string;
  detalhe?: string;
  metadados?: Record<string, unknown>;
};

const CHAVE_LOG_DECISOES_IA_PIPELINE = "log_decisoes_ia_pipeline";

const ROTULOS_ETAPA_LOG_DECISOES_IA_PT_BR: Record<string, string> = {
  interpretacao_escopo_edicao_secao: "Interpretação do pedido (escopo)",
  refino_escopo_edicao_secao: "Refino do escopo",
  geracao_tutorial_markdown: "Geração do tutorial",
  regeneracao_tutorial_markdown: "Regeneração do tutorial",
  revisao_profunda_analista_plano: "Revisão profunda — plano",
  revisao_profunda_worker_topico: "Revisão profunda — tópico",
  revisao_profunda_editor_final: "Revisão profunda — consolidação",
  verificacao_sustentacao_tutorial: "Auditor — chamada ao modelo",
  verificacao_sustentacao_decisao: "Auditor — decisão",
  verificacao_redundancia_secao_markdown: "Redundância entre seções — chamada",
  verificacao_redundancia_decisao: "Redundância — decisão",
  correcao_redundancia_secao_markdown: "Correção automática de redundância",
  regeneracao_secao_markdown: "Edição parcial — seção",
  regeneracao_zona_escopo_secao: "Edição parcial — trecho",
  chat_completions: "Chamada ao modelo",
};

function normalizarEntradaLogDecisoesIaTranscribrothers(
  raw: unknown,
  indice: number,
): EntradaLogDecisaoIaModalStatusJobTranscribrothers | null {
  if (!raw || typeof raw !== "object") return null;
  const o = raw as Record<string, unknown>;
  const etapa = typeof o.etapa === "string" ? o.etapa.trim() : "";
  const resumo = typeof o.resumo === "string" ? o.resumo.trim() : "";
  if (!etapa && !resumo) return null;
  const em =
    typeof o.em === "string" && o.em.trim()
      ? o.em.trim()
      : `entrada-${indice + 1}`;
  return {
    em,
    etapa: etapa || "ia",
    resumo: resumo || "(sem resumo)",
    sucesso: o.sucesso !== false,
    modelo: typeof o.modelo === "string" && o.modelo.trim() ? o.modelo.trim() : undefined,
    detalhe: typeof o.detalhe === "string" && o.detalhe.trim() ? o.detalhe.trim() : undefined,
    metadados:
      o.metadados && typeof o.metadados === "object" && !Array.isArray(o.metadados)
        ? (o.metadados as Record<string, unknown>)
        : undefined,
  };
}

function sintetizarEntradasLegadasDeStepsJsonTranscribrothers(
  steps: Record<string, unknown>,
): EntradaLogDecisaoIaModalStatusJobTranscribrothers[] {
  const saida: EntradaLogDecisaoIaModalStatusJobTranscribrothers[] = [];

  const interp = steps.interpretacao_escopo_edicao_secao_markdown;
  if (interp && typeof interp === "object") {
    const blob = interp as Record<string, unknown>;
    const explicacao =
      typeof blob.explicacao_curta === "string" ? blob.explicacao_curta.trim() : "";
    if (explicacao) {
      saida.push({
        em: "legado-interpretacao",
        etapa: "interpretacao_escopo_edicao_secao",
        resumo: explicacao,
        sucesso: true,
        metadados: {
          modo: blob.modo_escopo_edicao,
          confianca: blob.confianca,
          legado: true,
        },
      });
    }
  }

  const ver = steps.verificacao_sustentacao_tutorial;
  if (ver && typeof ver === "object") {
    const v = ver as Record<string, unknown>;
    if (!v.omitida) {
      saida.push({
        em: typeof v.executado_em === "string" ? v.executado_em : "legado-verificacao",
        etapa: "verificacao_sustentacao_decisao",
        resumo:
          (typeof v.classificacao_global === "string" && v.classificacao_global) ||
          (typeof v.mensagem_resumo === "string" && v.mensagem_resumo) ||
          (v.sucesso === false ? "Falhou" : "Concluída"),
        sucesso: v.sucesso !== false,
        detalhe: typeof v.mensagem_resumo === "string" ? v.mensagem_resumo : undefined,
        metadados: { legado: true },
      });
    }
  }

  return saida;
}

export function montarEntradasLogDecisoesIaParaModalStatusJobTranscribrothers(
  stepsJson: Record<string, unknown> | null | undefined,
): EntradaLogDecisaoIaModalStatusJobTranscribrothers[] {
  const steps = stepsJson ?? {};
  const raw = steps[CHAVE_LOG_DECISOES_IA_PIPELINE];
  const explicitas: EntradaLogDecisaoIaModalStatusJobTranscribrothers[] = [];
  if (Array.isArray(raw)) {
    raw.forEach((item, i) => {
      const norm = normalizarEntradaLogDecisoesIaTranscribrothers(item, i);
      if (norm) explicitas.push(norm);
    });
  }
  if (explicitas.length > 0) return explicitas;
  return sintetizarEntradasLegadasDeStepsJsonTranscribrothers(steps);
}

export function rotuloEtapaLogDecisoesIaEmPtBrTranscribrothers(etapa: string): string {
  const chave = (etapa || "").trim();
  return ROTULOS_ETAPA_LOG_DECISOES_IA_PT_BR[chave] ?? chave.replaceAll("_", " ");
}

export function formatarDataHoraLogDecisoesIaParaExibicaoTranscribrothers(emIso: string): string {
  if (!emIso || emIso.startsWith("legado-")) return "";
  const d = new Date(emIso);
  if (Number.isNaN(d.getTime())) return emIso;
  return d.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}
