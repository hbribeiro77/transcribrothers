import type { CueWebVttParaListaUiTranscribrothers } from "./modulo_util_parsear_webvtt_em_cues_para_lista_ui_transcribrothers.ts";

/** Timestamp WebVTT completo `HH:MM:SS.mmm` (compatível com o gerador do backend). */
export function formatarSegundosComoTimestampWebVttCompletoUiTranscribrothers(
  segundos: number,
): string {
  const totalMs = Math.max(0, Math.round(Number(segundos) * 1000));
  const h = Math.floor(totalMs / 3_600_000);
  const resto = totalMs % 3_600_000;
  const m = Math.floor(resto / 60_000);
  const s = Math.floor((resto % 60_000) / 1000);
  const ms = resto % 1000;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}.${String(ms).padStart(3, "0")}`;
}

/**
 * Serializa cues da UI em conteúdo WebVTT para `<track>` ao vivo (blob URL).
 */
export function serializarCuesParaConteudoWebVttUiTranscribrothers(
  cues: CueWebVttParaListaUiTranscribrothers[],
): string {
  const linhas = ["WEBVTT", ""];
  let indice = 0;
  for (const cue of cues) {
    const inicio = Number(cue.inicioSegundos);
    const fim = Number(cue.fimSegundos);
    if (!Number.isFinite(inicio) || !Number.isFinite(fim) || fim <= inicio) continue;
    const texto = String(cue.texto ?? "")
      .replace(/\r\n/g, "\n")
      .replace(/\r/g, "\n")
      .split("\n")
      .map((l) => l.trim())
      .filter(Boolean)
      .join(" ")
      .trim();
    if (!texto) continue;
    indice += 1;
    linhas.push(String(indice));
    // size alto = menos margem lateral (menos quebras); line perto da base = uma linha mais baixo.
    linhas.push(
      `${formatarSegundosComoTimestampWebVttCompletoUiTranscribrothers(inicio)} --> ${formatarSegundosComoTimestampWebVttCompletoUiTranscribrothers(fim)} line:94% size:96% align:center`,
    );
    linhas.push(texto);
    linhas.push("");
  }
  return `${linhas.join("\n").replace(/\n+$/, "")}\n`;
}
