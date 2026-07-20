import { useEffect, useId, useRef, useState } from "react";
import { createPortal } from "react-dom";

import type { PipelineCatalogoApiTranscribrothers } from "./tipos_catalogo_pipelines_api_transcribrothers.ts";
import { filtrarEOrdenarPipelinesCustomExecutaveisCatalogoTranscribrothers } from "./modulo_util_ordenar_e_filtrar_pipelines_custom_executaveis_catalogo_transcribrothers.ts";
import type { DestinoAposTranscricaoTranscribrothers } from "./modulo_constante_destino_apos_transcricao_e_rotulo_frame_documento_transcribrothers.ts";
import { DESTINO_APOS_TRANSCRICAO_PADRAO_NOVO_PROJETO_TRANSCRIBROTHERS } from "./modulo_constante_destino_apos_transcricao_e_rotulo_frame_documento_transcribrothers.ts";
import { carregarArquivoVideoDeStagingTranscribrothers } from "./modulo_util_deep_link_importacao_recbrothers_transcribrothers.ts";
import type { DestinoImportarTranscricaoProntaTranscribrothers } from "./modulo_api_importar_transcricao_pronta_job_transcribrothers.ts";

const DESCRICAO_DESTINO: Record<DestinoAposTranscricaoTranscribrothers, string> = {
  gerar_tutorial:
    "Transcreve o áudio, captura telas do vídeo e monta um tutorial em Markdown com imagens e links para o tempo no vídeo.",
  projeto_em_branco: "Cria um documento vazio para edição manual (sem pipeline de vídeo).",
  reproducao_bug:
    "Monta um passo a passo de reprodução do bug com capturas de tela e IA. Com JSON de cliques (RecBrothers ou manual), alinha aos cliques; sem JSON, infere passos da transcrição e das telas.",
  notas_proposta_funcionalidade:
    "Gera notas estruturadas (contexto, proposta, decisões, pendências) a partir da fala — com vídeo/áudio gera capturas quando possível; com transcrição importada, só texto.",
  so_transcricao:
    "Publica o texto da transcrição no job — sem capturas nem geração de tutorial/notas/bug. Com vídeo/áudio, faz STT; com texto já pronto, só importa.",
};

const MAPEAMENTO_PIPELINE_SISTEMA_COPIADO_DE_PARA_DESTINO_TRANSCRIBROTHERS: Record<
  string,
  DestinoAposTranscricaoTranscribrothers
> = {
  pipeline_inicial_tutorial: "gerar_tutorial",
  pipeline_inicial_notas_proposta: "notas_proposta_funcionalidade",
  pipeline_inicial_reproducao_bug: "reproducao_bug",
  pipeline_inicial_so_transcricao: "so_transcricao",
};

const ACCEPT_VIDEO =
  "video/mp4,video/webm,video/quicktime,.mkv,.mpeg,.mpg,.avi,.m4v";
const ACCEPT_AUDIO = "audio/wav,audio/mpeg,audio/mp4,audio/ogg,audio/flac,.wav,.mp3,.m4a,.ogg,.flac,.aac,.opus";
const ACCEPT_TRANSCRICAO = ".txt,.md,.srt,.vtt,text/plain,text/markdown,text/vtt";

type TipoEntradaStepperTranscribrothers = "video" | "audio" | "transcricao_pronta";

function pipelineAceitaTipoEntradaTranscribrothers(
  pipeline: PipelineCatalogoApiTranscribrothers,
  tipo: TipoEntradaStepperTranscribrothers,
): boolean {
  if (tipo === "transcricao_pronta") {
    return pipeline.copiado_de === "pipeline_inicial_notas_proposta";
  }
  const entradas = pipeline.entradas_aceitas?.length ? pipeline.entradas_aceitas : ["video"];
  return entradas.includes(tipo);
}

function resolverDestinoAposTranscricaoEfetivoStepperTranscribrothers(
  destino: DestinoAposTranscricaoTranscribrothers,
  pipelineCustomId: string | null,
  pipelinesCustom: PipelineCatalogoApiTranscribrothers[],
): DestinoAposTranscricaoTranscribrothers {
  if (!pipelineCustomId) return destino;
  const pipeline = pipelinesCustom.find((p) => p.id === pipelineCustomId);
  const copiadoDe = pipeline?.copiado_de?.trim();
  if (copiadoDe && MAPEAMENTO_PIPELINE_SISTEMA_COPIADO_DE_PARA_DESTINO_TRANSCRIBROTHERS[copiadoDe]) {
    return MAPEAMENTO_PIPELINE_SISTEMA_COPIADO_DE_PARA_DESTINO_TRANSCRIBROTHERS[copiadoDe];
  }
  return destino;
}

export type { DestinoAposTranscricaoTranscribrothers };

export type ImportacaoRecbrothersModalStepperTranscribrothers = {
  etapaInicial: 0 | 1;
  stagingId: string;
  destinoInicial?: DestinoAposTranscricaoTranscribrothers;
  totalCliquesStaging?: number;
};

type PropsModalStepperIniciarTranscricaoTranscribrothers = {
  aberto: boolean;
  carregando: boolean;
  importacaoRecbrothers?: ImportacaoRecbrothersModalStepperTranscribrothers | null;
  onFechar: () => void;
  onIniciar: (
    arquivo: File,
    destino: DestinoAposTranscricaoTranscribrothers,
    cliquesJsonOpcional?: File | null,
    pipelineCustomId?: string | null,
  ) => void;
  onIniciarComTranscricaoPronta?: (
    destino: DestinoImportarTranscricaoProntaTranscribrothers,
    opcoes: { texto: string; arquivo: File | null; pipelineCustomId: string | null },
  ) => void;
};

function formatarTamanhoArquivoMbTranscribrothers(bytes: number): string {
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function ModalStepperIniciarTranscricaoEscolherVideoEDestinoTranscribrothers({
  aberto,
  carregando,
  importacaoRecbrothers = null,
  onFechar,
  onIniciar,
  onIniciarComTranscricaoPronta,
}: PropsModalStepperIniciarTranscricaoTranscribrothers) {
  const tituloId = useId();
  const inputVideoRef = useRef<HTMLInputElement | null>(null);
  const inputCliquesJsonRef = useRef<HTMLInputElement | null>(null);
  const inputTranscricaoRef = useRef<HTMLInputElement | null>(null);
  const [etapa, setEtapa] = useState(0);
  const [tipoEntrada, setTipoEntrada] = useState<TipoEntradaStepperTranscribrothers>("video");
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [arquivoCliquesJson, setArquivoCliquesJson] = useState<File | null>(null);
  const [textoTranscricaoPronta, setTextoTranscricaoPronta] = useState("");
  const [arquivoTranscricaoPronta, setArquivoTranscricaoPronta] = useState<File | null>(null);
  const [destino, setDestino] = useState<DestinoAposTranscricaoTranscribrothers>(
    DESTINO_APOS_TRANSCRICAO_PADRAO_NOVO_PROJETO_TRANSCRIBROTHERS,
  );
  const [pipelineCustomId, setPipelineCustomId] = useState<string | null>(null);
  const [pipelinesCustomExecutaveis, setPipelinesCustomExecutaveis] = useState<PipelineCatalogoApiTranscribrothers[]>(
    [],
  );
  const [carregandoImportacaoRecbrothers, setCarregandoImportacaoRecbrothers] = useState(false);
  const [erroImportacaoRecbrothers, setErroImportacaoRecbrothers] = useState<string | null>(null);

  const importadoDoRecbrothers = Boolean(importacaoRecbrothers?.stagingId);
  const tipoEntradaEfetivo: TipoEntradaStepperTranscribrothers = importadoDoRecbrothers ? "video" : tipoEntrada;
  const ehTranscricaoPronta = tipoEntradaEfetivo === "transcricao_pronta";

  const pipelinesCustomFiltradas = pipelinesCustomExecutaveis.filter((p) =>
    pipelineAceitaTipoEntradaTranscribrothers(p, tipoEntradaEfetivo),
  );

  const destinoEfetivo = resolverDestinoAposTranscricaoEfetivoStepperTranscribrothers(
    destino,
    pipelineCustomId,
    pipelinesCustomFiltradas,
  );

  useEffect(() => {
    if (!aberto) return;
    void fetch("/api/pipelines/catalogo")
      .then((r) => r.json())
      .then((d: { pipelines?: PipelineCatalogoApiTranscribrothers[] }) => {
        const custom = filtrarEOrdenarPipelinesCustomExecutaveisCatalogoTranscribrothers(d.pipelines ?? []);
        setPipelinesCustomExecutaveis(custom);
      })
      .catch(() => setPipelinesCustomExecutaveis([]));
  }, [aberto]);

  useEffect(() => {
    if (!aberto) return;
    if (importacaoRecbrothers) {
      setEtapa(importacaoRecbrothers.etapaInicial);
      setTipoEntrada("video");
      setDestino(
        importacaoRecbrothers.destinoInicial ?? DESTINO_APOS_TRANSCRICAO_PADRAO_NOVO_PROJETO_TRANSCRIBROTHERS,
      );
      setArquivo(null);
      setArquivoCliquesJson(null);
      setTextoTranscricaoPronta("");
      setArquivoTranscricaoPronta(null);
      setErroImportacaoRecbrothers(null);
      setCarregandoImportacaoRecbrothers(true);
      let cancelado = false;
      void carregarArquivoVideoDeStagingTranscribrothers(importacaoRecbrothers.stagingId)
        .then((file) => {
          if (cancelado) return;
          setArquivo(file);
        })
        .catch((e: unknown) => {
          if (cancelado) return;
          const msg = e instanceof Error ? e.message : "Falha ao carregar vídeo do RecBrothers.";
          setErroImportacaoRecbrothers(msg);
        })
        .finally(() => {
          if (!cancelado) setCarregandoImportacaoRecbrothers(false);
        });
      return () => {
        cancelado = true;
      };
    }
    setEtapa(0);
    setTipoEntrada("video");
    setArquivo(null);
    setArquivoCliquesJson(null);
    setTextoTranscricaoPronta("");
    setArquivoTranscricaoPronta(null);
    setDestino(DESTINO_APOS_TRANSCRICAO_PADRAO_NOVO_PROJETO_TRANSCRIBROTHERS);
    setPipelineCustomId(null);
    setErroImportacaoRecbrothers(null);
    setCarregandoImportacaoRecbrothers(false);
  }, [aberto, importacaoRecbrothers]);

  useEffect(() => {
    if (tipoEntradaEfetivo === "audio") {
      if (destino !== "so_transcricao") setDestino("so_transcricao");
    }
    if (tipoEntradaEfetivo === "transcricao_pronta") {
      if (destino !== "so_transcricao" && destino !== "notas_proposta_funcionalidade") {
        setDestino("so_transcricao");
      }
    }
    if (pipelineCustomId && !pipelinesCustomFiltradas.some((p) => p.id === pipelineCustomId)) {
      setPipelineCustomId(null);
    }
  }, [tipoEntradaEfetivo, destino, pipelineCustomId, pipelinesCustomFiltradas]);

  if (!aberto) return null;

  const podeAvancarEtapaArquivo = ehTranscricaoPronta
    ? Boolean(textoTranscricaoPronta.trim() || arquivoTranscricaoPronta)
    : Boolean(arquivo);
  const ehUltimaEtapa = etapa === 1;

  function fecharModal() {
    if (carregando) return;
    onFechar();
  }

  function confirmarCriarProjeto() {
    if (ehTranscricaoPronta) {
      const dest =
        destinoEfetivo === "notas_proposta_funcionalidade"
          ? "notas_proposta_funcionalidade"
          : "so_transcricao";
      onIniciarComTranscricaoPronta?.(dest, {
        texto: textoTranscricaoPronta,
        arquivo: arquivoTranscricaoPronta,
        pipelineCustomId,
      });
      return;
    }
    if (arquivo) {
      const cliques =
        destinoEfetivo === "reproducao_bug" && !importadoDoRecbrothers ? arquivoCliquesJson : null;
      onIniciar(arquivo, destinoEfetivo, cliques, pipelineCustomId);
    }
  }

  return createPortal(
    <div className="tb-modal-job-root" role="presentation">
      <button
        type="button"
        className="tb-modal-job-backdrop"
        aria-label="Fechar"
        disabled={carregando}
        onClick={fecharModal}
      />
      <div className="tb-modal-job-shell tb-modal-job-shell-stepper-iniciar-transcricao">
        <div
          className="tb-modal-job tb-modal-stepper-iniciar-transcricao"
          role="dialog"
          aria-modal="true"
          aria-labelledby={tituloId}
        >
          <header className="tb-stepper-iniciar-transcricao-cabecalho">
            <h2 id={tituloId} className="tb-modal-job-titulo">
              Novo projeto
            </h2>
            <p className="tb-muted tb-stepper-iniciar-transcricao-lead-modal">
              {importadoDoRecbrothers
                ? importacaoRecbrothers?.destinoInicial === "reproducao_bug"
                  ? "Vídeo importado do RecBrothers com registro de cliques. Confirme o destino e crie o projeto."
                  : "Vídeo importado do RecBrothers. Escolha o destino e crie o projeto para iniciar a transcrição."
                : "Envie vídeo, áudio ou uma transcrição já pronta e escolha o destino."}
            </p>
            {carregandoImportacaoRecbrothers ? (
              <p className="tb-muted" role="status">
                Carregando vídeo importado…
              </p>
            ) : null}
            {erroImportacaoRecbrothers ? (
              <p className="tb-erro-formulario" role="alert">
                {erroImportacaoRecbrothers}
              </p>
            ) : null}
            <nav className="tb-stepper-iniciar-transcricao" aria-label="Etapas do novo projeto">
              <ol className="tb-stepper-iniciar-transcricao-lista">
                <li
                  className={`tb-stepper-iniciar-transcricao-passo${etapa === 0 ? " tb-stepper-iniciar-transcricao-passo--ativo" : etapa > 0 ? " tb-stepper-iniciar-transcricao-passo--feito" : ""}`}
                >
                  <span className="tb-stepper-iniciar-transcricao-numero" aria-hidden="true">
                    1
                  </span>
                  <span className="tb-stepper-iniciar-transcricao-rotulo">
                    {ehTranscricaoPronta ? "Transcrição" : "Arquivo"}
                  </span>
                </li>
                <li className="tb-stepper-iniciar-transcricao-conector" aria-hidden="true" />
                <li
                  className={`tb-stepper-iniciar-transcricao-passo${etapa === 1 ? " tb-stepper-iniciar-transcricao-passo--ativo" : ""}`}
                >
                  <span className="tb-stepper-iniciar-transcricao-numero" aria-hidden="true">
                    2
                  </span>
                  <span className="tb-stepper-iniciar-transcricao-rotulo">Destino</span>
                </li>
              </ol>
            </nav>
          </header>

          <div className="tb-stepper-iniciar-transcricao-corpo-rolavel">
            {etapa === 0 ? (
              <section className="tb-stepper-iniciar-transcricao-corpo" aria-labelledby={`${tituloId}-etapa-video`}>
                <h3 id={`${tituloId}-etapa-video`} className="tb-stepper-iniciar-transcricao-etapa-titulo">
                  {ehTranscricaoPronta ? "Cole ou envie a transcrição" : "Escolha o arquivo"}
                </h3>
                <p className="tb-muted tb-stepper-iniciar-transcricao-etapa-lead">
                  {ehTranscricaoPronta
                    ? "Sem STT: o texto vira o snapshot do job. Formatos: TXT, MD, SRT ou VTT."
                    : "O arquivo será enviado ao servidor. O tipo (vídeo ou áudio) limita as pipelines disponíveis."}
                </p>
                {!importadoDoRecbrothers ? (
                  <div
                    className="tb-stepper-iniciar-transcricao-opcoes-destino"
                    role="radiogroup"
                    aria-label="Tipo de entrada"
                  >
                    <label
                      className={`tb-stepper-iniciar-transcricao-opcao-destino${tipoEntrada === "video" ? " tb-stepper-iniciar-transcricao-opcao-destino--selecionada" : ""}`}
                    >
                      <input
                        type="radio"
                        name="tipo-entrada-midia"
                        value="video"
                        checked={tipoEntrada === "video"}
                        onChange={() => {
                          setTipoEntrada("video");
                          setArquivo(null);
                          setArquivoTranscricaoPronta(null);
                          setTextoTranscricaoPronta("");
                        }}
                      />
                      <span className="tb-stepper-iniciar-transcricao-opcao-titulo">Vídeo</span>
                    </label>
                    <label
                      className={`tb-stepper-iniciar-transcricao-opcao-destino${tipoEntrada === "audio" ? " tb-stepper-iniciar-transcricao-opcao-destino--selecionada" : ""}`}
                    >
                      <input
                        type="radio"
                        name="tipo-entrada-midia"
                        value="audio"
                        checked={tipoEntrada === "audio"}
                        onChange={() => {
                          setTipoEntrada("audio");
                          setArquivo(null);
                          setArquivoTranscricaoPronta(null);
                          setTextoTranscricaoPronta("");
                          setDestino("so_transcricao");
                          setPipelineCustomId(null);
                        }}
                      />
                      <span className="tb-stepper-iniciar-transcricao-opcao-titulo">Áudio</span>
                    </label>
                    <label
                      className={`tb-stepper-iniciar-transcricao-opcao-destino${tipoEntrada === "transcricao_pronta" ? " tb-stepper-iniciar-transcricao-opcao-destino--selecionada" : ""}`}
                    >
                      <input
                        type="radio"
                        name="tipo-entrada-midia"
                        value="transcricao_pronta"
                        checked={tipoEntrada === "transcricao_pronta"}
                        onChange={() => {
                          setTipoEntrada("transcricao_pronta");
                          setArquivo(null);
                          setDestino("so_transcricao");
                          setPipelineCustomId(null);
                        }}
                      />
                      <span className="tb-stepper-iniciar-transcricao-opcao-titulo">Transcrição pronta</span>
                    </label>
                  </div>
                ) : null}

                {ehTranscricaoPronta ? (
                  <>
                    <label className="tb-field">
                      <span className="tb-field-label">Texto da transcrição</span>
                      <textarea
                        className="tb-input"
                        rows={8}
                        value={textoTranscricaoPronta}
                        disabled={carregando}
                        placeholder="Cole aqui a fala já transcrita…"
                        onChange={(e) => setTextoTranscricaoPronta(e.target.value)}
                      />
                    </label>
                    <p className="tb-muted">Ou envie um arquivo (.txt, .md, .srt, .vtt):</p>
                    <input
                      ref={inputTranscricaoRef}
                      className="tb-input-file-oculto"
                      type="file"
                      accept={ACCEPT_TRANSCRICAO}
                      onChange={(e) => setArquivoTranscricaoPronta(e.target.files?.[0] ?? null)}
                    />
                    <button
                      type="button"
                      className={`tb-stepper-iniciar-transcricao-zona-arquivo${arquivoTranscricaoPronta ? " tb-stepper-iniciar-transcricao-zona-arquivo--preenchida" : ""}`}
                      onClick={() => inputTranscricaoRef.current?.click()}
                    >
                      {arquivoTranscricaoPronta ? (
                        <>
                          <strong className="tb-stepper-iniciar-transcricao-nome-arquivo">
                            {arquivoTranscricaoPronta.name}
                          </strong>
                          <span className="tb-muted">
                            {formatarTamanhoArquivoMbTranscribrothers(arquivoTranscricaoPronta.size)}
                          </span>
                          <span className="tb-stepper-iniciar-transcricao-trocar">Clique para trocar</span>
                        </>
                      ) : (
                        <>
                          <span className="tb-stepper-iniciar-transcricao-cta">Selecionar arquivo de texto</span>
                          <span className="tb-muted">TXT, MD, SRT, VTT</span>
                        </>
                      )}
                    </button>
                  </>
                ) : (
                  <>
                    <input
                      ref={inputVideoRef}
                      className="tb-input-file-oculto"
                      type="file"
                      accept={tipoEntradaEfetivo === "audio" ? ACCEPT_AUDIO : ACCEPT_VIDEO}
                      onChange={(e) => setArquivo(e.target.files?.[0] ?? null)}
                    />
                    <button
                      type="button"
                      className={`tb-stepper-iniciar-transcricao-zona-arquivo${arquivo ? " tb-stepper-iniciar-transcricao-zona-arquivo--preenchida" : ""}`}
                      onClick={() => inputVideoRef.current?.click()}
                    >
                      {arquivo ? (
                        <>
                          <strong className="tb-stepper-iniciar-transcricao-nome-arquivo">{arquivo.name}</strong>
                          <span className="tb-muted">
                            {formatarTamanhoArquivoMbTranscribrothers(arquivo.size)}
                          </span>
                          <span className="tb-stepper-iniciar-transcricao-trocar">Clique para trocar o arquivo</span>
                        </>
                      ) : (
                        <>
                          <span className="tb-stepper-iniciar-transcricao-cta">
                            {tipoEntradaEfetivo === "audio"
                              ? "Selecionar arquivo de áudio"
                              : "Selecionar arquivo de vídeo"}
                          </span>
                          <span className="tb-muted">
                            {tipoEntradaEfetivo === "audio"
                              ? "WAV, MP3, M4A, OGG, FLAC…"
                              : "MP4, WebM, MOV, MKV, AVI…"}
                          </span>
                        </>
                      )}
                    </button>
                  </>
                )}
              </section>
            ) : (
              <section className="tb-stepper-iniciar-transcricao-corpo" aria-labelledby={`${tituloId}-etapa-destino`}>
                <h3 id={`${tituloId}-etapa-destino`} className="tb-stepper-iniciar-transcricao-etapa-titulo">
                  O que fazer com a transcrição?
                </h3>
                <p className="tb-muted tb-stepper-iniciar-transcricao-etapa-lead">
                  {ehTranscricaoPronta
                    ? "Nesta versão: manter só o texto ou gerar notas (sem vídeo para tutorial/bug)."
                    : tipoEntradaEfetivo === "audio"
                      ? "Com áudio, nesta versão só está disponível «Só transcrição» (e pipelines custom compatíveis)."
                      : "Escolha como processar este arquivo no Transcribrothers."}
                </p>
                {importacaoRecbrothers?.totalCliquesStaging ? (
                  <p className="tb-muted tb-stepper-iniciar-transcricao-resumo-arquivo">
                    Registro RecBrothers:{" "}
                    <strong>{importacaoRecbrothers.totalCliquesStaging} clique(s)</strong> no JSON.
                  </p>
                ) : null}
                {ehTranscricaoPronta ? (
                  <p className="tb-stepper-iniciar-transcricao-resumo-arquivo">
                    <span className="tb-muted">Entrada:</span>{" "}
                    <strong>
                      {arquivoTranscricaoPronta
                        ? arquivoTranscricaoPronta.name
                        : `${textoTranscricaoPronta.trim().length} caracteres colados`}
                    </strong>
                  </p>
                ) : arquivo ? (
                  <p className="tb-stepper-iniciar-transcricao-resumo-arquivo">
                    <span className="tb-muted">{tipoEntradaEfetivo === "audio" ? "Áudio:" : "Vídeo:"}</span>{" "}
                    <strong>{arquivo.name}</strong> ({formatarTamanhoArquivoMbTranscribrothers(arquivo.size)})
                  </p>
                ) : null}
                <div className="tb-stepper-iniciar-transcricao-opcoes-destino" role="radiogroup" aria-label="Destino">
                  {tipoEntradaEfetivo === "video" ? (
                    <>
                      <label
                        className={`tb-stepper-iniciar-transcricao-opcao-destino${destino === "gerar_tutorial" && !pipelineCustomId ? " tb-stepper-iniciar-transcricao-opcao-destino--selecionada" : ""}`}
                      >
                        <input
                          type="radio"
                          name="destino-transcricao"
                          value="gerar_tutorial"
                          checked={destino === "gerar_tutorial" && !pipelineCustomId}
                          onChange={() => {
                            setDestino("gerar_tutorial");
                            setPipelineCustomId(null);
                          }}
                        />
                        <span className="tb-stepper-iniciar-transcricao-opcao-titulo">Gerar tutorial</span>
                        <span className="tb-muted tb-stepper-iniciar-transcricao-opcao-desc">
                          {DESCRICAO_DESTINO.gerar_tutorial}
                        </span>
                      </label>
                      <label
                        className={`tb-stepper-iniciar-transcricao-opcao-destino${destino === "notas_proposta_funcionalidade" && !pipelineCustomId ? " tb-stepper-iniciar-transcricao-opcao-destino--selecionada" : ""}`}
                      >
                        <input
                          type="radio"
                          name="destino-transcricao"
                          value="notas_proposta_funcionalidade"
                          checked={destino === "notas_proposta_funcionalidade" && !pipelineCustomId}
                          onChange={() => {
                            setDestino("notas_proposta_funcionalidade");
                            setPipelineCustomId(null);
                          }}
                        />
                        <span className="tb-stepper-iniciar-transcricao-opcao-titulo">Notas de proposta</span>
                        <span className="tb-muted tb-stepper-iniciar-transcricao-opcao-desc">
                          {DESCRICAO_DESTINO.notas_proposta_funcionalidade}
                        </span>
                      </label>
                      <label
                        className={`tb-stepper-iniciar-transcricao-opcao-destino${destino === "reproducao_bug" && !pipelineCustomId ? " tb-stepper-iniciar-transcricao-opcao-destino--selecionada" : ""}`}
                      >
                        <input
                          type="radio"
                          name="destino-transcricao"
                          value="reproducao_bug"
                          checked={destino === "reproducao_bug" && !pipelineCustomId}
                          onChange={() => {
                            setDestino("reproducao_bug");
                            setPipelineCustomId(null);
                          }}
                        />
                        <span className="tb-stepper-iniciar-transcricao-opcao-titulo">Reproduzir bug</span>
                        <span className="tb-muted tb-stepper-iniciar-transcricao-opcao-desc">
                          {DESCRICAO_DESTINO.reproducao_bug}
                        </span>
                      </label>
                    </>
                  ) : null}
                  {ehTranscricaoPronta ? (
                    <label
                      className={`tb-stepper-iniciar-transcricao-opcao-destino${destino === "notas_proposta_funcionalidade" && !pipelineCustomId ? " tb-stepper-iniciar-transcricao-opcao-destino--selecionada" : ""}`}
                    >
                      <input
                        type="radio"
                        name="destino-transcricao"
                        value="notas_proposta_funcionalidade"
                        checked={destino === "notas_proposta_funcionalidade" && !pipelineCustomId}
                        onChange={() => {
                          setDestino("notas_proposta_funcionalidade");
                          setPipelineCustomId(null);
                        }}
                      />
                      <span className="tb-stepper-iniciar-transcricao-opcao-titulo">Notas de proposta</span>
                      <span className="tb-muted tb-stepper-iniciar-transcricao-opcao-desc">
                        {DESCRICAO_DESTINO.notas_proposta_funcionalidade}
                      </span>
                    </label>
                  ) : null}
                  <label
                    className={`tb-stepper-iniciar-transcricao-opcao-destino${destino === "so_transcricao" && !pipelineCustomId ? " tb-stepper-iniciar-transcricao-opcao-destino--selecionada" : ""}`}
                  >
                    <input
                      type="radio"
                      name="destino-transcricao"
                      value="so_transcricao"
                      checked={destino === "so_transcricao" && !pipelineCustomId}
                      onChange={() => {
                        setDestino("so_transcricao");
                        setPipelineCustomId(null);
                      }}
                    />
                    <span className="tb-stepper-iniciar-transcricao-opcao-titulo">Só transcrição</span>
                    <span className="tb-muted tb-stepper-iniciar-transcricao-opcao-desc">
                      {DESCRICAO_DESTINO.so_transcricao}
                    </span>
                  </label>
                </div>
                {pipelinesCustomFiltradas.length > 0 ? (
                  <div className="tb-stepper-iniciar-transcricao-pipelines-custom">
                    <h4 className="tb-stepper-iniciar-transcricao-etapa-titulo">Pipelines customizadas</h4>
                    <div
                      className="tb-stepper-iniciar-transcricao-opcoes-destino"
                      role="radiogroup"
                      aria-label="Pipeline custom"
                    >
                      {pipelinesCustomFiltradas.map((p) => (
                        <label
                          key={p.id}
                          className={`tb-stepper-iniciar-transcricao-opcao-destino${pipelineCustomId === p.id ? " tb-stepper-iniciar-transcricao-opcao-destino--selecionada" : ""}`}
                        >
                          <input
                            type="radio"
                            name="destino-transcricao"
                            value={`custom:${p.id}`}
                            checked={pipelineCustomId === p.id}
                            onChange={() => {
                              setPipelineCustomId(p.id);
                              const copiadoDe = p.copiado_de?.trim();
                              if (
                                copiadoDe &&
                                MAPEAMENTO_PIPELINE_SISTEMA_COPIADO_DE_PARA_DESTINO_TRANSCRIBROTHERS[copiadoDe]
                              ) {
                                setDestino(
                                  MAPEAMENTO_PIPELINE_SISTEMA_COPIADO_DE_PARA_DESTINO_TRANSCRIBROTHERS[copiadoDe],
                                );
                              }
                            }}
                          />
                          <span className="tb-stepper-iniciar-transcricao-opcao-titulo">{p.titulo}</span>
                          <span className="tb-muted tb-stepper-iniciar-transcricao-opcao-desc">{p.descricao}</span>
                        </label>
                      ))}
                    </div>
                  </div>
                ) : null}
                {destinoEfetivo === "reproducao_bug" && !importadoDoRecbrothers && !ehTranscricaoPronta ? (
                  <div className="tb-stepper-iniciar-transcricao-anexo-cliques-json">
                    <p className="tb-muted tb-stepper-iniciar-transcricao-etapa-lead">
                      JSON de cliques (opcional): formato RecBrothers com array <code>cliques</code> e{" "}
                      <code>tRelativoMs</code>. Sem arquivo, os passos serão inferidos da transcrição e das capturas
                      de tela.
                    </p>
                    <input
                      ref={inputCliquesJsonRef}
                      className="tb-input-file-oculto"
                      type="file"
                      accept="application/json,.json"
                      onChange={(e) => setArquivoCliquesJson(e.target.files?.[0] ?? null)}
                    />
                    <button
                      type="button"
                      className={`tb-stepper-iniciar-transcricao-zona-arquivo tb-stepper-iniciar-transcricao-zona-arquivo--secundaria${arquivoCliquesJson ? " tb-stepper-iniciar-transcricao-zona-arquivo--preenchida" : ""}`}
                      onClick={() => inputCliquesJsonRef.current?.click()}
                    >
                      {arquivoCliquesJson ? (
                        <>
                          <strong className="tb-stepper-iniciar-transcricao-nome-arquivo">
                            {arquivoCliquesJson.name}
                          </strong>
                          <span className="tb-stepper-iniciar-transcricao-trocar">Clique para trocar o JSON</span>
                        </>
                      ) : (
                        <>
                          <span className="tb-stepper-iniciar-transcricao-cta">Anexar JSON de cliques (opcional)</span>
                          <span className="tb-muted">RecBrothers ou compatível</span>
                        </>
                      )}
                    </button>
                  </div>
                ) : null}
              </section>
            )}
          </div>

          <footer className="tb-stepper-iniciar-transcricao-rodape">
            <button type="button" className="tb-linkbtn" disabled={carregando} onClick={fecharModal}>
              Cancelar
            </button>
            <div className="tb-stepper-iniciar-transcricao-rodape-direita">
              {etapa > 0 && !importadoDoRecbrothers ? (
                <button type="button" className="tb-linkbtn" disabled={carregando} onClick={() => setEtapa(0)}>
                  Voltar
                </button>
              ) : null}
              {!ehUltimaEtapa ? (
                <button
                  type="button"
                  className="tb-primary"
                  disabled={!podeAvancarEtapaArquivo || carregando || carregandoImportacaoRecbrothers}
                  onClick={() => setEtapa(1)}
                >
                  Próximo
                </button>
              ) : (
                <button
                  type="button"
                  className="tb-primary"
                  disabled={
                    (ehTranscricaoPronta ? !podeAvancarEtapaArquivo || !onIniciarComTranscricaoPronta : !arquivo) ||
                    carregando ||
                    carregandoImportacaoRecbrothers ||
                    Boolean(erroImportacaoRecbrothers)
                  }
                  onClick={confirmarCriarProjeto}
                >
                  {carregando ? "A criar…" : "Criar projeto"}
                </button>
              )}
            </div>
          </footer>
        </div>
      </div>
    </div>,
    document.body,
  );
}
