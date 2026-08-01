/** Query `view=video-narrado`: página de edição do vídeo narrado (não o catálogo de pipelines). */

export const VIEW_QUERY_VIDEO_NARRADO_TRANSCRIBROTHERS = "video-narrado";

export function lerViewVideoNarradoAbertaNaUrlTranscribrothers(
  search: string = typeof window !== "undefined" ? window.location.search : "",
): boolean {
  return new URLSearchParams(search).get("view") === VIEW_QUERY_VIDEO_NARRADO_TRANSCRIBROTHERS;
}

/**
 * Atualiza a URL sem sair da tela do projeto.
 * `push` = true ao abrir (Voltar do browser funciona); `false` ao fechar (replace).
 */
export function sincronizarViewVideoNarradoNaUrlTranscribrothers(
  aberta: boolean,
  opts: { push: boolean },
): void {
  if (typeof window === "undefined") return;
  const url = new URL(window.location.href);
  const atual = url.searchParams.get("view");
  if (aberta) {
    if (atual === VIEW_QUERY_VIDEO_NARRADO_TRANSCRIBROTHERS) return;
    url.searchParams.set("view", VIEW_QUERY_VIDEO_NARRADO_TRANSCRIBROTHERS);
  } else {
    if (atual !== VIEW_QUERY_VIDEO_NARRADO_TRANSCRIBROTHERS) return;
    url.searchParams.delete("view");
  }
  const href = `${url.pathname}${url.search}${url.hash}`;
  if (opts.push) {
    window.history.pushState(null, "", href);
  } else {
    window.history.replaceState(null, "", href);
  }
}
