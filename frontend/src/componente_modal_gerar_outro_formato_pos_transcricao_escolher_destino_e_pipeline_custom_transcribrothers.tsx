import { useEffect, useId, useState } from "react";
import { createPortal } from "react-dom";

import type { PipelineCatalogoApiTranscribrothers } from "./tipos_catalogo_pipelines_api_transcribrothers.ts";
import { filtrarEOrdenarPipelinesCustomExecutaveisCatalogoTranscribrothers } from "./modulo_util_ordenar_e_filtrar_pipelines_custom_executaveis_catalogo_transcribrothers.ts";
import type { DestinoAposTranscricaoTranscribrothers } from "./modulo_constante_destino_apos_transcricao_e_rotulo_frame_documento_transcribrothers.ts";

const DESCRICAO_DESTINO: Record<
  Exclude<DestinoAposTranscricaoTranscribrothers, "projeto_em_branco" | "so_transcricao">,
  string
> = {
  gerar_tutorial:
    "Gera tutorial em Markdown com capturas e links para o tempo no vídeo, reutilizando a transcrição já feita.",
  reproducao_bug:
    "Monta passo a passo de reprodução do bug com capturas. Com JSON de cliques no job, alinha aos cliques; sem JSON, infere passos da transcrição.",
  notas_proposta_funcionalidade:
    "Gera notas estruturadas (contexto, proposta, decisões, pendências) com links para o vídeo e capturas, sem retranscrever.",
};

const MAPEAMENTO_PIPELINE_SISTEMA_COPIADO_DE_PARA_DESTINO_TRANSCRIBROTHERS: Record<
  string,
  Exclude<DestinoAposTranscricaoTranscribrothers, "projeto_em_branco" | "so_transcricao">
> = {
  pipeline_inicial_tutorial: "gerar_tutorial",
  pipeline_inicial_notas_proposta: "notas_proposta_funcionalidade",
  pipeline_inicial_reproducao_bug: "reproducao_bug",
};

type DestinoGerarOutroFormatoTranscribrothers = Exclude<
  DestinoAposTranscricaoTranscribrothers,
  "projeto_em_branco" | "so_transcricao"
>;

type PropsModalGerarOutroFormatoPosTranscricaoTranscribrothers = {
  aberto: boolean;
  carregando: boolean;
  destinoAtual: DestinoAposTranscricaoTranscribrothers;
  jobTemCliquesReproducaoBug: boolean;
  /** Jobs só com áudio só podem gerar notas nesta versão. */
  jobTipoEntradaMidia?: "video" | "audio" | null;
  /** Transcrição importada (sem mídia): só notas nesta versão. */
  jobTranscricaoImportada?: boolean;
  onFechar: () => void;
  onConfirmar: (
    destino: DestinoGerarOutroFormatoTranscribrothers,
    pipelineCustomId?: string | null,
  ) => void;
};

export function ModalGerarOutroFormatoPosTranscricaoEscolherDestinoEPipelineCustomTranscribrothers({
  aberto,
  carregando,
  destinoAtual,
  jobTemCliquesReproducaoBug,
  jobTipoEntradaMidia = null,
  jobTranscricaoImportada = false,
  onFechar,
  onConfirmar,
}: PropsModalGerarOutroFormatoPosTranscricaoTranscribrothers) {
  const tituloId = useId();
  const soNotas =
    jobTipoEntradaMidia === "audio" || jobTranscricaoImportada;
  const [destino, setDestino] = useState<DestinoGerarOutroFormatoTranscribrothers>("gerar_tutorial");
  const [pipelineCustomId, setPipelineCustomId] = useState<string | null>(null);
  const [pipelinesCustomExecutaveis, setPipelinesCustomExecutaveis] = useState<PipelineCatalogoApiTranscribrothers[]>(
    [],
  );

  const destinosDisponiveis: DestinoGerarOutroFormatoTranscribrothers[] = soNotas
    ? ["notas_proposta_funcionalidade"]
    : ["gerar_tutorial", "notas_proposta_funcionalidade", "reproducao_bug"];

  useEffect(() => {
    if (!aberto) return;
    void fetch("/api/pipelines/catalogo")
      .then((r) => r.json())
      .then((d: { pipelines?: PipelineCatalogoApiTranscribrothers[] }) => {
        let custom = filtrarEOrdenarPipelinesCustomExecutaveisCatalogoTranscribrothers(d.pipelines ?? []);
        if (soNotas) {
          custom = custom.filter((p) => p.copiado_de === "pipeline_inicial_notas_proposta");
        }
        setPipelinesCustomExecutaveis(custom);
      })
      .catch(() => setPipelinesCustomExecutaveis([]));
  }, [aberto, soNotas]);

  useEffect(() => {
    if (!aberto) return;
    setPipelineCustomId(null);
    if (soNotas) {
      setDestino("notas_proposta_funcionalidade");
      return;
    }
    if (destinoAtual === "projeto_em_branco" || destinoAtual === "so_transcricao") {
      setDestino("gerar_tutorial");
      return;
    }
    const alternativas: DestinoGerarOutroFormatoTranscribrothers[] = [
      "gerar_tutorial",
      "notas_proposta_funcionalidade",
      "reproducao_bug",
    ];
    const primeiraDiferente = alternativas.find((d) => d !== destinoAtual);
    setDestino(primeiraDiferente ?? "gerar_tutorial");
  }, [aberto, destinoAtual, soNotas]);

  if (!aberto) return null;

  const destinoEfetivo = pipelineCustomId
    ? (() => {
        const pipeline = pipelinesCustomExecutaveis.find((p) => p.id === pipelineCustomId);
        const copiadoDe = pipeline?.copiado_de?.trim();
        if (copiadoDe && MAPEAMENTO_PIPELINE_SISTEMA_COPIADO_DE_PARA_DESTINO_TRANSCRIBROTHERS[copiadoDe]) {
          return MAPEAMENTO_PIPELINE_SISTEMA_COPIADO_DE_PARA_DESTINO_TRANSCRIBROTHERS[copiadoDe];
        }
        return destino;
      })()
    : destino;

  const destinoIgualAoAtual =
    !pipelineCustomId && destino === destinoAtual && destinoAtual !== "projeto_em_branco";

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
      <div className="tb-modal-job-shell">
        <div className="tb-modal-job" role="dialog" aria-modal="true" aria-labelledby={tituloId}>
          <header className="tb-stepper-iniciar-transcricao-cabecalho">
            <h2 id={tituloId} className="tb-modal-job-titulo">
              Gerar outro formato
            </h2>
            <p className="tb-muted tb-stepper-iniciar-transcricao-lead-modal">
              O documento atual será guardado no histórico de versões. A transcrição existente será reutilizada — não
              haverá novo upload nem retranscrição.
            </p>
          </header>

          <div className="tb-stepper-iniciar-transcricao-corpo-rolavel">
            <section className="tb-stepper-iniciar-transcricao-corpo" aria-labelledby={`${tituloId}-destino`}>
              <h3 id={`${tituloId}-destino`} className="tb-stepper-iniciar-transcricao-etapa-titulo">
                Novo destino pós-transcrição
              </h3>
              {soNotas ? (
                <p className="tb-muted" role="note">
                  {jobTranscricaoImportada
                    ? "Este job veio de uma transcrição importada (sem vídeo): nesta versão só é possível gerar notas de proposta."
                    : "Este job foi iniciado só com áudio: nesta versão só é possível gerar notas de proposta."}
                </p>
              ) : null}
              <div className="tb-stepper-iniciar-transcricao-opcoes-destino" role="radiogroup" aria-label="Destino">
                {(
                  [
                    ["gerar_tutorial", "Gerar tutorial"],
                    ["notas_proposta_funcionalidade", "Notas de proposta"],
                    ["reproducao_bug", "Reproduzir bug"],
                  ] as const
                )
                  .filter(([valor]) => destinosDisponiveis.includes(valor))
                  .map(([valor, rotulo]) => (
                    <label
                      key={valor}
                      className={`tb-stepper-iniciar-transcricao-opcao-destino${destino === valor && !pipelineCustomId ? " tb-stepper-iniciar-transcricao-opcao-destino--selecionada" : ""}`}
                    >
                      <input
                        type="radio"
                        name="destino-gerar-outro-formato"
                        value={valor}
                        checked={destino === valor && !pipelineCustomId}
                        onChange={() => {
                          setDestino(valor);
                          setPipelineCustomId(null);
                        }}
                      />
                      <span className="tb-stepper-iniciar-transcricao-opcao-titulo">{rotulo}</span>
                      <span className="tb-muted tb-stepper-iniciar-transcricao-opcao-desc">
                        {DESCRICAO_DESTINO[valor]}
                      </span>
                      {valor === destinoAtual ? (
                        <span className="tb-muted tb-stepper-iniciar-transcricao-opcao-desc">(formato atual)</span>
                      ) : null}
                    </label>
                  ))}
              </div>

              {destinoEfetivo === "reproducao_bug" && !jobTemCliquesReproducaoBug ? (
                <p className="tb-muted" role="note">
                  Este job não possui JSON de cliques. O fluxo de bug ainda pode rodar inferindo passos da transcrição
                  e das telas.
                </p>
              ) : null}

              {pipelinesCustomExecutaveis.length > 0 ? (
                <div className="tb-stepper-iniciar-transcricao-pipelines-custom">
                  <h4 className="tb-stepper-iniciar-transcricao-etapa-titulo">Pipelines customizadas</h4>
                  <div
                    className="tb-stepper-iniciar-transcricao-opcoes-destino"
                    role="radiogroup"
                    aria-label="Pipeline custom"
                  >
                    {pipelinesCustomExecutaveis.map((p) => (
                      <label
                        key={p.id}
                        className={`tb-stepper-iniciar-transcricao-opcao-destino${pipelineCustomId === p.id ? " tb-stepper-iniciar-transcricao-opcao-destino--selecionada" : ""}`}
                      >
                        <input
                          type="radio"
                          name="destino-gerar-outro-formato"
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
                        {p.descricao ? (
                          <span className="tb-muted tb-stepper-iniciar-transcricao-opcao-desc">{p.descricao}</span>
                        ) : null}
                      </label>
                    ))}
                  </div>
                </div>
              ) : null}
            </section>
          </div>

          <footer className="tb-modal-job-rodape">
            <button type="button" className="tb-btn-secundario" disabled={carregando} onClick={fecharModal}>
              Cancelar
            </button>
            <button
              type="button"
              className="tb-btn-primario"
              disabled={carregando || destinoIgualAoAtual}
              onClick={() => onConfirmar(destinoEfetivo, pipelineCustomId)}
            >
              {carregando ? "Agendando…" : "Gerar outro formato"}
            </button>
          </footer>
        </div>
      </div>
    </div>,
    document.body,
  );
}
