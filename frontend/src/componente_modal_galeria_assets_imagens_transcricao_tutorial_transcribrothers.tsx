import { useCallback, useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { ComponenteDialogoConfirmacaoAcaoDestrutivaOverlayTranscribrothers } from "./componente_dialogo_confirmacao_acao_destrutiva_overlay_transcribrothers.tsx";
import {
  excluirAssetImagemTutorialJobApiTranscribrothers,
  listarAssetsImagensTutorialJobApiTranscribrothers,
  type ItemListaAssetImagemTutorialApiTranscribrothers,
} from "./modulo_api_listar_assets_imagens_tutorial_job_transcribrothers.ts";
import type { JobStatus } from "./tipos_job_status_api_transcribrothers.ts";
import {
  resolverNomeArquivoAssetPngParaExibicaoNoTutorialTranscribrothers,
  urlAssetPngJobParaNomeArquivoTranscribrothers,
} from "./modulo_util_resolver_nome_asset_png_para_exibicao_com_metadados_anotacao_tutorial_transcribrothers.ts";

type PropsModalGaleriaAssetsImagensTranscricaoTutorialTranscribrothers = {
  aberto: boolean;
  jobId: string;
  aoFechar: () => void;
  aoSelecionarImagemParaAnotar: (nomeArquivoOriginal: string) => void;
  aoJobAtualizado: (job: JobStatus) => void;
  aoNotificarToast: (mensagem: string, tipo: "success" | "error" | "info") => void;
  aoAssetExcluido?: (nomeArquivoOriginal: string) => void;
};

type ConfirmacaoExclusaoAssetGaleriaTranscribrothers = {
  nomeArquivoOriginal: string;
  referenciadoNoMarkdown: boolean;
};

function IconeLixeiraExcluirAssetGaleriaTranscribrothers() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M9 3h6l1 2h5v2H3V5h5l1-2zm1 6h2v9h-2V9zm4 0h2v9h-2V9zM7 9h2v9H7V9z"
        fill="currentColor"
      />
    </svg>
  );
}

function MiniaturaAssetImagemTutorialTranscribrothers({
  jobId,
  item,
  aoSelecionar,
  aoSolicitarExcluir,
  excluindo,
}: {
  jobId: string;
  item: ItemListaAssetImagemTutorialApiTranscribrothers;
  aoSelecionar: (nomeArquivoOriginal: string) => void;
  aoSolicitarExcluir: (item: ItemListaAssetImagemTutorialApiTranscribrothers) => void;
  excluindo: boolean;
}) {
  const [forcarOriginalPorErro, setForcarOriginalPorErro] = useState(false);
  const registro = {
    nome_arquivo_original: item.nome_arquivo_original,
    nome_arquivo_anotado: item.nome_arquivo_anotado,
    exibir_no_tutorial: item.exibir_no_tutorial,
    tem_arquivo_anotado: item.tem_arquivo_anotado,
    atualizado_em: item.atualizado_em,
  };
  const nomeExibir = forcarOriginalPorErro
    ? item.nome_arquivo_original
    : resolverNomeArquivoAssetPngParaExibicaoNoTutorialTranscribrothers(
        item.nome_arquivo_original,
        registro,
      );
  const url = urlAssetPngJobParaNomeArquivoTranscribrothers(jobId, nomeExibir);

  return (
    <article className="tb-galeria-assets-item">
      <button
        type="button"
        className="tb-galeria-assets-item-corpo"
        title={`Abrir anotação: ${item.nome_arquivo_original}`}
        aria-label={`Abrir imagem ${item.nome_arquivo_original} no editor de anotação`}
        disabled={excluindo}
        onClick={() => aoSelecionar(item.nome_arquivo_original)}
      >
        <span className="tb-galeria-assets-miniatura">
          <img
            src={url}
            alt=""
            loading="lazy"
            draggable={false}
            onError={() => {
              if (!forcarOriginalPorErro && nomeExibir !== item.nome_arquivo_original) {
                setForcarOriginalPorErro(true);
              }
            }}
          />
        </span>
        <span className="tb-galeria-assets-legenda" title={item.nome_arquivo_original}>
          {item.nome_arquivo_original}
        </span>
        <span className="tb-galeria-assets-badges">
          {item.referenciado_no_markdown ? (
            <span className="tb-galeria-assets-badge tb-galeria-assets-badge--md">No tutorial</span>
          ) : null}
          {item.tem_arquivo_anotado ? (
            <span className="tb-galeria-assets-badge tb-galeria-assets-badge--anotada">Anotada</span>
          ) : null}
        </span>
      </button>
      <button
        type="button"
        className="tb-galeria-assets-btn-excluir"
        title="Excluir imagem do servidor"
        aria-label={`Excluir ${item.nome_arquivo_original}`}
        disabled={excluindo}
        onClick={(evento) => {
          evento.stopPropagation();
          aoSolicitarExcluir(item);
        }}
      >
        <IconeLixeiraExcluirAssetGaleriaTranscribrothers />
      </button>
    </article>
  );
}

function GaleriaAssetsCorpoLista({
  carregando,
  erro,
  itens,
  aoAtualizar,
  aoSelecionar,
  aoSolicitarExcluir,
  processandoExclusao,
  jobId,
}: {
  carregando: boolean;
  erro: string | null;
  itens: ItemListaAssetImagemTutorialApiTranscribrothers[] | null;
  aoAtualizar: () => void;
  aoSelecionar: (nome: string) => void;
  aoSolicitarExcluir: (item: ItemListaAssetImagemTutorialApiTranscribrothers) => void;
  processandoExclusao: boolean;
  jobId: string;
}) {
  return (
    <>
      <div className="tb-galeria-assets-toolbar">
        <button type="button" className="tb-linkbtn" disabled={carregando} onClick={aoAtualizar}>
          {carregando ? "A atualizar…" : "Atualizar lista"}
        </button>
        {itens ? (
          <span className="tb-muted tb-galeria-assets-contagem">
            {itens.length} {itens.length === 1 ? "imagem" : "imagens"}
          </span>
        ) : null}
      </div>
      {erro ? <pre className="tb-err tb-galeria-assets-erro">{erro}</pre> : null}
      {carregando && itens === null ? <p className="tb-muted tb-galeria-assets-loading">A carregar…</p> : null}
      {!carregando && itens && itens.length === 0 ? (
        <p className="tb-muted tb-galeria-assets-vazio">
          Nenhum PNG em <code>assets/</code> para este job ainda. As capturas aparecem após a etapa de screenshots no
          pipeline.
        </p>
      ) : null}
      {itens && itens.length > 0 ? (
        <div className="tb-galeria-assets-grade" role="list">
          {itens.map((item) => (
            <MiniaturaAssetImagemTutorialTranscribrothers
              key={item.nome_arquivo_original}
              jobId={jobId}
              item={item}
              aoSelecionar={aoSelecionar}
              aoSolicitarExcluir={aoSolicitarExcluir}
              excluindo={processandoExclusao}
            />
          ))}
        </div>
      ) : null}
    </>
  );
}

export function ComponenteModalGaleriaAssetsImagensTranscricaoTutorialTranscribrothers({
  aberto,
  jobId,
  aoFechar,
  aoSelecionarImagemParaAnotar,
  aoJobAtualizado,
  aoNotificarToast,
  aoAssetExcluido,
}: PropsModalGaleriaAssetsImagensTranscricaoTutorialTranscribrothers) {
  const [itens, setItens] = useState<ItemListaAssetImagemTutorialApiTranscribrothers[] | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [confirmacaoExclusao, setConfirmacaoExclusao] =
    useState<ConfirmacaoExclusaoAssetGaleriaTranscribrothers | null>(null);
  const [processandoExclusao, setProcessandoExclusao] = useState(false);

  const carregarLista = useCallback(async () => {
    setCarregando(true);
    setErro(null);
    try {
      const lista = await listarAssetsImagensTutorialJobApiTranscribrothers(jobId);
      setItens(lista);
    } catch (e) {
      setItens(null);
      setErro(e instanceof Error ? e.message : String(e));
    } finally {
      setCarregando(false);
    }
  }, [jobId]);

  useEffect(() => {
    if (!aberto) {
      setItens(null);
      setErro(null);
      setConfirmacaoExclusao(null);
      return;
    }
    void carregarLista();
  }, [aberto, carregarLista]);

  const aoSelecionarMiniatura = (nome: string) => {
    aoFechar();
    aoSelecionarImagemParaAnotar(nome);
  };

  const confirmarExclusaoAsset = async () => {
    if (!confirmacaoExclusao) return;
    setProcessandoExclusao(true);
    try {
      const j = await excluirAssetImagemTutorialJobApiTranscribrothers(
        jobId,
        confirmacaoExclusao.nomeArquivoOriginal,
      );
      aoJobAtualizado(j);
      aoAssetExcluido?.(confirmacaoExclusao.nomeArquivoOriginal);
      setConfirmacaoExclusao(null);
      aoNotificarToast(
        confirmacaoExclusao.referenciadoNoMarkdown
          ? "Imagem excluída e referência removida do tutorial."
          : "Imagem excluída do servidor.",
        "success",
      );
      await carregarLista();
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e);
      aoNotificarToast(msg, "error");
    } finally {
      setProcessandoExclusao(false);
    }
  };

  const mensagemConfirmacaoExclusao = confirmacaoExclusao
    ? confirmacaoExclusao.referenciadoNoMarkdown
      ? `O arquivo «${confirmacaoExclusao.nomeArquivoOriginal}» será excluído do servidor (captura original e versão anotada, se existir). Esta imagem está referenciada no tutorial em Markdown — a linha ![](assets/…) e o link de tempo do vídeo logo abaixo, se houver, também serão removidos.`
      : `O arquivo «${confirmacaoExclusao.nomeArquivoOriginal}» será excluído permanentemente do servidor (captura original e versão anotada, se existir). Não consta no tutorial em Markdown.`
    : "";

  if (!aberto) return null;

  return createPortal(
    <>
      <div className="tb-modal-job-root" role="presentation">
        <button
          type="button"
          className="tb-modal-job-backdrop"
          aria-label="Fechar galeria de assets"
          onClick={aoFechar}
        />
        <div className="tb-modal-job-shell tb-modal-job-shell-galeria-assets">
          <div
            className="tb-modal-job tb-modal-galeria-assets"
            role="dialog"
            aria-modal="true"
            aria-labelledby="tb-modal-galeria-assets-titulo"
          >
            <h2 id="tb-modal-galeria-assets-titulo" className="tb-modal-job-titulo">
              Assets da transcrição
            </h2>
            <p className="tb-muted tb-galeria-assets-intro">
              Capturas PNG geradas a partir do vídeo. Clique na miniatura para anotar; use a lixeira para excluir do
              servidor.
            </p>
            <GaleriaAssetsCorpoLista
              carregando={carregando}
              erro={erro}
              itens={itens}
              aoAtualizar={() => void carregarLista()}
              aoSelecionar={aoSelecionarMiniatura}
              aoSolicitarExcluir={(item) =>
                setConfirmacaoExclusao({
                  nomeArquivoOriginal: item.nome_arquivo_original,
                  referenciadoNoMarkdown: item.referenciado_no_markdown,
                })
              }
              processandoExclusao={processandoExclusao}
              jobId={jobId}
            />
            <footer className="tb-modal-job-rodape">
              <div className="tb-modal-job-acoes-finais">
                <button type="button" className="tb-btn tb-btn-secundario" onClick={aoFechar}>
                  Fechar
                </button>
              </div>
            </footer>
          </div>
        </div>
      </div>

      <ComponenteDialogoConfirmacaoAcaoDestrutivaOverlayTranscribrothers
        aberto={confirmacaoExclusao !== null}
        titulo="Excluir imagem?"
        mensagem={mensagemConfirmacaoExclusao}
        rotuloConfirmar="Excluir"
        rotuloCancelar="Cancelar"
        processando={processandoExclusao}
        aoConfirmar={() => void confirmarExclusaoAsset()}
        aoCancelar={() => {
          if (!processandoExclusao) setConfirmacaoExclusao(null);
        }}
      />
    </>,
    document.body,
  );
}
