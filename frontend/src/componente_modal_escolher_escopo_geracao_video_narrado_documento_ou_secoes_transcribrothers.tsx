import { useEffect, useId, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";

import { gerarPreviewTtsAmostraVozNarracaoApiTranscribrothers } from "./modulo_api_preview_tts_amostra_voz_narracao_transcribrothers.ts";
import {
  escolherModeloTtsDaListaDisponivelTranscribrothers,
  listarModelosTtsDaListaDisponivelTranscribrothers,
  rotuloCurtoModeloTtsParaUiTranscribrothers,
} from "./modulo_api_gerar_narracao_tts_markdown_job_transcribrothers.ts";
import {
  carregarModeloTtsNarracaoPreferidoSalvoNoNavegadorTranscribrothers,
  salvarModeloTtsNarracaoPreferidoNoNavegadorTranscribrothers,
} from "./modulo_armazenamento_local_modelo_tts_narracao_preferido_navegador_transcribrothers.ts";
import {
  carregarTemperaturaTtsNarracaoPreferidaSalvaNoNavegadorTranscribrothers,
  salvarTemperaturaTtsNarracaoPreferidaNoNavegadorTranscribrothers,
} from "./modulo_armazenamento_local_temperatura_tts_narracao_preferido_navegador_transcribrothers.ts";
import {
  carregarRitmoTtsNarracaoPreferidoSalvoNoNavegadorTranscribrothers,
  salvarRitmoTtsNarracaoPreferidoNoNavegadorTranscribrothers,
} from "./modulo_armazenamento_local_ritmo_tts_narracao_preferido_navegador_transcribrothers.ts";
import {
  carregarDiretrizConteudoLegendasPreferidaSalvaNoNavegadorTranscribrothers,
  salvarDiretrizConteudoLegendasPreferidaNoNavegadorTranscribrothers,
} from "./modulo_armazenamento_local_diretriz_conteudo_legendas_preferida_navegador_transcribrothers.ts";
import {
  filtrarMarkdownPorIdsEscopoSecoesVideoNarradoTranscribrothers,
  listarOpcoesEscopoSecoesVideoNarradoAPartirMarkdownTranscribrothers,
  type OpcaoEscopoSecaoVideoNarradoTranscribrothers,
} from "./modulo_util_filtrar_markdown_por_secoes_heading_nivel2_selecionadas_transcribrothers.ts";
import { ComponenteControleSliderTemperaturaTtsNarracaoComAjudaTranscribrothers } from "./componente_controle_slider_temperatura_tts_narracao_com_ajuda_transcribrothers.tsx";
import {
  DIRETRIZ_CONTEUDO_LEGENDAS_PADRAO_TRANSCRIBROTHERS,
  listarOpcoesDiretrizConteudoLegendasParaUiTranscribrothers,
  normalizarDiretrizConteudoLegendasTranscribrothers,
  type DiretrizConteudoLegendasTranscribrothers,
} from "./modulo_diretriz_conteudo_legendas_narracao_transcribrothers.ts";
import {
  PARALELISMO_TTS_CUES_EXPERIMENTAL_PADRAO_TRANSCRIBROTHERS,
  PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
  RITMO_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
  TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
  listarOpcoesParalelismoTtsCuesExperimentalParaUiTranscribrothers,
  listarOpcoesPerfilTtsNarracaoParaUiTranscribrothers,
  listarOpcoesRitmoTtsNarracaoParaUiTranscribrothers,
  normalizarParalelismoTtsCuesExperimentalTranscribrothers,
  normalizarPerfilTtsNarracaoTranscribrothers,
  normalizarRitmoTtsNarracaoTranscribrothers,
  normalizarTemperaturaTtsNarracaoTranscribrothers,
  type PerfilTtsNarracaoTranscribrothers,
  type RitmoTtsNarracaoTranscribrothers,
} from "./modulo_perfil_motor_sintese_tts_narracao_transcribrothers.ts";

export type OpcaoVozTtsNarracaoUiTranscribrothers = {
  id: string;
  estilo: string;
};

export type ResultadoEscopoGeracaoVideoNarradoTranscribrothers = {
  modo: "documento_inteiro" | "secoes";
  markdownNarracao: string | null;
  titulosSecoes: string[];
  voz: string;
  perfilTts: PerfilTtsNarracaoTranscribrothers;
  /** Cues TTS em paralelo (1–9; padrão 3) — padrao e experimental_voz. */
  paralelismoTtsExperimental: number;
  /** Temperatura TTS (0.2–1.0, passo 0.1; padrão 0.4). */
  temperaturaTts: number;
  /** Ritmo via prompt: lento | normal | rapido | muito_rapido. */
  ritmoTts: RitmoTtsNarracaoTranscribrothers;
  /** Diretriz da limpeza IA das legendas (conservador | mais_falavel | mais_didatico). */
  diretrizConteudoLegendas: DiretrizConteudoLegendasTranscribrothers;
  /** Slug LiteLLM TTS escolhido (ex.: gemini/gemini-2.5-flash-preview-tts). */
  modeloTts: string;
};

type Props = {
  aberto: boolean;
  markdown: string;
  carregando: boolean;
  vozInicial: string;
  vozesDisponiveis: OpcaoVozTtsNarracaoUiTranscribrothers[];
  perfilTtsInicial?: string | null;
  paralelismoTtsExperimentalInicial?: number | null;
  temperaturaTtsInicial?: number | null;
  ritmoTtsInicial?: string | null;
  diretrizConteudoLegendasInicial?: string | null;
  /** Lista de modelos da UI (chat + TTS); o select filtra só os com -tts. */
  modelosLitellmDisponiveis?: string[] | null;
  litellmModelTtsInicial?: string | null;
  onFechar: () => void;
  onConfirmar: (resultado: ResultadoEscopoGeracaoVideoNarradoTranscribrothers) => void;
};

export function ComponenteModalEscolherEscopoGeracaoVideoNarradoDocumentoOuSecoesTranscribrothers({
  aberto,
  markdown,
  carregando,
  vozInicial,
  vozesDisponiveis,
  perfilTtsInicial,
  paralelismoTtsExperimentalInicial,
  temperaturaTtsInicial,
  ritmoTtsInicial,
  diretrizConteudoLegendasInicial,
  modelosLitellmDisponiveis,
  litellmModelTtsInicial,
  onFechar,
  onConfirmar,
}: Props) {
  const tituloId = useId();
  const opcoes = useMemo(
    () => listarOpcoesEscopoSecoesVideoNarradoAPartirMarkdownTranscribrothers(markdown),
    [markdown],
  );
  const opcoesPerfilTts = useMemo(
    () => listarOpcoesPerfilTtsNarracaoParaUiTranscribrothers(),
    [],
  );
  const opcoesRitmoTts = useMemo(
    () => listarOpcoesRitmoTtsNarracaoParaUiTranscribrothers(),
    [],
  );
  const opcoesDiretrizConteudo = useMemo(
    () => listarOpcoesDiretrizConteudoLegendasParaUiTranscribrothers(),
    [],
  );
  const opcoesParalelismoExperimental = useMemo(
    () => listarOpcoesParalelismoTtsCuesExperimentalParaUiTranscribrothers(),
    [],
  );
  const opcoesModeloTts = useMemo(
    () => listarModelosTtsDaListaDisponivelTranscribrothers(modelosLitellmDisponiveis || []),
    [modelosLitellmDisponiveis],
  );
  const [modo, setModo] = useState<"documento_inteiro" | "secoes">("documento_inteiro");
  const [idsSelecionados, setIdsSelecionados] = useState<Set<string>>(() => new Set());
  const [voz, setVoz] = useState(vozInicial || "Kore");
  const [perfilTts, setPerfilTts] = useState<PerfilTtsNarracaoTranscribrothers>(() =>
    normalizarPerfilTtsNarracaoTranscribrothers(
      perfilTtsInicial || PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
    ),
  );
  const [paralelismoTtsExperimental, setParalelismoTtsExperimental] = useState(() =>
    normalizarParalelismoTtsCuesExperimentalTranscribrothers(
      paralelismoTtsExperimentalInicial ?? PARALELISMO_TTS_CUES_EXPERIMENTAL_PADRAO_TRANSCRIBROTHERS,
    ),
  );
  const [temperaturaTts, setTemperaturaTts] = useState(() =>
    normalizarTemperaturaTtsNarracaoTranscribrothers(
      temperaturaTtsInicial ??
        carregarTemperaturaTtsNarracaoPreferidaSalvaNoNavegadorTranscribrothers() ??
        TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
    ),
  );
  const [ritmoTts, setRitmoTts] = useState<RitmoTtsNarracaoTranscribrothers>(() =>
    normalizarRitmoTtsNarracaoTranscribrothers(
      ritmoTtsInicial ??
        carregarRitmoTtsNarracaoPreferidoSalvoNoNavegadorTranscribrothers() ??
        RITMO_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
    ),
  );
  const [diretrizConteudoLegendas, setDiretrizConteudoLegendas] =
    useState<DiretrizConteudoLegendasTranscribrothers>(() =>
      normalizarDiretrizConteudoLegendasTranscribrothers(
        diretrizConteudoLegendasInicial ??
          carregarDiretrizConteudoLegendasPreferidaSalvaNoNavegadorTranscribrothers() ??
          DIRETRIZ_CONTEUDO_LEGENDAS_PADRAO_TRANSCRIBROTHERS,
      ),
    );
  const [modeloTts, setModeloTts] = useState(
    () =>
      escolherModeloTtsDaListaDisponivelTranscribrothers(
        modelosLitellmDisponiveis || [],
        litellmModelTtsInicial ||
          carregarModeloTtsNarracaoPreferidoSalvoNoNavegadorTranscribrothers(),
      ) || "",
  );
  const [gerandoAmostra, setGerandoAmostra] = useState(false);
  const [erroAmostra, setErroAmostra] = useState<string | null>(null);
  const audioAmostraRef = useRef<HTMLAudioElement | null>(null);
  const urlAmostraRef = useRef<string | null>(null);

  const liberarAudioAmostra = () => {
    if (audioAmostraRef.current) {
      audioAmostraRef.current.pause();
      audioAmostraRef.current = null;
    }
    if (urlAmostraRef.current) {
      URL.revokeObjectURL(urlAmostraRef.current);
      urlAmostraRef.current = null;
    }
  };

  useEffect(() => {
    if (!aberto) {
      liberarAudioAmostra();
      setGerandoAmostra(false);
      setErroAmostra(null);
      return;
    }
    setModo("documento_inteiro");
    setIdsSelecionados(new Set(opcoes.map((o) => o.id)));
    setVoz((vozInicial || "Kore").trim() || "Kore");
    setPerfilTts(
      normalizarPerfilTtsNarracaoTranscribrothers(
        perfilTtsInicial || PERFIL_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
      ),
    );
    setParalelismoTtsExperimental(
      normalizarParalelismoTtsCuesExperimentalTranscribrothers(
        paralelismoTtsExperimentalInicial ??
          PARALELISMO_TTS_CUES_EXPERIMENTAL_PADRAO_TRANSCRIBROTHERS,
      ),
    );
    setTemperaturaTts(
      normalizarTemperaturaTtsNarracaoTranscribrothers(
        temperaturaTtsInicial ??
          carregarTemperaturaTtsNarracaoPreferidaSalvaNoNavegadorTranscribrothers() ??
          TEMPERATURA_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
      ),
    );
    setRitmoTts(
      normalizarRitmoTtsNarracaoTranscribrothers(
        ritmoTtsInicial ??
          carregarRitmoTtsNarracaoPreferidoSalvoNoNavegadorTranscribrothers() ??
          RITMO_TTS_NARRACAO_PADRAO_TRANSCRIBROTHERS,
      ),
    );
    setDiretrizConteudoLegendas(
      normalizarDiretrizConteudoLegendasTranscribrothers(
        diretrizConteudoLegendasInicial ??
          carregarDiretrizConteudoLegendasPreferidaSalvaNoNavegadorTranscribrothers() ??
          DIRETRIZ_CONTEUDO_LEGENDAS_PADRAO_TRANSCRIBROTHERS,
      ),
    );
    setModeloTts(
      escolherModeloTtsDaListaDisponivelTranscribrothers(
        modelosLitellmDisponiveis || [],
        litellmModelTtsInicial ||
          carregarModeloTtsNarracaoPreferidoSalvoNoNavegadorTranscribrothers(),
      ) || "",
    );
    setErroAmostra(null);
  }, [
    aberto,
    opcoes,
    vozInicial,
    perfilTtsInicial,
    paralelismoTtsExperimentalInicial,
    temperaturaTtsInicial,
    ritmoTtsInicial,
    diretrizConteudoLegendasInicial,
    modelosLitellmDisponiveis,
    litellmModelTtsInicial,
  ]);

  useEffect(() => {
    return () => {
      liberarAudioAmostra();
    };
  }, []);

  if (!aberto) return null;

  const semSecoesH2 = opcoes.length === 0;
  const podeConfirmarSecoes = idsSelecionados.size > 0;
  const listaVozes =
    vozesDisponiveis.length > 0 ? vozesDisponiveis : [{ id: "Kore", estilo: "Firme" }];

  const fecharModal = () => {
    if (carregando || gerandoAmostra) return;
    liberarAudioAmostra();
    onFechar();
  };

  const alternarId = (id: string) => {
    setIdsSelecionados((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const selecionarTodas = (opcoesLista: OpcaoEscopoSecaoVideoNarradoTranscribrothers[]) => {
    setIdsSelecionados(new Set(opcoesLista.map((o) => o.id)));
  };

  const ouvirAmostra = async () => {
    if (carregando || gerandoAmostra) return;
    setErroAmostra(null);
    setGerandoAmostra(true);
    liberarAudioAmostra();
    try {
      const blob = await gerarPreviewTtsAmostraVozNarracaoApiTranscribrothers({
        voz,
        litellmModel: modeloTts || litellmModelTtsInicial,
        perfilTts,
        temperaturaTts: normalizarTemperaturaTtsNarracaoTranscribrothers(temperaturaTts),
        ritmoTts: normalizarRitmoTtsNarracaoTranscribrothers(ritmoTts),
      });
      const url = URL.createObjectURL(blob);
      urlAmostraRef.current = url;
      const audio = new Audio(url);
      audioAmostraRef.current = audio;
      audio.onended = () => {
        liberarAudioAmostra();
      };
      await audio.play();
    } catch (e) {
      setErroAmostra(e instanceof Error ? e.message : String(e));
    } finally {
      setGerandoAmostra(false);
    }
  };

  const confirmar = () => {
    if (gerandoAmostra) return;
    const vozEfetiva = (voz || "Kore").trim() || "Kore";
    const perfilEfetivo = normalizarPerfilTtsNarracaoTranscribrothers(perfilTts);
    const paralelismoEfetivo = normalizarParalelismoTtsCuesExperimentalTranscribrothers(
      paralelismoTtsExperimental,
    );
    const temperaturaEfetiva = normalizarTemperaturaTtsNarracaoTranscribrothers(temperaturaTts);
    const ritmoEfetivo = normalizarRitmoTtsNarracaoTranscribrothers(ritmoTts);
    const diretrizEfetiva = normalizarDiretrizConteudoLegendasTranscribrothers(
      diretrizConteudoLegendas,
    );
    const modeloTtsEfetivo =
      escolherModeloTtsDaListaDisponivelTranscribrothers(opcoesModeloTts, modeloTts) || "";
    if (!modeloTtsEfetivo) return;
    salvarModeloTtsNarracaoPreferidoNoNavegadorTranscribrothers(modeloTtsEfetivo);
    salvarTemperaturaTtsNarracaoPreferidaNoNavegadorTranscribrothers(temperaturaEfetiva);
    salvarRitmoTtsNarracaoPreferidoNoNavegadorTranscribrothers(ritmoEfetivo);
    salvarDiretrizConteudoLegendasPreferidaNoNavegadorTranscribrothers(diretrizEfetiva);
    if (modo === "documento_inteiro") {
      onConfirmar({
        modo: "documento_inteiro",
        markdownNarracao: null,
        titulosSecoes: [],
        voz: vozEfetiva,
        perfilTts: perfilEfetivo,
        paralelismoTtsExperimental: paralelismoEfetivo,
        temperaturaTts: temperaturaEfetiva,
        ritmoTts: ritmoEfetivo,
        diretrizConteudoLegendas: diretrizEfetiva,
        modeloTts: modeloTtsEfetivo,
      });
      return;
    }
    if (!podeConfirmarSecoes) return;
    const md = filtrarMarkdownPorIdsEscopoSecoesVideoNarradoTranscribrothers(
      markdown,
      idsSelecionados,
    );
    if (!md.trim()) return;
    const titulos = opcoes.filter((o) => idsSelecionados.has(o.id)).map((o) => o.titulo);
    onConfirmar({
      modo: "secoes",
      markdownNarracao: md,
      titulosSecoes: titulos,
      voz: vozEfetiva,
      perfilTts: perfilEfetivo,
      paralelismoTtsExperimental: paralelismoEfetivo,
      temperaturaTts: temperaturaEfetiva,
      ritmoTts: ritmoEfetivo,
      diretrizConteudoLegendas: diretrizEfetiva,
      modeloTts: modeloTtsEfetivo,
    });
  };

  return createPortal(
    <div className="tb-modal-job-root" role="presentation">
      <button
        type="button"
        className="tb-modal-job-backdrop"
        aria-label="Fechar"
        disabled={carregando || gerandoAmostra}
        onClick={fecharModal}
      />
      <div className="tb-modal-job-shell">
        <div className="tb-modal-job" role="dialog" aria-modal="true" aria-labelledby={tituloId}>
          <header className="tb-stepper-iniciar-transcricao-cabecalho">
            <h2 id={tituloId} className="tb-modal-job-titulo">
              Gerar vídeo narrado
            </h2>
            <p className="tb-muted tb-stepper-iniciar-transcricao-lead-modal">
              Escopo, texto das legendas, motor TTS e voz. O Markdown do job não muda.
            </p>
          </header>

          <div className="tb-stepper-iniciar-transcricao-corpo-rolavel">
            <section className="tb-stepper-iniciar-transcricao-corpo" aria-labelledby={`${tituloId}-escopo`}>
              <h3 id={`${tituloId}-escopo`} className="tb-stepper-iniciar-transcricao-etapa-titulo">
                Escopo da narração
              </h3>
              <div
                className="tb-stepper-iniciar-transcricao-opcoes-destino"
                role="radiogroup"
                aria-label="Escopo"
              >
                <label
                  className={`tb-stepper-iniciar-transcricao-opcao-destino${
                    modo === "documento_inteiro"
                      ? " tb-stepper-iniciar-transcricao-opcao-destino--selecionada"
                      : ""
                  }`}
                >
                  <input
                    type="radio"
                    name="escopo-video-narrado"
                    checked={modo === "documento_inteiro"}
                    disabled={carregando || gerandoAmostra}
                    onChange={() => setModo("documento_inteiro")}
                  />
                  <span className="tb-stepper-iniciar-transcricao-opcao-titulo">Documento inteiro</span>
                  <span className="tb-muted tb-stepper-iniciar-transcricao-opcao-desc">
                    Usa todo o Markdown atual (comportamento atual).
                  </span>
                </label>
                <label
                  className={`tb-stepper-iniciar-transcricao-opcao-destino${
                    modo === "secoes" ? " tb-stepper-iniciar-transcricao-opcao-destino--selecionada" : ""
                  }${semSecoesH2 ? " tb-stepper-iniciar-transcricao-opcao-destino--desabilitada" : ""}`}
                >
                  <input
                    type="radio"
                    name="escopo-video-narrado"
                    checked={modo === "secoes"}
                    disabled={carregando || gerandoAmostra || semSecoesH2}
                    onChange={() => setModo("secoes")}
                  />
                  <span className="tb-stepper-iniciar-transcricao-opcao-titulo">Tópicos específicos</span>
                  <span className="tb-muted tb-stepper-iniciar-transcricao-opcao-desc">
                    {semSecoesH2
                      ? "Este documento não tem seções ## para escolher."
                      : "Marque as seções que entram na narração e no MP4."}
                  </span>
                </label>
              </div>

              {modo === "secoes" && !semSecoesH2 ? (
                <div className="tb-escopo-video-narrado-lista-wrap">
                  <div className="tb-escopo-video-narrado-lista-acoes">
                    <button
                      type="button"
                      className="tb-btn-secundario"
                      disabled={carregando || gerandoAmostra}
                      onClick={() => selecionarTodas(opcoes)}
                    >
                      Marcar todas
                    </button>
                    <button
                      type="button"
                      className="tb-btn-secundario"
                      disabled={carregando || gerandoAmostra}
                      onClick={() => setIdsSelecionados(new Set())}
                    >
                      Limpar
                    </button>
                  </div>
                  <ul className="tb-escopo-video-narrado-lista" aria-label="Seções do documento">
                    {opcoes.map((o) => (
                      <li key={o.id}>
                        <label className="tb-escopo-video-narrado-check">
                          <input
                            type="checkbox"
                            checked={idsSelecionados.has(o.id)}
                            disabled={carregando || gerandoAmostra}
                            onChange={() => alternarId(o.id)}
                          />
                          <span>{o.titulo}</span>
                        </label>
                      </li>
                    ))}
                  </ul>
                </div>
              ) : null}
            </section>

            <section
              className="tb-stepper-iniciar-transcricao-corpo tb-escopo-video-narrado-secao-diretriz"
              aria-labelledby={`${tituloId}-diretriz-conteudo`}
            >
              <h3
                id={`${tituloId}-diretriz-conteudo`}
                className="tb-stepper-iniciar-transcricao-etapa-titulo"
              >
                Texto da narração / legendas
              </h3>
              <p className="tb-muted tb-escopo-video-narrado-diretriz-lead">
                Define como a IA prepara o texto das cues (mesmo texto na legenda e no TTS). Não altera
                a voz.
              </p>
              <div className="tb-escopo-video-narrado-campo">
                <label className="tb-label" htmlFor={`${tituloId}-select-diretriz-conteudo`}>
                  Diretriz de conteúdo
                </label>
                <select
                  id={`${tituloId}-select-diretriz-conteudo`}
                  className="tb-select"
                  value={diretrizConteudoLegendas}
                  disabled={carregando || gerandoAmostra}
                  onChange={(e) =>
                    setDiretrizConteudoLegendas(
                      normalizarDiretrizConteudoLegendasTranscribrothers(e.target.value),
                    )
                  }
                >
                  {opcoesDiretrizConteudo.map((op) => (
                    <option key={op.id} value={op.id} title={op.descricao}>
                      {op.rotulo}
                    </option>
                  ))}
                </select>
                <p className="tb-muted tb-escopo-video-narrado-diretriz-desc">
                  {
                    opcoesDiretrizConteudo.find((o) => o.id === diretrizConteudoLegendas)
                      ?.descricao
                  }
                </p>
              </div>
            </section>

            <section
              className="tb-stepper-iniciar-transcricao-corpo tb-escopo-video-narrado-secao-motor"
              aria-labelledby={`${tituloId}-perfil-tts`}
            >
              <div className="tb-escopo-video-narrado-secao-titulo-com-ajuda">
                <h3 id={`${tituloId}-perfil-tts`} className="tb-stepper-iniciar-transcricao-etapa-titulo">
                  Motor de áudio (TTS)
                </h3>
                <details className="tb-escopo-video-narrado-ajuda">
                  <summary
                    className="tb-escopo-video-narrado-ajuda-resumo"
                    aria-label="Ajuda sobre o motor TTS"
                    title="Ajuda sobre o motor TTS"
                  >
                    <svg
                      className="tb-escopo-video-narrado-ajuda-icone"
                      width="16"
                      height="16"
                      viewBox="0 0 16 16"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                      aria-hidden="true"
                    >
                      <circle cx="8" cy="8" r="6.25" stroke="currentColor" strokeWidth="1.5" />
                      <path
                        d="M8 7.25v4"
                        stroke="currentColor"
                        strokeWidth="1.5"
                        strokeLinecap="round"
                      />
                      <circle cx="8" cy="5.1" r="0.9" fill="currentColor" />
                    </svg>
                  </summary>
                  <div className="tb-escopo-video-narrado-ajuda-popover" role="note">
                    <p>
                      Flash costuma ser mais rápido; Pro tende a ser mais estável/expressivo.
                      Inclua slugs com <code>-tts</code> em Configurações /{" "}
                      <code>LITELLM_MODELOS_PROVISIONADOS</code>.
                    </p>
                    <p>
                      {opcoesPerfilTts.find((o) => o.id === perfilTts)?.descricao ||
                        "Use o padrão no dia a dia; o experimental é só para testes de voz."}
                    </p>
                    <p>
                      Cues em paralelo: quantas narrações pedir ao mesmo tempo (1 a 9). Valores
                      altos aceleram, mas podem aumentar 429/timeout no proxy.
                    </p>
                  </div>
                </details>
              </div>
              <div className="tb-escopo-video-narrado-grid-motor">
                <div className="tb-escopo-video-narrado-campo">
                  <label className="tb-label" htmlFor={`${tituloId}-select-modelo-tts`}>
                    Modelo TTS
                  </label>
                  <select
                    id={`${tituloId}-select-modelo-tts`}
                    className="tb-select"
                    value={modeloTts}
                    disabled={carregando || gerandoAmostra || opcoesModeloTts.length === 0}
                    onChange={(e) => {
                      setModeloTts(e.target.value);
                      setErroAmostra(null);
                      liberarAudioAmostra();
                    }}
                  >
                    {opcoesModeloTts.length === 0 ? (
                      <option value="">Nenhum modelo TTS na lista</option>
                    ) : (
                      opcoesModeloTts.map((m) => (
                        <option key={m} value={m}>
                          {rotuloCurtoModeloTtsParaUiTranscribrothers(m)}
                        </option>
                      ))
                    )}
                  </select>
                </div>
                <div className="tb-escopo-video-narrado-campo">
                  <label className="tb-label" htmlFor={`${tituloId}-select-perfil-tts`}>
                    Perfil de geração
                  </label>
                  <select
                    id={`${tituloId}-select-perfil-tts`}
                    className="tb-select"
                    value={perfilTts}
                    disabled={carregando || gerandoAmostra}
                    onChange={(e) => {
                      setPerfilTts(normalizarPerfilTtsNarracaoTranscribrothers(e.target.value));
                      setErroAmostra(null);
                      liberarAudioAmostra();
                    }}
                  >
                    {opcoesPerfilTts.map((op) => (
                      <option key={op.id} value={op.id}>
                        {op.rotulo}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="tb-escopo-video-narrado-campo">
                  <label className="tb-label" htmlFor={`${tituloId}-select-paralelismo-tts`}>
                    Cues em paralelo
                  </label>
                  <select
                    id={`${tituloId}-select-paralelismo-tts`}
                    className="tb-select"
                    value={paralelismoTtsExperimental}
                    disabled={carregando || gerandoAmostra}
                    onChange={(e) =>
                      setParalelismoTtsExperimental(
                        normalizarParalelismoTtsCuesExperimentalTranscribrothers(e.target.value),
                      )
                    }
                  >
                    {opcoesParalelismoExperimental.map((n) => (
                      <option key={n} value={n}>
                        {n}
                        {n === PARALELISMO_TTS_CUES_EXPERIMENTAL_PADRAO_TRANSCRIBROTHERS
                          ? " (padrão)"
                          : ""}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="tb-escopo-video-narrado-campo">
                  <ComponenteControleSliderTemperaturaTtsNarracaoComAjudaTranscribrothers
                    idInput={`${tituloId}-slider-temperatura-tts`}
                    valor={temperaturaTts}
                    desabilitado={carregando || gerandoAmostra}
                    onChange={(t) => {
                      setTemperaturaTts(t);
                      setErroAmostra(null);
                      liberarAudioAmostra();
                    }}
                  />
                </div>
                <div className="tb-escopo-video-narrado-campo">
                  <label className="tb-label" htmlFor={`${tituloId}-select-ritmo-tts`}>
                    Ritmo da fala
                  </label>
                  <select
                    id={`${tituloId}-select-ritmo-tts`}
                    className="tb-select"
                    value={ritmoTts}
                    disabled={carregando || gerandoAmostra}
                    title="Ajusta o ritmo via prompt (sem atempo no áudio)."
                    onChange={(e) => {
                      setRitmoTts(normalizarRitmoTtsNarracaoTranscribrothers(e.target.value));
                      setErroAmostra(null);
                      liberarAudioAmostra();
                    }}
                  >
                    {opcoesRitmoTts.map((op) => (
                      <option key={op.id} value={op.id} title={op.descricao}>
                        {op.rotulo}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            </section>

            <section
              className="tb-stepper-iniciar-transcricao-corpo tb-escopo-video-narrado-secao-voz"
              aria-labelledby={`${tituloId}-voz`}
            >
              <h3 id={`${tituloId}-voz`} className="tb-stepper-iniciar-transcricao-etapa-titulo">
                Voz da narração
              </h3>
              <div className="tb-escopo-video-narrado-voz-linha">
                <div className="tb-escopo-video-narrado-campo tb-escopo-video-narrado-campo--voz">
                  <label className="tb-label" htmlFor={`${tituloId}-select-voz`}>
                    Voz Gemini TTS 2.5
                  </label>
                  <select
                    id={`${tituloId}-select-voz`}
                    className="tb-select"
                    value={voz}
                    disabled={carregando || gerandoAmostra}
                    onChange={(e) => {
                      setVoz(e.target.value);
                      setErroAmostra(null);
                      liberarAudioAmostra();
                    }}
                  >
                    {listaVozes.map((op) => (
                      <option key={op.id} value={op.id}>
                        {op.id} — {op.estilo}
                      </option>
                    ))}
                  </select>
                </div>
                <button
                  type="button"
                  className="tb-btn-secundario tb-escopo-video-narrado-btn-amostra"
                  disabled={carregando || gerandoAmostra}
                  onClick={() => void ouvirAmostra()}
                >
                  {gerandoAmostra ? "Gerando…" : "Ouvir amostra"}
                </button>
              </div>
              {erroAmostra ? <p className="tb-drawer-erro-mm">{erroAmostra}</p> : null}
              <p className="tb-muted tb-drawer-dica-inline">
                Amostra curta com o motor e a temperatura acima. A voz fica salva para as próximas
                gerações.
              </p>
            </section>
          </div>

          <footer className="tb-stepper-iniciar-transcricao-rodape">
            <button
              type="button"
              className="tb-linkbtn"
              disabled={carregando || gerandoAmostra}
              onClick={fecharModal}
            >
              Cancelar
            </button>
            <div className="tb-stepper-iniciar-transcricao-rodape-direita">
              <button
                type="button"
                className="tb-primary"
                disabled={
                  carregando ||
                  gerandoAmostra ||
                  !modeloTts ||
                  opcoesModeloTts.length === 0 ||
                  (modo === "secoes" && !podeConfirmarSecoes)
                }
                onClick={confirmar}
              >
                {carregando ? "Agendando…" : "Gerar vídeo narrado"}
              </button>
            </div>
          </footer>
        </div>
      </div>
    </div>,
    document.body,
  );
}
