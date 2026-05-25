import { useEffect, useId, useRef, useState } from "react";
import { createPortal } from "react-dom";

import type { DestinoAposTranscricaoTranscribrothers } from "./modulo_constante_destino_apos_transcricao_e_rotulo_frame_documento_transcribrothers.ts";
import { DESTINO_APOS_TRANSCRICAO_PADRAO_NOVO_PROJETO_TRANSCRIBROTHERS } from "./modulo_constante_destino_apos_transcricao_e_rotulo_frame_documento_transcribrothers.ts";
import { carregarArquivoVideoDeStagingTranscribrothers } from "./modulo_util_deep_link_importacao_recbrothers_transcribrothers.ts";

export type { DestinoAposTranscricaoTranscribrothers };

const DESCRICAO_DESTINO: Record<DestinoAposTranscricaoTranscribrothers, string> = {
  gerar_tutorial:
    "Transcreve o áudio, captura telas do vídeo e monta um tutorial em Markdown com imagens e links para o tempo no vídeo.",
  projeto_em_branco: "Cria um documento vazio para edição manual (sem pipeline de vídeo).",
  reproducao_bug:
    "Monta um passo a passo de reprodução do bug com capturas de tela e IA. Com JSON de cliques (RecBrothers ou manual), alinha aos cliques; sem JSON, infere passos da transcrição e das telas.",
  notas_proposta_funcionalidade:
    "Transcreve reunião de discovery ou refinement e gera notas estruturadas (contexto, proposta, decisões, pendências) com links para o vídeo e capturas de slides ou telas compartilhadas.",
};

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
}: PropsModalStepperIniciarTranscricaoTranscribrothers) {
  const tituloId = useId();
  const inputVideoRef = useRef<HTMLInputElement | null>(null);
  const inputCliquesJsonRef = useRef<HTMLInputElement | null>(null);
  const [etapa, setEtapa] = useState(0);
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [arquivoCliquesJson, setArquivoCliquesJson] = useState<File | null>(null);
  const [destino, setDestino] = useState<DestinoAposTranscricaoTranscribrothers>(
    DESTINO_APOS_TRANSCRICAO_PADRAO_NOVO_PROJETO_TRANSCRIBROTHERS,
  );
  const [carregandoImportacaoRecbrothers, setCarregandoImportacaoRecbrothers] = useState(false);
  const [erroImportacaoRecbrothers, setErroImportacaoRecbrothers] = useState<string | null>(null);

  const importadoDoRecbrothers = Boolean(importacaoRecbrothers?.stagingId);

  useEffect(() => {
    if (!aberto) return;
    if (importacaoRecbrothers) {
      setEtapa(importacaoRecbrothers.etapaInicial);
      setDestino(
        importacaoRecbrothers.destinoInicial ?? DESTINO_APOS_TRANSCRICAO_PADRAO_NOVO_PROJETO_TRANSCRIBROTHERS,
      );
      setArquivo(null);
      setArquivoCliquesJson(null);
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
    setArquivo(null);
    setArquivoCliquesJson(null);
    setDestino(DESTINO_APOS_TRANSCRICAO_PADRAO_NOVO_PROJETO_TRANSCRIBROTHERS);
    setErroImportacaoRecbrothers(null);
    setCarregandoImportacaoRecbrothers(false);
  }, [aberto, importacaoRecbrothers]);

  if (!aberto) return null;

  const podeAvancarEtapaVideo = Boolean(arquivo);
  const ehUltimaEtapa = etapa === 1;

  function fecharModal() {
    if (carregando) return;
    onFechar();
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
                : "Envie um vídeo do seu computador para gerar transcrição, capturas de tela e tutorial em Markdown."}
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
                  <span className="tb-stepper-iniciar-transcricao-rotulo">Vídeo</span>
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
                Escolha o vídeo
              </h3>
              <p className="tb-muted tb-stepper-iniciar-transcricao-etapa-lead">
                O arquivo será enviado ao servidor para transcrição e processamento.
              </p>
              <input
                ref={inputVideoRef}
                className="tb-input-file-oculto"
                type="file"
                accept="video/mp4,video/webm,video/quicktime,.mkv,.mpeg,.mpg,.avi,.m4v"
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
                    <span className="tb-stepper-iniciar-transcricao-cta">Selecionar arquivo de vídeo</span>
                    <span className="tb-muted">MP4, WebM, MOV, MKV, AVI…</span>
                  </>
                )}
              </button>
            </section>
          ) : (
            <section className="tb-stepper-iniciar-transcricao-corpo" aria-labelledby={`${tituloId}-etapa-destino`}>
              <h3 id={`${tituloId}-etapa-destino`} className="tb-stepper-iniciar-transcricao-etapa-titulo">
                O que fazer com a transcrição?
              </h3>
              <p className="tb-muted tb-stepper-iniciar-transcricao-etapa-lead">
                Escolha como processar este vídeo no Transcribrothers.
              </p>
              {importacaoRecbrothers?.totalCliquesStaging ? (
                <p className="tb-muted tb-stepper-iniciar-transcricao-resumo-arquivo">
                  Registro RecBrothers:{" "}
                  <strong>{importacaoRecbrothers.totalCliquesStaging} clique(s)</strong> no JSON.
                </p>
              ) : null}
              {arquivo ? (
                <p className="tb-stepper-iniciar-transcricao-resumo-arquivo">
                  <span className="tb-muted">Vídeo:</span> <strong>{arquivo.name}</strong> (
                  {formatarTamanhoArquivoMbTranscribrothers(arquivo.size)})
                </p>
              ) : null}
              <div className="tb-stepper-iniciar-transcricao-opcoes-destino" role="radiogroup" aria-label="Destino">
                <label
                  className={`tb-stepper-iniciar-transcricao-opcao-destino${destino === "gerar_tutorial" ? " tb-stepper-iniciar-transcricao-opcao-destino--selecionada" : ""}`}
                >
                  <input
                    type="radio"
                    name="destino-transcricao"
                    value="gerar_tutorial"
                    checked={destino === "gerar_tutorial"}
                    onChange={() => setDestino("gerar_tutorial")}
                  />
                  <span className="tb-stepper-iniciar-transcricao-opcao-titulo">Gerar tutorial</span>
                  <span className="tb-muted tb-stepper-iniciar-transcricao-opcao-desc">
                    {DESCRICAO_DESTINO.gerar_tutorial}
                  </span>
                </label>
                <label
                  className={`tb-stepper-iniciar-transcricao-opcao-destino${destino === "notas_proposta_funcionalidade" ? " tb-stepper-iniciar-transcricao-opcao-destino--selecionada" : ""}`}
                >
                  <input
                    type="radio"
                    name="destino-transcricao"
                    value="notas_proposta_funcionalidade"
                    checked={destino === "notas_proposta_funcionalidade"}
                    onChange={() => setDestino("notas_proposta_funcionalidade")}
                  />
                  <span className="tb-stepper-iniciar-transcricao-opcao-titulo">Notas de proposta</span>
                  <span className="tb-muted tb-stepper-iniciar-transcricao-opcao-desc">
                    {DESCRICAO_DESTINO.notas_proposta_funcionalidade}
                  </span>
                </label>
                <label
                  className={`tb-stepper-iniciar-transcricao-opcao-destino${destino === "reproducao_bug" ? " tb-stepper-iniciar-transcricao-opcao-destino--selecionada" : ""}`}
                >
                  <input
                    type="radio"
                    name="destino-transcricao"
                    value="reproducao_bug"
                    checked={destino === "reproducao_bug"}
                    onChange={() => setDestino("reproducao_bug")}
                  />
                  <span className="tb-stepper-iniciar-transcricao-opcao-titulo">Reproduzir bug</span>
                  <span className="tb-muted tb-stepper-iniciar-transcricao-opcao-desc">
                    {DESCRICAO_DESTINO.reproducao_bug}
                  </span>
                </label>
              </div>
              {destino === "reproducao_bug" && !importadoDoRecbrothers ? (
                <div className="tb-stepper-iniciar-transcricao-anexo-cliques-json">
                  <p className="tb-muted tb-stepper-iniciar-transcricao-etapa-lead">
                    JSON de cliques (opcional): formato RecBrothers com array{" "}
                    <code>cliques</code> e <code>tRelativoMs</code>. Sem arquivo, os passos serão inferidos da
                    transcrição e das capturas de tela.
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
                <button
                  type="button"
                  className="tb-linkbtn"
                  disabled={carregando}
                  onClick={() => setEtapa(0)}
                >
                  Voltar
                </button>
              ) : null}
              {!ehUltimaEtapa ? (
                <button
                  type="button"
                  className="tb-primary"
                  disabled={!podeAvancarEtapaVideo || carregando || carregandoImportacaoRecbrothers}
                  onClick={() => setEtapa(1)}
                >
                  Próximo
                </button>
              ) : (
                <button
                  type="button"
                  className="tb-primary"
                  disabled={
                    !arquivo ||
                    carregando ||
                    carregandoImportacaoRecbrothers ||
                    Boolean(erroImportacaoRecbrothers)
                  }
                  onClick={() => {
                    if (arquivo) {
                      const cliques =
                        destino === "reproducao_bug" && !importadoDoRecbrothers ? arquivoCliquesJson : null;
                      onIniciar(arquivo, destino, cliques);
                    }
                  }}
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
