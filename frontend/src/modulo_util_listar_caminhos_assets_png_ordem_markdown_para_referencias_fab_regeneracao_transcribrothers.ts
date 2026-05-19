/** Lista `assets/*.png` na ordem da primeira ocorrência em `![](...)` — alinhado ao backend da regeneração. */

const RE_IMAGEM_MARKDOWN_TRANSCRIBROTHERS = /!\[[^\]]*]\(\s*([^)]+?)\s*\)/g;

function normalizarCaminhoRelativoAssetPngTutorialTranscribrothers(raw: string): string | null {
  let s = raw.trim().replace(/^["']|["']$/g, "");
  if (!s) return null;
  const q = s.indexOf("?");
  if (q >= 0) s = s.slice(0, q).trim();
  s = s.replace(/\\/g, "/");
  const h = s.indexOf("#");
  if (h >= 0) s = s.slice(0, h).trim();
  if (/^https?:\/\//i.test(s) || /^data:/i.test(s)) return null;
  s = s.replace(/^\.\//, "");
  if (!s.toLowerCase().endsWith(".png")) return null;
  if (s.startsWith("assets/")) return s;
  const idx = s.indexOf("assets/");
  if (idx >= 0) return s.slice(idx);
  return null;
}

export function listarCaminhosAssetsPngOrdemPrimeiraOcorrenciaMarkdownTutorialTranscribrothers(
  markdown: string,
): string[] {
  if (!(markdown || "").trim()) return [];
  const vistos = new Set<string>();
  const saida: string[] = [];
  RE_IMAGEM_MARKDOWN_TRANSCRIBROTHERS.lastIndex = 0;
  let m: RegExpExecArray | null;
  while ((m = RE_IMAGEM_MARKDOWN_TRANSCRIBROTHERS.exec(markdown)) !== null) {
    const norm = normalizarCaminhoRelativoAssetPngTutorialTranscribrothers(m[1]);
    if (!norm || vistos.has(norm)) continue;
    vistos.add(norm);
    saida.push(norm);
  }
  return saida;
}
