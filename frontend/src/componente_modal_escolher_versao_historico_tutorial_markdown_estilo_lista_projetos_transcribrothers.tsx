import { createPortal } from "react-dom";
import { montarRotuloVersaoHistoricoTutorialMarkdownParaSelectUiTranscribrothers } from "./modulo_util_rotulo_numero_versao_historico_tutorial_markdown_por_projeto_transcribrothers.ts";
import "./estilos_css_modal_escolher_versao_historico_tutorial_markdown_transcribrothers.css";

export type ResumoVersaoHistoricoTutorialMarkdownModalTranscribrothers = {
  id: number;
  criado_em: string | null;
  origem: string;
  preview_linha: string;
};

export type PropsComponenteModalEscolherVersaoHistoricoTutorialMarkdownEstiloListaProjetosTranscribrothers =
  {
    aberta: boolean;
    onFechar: () => void;
    versaoHistoricoSelecionadaId: number | null;
    onEscolherVersao: (historicoId: number | null) => void;
    listaVersoes: ResumoVersaoHistoricoTutorialMarkdownModalTranscribrothers[] | null;
    carregandoLista: boolean;
    rotuloVersaoAtualServidor: string;
    dataHoraVersaoAtualServidor: string | null;
    formatarDataHora: (iso: string | null) => string;
    obterRotuloOrigemPortugues: (origem: string) => string;
  };

export function ComponenteModalEscolherVersaoHistoricoTutorialMarkdownEstiloListaProjetosTranscribrothers({
  aberta,
  onFechar,
  versaoHistoricoSelecionadaId,
  onEscolherVersao,
  listaVersoes,
  carregandoLista,
  rotuloVersaoAtualServidor,
  dataHoraVersaoAtualServidor,
  formatarDataHora,
  obterRotuloOrigemPortugues,
}: PropsComponenteModalEscolherVersaoHistoricoTutorialMarkdownEstiloListaProjetosTranscribrothers) {
  if (!aberta) {
    return null;
  }

  const total = listaVersoes?.length ?? 0;
  const versaoAtualServidorSelecionada = versaoHistoricoSelecionadaId === null;

  const escolherEFechar = (historicoId: number | null) => {
    onEscolherVersao(historicoId);
    onFechar();
  };

  return createPortal(
    <div className="tb-modal-job-root" role="presentation">
      <button
        type="button"
        className="tb-modal-job-backdrop"
        aria-label="Fechar histórico de versões"
        onClick={onFechar}
      />
      <div className="tb-modal-job-shell tb-modal-job-shell-historico-versoes-tutorial">
        <div
          className="tb-modal-job tb-modal-historico-versoes-tutorial"
          role="dialog"
          aria-modal="true"
          aria-labelledby="tb-modal-historico-versoes-tutorial-titulo"
        >
          <h2 id="tb-modal-historico-versoes-tutorial-titulo" className="tb-modal-job-titulo">
            Histórico do tutorial
          </h2>
          <p className="tb-muted tb-modal-historico-versoes-intro">
            Escolha uma versão guardada neste projeto ou volte à versão atual no servidor. Ao visualizar uma
            versão antiga, use <strong>Restaurar esta versão</strong> no aviso amarelo abaixo do documento.
          </p>

          {carregandoLista && listaVersoes === null ? (
            <p className="tb-muted tb-modal-historico-versoes-loading">A carregar versões…</p>
          ) : null}

          <ul className="tb-modal-historico-versoes-lista" role="listbox" aria-label="Versões do tutorial">
            <li role="presentation">
              <button
                type="button"
                role="option"
                aria-selected={versaoAtualServidorSelecionada}
                className={[
                  "tb-modal-historico-versoes-item",
                  versaoAtualServidorSelecionada ? "tb-modal-historico-versoes-item--selecionada" : "",
                ]
                  .filter(Boolean)
                  .join(" ")}
                onClick={() => escolherEFechar(null)}
              >
                <span className="tb-modal-historico-versoes-item-titulo">{rotuloVersaoAtualServidor}</span>
                {dataHoraVersaoAtualServidor ? (
                  <span className="tb-muted tb-modal-historico-versoes-item-meta">
                    {dataHoraVersaoAtualServidor}
                  </span>
                ) : null}
                <span className="tb-muted tb-modal-historico-versoes-item-preview">
                  Markdown gravado no servidor agora (edições, regenerações e restaurações).
                </span>
              </button>
            </li>

            {(listaVersoes ?? []).map((row, indice) => {
              const rótuloData = formatarDataHora(row.criado_em);
              const rótuloOrigem = obterRotuloOrigemPortugues(row.origem);
              const trunc =
                row.preview_linha.length > 80
                  ? `${row.preview_linha.slice(0, 79)}…`
                  : row.preview_linha;
              const { textoOpcao } = montarRotuloVersaoHistoricoTutorialMarkdownParaSelectUiTranscribrothers({
                indiceNaListaDesc: indice,
                totalVersoesNoProjeto: total,
                criadoEmFormatado: rótuloData,
                rotuloOrigemPortugues: rótuloOrigem,
                previewLinhaTruncada: trunc,
                idInternoSqlite: row.id,
              });
              const selecionada = versaoHistoricoSelecionadaId === row.id;
              return (
                <li key={row.id} role="presentation">
                  <button
                    type="button"
                    role="option"
                    aria-selected={selecionada}
                    className={[
                      "tb-modal-historico-versoes-item",
                      selecionada ? "tb-modal-historico-versoes-item--selecionada" : "",
                    ]
                      .filter(Boolean)
                      .join(" ")}
                    onClick={() => escolherEFechar(row.id)}
                  >
                    <span className="tb-modal-historico-versoes-item-titulo">{textoOpcao}</span>
                    {trunc ? (
                      <span className="tb-muted tb-modal-historico-versoes-item-preview">{trunc}</span>
                    ) : null}
                  </button>
                </li>
              );
            })}
          </ul>

          {listaVersoes && listaVersoes.length === 0 && !carregandoLista ? (
            <p className="tb-muted tb-modal-historico-versoes-vazio">
              Ainda não há snapshots no histórico (aparecem após o pipeline, regenerações ou uma edição gravada com
              texto novo).
            </p>
          ) : null}

          <div className="tb-modal-historico-versoes-rodape">
            <button type="button" className="tb-primary" onClick={onFechar}>
              Fechar
            </button>
          </div>
        </div>
      </div>
    </div>,
    document.body,
  );
}
