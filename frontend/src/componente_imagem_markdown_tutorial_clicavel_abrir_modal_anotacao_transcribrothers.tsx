import type * as React from "react";
import { useEffect, useState } from "react";
import type { RegistroAnotacaoImagemTutorialApiTranscribrothers } from "./modulo_api_anotacao_imagens_tutorial_assets_png_duas_versoes_transcribrothers.ts";
import {
  resolverNomeArquivoAssetPngParaExibicaoNoTutorialTranscribrothers,
  urlAssetPngJobParaNomeArquivoTranscribrothers,
} from "./modulo_util_resolver_nome_asset_png_para_exibicao_com_metadados_anotacao_tutorial_transcribrothers.ts";

type PropsImagemMarkdownTutorialClicavelAbrirModalAnotacaoTranscribrothers = {
  jobId: string;
  nomeArquivoOriginal: string;
  registroAnotacao?: RegistroAnotacaoImagemTutorialApiTranscribrothers;
  alt?: string;
  imgProps?: React.ImgHTMLAttributes<HTMLImageElement>;
  aoClicarAbrirEditor: (nomeArquivoOriginal: string) => void;
  aoSolicitarExcluirImagemDoTutorial?: (
    nomeArquivoOriginal: string,
    rotuloImagem: string,
  ) => void;
};

function IconeLixeiraExcluirImagemTutorialTranscribrothers() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M9 3h6l1 2h5v2H3V5h5l1-2zm1 6h2v9h-2V9zm4 0h2v9h-2V9zM7 9h2v9H7V9z"
        fill="currentColor"
      />
    </svg>
  );
}

export function ComponenteImagemMarkdownTutorialClicavelAbrirModalAnotacaoTranscribrothers({
  jobId,
  nomeArquivoOriginal,
  registroAnotacao,
  alt,
  imgProps,
  aoClicarAbrirEditor,
  aoSolicitarExcluirImagemDoTutorial,
}: PropsImagemMarkdownTutorialClicavelAbrirModalAnotacaoTranscribrothers) {
  const [cacheBust, setCacheBust] = useState(0);
  const [forcarOriginalPorFalhaCarregamento, setForcarOriginalPorFalhaCarregamento] = useState(false);

  useEffect(() => {
    setForcarOriginalPorFalhaCarregamento(false);
    setCacheBust(0);
  }, [nomeArquivoOriginal, registroAnotacao?.exibir_no_tutorial, registroAnotacao?.nome_arquivo_anotado]);

  const nomeExibirResolvido = resolverNomeArquivoAssetPngParaExibicaoNoTutorialTranscribrothers(
    nomeArquivoOriginal,
    registroAnotacao,
  );
  const nomeExibir = forcarOriginalPorFalhaCarregamento ? nomeArquivoOriginal : nomeExibirResolvido;
  const url =
    urlAssetPngJobParaNomeArquivoTranscribrothers(jobId, nomeExibir) +
    (cacheBust ? `?v=${cacheBust}` : "");

  const exibindoAnotado =
    registroAnotacao?.tem_arquivo_anotado && registroAnotacao.exibir_no_tutorial === "anotado";

  const rotuloImagem = alt?.trim() || nomeArquivoOriginal;
  const { onClick: _ignorarOnClickImg, ...restImgProps } = imgProps ?? {};

  return (
    <div
      className="tb-imagem-tutorial-clicavel-envoltorio"
      data-tb-nome-arquivo-asset-original={nomeArquivoOriginal}
    >
      <button
        type="button"
        className="tb-imagem-tutorial-clicavel-anotacao"
        title="Clique para anotar ou editar esta imagem"
        aria-label={
          registroAnotacao?.tem_arquivo_anotado
            ? `Editar anotação da imagem: ${rotuloImagem}`
            : `Anotar imagem: ${rotuloImagem}`
        }
        onClick={() => aoClicarAbrirEditor(nomeArquivoOriginal)}
      >
        <img
          {...restImgProps}
          alt={alt ?? ""}
          src={url}
          draggable={false}
          onLoad={() => {
            if (cacheBust === 0 && exibindoAnotado) setCacheBust(Date.now());
          }}
          onError={() => {
            if (nomeExibir !== nomeArquivoOriginal && !forcarOriginalPorFalhaCarregamento) {
              setForcarOriginalPorFalhaCarregamento(true);
              setCacheBust(Date.now());
            }
          }}
        />
        {registroAnotacao?.tem_arquivo_anotado ? (
          <span className="tb-imagem-tutorial-clicavel-indicador" aria-hidden>
            {exibindoAnotado ? "Anotada" : "Original"}
          </span>
        ) : null}
        <span className="tb-imagem-tutorial-clicavel-dica" aria-hidden>
          Clique para anotar
        </span>
      </button>

      {aoSolicitarExcluirImagemDoTutorial ? (
        <button
          type="button"
          className="tb-imagem-tutorial-clicavel-btn-excluir"
          title="Remover imagem do tutorial"
          aria-label={`Remover do tutorial: ${rotuloImagem}`}
          onClick={(evento) => {
            evento.preventDefault();
            evento.stopPropagation();
            aoSolicitarExcluirImagemDoTutorial(nomeArquivoOriginal, rotuloImagem);
          }}
        >
          <IconeLixeiraExcluirImagemTutorialTranscribrothers />
        </button>
      ) : null}
    </div>
  );
}
