import type { AnchorHTMLAttributes, ReactNode } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { segundosDeHrefTimestampTutorialOuChatTranscribrothers } from "./modulo_tipos_item_historico_chat_ask_agente_documento_job_transcribrothers.ts";

export function ComponenteTextoMarkdownBolhaChatAskAgenteDocumentoTranscribrothers({
  texto,
  aoIrParaInstante,
}: {
  texto: string;
  aoIrParaInstante?: (segundos: number) => void;
}) {
  const conteudo = (texto || "").trim() ? texto : "";
  if (!conteudo) return null;
  return (
    <div className="tb-chat-ask-agente-mensagem-texto tb-chat-ask-agente-mensagem-texto--markdown">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          img: () => null,
          a: ({
            href,
            children,
            ...rest
          }: AnchorHTMLAttributes<HTMLAnchorElement> & { children?: ReactNode }) => {
            const segundos = segundosDeHrefTimestampTutorialOuChatTranscribrothers(href);
            if (segundos != null && aoIrParaInstante) {
              return (
                <button
                  type="button"
                  className="tb-tslink"
                  onClick={() => aoIrParaInstante(segundos)}
                >
                  {children}
                </button>
              );
            }
            return (
              <a href={href} {...rest}>
                {children}
              </a>
            );
          },
        }}
      >
        {conteudo}
      </ReactMarkdown>
    </div>
  );
}
