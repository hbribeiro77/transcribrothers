import { useCallback, useEffect, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { ComponenteDialogoConfirmacaoAcaoDestrutivaOverlayTranscribrothers } from "./componente_dialogo_confirmacao_acao_destrutiva_overlay_transcribrothers.tsx";
import {
  excluirAssetImagemTutorialJobApiTranscribrothers,
  listarAssetsImagensTutorialJobApiTranscribrothers,
  type ItemListaAssetImagemTutorialApiTranscribrothers,
} from "./modulo_api_listar_assets_imagens_tutorial_job_transcribrothers.ts";
import {
  apagarVersaoVideoNarradoJobApiTranscribrothers,
  listarVersoesVideoNarradoJobApiTranscribrothers,
  tornarVersaoVideoNarradoAtualJobApiTranscribrothers,
  type MetaVersaoVideoNarradoApiTranscribrothers,
} from "./modulo_api_listar_versoes_video_narrado_job_transcribrothers.ts";
import {
  limparCacheMidiaFonteJobApiTranscribrothers,
  listarMidiaFonteJobApiTranscribrothers,
  type ItemMidiaFonteJobApiTranscribrothers,
} from "./modulo_api_midia_fonte_job_transcribrothers.ts";
import type { JobStatus } from "./tipos_job_status_api_transcribrothers.ts";
import {
  resolverNomeArquivoAssetPngParaExibicaoNoTutorialTranscribrothers,
  urlAssetPngJobParaNomeArquivoTranscribrothers,
} from "./modulo_util_resolver_nome_asset_png_para_exibicao_com_metadados_anotacao_tutorial_transcribrothers.ts";

type AbaGaleriaAssetsTranscribrothers = "imagens" | "videos" | "fonte";

function formatarTamanhoBytesGaleriaAssetsTranscribrothers(bytes: number): string {
  const n = Math.max(0, Number(bytes) || 0);
  if (n < 1024) return `${n} B`;
  const kb = n / 1024;
  if (kb < 1024) return `${kb < 10 ? kb.toFixed(1) : Math.round(kb)} KB`;
  const mb = kb / 1024;
  if (mb < 1024) return `${mb < 10 ? mb.toFixed(1) : Math.round(mb)} MB`;
  const gb = mb / 1024;
  return `${gb < 10 ? gb.toFixed(2) : gb.toFixed(1)} GB`;
}

type PropsModalGaleriaAssetsImagensTranscricaoTutorialTranscribrothers = {
  aberto: boolean;
  jobId: string;
  aoFechar: () => void;
  aoSelecionarImagemParaAnotar: (nomeArquivoOriginal: string) => void;
  aoJobAtualizado: (job: JobStatus) => void;
  aoNotificarToast: (mensagem: string, tipo: "success" | "error" | "info") => void;
  aoAssetExcluido?: (nomeArquivoOriginal: string) => void;
  aoAbrirEdicaoVideoNarrado?: () => void;
};

type ConfirmacaoExclusaoAssetGaleriaTranscribrothers = {
  nomeArquivoOriginal: string;
  referenciadoNoMarkdown: boolean;
};

type ConfirmacaoExclusaoVersaoVideoTranscribrothers = {
  versaoId: string;
  ehAtual: boolean;
  unicaVersao: boolean;
};

function IconeSvgGaleriaToolbarTranscribrothers({ children }: { children: ReactNode }) {
  return (
    <svg className="tb-icone-header-toolbar" viewBox="0 0 24 24" aria-hidden="true" width="16" height="16">
      {children}
    </svg>
  );
}

function IconeLixeiraExcluirAssetGaleriaTranscribrothers() {
  return (
    <IconeSvgGaleriaToolbarTranscribrothers>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
      />
    </IconeSvgGaleriaToolbarTranscribrothers>
  );
}

function IconeEditarVideoNarradoGaleriaTranscribrothers() {
  return (
    <IconeSvgGaleriaToolbarTranscribrothers>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
      />
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    </IconeSvgGaleriaToolbarTranscribrothers>
  );
}

function IconeBaixarVideoNarradoGaleriaTranscribrothers() {
  return (
    <IconeSvgGaleriaToolbarTranscribrothers>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
      />
    </IconeSvgGaleriaToolbarTranscribrothers>
  );
}

function IconeLimparCacheFonteGaleriaTranscribrothers() {
  return (
    <IconeSvgGaleriaToolbarTranscribrothers>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
      />
    </IconeSvgGaleriaToolbarTranscribrothers>
  );
}

function IconeTornarAtualVideoNarradoGaleriaTranscribrothers() {
  return (
    <IconeSvgGaleriaToolbarTranscribrothers>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
      />
    </IconeSvgGaleriaToolbarTranscribrothers>
  );
}

function formatarDuracaoSegundosTranscribrothers(segundos: number): string {
  const s = Math.max(0, Math.round(Number(segundos) || 0));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${m}:${String(r).padStart(2, "0")}`;
}

function formatarDataIsoCurtaTranscribrothers(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso || "—";
  return d.toLocaleString("pt-BR", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function rotuloOrigemVersaoVideoTranscribrothers(origem: string): string {
  switch ((origem || "").trim()) {
    case "pipeline_completo":
      return "Documento";
    case "edicoes_modal":
      return "Edições";
    case "remux":
      return "Remux";
    case "atualizar_vtt":
      return "Legendas";
    default:
      return origem || "Geração";
  }
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

function GaleriaAssetsCorpoListaImagens({
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
          {carregando ? "Atualizando…" : "Atualizar lista"}
        </button>
        {itens ? (
          <span className="tb-muted tb-galeria-assets-contagem">
            {itens.length} {itens.length === 1 ? "imagem" : "imagens"}
          </span>
        ) : null}
      </div>
      {erro ? <pre className="tb-err tb-galeria-assets-erro">{erro}</pre> : null}
      {carregando && itens === null ? <p className="tb-muted tb-galeria-assets-loading">Carregando…</p> : null}
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

function CardVersaoVideoNarradoGaleriaTranscribrothers({
  versao,
  ehAtual,
  processando,
  aoEditar,
  aoTornarAtual,
  aoExcluir,
}: {
  versao: MetaVersaoVideoNarradoApiTranscribrothers;
  ehAtual: boolean;
  processando: boolean;
  aoEditar: () => void;
  aoTornarAtual: () => void;
  aoExcluir: () => void;
}) {
  const escopo =
    versao.escopo_modo === "secoes" && versao.escopo_titulos.length > 0
      ? `Seções: ${versao.escopo_titulos.join(", ")}`
      : "Documento completo";
  const urlThumb = versao.url_thumbnail || undefined;
  const urlMp4 = versao.url_download_mp4 || undefined;

  return (
    <article className={`tb-galeria-videos-card${ehAtual ? " tb-galeria-videos-card--atual" : ""}`}>
      <div className="tb-galeria-videos-thumb">
        {urlThumb ? (
          <img src={urlThumb} alt="" loading="lazy" draggable={false} />
        ) : (
          <span className="tb-galeria-videos-thumb-placeholder" aria-hidden>
            Vídeo
          </span>
        )}
      </div>
      <div className="tb-galeria-videos-meta">
        <div className="tb-galeria-videos-titulo-linha">
          <strong>{versao.id}</strong>
          {ehAtual ? (
            <span className="tb-galeria-assets-badge tb-galeria-videos-badge-atual">Atual</span>
          ) : null}
        </div>
        <p className="tb-muted tb-galeria-videos-detalhe">{formatarDataIsoCurtaTranscribrothers(versao.criado_em)}</p>
        <p className="tb-muted tb-galeria-videos-detalhe">
          {rotuloOrigemVersaoVideoTranscribrothers(versao.origem)} · {escopo}
        </p>
        <p className="tb-muted tb-galeria-videos-detalhe">
          Duração {formatarDuracaoSegundosTranscribrothers(versao.duracao_segundos)}
          {versao.voz_tts ? ` · Voz ${versao.voz_tts}` : ""}
        </p>
      </div>
      <div className="tb-galeria-videos-acoes" role="group" aria-label={`Ações da versão ${versao.id}`}>
        <button
          type="button"
          className="tb-btn-md-toolbar-icone"
          title="Editar vídeo narrado"
          aria-label={`Editar versão ${versao.id}`}
          disabled={processando}
          onClick={aoEditar}
        >
          <IconeEditarVideoNarradoGaleriaTranscribrothers />
        </button>
        {urlMp4 ? (
          <a
            className="tb-btn-md-toolbar-icone"
            href={urlMp4}
            download={`video_narrado_${versao.id}.mp4`}
            title="Baixar MP4"
            aria-label={`Baixar MP4 da versão ${versao.id}`}
          >
            <IconeBaixarVideoNarradoGaleriaTranscribrothers />
          </a>
        ) : null}
        {!ehAtual ? (
          <button
            type="button"
            className="tb-btn-md-toolbar-icone"
            title="Tornar atual"
            aria-label={`Tornar ${versao.id} a versão atual`}
            disabled={processando}
            onClick={aoTornarAtual}
          >
            <IconeTornarAtualVideoNarradoGaleriaTranscribrothers />
          </button>
        ) : null}
        <button
          type="button"
          className="tb-btn-md-toolbar-icone tb-galeria-videos-btn-icone--excluir"
          title="Excluir versão"
          aria-label={`Excluir versão ${versao.id}`}
          disabled={processando}
          onClick={aoExcluir}
        >
          <IconeLixeiraExcluirAssetGaleriaTranscribrothers />
        </button>
      </div>
    </article>
  );
}

function GaleriaAssetsCorpoListaFonte({
  carregando,
  erro,
  itens,
  cacheBytes,
  aoAtualizar,
  processando,
  aoLimparCache,
}: {
  carregando: boolean;
  erro: string | null;
  itens: ItemMidiaFonteJobApiTranscribrothers[] | null;
  cacheBytes: number;
  aoAtualizar: () => void;
  processando: boolean;
  aoLimparCache: () => void;
}) {
  const vazio = !carregando && itens && itens.length === 0 && cacheBytes <= 0;
  return (
    <>
      <div className="tb-galeria-assets-toolbar">
        <button type="button" className="tb-linkbtn" disabled={carregando} onClick={aoAtualizar}>
          {carregando ? "Atualizando…" : "Atualizar lista"}
        </button>
        {itens ? (
          <span className="tb-muted tb-galeria-assets-contagem">
            {itens.length} {itens.length === 1 ? "arquivo" : "arquivos"}
            {cacheBytes > 0 ? ` · cache ${formatarTamanhoBytesGaleriaAssetsTranscribrothers(cacheBytes)}` : ""}
          </span>
        ) : null}
      </div>
      {erro ? <pre className="tb-err tb-galeria-assets-erro">{erro}</pre> : null}
      {carregando && itens === null ? <p className="tb-muted tb-galeria-assets-loading">Carregando…</p> : null}
      {vazio ? (
        <p className="tb-muted tb-galeria-assets-vazio">
          Nenhuma mídia de origem neste projeto ainda (vídeo de entrada ou áudio extraído).
        </p>
      ) : null}
      {itens && itens.length > 0 ? (
        <div className="tb-galeria-fonte-lista" role="list">
          {itens.map((item) => (
            <article key={item.id} className="tb-galeria-fonte-card">
              <div className="tb-galeria-fonte-meta">
                <div className="tb-galeria-videos-titulo-linha">
                  <strong>{item.rotulo}</strong>
                  <span className="tb-galeria-assets-badge">{item.tipo}</span>
                </div>
                <p className="tb-muted tb-galeria-videos-detalhe" title={item.nome_arquivo}>
                  {item.nome_arquivo}
                </p>
                <p className="tb-muted tb-galeria-videos-detalhe">
                  {formatarTamanhoBytesGaleriaAssetsTranscribrothers(item.tamanho_bytes)}
                </p>
              </div>
              <div className="tb-galeria-videos-acoes">
                <a
                  className="tb-btn-md-toolbar-icone"
                  href={item.url_download}
                  download={item.nome_arquivo}
                  title="Baixar"
                  aria-label={`Baixar ${item.rotulo}`}
                >
                  <IconeBaixarVideoNarradoGaleriaTranscribrothers />
                </a>
              </div>
            </article>
          ))}
        </div>
      ) : null}
      {cacheBytes > 0 || (itens !== null && !carregando) ? (
        <div className="tb-galeria-fonte-cache">
          <div className="tb-galeria-fonte-meta">
            <strong>Cache regenerável</strong>
            <p className="tb-muted tb-galeria-videos-detalhe">
              Segmentos de montagem e frames intermediários. Pode ser apagado sem perder o tutorial nem o vídeo
              narrado; o pipeline regenera se precisar.
            </p>
            <p className="tb-muted tb-galeria-videos-detalhe">
              {formatarTamanhoBytesGaleriaAssetsTranscribrothers(cacheBytes)}
            </p>
          </div>
          <button
            type="button"
            className="tb-btn-md-toolbar-icone tb-galeria-videos-btn-icone--excluir"
            title="Limpar cache"
            aria-label="Limpar cache regenerável"
            disabled={processando || cacheBytes <= 0}
            onClick={aoLimparCache}
          >
            <IconeLimparCacheFonteGaleriaTranscribrothers />
          </button>
        </div>
      ) : null}
    </>
  );
}

function GaleriaAssetsCorpoListaVideos({
  carregando,
  erro,
  versaoAtualId,
  versoes,
  aoAtualizar,
  processando,
  aoEditar,
  aoTornarAtual,
  aoExcluir,
}: {
  carregando: boolean;
  erro: string | null;
  versaoAtualId: string | null;
  versoes: MetaVersaoVideoNarradoApiTranscribrothers[] | null;
  aoAtualizar: () => void;
  processando: boolean;
  aoEditar: (versao: MetaVersaoVideoNarradoApiTranscribrothers, ehAtual: boolean) => void;
  aoTornarAtual: (versaoId: string) => void;
  aoExcluir: (versaoId: string) => void;
}) {
  return (
    <>
      <div className="tb-galeria-assets-toolbar">
        <button type="button" className="tb-linkbtn" disabled={carregando} onClick={aoAtualizar}>
          {carregando ? "Atualizando…" : "Atualizar lista"}
        </button>
        {versoes ? (
          <span className="tb-muted tb-galeria-assets-contagem">
            {versoes.length} {versoes.length === 1 ? "versão" : "versões"}
          </span>
        ) : null}
      </div>
      {erro ? <pre className="tb-err tb-galeria-assets-erro">{erro}</pre> : null}
      {carregando && versoes === null ? <p className="tb-muted tb-galeria-assets-loading">Carregando…</p> : null}
      {!carregando && versoes && versoes.length === 0 ? (
        <p className="tb-muted tb-galeria-assets-vazio">
          Nenhuma versão de vídeo narrado ainda. Gere o vídeo narrado a partir do documento ou das edições para
          arquivar a primeira versão aqui.
        </p>
      ) : null}
      {versoes && versoes.length > 0 ? (
        <div className="tb-galeria-videos-lista" role="list">
          {versoes.map((v) => {
            const ehAtual = v.id === versaoAtualId;
            return (
              <CardVersaoVideoNarradoGaleriaTranscribrothers
                key={v.id}
                versao={v}
                ehAtual={ehAtual}
                processando={processando}
                aoEditar={() => aoEditar(v, ehAtual)}
                aoTornarAtual={() => aoTornarAtual(v.id)}
                aoExcluir={() => aoExcluir(v.id)}
              />
            );
          })}
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
  aoAbrirEdicaoVideoNarrado,
}: PropsModalGaleriaAssetsImagensTranscricaoTutorialTranscribrothers) {
  const [aba, setAba] = useState<AbaGaleriaAssetsTranscribrothers>("imagens");
  const [itens, setItens] = useState<ItemListaAssetImagemTutorialApiTranscribrothers[] | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [confirmacaoExclusao, setConfirmacaoExclusao] =
    useState<ConfirmacaoExclusaoAssetGaleriaTranscribrothers | null>(null);
  const [processandoExclusao, setProcessandoExclusao] = useState(false);

  const [versoes, setVersoes] = useState<MetaVersaoVideoNarradoApiTranscribrothers[] | null>(null);
  const [versaoAtualId, setVersaoAtualId] = useState<string | null>(null);
  const [carregandoVideos, setCarregandoVideos] = useState(false);
  const [erroVideos, setErroVideos] = useState<string | null>(null);
  const [processandoVideo, setProcessandoVideo] = useState(false);
  const [confirmacaoExclusaoVideo, setConfirmacaoExclusaoVideo] =
    useState<ConfirmacaoExclusaoVersaoVideoTranscribrothers | null>(null);

  const [itensFonte, setItensFonte] = useState<ItemMidiaFonteJobApiTranscribrothers[] | null>(null);
  const [cacheBytesFonte, setCacheBytesFonte] = useState(0);
  const [carregandoFonte, setCarregandoFonte] = useState(false);
  const [erroFonte, setErroFonte] = useState<string | null>(null);
  const [processandoFonte, setProcessandoFonte] = useState(false);
  const [confirmacaoLimparCache, setConfirmacaoLimparCache] = useState(false);

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

  const carregarListaVideos = useCallback(async () => {
    setCarregandoVideos(true);
    setErroVideos(null);
    try {
      const resp = await listarVersoesVideoNarradoJobApiTranscribrothers(jobId);
      setVersoes(resp.versoes ?? []);
      setVersaoAtualId(resp.versao_atual_id ?? null);
    } catch (e) {
      setVersoes(null);
      setErroVideos(e instanceof Error ? e.message : String(e));
    } finally {
      setCarregandoVideos(false);
    }
  }, [jobId]);

  const carregarListaFonte = useCallback(async () => {
    setCarregandoFonte(true);
    setErroFonte(null);
    try {
      const resp = await listarMidiaFonteJobApiTranscribrothers(jobId);
      setItensFonte(resp.itens ?? []);
      setCacheBytesFonte(Number(resp.cache_bytes) || 0);
    } catch (e) {
      setItensFonte(null);
      setErroFonte(e instanceof Error ? e.message : String(e));
    } finally {
      setCarregandoFonte(false);
    }
  }, [jobId]);

  useEffect(() => {
    if (!aberto) {
      setItens(null);
      setErro(null);
      setConfirmacaoExclusao(null);
      setVersoes(null);
      setVersaoAtualId(null);
      setErroVideos(null);
      setConfirmacaoExclusaoVideo(null);
      setItensFonte(null);
      setCacheBytesFonte(0);
      setErroFonte(null);
      setConfirmacaoLimparCache(false);
      setAba("imagens");
      return;
    }
    void carregarLista();
  }, [aberto, carregarLista]);

  useEffect(() => {
    if (!aberto || aba !== "videos") return;
    void carregarListaVideos();
  }, [aberto, aba, carregarListaVideos]);

  useEffect(() => {
    if (!aberto || aba !== "fonte") return;
    void carregarListaFonte();
  }, [aberto, aba, carregarListaFonte]);

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

  const tornarAtualEOpcionalmenteEditar = async (versaoId: string, abrirEdicao: boolean) => {
    setProcessandoVideo(true);
    try {
      const j = await tornarVersaoVideoNarradoAtualJobApiTranscribrothers(jobId, versaoId);
      aoJobAtualizado(j);
      await carregarListaVideos();
      aoNotificarToast(`Versão ${versaoId} definida como atual.`, "success");
      if (abrirEdicao) {
        aoFechar();
        aoAbrirEdicaoVideoNarrado?.();
      }
    } catch (e) {
      aoNotificarToast(e instanceof Error ? e.message : String(e), "error");
    } finally {
      setProcessandoVideo(false);
    }
  };

  const aoEditarVersao = async (versao: MetaVersaoVideoNarradoApiTranscribrothers, ehAtual: boolean) => {
    if (ehAtual) {
      aoFechar();
      aoAbrirEdicaoVideoNarrado?.();
      return;
    }
    await tornarAtualEOpcionalmenteEditar(versao.id, true);
  };

  const confirmarLimparCacheFonte = async () => {
    setProcessandoFonte(true);
    try {
      const resp = await limparCacheMidiaFonteJobApiTranscribrothers(jobId);
      setCacheBytesFonte(Number(resp.cache_bytes) || 0);
      setConfirmacaoLimparCache(false);
      aoNotificarToast("Cache regenerável limpo.", "success");
      await carregarListaFonte();
    } catch (e) {
      aoNotificarToast(e instanceof Error ? e.message : String(e), "error");
    } finally {
      setProcessandoFonte(false);
    }
  };

  const confirmarExclusaoVersao = async () => {
    if (!confirmacaoExclusaoVideo) return;
    setProcessandoVideo(true);
    try {
      const resp = await apagarVersaoVideoNarradoJobApiTranscribrothers(
        jobId,
        confirmacaoExclusaoVideo.versaoId,
      );
      setVersoes(resp.versoes ?? []);
      setVersaoAtualId(resp.versao_atual_id ?? null);
      if (resp.job) {
        aoJobAtualizado(resp.job);
      }
      setConfirmacaoExclusaoVideo(null);
      aoNotificarToast(
        confirmacaoExclusaoVideo.unicaVersao
          ? `Versão ${confirmacaoExclusaoVideo.versaoId} excluída e vídeo narrado removido do projeto.`
          : confirmacaoExclusaoVideo.ehAtual
            ? `Versão ${confirmacaoExclusaoVideo.versaoId} excluída; outra versão passou a ser a atual.`
            : `Versão ${confirmacaoExclusaoVideo.versaoId} excluída.`,
        "success",
      );
    } catch (e) {
      aoNotificarToast(e instanceof Error ? e.message : String(e), "error");
    } finally {
      setProcessandoVideo(false);
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
            <div className="tb-galeria-assets-abas" role="tablist" aria-label="Tipo de asset">
              <button
                type="button"
                role="tab"
                aria-selected={aba === "imagens"}
                className={`tb-galeria-assets-aba${aba === "imagens" ? " tb-galeria-assets-aba--ativa" : ""}`}
                onClick={() => setAba("imagens")}
              >
                Imagens
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={aba === "videos"}
                className={`tb-galeria-assets-aba${aba === "videos" ? " tb-galeria-assets-aba--ativa" : ""}`}
                onClick={() => setAba("videos")}
              >
                Vídeos
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={aba === "fonte"}
                className={`tb-galeria-assets-aba${aba === "fonte" ? " tb-galeria-assets-aba--ativa" : ""}`}
                onClick={() => setAba("fonte")}
              >
                Fonte
              </button>
            </div>
            {aba === "imagens" ? (
              <>
                <p className="tb-muted tb-galeria-assets-intro">
                  Capturas PNG geradas a partir do vídeo. Clique na miniatura para anotar; use a lixeira para excluir do
                  servidor.
                </p>
                <GaleriaAssetsCorpoListaImagens
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
              </>
            ) : null}
            {aba === "videos" ? (
              <>
                <p className="tb-muted tb-galeria-assets-intro">
                  Versões do vídeo narrado. A versão atual é a que a tela de edição e os pipelines usam. Editar uma
                  versão antiga a torna atual antes de abrir o editor.
                </p>
                <GaleriaAssetsCorpoListaVideos
                  carregando={carregandoVideos}
                  erro={erroVideos}
                  versaoAtualId={versaoAtualId}
                  versoes={versoes}
                  aoAtualizar={() => void carregarListaVideos()}
                  processando={processandoVideo}
                  aoEditar={(v, ehAtual) => void aoEditarVersao(v, ehAtual)}
                  aoTornarAtual={(id) => void tornarAtualEOpcionalmenteEditar(id, false)}
                  aoExcluir={(id) =>
                    setConfirmacaoExclusaoVideo({
                      versaoId: id,
                      ehAtual: id === versaoAtualId,
                      unicaVersao: (versoes?.length ?? 0) <= 1,
                    })
                  }
                />
              </>
            ) : null}
            {aba === "fonte" ? (
              <>
                <p className="tb-muted tb-galeria-assets-intro">
                  Mídia usada na transcrição (vídeo de entrada e áudios extraídos). O cache regenerável pode ser limpo
                  para liberar espaço.
                </p>
                <GaleriaAssetsCorpoListaFonte
                  carregando={carregandoFonte}
                  erro={erroFonte}
                  itens={itensFonte}
                  cacheBytes={cacheBytesFonte}
                  aoAtualizar={() => void carregarListaFonte()}
                  processando={processandoFonte}
                  aoLimparCache={() => setConfirmacaoLimparCache(true)}
                />
              </>
            ) : null}
            <footer className="tb-modal-job-rodape">
              <div className="tb-modal-job-acoes-finais">
                <button type="button" className="tb-primary" onClick={aoFechar}>
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

      <ComponenteDialogoConfirmacaoAcaoDestrutivaOverlayTranscribrothers
        aberto={confirmacaoExclusaoVideo !== null}
        titulo="Excluir versão do vídeo?"
        mensagem={
          confirmacaoExclusaoVideo
            ? confirmacaoExclusaoVideo.unicaVersao
              ? `A versão «${confirmacaoExclusaoVideo.versaoId}» é a única. Ela será removida e o vídeo narrado atual do projeto também será apagado (MP4, legendas e áudio TTS do conjunto de trabalho).`
              : confirmacaoExclusaoVideo.ehAtual
                ? `A versão «${confirmacaoExclusaoVideo.versaoId}» é a atual. Ela será excluída e a versão mais recente restante passará a ser a atual.`
                : `A versão «${confirmacaoExclusaoVideo.versaoId}» será removida permanentemente.`
            : ""
        }
        rotuloConfirmar="Excluir"
        rotuloCancelar="Cancelar"
        processando={processandoVideo}
        aoConfirmar={() => void confirmarExclusaoVersao()}
        aoCancelar={() => {
          if (!processandoVideo) setConfirmacaoExclusaoVideo(null);
        }}
      />

      <ComponenteDialogoConfirmacaoAcaoDestrutivaOverlayTranscribrothers
        aberto={confirmacaoLimparCache}
        titulo="Limpar cache?"
        mensagem={`Serão removidos ${formatarTamanhoBytesGaleriaAssetsTranscribrothers(cacheBytesFonte)} de cache regenerável (segmentos de montagem e frames intermediários). O vídeo de entrada, o áudio da transcrição, as imagens do tutorial e as versões do vídeo narrado permanecem.`}
        rotuloConfirmar="Limpar"
        rotuloCancelar="Cancelar"
        processando={processandoFonte}
        aoConfirmar={() => void confirmarLimparCacheFonte()}
        aoCancelar={() => {
          if (!processandoFonte) setConfirmacaoLimparCache(false);
        }}
      />
    </>,
    document.body,
  );
}
