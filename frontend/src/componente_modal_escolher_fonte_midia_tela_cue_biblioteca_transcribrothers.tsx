/**
 * Modal para escolher a fonte de tela de uma cue (entrada + biblioteca) e/ou enviar vídeo extra.
 * Visual alinhado à galeria de assets: cards, miniatura e prévia opcional.
 */

import { useCallback, useEffect, useId, useRef, useState } from "react";
import { createPortal } from "react-dom";

import {
  apagarItemBibliotecaMidiasTelaJobApiTranscribrothers,
  enviarVideoBibliotecaMidiasTelaJobApiTranscribrothers,
  ID_FONTE_VIDEO_ENTRADA_UI_TRANSCRIBROTHERS,
  listarBibliotecaMidiasTelaJobApiTranscribrothers,
  urlArquivoBibliotecaMidiasTelaJobUiTranscribrothers,
  type ItemBibliotecaMidiaTelaApiTranscribrothers,
} from "./modulo_api_biblioteca_midias_tela_job_transcribrothers.ts";
import "./estilos_css_modal_escolher_fonte_midia_tela_cue_biblioteca_transcribrothers.css";

export type PropsComponenteModalEscolherFonteMidiaTelaCueBibliotecaTranscribrothers = {
  aberto: boolean;
  jobId: string;
  idFonteAtual?: string | null;
  onFechar: () => void;
  onEscolherFonte: (idFonteVideo: string, rotulo: string) => void;
};

function rotuloItemTranscribrothers(item: ItemBibliotecaMidiaTelaApiTranscribrothers): string {
  if (item.eh_entrada || item.id === ID_FONTE_VIDEO_ENTRADA_UI_TRANSCRIBROTHERS) {
    return "Vídeo de entrada";
  }
  return item.nome_original || item.nome_arquivo || item.id;
}

function formatarTamanhoBytesFonteMidiaTelaTranscribrothers(bytes: number): string {
  const n = Math.max(0, Number(bytes) || 0);
  if (n < 1024) return `${n} B`;
  const kb = n / 1024;
  if (kb < 1024) return `${kb < 10 ? kb.toFixed(1) : Math.round(kb)} KB`;
  const mb = kb / 1024;
  if (mb < 1024) return `${mb < 10 ? mb.toFixed(1) : Math.round(mb)} MB`;
  const gb = mb / 1024;
  return `${gb < 10 ? gb.toFixed(2) : gb.toFixed(1)} GB`;
}

function formatarDuracaoSegundosFonteMidiaTelaTranscribrothers(segundos: number | null | undefined): string {
  if (segundos == null || !Number.isFinite(segundos) || segundos <= 0) return "—";
  const s = Math.max(0, Math.round(segundos));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${m}:${String(r).padStart(2, "0")}`;
}

function urlStreamItemFonteMidiaTelaTranscribrothers(
  jobId: string,
  item: ItemBibliotecaMidiaTelaApiTranscribrothers,
): string {
  const urlApi = (item.url_arquivo || "").trim();
  if (urlApi) return urlApi;
  return urlArquivoBibliotecaMidiasTelaJobUiTranscribrothers(jobId, item.id);
}

/** Captura um frame do vídeo (mesmo origin) para miniatura no card. */
function MiniaturaVideoFonteMidiaTelaBibliotecaTranscribrothers({
  urlVideo,
  rotulo,
}: {
  urlVideo: string;
  rotulo: string;
}) {
  const [src, setSrc] = useState<string | null>(null);
  const [falhou, setFalhou] = useState(false);

  useEffect(() => {
    let cancelado = false;
    setSrc(null);
    setFalhou(false);

    const video = document.createElement("video");
    video.muted = true;
    video.playsInline = true;
    video.preload = "auto";
    video.setAttribute("playsinline", "");

    const aoErro = () => {
      if (!cancelado) setFalhou(true);
    };

    const capturar = () => {
      try {
        const w = video.videoWidth;
        const h = video.videoHeight;
        if (!w || !h) {
          aoErro();
          return;
        }
        const canvas = document.createElement("canvas");
        const maxW = 240;
        const escala = Math.min(1, maxW / w);
        canvas.width = Math.max(1, Math.round(w * escala));
        canvas.height = Math.max(1, Math.round(h * escala));
        const ctx = canvas.getContext("2d");
        if (!ctx) {
          aoErro();
          return;
        }
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const dataUrl = canvas.toDataURL("image/jpeg", 0.72);
        if (!cancelado) setSrc(dataUrl);
      } catch {
        aoErro();
      }
    };

    const aoSeeked = () => capturar();

    const aoMeta = () => {
      const dur = Number(video.duration);
      const alvo =
        Number.isFinite(dur) && dur > 0.4 ? Math.min(1, dur * 0.08) : 0.05;
      try {
        video.currentTime = alvo;
      } catch {
        capturar();
      }
    };

    video.addEventListener("loadeddata", aoMeta);
    video.addEventListener("seeked", aoSeeked);
    video.addEventListener("error", aoErro);
    video.src = urlVideo;
    video.load();

    return () => {
      cancelado = true;
      video.removeEventListener("loadeddata", aoMeta);
      video.removeEventListener("seeked", aoSeeked);
      video.removeEventListener("error", aoErro);
      video.removeAttribute("src");
      video.load();
    };
  }, [urlVideo]);

  if (falhou) {
    return (
      <span className="tb-modal-escolher-fonte-midia-tela-thumb-placeholder" aria-hidden>
        Vídeo
      </span>
    );
  }
  if (!src) {
    return (
      <span className="tb-modal-escolher-fonte-midia-tela-thumb-placeholder" aria-hidden>
        …
      </span>
    );
  }
  return <img src={src} alt={`Prévia de ${rotulo}`} draggable={false} />;
}

export function ComponenteModalEscolherFonteMidiaTelaCueBibliotecaTranscribrothers({
  aberto,
  jobId,
  idFonteAtual,
  onFechar,
  onEscolherFonte,
}: PropsComponenteModalEscolherFonteMidiaTelaCueBibliotecaTranscribrothers) {
  const tituloId = useId();
  const inputFileRef = useRef<HTMLInputElement | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [apagandoId, setApagandoId] = useState<string | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [entrada, setEntrada] = useState<ItemBibliotecaMidiaTelaApiTranscribrothers | null>(null);
  const [itens, setItens] = useState<ItemBibliotecaMidiaTelaApiTranscribrothers[]>([]);
  const [idPrevia, setIdPrevia] = useState<string | null>(null);

  const recarregar = useCallback(async () => {
    setCarregando(true);
    setErro(null);
    try {
      const resp = await listarBibliotecaMidiasTelaJobApiTranscribrothers(jobId);
      setEntrada(resp.entrada);
      setItens(resp.itens || []);
    } catch (e: unknown) {
      setErro(e instanceof Error ? e.message : String(e));
    } finally {
      setCarregando(false);
    }
  }, [jobId]);

  useEffect(() => {
    if (!aberto) return;
    setIdPrevia(null);
    void recarregar();
  }, [aberto, recarregar]);

  useEffect(() => {
    if (!aberto) return;
    const aoTeclar = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        if (idPrevia) {
          setIdPrevia(null);
          return;
        }
        onFechar();
      }
    };
    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
  }, [aberto, onFechar, idPrevia]);

  if (!aberto) return null;

  const idAtual = (idFonteAtual || "").trim() || ID_FONTE_VIDEO_ENTRADA_UI_TRANSCRIBROTHERS;
  const lista: ItemBibliotecaMidiaTelaApiTranscribrothers[] = [
    ...(entrada
      ? [{ ...entrada, eh_entrada: true, id: ID_FONTE_VIDEO_ENTRADA_UI_TRANSCRIBROTHERS }]
      : []),
    ...itens,
  ];
  const itemPrevia = idPrevia ? lista.find((i) => i.id === idPrevia) ?? null : null;
  const urlPrevia = itemPrevia
    ? urlStreamItemFonteMidiaTelaTranscribrothers(jobId, itemPrevia)
    : null;

  return createPortal(
    <div className="tb-modal-escolher-fonte-midia-tela-overlay" role="presentation">
      <button
        type="button"
        className="tb-modal-escolher-fonte-midia-tela-backdrop"
        aria-label="Fechar mídias de tela"
        onClick={onFechar}
      />
      <div
        className="tb-modal-escolher-fonte-midia-tela"
        role="dialog"
        aria-modal="true"
        aria-labelledby={tituloId}
      >
        <header className="tb-modal-escolher-fonte-midia-tela-cabecalho">
          <h2 id={tituloId} className="tb-modal-escolher-fonte-midia-tela-titulo">
            Escolher origem
          </h2>
          <button
            type="button"
            className="tb-modal-escolher-fonte-midia-tela-fechar"
            onClick={onFechar}
            aria-label="Fechar"
          >
            ×
          </button>
        </header>

        <p className="tb-muted tb-modal-escolher-fonte-midia-tela-ajuda">
          Escolha o vídeo de origem desta cue (de onde cortar o trecho). Vídeos extras não alteram a
          entrada do projeto. Use Prévia para conferir o conteúdo antes de usar.
        </p>

        <div className="tb-modal-escolher-fonte-midia-tela-toolbar">
          <span className="tb-muted tb-modal-escolher-fonte-midia-tela-contagem">
            {carregando
              ? "Carregando…"
              : `${lista.length} mídia${lista.length === 1 ? "" : "s"}`}
          </span>
          <input
            ref={inputFileRef}
            type="file"
            accept="video/*,.mp4,.webm,.mov,.mkv"
            hidden
            onChange={(e) => {
              const file = e.target.files?.[0];
              e.target.value = "";
              if (!file) return;
              void (async () => {
                setEnviando(true);
                setErro(null);
                try {
                  const item = await enviarVideoBibliotecaMidiasTelaJobApiTranscribrothers(
                    jobId,
                    file,
                  );
                  await recarregar();
                  onEscolherFonte(item.id, rotuloItemTranscribrothers(item));
                } catch (err: unknown) {
                  setErro(err instanceof Error ? err.message : String(err));
                } finally {
                  setEnviando(false);
                }
              })();
            }}
          />
          <button
            type="button"
            className="tb-btn"
            disabled={enviando || carregando}
            onClick={() => inputFileRef.current?.click()}
          >
            {enviando ? "Enviando…" : "Adicionar vídeo"}
          </button>
        </div>

        {erro ? <p className="tb-modal-escolher-fonte-midia-tela-erro">{erro}</p> : null}

        {carregando ? (
          <p className="tb-muted tb-modal-escolher-fonte-midia-tela-estado">Carregando…</p>
        ) : lista.length === 0 ? (
          <p className="tb-muted tb-modal-escolher-fonte-midia-tela-estado">
            Nenhuma mídia disponível. Adicione um vídeo ou use a entrada do projeto.
          </p>
        ) : (
          <ul className="tb-modal-escolher-fonte-midia-tela-grade" role="list">
            {lista.map((item) => {
              const selecionado = item.id === idAtual;
              const ehEntrada =
                Boolean(item.eh_entrada) ||
                item.id === ID_FONTE_VIDEO_ENTRADA_UI_TRANSCRIBROTHERS;
              const rotulo = rotuloItemTranscribrothers(item);
              const url = urlStreamItemFonteMidiaTelaTranscribrothers(jobId, item);
              const previaAtiva = idPrevia === item.id;
              return (
                <li
                  key={item.id}
                  className={
                    "tb-modal-escolher-fonte-midia-tela-card" +
                    (selecionado
                      ? " tb-modal-escolher-fonte-midia-tela-card--selecionado"
                      : "") +
                    (previaAtiva ? " tb-modal-escolher-fonte-midia-tela-card--previa" : "")
                  }
                >
                  <button
                    type="button"
                    className="tb-modal-escolher-fonte-midia-tela-card-corpo"
                    title="Usar esta mídia e abrir o recorte"
                    onClick={() => onEscolherFonte(item.id, rotulo)}
                  >
                    <div className="tb-modal-escolher-fonte-midia-tela-thumb">
                      <MiniaturaVideoFonteMidiaTelaBibliotecaTranscribrothers
                        urlVideo={url}
                        rotulo={rotulo}
                      />
                    </div>
                    <div className="tb-modal-escolher-fonte-midia-tela-meta">
                      <div className="tb-modal-escolher-fonte-midia-tela-titulo-linha">
                        <strong className="tb-modal-escolher-fonte-midia-tela-nome" title={rotulo}>
                          {rotulo}
                        </strong>
                        {ehEntrada ? (
                          <span className="tb-modal-escolher-fonte-midia-tela-badge tb-modal-escolher-fonte-midia-tela-badge--entrada">
                            entrada
                          </span>
                        ) : null}
                        {selecionado ? (
                          <span className="tb-modal-escolher-fonte-midia-tela-badge tb-modal-escolher-fonte-midia-tela-badge--atual">
                            atual
                          </span>
                        ) : null}
                      </div>
                      <p className="tb-muted tb-modal-escolher-fonte-midia-tela-detalhe">
                        Duração {formatarDuracaoSegundosFonteMidiaTelaTranscribrothers(item.duracao_segundos)}
                        {item.tamanho_bytes > 0
                          ? ` · ${formatarTamanhoBytesFonteMidiaTelaTranscribrothers(item.tamanho_bytes)}`
                          : ""}
                      </p>
                    </div>
                  </button>
                  <div
                    className="tb-modal-escolher-fonte-midia-tela-acoes"
                    role="group"
                    aria-label={`Ações de ${rotulo}`}
                  >
                    <button
                      type="button"
                      className={
                        "tb-btn tb-btn-secondary tb-modal-escolher-fonte-midia-tela-btn-acao" +
                        (previaAtiva
                          ? " tb-modal-escolher-fonte-midia-tela-btn-acao--ativa"
                          : "")
                      }
                      title="Pré-visualizar este vídeo"
                      onClick={() => setIdPrevia((atual) => (atual === item.id ? null : item.id))}
                    >
                      {previaAtiva ? "Fechar prévia" : "Prévia"}
                    </button>
                    <button
                      type="button"
                      className="tb-btn tb-modal-escolher-fonte-midia-tela-btn-acao"
                      title="Usar esta mídia e abrir o recorte"
                      onClick={() => onEscolherFonte(item.id, rotulo)}
                    >
                      Usar
                    </button>
                    {!ehEntrada ? (
                      <button
                        type="button"
                        className="tb-btn tb-btn-secondary tb-modal-escolher-fonte-midia-tela-btn-acao tb-modal-escolher-fonte-midia-tela-btn-acao--excluir"
                        disabled={apagandoId === item.id}
                        title="Remover desta biblioteca"
                        onClick={() => {
                          void (async () => {
                            setApagandoId(item.id);
                            setErro(null);
                            try {
                              await apagarItemBibliotecaMidiasTelaJobApiTranscribrothers(
                                jobId,
                                item.id,
                              );
                              if (idPrevia === item.id) setIdPrevia(null);
                              await recarregar();
                            } catch (e: unknown) {
                              setErro(e instanceof Error ? e.message : String(e));
                            } finally {
                              setApagandoId(null);
                            }
                          })();
                        }}
                      >
                        {apagandoId === item.id ? "…" : "Excluir"}
                      </button>
                    ) : null}
                  </div>
                </li>
              );
            })}
          </ul>
        )}

        {itemPrevia && urlPrevia ? (
          <div className="tb-modal-escolher-fonte-midia-tela-previa">
            <div className="tb-modal-escolher-fonte-midia-tela-previa-cabecalho">
              <strong>Prévia — {rotuloItemTranscribrothers(itemPrevia)}</strong>
              <button
                type="button"
                className="tb-btn tb-btn-secondary"
                onClick={() => setIdPrevia(null)}
              >
                Fechar
              </button>
            </div>
            <video
              key={urlPrevia}
              className="tb-modal-escolher-fonte-midia-tela-previa-video"
              src={urlPrevia}
              controls
              playsInline
              preload="metadata"
            />
          </div>
        ) : null}

        <footer className="tb-modal-escolher-fonte-midia-tela-rodape">
          <button type="button" className="tb-btn tb-btn-secondary" onClick={onFechar}>
            Cancelar
          </button>
        </footer>
      </div>
    </div>,
    document.body,
  );
}
