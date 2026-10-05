import { modeloLitellmPareceTtsPeloSlugTranscribrothers } from "./modulo_api_gerar_narracao_tts_markdown_job_transcribrothers.ts";

export function listarModelosChatAskAgenteDaListaDisponivelTranscribrothers(
  modelos: string[],
): string[] {
  const out: string[] = [];
  const visto = new Set<string>();
  for (const modelo of modelos) {
    const slug = (modelo || "").trim();
    if (!slug || visto.has(slug) || modeloLitellmPareceTtsPeloSlugTranscribrothers(slug)) {
      continue;
    }
    visto.add(slug);
    out.push(slug);
  }
  return out;
}

export function rotuloCurtoModeloChatAskAgenteParaUiTranscribrothers(modelo: string): string {
  const slug = (modelo || "").trim();
  if (!slug) return "";
  return slug.includes("/") ? slug.split("/").pop() || slug : slug;
}

export function escolherModeloChatAskAgenteDaListaDisponivelTranscribrothers(
  modelos: string[],
  preferido?: string | null,
): string | null {
  const chat = listarModelosChatAskAgenteDaListaDisponivelTranscribrothers(modelos);
  const pref = (preferido || "").trim();
  if (pref && chat.includes(pref)) return pref;
  return chat[0] ?? null;
}
