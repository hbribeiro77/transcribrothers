import type { OpcaoEscopoSecaoVideoNarradoTranscribrothers } from "./modulo_util_filtrar_markdown_por_secoes_heading_nivel2_selecionadas_transcribrothers.ts";
import { listarSecoesHeadingNivel2ComLinhaESlugMarkdownTutorialTranscribrothers } from "./modulo_util_contexto_cursor_markdown_e_slug_secao_heading_nivel2_tutorial_transcribrothers.ts";
import type { EfeitoDaVinheta } from "./previa_ao_vivo_cena_vinheta_copiada_do_app_vinhetas/modulo_amostragem_dos_modelos_de_abertura_da_vinheta.ts";

export const EFEITO_PADRAO_TRANSICAO_SECAO_GERACAO_VIDEO_NARRADO = "linhas-que-desenham-o-lugar" as const;
export const DURACAO_PADRAO_TRANSICAO_SECAO_GERACAO_VIDEO_NARRADO_SEGUNDOS = 2;

export function normalizarEfeitoTransicaoSecaoGeracaoVideoNarradoTranscribrothers(
  valor: string | null | undefined,
): EfeitoDaVinheta {
  if (
    valor === "linhas-que-desenham-o-lugar" ||
    valor === "barras-que-se-cruzam" ||
    valor === "planos-que-abrem-espaco"
  ) {
    return valor;
  }
  return EFEITO_PADRAO_TRANSICAO_SECAO_GERACAO_VIDEO_NARRADO;
}

export function normalizarDuracaoTransicaoSecaoGeracaoVideoNarradoTranscribrothers(
  valor: number | null | undefined,
): 2 | 5 {
  return valor === 5 ? 5 : 2;
}

export function chaveCartaoTransicaoSecaoAPartirDaPreferenciaTranscribrothers(pref: {
  efeito: string | null | undefined;
  vinhetaId?: string | null;
}): string {
  const vinhetaId = (pref.vinhetaId || "").trim();
  if (vinhetaId) return `salva:${vinhetaId}`;
  return `modelo:${normalizarEfeitoTransicaoSecaoGeracaoVideoNarradoTranscribrothers(pref.efeito)}`;
}

export function contarSecoesH2DoEscopoGeracaoVideoNarradoTranscribrothers(opts: {
  modo: "documento_inteiro" | "secoes";
  markdown: string;
  idsSelecionados: ReadonlySet<string>;
  opcoes: readonly OpcaoEscopoSecaoVideoNarradoTranscribrothers[];
}): number {
  if (opts.modo === "documento_inteiro") {
    return listarSecoesHeadingNivel2ComLinhaESlugMarkdownTutorialTranscribrothers(opts.markdown).length;
  }
  return opts.opcoes.filter((opcao) => opcao.id !== "preambulo" && opts.idsSelecionados.has(opcao.id))
    .length;
}

export function deveOferecerTransicoesEntreSecoesNaGeracaoVideoNarradoTranscribrothers(
  quantidadeSecoesH2: number,
): boolean {
  return quantidadeSecoesH2 >= 2;
}
