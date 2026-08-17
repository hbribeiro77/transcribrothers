const CHAVE_LOCAL_STORAGE_MODELO_TTS_NARRACAO_PREFERIDO_TRANSCRIBROTHERS =
  "transcribrothers_modelo_tts_narracao_preferido_navegador_v1";

export function carregarModeloTtsNarracaoPreferidoSalvoNoNavegadorTranscribrothers(): string | null {
  try {
    const raw = window.localStorage.getItem(
      CHAVE_LOCAL_STORAGE_MODELO_TTS_NARRACAO_PREFERIDO_TRANSCRIBROTHERS,
    );
    const t = (raw || "").trim();
    return t || null;
  } catch {
    return null;
  }
}

export function salvarModeloTtsNarracaoPreferidoNoNavegadorTranscribrothers(
  slugModelo: string,
): void {
  const t = (slugModelo || "").trim();
  if (!t) return;
  try {
    window.localStorage.setItem(
      CHAVE_LOCAL_STORAGE_MODELO_TTS_NARRACAO_PREFERIDO_TRANSCRIBROTHERS,
      t,
    );
  } catch {
    /* ignore quota / private mode */
  }
}
