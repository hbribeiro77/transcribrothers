const CHAVE_LOCAL_STORAGE_MODELOS_LITELLM_EXTRAS_TRANSCRIBROTHERS =
  "transcribrothers_modelos_litellm_extras_navegador_v1";

export function carregarListaModelosLitellmExtrasSalvosNoNavegadorTranscribrothers(): string[] {
  try {
    const raw = window.localStorage.getItem(CHAVE_LOCAL_STORAGE_MODELOS_LITELLM_EXTRAS_TRANSCRIBROTHERS);
    if (!raw) return [];
    const parsed = JSON.parse(raw) as unknown;
    if (!Array.isArray(parsed)) return [];
    return parsed.map((x) => String(x).trim()).filter(Boolean);
  } catch {
    return [];
  }
}

export function salvarListaModelosLitellmExtrasNoNavegadorTranscribrothers(modelos: string[]): void {
  const unicos: string[] = [];
  const visto = new Set<string>();
  for (const m of modelos) {
    const t = m.trim();
    if (!t || visto.has(t)) continue;
    visto.add(t);
    unicos.push(t);
  }
  window.localStorage.setItem(
    CHAVE_LOCAL_STORAGE_MODELOS_LITELLM_EXTRAS_TRANSCRIBROTHERS,
    JSON.stringify(unicos),
  );
}

export function adicionarModeloLitellmExtraAoArmazenamentoLocalNavegadorTranscribrothers(
  slugModelo: string,
): string[] {
  const t = slugModelo.trim();
  if (!t) return carregarListaModelosLitellmExtrasSalvosNoNavegadorTranscribrothers();
  const atual = carregarListaModelosLitellmExtrasSalvosNoNavegadorTranscribrothers();
  if (atual.includes(t)) return atual;
  const novo = [...atual, t];
  salvarListaModelosLitellmExtrasNoNavegadorTranscribrothers(novo);
  return novo;
}

export function mesclarModelosServidorComExtrasNavegadorTranscribrothers(
  modelosServidor: string[],
  extrasNavegador: string[],
): string[] {
  const ordem: string[] = [];
  const visto = new Set<string>();
  for (const m of [...modelosServidor, ...extrasNavegador]) {
    const t = m.trim();
    if (!t || visto.has(t)) continue;
    visto.add(t);
    ordem.push(t);
  }
  return ordem;
}
