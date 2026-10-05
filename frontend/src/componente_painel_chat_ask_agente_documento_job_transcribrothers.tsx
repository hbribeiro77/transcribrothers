import type * as React from "react";
import { useEffect, useRef, useState } from "react";
import {
  rotuloCurtoModeloChatAskAgenteParaUiTranscribrothers,
} from "./modulo_util_modelo_chat_ask_agente_documento_transcribrothers.ts";
import type { AnexoContextoFabUiTranscribrothers } from "./modulo_api_anexos_contexto_fab_projeto_em_branco_transcribrothers.ts";
import {
  caminhosRelativosDeImagensHistoricoChatAskTranscribrothers,
  citacaoChatAskDeveAparecerComoChipTranscribrothers,
  instanteSegundosParaSeekCitacaoChatAskTranscribrothers,
  propostaFerramentaChatAgenteDeveMostrarBotaoAplicarNaBolhaTranscribrothers,
  rotuloChipCitacaoChatAskDocumentoJobTranscribrothers,
  type CitacaoItemHistoricoChatAskDocumentoJobTranscribrothers,
  type ImagemItemHistoricoChatAskDocumentoJobTranscribrothers,
  type PropostaFerramentaChatAgenteDocumentoJobTranscribrothers,
} from "./modulo_tipos_item_historico_chat_ask_agente_documento_job_transcribrothers.ts";
import { rotuloBotaoPropostaFerramentaChatAgenteTranscribrothers } from "./modulo_util_ferramenta_forcada_pelo_chip_agente_documento_transcribrothers.ts";
import { rotuloExibicaoAnexoTextoContextoFabUiTranscribrothers } from "./modulo_util_anexo_texto_contexto_fab_projeto_em_branco_transcribrothers.ts";
import { classesPainelGavetaChatAskAgenteDocumentoTranscribrothers } from "./modulo_util_classes_gaveta_chat_ask_agente_empurra_grid_transcribrothers.ts";
import { ComponenteTextoMarkdownBolhaChatAskAgenteDocumentoTranscribrothers } from "./componente_texto_markdown_bolha_chat_ask_agente_documento_transcribrothers.tsx";
import { TEXTO_STATUS_PREPARANDO_PREVIA_DOCUMENTO_CHAT_TRANSCRIBROTHERS } from "./modulo_util_feedback_previa_documento_no_chat_ask_agente_transcribrothers.ts";

function IconeMaisComposerChatAskAgenteTranscribrothers() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M12 5v14M5 12h14"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
      />
    </svg>
  );
}

function IconeEnviarComposerChatAskAgenteTranscribrothers() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M12 19V5M6 11l6-6 6 6"
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export type ModoChatAskOuAgenteDocumentoTranscribrothers = "ask" | "agente";

export type MensagemChatAskAgenteDocumentoEmMemoriaTranscribrothers = {
  id: string;
  papel: "usuario" | "assistente" | "agente";
  texto: string;
  citacoes?: CitacaoItemHistoricoChatAskDocumentoJobTranscribrothers[];
  imagens?: ImagemItemHistoricoChatAskDocumentoJobTranscribrothers[];
  estado?: string | null;
  tipo_pipeline?: string | null;
  proposta_ferramenta?: PropostaFerramentaChatAgenteDocumentoJobTranscribrothers | null;
  propostas_ferramenta?: PropostaFerramentaChatAgenteDocumentoJobTranscribrothers[];
  executar_proposta?: boolean;
  ehErro?: boolean;
};

export type ImagemContextoPedidoPainelChatAskAgenteTranscribrothers = {
  figura: number;
  rotulo: string;
  caminho: string;
};

export type PropsAnexosProjetoEmBrancoPainelChatAskAgenteDocumentoTranscribrothers = {
  anexos: AnexoContextoFabUiTranscribrothers[];
  aoRemoverAnexo: (id: string) => void;
  processando: boolean;
  arrastando: boolean;
  imagensQueOModeloVera: ImagemContextoPedidoPainelChatAskAgenteTranscribrothers[];
  menuMaisAberto: boolean;
  aoAlternarMenuMais: () => void;
  aoFecharMenuMais: () => void;
  menuMaisDesabilitado: boolean;
  aoPedirTexto: () => void;
  aoSelecionarImagem: (arquivo: File) => void;
  aoSelecionarDocumentos: (arquivos: File[]) => void;
  refMenuMais: React.RefObject<HTMLDivElement | null>;
  refInputImagem: React.RefObject<HTMLInputElement | null>;
  refInputDocumento: React.RefObject<HTMLInputElement | null>;
};

export type PropsComponentePainelChatAskAgenteDocumentoJobTranscribrothers = {
  modo: ModoChatAskOuAgenteDocumentoTranscribrothers;
  aoAlternarModo: (modo: ModoChatAskOuAgenteDocumentoTranscribrothers) => void;
  askDisponivel: boolean;
  titulo?: string;
  disabledEnviar: boolean;
  textoInstrucoes: string;
  aoMudarTexto: (texto: string) => void;
  aoEnviar: () => void;
  childrenChips: React.ReactNode;
  mensagens: MensagemChatAskAgenteDocumentoEmMemoriaTranscribrothers[];
  exibirCartaoVerPreviaNaUltimaMensagemAgente?: boolean;
  aoAbrirPreviaDocumento?: () => void;
  aoAplicarPropostaFerramenta?: (
    proposta: PropostaFerramentaChatAgenteDocumentoJobTranscribrothers,
    caminhosImagensMensagem?: string[],
    propostas?: PropostaFerramentaChatAgenteDocumentoJobTranscribrothers[],
    mensagemId?: string,
  ) => void;
  aoIrParaInstanteCitacao?: (segundos: number) => void;
  enviandoMensagemAsk?: boolean;
  preparandoPreviaDocumento?: boolean;
  composerTravado?: boolean;
  aoFechar: () => void;
  rotuloBotaoEnviar: string;
  placeholderCampo: string;
  rotuloCampo: string | null;
  refTextarea: React.RefObject<HTMLTextAreaElement | null>;
  referenciasFigurasMarkdown: string[];
  anexosProjetoEmBranco: PropsAnexosProjetoEmBrancoPainelChatAskAgenteDocumentoTranscribrothers | null;
  aoColarNoPainel?: (evento: React.ClipboardEvent) => void;
  aoDragEnter?: (evento: React.DragEvent) => void;
  aoDragLeave?: (evento: React.DragEvent) => void;
  aoDrop?: (evento: React.DragEvent) => void;
  aoPedirLimpar: () => void;
  limparDesabilitado: boolean;
  aoAnexarFrameDoPlayer?: () => void;
  anexarFrameDesabilitado?: boolean;
  tituloAnexarFrame?: string;
  chipFrameAnexo?: {
    url: string;
    instante_segundos: number;
    caminho_relativo: string;
    origem: string;
  } | null;
  aoRemoverChipFrameAnexo?: () => void;
  aberta?: boolean;
  modeloChat?: string;
  modelosChat?: string[];
  aoEscolherModeloChat?: (modelo: string) => void;
};

export function ComponentePainelChatAskAgenteDocumentoJobTranscribrothers({
  modo,
  aoAlternarModo,
  askDisponivel,
  disabledEnviar,
  textoInstrucoes,
  aoMudarTexto,
  aoEnviar,
  childrenChips,
  mensagens,
  exibirCartaoVerPreviaNaUltimaMensagemAgente = false,
  aoAbrirPreviaDocumento,
  aoAplicarPropostaFerramenta,
  aoIrParaInstanteCitacao,
  enviandoMensagemAsk = false,
  preparandoPreviaDocumento = false,
  composerTravado = false,
  aoFechar,
  rotuloBotaoEnviar,
  placeholderCampo,
  refTextarea,
  referenciasFigurasMarkdown,
  anexosProjetoEmBranco,
  aoColarNoPainel,
  aoDragEnter,
  aoDragLeave,
  aoDrop,
  aoPedirLimpar,
  limparDesabilitado,
  aoAnexarFrameDoPlayer,
  anexarFrameDesabilitado = true,
  tituloAnexarFrame,
  chipFrameAnexo = null,
  aoRemoverChipFrameAnexo,
  aberta = true,
  modeloChat = "",
  modelosChat = [],
  aoEscolherModeloChat,
}: PropsComponentePainelChatAskAgenteDocumentoJobTranscribrothers) {
  const refFimListaMensagens = useRef<HTMLDivElement | null>(null);
  const refMenuModeloChat = useRef<HTMLDivElement | null>(null);
  const [menuModeloChatAberto, setMenuModeloChatAberto] = useState(false);
  useEffect(() => {
    if (!menuModeloChatAberto) return;
    const fecharSeCliqueFora = (evento: MouseEvent) => {
      const alvo = evento.target as Node | null;
      if (alvo && refMenuModeloChat.current?.contains(alvo)) return;
      setMenuModeloChatAberto(false);
    };
    document.addEventListener("mousedown", fecharSeCliqueFora);
    return () => document.removeEventListener("mousedown", fecharSeCliqueFora);
  }, [menuModeloChatAberto]);
  const enviarBloqueado =
    composerTravado ||
    (modo === "ask"
      ? !askDisponivel || enviandoMensagemAsk || !textoInstrucoes.trim()
      : disabledEnviar);

  useEffect(() => {
    refFimListaMensagens.current?.scrollIntoView({ block: "nearest" });
  }, [mensagens, enviandoMensagemAsk]);
  const indiceUltimoAgente = mensagens.reduce(
    (acumulado, item, indice) => (item.papel === "agente" ? indice : acumulado),
    -1,
  );
  const placeholder =
    modo === "ask" ? "Pergunte sobre o documento…" : placeholderCampo;
  const classesPainel = classesPainelGavetaChatAskAgenteDocumentoTranscribrothers({
    aberta,
    projetoEmBranco: Boolean(anexosProjetoEmBranco),
    arrastando: Boolean(anexosProjetoEmBranco?.arrastando),
    processando: Boolean(anexosProjetoEmBranco?.processando),
  });

  const tituloBotaoMaisFrame =
    tituloAnexarFrame ?? "Não há vídeo para anexar um frame.";

  return (
    <aside
      className={classesPainel}
      aria-label="Chat"
      aria-hidden={!aberta}
      {...(!aberta ? { inert: "" } : {})}
      onPaste={anexosProjetoEmBranco ? aoColarNoPainel : undefined}
      onDragEnter={anexosProjetoEmBranco ? aoDragEnter : undefined}
      onDragLeave={anexosProjetoEmBranco ? aoDragLeave : undefined}
      onDragOver={
        anexosProjetoEmBranco
          ? (evento) => {
              evento.preventDefault();
            }
          : undefined
      }
      onDrop={anexosProjetoEmBranco ? aoDrop : undefined}
    >
      <div className="tb-chat-ask-agente-cabecalho">
        <span className="tb-chat-ask-agente-cabecalho-titulo">Chat</span>
        <button
          type="button"
          className="tb-chat-ask-agente-ocultar"
          aria-label="Ocultar chat"
          onClick={aoFechar}
        >
          ×
        </button>
      </div>
      <div className="tb-chat-ask-agente-mensagens" aria-live="polite">
        {mensagens.length === 0 && !enviandoMensagemAsk ? (
          <p className="tb-muted tb-fab-chat-vazio">As mensagens deste job aparecem aqui.</p>
        ) : (
          mensagens.map((mensagem, indiceMensagem) => {
            const mostrarVerPrevia =
              exibirCartaoVerPreviaNaUltimaMensagemAgente &&
              indiceMensagem === indiceUltimoAgente &&
              Boolean(aoAbrirPreviaDocumento);
            const mostrarGerando =
              mensagem.papel === "agente" && mensagem.estado === "gerando" && !mostrarVerPrevia;
            const mostrarFalhou =
              mensagem.papel === "agente" && mensagem.estado === "falhou" && !mostrarVerPrevia;
            const mostrarCitacoesEImagens =
              !mensagem.ehErro && (mensagem.papel === "assistente" || mensagem.papel === "agente");
            const rotuloProposta = rotuloBotaoPropostaFerramentaChatAgenteTranscribrothers(
              mensagem.proposta_ferramenta?.nome,
            );
            const mostrarProposta =
              Boolean(aoAplicarPropostaFerramenta) &&
              rotuloProposta.length > 0 &&
              propostaFerramentaChatAgenteDeveMostrarBotaoAplicarNaBolhaTranscribrothers({
                temProposta: Boolean(mensagem.proposta_ferramenta),
                executarProposta: mensagem.executar_proposta === true,
                estado: mensagem.estado,
                nomeFerramenta: mensagem.proposta_ferramenta?.nome,
                ehUltimaMensagemAgente: indiceMensagem === indiceUltimoAgente,
              }) && !preparandoPreviaDocumento;
            const citacoesVisiveis = mostrarCitacoesEImagens
              ? (mensagem.citacoes ?? []).filter((citacao) =>
                  citacaoChatAskDeveAparecerComoChipTranscribrothers(citacao, mensagem.texto),
                )
              : [];
            const imagens = mostrarCitacoesEImagens
              ? (mensagem.imagens ?? []).filter((imagem) => imagem.url.trim().length > 0)
              : [];
            return (
              <div
                key={mensagem.id}
                className={[
                  "tb-chat-ask-agente-mensagem",
                  `tb-chat-ask-agente-mensagem--${mensagem.papel}`,
                  mensagem.ehErro ? "tb-chat-ask-agente-mensagem--erro" : "",
                ]
                  .filter(Boolean)
                  .join(" ")}
              >
                {mensagem.ehErro || mensagem.papel === "usuario" ? (
                  <p className="tb-chat-ask-agente-mensagem-texto">{mensagem.texto}</p>
                ) : (
                  <ComponenteTextoMarkdownBolhaChatAskAgenteDocumentoTranscribrothers
                    texto={mensagem.texto}
                    aoIrParaInstante={aoIrParaInstanteCitacao}
                  />
                )}
                {mostrarGerando ? (
                  <p className="tb-chat-ask-agente-gerando">Gerando prévia…</p>
                ) : null}
                {mostrarFalhou ? (
                  <p className="tb-chat-ask-agente-falhou">A prévia não foi gerada.</p>
                ) : null}
                {mostrarVerPrevia ? (
                  <button
                    type="button"
                    className="tb-chat-ask-agente-ver-previa"
                    onClick={() => aoAbrirPreviaDocumento?.()}
                  >
                    Ver prévia
                  </button>
                ) : null}
                {mostrarProposta && mensagem.proposta_ferramenta ? (
                  <button
                    type="button"
                    className="tb-chat-ask-agente-ver-previa"
                    onClick={() =>
                      aoAplicarPropostaFerramenta?.(
                        mensagem.proposta_ferramenta!,
                        caminhosRelativosDeImagensHistoricoChatAskTranscribrothers(mensagem.imagens),
                        mensagem.propostas_ferramenta,
                        mensagem.id,
                      )
                    }
                  >
                    {rotuloProposta}
                  </button>
                ) : null}
                {citacoesVisiveis.length > 0 ? (
                  <ul className="tb-chat-ask-agente-citacoes" aria-label="Citações">
                    {citacoesVisiveis.map((citacao, indice) => {
                      const rotulo = rotuloChipCitacaoChatAskDocumentoJobTranscribrothers(citacao);
                      const instante = instanteSegundosParaSeekCitacaoChatAskTranscribrothers(citacao);
                      return (
                        <li key={`${mensagem.id}-cit-${indice}`}>
                          {instante != null && aoIrParaInstanteCitacao ? (
                            <button
                              type="button"
                              className="tb-chat-ask-agente-citacao-chip tb-chat-ask-agente-citacao-chip--tempo"
                              onClick={() => aoIrParaInstanteCitacao(instante)}
                              aria-label={`Ir para ${rotulo} no vídeo`}
                            >
                              {rotulo}
                            </button>
                          ) : (
                            <span className="tb-chat-ask-agente-citacao-chip">{rotulo}</span>
                          )}
                        </li>
                      );
                    })}
                  </ul>
                ) : null}
                {imagens.map((imagem, indice) => (
                  <img
                    key={`${mensagem.id}-img-${indice}`}
                    className="tb-chat-ask-agente-imagem"
                    src={imagem.url}
                    alt=""
                  />
                ))}
              </div>
            );
          })
        )}
        {enviandoMensagemAsk &&
        !mensagens.some(
          (mensagem) => mensagem.estado === "escrevendo" && (mensagem.texto || "").trim().length > 0,
        ) ? (
          <p className="tb-chat-ask-agente-mensagem tb-chat-ask-agente-mensagem--assistente tb-chat-ask-agente-mensagem--pensando">
            pensando…
          </p>
        ) : null}
        {preparandoPreviaDocumento ? (
          <p
            className="tb-chat-ask-agente-mensagem tb-chat-ask-agente-mensagem--agente tb-chat-ask-agente-preparando-previa"
            aria-live="polite"
          >
            <span className="tb-chat-ask-agente-preparando-previa-spinner" aria-hidden />
            {TEXTO_STATUS_PREPARANDO_PREVIA_DOCUMENTO_CHAT_TRANSCRIBROTHERS}
          </p>
        ) : null}
        <div ref={refFimListaMensagens} />
      </div>
      {anexosProjetoEmBranco ? (
        <div className="tb-fab-chat-anexos-secao">
          {anexosProjetoEmBranco.anexos.length > 0 ||
          anexosProjetoEmBranco.processando ||
          anexosProjetoEmBranco.arrastando ? (
            <div className="tb-fab-chat-corpo" aria-live="polite">
              {anexosProjetoEmBranco.processando ? (
                <p className="tb-muted tb-fab-chat-status">Processando anexos…</p>
              ) : null}
              {anexosProjetoEmBranco.arrastando ? (
                <p className="tb-fab-chat-status tb-fab-chat-status--arraste">
                  Solte para anexar ao pedido
                </p>
              ) : null}
              {anexosProjetoEmBranco.anexos.length > 0 ? (
                <ul className="tb-fab-anexos-lista" aria-label="Anexos do pedido">
                  {anexosProjetoEmBranco.anexos.map((anexo, indiceAnexo) => (
                    <li key={anexo.id} className="tb-fab-anexos-item">
                      <span className="tb-fab-anexos-item-rotulo">
                        {anexo.tipo === "imagem"
                          ? `Imagem · ${anexo.nomeArquivo}`
                          : `Texto · ${rotuloExibicaoAnexoTextoContextoFabUiTranscribrothers(anexo, indiceAnexo)}`}
                      </span>
                      <button
                        type="button"
                        className="tb-fab-anexos-remover"
                        aria-label="Remover anexo"
                        onClick={() => anexosProjetoEmBranco.aoRemoverAnexo(anexo.id)}
                      >
                        ×
                      </button>
                    </li>
                  ))}
                </ul>
              ) : null}
            </div>
          ) : null}
        </div>
      ) : null}
      {modo === "agente" ? childrenChips : null}
      <div className="tb-chat-ask-agente-composer-faixa">
        <div role="tablist" aria-label="Modo do chat" className="tb-chat-ask-agente-modo-tablist">
          <button
            type="button"
            role="tab"
            className="tb-chat-ask-agente-modo-tab"
            aria-selected={modo === "ask"}
            disabled={composerTravado}
            onClick={() => aoAlternarModo("ask")}
          >
            Ask
          </button>
          <button
            type="button"
            role="tab"
            className="tb-chat-ask-agente-modo-tab"
            aria-selected={modo === "agente"}
            disabled={composerTravado}
            onClick={() => aoAlternarModo("agente")}
          >
            Agente
          </button>
        </div>
        {modelosChat.length > 0 && aoEscolherModeloChat ? (
          <div className="tb-chat-ask-agente-modelo-wrap" ref={refMenuModeloChat}>
            <button
              type="button"
              className="tb-chat-ask-agente-modelo-btn"
              aria-haspopup="listbox"
              aria-expanded={menuModeloChatAberto}
              aria-label={`Modelo do chat: ${modeloChat || "escolher"}`}
              title={modeloChat || "Escolher modelo do chat"}
              disabled={composerTravado}
              onClick={() => setMenuModeloChatAberto((aberto) => !aberto)}
            >
              <span className="tb-chat-ask-agente-modelo-rotulo">
                {rotuloCurtoModeloChatAskAgenteParaUiTranscribrothers(modeloChat) || "Modelo"}
              </span>
              <span className="tb-chat-ask-agente-modelo-seta" aria-hidden>
                ▾
              </span>
            </button>
            {menuModeloChatAberto ? (
              <ul className="tb-chat-ask-agente-modelo-menu" role="listbox" aria-label="Modelos do chat">
                {modelosChat.map((slug) => (
                  <li key={slug}>
                    <button
                      type="button"
                      role="option"
                      aria-selected={slug === modeloChat}
                      className={
                        slug === modeloChat
                          ? "tb-chat-ask-agente-modelo-item tb-chat-ask-agente-modelo-item--ativo"
                          : "tb-chat-ask-agente-modelo-item"
                      }
                      onClick={() => {
                        aoEscolherModeloChat(slug);
                        setMenuModeloChatAberto(false);
                      }}
                    >
                      {rotuloCurtoModeloChatAskAgenteParaUiTranscribrothers(slug)}
                    </button>
                  </li>
                ))}
              </ul>
            ) : null}
          </div>
        ) : null}
        <button
          type="button"
          className="tb-chat-ask-agente-limpar-btn"
          disabled={limparDesabilitado}
          onClick={aoPedirLimpar}
        >
          Limpar
        </button>
      </div>
      <div className="tb-fab-chat-composer">
        {chipFrameAnexo ? (
          <div className="tb-chat-ask-agente-chip-frame-anexo">
            <img
              src={chipFrameAnexo.url}
              alt=""
              className="tb-chat-ask-agente-chip-frame-anexo-img"
            />
            <span className="tb-chat-ask-agente-chip-frame-anexo-label">
              Frame em {chipFrameAnexo.instante_segundos.toFixed(1)}s
            </span>
            <button
              type="button"
              className="tb-chat-ask-agente-chip-frame-anexo-remover"
              aria-label="Remover frame anexado"
              onClick={() => aoRemoverChipFrameAnexo?.()}
            >
              ×
            </button>
          </div>
        ) : null}
        <div className="tb-fab-chat-composer-capsule">
          {anexosProjetoEmBranco ? (
            <div className="tb-fab-mais-menu-wrap" ref={anexosProjetoEmBranco.refMenuMais as React.Ref<HTMLDivElement>}>
              <button
                type="button"
                className="tb-fab-mais-btn"
                aria-label="Adicionar conteúdo ao pedido"
                aria-expanded={anexosProjetoEmBranco.menuMaisAberto}
                aria-haspopup="menu"
                disabled={anexosProjetoEmBranco.menuMaisDesabilitado}
                onClick={anexosProjetoEmBranco.aoAlternarMenuMais}
              >
                <IconeMaisComposerChatAskAgenteTranscribrothers />
              </button>
              {anexosProjetoEmBranco.menuMaisAberto ? (
                <div className="tb-fab-mais-menu" role="menu">
                  <button
                    type="button"
                    className="tb-fab-mais-menu-item"
                    role="menuitem"
                    onClick={() => {
                      anexosProjetoEmBranco.aoFecharMenuMais();
                      anexosProjetoEmBranco.aoPedirTexto();
                    }}
                  >
                    Texto
                  </button>
                  <button
                    type="button"
                    className="tb-fab-mais-menu-item"
                    role="menuitem"
                    onClick={() => {
                      anexosProjetoEmBranco.aoFecharMenuMais();
                      anexosProjetoEmBranco.refInputImagem.current?.click();
                    }}
                  >
                    Imagem
                  </button>
                  <button
                    type="button"
                    className="tb-fab-mais-menu-item"
                    role="menuitem"
                    onClick={() => {
                      anexosProjetoEmBranco.aoFecharMenuMais();
                      anexosProjetoEmBranco.refInputDocumento.current?.click();
                    }}
                  >
                    Arquivo (.pdf, .md, .txt)
                  </button>
                </div>
              ) : null}
              <input
                ref={anexosProjetoEmBranco.refInputImagem as React.Ref<HTMLInputElement>}
                type="file"
                accept="image/png,image/jpeg,image/webp,image/gif"
                className="tb-fab-anexos-input-file"
                aria-hidden
                tabIndex={-1}
                onChange={(evento) => {
                  const arquivo = evento.target.files?.[0];
                  evento.target.value = "";
                  if (arquivo) anexosProjetoEmBranco.aoSelecionarImagem(arquivo);
                }}
              />
              <input
                ref={anexosProjetoEmBranco.refInputDocumento as React.Ref<HTMLInputElement>}
                type="file"
                multiple
                accept=".md,.txt,.pdf,text/plain,text/markdown,application/pdf"
                className="tb-fab-anexos-input-file"
                aria-hidden
                tabIndex={-1}
                onChange={(evento) => {
                  const lista = Array.from(evento.target.files ?? []);
                  evento.target.value = "";
                  if (lista.length > 0) anexosProjetoEmBranco.aoSelecionarDocumentos(lista);
                }}
              />
            </div>
          ) : (
            <button
              type="button"
              className="tb-fab-mais-btn"
              aria-label="Anexar frame do vídeo no instante atual do player"
              disabled={anexarFrameDesabilitado || !aoAnexarFrameDoPlayer}
              title={tituloBotaoMaisFrame}
              onClick={() => aoAnexarFrameDoPlayer?.()}
            >
              <IconeMaisComposerChatAskAgenteTranscribrothers />
            </button>
          )}
          <textarea
            ref={refTextarea as React.Ref<HTMLTextAreaElement>}
            id="tb-fab-instrucoes"
            className="tb-input tb-fab-chat-textarea tb-chat-ask-agente-textarea"
            rows={1}
            value={textoInstrucoes}
            disabled={composerTravado}
            onChange={(evento) => aoMudarTexto(evento.target.value)}
            onKeyDown={(evento) => {
              if (evento.key !== "Enter" || evento.shiftKey) return;
              evento.preventDefault();
              if (enviarBloqueado) return;
              aoEnviar();
            }}
            placeholder={placeholder}
          />
          <button
            type="button"
            className={[
              "tb-chat-ask-agente-enviar-seta",
              enviarBloqueado ? "" : "tb-chat-ask-agente-enviar-seta--ativo",
            ]
              .filter(Boolean)
              .join(" ")}
            disabled={enviarBloqueado}
            aria-label={modo === "ask" ? "Enviar" : rotuloBotaoEnviar}
            title={
              modo === "ask" && !askDisponivel
                ? "Ask ainda não está disponível nesta versão."
                : modo === "ask"
                  ? "Enviar"
                  : rotuloBotaoEnviar
            }
            onClick={() => {
              if (modo === "ask" && (!askDisponivel || enviandoMensagemAsk || !textoInstrucoes.trim())) return;
              aoEnviar();
            }}
          >
            <IconeEnviarComposerChatAskAgenteTranscribrothers />
          </button>
        </div>
      </div>
    </aside>
  );
}
