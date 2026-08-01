import { useEffect, useId, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";

import { gerarPreviewTtsAmostraVozNarracaoApiTranscribrothers } from "./modulo_api_preview_tts_amostra_voz_narracao_transcribrothers.ts";
import {
  filtrarMarkdownPorIdsEscopoSecoesVideoNarradoTranscribrothers,
  listarOpcoesEscopoSecoesVideoNarradoAPartirMarkdownTranscribrothers,
  type OpcaoEscopoSecaoVideoNarradoTranscribrothers,
} from "./modulo_util_filtrar_markdown_por_secoes_heading_nivel2_selecionadas_transcribrothers.ts";

export type OpcaoVozTtsNarracaoUiTranscribrothers = {
  id: string;
  estilo: string;
};

export type ResultadoEscopoGeracaoVideoNarradoTranscribrothers = {
  modo: "documento_inteiro" | "secoes";
  markdownNarracao: string | null;
  titulosSecoes: string[];
  voz: string;
};

type Props = {
  aberto: boolean;
  markdown: string;
  carregando: boolean;
  vozInicial: string;
  vozesDisponiveis: OpcaoVozTtsNarracaoUiTranscribrothers[];
  litellmModelTts?: string | null;
  onFechar: () => void;
  onConfirmar: (resultado: ResultadoEscopoGeracaoVideoNarradoTranscribrothers) => void;
};

export function ComponenteModalEscolherEscopoGeracaoVideoNarradoDocumentoOuSecoesTranscribrothers({
  aberto,
  markdown,
  carregando,
  vozInicial,
  vozesDisponiveis,
  litellmModelTts,
  onFechar,
  onConfirmar,
}: Props) {
  const tituloId = useId();
  const opcoes = useMemo(
    () => listarOpcoesEscopoSecoesVideoNarradoAPartirMarkdownTranscribrothers(markdown),
    [markdown],
  );
  const [modo, setModo] = useState<"documento_inteiro" | "secoes">("documento_inteiro");
  const [idsSelecionados, setIdsSelecionados] = useState<Set<string>>(() => new Set());
  const [voz, setVoz] = useState(vozInicial || "Kore");
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
    setErroAmostra(null);
  }, [aberto, opcoes, vozInicial]);

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
        litellmModel: litellmModelTts,
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
    if (modo === "documento_inteiro") {
      onConfirmar({
        modo: "documento_inteiro",
        markdownNarracao: null,
        titulosSecoes: [],
        voz: vozEfetiva,
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
              Escolha o escopo e a voz da narração (Gemini TTS 2.5). O Markdown do job não é alterado.
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
              className="tb-stepper-iniciar-transcricao-corpo tb-escopo-video-narrado-secao-voz"
              aria-labelledby={`${tituloId}-voz`}
            >
              <h3 id={`${tituloId}-voz`} className="tb-stepper-iniciar-transcricao-etapa-titulo">
                Voz da narração
              </h3>
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
              <div className="tb-escopo-video-narrado-voz-acoes">
                <button
                  type="button"
                  className="tb-btn-secundario"
                  disabled={carregando || gerandoAmostra}
                  onClick={() => void ouvirAmostra()}
                >
                  {gerandoAmostra ? "Gerando amostra…" : "Ouvir amostra"}
                </button>
              </div>
              {erroAmostra ? <p className="tb-drawer-erro-mm">{erroAmostra}</p> : null}
              <p className="tb-muted tb-drawer-dica-inline">
                A amostra usa uma frase curta só para você ouvir o timbre. A voz escolhida fica salva para as
                próximas gerações.
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
                  carregando || gerandoAmostra || (modo === "secoes" && !podeConfirmarSecoes)
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
