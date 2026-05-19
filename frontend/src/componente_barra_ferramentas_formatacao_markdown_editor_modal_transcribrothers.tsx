import type { ReactNode } from "react";
import type { TipoAcaoFormatacaoMarkdownTextareaEdicaoTranscribrothers } from "./modulo_util_aplicar_formatacao_markdown_selecao_textarea_edicao_transcribrothers.ts";

type BotaoFormatacaoMarkdownEditorModalTranscribrothers = {
  acao: TipoAcaoFormatacaoMarkdownTextareaEdicaoTranscribrothers;
  rotuloAcessivel: string;
  titulo: string;
  conteudo: ReactNode;
  classeExtra?: string;
};

const BOTOES_FORMATACAO_MARKDOWN_EDITOR_MODAL: BotaoFormatacaoMarkdownEditorModalTranscribrothers[] =
  [
    {
      acao: "negrito",
      rotuloAcessivel: "Negrito",
      titulo: "Negrito (**texto**)",
      conteudo: <strong>B</strong>,
      classeExtra: "tb-modal-md-edit-barra-formatacao-btn--negrito",
    },
    {
      acao: "italico",
      rotuloAcessivel: "Itálico",
      titulo: "Itálico (*texto*)",
      conteudo: <em>I</em>,
      classeExtra: "tb-modal-md-edit-barra-formatacao-btn--italico",
    },
    {
      acao: "tachado",
      rotuloAcessivel: "Tachado",
      titulo: "Tachado (~~texto~~)",
      conteudo: <span className="tb-modal-md-edit-barra-formatacao-tachado">S</span>,
    },
    {
      acao: "codigo-inline",
      rotuloAcessivel: "Código inline",
      titulo: "Código inline (`codigo`)",
      conteudo: <span className="tb-modal-md-edit-barra-formatacao-codigo">{`</>`}</span>,
    },
    {
      acao: "link",
      rotuloAcessivel: "Link",
      titulo: "Link ([texto](url))",
      conteudo: "🔗",
    },
    {
      acao: "titulo-2",
      rotuloAcessivel: "Título nível 2",
      titulo: "Título (## texto)",
      conteudo: "H2",
    },
    {
      acao: "lista-marcadores",
      rotuloAcessivel: "Lista com marcadores",
      titulo: "Lista com marcadores (- item)",
      conteudo: "•",
    },
    {
      acao: "lista-numerada",
      rotuloAcessivel: "Lista numerada",
      titulo: "Lista numerada (1. item)",
      conteudo: "1.",
    },
    {
      acao: "citacao",
      rotuloAcessivel: "Citação",
      titulo: "Citação (> texto)",
      conteudo: "❝",
    },
    {
      acao: "tabela",
      rotuloAcessivel: "Tabela",
      titulo: "Inserir tabela Markdown",
      conteudo: "⊞",
      classeExtra: "tb-modal-md-edit-barra-formatacao-btn--tabela",
    },
  ];

export type PropsComponenteBarraFerramentasFormatacaoMarkdownEditorModalTranscribrothers =
  {
    aoAcionarFormatacao: (
      acao: TipoAcaoFormatacaoMarkdownTextareaEdicaoTranscribrothers,
    ) => void;
    desabilitado?: boolean;
  };

export function ComponenteBarraFerramentasFormatacaoMarkdownEditorModalTranscribrothers({
  aoAcionarFormatacao,
  desabilitado = false,
}: PropsComponenteBarraFerramentasFormatacaoMarkdownEditorModalTranscribrothers) {
  return (
    <div
      className="tb-modal-md-edit-barra-formatacao-md"
      role="toolbar"
      aria-label="Formatação Markdown"
      onMouseDown={(evento) => evento.preventDefault()}
    >
      {BOTOES_FORMATACAO_MARKDOWN_EDITOR_MODAL.map((botao) => (
        <button
          key={botao.acao}
          type="button"
          className={[
            "tb-modal-md-edit-barra-formatacao-btn",
            botao.classeExtra ?? "",
          ]
            .filter(Boolean)
            .join(" ")}
          title={botao.titulo}
          aria-label={botao.rotuloAcessivel}
          disabled={desabilitado}
          onClick={() => aoAcionarFormatacao(botao.acao)}
        >
          {botao.conteudo}
        </button>
      ))}
    </div>
  );
}
