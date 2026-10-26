export type TemposDebugUltimaVinhetaSeparadorTranscribrothers = {
  total?: number | null;
  captura_png_seguinte?: number | null;
  captura_png_anterior?: number | null;
  sonda_dimensoes?: number | null;
  render_vinhetas?: number | null;
  sonda_duracao?: number | null;
  amostragem_vite_node?: number | null;
  desenho_pil?: number | null;
  encode_ffmpeg?: number | null;
};

export type UltimaVinhetaDebugApiTranscribrothers = {
  gerado_em?: string | null;
  titulo?: string | null;
  efeito?: string | null;
  vinheta_id?: string | null;
  largura?: number | null;
  altura?: number | null;
  largura_fonte?: number | null;
  altura_fonte?: number | null;
  resolucao_encode?: string | null;
  duracao_pedida_segundos?: number | null;
  duracao_medida_segundos?: number | null;
  presenca_da_imagem?: number | null;
  tem_quadro_anterior?: boolean | null;
  tem_quadro_seguinte?: boolean | null;
  bytes_mp4?: number | null;
  fps?: number | null;
  quantidade_quadros?: number | null;
  dissolve_assada_nos_quadros?: boolean | null;
  url_api_vinhetas?: string | null;
  tempos_ms?: TemposDebugUltimaVinhetaSeparadorTranscribrothers | null;
};

function linha(rotulo: string, valor: string | number | boolean | null | undefined): string | null {
  if (valor === null || valor === undefined || valor === "") return null;
  if (valor === true) return `${rotulo}: sim`;
  if (valor === false) return `${rotulo}: não`;
  return `${rotulo}: ${valor}`;
}

function milissegundos(rotulo: string, valor: number | null | undefined): string | null {
  if (valor === null || valor === undefined) return null;
  return `${rotulo}: ${valor} ms`;
}

export function formatarTextoDebugUltimaVinhetaSeparadorTranscribrothers(
  dados: UltimaVinhetaDebugApiTranscribrothers | null | undefined,
): string {
  if (!dados) {
    return "Ainda não há relatório da última vinheta neste job.";
  }
  const tempos = dados.tempos_ms ?? {};
  const canvas =
    dados.largura != null && dados.altura != null ? `${dados.largura}×${dados.altura}` : null;
  let quadros: string | null = null;
  if (dados.quantidade_quadros != null && dados.fps != null) {
    quadros = `${dados.quantidade_quadros} · ${dados.fps} fps`;
  } else if (dados.quantidade_quadros != null) {
    quadros = String(dados.quantidade_quadros);
  }
  const duracaoPedida =
    dados.duracao_pedida_segundos != null ? `${dados.duracao_pedida_segundos}s` : null;
  const duracaoMedida =
    dados.duracao_medida_segundos != null ? `${dados.duracao_medida_segundos}s` : null;
  let duracao: string | null = null;
  if (duracaoPedida && duracaoMedida) {
    duracao = `duração pedida: ${duracaoPedida} · medida: ${duracaoMedida}`;
  } else if (duracaoMedida) {
    duracao = `duração medida: ${duracaoMedida}`;
  } else if (duracaoPedida) {
    duracao = `duração pedida: ${duracaoPedida}`;
  }

  const linhas = [
    "Última vinheta",
    linha("gerado em", dados.gerado_em),
    linha("título", dados.titulo),
    linha("efeito", dados.efeito),
    linha("vinheta id", dados.vinheta_id),
    linha("resolução encode", dados.resolucao_encode),
    canvas ? `canvas: ${canvas}` : null,
    dados.largura_fonte != null && dados.altura_fonte != null
      ? `fonte: ${dados.largura_fonte}×${dados.altura_fonte}`
      : null,
    duracao,
    linha("presença", dados.presenca_da_imagem),
    quadros ? `quadros: ${quadros}` : null,
    linha("MP4 bytes", dados.bytes_mp4),
    linha("quadro anterior", dados.tem_quadro_anterior),
    linha("quadro seguinte", dados.tem_quadro_seguinte),
    linha("dissolve assada", dados.dissolve_assada_nos_quadros),
    linha("API vinhetas", dados.url_api_vinhetas),
    milissegundos("total", tempos.total),
    milissegundos("captura png seguinte", tempos.captura_png_seguinte),
    milissegundos("captura png anterior", tempos.captura_png_anterior),
    milissegundos("sonda dimensões", tempos.sonda_dimensoes),
    milissegundos("render vinhetas", tempos.render_vinhetas),
    milissegundos("amostragem vite-node", tempos.amostragem_vite_node),
    milissegundos("desenho PIL", tempos.desenho_pil),
    milissegundos("encode ffmpeg", tempos.encode_ffmpeg),
    milissegundos("sonda duração", tempos.sonda_duracao),
  ].filter((item): item is string => item != null);
  return linhas.join("\n");
}
