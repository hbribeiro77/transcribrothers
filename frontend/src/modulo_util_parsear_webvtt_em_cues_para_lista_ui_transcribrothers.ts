/** Parser mínimo de WebVTT para lista de cues na UI (modal vídeo narrado). */

export type CueWebVttParaListaUiTranscribrothers = {
  inicioSegundos: number;
  fimSegundos: number;
  texto: string;
  /**
   * Texto só para TTS (pronúncia). Vazio = narrar o mesmo da legenda (`texto`).
   * Não entra no arquivo VTT.
   */
  textoTts?: string;
};

function parsearTimestampWebVttParaSegundosTranscribrothers(bruto: string): number | null {
  const s = (bruto || "").trim().replace(",", ".");
  const partes = s.split(":");
  if (partes.length < 2 || partes.length > 3) return null;
  let horas = 0;
  let minutos = 0;
  let segundosStr = "";
  if (partes.length === 3) {
    horas = Number(partes[0]);
    minutos = Number(partes[1]);
    segundosStr = partes[2];
  } else {
    minutos = Number(partes[0]);
    segundosStr = partes[1];
  }
  const segundos = Number(segundosStr);
  if (![horas, minutos, segundos].every((n) => Number.isFinite(n))) return null;
  return horas * 3600 + minutos * 60 + segundos;
}

/**
 * Converte conteúdo `.vtt` em cues `{ inicio, fim, texto }`.
 * Ignora cabeçalho WEBVTT, NOTE, STYLE e identificadores numéricos de cue.
 */
export function parsearConteudoWebVttEmCuesParaListaUiTranscribrothers(
  conteudoVtt: string,
): CueWebVttParaListaUiTranscribrothers[] {
  const texto = (conteudoVtt || "").replace(/^\uFEFF/, "").replace(/\r\n/g, "\n").replace(/\r/g, "\n");
  if (!texto.trim()) return [];

  const blocos = texto.split(/\n\n+/);
  const cues: CueWebVttParaListaUiTranscribrothers[] = [];
  const reSeta = /-->/;

  for (const blocoBruto of blocos) {
    const linhas = blocoBruto
      .split("\n")
      .map((l) => l.trimEnd())
      .filter((l) => l.length > 0);
    if (linhas.length === 0) continue;

    const primeira = linhas[0].trim();
    if (/^WEBVTT\b/i.test(primeira)) continue;
    if (/^NOTE\b/i.test(primeira) || /^STYLE\b/i.test(primeira) || /^REGION\b/i.test(primeira)) {
      continue;
    }

    let idxSeta = linhas.findIndex((l) => reSeta.test(l));
    if (idxSeta < 0) continue;

    const linhaTempo = linhas[idxSeta];
    const m = linhaTempo.match(
      /^(\d{1,2}:\d{2}(?::\d{2})?[.,]\d{1,3}|\d{1,2}:\d{2}[.,]\d{1,3})\s*-->\s*(\d{1,2}:\d{2}(?::\d{2})?[.,]\d{1,3}|\d{1,2}:\d{2}[.,]\d{1,3})/,
    );
    if (!m) continue;
    const inicio = parsearTimestampWebVttParaSegundosTranscribrothers(m[1]);
    const fim = parsearTimestampWebVttParaSegundosTranscribrothers(m[2]);
    if (inicio === null || fim === null) continue;

    const textoCue = linhas
      .slice(idxSeta + 1)
      .join("\n")
      .replace(/<\/?[^>]+>/g, "")
      .trim();
    if (!textoCue) continue;

    cues.push({
      inicioSegundos: inicio,
      fimSegundos: Math.max(inicio, fim),
      texto: textoCue,
    });
  }

  return cues;
}

export function formatarSegundosComoTimestampVttCurtoUiTranscribrothers(segundos: number): string {
  const totalMs = Math.max(0, Math.round(segundos * 1000));
  const h = Math.floor(totalMs / 3_600_000);
  const resto = totalMs % 3_600_000;
  const m = Math.floor(resto / 60_000);
  const s = Math.floor((resto % 60_000) / 1000);
  const ms = resto % 1000;
  if (h > 0) {
    return `${h}:${String(m).padStart(2, "0")}:${String(s).padStart(2, "0")}.${String(ms).padStart(3, "0")}`;
  }
  return `${m}:${String(s).padStart(2, "0")}.${String(ms).padStart(3, "0")}`;
}

export async function carregarCuesWebVttDeUrlParaListaUiTranscribrothers(
  urlVtt: string,
): Promise<CueWebVttParaListaUiTranscribrothers[]> {
  const r = await fetch(urlVtt);
  if (!r.ok) {
    throw new Error(`Não foi possível carregar as legendas VTT (HTTP ${r.status}).`);
  }
  const texto = await r.text();
  return parsearConteudoWebVttEmCuesParaListaUiTranscribrothers(texto);
}
