import type { DestinoAposTranscricaoTranscribrothers } from "./modulo_constante_destino_apos_transcricao_e_rotulo_frame_documento_transcribrothers.ts";

export type ParametrosImportacaoRecbrothersTranscribrothers = {
  recbrothers: boolean;
  etapa: "video" | "destino" | null;
  stagingId: string | null;
  destino: DestinoAposTranscricaoTranscribrothers | null;
};

export type MetadadosStagingVideoTranscribrothers = {
  staging_id: string;
  filename: string;
  size_bytes: number;
  ext: string;
  created_at: string;
  expires_at: string;
  modo_recbrothers?: string | null;
  cliques_json_presente?: boolean;
  total_cliques?: number;
};

export function lerParametrosImportacaoRecbrothersDaUrl(
  search: string = typeof window !== "undefined" ? window.location.search : "",
): ParametrosImportacaoRecbrothersTranscribrothers {
  const params = new URLSearchParams(search);
  const recbrothers = params.get("recbrothers") === "1";
  const etapaRaw = (params.get("etapa") || "").trim().toLowerCase();
  const etapa =
    etapaRaw === "destino" ? "destino" : etapaRaw === "video" ? "video" : null;
  const stagingId = (params.get("staging_id") || "").trim() || null;
  const destinoRaw = (params.get("destino") || "").trim().toLowerCase();
  const destino =
    destinoRaw === "reproducao_bug"
      ? ("reproducao_bug" as DestinoAposTranscricaoTranscribrothers)
      : destinoRaw === "gerar_tutorial"
        ? ("gerar_tutorial" as DestinoAposTranscricaoTranscribrothers)
        : null;
  return { recbrothers, etapa, stagingId, destino };
}

export function limparParametrosImportacaoRecbrothersDaUrlBarraNavegador(): void {
  if (typeof window === "undefined") return;
  const url = new URL(window.location.href);
  url.searchParams.delete("recbrothers");
  url.searchParams.delete("etapa");
  url.searchParams.delete("staging_id");
  url.searchParams.delete("destino");
  const qs = url.searchParams.toString();
  const novo = `${url.pathname}${qs ? `?${qs}` : ""}${url.hash}`;
  window.history.replaceState({}, "", novo);
}

export async function carregarArquivoVideoDeStagingTranscribrothers(
  stagingId: string,
): Promise<File> {
  const rMeta = await fetch(`/api/staging/${encodeURIComponent(stagingId)}`);
  if (!rMeta.ok) {
    const texto = await rMeta.text();
    throw new Error(texto || `Não foi possível carregar o vídeo (HTTP ${rMeta.status}).`);
  }
  const meta = (await rMeta.json()) as MetadadosStagingVideoTranscribrothers;

  const rVideo = await fetch(`/api/staging/${encodeURIComponent(stagingId)}/video`);
  if (!rVideo.ok) {
    const texto = await rVideo.text();
    throw new Error(texto || `Não foi possível baixar o vídeo (HTTP ${rVideo.status}).`);
  }
  const blob = await rVideo.blob();
  const mime =
    blob.type ||
    (meta.ext === ".webm"
      ? "video/webm"
      : meta.ext === ".mp4"
        ? "video/mp4"
        : "application/octet-stream");
  return new File([blob], meta.filename, { type: mime });
}
