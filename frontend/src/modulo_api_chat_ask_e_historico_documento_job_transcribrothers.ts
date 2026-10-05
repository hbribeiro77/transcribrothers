import {
  normalizarCitacaoItemHistoricoChatAskDocumentoJobTranscribrothers,
  normalizarImagemItemHistoricoChatAskDocumentoJobTranscribrothers,
  normalizarListaHistoricoChatAskAgenteDocumentoJobTranscribrothers,
  normalizarListaPropostasFerramentaChatAgenteDocumentoTranscribrothers,
  normalizarPropostaFerramentaChatAgenteDocumentoJobTranscribrothers,
  type CitacaoItemHistoricoChatAskDocumentoJobTranscribrothers,
  type ImagemItemHistoricoChatAskDocumentoJobTranscribrothers,
  type ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers,
  type RespostaEnviarMensagemChatAgenteDocumentoJobApiTranscribrothers,
  type RespostaEnviarMensagemChatAskDocumentoJobApiTranscribrothers,
} from "./modulo_tipos_item_historico_chat_ask_agente_documento_job_transcribrothers.ts";
import { consumirEventosSseBufferChatAskAgenteTranscribrothers } from "./modulo_util_consumir_eventos_sse_buffer_chat_ask_agente_transcribrothers.ts";

function mensagemErroDeCorpoHttpChatAskTranscribrothers(texto: string, status: number): string {
  const cru = texto.trim();
  if (!cru) return `Erro HTTP ${status}`;
  try {
    const parsed = JSON.parse(cru) as { detail?: unknown };
    if (typeof parsed.detail === "string" && parsed.detail.trim()) return parsed.detail.trim();
  } catch {
    /* corpo em texto puro */
  }
  return cru;
}

async function garantirRespostaHttpOkChatAskTranscribrothers(r: Response): Promise<void> {
  if (r.ok) return;
  const t = await r.text();
  throw new Error(mensagemErroDeCorpoHttpChatAskTranscribrothers(t, r.status));
}

export type CorpoAnexarHistoricoChatAskAgenteDocumentoJobTranscribrothers = {
  papel: string;
  modo: string;
  texto: string;
  estado?: string | null;
  tipo_pipeline?: string | null;
};

export async function buscarHistoricoChatAskAgenteDocumentoJobApiTranscribrothers(
  jobId: string,
): Promise<ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers[]> {
  const r = await fetch(`/api/jobs/${encodeURIComponent(jobId)}/chat-historico`);
  await garantirRespostaHttpOkChatAskTranscribrothers(r);
  const data = (await r.json()) as { historico?: unknown };
  return normalizarListaHistoricoChatAskAgenteDocumentoJobTranscribrothers(data.historico);
}

export async function anexarItemHistoricoChatAskAgenteDocumentoJobApiTranscribrothers(
  jobId: string,
  item: CorpoAnexarHistoricoChatAskAgenteDocumentoJobTranscribrothers,
): Promise<ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers[]> {
  const r = await fetch(`/api/jobs/${encodeURIComponent(jobId)}/chat-historico`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      papel: item.papel,
      modo: item.modo,
      texto: item.texto,
      estado: item.estado ?? null,
      tipo_pipeline: item.tipo_pipeline ?? null,
    }),
  });
  await garantirRespostaHttpOkChatAskTranscribrothers(r);
  const data = (await r.json()) as { historico?: unknown };
  return normalizarListaHistoricoChatAskAgenteDocumentoJobTranscribrothers(data.historico);
}

export async function limparHistoricoChatAskAgenteDocumentoJobApiTranscribrothers(
  jobId: string,
): Promise<ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers[]> {
  const r = await fetch(`/api/jobs/${encodeURIComponent(jobId)}/chat-historico`, {
    method: "DELETE",
  });
  await garantirRespostaHttpOkChatAskTranscribrothers(r);
  const data = (await r.json()) as { historico?: unknown };
  return normalizarListaHistoricoChatAskAgenteDocumentoJobTranscribrothers(data.historico);
}

export type RespostaResolverFrameChatAskDocumentoJobApiTranscribrothers = {
  caminho_relativo: string;
  url: string;
  instante_segundos: number;
  origem: string;
};

export async function resolverFrameChatAskDocumentoJobApiTranscribrothers(
  jobId: string,
  instanteSegundos: number,
): Promise<RespostaResolverFrameChatAskDocumentoJobApiTranscribrothers> {
  const r = await fetch(`/api/jobs/${encodeURIComponent(jobId)}/chat-ask-resolver-frame`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ instante_segundos: instanteSegundos }),
  });
  await garantirRespostaHttpOkChatAskTranscribrothers(r);
  const data = (await r.json()) as {
    caminho_relativo?: unknown;
    url?: unknown;
    instante_segundos?: unknown;
    origem?: unknown;
  };
  return {
    caminho_relativo: typeof data.caminho_relativo === "string" ? data.caminho_relativo : "",
    url: typeof data.url === "string" ? data.url : "",
    instante_segundos: typeof data.instante_segundos === "number" ? data.instante_segundos : 0,
    origem: typeof data.origem === "string" ? data.origem : "",
  };
}

export async function enviarMensagemChatAskDocumentoJobApiTranscribrothers(
  jobId: string,
  mensagem: string,
  instanteAnexoSegundos?: number | null,
  litellmModel?: string | null,
): Promise<RespostaEnviarMensagemChatAskDocumentoJobApiTranscribrothers> {
  const corpo: { mensagem: string; instante_anexo_segundos?: number; litellm_model?: string } = {
    mensagem,
  };
  if (instanteAnexoSegundos != null && Number.isFinite(instanteAnexoSegundos)) {
    corpo.instante_anexo_segundos = instanteAnexoSegundos;
  }
  const modelo = (litellmModel || "").trim();
  if (modelo) {
    corpo.litellm_model = modelo;
  }
  const r = await fetch(`/api/jobs/${encodeURIComponent(jobId)}/chat-ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(corpo),
  });
  await garantirRespostaHttpOkChatAskTranscribrothers(r);
  const data = (await r.json()) as {
    texto?: unknown;
    citacoes?: unknown;
    imagens?: unknown;
    historico?: unknown;
  };
  return {
    texto: typeof data.texto === "string" ? data.texto : "",
    citacoes: normalizarListaCitacoesRespostaChatAskTranscribrothers(data.citacoes),
    imagens: normalizarListaImagensRespostaChatAskTranscribrothers(data.imagens),
    historico: normalizarListaHistoricoChatAskAgenteDocumentoJobTranscribrothers(data.historico),
  };
}

function normalizarListaCitacoesRespostaChatAskTranscribrothers(
  raw: unknown,
): CitacaoItemHistoricoChatAskDocumentoJobTranscribrothers[] {
  if (!Array.isArray(raw)) return [];
  return raw
    .map(normalizarCitacaoItemHistoricoChatAskDocumentoJobTranscribrothers)
    .filter((c): c is CitacaoItemHistoricoChatAskDocumentoJobTranscribrothers => c != null);
}

export async function enviarMensagemChatAgenteDocumentoJobApiTranscribrothers(
  jobId: string,
  mensagem: string,
  instanteAnexoSegundos?: number | null,
  litellmModel?: string | null,
  forcarFerramenta?: string | null,
): Promise<RespostaEnviarMensagemChatAgenteDocumentoJobApiTranscribrothers> {
  const corpo: {
    mensagem: string;
    instante_anexo_segundos?: number;
    litellm_model?: string;
    forcar_ferramenta?: string;
  } = {
    mensagem,
  };
  if (instanteAnexoSegundos != null && Number.isFinite(instanteAnexoSegundos)) {
    corpo.instante_anexo_segundos = instanteAnexoSegundos;
  }
  const modelo = (litellmModel || "").trim();
  if (modelo) {
    corpo.litellm_model = modelo;
  }
  const forcar = (forcarFerramenta || "").trim();
  if (forcar) {
    corpo.forcar_ferramenta = forcar;
  }
  const r = await fetch(`/api/jobs/${encodeURIComponent(jobId)}/chat-agente`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(corpo),
  });
  await garantirRespostaHttpOkChatAskTranscribrothers(r);
  const data = (await r.json()) as {
    texto?: unknown;
    citacoes?: unknown;
    imagens?: unknown;
    proposta_ferramenta?: unknown;
    propostas_ferramenta?: unknown;
    executar_proposta?: unknown;
    historico?: unknown;
  };
  return {
    texto: typeof data.texto === "string" ? data.texto : "",
    citacoes: normalizarListaCitacoesRespostaChatAskTranscribrothers(data.citacoes),
    imagens: normalizarListaImagensRespostaChatAskTranscribrothers(data.imagens),
    proposta_ferramenta: normalizarPropostaFerramentaChatAgenteDocumentoJobTranscribrothers(
      data.proposta_ferramenta,
    ),
    propostas_ferramenta: normalizarListaPropostasFerramentaChatAgenteDocumentoTranscribrothers(
      data.propostas_ferramenta,
    ),
    executar_proposta: data.executar_proposta === true,
    historico: normalizarListaHistoricoChatAskAgenteDocumentoJobTranscribrothers(data.historico),
  };
}

async function lerEventoFinalSseChatAskAgenteTranscribrothers(
  r: Response,
  aoDeltaTexto: (texto: string) => void,
): Promise<Record<string, unknown>> {
  await garantirRespostaHttpOkChatAskTranscribrothers(r);
  if (!r.body) {
    throw new Error("O stream do chat veio sem corpo.");
  }
  const leitor = r.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let final: Record<string, unknown> | null = null;
  while (true) {
    const { done, value } = await leitor.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const { eventos, resto } = consumirEventosSseBufferChatAskAgenteTranscribrothers(buffer);
    buffer = resto;
    for (const evento of eventos) {
      if (evento.tipo === "delta" && typeof evento.texto === "string") {
        aoDeltaTexto(evento.texto);
      } else if (evento.tipo === "erro") {
        const msg =
          typeof evento.mensagem === "string" && evento.mensagem.trim()
            ? evento.mensagem.trim()
            : "Erro no stream do chat.";
        throw new Error(msg);
      } else if (evento.tipo === "final") {
        final = evento;
      }
    }
  }
  if (!final) {
    throw new Error("O stream do chat encerrou sem resposta final.");
  }
  return final;
}

function montarCorpoPostChatAskAgenteTranscribrothers(
  mensagem: string,
  instanteAnexoSegundos?: number | null,
  litellmModel?: string | null,
  forcarFerramenta?: string | null,
): Record<string, string | number> {
  const corpo: Record<string, string | number> = { mensagem };
  if (instanteAnexoSegundos != null && Number.isFinite(instanteAnexoSegundos)) {
    corpo.instante_anexo_segundos = instanteAnexoSegundos;
  }
  const modelo = (litellmModel || "").trim();
  if (modelo) corpo.litellm_model = modelo;
  const forcar = (forcarFerramenta || "").trim();
  if (forcar) corpo.forcar_ferramenta = forcar;
  return corpo;
}

export async function enviarMensagemChatAskDocumentoJobApiEmStreamTranscribrothers(
  jobId: string,
  mensagem: string,
  instanteAnexoSegundos: number | null | undefined,
  litellmModel: string | null | undefined,
  aoDeltaTexto: (texto: string) => void,
): Promise<RespostaEnviarMensagemChatAskDocumentoJobApiTranscribrothers> {
  const r = await fetch(`/api/jobs/${encodeURIComponent(jobId)}/chat-ask-stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(
      montarCorpoPostChatAskAgenteTranscribrothers(mensagem, instanteAnexoSegundos, litellmModel),
    ),
  });
  const data = await lerEventoFinalSseChatAskAgenteTranscribrothers(r, aoDeltaTexto);
  return {
    texto: typeof data.texto === "string" ? data.texto : "",
    citacoes: normalizarListaCitacoesRespostaChatAskTranscribrothers(data.citacoes),
    imagens: normalizarListaImagensRespostaChatAskTranscribrothers(data.imagens),
    historico: normalizarListaHistoricoChatAskAgenteDocumentoJobTranscribrothers(data.historico),
  };
}

export async function enviarMensagemChatAgenteDocumentoJobApiEmStreamTranscribrothers(
  jobId: string,
  mensagem: string,
  instanteAnexoSegundos: number | null | undefined,
  litellmModel: string | null | undefined,
  forcarFerramenta: string | null | undefined,
  aoDeltaTexto: (texto: string) => void,
): Promise<RespostaEnviarMensagemChatAgenteDocumentoJobApiTranscribrothers> {
  const r = await fetch(`/api/jobs/${encodeURIComponent(jobId)}/chat-agente-stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(
      montarCorpoPostChatAskAgenteTranscribrothers(
        mensagem,
        instanteAnexoSegundos,
        litellmModel,
        forcarFerramenta,
      ),
    ),
  });
  const data = await lerEventoFinalSseChatAskAgenteTranscribrothers(r, aoDeltaTexto);
  return {
    texto: typeof data.texto === "string" ? data.texto : "",
    citacoes: normalizarListaCitacoesRespostaChatAskTranscribrothers(data.citacoes),
    imagens: normalizarListaImagensRespostaChatAskTranscribrothers(data.imagens),
    proposta_ferramenta: normalizarPropostaFerramentaChatAgenteDocumentoJobTranscribrothers(
      data.proposta_ferramenta,
    ),
    propostas_ferramenta: normalizarListaPropostasFerramentaChatAgenteDocumentoTranscribrothers(
      data.propostas_ferramenta,
    ),
    executar_proposta: data.executar_proposta === true,
    historico: normalizarListaHistoricoChatAskAgenteDocumentoJobTranscribrothers(data.historico),
  };
}

function normalizarListaImagensRespostaChatAskTranscribrothers(
  raw: unknown,
): ImagemItemHistoricoChatAskDocumentoJobTranscribrothers[] {
  if (!Array.isArray(raw)) return [];
  return raw
    .map(normalizarImagemItemHistoricoChatAskDocumentoJobTranscribrothers)
    .filter((img): img is ImagemItemHistoricoChatAskDocumentoJobTranscribrothers => img != null);
}
