import { useMemo, useState } from "react";
import {
  calcularResumoAlteracoesTextoMarkdownAntesDepoisTranscribrothers,
  montarLinhasDiffUnificadoMarkdownAntesDepoisTranscribrothers,
  montarParesColunasDiffLadoALadoMarkdownAntesDepoisTranscribrothers,
} from "./modulo_util_calcular_resumo_alteracoes_texto_markdown_antes_depois_transcribrothers.ts";

export type ModoVisualizacaoComparacaoMarkdownAntesDepoisTranscribrothers =
  | "lado_a_lado"
  | "diff_unificado"
  | "somente_alteracoes";

type PropsComparacaoMarkdownAntesDepoisVisualizacaoDiffTranscribrothers = {
  rotuloBloco: string;
  textoAntes: string;
  textoDepois: string;
  rotuloColunaAntes?: string;
  rotuloColunaDepois?: string;
  className?: string;
};

function montarTextoResumoAlteracoesPortuguesTranscribrothers(
  resumo: ReturnType<typeof calcularResumoAlteracoesTextoMarkdownAntesDepoisTranscribrothers>,
): string {
  if (resumo.textoIgual) {
    return "Nenhuma alteração de texto detectada entre «antes» e «depois».";
  }
  const partes: string[] = [];
  if (resumo.linhasRemovidas > 0) partes.push(`${resumo.linhasRemovidas} linha(s) removida(s)`);
  if (resumo.linhasAdicionadas > 0) partes.push(`${resumo.linhasAdicionadas} linha(s) adicionada(s)`);
  if (partes.length === 0) partes.push("texto reformulado (mesmo tamanho aproximado)");
  let s = partes.join(", ");
  s += ` — ${resumo.linhasAntes} → ${resumo.linhasDepois} linhas`;
  if (resumo.secoesHeadingAlteradas.length > 0) {
    s += ` · ${resumo.secoesHeadingAlteradas.length} seção(ões) ## tocada(s)`;
  }
  if (resumo.imagensAdicionadas > 0 || resumo.imagensRemovidas > 0) {
    const img: string[] = [];
    if (resumo.imagensAdicionadas > 0) img.push(`+${resumo.imagensAdicionadas} img`);
    if (resumo.imagensRemovidas > 0) img.push(`-${resumo.imagensRemovidas} img`);
    s += ` · ${img.join(", ")}`;
  }
  return s;
}

export function ComponenteComparacaoMarkdownAntesDepoisVisualizacaoDiffELadoALadoTranscribrothers({
  rotuloBloco,
  textoAntes,
  textoDepois,
  rotuloColunaAntes = "Antes",
  rotuloColunaDepois = "Depois (proposta)",
  className = "",
}: PropsComparacaoMarkdownAntesDepoisVisualizacaoDiffTranscribrothers) {
  const [modo, setModo] = useState<ModoVisualizacaoComparacaoMarkdownAntesDepoisTranscribrothers>("lado_a_lado");

  const resumo = useMemo(
    () => calcularResumoAlteracoesTextoMarkdownAntesDepoisTranscribrothers(textoAntes, textoDepois),
    [textoAntes, textoDepois],
  );

  const linhasUnificado = useMemo(
    () =>
      montarLinhasDiffUnificadoMarkdownAntesDepoisTranscribrothers(textoAntes, textoDepois, {
        somenteAlteracoes: modo === "somente_alteracoes",
      }),
    [textoAntes, textoDepois, modo],
  );

  const paresLadoALado = useMemo(
    () => montarParesColunasDiffLadoALadoMarkdownAntesDepoisTranscribrothers(textoAntes, textoDepois),
    [textoAntes, textoDepois],
  );

  const textoResumo = montarTextoResumoAlteracoesPortuguesTranscribrothers(resumo);

  return (
    <section className={`tb-comparacao-md ${className}`.trim()} aria-label={rotuloBloco}>
      <div className="tb-comparacao-md-cabecalho">
        <h3 className="tb-comparacao-md-titulo-bloco">{rotuloBloco}</h3>
        <div className="tb-comparacao-md-modos" role="tablist" aria-label="Modo de comparação">
          <button
            type="button"
            role="tab"
            aria-selected={modo === "lado_a_lado"}
            className={`tb-comparacao-md-modo-btn${modo === "lado_a_lado" ? " tb-comparacao-md-modo-btn--ativo" : ""}`}
            onClick={() => setModo("lado_a_lado")}
          >
            Lado a lado
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={modo === "diff_unificado"}
            className={`tb-comparacao-md-modo-btn${modo === "diff_unificado" ? " tb-comparacao-md-modo-btn--ativo" : ""}`}
            onClick={() => setModo("diff_unificado")}
          >
            Diff
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={modo === "somente_alteracoes"}
            className={`tb-comparacao-md-modo-btn${modo === "somente_alteracoes" ? " tb-comparacao-md-modo-btn--ativo" : ""}`}
            onClick={() => setModo("somente_alteracoes")}
          >
            Só mudanças
          </button>
        </div>
      </div>

      <div
        role="status"
        className={`tb-comparacao-md-resumo${resumo.textoIgual ? " tb-comparacao-md-resumo--igual" : " tb-comparacao-md-resumo--alterado"}`}
      >
        <strong>{resumo.textoIgual ? "Sem alterações" : "Alterações detectadas"}</strong>
        <span className="tb-comparacao-md-resumo-detalhe"> — {textoResumo}</span>
      </div>

      {modo === "lado_a_lado" ? (
        <div className="tb-comparacao-md-split">
          <div className="tb-comparacao-md-split-cabecalho">
            <span className="tb-comparacao-md-split-col-titulo">{rotuloColunaAntes}</span>
            <span className="tb-comparacao-md-split-col-titulo">{rotuloColunaDepois}</span>
          </div>
          <div className="tb-comparacao-md-split-corpo">
            {paresLadoALado.map((par, idx) => (
              <div
                key={idx}
                className={`tb-comparacao-md-split-linha tb-comparacao-md-split-linha--${par.tipo}`}
              >
                <pre className="tb-comparacao-md-linha-pre">{par.esquerda ?? ""}</pre>
                <pre className="tb-comparacao-md-linha-pre">{par.direita ?? ""}</pre>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="tb-comparacao-md-diff-unificado" role="region" aria-label="Diff unificado">
          {linhasUnificado.map((linha, idx) =>
            linha.omitida ? (
              <div key={idx} className="tb-comparacao-md-diff-omitido">
                … {linha.rotuloOmitida ?? "trecho oculto"} …
              </div>
            ) : (
              <div
                key={idx}
                className={`tb-comparacao-md-diff-linha tb-comparacao-md-diff-linha--${linha.tipo}`}
              >
                <span className="tb-comparacao-md-diff-prefixo" aria-hidden>
                  {linha.tipo === "adicionada" ? "+" : linha.tipo === "removida" ? "−" : " "}
                </span>
                <span className="tb-comparacao-md-diff-texto">{linha.texto || " "}</span>
              </div>
            ),
          )}
        </div>
      )}
    </section>
  );
}
