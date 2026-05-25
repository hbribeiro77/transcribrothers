/** Duração do vídeo no job (ffprobe no servidor, gravada em `steps_json`). */
export function lerDuracaoVideoSegundosStepsJsonJobTranscribrothers(
  stepsJson: Record<string, unknown> | null | undefined,
): number {
  if (!stepsJson) return 0;

  const candidatos = [
    stepsJson.duracao_video_segundos,
    stepsJson.duracao_audio_ffprobe,
  ];

  for (const bruto of candidatos) {
    if (typeof bruto === "number" && Number.isFinite(bruto) && bruto > 0) return bruto;
  }

  const planejamento = stepsJson.planejamento_instantes_captura_frames;
  if (planejamento && typeof planejamento === "object" && !Array.isArray(planejamento)) {
    const durPlan = (planejamento as Record<string, unknown>).duracao_video_segundos;
    if (typeof durPlan === "number" && Number.isFinite(durPlan) && durPlan > 0) return durPlan;
  }

  return 0;
}
