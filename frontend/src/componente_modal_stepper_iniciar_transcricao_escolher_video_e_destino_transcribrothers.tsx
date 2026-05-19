import { useEffect, useId, useRef, useState } from "react";
import { createPortal } from "react-dom";

export type DestinoAposTranscricaoTranscribrothers = "gerar_tutorial";

const DESCRICAO_DESTINO: Record<DestinoAposTranscricaoTranscribrothers, string> = {
  gerar_tutorial:
    "Transcreve o áudio, captura telas do vídeo e monta um tutorial em Markdown com imagens e links para o tempo no vídeo.",
};

type PropsModalStepperIniciarTranscricaoTranscribrothers = {
  aberto: boolean;
  carregando: boolean;
  onFechar: () => void;
  onIniciar: (arquivo: File, destino: DestinoAposTranscricaoTranscribrothers) => void;
};

function formatarTamanhoArquivoMbTranscribrothers(bytes: number): string {
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export function ModalStepperIniciarTranscricaoEscolherVideoEDestinoTranscribrothers({
  aberto,
  carregando,
  onFechar,
  onIniciar,
}: PropsModalStepperIniciarTranscricaoTranscribrothers) {
  const tituloId = useId();
  const inputVideoRef = useRef<HTMLInputElement | null>(null);
  const [etapa, setEtapa] = useState(0);
  const [arquivo, setArquivo] = useState<File | null>(null);
  const [destino, setDestino] = useState<DestinoAposTranscricaoTranscribrothers>("gerar_tutorial");

  useEffect(() => {
    if (!aberto) return;
    setEtapa(0);
    setArquivo(null);
    setDestino("gerar_tutorial");
  }, [aberto]);

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
          <h2 id={tituloId} className="tb-modal-job-titulo">
            Iniciar transcrição
          </h2>
          <nav className="tb-stepper-iniciar-transcricao" aria-label="Etapas">
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
                Por enquanto há uma opção; outras destinações podem ser adicionadas depois.
              </p>
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
              </div>
            </section>
          )}

          <footer className="tb-stepper-iniciar-transcricao-rodape">
            <button type="button" className="tb-linkbtn" disabled={carregando} onClick={fecharModal}>
              Cancelar
            </button>
            <div className="tb-stepper-iniciar-transcricao-rodape-direita">
              {etapa > 0 ? (
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
                  disabled={!podeAvancarEtapaVideo || carregando}
                  onClick={() => setEtapa(1)}
                >
                  Próximo
                </button>
              ) : (
                <button
                  type="button"
                  className="tb-primary"
                  disabled={!arquivo || carregando}
                  onClick={() => {
                    if (arquivo) onIniciar(arquivo, destino);
                  }}
                >
                  {carregando ? "A iniciar…" : "Iniciar"}
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
