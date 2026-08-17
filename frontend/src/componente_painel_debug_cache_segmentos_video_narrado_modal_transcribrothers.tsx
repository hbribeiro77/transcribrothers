/**
 * Painel colapsável de debug: cache de segmentos do vídeo narrado no job.
 */

import { useCallback, useEffect, useState } from "react";
import {
  obterDebugCacheSegmentosVideoNarradoJobApiTranscribrothers,
  type PayloadDebugCacheSegmentosVideoNarradoApiTranscribrothers,
} from "./modulo_api_debug_cache_segmentos_video_narrado_job_transcribrothers.ts";

function formatarTamanhoBytesDebugCacheSegmentosTranscribrothers(bytes: number): string {
  const n = Math.max(0, Number(bytes) || 0);
  if (n < 1024) return `${n} B`;
  const kb = n / 1024;
  if (kb < 1024) return `${kb < 10 ? kb.toFixed(1) : Math.round(kb)} KB`;
  const mb = kb / 1024;
  if (mb < 1024) return `${mb < 10 ? mb.toFixed(1) : Math.round(mb)} MB`;
  const gb = mb / 1024;
  return `${gb < 10 ? gb.toFixed(2) : Math.round(gb)} GB`;
}

function textoOuTraco(valor: string | number | null | undefined): string {
  if (valor === null || valor === undefined || valor === "") return "—";
  return String(valor);
}

export type PropsPainelDebugCacheSegmentosVideoNarradoModalTranscribrothers = {
  jobId: string;
  aberto: boolean;
  onFechar: () => void;
};

export function ComponentePainelDebugCacheSegmentosVideoNarradoModalTranscribrothers({
  jobId,
  aberto,
  onFechar,
}: PropsPainelDebugCacheSegmentosVideoNarradoModalTranscribrothers) {
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [dados, setDados] = useState<PayloadDebugCacheSegmentosVideoNarradoApiTranscribrothers | null>(
    null,
  );

  const carregar = useCallback(async () => {
    setCarregando(true);
    setErro(null);
    try {
      const payload = await obterDebugCacheSegmentosVideoNarradoJobApiTranscribrothers(jobId);
      setDados(payload);
    } catch (e) {
      setDados(null);
      setErro(e instanceof Error ? e.message : "Não foi possível carregar o debug.");
    } finally {
      setCarregando(false);
    }
  }, [jobId]);

  useEffect(() => {
    if (!aberto) return;
    void carregar();
  }, [aberto, carregar]);

  if (!aberto) return null;

  const seg = dados?.segmentos;
  const mux = dados?.ultimo_mux;
  const edicoes = dados?.edicoes_modal;
  const hits = mux?.hits_cache;
  const total = mux?.total_segmentos;
  let rotuloHits = "—";
  if (hits !== null && hits !== undefined && total !== null && total !== undefined && total > 0) {
    rotuloHits = `${hits} / ${total} (${Math.round((hits / total) * 100)}%)`;
  } else if (hits !== null && hits !== undefined) {
    rotuloHits = String(hits);
  }

  let rotuloHitsEdicoes = "—";
  if (
    edicoes?.mux_hits_cache != null &&
    edicoes?.mux_total_segmentos != null &&
    edicoes.mux_total_segmentos > 0
  ) {
    rotuloHitsEdicoes = `${edicoes.mux_hits_cache} / ${edicoes.mux_total_segmentos}`;
  } else if (edicoes?.mux_hits_cache != null) {
    rotuloHitsEdicoes = String(edicoes.mux_hits_cache);
  }

  return (
    <aside
      className="tb-modal-assistir-video-narrado-painel-debug"
      aria-label="Debug: cache de segmentos"
    >
      <div className="tb-modal-assistir-video-narrado-painel-debug-cabecalho">
        <h3 className="tb-modal-assistir-video-narrado-painel-debug-titulo">Debug · cache</h3>
        <div className="tb-modal-assistir-video-narrado-painel-debug-acoes">
          <button
            type="button"
            className="tb-modal-assistir-video-narrado-painel-debug-btn"
            onClick={() => void carregar()}
            disabled={carregando}
          >
            {carregando ? "Atualizando…" : "Atualizar"}
          </button>
          <button
            type="button"
            className="tb-modal-assistir-video-narrado-painel-debug-btn"
            onClick={onFechar}
            aria-label="Esconder debug"
          >
            Esconder
          </button>
        </div>
      </div>

      {erro ? (
        <p className="tb-modal-assistir-video-narrado-painel-debug-erro" role="alert">
          {erro}
        </p>
      ) : null}

      {carregando && !dados ? (
        <p className="tb-modal-assistir-video-narrado-painel-debug-vazio">Carregando…</p>
      ) : null}

      {seg ? (
        <dl className="tb-modal-assistir-video-narrado-painel-debug-lista">
          <div>
            <dt>Cache de segmentos</dt>
            <dd>
              {seg.tem_cache_segmentos ? (
                <span className="tb-modal-assistir-video-narrado-painel-debug-ok">sim</span>
              ) : (
                <span className="tb-modal-assistir-video-narrado-painel-debug-nao">não</span>
              )}
            </dd>
          </div>
          <div>
            <dt>Pasta</dt>
            <dd>
              <code>{seg.nome_pasta}</code>
              {seg.pasta_existe ? " (existe)" : " (ausente)"}
            </dd>
          </div>
          <div>
            <dt>MP4s na pasta</dt>
            <dd>{seg.quantidade_mp4}</dd>
          </div>
          <div>
            <dt>Tamanho (segmentos)</dt>
            <dd>{formatarTamanhoBytesDebugCacheSegmentosTranscribrothers(seg.bytes_pasta)}</dd>
          </div>
          <div>
            <dt>Cache regenerável (total)</dt>
            <dd>
              {formatarTamanhoBytesDebugCacheSegmentosTranscribrothers(
                dados?.cache_bytes_total_regeneravel ?? 0,
              )}
            </dd>
          </div>
        </dl>
      ) : null}

      <h4 className="tb-modal-assistir-video-narrado-painel-debug-subtitulo">
        Edições do modal
      </h4>
      {edicoes ? (
        <dl className="tb-modal-assistir-video-narrado-painel-debug-lista">
          <div>
            <dt>Origem da corrida</dt>
            <dd>
              <code>{textoOuTraco(edicoes.origem_corrida)}</code>
            </dd>
          </div>
          <div>
            <dt>Cues sujas (TTS)</dt>
            <dd>{textoOuTraco(edicoes.cues_sujas)}</dd>
          </div>
          <div>
            <dt>WAVs reusados</dt>
            <dd>{textoOuTraco(edicoes.wavs_reusados)}</dd>
          </div>
          <div>
            <dt>Hits mux (desta corrida)</dt>
            <dd>{rotuloHitsEdicoes}</dd>
          </div>
          <div>
            <dt>Fase</dt>
            <dd>{textoOuTraco(edicoes.pipeline_fase)}</dd>
          </div>
        </dl>
      ) : (
        <p className="tb-modal-assistir-video-narrado-painel-debug-vazio">
          Ainda não há métricas de edições do modal neste job.
        </p>
      )}

      <h4 className="tb-modal-assistir-video-narrado-painel-debug-subtitulo">Último mux</h4>
      {mux ? (
        <dl className="tb-modal-assistir-video-narrado-painel-debug-lista">
          <div>
            <dt>Hits de cache</dt>
            <dd>{rotuloHits}</dd>
          </div>
          <div>
            <dt>Fase mux</dt>
            <dd>{textoOuTraco(mux.fase_mux)}</dd>
          </div>
          <div>
            <dt>Encode</dt>
            <dd>
              {textoOuTraco(mux.resolucao)}
              {mux.fps != null ? ` · ${mux.fps} fps` : ""}
              {mux.paralelismo != null && mux.paralelismo > 1
                ? ` · ${mux.paralelismo} em paralelo`
                : ""}
            </dd>
          </div>
          <div>
            <dt>Modo montagem</dt>
            <dd>
              <code>{textoOuTraco(mux.modo_montagem)}</code>
            </dd>
          </div>
          <div>
            <dt>Pipeline</dt>
            <dd>{textoOuTraco(mux.pipeline_fase)}</dd>
          </div>
          <div>
            <dt>Gerado em</dt>
            <dd>{textoOuTraco(mux.gerado_em)}</dd>
          </div>
        </dl>
      ) : (
        <p className="tb-modal-assistir-video-narrado-painel-debug-vazio">
          Ainda não há dados de mux neste job (gere o vídeo narrado ao menos uma vez).
        </p>
      )}
    </aside>
  );
}
