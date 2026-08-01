export type RespostaVerificarModeloLitellmChatProbeApiTranscribrothers = {
  ok: boolean;
  modelo: string;
  mensagem: string;
};

export async function verificarModeloLitellmChatCompletionsProbeApiTranscribrothers(
  modelo: string,
): Promise<RespostaVerificarModeloLitellmChatProbeApiTranscribrothers> {
  const r = await fetch("/api/config/transcribrothers/verificar-modelo-litellm", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ model: modelo.trim() }),
  });
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `Erro HTTP ${r.status}`);
  }
  return (await r.json()) as RespostaVerificarModeloLitellmChatProbeApiTranscribrothers;
}
