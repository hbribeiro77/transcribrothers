/** Abre URL http(s) em nova aba — mais confiável que window.open após await (bloqueio de popup). */

export function abrirUrlExternaNovaAbaNavegadorTranscribrothers(url: string): void {
  const href = (url || "").trim();
  if (!href) return;
  const link = document.createElement("a");
  link.href = href;
  link.target = "_blank";
  link.rel = "noopener noreferrer";
  document.body.appendChild(link);
  link.click();
  link.remove();
}
