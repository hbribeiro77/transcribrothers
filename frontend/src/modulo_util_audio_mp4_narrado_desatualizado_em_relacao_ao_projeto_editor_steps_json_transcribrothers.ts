/**
 * Detecta se o áudio embutido do MP4 narrado ficou atrás do projeto/WAVs do editor.
 * Nesse caso o player deve usar a cadeia WAV por cue (como «Ir»), não o áudio do MP4.
 */

export const CHAVE_STEPS_EDITOR_VIDEO_NARRADO_AUDIO_MP4_DESATUALIZADO_TRANSCRIBROTHERS =
  "editor_video_narrado_audio_mp4_desatualizado";

function parseIsoMsTranscribrothers(valor: unknown): number | null {
  if (typeof valor !== "string" || !valor.trim()) return null;
  const ms = Date.parse(valor.trim());
  return Number.isFinite(ms) ? ms : null;
}

/**
 * True quando o play do player deve preferir WAVs/prévia em vez do áudio do MP4.
 */
export function audioMp4NarradoDesatualizadoEmRelacaoAoProjetoEditorDosStepsJsonTranscribrothers(
  stepsJson: Record<string, unknown> | null | undefined,
): boolean {
  if (!stepsJson || typeof stepsJson !== "object") return false;

  const flag = stepsJson[CHAVE_STEPS_EDITOR_VIDEO_NARRADO_AUDIO_MP4_DESATUALIZADO_TRANSCRIBROTHERS];
  if (flag === true) return true;
  if (flag === false) return false;

  const nPrev = Number(stepsJson.editor_video_narrado_projeto_previews_promovidas ?? 0);
  if (!Number.isFinite(nPrev) || nPrev <= 0) return false;

  const salvoEm = parseIsoMsTranscribrothers(stepsJson.editor_video_narrado_projeto_salvo_em);
  const bloco = stepsJson.video_com_narracao_tts;
  const geradoEm =
    bloco && typeof bloco === "object"
      ? parseIsoMsTranscribrothers((bloco as { gerado_em?: unknown }).gerado_em)
      : null;

  if (salvoEm == null) return true;
  if (geradoEm == null) return true;
  return salvoEm > geradoEm;
}
