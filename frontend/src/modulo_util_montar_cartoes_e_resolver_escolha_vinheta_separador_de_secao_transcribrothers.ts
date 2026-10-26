import {
  EFEITO_PADRAO_DA_VINHETA,
  type EfeitoDaVinheta,
} from "./previa_ao_vivo_cena_vinheta_copiada_do_app_vinhetas/modulo_amostragem_dos_modelos_de_abertura_da_vinheta.ts";

export function normalizarEfeitoDaPreviaAoVivoVinhetaTranscribrothers(
  valor: string | null | undefined,
): EfeitoDaVinheta {
  if (
    valor === "planos-que-abrem-espaco" ||
    valor === "linhas-que-desenham-o-lugar" ||
    valor === "barras-que-se-cruzam"
  ) {
    return valor;
  }
  return EFEITO_PADRAO_DA_VINHETA;
}

export type ItemModeloVinhetaSeparadorApiTranscribrothers = {
  id: string;
  nome: string;
  url_preview?: string | null;
  urlPreview?: string | null;
  preview_url?: string | null;
  url_video?: string | null;
};

export type ItemProjetoVinhetaSeparadorApiTranscribrothers = {
  id: string;
  titulo: string;
  efeito?: string | null;
  url_preview?: string | null;
  urlPreview?: string | null;
  preview_url?: string | null;
  url_video?: string | null;
};

export type CartaoVinhetaSeparadorDeSecaoTranscribrothers = {
  chave: string;
  rotulo: string;
  grupo: "modelo" | "salva";
  urlPreview: string | null;
  efeitoPrevia: EfeitoDaVinheta;
};

export type EscolhaDeVinhetaParaSeparadorTranscribrothers = {
  titulo: string;
  efeito: string | null;
  vinhetaId: string | null;
  duracaoSegundos?: number;
  presencaDaImagem?: number;
  cores?: {
    fundo: string;
    plano_principal: string;
    plano_destaque: string;
    texto: string;
  };
};

export function lerUrlPreviewOpcionalDoItemVinhetaApiTranscribrothers(
  item: ItemModeloVinhetaSeparadorApiTranscribrothers | ItemProjetoVinhetaSeparadorApiTranscribrothers,
): string | null {
  const candidatas = [item.url_preview, item.urlPreview, item.preview_url, item.url_video];
  for (const valor of candidatas) {
    if (typeof valor === "string" && valor.trim()) return valor.trim();
  }
  return null;
}

export function montarCartoesVinhetaSeparadorDeSecaoTranscribrothers(lista: {
  modelos: ItemModeloVinhetaSeparadorApiTranscribrothers[];
  projetos: ItemProjetoVinhetaSeparadorApiTranscribrothers[];
}): CartaoVinhetaSeparadorDeSecaoTranscribrothers[] {
  return [
    ...lista.modelos.map((modelo) => ({
      chave: `modelo:${modelo.id}`,
      rotulo: modelo.nome,
      grupo: "modelo" as const,
      urlPreview: lerUrlPreviewOpcionalDoItemVinhetaApiTranscribrothers(modelo),
      efeitoPrevia: normalizarEfeitoDaPreviaAoVivoVinhetaTranscribrothers(modelo.id),
    })),
    ...lista.projetos.map((projeto) => ({
      chave: `salva:${projeto.id}`,
      rotulo: projeto.titulo,
      grupo: "salva" as const,
      urlPreview: lerUrlPreviewOpcionalDoItemVinhetaApiTranscribrothers(projeto),
      efeitoPrevia: normalizarEfeitoDaPreviaAoVivoVinhetaTranscribrothers(projeto.efeito),
    })),
  ];
}

export function resolverEscolhaVinhetaAPartirDaChaveDoCartaoTranscribrothers(args: {
  chave: string;
  titulo: string;
}): EscolhaDeVinhetaParaSeparadorTranscribrothers {
  const titulo = args.titulo.trim();
  if (args.chave.startsWith("salva:")) {
    return { titulo, efeito: null, vinhetaId: args.chave.slice("salva:".length) };
  }
  return {
    titulo,
    efeito: args.chave.startsWith("modelo:") ? args.chave.slice("modelo:".length) : args.chave,
    vinhetaId: null,
  };
}

export function montarUrlPreviaVinhetaSeparadorNaApiTranscribrothers(
  escolha: EscolhaDeVinhetaParaSeparadorTranscribrothers,
): string | null {
  const titulo = escolha.titulo.trim() || "Nova funcionalidade";
  const params = new URLSearchParams();
  params.set("titulo", titulo);
  if (escolha.vinhetaId) {
    params.set("vinheta_id", escolha.vinhetaId);
  } else if (escolha.efeito) {
    params.set("efeito", escolha.efeito);
  } else {
    return null;
  }
  return `/api/integracao/vinhetas/previsualizar?${params.toString()}`;
}
