import { describe, expect, it } from "vitest";
import {
  citacaoChatAskDeveAparecerComoChipTranscribrothers,
  instanteSegundosParaSeekCitacaoChatAskTranscribrothers,
  segundosDeHrefTimestampTutorialOuChatTranscribrothers,
  itensHistoricoChatAskAgenteOcultandoGerandoSubstituidoPorPreviewProntaTranscribrothers,
  mensagensPainelAPartirDoHistoricoChatAskAgenteDocumentoJobTranscribrothers,
  mesclarCaminhosImagensPropostaChatAgenteDocumentoTranscribrothers,
  normalizarItemHistoricoChatAskAgenteDocumentoJobTranscribrothers,
  normalizarPropostaFerramentaChatAgenteDocumentoJobTranscribrothers,
  propostaFerramentaChatAgenteDeveMostrarBotaoAplicarNaBolhaTranscribrothers,
  resolverPropostasEdicaoParcialParaAplicarChatAgenteTranscribrothers,
  modoAplicacaoLoteEdicaoParcialChatAgenteTranscribrothers,
  turnoAgenteGerandoDevePersistirEstadoFalhouSemPreviaTranscribrothers,
  type ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers,
} from "./modulo_tipos_item_historico_chat_ask_agente_documento_job_transcribrothers.ts";

function item(
  parcial: Partial<ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers> &
    Pick<ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers, "papel" | "texto" | "criado_em">,
): ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers {
  return {
    modo: parcial.papel === "agente" ? "agente" : "ask",
    citacoes: [],
    imagens: [],
    estado: null,
    tipo_pipeline: null,
    proposta_ferramenta: null,
    propostas_ferramenta: [],
    executar_proposta: false,
    ...parcial,
  };
}

describe("histórico do painel Ask/Agente", () => {
  it("esconde o turno agente gerando quando a prévia do mesmo texto já foi gravada", () => {
    const visiveis = itensHistoricoChatAskAgenteOcultandoGerandoSubstituidoPorPreviewProntaTranscribrothers([
      item({ papel: "usuario", texto: "tom mais formal", criado_em: "t0" }),
      item({
        papel: "agente",
        texto: "tom mais formal",
        criado_em: "t1",
        estado: "gerando",
        tipo_pipeline: "tutorial",
      }),
      item({
        papel: "agente",
        texto: "tom mais formal",
        criado_em: "t2",
        estado: "preview_pronta",
        tipo_pipeline: "tutorial",
      }),
    ]);
    expect(visiveis.map((entrada) => entrada.estado)).toEqual([null, "preview_pronta"]);
    const mensagens = mensagensPainelAPartirDoHistoricoChatAskAgenteDocumentoJobTranscribrothers([
      item({ papel: "usuario", texto: "tom mais formal", criado_em: "t0" }),
      item({
        papel: "agente",
        texto: "tom mais formal",
        criado_em: "t1",
        estado: "gerando",
        tipo_pipeline: "tutorial",
      }),
      item({
        papel: "agente",
        texto: "tom mais formal",
        criado_em: "t2",
        estado: "preview_pronta",
        tipo_pipeline: "secao",
      }),
    ]);
    expect(mensagens).toHaveLength(2);
    expect(mensagens[1]?.estado).toBe("preview_pronta");
    expect(mensagens[1]?.tipo_pipeline).toBe("secao");
  });

  it("esconde a fala do agente copiada na prévia pronta e mantém o pedido do usuário", () => {
    const visiveis = itensHistoricoChatAskAgenteOcultandoGerandoSubstituidoPorPreviewProntaTranscribrothers([
      item({ papel: "usuario", texto: "pode aplicar", criado_em: "t0" }),
      item({
        papel: "agente",
        texto: "Confirmado. Vou aplicar agora.",
        criado_em: "t1",
      }),
      item({
        papel: "agente",
        texto: "Confirmado. Vou aplicar agora.",
        criado_em: "t2",
        estado: "preview_pronta",
      }),
    ]);
    expect(visiveis.map((entrada) => `${entrada.papel}:${entrada.estado ?? ""}`)).toEqual([
      "usuario:",
      "agente:preview_pronta",
    ]);
    expect(visiveis[0]?.texto).toBe("pode aplicar");
  });

  it("não esconde falas iguais de turnos anteriores quando houve outro pedido no meio", () => {
    const visiveis = itensHistoricoChatAskAgenteOcultandoGerandoSubstituidoPorPreviewProntaTranscribrothers([
      item({ papel: "usuario", texto: "pode aplicar", criado_em: "t0" }),
      item({ papel: "agente", texto: "Confirmado. Vou aplicar agora.", criado_em: "t1" }),
      item({ papel: "usuario", texto: "pode aplicar", criado_em: "t2" }),
      item({ papel: "agente", texto: "Confirmado. Vou aplicar agora.", criado_em: "t3" }),
      item({
        papel: "agente",
        texto: "Confirmado. Vou aplicar agora.",
        criado_em: "t4",
        estado: "preview_pronta",
      }),
    ]);
    expect(visiveis.map((entrada) => entrada.papel)).toEqual([
      "usuario",
      "agente",
      "usuario",
      "agente",
    ]);
    expect(visiveis[3]?.estado).toBe("preview_pronta");
  });

  it("esconde o turno gerando quando o mesmo texto já foi marcado como falhou", () => {
    const visiveis = itensHistoricoChatAskAgenteOcultandoGerandoSubstituidoPorPreviewProntaTranscribrothers([
      item({ papel: "usuario", texto: "tom mais formal", criado_em: "t0" }),
      item({
        papel: "agente",
        texto: "tom mais formal",
        criado_em: "t1",
        estado: "gerando",
        tipo_pipeline: "tutorial",
      }),
      item({
        papel: "agente",
        texto: "tom mais formal",
        criado_em: "t2",
        estado: "falhou",
        tipo_pipeline: "tutorial",
      }),
    ]);
    expect(visiveis.map((entrada) => entrada.estado)).toEqual([null, "falhou"]);
  });

  it("pede falhou só quando o job terminou sem prévia e o último agente ainda gera", () => {
    expect(
      turnoAgenteGerandoDevePersistirEstadoFalhouSemPreviaTranscribrothers({
        statusJob: "failed",
        temObjetoPreview: false,
        estadoUltimoTurnoAgente: "gerando",
      }),
    ).toBe(true);
    expect(
      turnoAgenteGerandoDevePersistirEstadoFalhouSemPreviaTranscribrothers({
        statusJob: "completed",
        temObjetoPreview: false,
        estadoUltimoTurnoAgente: "gerando",
      }),
    ).toBe(true);
    expect(
      turnoAgenteGerandoDevePersistirEstadoFalhouSemPreviaTranscribrothers({
        statusJob: "completed",
        temObjetoPreview: true,
        estadoUltimoTurnoAgente: "gerando",
      }),
    ).toBe(false);
    expect(
      turnoAgenteGerandoDevePersistirEstadoFalhouSemPreviaTranscribrothers({
        statusJob: "generating_tutorial",
        temObjetoPreview: false,
        estadoUltimoTurnoAgente: "gerando",
      }),
    ).toBe(false);
    expect(
      turnoAgenteGerandoDevePersistirEstadoFalhouSemPreviaTranscribrothers({
        statusJob: "failed",
        temObjetoPreview: false,
        estadoUltimoTurnoAgente: "falhou",
      }),
    ).toBe(false);
  });

  it("normaliza caminhos_imagens da proposta e mescla sem repetir", () => {
    const proposta = normalizarPropostaFerramentaChatAgenteDocumentoJobTranscribrothers({
      nome: "edicao_parcial",
      titulo_secao_heading: "O que foi discutido",
      instrucoes: "aprofunda Assistido Digital",
      caminhos_imagens: ["assets/tela_chat_758.png", "assets/tela_chat_758.png", 12],
    });
    expect(proposta?.caminhos_imagens).toEqual(["assets/tela_chat_758.png"]);
    expect(
      mesclarCaminhosImagensPropostaChatAgenteDocumentoTranscribrothers(
        proposta?.caminhos_imagens,
        ["assets/outra.png", "assets/tela_chat_758.png"],
      ),
    ).toEqual(["assets/tela_chat_758.png", "assets/outra.png"]);
  });

  it("resolve o lote de edicao_parcial em vez de só a primeira proposta", () => {
    const primeira = {
      nome: "edicao_parcial",
      titulo_secao_heading: "Contexto e problema",
      instrucoes: "um",
      caminhos_imagens: [],
    };
    const lote = resolverPropostasEdicaoParcialParaAplicarChatAgenteTranscribrothers(primeira, [
      primeira,
      {
        nome: "edicao_parcial",
        titulo_secao_heading: "Dúvidas em aberto",
        instrucoes: "dois",
        caminhos_imagens: [],
      },
    ]);
    expect(lote).toHaveLength(2);
    expect(lote[1]?.titulo_secao_heading).toBe("Dúvidas em aberto");
  });

  it("reescreve seção ou documento quando o lote tira timestamp ou pede legenda", () => {
    const cirurgica = {
      nome: "edicao_parcial",
      titulo_secao_heading: "Contexto e problema",
      instrucoes: "Adicionar ao final da lista: '**Filtros:** etiqueta.'",
      caminhos_imagens: [] as string[],
    };
    const reescrita = {
      nome: "edicao_parcial",
      titulo_secao_heading: "1. Visão Geral e Triagem Manual",
      instrucoes:
        "Remover os links de tempo '[00:47](?t=47)' do texto corrido. Adicionar uma legenda curta abaixo de cada imagem.",
      caminhos_imagens: [] as string[],
    };
    expect(modoAplicacaoLoteEdicaoParcialChatAgenteTranscribrothers([cirurgica])).toBe("cirurgico");
    expect(modoAplicacaoLoteEdicaoParcialChatAgenteTranscribrothers([reescrita])).toBe("reescrever_secao");
    expect(
      modoAplicacaoLoteEdicaoParcialChatAgenteTranscribrothers([
        reescrita,
        { ...reescrita, titulo_secao_heading: "2. Triagem Automatizada com IA" },
      ]),
    ).toBe("reescrever_documento");
  });
});

describe("chips de citação na bolha", () => {
  it("no rodapé só cai tempo sem link no texto; heading e trecho solto somem", () => {
    expect(
      citacaoChatAskDeveAparecerComoChipTranscribrothers({
        tipo: "transcricao",
        rotulo: "12:40",
        instante_segundos: 760,
        heading: null,
      }),
    ).toBe(true);
    expect(
      citacaoChatAskDeveAparecerComoChipTranscribrothers(
        {
          tipo: "transcricao",
          rotulo: "12:40",
          instante_segundos: 760,
          heading: null,
        },
        "Filtros por etiquetas [12:40](?t=760)",
      ),
    ).toBe(false);
    expect(
      citacaoChatAskDeveAparecerComoChipTranscribrothers({
        tipo: "markdown",
        rotulo: "Prompt de intimação",
        instante_segundos: null,
        heading: "Prompt de intimação",
      }),
    ).toBe(false);
    expect(
      citacaoChatAskDeveAparecerComoChipTranscribrothers({
        tipo: "markdown",
        rotulo: "Ele não precisa ficar nisso aí",
        instante_segundos: null,
        heading: null,
      }),
    ).toBe(false);
    expect(
      citacaoChatAskDeveAparecerComoChipTranscribrothers({
        tipo: "transcricao",
        rotulo: "Ele não precisa ficar nisso aí",
        instante_segundos: null,
        heading: null,
      }),
    ).toBe(false);
  });

  it("lê segundos de um atalho ?t= do Markdown", () => {
    expect(segundosDeHrefTimestampTutorialOuChatTranscribrothers("?t=760")).toBe(760);
    expect(segundosDeHrefTimestampTutorialOuChatTranscribrothers("?t=12.5")).toBe(12.5);
    expect(segundosDeHrefTimestampTutorialOuChatTranscribrothers("https://exemplo")).toBeNull();
  });

  it("extrai segundos para seek no vídeo a partir do instante ou do rótulo", () => {
    expect(
      instanteSegundosParaSeekCitacaoChatAskTranscribrothers({
        tipo: "transcricao",
        rotulo: "12:40",
        instante_segundos: 760,
        heading: null,
      }),
    ).toBe(760);
    expect(
      instanteSegundosParaSeekCitacaoChatAskTranscribrothers({
        tipo: "transcricao",
        rotulo: "1:02:03",
        instante_segundos: null,
        heading: null,
      }),
    ).toBe(3723);
    expect(
      instanteSegundosParaSeekCitacaoChatAskTranscribrothers({
        tipo: "markdown",
        rotulo: "Fluxo",
        instante_segundos: null,
        heading: "Fluxo",
      }),
    ).toBeNull();
  });
});

describe("botão de proposta na bolha", () => {
  it("esconde o aplicar quando a proposta já foi executada", () => {
    expect(
      propostaFerramentaChatAgenteDeveMostrarBotaoAplicarNaBolhaTranscribrothers({
        temProposta: true,
        executarProposta: false,
        estado: null,
        nomeFerramenta: "revisao_profunda",
      }),
    ).toBe(true);
    expect(
      propostaFerramentaChatAgenteDeveMostrarBotaoAplicarNaBolhaTranscribrothers({
        temProposta: true,
        executarProposta: true,
        estado: null,
        nomeFerramenta: "revisao_profunda",
      }),
    ).toBe(false);
    expect(
      propostaFerramentaChatAgenteDeveMostrarBotaoAplicarNaBolhaTranscribrothers({
        temProposta: true,
        executarProposta: false,
        estado: "preview_pronta",
        nomeFerramenta: "revisao_profunda",
      }),
    ).toBe(false);
    expect(
      propostaFerramentaChatAgenteDeveMostrarBotaoAplicarNaBolhaTranscribrothers({
        temProposta: true,
        executarProposta: false,
        estado: null,
        nomeFerramenta: "edicao_parcial",
        ehUltimaMensagemAgente: true,
      }),
    ).toBe(true);
    expect(
      propostaFerramentaChatAgenteDeveMostrarBotaoAplicarNaBolhaTranscribrothers({
        temProposta: true,
        executarProposta: false,
        estado: null,
        nomeFerramenta: "edicao_parcial",
        ehUltimaMensagemAgente: false,
      }),
    ).toBe(false);
  });

  it("lê executar_proposta do histórico persistido", () => {
    const item = normalizarItemHistoricoChatAskAgenteDocumentoJobTranscribrothers({
      papel: "agente",
      modo: "agente",
      texto: "Apliquei.",
      criado_em: "t1",
      citacoes: [],
      imagens: [],
      proposta_ferramenta: { nome: "edicao_parcial" },
      executar_proposta: true,
    });
    expect(item?.executar_proposta).toBe(true);
    const mensagens = mensagensPainelAPartirDoHistoricoChatAskAgenteDocumentoJobTranscribrothers([
      item!,
    ]);
    expect(mensagens[0]?.executar_proposta).toBe(true);
  });
});
