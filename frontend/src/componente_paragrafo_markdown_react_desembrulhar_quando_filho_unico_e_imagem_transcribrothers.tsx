import type * as React from "react";
import type { Element } from "hast";

type PropsParagrafoMarkdownDesembrulharImagemTranscribrothers = React.HTMLAttributes<HTMLParagraphElement> & {
  node?: { children?: unknown[] };
};

/** Evita `<p><figure>…` inválido: parágrafo só com imagem vira fragmento. */
export function ComponenteParagrafoMarkdownReactDesembrulharQuandoFilhoUnicoEImagemTranscribrothers({
  node,
  children,
  ...props
}: PropsParagrafoMarkdownDesembrulharImagemTranscribrothers) {
  const filhos = node?.children;
  const filhoUnicoEImagem =
    Array.isArray(filhos) &&
    filhos.length === 1 &&
    typeof filhos[0] === "object" &&
    filhos[0] !== null &&
    "type" in filhos[0] &&
    (filhos[0] as { type?: string }).type === "element" &&
    "tagName" in filhos[0] &&
    (filhos[0] as Element).tagName === "img";

  if (filhoUnicoEImagem) {
    return <>{children}</>;
  }
  return <p {...props}>{children}</p>;
}
