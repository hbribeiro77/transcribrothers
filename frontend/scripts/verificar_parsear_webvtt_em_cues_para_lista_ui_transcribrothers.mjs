/**
 * Verificação rápida do parser WebVTT (sem Vitest no frontend).
 * Uso: node scripts/verificar_parsear_webvtt_em_cues_para_lista_ui_transcribrothers.mjs
 */

function parsearTimestampWebVttParaSegundosTranscribrothers(bruto) {
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

function parsearConteudoWebVttEmCuesParaListaUiTranscribrothers(conteudoVtt) {
  const texto = (conteudoVtt || "").replace(/^\uFEFF/, "").replace(/\r\n/g, "\n").replace(/\r/g, "\n");
  if (!texto.trim()) return [];
  const blocos = texto.split(/\n\n+/);
  const cues = [];
  const reSeta = /-->/;
  for (const blocoBruto of blocos) {
    const linhas = blocoBruto
      .split("\n")
      .map((l) => l.trimEnd())
      .filter((l) => l.length > 0);
    if (linhas.length === 0) continue;
    const primeira = linhas[0].trim();
    if (/^WEBVTT\b/i.test(primeira)) continue;
    if (/^NOTE\b/i.test(primeira) || /^STYLE\b/i.test(primeira) || /^REGION\b/i.test(primeira)) continue;
    const idxSeta = linhas.findIndex((l) => reSeta.test(l));
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
    cues.push({ inicioSegundos: inicio, fimSegundos: Math.max(inicio, fim), texto: textoCue });
  }
  return cues;
}

const amostra = `WEBVTT

1
00:00:00.000 --> 00:00:01.500
Primeira frase.

2
00:00:01.500 --> 00:00:03.000
Segunda frase.

NOTE isto é nota

00:01:05.200 --> 00:01:07.000
Terceira.
`;

const cues = parsearConteudoWebVttEmCuesParaListaUiTranscribrothers(amostra);
if (cues.length !== 3) throw new Error(`esperado 3 cues, veio ${cues.length}`);
if (cues[0].texto !== "Primeira frase.") throw new Error("texto cue 0");
if (Math.abs(cues[0].inicioSegundos - 0) > 1e-6) throw new Error("inicio cue 0");
if (Math.abs(cues[0].fimSegundos - 1.5) > 1e-6) throw new Error("fim cue 0");
if (Math.abs(cues[2].inicioSegundos - 65.2) > 1e-6) throw new Error("inicio cue 2 (1:05.2)");
console.log("ok: parser WebVTT lista UI");
