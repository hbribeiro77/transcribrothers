/**
 * Extrai um Markdown parcial a partir de seções `##` selecionadas (e opcionalmente o preâmbulo).
 */

import { listarSecoesHeadingNivel2ComLinhaESlugMarkdownTutorialTranscribrothers } from "./modulo_util_contexto_cursor_markdown_e_slug_secao_heading_nivel2_tutorial_transcribrothers.ts";

export type OpcaoEscopoSecaoVideoNarradoTranscribrothers = {
  /** Chave estável: `preambulo` ou slug da seção. */
  id: string;
  titulo: string;
  /** Linha 1-based do `##` (0 para preâmbulo). */
  numeroLinhaHeading: number;
};

export function listarOpcoesEscopoSecoesVideoNarradoAPartirMarkdownTranscribrothers(
  markdown: string,
): OpcaoEscopoSecaoVideoNarradoTranscribrothers[] {
  const texto = (markdown || "").replace(/\r\n/g, "\n");
  const linhas = texto.split("\n");
  const secoes = listarSecoesHeadingNivel2ComLinhaESlugMarkdownTutorialTranscribrothers(texto);
  const opcoes: OpcaoEscopoSecaoVideoNarradoTranscribrothers[] = [];

  if (secoes.length === 0) {
    return opcoes;
  }

  const primeiraLinhaH2 = secoes[0].numeroLinha;
  const temPreambulo = linhas.slice(0, primeiraLinhaH2 - 1).some((l) => l.trim().length > 0);
  if (temPreambulo) {
    opcoes.push({
      id: "preambulo",
      titulo: "Introdução (antes do primeiro ##)",
      numeroLinhaHeading: 0,
    });
  }

  for (const s of secoes) {
    opcoes.push({
      id: s.slugIdAncoraPreview,
      titulo: s.titulo,
      numeroLinhaHeading: s.numeroLinha,
    });
  }
  return opcoes;
}

export function filtrarMarkdownPorIdsEscopoSecoesVideoNarradoTranscribrothers(
  markdown: string,
  idsSelecionados: ReadonlySet<string> | readonly string[],
): string {
  const ids =
    idsSelecionados instanceof Set ? idsSelecionados : new Set(idsSelecionados.map((x) => x.trim()).filter(Boolean));
  if (ids.size === 0) {
    return "";
  }

  const texto = (markdown || "").replace(/\r\n/g, "\n");
  const linhas = texto.split("\n");
  const secoes = listarSecoesHeadingNivel2ComLinhaESlugMarkdownTutorialTranscribrothers(texto);
  if (secoes.length === 0) {
    return ids.has("preambulo") || ids.has("documento_inteiro") ? texto.trim() : "";
  }

  const blocos: string[] = [];
  const primeiraLinhaH2 = secoes[0].numeroLinha;

  if (ids.has("preambulo")) {
    const pre = linhas.slice(0, primeiraLinhaH2 - 1).join("\n").trimEnd();
    if (pre.trim()) blocos.push(pre);
  }

  for (let i = 0; i < secoes.length; i += 1) {
    const secao = secoes[i];
    if (!ids.has(secao.slugIdAncoraPreview)) continue;
    const inicio = secao.numeroLinha - 1;
    const fimExclusivo = i + 1 < secoes.length ? secoes[i + 1].numeroLinha - 1 : linhas.length;
    const bloco = linhas.slice(inicio, fimExclusivo).join("\n").trimEnd();
    if (bloco.trim()) blocos.push(bloco);
  }

  return blocos.join("\n\n").trim();
}
