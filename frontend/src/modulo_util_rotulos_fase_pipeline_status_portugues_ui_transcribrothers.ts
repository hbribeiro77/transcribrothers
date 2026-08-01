/** Rótulos legíveis para `steps_json.pipeline_fase` e `status` do job (API). */

const PIPELINE_FASE_PARA_ROTULO_PORTUGUES: Record<string, string> = {
  metadados_job_carregados: "Preparando…",
  ffmpeg_extrair_audio: "Extraindo áudio do vídeo…",
  transcrevendo_audio: "Transcrevendo áudio…",
  transcrevendo_audio_janela_litellm_multimodal: "Transcrevendo áudio (trecho)…",
  transcrevendo_audio_janelas_litellm_multimodal_paralelo: "Transcrevendo áudio (vários trechos em paralelo)…",
  transcrevendo_audio_litellm_multimodal_arquivo_unico: "Transcrevendo áudio (arquivo inteiro)…",
  transcricao_concluida: "Transcrição concluída",
  capturando_frames_png: "Capturando telas (screenshots)…",
  capturando_frame_png_individual: "Capturando telas (screenshots)…",
  gerando_tutorial_http_chat_completions: "Gerando tutorial em Markdown…",
  regenerando_somente_tutorial_litellm_agendado: "Regenerando tutorial (reaproveitando dados)…",
  regenerando_somente_tutorial_litellm: "Gerando novo texto do tutorial…",
  regenerando_markdown_reproducao_bug_litellm_agendado: "Regenerando roteiro de reprodução do bug…",
  regenerando_markdown_reproducao_bug_litellm: "Gerando novo roteiro de reprodução do bug…",
  notas_proposta_inicio: "Iniciando notas de proposta…",
  gerando_rascunho_notas_proposta: "Rascunho das notas (sem capturas ainda)…",
  planejando_instantes_captura_notas_proposta: "Escolhendo momentos de slide ou tela para captura…",
  capturando_frames_notas_proposta: "Capturando telas da reunião…",
  gerando_markdown_notas_proposta_litellm: "Gerando notas de proposta em Markdown…",
  verificacao_sustentacao_notas_proposta_litellm: "Verificando decisões e pendências vs transcrição…",
  verificacao_sustentacao_notas_proposta_concluida: "Verificação de sustentação concluída",
  notas_proposta_concluida: "Notas de proposta concluídas",
  regenerando_markdown_notas_proposta_litellm_agendado: "Regenerando notas de proposta…",
  regenerando_markdown_notas_proposta_litellm: "Gerando novas notas de proposta…",
  revisao_profunda_analista_litellm: "Revisão profunda: analista (plano)…",
  revisao_profunda_plano_concluido: "Revisão profunda: plano concluído…",
  revisao_profunda_worker_topico: "Revisão profunda: aprofundar tópico…",
  revisao_profunda_editor_final: "Revisão profunda: consolidação final…",
  revisao_profunda_analista_erro_parse: "Revisão profunda: erro ao ler plano…",
  verificacao_sustentacao_tutorial_litellm: "Verificando tutorial vs transcrição (possíveis inconsistências)…",
  verificacao_sustentacao_tutorial_concluida: "Verificação de sustentação concluída",
  verificacao_imagens_duplicadas_tutorial_litellm_visao: "Verificando imagens duplicadas (visão)…",
  verificacao_imagens_duplicadas_tutorial_concluida: "Verificação de imagens duplicadas concluída",
  regeneracao_tutorial_concluida: "Regeneração do tutorial concluída",
  regenerando_secao_markdown_litellm_agendado: "Regenerando seção (agendado)…",
  interpretando_escopo_pedido_edicao_secao_markdown_litellm: "Entendendo o escopo do seu pedido…",
  validando_escopo_edicao_secao_markdown: "Validando escopo no tutorial…",
  refinando_escopo_pedido_edicao_secao_markdown_litellm: "Ajustando escopo com IA…",
  escopo_edicao_secao_confirmado: "Escopo confirmado — gerando texto…",
  regenerando_secao_markdown_litellm: "Regenerando seção com IA…",
  regeneracao_secao_markdown_preview_pronta: "Pré-visualização da seção pronta",
  verificacao_redundancia_secao_markdown_litellm: "Verificando redundância com outras seções…",
  verificacao_redundancia_secao_markdown_concluida: "Verificação de redundância concluída",
  corrigindo_redundancia_secao_markdown_litellm: "Corrigindo redundância na seção…",
  verificacao_redundancia_secao_apos_correcao_automatica_litellm: "Reverificando seção após correção…",
  correcao_redundancia_secao_markdown_concluida: "Correção automática de redundância concluída",
  cancelado_pelo_usuario: "Cancelado",
  retry_reiniciando_pipeline_completo: "Reiniciando pipeline completo…",
  retry_retomando_pipeline_reutilizando_artefatos: "Retomando (reutilizando vídeo/áudio já no servidor)…",
  transcricao_reutilizada_snapshot_sem_retranscrever:
    "Retomando: transcrição já concluída (sem retranscrever o áudio)…",
  transcricao_recuperada_automaticamente_sem_retranscrever:
    "Transcrição recuperada automaticamente (snapshot ou checkpoint completo)…",
  rascunho_notas_reutilizado_sem_regenerar_litellm:
    "Retomando: rascunho das notas já salvo (sem nova chamada ao modelo)…",
  video_entrada_reutilizado_sem_redownload: "Vídeo já no servidor (sem novo download)…",
  audio_wav_reutilizado_sem_reextrair: "Áudio já extraído (sem novo ffmpeg)…",
  gerando_rascunho_tutorial_sem_imagens: "Rascunho do tutorial (sem capturas ainda)…",
  planejando_instantes_captura_frames_tutorial: "Escolhendo quais momentos merecem captura de tela…",
  capturando_frames_png_sob_demanda: "Capturando telas nos momentos do rascunho…",
  capturando_frame_png_sob_demanda: "Capturando tela (sob demanda)…",
  video_narrado_agendado: "Vídeo narrado: na fila…",
  video_narrado_alinhando_legendas: "Vídeo narrado: alinhando legendas…",
  video_narrado_validando_legendas: "Vídeo narrado: validando legendas…",
  video_narrado_limpando_legendas_ia: "Vídeo narrado: limpeza IA das legendas…",
  video_narrado_gerando_tts: "Vídeo narrado: gerando narração…",
  video_narrado_mux_ffmpeg: "Vídeo narrado: montando MP4…",
  video_narrado_atualizando_legendas_editadas: "Vídeo narrado: atualizando legendas editadas…",
  video_narrado_gerando_com_edicoes_modal: "Vídeo narrado: gerando com edições do modal…",
  video_narrado_remux_janelas_editadas: "Vídeo narrado: aplicando tempos de tela…",
  video_narrado_concluido: "Vídeo narrado concluído",
  video_narrado_falhou: "Vídeo narrado falhou",
};

const STATUS_JOB_PARA_ROTULO_PORTUGUES: Record<string, string> = {
  pending: "Na fila…",
  downloading: "Baixando vídeo…",
  extracting_audio: "Extraindo áudio…",
  transcribing: "Transcrevendo…",
  capturing_frames: "Capturando telas…",
  generating_tutorial: "Gerando tutorial…",
  completed: "Concluído",
  failed: "Falhou",
  cancelled: "Cancelado",
};

/** Formata segundos (ex.: posição no vídeo ou duração arredondada) como `m:ss`. */
export function formatarSegundosComoMmSsTranscribrothers(seg: number): string {
  const s = Math.max(0, Math.floor(seg));
  const m = Math.floor(s / 60);
  const r = s % 60;
  return `${m}:${String(r).padStart(2, "0")}`;
}

export type RegistroTempoInferenciaTrechoTranscricaoMultimodalTranscribrothers = {
  indice: number;
  inicio_segundos: number;
  fim_segundos: number;
  duracao_inferencia_segundos: number;
};

function numeroDeStepsJsonTranscribrothers(v: unknown): number | null {
  if (typeof v === "number" && Number.isFinite(v)) return v;
  if (typeof v === "string") {
    const n = Number(v);
    if (Number.isFinite(n)) return n;
  }
  return null;
}

/** Lista ordenada por trecho, vinda de `steps_json.transcricao_janelas_registros_tempo_inferencia`. */
export function extrairRegistrosTempoInferenciaTranscricaoJanelasDoStepsJsonTranscribrothers(
  steps: Record<string, unknown> | null | undefined,
): RegistroTempoInferenciaTrechoTranscricaoMultimodalTranscribrothers[] {
  const raw = steps?.transcricao_janelas_registros_tempo_inferencia;
  if (!Array.isArray(raw)) return [];
  const out: RegistroTempoInferenciaTrechoTranscricaoMultimodalTranscribrothers[] = [];
  for (const item of raw) {
    if (!item || typeof item !== "object") continue;
    const o = item as Record<string, unknown>;
    const indice = numeroDeStepsJsonTranscribrothers(o.indice);
    const ini = numeroDeStepsJsonTranscribrothers(o.inicio_segundos);
    const fim = numeroDeStepsJsonTranscribrothers(o.fim_segundos);
    const dur = numeroDeStepsJsonTranscribrothers(o.duracao_inferencia_segundos);
    if (indice === null || dur === null) continue;
    out.push({
      indice,
      inicio_segundos: ini ?? 0,
      fim_segundos: fim ?? 0,
      duracao_inferencia_segundos: dur,
    });
  }
  out.sort((a, b) => a.indice - b.indice);
  return out;
}

/** Linha secundária com janela X/Y, intervalo de tempo ou frame N/M (vindo de `steps_json`). */
export function obterLinhaDetalheSubetapaProgressoJobPipelinePortuguesTranscribrothers(
  steps: Record<string, unknown> | null | undefined,
): string {
  if (!steps || typeof steps !== "object") return "";
  const fase = typeof steps.pipeline_fase === "string" ? steps.pipeline_fase : "";

  if (fase === "transcrevendo_audio_janelas_litellm_multimodal_paralelo") {
    const jc = numeroDeStepsJsonTranscribrothers(steps.transcricao_janelas_concluidas);
    const jt = numeroDeStepsJsonTranscribrothers(steps.transcricao_janelas_total);
    const jpm = numeroDeStepsJsonTranscribrothers(steps.transcricao_janelas_paralelo_max);
    const ji = numeroDeStepsJsonTranscribrothers(steps.transcricao_janela_indice);
    const ini = numeroDeStepsJsonTranscribrothers(steps.transcricao_janela_inicio_segundos);
    const fim = numeroDeStepsJsonTranscribrothers(steps.transcricao_janela_fim_segundos);
    let partes: string[] = [];
    if (jc !== null && jt !== null) {
      partes.push(`${jc}/${jt} trechos concluídos`);
    }
    if (jpm !== null && jpm > 1) {
      partes.push(`até ${jpm} em paralelo`);
    }
    if (ji !== null && jt !== null && ini !== null && fim !== null) {
      partes.push(
        `último evento: trecho ${ji} (${formatarSegundosComoMmSsTranscribrothers(ini)}–${formatarSegundosComoMmSsTranscribrothers(fim)})`,
      );
    }
    if (partes.length > 0) return partes.join(" · ");
  }

  if (fase === "transcrevendo_audio_janela_litellm_multimodal") {
    const ji = numeroDeStepsJsonTranscribrothers(steps.transcricao_janela_indice);
    const jt = numeroDeStepsJsonTranscribrothers(steps.transcricao_janelas_total);
    const ini = numeroDeStepsJsonTranscribrothers(steps.transcricao_janela_inicio_segundos);
    const fim = numeroDeStepsJsonTranscribrothers(steps.transcricao_janela_fim_segundos);
    if (ji !== null && jt !== null) {
      let tempo = "";
      if (ini !== null && fim !== null) {
        tempo = ` — ${formatarSegundosComoMmSsTranscribrothers(ini)} a ${formatarSegundosComoMmSsTranscribrothers(fim)}`;
      }
      return `Trecho ${ji} de ${jt}${tempo}`;
    }
  }

  if (fase === "transcrevendo_audio_litellm_multimodal_arquivo_unico") {
    return "Envio do WAV completo em uma única chamada (janela 0 s no servidor).";
  }

  if (fase === "capturando_frame_png_individual") {
    const fi = numeroDeStepsJsonTranscribrothers(steps.captura_frame_indice);
    const ft = numeroDeStepsJsonTranscribrothers(steps.captura_frames_total);
    const ts = numeroDeStepsJsonTranscribrothers(steps.captura_frame_timestamp_segundos);
    if (fi !== null && ft !== null) {
      const noVideo = ts !== null ? ` (~${formatarSegundosComoMmSsTranscribrothers(ts)} no vídeo)` : "";
      return `Screenshot ${fi} de ${ft}${noVideo}`;
    }
  }

  if (fase === "gerando_tutorial_http_chat_completions") {
    const n = numeroDeStepsJsonTranscribrothers(steps.geracao_tutorial_litellm_total_imagens);
    if (n !== null && n > 0) {
      return `${n} imagem(ns) do Markdown atual anexada(s) ao pedido (multimodal); POST ao LiteLLM pode levar vários minutos.`;
    }
    return "Modo texto: transcrição + caminhos em assets/ (sem envio de pixels ao modelo).";
  }

  if (fase === "revisao_profunda_worker_topico") {
    const i = numeroDeStepsJsonTranscribrothers(steps.revisao_profunda_indice);
    const t = numeroDeStepsJsonTranscribrothers(steps.revisao_profunda_total);
    if (i !== null && t !== null) {
      return `Tópico ${i} de ${t}`;
    }
  }

  if (fase === "video_narrado_gerando_tts") {
    const i = numeroDeStepsJsonTranscribrothers(steps.video_narrado_tts_cue_indice);
    const t = numeroDeStepsJsonTranscribrothers(steps.video_narrado_tts_cue_total);
    const preview =
      typeof steps.video_narrado_tts_cue_preview === "string"
        ? steps.video_narrado_tts_cue_preview.trim()
        : "";
    const puladas = numeroDeStepsJsonTranscribrothers(steps.video_narrado_tts_cues_puladas);
    const partes: string[] = [];
    if (i !== null && t !== null && t > 0) {
      partes.push(`Trecho ${i} de ${t}`);
    }
    if (preview) {
      partes.push(`«${preview}»`);
    }
    if (puladas !== null && puladas > 0) {
      partes.push(`${puladas} pulado(s)`);
    }
    if (partes.length > 0) return partes.join(" · ");
    return "Sintetizando narração trecho a trecho (pode levar vários minutos)…";
  }

  if (fase === "video_narrado_limpando_legendas_ia") {
    const resumo =
      typeof steps.video_narrado_limpeza_ia_resumo === "string"
        ? steps.video_narrado_limpeza_ia_resumo.trim()
        : "";
    const modelo =
      typeof steps.video_narrado_limpeza_ia_modelo_atual === "string"
        ? steps.video_narrado_limpeza_ia_modelo_atual.trim()
        : "";
    const partes: string[] = [];
    if (resumo) partes.push(resumo);
    else partes.push("Removendo lixo de Markdown/âncoras nas legendas com modelo de chat…");
    if (modelo) partes.push(`modelo: ${modelo}`);
    return partes.join(" · ");
  }

  if (fase === "video_narrado_mux_ffmpeg") {
    const i = numeroDeStepsJsonTranscribrothers(steps.video_narrado_mux_segmento_indice);
    const t = numeroDeStepsJsonTranscribrothers(steps.video_narrado_mux_segmento_total);
    const muxFase =
      typeof steps.video_narrado_mux_fase === "string" ? steps.video_narrado_mux_fase : "";
    const paralelismo = numeroDeStepsJsonTranscribrothers(steps.video_narrado_mux_paralelismo);
    const cacheHits = numeroDeStepsJsonTranscribrothers(steps.video_narrado_mux_segmentos_cache);
    if (muxFase === "precorte") {
      const extra =
        paralelismo !== null && paralelismo > 1 ? ` · ${paralelismo} em paralelo` : "";
      return i !== null && t !== null && t > 0
        ? `Cortando janelas ${i} de ${t} (clips pequenos)${extra}…`
        : "Cortando janelas do vídeo em clips pequenos…";
    }
    if (muxFase === "passagem_unica" || muxFase === "passagem_unica_ok") {
      const encoder =
        typeof steps.video_narrado_mux_encoder === "string"
          ? steps.video_narrado_mux_encoder.trim()
          : "";
      const encTxt =
        encoder === "h264_nvenc" ? " · GPU" : encoder === "libx264" ? " · CPU" : "";
      return t !== null && t > 0
        ? `Montando MP4 em uma passagem (${t} cues → 1 encode)${encTxt}…`
        : `Montando MP4 em uma passagem (ffmpeg)${encTxt}…`;
    }
    if (muxFase === "fallback_paralelo") {
      return "Passagem única falhou — montando segmentos em paralelo…";
    }
    if (muxFase === "concat") {
      return "Concatenando segmentos do vídeo narrado…";
    }
    if (muxFase === "segmento_cache" && i !== null && t !== null && t > 0) {
      return `Reusando cache ${i} de ${t} segmentos…`;
    }
    if (i !== null && t !== null && t > 0) {
      const extra =
        paralelismo !== null && paralelismo > 1 ? ` · ${paralelismo} em paralelo` : "";
      const cacheTxt =
        cacheHits !== null && cacheHits > 0 ? ` · ${cacheHits} do cache` : "";
      return `Montando segmento ${i} de ${t} (vídeo + fala)${extra}${cacheTxt}`;
    }
    return "Montando MP4 com áudio narrado…";
  }

  return "";
}

export function obterDescricaoLegivelProgressoJobPipelinePortuguesTranscribrothers(
  status: string,
  pipelineFase: unknown,
): string {
  const terminal = status === "completed" || status === "failed" || status === "cancelled";
  if (terminal) {
    const porStatus = STATUS_JOB_PARA_ROTULO_PORTUGUES[status];
    if (porStatus) return porStatus;
  }
  if (typeof pipelineFase === "string" && pipelineFase.trim()) {
    const porFase = PIPELINE_FASE_PARA_ROTULO_PORTUGUES[pipelineFase];
    if (porFase) return porFase;
  }
  const porStatus = STATUS_JOB_PARA_ROTULO_PORTUGUES[status];
  if (porStatus) return porStatus;
  return status;
}
