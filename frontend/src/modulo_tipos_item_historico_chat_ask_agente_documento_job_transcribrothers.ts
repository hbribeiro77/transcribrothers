/** Espelho do item persistido em historico_chat_ask_agente_documento_job.json. */

export type CitacaoItemHistoricoChatAskDocumentoJobTranscribrothers = {
  tipo: string;
  rotulo: string;
  instante_segundos: number | null;
  heading: string | null;
};

export type ImagemItemHistoricoChatAskDocumentoJobTranscribrothers = {
  caminho_relativo: string;
  url: string;
  instante_segundos: number | null;
  origem: string;
};

export type PropostaFerramentaChatAgenteDocumentoJobTranscribrothers = {
  nome: string;
  titulo_secao_heading: string | null;
  instrucoes: string | null;
  caminhos_imagens: string[];
};

export type ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers = {
  papel: string;
  modo: string;
  texto: string;
  criado_em: string;
  citacoes: CitacaoItemHistoricoChatAskDocumentoJobTranscribrothers[];
  imagens: ImagemItemHistoricoChatAskDocumentoJobTranscribrothers[];
  estado: string | null;
  tipo_pipeline: string | null;
  proposta_ferramenta: PropostaFerramentaChatAgenteDocumentoJobTranscribrothers | null;
  propostas_ferramenta: PropostaFerramentaChatAgenteDocumentoJobTranscribrothers[];
  executar_proposta: boolean;
};

export type RespostaEnviarMensagemChatAskDocumentoJobApiTranscribrothers = {
  texto: string;
  citacoes: CitacaoItemHistoricoChatAskDocumentoJobTranscribrothers[];
  imagens: ImagemItemHistoricoChatAskDocumentoJobTranscribrothers[];
  historico: ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers[];
};

export type RespostaEnviarMensagemChatAgenteDocumentoJobApiTranscribrothers = {
  texto: string;
  citacoes: CitacaoItemHistoricoChatAskDocumentoJobTranscribrothers[];
  imagens: ImagemItemHistoricoChatAskDocumentoJobTranscribrothers[];
  proposta_ferramenta: PropostaFerramentaChatAgenteDocumentoJobTranscribrothers | null;
  propostas_ferramenta: PropostaFerramentaChatAgenteDocumentoJobTranscribrothers[];
  executar_proposta: boolean;
  historico: ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers[];
};

export type MensagemPainelHistoricoChatAskAgenteDocumentoJobTranscribrothers = {
  id: string;
  papel: "usuario" | "assistente" | "agente";
  texto: string;
  citacoes: CitacaoItemHistoricoChatAskDocumentoJobTranscribrothers[];
  imagens: ImagemItemHistoricoChatAskDocumentoJobTranscribrothers[];
  estado: string | null;
  tipo_pipeline: string | null;
  proposta_ferramenta: PropostaFerramentaChatAgenteDocumentoJobTranscribrothers | null;
  propostas_ferramenta: PropostaFerramentaChatAgenteDocumentoJobTranscribrothers[];
  executar_proposta: boolean;
};

/** O turno agente em geração sai da lista quando um turno posterior, com o mesmo texto, já está em preview_pronta ou falhou. */
export function itensHistoricoChatAskAgenteOcultandoGerandoSubstituidoPorPreviewProntaTranscribrothers(
  itens: ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers[],
): ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers[] {
  return itens.filter((item, indice) => {
    if (item.papel !== "agente" || item.estado !== "gerando") return true;
    return !itens.slice(indice + 1).some(
      (outro) =>
        outro.papel === "agente" &&
        (outro.estado === "preview_pronta" || outro.estado === "falhou") &&
        outro.texto === item.texto,
    );
  });
}

/** Job saiu de generating_tutorial sem objeto de prévia e o último turno agente ainda está gerando. */
export function turnoAgenteGerandoDevePersistirEstadoFalhouSemPreviaTranscribrothers(entrada: {
  statusJob: string | null | undefined;
  temObjetoPreview: boolean;
  estadoUltimoTurnoAgente: string | null | undefined;
}): boolean {
  if (entrada.temObjetoPreview) return false;
  if (entrada.statusJob !== "failed" && entrada.statusJob !== "completed") return false;
  return entrada.estadoUltimoTurnoAgente === "gerando";
}

function _texto(valor: unknown): string {
  return typeof valor === "string" ? valor : "";
}

function _numeroOuNull(valor: unknown): number | null {
  return typeof valor === "number" && Number.isFinite(valor) ? valor : null;
}

export function normalizarCitacaoItemHistoricoChatAskDocumentoJobTranscribrothers(
  raw: unknown,
): CitacaoItemHistoricoChatAskDocumentoJobTranscribrothers | null {
  if (!raw || typeof raw !== "object") return null;
  const o = raw as Record<string, unknown>;
  return {
    tipo: _texto(o.tipo),
    rotulo: _texto(o.rotulo),
    instante_segundos: _numeroOuNull(o.instante_segundos),
    heading: typeof o.heading === "string" ? o.heading : null,
  };
}

export function normalizarImagemItemHistoricoChatAskDocumentoJobTranscribrothers(
  raw: unknown,
): ImagemItemHistoricoChatAskDocumentoJobTranscribrothers | null {
  if (!raw || typeof raw !== "object") return null;
  const o = raw as Record<string, unknown>;
  return {
    caminho_relativo: _texto(o.caminho_relativo),
    url: _texto(o.url),
    instante_segundos: _numeroOuNull(o.instante_segundos),
    origem: _texto(o.origem),
  };
}

export function normalizarItemHistoricoChatAskAgenteDocumentoJobTranscribrothers(
  raw: unknown,
): ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers | null {
  if (!raw || typeof raw !== "object") return null;
  const o = raw as Record<string, unknown>;
  if (typeof o.papel !== "string" || typeof o.modo !== "string") return null;
  if (typeof o.texto !== "string" || typeof o.criado_em !== "string") return null;
  const citacoes = Array.isArray(o.citacoes)
    ? o.citacoes
        .map(normalizarCitacaoItemHistoricoChatAskDocumentoJobTranscribrothers)
        .filter((c): c is CitacaoItemHistoricoChatAskDocumentoJobTranscribrothers => c != null)
    : [];
  const imagens = Array.isArray(o.imagens)
    ? o.imagens
        .map(normalizarImagemItemHistoricoChatAskDocumentoJobTranscribrothers)
        .filter((img): img is ImagemItemHistoricoChatAskDocumentoJobTranscribrothers => img != null)
    : [];
  return {
    papel: o.papel,
    modo: o.modo,
    texto: o.texto,
    criado_em: o.criado_em,
    citacoes,
    imagens,
    estado: typeof o.estado === "string" ? o.estado : null,
    tipo_pipeline: typeof o.tipo_pipeline === "string" ? o.tipo_pipeline : null,
    proposta_ferramenta: normalizarPropostaFerramentaChatAgenteDocumentoJobTranscribrothers(
      o.proposta_ferramenta,
    ),
    propostas_ferramenta: normalizarListaPropostasFerramentaChatAgenteDocumentoTranscribrothers(
      o.propostas_ferramenta,
    ),
    executar_proposta: o.executar_proposta === true,
  };
}

export function normalizarPropostaFerramentaChatAgenteDocumentoJobTranscribrothers(
  raw: unknown,
): PropostaFerramentaChatAgenteDocumentoJobTranscribrothers | null {
  if (!raw || typeof raw !== "object") return null;
  const o = raw as Record<string, unknown>;
  if (typeof o.nome !== "string" || !o.nome.trim()) return null;
  return {
    nome: o.nome.trim(),
    titulo_secao_heading: typeof o.titulo_secao_heading === "string" ? o.titulo_secao_heading : null,
    instrucoes: typeof o.instrucoes === "string" ? o.instrucoes : null,
    caminhos_imagens: mesclarCaminhosImagensPropostaChatAgenteDocumentoTranscribrothers(
      Array.isArray(o.caminhos_imagens)
        ? o.caminhos_imagens.filter((item): item is string => typeof item === "string")
        : [],
    ),
  };
}

export function mesclarCaminhosImagensPropostaChatAgenteDocumentoTranscribrothers(
  ...listas: Array<readonly string[] | null | undefined>
): string[] {
  const vistos = new Set<string>();
  const saida: string[] = [];
  for (const lista of listas) {
    for (const cru of lista ?? []) {
      const rel = cru.trim();
      if (!rel || vistos.has(rel)) continue;
      vistos.add(rel);
      saida.push(rel);
    }
  }
  return saida;
}

export function caminhosRelativosDeImagensHistoricoChatAskTranscribrothers(
  imagens: ImagemItemHistoricoChatAskDocumentoJobTranscribrothers[] | null | undefined,
): string[] {
  return mesclarCaminhosImagensPropostaChatAgenteDocumentoTranscribrothers(
    (imagens ?? []).map((imagem) => imagem.caminho_relativo),
  );
}

export function normalizarListaHistoricoChatAskAgenteDocumentoJobTranscribrothers(
  raw: unknown,
): ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers[] {
  if (!Array.isArray(raw)) return [];
  return raw
    .map(normalizarItemHistoricoChatAskAgenteDocumentoJobTranscribrothers)
    .filter((item): item is ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers => item != null);
}

export function mensagensPainelAPartirDoHistoricoChatAskAgenteDocumentoJobTranscribrothers(
  itens: ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers[],
): MensagemPainelHistoricoChatAskAgenteDocumentoJobTranscribrothers[] {
  return itensHistoricoChatAskAgenteOcultandoGerandoSubstituidoPorPreviewProntaTranscribrothers(itens).map(
    (item, indice) => ({
      id: `${item.criado_em}-${indice}-${item.papel}`,
      papel: item.papel === "usuario" || item.papel === "agente" ? item.papel : "assistente",
      texto: item.texto,
      citacoes: item.citacoes,
      imagens: item.imagens,
      estado: item.estado,
      tipo_pipeline: item.tipo_pipeline,
      proposta_ferramenta: item.proposta_ferramenta,
      propostas_ferramenta: item.propostas_ferramenta,
      executar_proposta: item.executar_proposta,
    }),
  );
}

export function normalizarListaPropostasFerramentaChatAgenteDocumentoTranscribrothers(
  raw: unknown,
): PropostaFerramentaChatAgenteDocumentoJobTranscribrothers[] {
  if (!Array.isArray(raw)) return [];
  return raw
    .map(normalizarPropostaFerramentaChatAgenteDocumentoJobTranscribrothers)
    .filter((item): item is PropostaFerramentaChatAgenteDocumentoJobTranscribrothers => item != null);
}

export function resolverPropostasEdicaoParcialParaAplicarChatAgenteTranscribrothers(
  proposta: PropostaFerramentaChatAgenteDocumentoJobTranscribrothers | null | undefined,
  propostas: PropostaFerramentaChatAgenteDocumentoJobTranscribrothers[] | null | undefined,
): PropostaFerramentaChatAgenteDocumentoJobTranscribrothers[] {
  const lote = (propostas ?? []).filter((item) => item.nome === "edicao_parcial");
  if (lote.length > 0) return lote;
  if (proposta?.nome === "edicao_parcial") return [proposta];
  return [];
}

/** Chip da bolha: tempo da transcrição ou heading do Markdown. */
export function rotuloChipCitacaoChatAskDocumentoJobTranscribrothers(
  citacao: CitacaoItemHistoricoChatAskDocumentoJobTranscribrothers,
): string {
  if (citacao.tipo === "transcricao") return citacao.rotulo.trim();
  const heading = (citacao.heading ?? "").trim();
  if (heading) return heading.startsWith("#") ? heading : `## ${heading}`;
  return citacao.rotulo.trim();
}

function parsearRotuloTempoCitacaoChatAskParaSegundosTranscribrothers(
  rotulo: string,
): number | null {
  const limpo = rotulo.trim();
  if (!/^\d{1,2}:\d{2}(?::\d{2}(?:\.\d+)?)?$/.test(limpo)) return null;
  const partes = limpo.split(":");
  const numeros = partes.map((parte) => Number(parte));
  if (numeros.some((n) => !Number.isFinite(n))) return null;
  if (partes.length === 3) {
    return numeros[0] * 3600 + numeros[1] * 60 + numeros[2];
  }
  return numeros[0] * 60 + numeros[1];
}

export function instanteSegundosParaSeekCitacaoChatAskTranscribrothers(
  citacao: CitacaoItemHistoricoChatAskDocumentoJobTranscribrothers,
): number | null {
  if (
    typeof citacao.instante_segundos === "number" &&
    Number.isFinite(citacao.instante_segundos) &&
    citacao.instante_segundos >= 0
  ) {
    return citacao.instante_segundos;
  }
  if (citacao.tipo !== "transcricao") return null;
  return parsearRotuloTempoCitacaoChatAskParaSegundosTranscribrothers(citacao.rotulo);
}

export function segundosDeHrefTimestampTutorialOuChatTranscribrothers(
  href: string | null | undefined,
): number | null {
  const bruto = (href || "").trim();
  if (!bruto.startsWith("?t=")) return null;
  const segundos = Number.parseFloat(bruto.slice(3));
  if (!Number.isFinite(segundos) || segundos < 0) return null;
  return segundos;
}

export function citacaoChatAskDeveAparecerComoChipTranscribrothers(
  citacao: CitacaoItemHistoricoChatAskDocumentoJobTranscribrothers,
  textoBolha?: string,
): boolean {
  if (citacao.tipo !== "transcricao") return false;
  if (typeof textoBolha === "string" && textoBolha.includes("?t=")) return false;
  return instanteSegundosParaSeekCitacaoChatAskTranscribrothers(citacao) != null;
}

export function propostaFerramentaChatAgenteDeveMostrarBotaoAplicarNaBolhaTranscribrothers(args: {
  temProposta: boolean;
  executarProposta: boolean;
  estado: string | null | undefined;
  nomeFerramenta?: string | null;
  ehUltimaMensagemAgente?: boolean;
}): boolean {
  if (!args.temProposta) return false;
  if (args.executarProposta) return false;
  if (args.ehUltimaMensagemAgente === false) return false;
  if (args.estado === "gerando" || args.estado === "falhou" || args.estado === "preview_pronta") {
    return false;
  }
  return true;
}
