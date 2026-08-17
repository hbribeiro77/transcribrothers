import {
  DIRETRIZ_CONTEUDO_LEGENDAS_PADRAO_TRANSCRIBROTHERS,
  type DiretrizConteudoLegendasTranscribrothers,
  normalizarDiretrizConteudoLegendasTranscribrothers,
} from "./modulo_diretriz_conteudo_legendas_narracao_transcribrothers.ts";

const CHAVE_LOCAL_STORAGE_DIRETRIZ_CONTEUDO_LEGENDAS_PREFERIDA_TRANSCRIBROTHERS =
  "transcribrothers_diretriz_conteudo_legendas_preferida_navegador_v1";

export function carregarDiretrizConteudoLegendasPreferidaSalvaNoNavegadorTranscribrothers(): DiretrizConteudoLegendasTranscribrothers {
  try {
    const raw = window.localStorage.getItem(
      CHAVE_LOCAL_STORAGE_DIRETRIZ_CONTEUDO_LEGENDAS_PREFERIDA_TRANSCRIBROTHERS,
    );
    if (raw == null || !String(raw).trim()) {
      return DIRETRIZ_CONTEUDO_LEGENDAS_PADRAO_TRANSCRIBROTHERS;
    }
    return normalizarDiretrizConteudoLegendasTranscribrothers(raw);
  } catch {
    return DIRETRIZ_CONTEUDO_LEGENDAS_PADRAO_TRANSCRIBROTHERS;
  }
}

export function salvarDiretrizConteudoLegendasPreferidaNoNavegadorTranscribrothers(
  diretriz: string,
): void {
  const n = normalizarDiretrizConteudoLegendasTranscribrothers(diretriz);
  try {
    window.localStorage.setItem(
      CHAVE_LOCAL_STORAGE_DIRETRIZ_CONTEUDO_LEGENDAS_PREFERIDA_TRANSCRIBROTHERS,
      n,
    );
  } catch {
    /* ignore quota / private mode */
  }
}
