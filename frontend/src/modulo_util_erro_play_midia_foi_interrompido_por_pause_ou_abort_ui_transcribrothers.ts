/**
 * Erros benignos de play()/pause() em corrida (scrub, troca de cue, seek).
 * Não devem virar toast vermelho.
 */

export function erroPlayMidiaFoiInterrompidoPorPauseOuAbortUiTranscribrothers(
  erro: unknown,
): boolean {
  if (erro == null) return false;
  const nome =
    typeof erro === "object" && erro !== null && "name" in erro
      ? String((erro as { name?: unknown }).name || "")
      : "";
  if (nome === "AbortError") return true;
  const msg = erro instanceof Error ? erro.message : String(erro);
  const m = msg.toLowerCase();
  if (m.includes("interrupted by a call to pause")) return true;
  if (m.includes("the play() request was interrupted")) return true;
  if (m.includes("interrupted by a new load request")) return true;
  return false;
}
