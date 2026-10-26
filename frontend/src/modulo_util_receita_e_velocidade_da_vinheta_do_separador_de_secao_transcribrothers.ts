import { PALETA_PADRAO_DA_VINHETA, type CoresDaVinheta } from "./previa_ao_vivo_cena_vinheta_copiada_do_app_vinhetas/modulo_validacao_de_titulo_e_cores_da_vinheta.ts";
import { resolverEscolhaVinhetaAPartirDaChaveDoCartaoTranscribrothers } from "./modulo_util_montar_cartoes_e_resolver_escolha_vinheta_separador_de_secao_transcribrothers.ts";

export const DURACAO_MINIMA_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS = 0.5;
export const DURACAO_MAXIMA_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS = 8;
export const PASSO_DE_DURACAO_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS = 0.5;
export const PRESENCA_PADRAO_DA_IMAGEM_DE_FUNDO_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS = 60;

export const CAMPOS_DE_COR_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS: {
  chave: keyof CoresDaVinheta;
  rotulo: string;
}[] = [
  { chave: "fundo", rotulo: "Fundo" },
  { chave: "plano_principal", rotulo: "Plano principal" },
  { chave: "plano_destaque", rotulo: "Plano de destaque" },
  { chave: "texto", rotulo: "Texto" },
];

export type ReceitaVinhetaDoSeparadorTranscribrothers = {
  titulo: string;
  efeito: string | null;
  vinhetaId: string | null;
  duracaoSegundos: number;
  presencaDaImagem: number;
  cores: CoresDaVinheta;
};

export function normalizarDuracaoSegundosDaVinhetaDoSeparadorTranscribrothers(valor: number): number {
  if (!Number.isFinite(valor)) {
    return 5;
  }
  const meios = Math.round(valor * 2) / 2;
  return Math.min(
    DURACAO_MAXIMA_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS,
    Math.max(DURACAO_MINIMA_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS, meios),
  );
}

export function normalizarPresencaDaImagemDaVinhetaDoSeparadorTranscribrothers(valor: number): number {
  if (!Number.isFinite(valor)) return 0;
  return Math.min(100, Math.max(0, Math.round(valor)));
}

export function montarReceitaVinhetaDoSeparadorTranscribrothers(args: {
  chave: string;
  titulo: string;
  duracaoSegundos: number;
  presencaDaImagem: number;
  cores: CoresDaVinheta;
}): ReceitaVinhetaDoSeparadorTranscribrothers {
  const escolha = resolverEscolhaVinhetaAPartirDaChaveDoCartaoTranscribrothers({
    chave: args.chave,
    titulo: args.titulo,
  });
  return {
    ...escolha,
    duracaoSegundos: normalizarDuracaoSegundosDaVinhetaDoSeparadorTranscribrothers(args.duracaoSegundos),
    presencaDaImagem: normalizarPresencaDaImagemDaVinhetaDoSeparadorTranscribrothers(args.presencaDaImagem),
    cores: { ...PALETA_PADRAO_DA_VINHETA, ...args.cores },
  };
}

export function normalizarDimensoesParesDoCanvasDaVinhetaTranscribrothers(
  largura: number,
  altura: number,
): { largura: number; altura: number } {
  const par = (valor: number) => {
    const inteiro = Math.floor(Number.isFinite(valor) ? valor : 0);
    return Math.max(2, inteiro - (inteiro % 2));
  };
  return { largura: par(largura), altura: par(altura) };
}

export function capturarQuadroAtualDoElementoVideoComoDataUrlPngTranscribrothers(
  video: HTMLVideoElement | null,
): string | null {
  if (!video || video.readyState < 2 || video.videoWidth < 2 || video.videoHeight < 2) {
    return null;
  }
  const canvas = document.createElement("canvas");
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  const contexto = canvas.getContext("2d");
  if (!contexto) return null;
  try {
    contexto.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/png");
  } catch {
    return null;
  }
}
