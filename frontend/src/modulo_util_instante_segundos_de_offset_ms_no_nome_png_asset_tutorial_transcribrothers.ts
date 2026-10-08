const RE_OFFSET_MS_NO_NOME_PNG_ASSET_TUTORIAL_TRANSCRIBROTHERS = /offset_ms_(\d+)/i;

export function instanteSegundosDeOffsetMsNoNomePngAssetTutorialTranscribrothers(
  nomeOuCaminho: string,
): number | null {
  const bruto = (nomeOuCaminho || "").trim();
  if (!bruto) return null;
  const semQuery = bruto.split("?")[0]?.split("#")[0] ?? bruto;
  const nome = semQuery.replace(/\\/g, "/").split("/").pop() ?? semQuery;
  const achado = RE_OFFSET_MS_NO_NOME_PNG_ASSET_TUTORIAL_TRANSCRIBROTHERS.exec(nome);
  if (!achado?.[1]) return null;
  return Number.parseInt(achado[1], 10) / 1000;
}
