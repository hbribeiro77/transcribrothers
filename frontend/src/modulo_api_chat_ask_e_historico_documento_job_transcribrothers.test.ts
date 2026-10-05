import { afterEach, describe, expect, it, vi } from "vitest";
import {
  anexarItemHistoricoChatAskAgenteDocumentoJobApiTranscribrothers,
  buscarHistoricoChatAskAgenteDocumentoJobApiTranscribrothers,
  enviarMensagemChatAgenteDocumentoJobApiTranscribrothers,
  enviarMensagemChatAskDocumentoJobApiEmStreamTranscribrothers,
  enviarMensagemChatAskDocumentoJobApiTranscribrothers,
  limparHistoricoChatAskAgenteDocumentoJobApiTranscribrothers,
} from "./modulo_api_chat_ask_e_historico_documento_job_transcribrothers.ts";

function respostaOk(corpo: unknown) {
  return {
    ok: true,
    status: 200,
    json: async () => corpo,
    text: async () => JSON.stringify(corpo),
  };
}

describe("API chat Ask e histórico do documento", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("DELETE chat-historico esvazia e devolve lista vazia", async () => {
    const fetchMock = vi.fn(async () => respostaOk({ historico: [] }));
    vi.stubGlobal("fetch", fetchMock);
    const itens = await limparHistoricoChatAskAgenteDocumentoJobApiTranscribrothers("job-1");
    expect(fetchMock).toHaveBeenCalledWith("/api/jobs/job-1/chat-historico", {
      method: "DELETE",
    });
    expect(itens).toEqual([]);
  });

  it("GET chat-historico devolve os itens", async () => {
    const fetchMock = vi.fn(async () =>
      respostaOk({
        historico: [
          {
            papel: "usuario",
            modo: "ask",
            texto: "oi",
            criado_em: "2026-10-03T00:00:00Z",
            citacoes: [],
            imagens: [],
            estado: null,
            tipo_pipeline: null,
          },
        ],
      }),
    );
    vi.stubGlobal("fetch", fetchMock);
    const itens = await buscarHistoricoChatAskAgenteDocumentoJobApiTranscribrothers("job-1");
    expect(fetchMock).toHaveBeenCalledWith("/api/jobs/job-1/chat-historico");
    expect(itens).toHaveLength(1);
    expect(itens[0]?.texto).toBe("oi");
  });

  it("POST chat-historico anexa o item e devolve o histórico", async () => {
    const fetchMock = vi.fn(async () =>
      respostaOk({
        historico: [
          {
            papel: "agente",
            modo: "agente",
            texto: "tom mais formal",
            criado_em: "2026-10-03T00:00:02Z",
            citacoes: [],
            imagens: [],
            estado: "gerando",
            tipo_pipeline: "tutorial",
          },
        ],
      }),
    );
    vi.stubGlobal("fetch", fetchMock);
    const itens = await anexarItemHistoricoChatAskAgenteDocumentoJobApiTranscribrothers("job-1", {
      papel: "agente",
      modo: "agente",
      texto: "tom mais formal",
      estado: "gerando",
      tipo_pipeline: "tutorial",
    });
    expect(fetchMock).toHaveBeenCalledWith("/api/jobs/job-1/chat-historico", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        papel: "agente",
        modo: "agente",
        texto: "tom mais formal",
        estado: "gerando",
        tipo_pipeline: "tutorial",
      }),
    });
    expect(itens).toHaveLength(1);
    expect(itens[0]?.estado).toBe("gerando");
    expect(itens[0]?.tipo_pipeline).toBe("tutorial");
  });

  it("POST chat-ask envia só a mensagem e devolve texto, citações e histórico", async () => {
    const fetchMock = vi.fn(async () =>
      respostaOk({
        texto: "resposta",
        citacoes: [{ tipo: "markdown", rotulo: "Fluxo", instante_segundos: null, heading: "Fluxo" }],
        imagens: [],
        historico: [
          {
            papel: "assistente",
            modo: "ask",
            texto: "resposta",
            criado_em: "2026-10-03T00:00:01Z",
            citacoes: [{ tipo: "markdown", rotulo: "Fluxo", instante_segundos: null, heading: "Fluxo" }],
            imagens: [],
            estado: null,
            tipo_pipeline: null,
          },
        ],
      }),
    );
    vi.stubGlobal("fetch", fetchMock);
    const r = await enviarMensagemChatAskDocumentoJobApiTranscribrothers("abc", "qual a jornada?");
    expect(fetchMock).toHaveBeenCalledWith("/api/jobs/abc/chat-ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mensagem: "qual a jornada?" }),
    });
    expect(r.texto).toBe("resposta");
    expect(r.citacoes[0]?.heading).toBe("Fluxo");
    expect(r.historico).toHaveLength(1);
    expect(r.imagens).toEqual([]);
  });

  it("POST chat-ask envia o modelo do chat quando informado", async () => {
    const fetchMock = vi.fn(async () =>
      respostaOk({
        texto: "ok",
        citacoes: [],
        imagens: [],
        historico: [],
      }),
    );
    vi.stubGlobal("fetch", fetchMock);
    await enviarMensagemChatAskDocumentoJobApiTranscribrothers(
      "abc",
      "oi",
      null,
      "gemini/gemini-2.5-flash",
    );
    expect(fetchMock).toHaveBeenCalledWith("/api/jobs/abc/chat-ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mensagem: "oi",
        litellm_model: "gemini/gemini-2.5-flash",
      }),
    });
  });

  it("POST chat-agente envia mensagem e forcar_ferramenta", async () => {
    const fetchMock = vi.fn(async () =>
      respostaOk({
        texto: "Sugiro a Visão Geral",
        citacoes: [],
        imagens: [],
        proposta_ferramenta: {
          nome: "edicao_parcial",
          titulo_secao_heading: "Visão Geral",
          instrucoes: "inclua o parágrafo",
        },
        executar_proposta: false,
        historico: [],
      }),
    );
    vi.stubGlobal("fetch", fetchMock);
    const r = await enviarMensagemChatAgenteDocumentoJobApiTranscribrothers(
      "abc",
      "bola um texto",
      null,
      "gemini/gemini-2.5-flash",
      "edicao_parcial",
    );
    expect(fetchMock).toHaveBeenCalledWith("/api/jobs/abc/chat-agente", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mensagem: "bola um texto",
        litellm_model: "gemini/gemini-2.5-flash",
        forcar_ferramenta: "edicao_parcial",
      }),
    });
    expect(r.proposta_ferramenta?.nome).toBe("edicao_parcial");
  });

  it("lança com o texto da resposta quando o HTTP não é ok", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => ({
        ok: false,
        status: 409,
        text: async () => "Não há Markdown nem transcrição neste job para o Ask.",
        json: async () => ({}),
      })),
    );
    await expect(enviarMensagemChatAskDocumentoJobApiTranscribrothers("x", "oi")).rejects.toThrow(
      "Não há Markdown nem transcrição neste job para o Ask.",
    );
  });

  it("POST chat-ask-stream aplica deltas e devolve o evento final", async () => {
    const corpoSse =
      'data: {"tipo":"delta","texto":"Olá"}\n\n' +
      'data: {"tipo":"delta","texto":"Olá **mundo**"}\n\n' +
      'data: {"tipo":"final","texto":"Olá **mundo**","citacoes":[],"imagens":[],"historico":[]}\n\n';
    const fetchMock = vi.fn(async () => ({
      ok: true,
      status: 200,
      body: new ReadableStream({
        start(controller) {
          controller.enqueue(new TextEncoder().encode(corpoSse));
          controller.close();
        },
      }),
      json: async () => ({}),
      text: async () => corpoSse,
    }));
    vi.stubGlobal("fetch", fetchMock);
    const deltas: string[] = [];
    const r = await enviarMensagemChatAskDocumentoJobApiEmStreamTranscribrothers(
      "abc",
      "oi",
      null,
      null,
      (texto) => deltas.push(texto),
    );
    expect(fetchMock).toHaveBeenCalledWith("/api/jobs/abc/chat-ask-stream", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mensagem: "oi" }),
    });
    expect(deltas).toEqual(["Olá", "Olá **mundo**"]);
    expect(r.texto).toBe("Olá **mundo**");
  });
});
