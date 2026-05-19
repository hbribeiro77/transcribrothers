const CHAVE_LOCAL_STORAGE_RASCUNHO_INSTRUCAO_PREFIXO_LITELLM_TUTORIAL_MARKDOWN_TRANSCRIBROTHERS =
  "transcribrothers_v1_rascunho_instrucao_prefixo_litellm_tutorial_markdown";

export function carregarRascunhoInstrucaoPrefixoLitellmTutorialMarkdownDoNavegadorTranscribrothers(): string | null {
  try {
    const raw = localStorage.getItem(CHAVE_LOCAL_STORAGE_RASCUNHO_INSTRUCAO_PREFIXO_LITELLM_TUTORIAL_MARKDOWN_TRANSCRIBROTHERS);
    if (raw === null || raw === "") return null;
    return raw;
  } catch {
    return null;
  }
}

export function gravarRascunhoInstrucaoPrefixoLitellmTutorialMarkdownNoNavegadorTranscribrothers(texto: string): void {
  try {
    localStorage.setItem(
      CHAVE_LOCAL_STORAGE_RASCUNHO_INSTRUCAO_PREFIXO_LITELLM_TUTORIAL_MARKDOWN_TRANSCRIBROTHERS,
      texto,
    );
  } catch {
    /* ignore */
  }
}
