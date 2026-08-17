import {
  RITMO_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
  type RitmoTtsNarracaoTranscribrothers,
  normalizarRitmoTtsNarracaoTranscribrothers,
} from "./modulo_perfil_motor_sintese_tts_narracao_transcribrothers.ts";

const CHAVE_LOCAL_STORAGE_RITMO_TTS_NARRACAO_PREFERIDO_TRANSCRIBROTHERS =
  "transcribrothers_ritmo_tts_narracao_preferido_navegador_v1";

export function carregarRitmoTtsNarracaoPreferidoSalvoNoNavegadorTranscribrothers(): RitmoTtsNarracaoTranscribrothers {
  try {
    const raw = window.localStorage.getItem(
      CHAVE_LOCAL_STORAGE_RITMO_TTS_NARRACAO_PREFERIDO_TRANSCRIBROTHERS,
    );
    if (raw == null || !String(raw).trim()) {
      return RITMO_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS;
    }
    return normalizarRitmoTtsNarracaoTranscribrothers(raw);
  } catch {
    return RITMO_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS;
  }
}

export function salvarRitmoTtsNarracaoPreferidoNoNavegadorTranscribrothers(
  ritmo: string,
): void {
  const n = normalizarRitmoTtsNarracaoTranscribrothers(ritmo);
  try {
    window.localStorage.setItem(
      CHAVE_LOCAL_STORAGE_RITMO_TTS_NARRACAO_PREFERIDO_TRANSCRIBROTHERS,
      n,
    );
  } catch {
    /* ignore quota / private mode */
  }
}
