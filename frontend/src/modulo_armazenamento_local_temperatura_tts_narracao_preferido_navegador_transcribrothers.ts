import {
  TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
  normalizarTemperaturaTtsNarracaoTranscribrothers,
} from "./modulo_perfil_motor_sintese_tts_narracao_transcribrothers.ts";

const CHAVE_LOCAL_STORAGE_TEMPERATURA_TTS_NARRACAO_PREFERIDO_TRANSCRIBROTHERS =
  "transcribrothers_temperatura_tts_narracao_preferido_navegador_v1";

export function carregarTemperaturaTtsNarracaoPreferidaSalvaNoNavegadorTranscribrothers(): number {
  try {
    const raw = window.localStorage.getItem(
      CHAVE_LOCAL_STORAGE_TEMPERATURA_TTS_NARRACAO_PREFERIDO_TRANSCRIBROTHERS,
    );
    if (raw == null || !String(raw).trim()) {
      return TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS;
    }
    return normalizarTemperaturaTtsNarracaoTranscribrothers(raw);
  } catch {
    return TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS;
  }
}

export function salvarTemperaturaTtsNarracaoPreferidaNoNavegadorTranscribrothers(
  temperatura: number,
): void {
  const n = normalizarTemperaturaTtsNarracaoTranscribrothers(temperatura);
  try {
    window.localStorage.setItem(
      CHAVE_LOCAL_STORAGE_TEMPERATURA_TTS_NARRACAO_PREFERIDO_TRANSCRIBROTHERS,
      String(n),
    );
  } catch {
    /* ignore quota / private mode */
  }
}
