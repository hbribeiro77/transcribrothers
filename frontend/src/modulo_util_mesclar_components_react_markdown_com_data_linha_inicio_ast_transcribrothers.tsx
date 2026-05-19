import type { Components } from "react-markdown";
import type { Element } from "hast";
import type { ImgHTMLAttributes, ReactNode } from "react";
import { createContext, createElement, useContext, type MutableRefObject } from "react";
import type { AncoraBlocoMarkdownTutorialTranscribrothers } from "./modulo_util_bloco_ancora_linha_markdown_sincronizacao_preview_editor_transcribrothers.ts";

type PropsComponenteMarkdownComNoAstTranscribrothers = {
  node?: { children?: unknown[] };
  children?: ReactNode;
  className?: string;
  id?: string;
};

const ContextoDentroBlockquoteMarkdownPreviewTranscribrothers = createContext(false);
const ContextoDentroItemListaMarkdownPreviewTranscribrothers = createContext(false);
const ContextoDentroTabelaMarkdownPreviewTranscribrothers = createContext(false);

const TAGS_BLOCO_COM_ANCORA_FONTE_MARKDOWN: Array<keyof JSX.IntrinsicElements> = [
  "h1",
  "h3",
  "h4",
  "h5",
  "h6",
  "pre",
  "hr",
];

export function consumirProximaAncoraLinhaFonteMarkdownPreviewTranscribrothers(
  indiceAncoraRef: MutableRefObject<number>,
  ancorasFonte: AncoraBlocoMarkdownTutorialTranscribrothers[],
): AncoraBlocoMarkdownTutorialTranscribrothers | null {
  if (indiceAncoraRef.current >= ancorasFonte.length) return null;
  return ancorasFonte[indiceAncoraRef.current++];
}

function atributosAncoraLinhaFonteMarkdownPreviewTranscribrothers(
  ancora: AncoraBlocoMarkdownTutorialTranscribrothers | null,
): Record<string, string> {
  if (!ancora) return {};
  return {
    "data-tb-linha-inicio": String(ancora.numeroLinha),
    "data-tb-tipo-bloco": ancora.tipo,
    id: `tb-md-linha-${ancora.numeroLinha}`,
  };
}

function mesclarClasseComAncoraBlocoMarkdownTranscribrothers(className?: string): string {
  return [className, "tb-modal-md-edit-bloco-ancora"].filter(Boolean).join(" ");
}

function envolverConteudoComAncoraLinhaSeNecessarioTranscribrothers(
  conteudo: ReactNode,
  ancora: AncoraBlocoMarkdownTutorialTranscribrothers | null,
): ReactNode {
  if (conteudo == null || !ancora) return conteudo;
  return (
    <div
      className="tb-modal-md-edit-bloco-ancora tb-modal-md-edit-bloco-wrap"
      {...atributosAncoraLinhaFonteMarkdownPreviewTranscribrothers(ancora)}
    >
      {conteudo}
    </div>
  );
}

export function mesclarComponentsReactMarkdownComAncorasLinhaFonteDocumentoTranscribrothers(
  componentsBase: Components,
  ancorasFonte: AncoraBlocoMarkdownTutorialTranscribrothers[],
  indiceAncoraRenderizadoRef: MutableRefObject<number>,
): Components {
  const resultado: Components = { ...componentsBase };

  const renderComAncoraFonte = (
    tag: keyof JSX.IntrinsicElements,
    props: PropsComponenteMarkdownComNoAstTranscribrothers,
    componenteOriginal: Components[keyof Components] | undefined,
  ): ReactNode => {
    const dentroBlockquote = useContext(ContextoDentroBlockquoteMarkdownPreviewTranscribrothers);
    const dentroItemLista = useContext(ContextoDentroItemListaMarkdownPreviewTranscribrothers);
    const dentroTabela = useContext(ContextoDentroTabelaMarkdownPreviewTranscribrothers);

    if (dentroBlockquote || dentroItemLista || dentroTabela) {
      if (typeof componenteOriginal === "function") {
        const Elemento = componenteOriginal;
        return <Elemento {...props} />;
      }
      if (typeof componenteOriginal === "string") {
        return createElement(componenteOriginal, props);
      }
      return createElement(tag, props);
    }

    const ancora = consumirProximaAncoraLinhaFonteMarkdownPreviewTranscribrothers(
      indiceAncoraRenderizadoRef,
      ancorasFonte,
    );
    const propsComAncora = {
      ...props,
      ...atributosAncoraLinhaFonteMarkdownPreviewTranscribrothers(ancora),
      className: mesclarClasseComAncoraBlocoMarkdownTranscribrothers(props.className),
    };

    if (typeof componenteOriginal === "function") {
      const Elemento = componenteOriginal;
      return <Elemento {...propsComAncora} />;
    }
    if (typeof componenteOriginal === "string") {
      return createElement(componenteOriginal, propsComAncora);
    }
    return createElement(tag, propsComAncora);
  };

  const paragrafoOriginal = componentsBase.p;
  resultado.p = (props) => {
    const filhosNo = props.node?.children;
    const paragrafoSoComImagem =
      Array.isArray(filhosNo) &&
      filhosNo.length === 1 &&
      typeof filhosNo[0] === "object" &&
      filhosNo[0] !== null &&
      "type" in filhosNo[0] &&
      (filhosNo[0] as { type?: string }).type === "element" &&
      "tagName" in filhosNo[0] &&
      (filhosNo[0] as Element).tagName === "img";

    if (paragrafoSoComImagem) {
      if (typeof paragrafoOriginal === "function") {
        const ParagrafoOriginal = paragrafoOriginal;
        return <ParagrafoOriginal {...props} />;
      }
      return <p {...props}>{props.children}</p>;
    }

    const dentroBlockquote = useContext(ContextoDentroBlockquoteMarkdownPreviewTranscribrothers);
    const dentroItemLista = useContext(ContextoDentroItemListaMarkdownPreviewTranscribrothers);
    const dentroTabela = useContext(ContextoDentroTabelaMarkdownPreviewTranscribrothers);

    if (dentroBlockquote || dentroItemLista || dentroTabela) {
      if (typeof paragrafoOriginal === "function") {
        const ParagrafoOriginal = paragrafoOriginal;
        return <ParagrafoOriginal {...props} />;
      }
      return <p {...props}>{props.children}</p>;
    }

    const ancora = consumirProximaAncoraLinhaFonteMarkdownPreviewTranscribrothers(
      indiceAncoraRenderizadoRef,
      ancorasFonte,
    );
    const propsComAncora = {
      ...props,
      ...atributosAncoraLinhaFonteMarkdownPreviewTranscribrothers(ancora),
      className: mesclarClasseComAncoraBlocoMarkdownTranscribrothers(props.className),
    };

    if (typeof paragrafoOriginal === "function") {
      const ParagrafoOriginal = paragrafoOriginal;
      return <ParagrafoOriginal {...propsComAncora} />;
    }
    return <p {...propsComAncora}>{props.children}</p>;
  };

  const blockquoteOriginal = componentsBase.blockquote;
  resultado.blockquote = (props) => {
    const ancora = consumirProximaAncoraLinhaFonteMarkdownPreviewTranscribrothers(
      indiceAncoraRenderizadoRef,
      ancorasFonte,
    );
    const propsComAncora = {
      ...props,
      ...atributosAncoraLinhaFonteMarkdownPreviewTranscribrothers(ancora),
      className: mesclarClasseComAncoraBlocoMarkdownTranscribrothers(props.className),
    };
    const conteudo =
      typeof blockquoteOriginal === "function" ? (
        (() => {
          const BlockquoteOriginal = blockquoteOriginal;
          return <BlockquoteOriginal {...propsComAncora} />;
        })()
      ) : (
        <blockquote {...propsComAncora}>{props.children}</blockquote>
      );
    return (
      <ContextoDentroBlockquoteMarkdownPreviewTranscribrothers.Provider value={true}>
        {conteudo}
      </ContextoDentroBlockquoteMarkdownPreviewTranscribrothers.Provider>
    );
  };

  const liOriginal = componentsBase.li;
  resultado.li = (props) => {
    const ancora = consumirProximaAncoraLinhaFonteMarkdownPreviewTranscribrothers(
      indiceAncoraRenderizadoRef,
      ancorasFonte,
    );
    const propsComAncora = {
      ...props,
      ...atributosAncoraLinhaFonteMarkdownPreviewTranscribrothers(ancora),
      className: mesclarClasseComAncoraBlocoMarkdownTranscribrothers(props.className),
    };
    const conteudo =
      typeof liOriginal === "function" ? (
        (() => {
          const LiOriginal = liOriginal;
          return <LiOriginal {...propsComAncora} />;
        })()
      ) : (
        <li {...propsComAncora}>{props.children}</li>
      );
    return (
      <ContextoDentroItemListaMarkdownPreviewTranscribrothers.Provider value={true}>
        {conteudo}
      </ContextoDentroItemListaMarkdownPreviewTranscribrothers.Provider>
    );
  };

  const tableOriginal = componentsBase.table;
  resultado.table = (props) => {
    const ancora = consumirProximaAncoraLinhaFonteMarkdownPreviewTranscribrothers(
      indiceAncoraRenderizadoRef,
      ancorasFonte,
    );
    const propsComAncora = {
      ...props,
      ...atributosAncoraLinhaFonteMarkdownPreviewTranscribrothers(ancora),
      className: mesclarClasseComAncoraBlocoMarkdownTranscribrothers(props.className),
    };
    const conteudo =
      typeof tableOriginal === "function" ? (
        (() => {
          const TableOriginal = tableOriginal;
          return <TableOriginal {...propsComAncora} />;
        })()
      ) : (
        <table {...propsComAncora}>{props.children}</table>
      );
    return (
      <ContextoDentroTabelaMarkdownPreviewTranscribrothers.Provider value={true}>
        {conteudo}
      </ContextoDentroTabelaMarkdownPreviewTranscribrothers.Provider>
    );
  };

  for (const tag of TAGS_BLOCO_COM_ANCORA_FONTE_MARKDOWN) {
    const original = componentsBase[tag];
    resultado[tag] = (props) => renderComAncoraFonte(tag, props, original);
  }

  const imgOriginal = componentsBase.img;
  resultado.img = (props) => {
    const ancora = consumirProximaAncoraLinhaFonteMarkdownPreviewTranscribrothers(
      indiceAncoraRenderizadoRef,
      ancorasFonte,
    );
    const { node, alt, src, className, ...restImg } = props;

    let conteudo: ReactNode;
    if (typeof imgOriginal === "function") {
      const ImgOriginal = imgOriginal;
      conteudo = <ImgOriginal node={node} alt={alt} src={src} className={className} {...restImg} />;
    } else {
      conteudo = <img alt={alt ?? ""} src={src} className={className} {...restImg} />;
    }

    return envolverConteudoComAncoraLinhaSeNecessarioTranscribrothers(conteudo, ancora);
  };

  return resultado;
}
