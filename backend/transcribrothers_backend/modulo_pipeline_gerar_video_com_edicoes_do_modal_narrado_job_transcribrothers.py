"""Orquestra salvar VTT/janelas + TTS parcial + remux honrando a timeline VTT do modal."""

from __future__ import annotations

import asyncio
import traceback
import wave
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm.attributes import flag_modified

from transcribrothers_backend.modulo_api_janelas_video_e_wavs_por_cue_narracao_job_transcribrothers import (
    obter_caminho_wav_narracao_por_cue_se_existir_transcribrothers,
)
from transcribrothers_backend.modulo_api_salvar_legendas_documento_alinhadas_vtt_editadas_job_transcribrothers import (
    salvar_legendas_documento_alinhadas_vtt_editadas_no_job_transcribrothers,
    validar_e_normalizar_cues_legendas_editadas_para_vtt_transcribrothers,
)
from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    JobPipelineTranscribrothers,
    StatusJobTranscribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    ErroFfmpegTranscribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_montar_video_narrado_por_segmentos_retarget_audio_transcribrothers import (
    montar_video_narrado_por_segmentos_retarget_audio_via_ffmpeg_transcribrothers,
)
from transcribrothers_backend.modulo_ffmpeg_substituir_audio_video_por_narracao_tts_wav_transcribrothers import (
    CHAVE_STEPS_JSON_VIDEO_COM_NARRACAO_TTS_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    CHAVE_STEPS_JSON_NARRACAO_TTS_TRANSCRIBROTHERS,
    NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS,
    gerar_narracao_tts_wavs_individuais_por_cue_e_concatenar_via_litellm_transcribrothers,
)
from transcribrothers_backend.modulo_alinhar_frases_markdown_aos_segmentos_transcricao_para_legendas_transcribrothers import (
    CueLegendaAlinhadaTranscribrothers,
)
from transcribrothers_backend.modulo_montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers import (
    CueNarracaoComJanelaVideoTranscribrothers,
    ResultadoCuesNarracaoComJanelasVideoTranscribrothers,
)
from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    obter_duracao_video_segundos_via_ffprobe,
)
from transcribrothers_backend.modulo_persistencia_manifest_cues_narracao_janelas_video_job_transcribrothers import (
    carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers,
    cues_janela_a_partir_manifest_transcribrothers,
    gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers,
    indices_cues_com_texto_diferente_do_manifest_transcribrothers,
    normalizar_texto_cue_para_comparacao_narracao_transcribrothers,
)
from transcribrothers_backend.modulo_util_texto_efetivo_para_tts_cue_legenda_ou_override_transcribrothers import (
    texto_efetivo_para_tts_cue_narracao_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers import (
    CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS,
    FASE_VIDEO_NARRADO_CONCLUIDO,
    FASE_VIDEO_NARRADO_FALHOU,
    FASE_VIDEO_NARRADO_GERANDO_TTS,
    FASE_VIDEO_NARRADO_MUX_FFMPEG,
    FASE_VIDEO_NARRADO_VALIDANDO_LEGENDAS,
    _localizar_arquivo_video_entrada_no_diretorio_job,
)
from transcribrothers_backend.modulo_util_gerar_arquivo_vtt_a_partir_cues_legendas_transcribrothers import (
    CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS,
    gravar_arquivo_vtt_a_partir_cues_legendas_transcribrothers,
)
from transcribrothers_backend.modulo_util_montar_segmentos_retarget_respeitando_timeline_vtt_cues_editadas_transcribrothers import (
    CueEdicaoModalNarradoParaMontagemTimelineVttTranscribrothers,
    gravar_wav_silencio_pcm16_mono_segundos_transcribrothers,
    montar_lista_segmentos_retarget_a_partir_cues_vtt_janelas_e_wavs_transcribrothers,
)
from transcribrothers_backend.modulo_validar_cues_janelas_video_antes_narracao_tts_transcribrothers import (
    validar_cues_janelas_video_antes_narracao_tts_transcribrothers,
)

FASE_VIDEO_NARRADO_GERANDO_COM_EDICOES_MODAL = "video_narrado_gerando_com_edicoes_modal"
_NOME_SUBPASTA_WAVS_POR_CUE = "wavs_narracao_por_cue"
_NOME_SUBPASTA_WAVS_TIMELINE_VTT = "wavs_timeline_vtt_edicoes_modal"


def _diretorio_trabalho_job(data_dir: Path, job_id: str) -> Path:
    return data_dir / "jobs" / job_id


def _diretorio_assets_do_job(data_dir: Path, job_id: str) -> Path:
    return _diretorio_trabalho_job(data_dir, job_id) / "assets_exportados_para_markdown"


async def _atualizar_steps_job_transcribrothers(
    session_factory: async_sessionmaker[AsyncSession],
    job_id: str,
    *,
    steps: dict[str, Any],
    status: StatusJobTranscribrothers | None = None,
    error: str | None = None,
    limpar_mensagem_erro: bool = False,
) -> None:
    async with session_factory() as session:
        row = await session.get(JobPipelineTranscribrothers, job_id)
        if row is None:
            return
        if status is not None:
            row.status = status.value
        if limpar_mensagem_erro:
            row.error_message = None
        elif error is not None:
            row.error_message = error
        row.steps_json = steps
        flag_modified(row, "steps_json")
        row.updated_at = datetime.now(timezone.utc)
        await session.commit()


def gravar_wav_silencio_para_cue_sem_narracao_com_duracao_da_janela_transcribrothers(
    *,
    caminho_wav_saida: Path,
    inicio_video_segundos: float,
    fim_video_segundos: float,
) -> Path:
    """Áudio mudo com a duração da janela de tela — custo de mux = tempo que entra no MP4."""
    ini = max(0.0, float(inicio_video_segundos))
    fim = max(ini, float(fim_video_segundos))
    dur = max(0.05, fim - ini)
    return gravar_wav_silencio_pcm16_mono_segundos_transcribrothers(caminho_wav_saida, dur)


def _concatenar_wavs_pcm16_mono_em_arquivo_transcribrothers(
    caminhos: list[Path],
    caminho_saida: Path,
) -> None:
    if not caminhos:
        raise ValueError("Nenhum WAV para concatenar.")
    pcm = bytearray()
    rate: int | None = None
    for caminho in caminhos:
        with wave.open(str(caminho), "rb") as wf:
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2:
                raise ValueError(f"WAV inválido para concat: {caminho.name}")
            if rate is None:
                rate = wf.getframerate()
            elif wf.getframerate() != rate:
                raise ValueError("Sample rates diferentes ao concatenar WAVs da timeline.")
            pcm.extend(wf.readframes(wf.getnframes()))
    assert rate is not None
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(caminho_saida), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(bytes(pcm))


def _normalizar_voz_tts_efetiva_para_cue_transcribrothers(voz: str, voz_padrao: str) -> str:
    from transcribrothers_backend.modulo_preferencias_voz_tts_gemini_narracao_transcribrothers import (
        VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS,
        normalizar_voz_tts_gemini_transcribrothers,
    )

    padrao = (voz_padrao or "").strip() or VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS
    try:
        return normalizar_voz_tts_gemini_transcribrothers((voz or "").strip() or padrao)
    except ValueError:
        try:
            return normalizar_voz_tts_gemini_transcribrothers(padrao)
        except ValueError:
            return VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS


def _resolver_cues_janela_a_partir_edicoes_modal_transcribrothers(
    *,
    work: Path,
    textos_desejados: list[str],
    flags_sem_narracao: list[bool],
    vozes_desejadas: list[str],
    voz_padrao: str,
    janelas_brutas: list[dict[str, Any]] | None,
    textos_tts_desejados: list[str] | None = None,
) -> tuple[list[CueNarracaoComJanelaVideoTranscribrothers], list[int]]:
    """
    Retorna cues com janelas + índices que precisam de TTS novo.

    Se a quantidade de cues mudou (ex.: exclusão no modal) e há janelas no payload,
    reconstrói a lista a partir do payload (TTS novo em todas as cues com narração).

    Dirty de TTS compara o texto efetivo de fala (override ``texto_tts`` ou legenda),
    não a legenda sozinha — assim dá para ajustar a legenda sem regenerar áudio.
    """
    manifest = carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers(work)
    if manifest is None:
        raise RuntimeError(
            "Não há manifesto de janelas de tela. Gere o vídeo narrado antes de aplicar edições."
        )
    if len(flags_sem_narracao) != len(textos_desejados):
        raise RuntimeError("Flags sem_narracao não batem com a quantidade de cues.")
    if len(vozes_desejadas) != len(textos_desejados):
        raise RuntimeError("Lista de vozes não bate com a quantidade de cues.")
    if not textos_desejados:
        raise RuntimeError("Informe ao menos uma cue para gerar o vídeo narrado.")

    if textos_tts_desejados is None:
        textos_tts_norm = [""] * len(textos_desejados)
    else:
        if len(textos_tts_desejados) != len(textos_desejados):
            raise RuntimeError("Lista de texto_tts não bate com a quantidade de cues.")
        textos_tts_norm = [
            normalizar_texto_cue_para_comparacao_narracao_transcribrothers(t)
            for t in textos_tts_desejados
        ]

    vozes_norm = [
        _normalizar_voz_tts_efetiva_para_cue_transcribrothers(v, voz_padrao) for v in vozes_desejadas
    ]
    lista_encolheu_ou_cresceu = len(manifest) != len(textos_desejados)

    if lista_encolheu_ou_cresceu:
        if janelas_brutas is None or len(janelas_brutas) != len(textos_desejados):
            raise RuntimeError(
                "Ao excluir ou alterar a quantidade de cues, envie os tempos de tela "
                f"de cada cue restante ({len(textos_desejados)} janela(s))."
            )
        cues_finais: list[CueNarracaoComJanelaVideoTranscribrothers] = []
        for texto, texto_tts, janela, sem_narracao, voz in zip(
            textos_desejados,
            textos_tts_norm,
            janelas_brutas,
            flags_sem_narracao,
            vozes_norm,
            strict=True,
        ):
            try:
                ini = float(janela["inicio_video_segundos"])
                fim = float(janela["fim_video_segundos"])
            except (KeyError, TypeError, ValueError) as exc:
                raise RuntimeError("Tempos de tela inválidos no payload.") from exc
            if fim + 1e-9 < ini:
                raise RuntimeError("Tempos de tela: fim anterior ao início.")
            cues_finais.append(
                CueNarracaoComJanelaVideoTranscribrothers(
                    texto=normalizar_texto_cue_para_comparacao_narracao_transcribrothers(texto),
                    inicio_video_segundos=ini,
                    fim_video_segundos=fim,
                    origem_ancora="edicao_modal",
                    casado=True,
                    sem_narracao=bool(sem_narracao),
                    voz_tts=voz,
                    texto_tts=texto_tts,
                )
            )
        # Remapeamento de índices: regenera TTS de tudo que ainda tem fala.
        indices_tts = [i for i, c in enumerate(cues_finais) if not c.sem_narracao]
        return cues_finais, indices_tts

    cues_base = cues_janela_a_partir_manifest_transcribrothers(manifest)
    textos_tts_efetivos_desejados = [
        texto_efetivo_para_tts_cue_narracao_transcribrothers(
            texto_legenda=texto,
            texto_tts=texto_tts,
        )
        for texto, texto_tts in zip(textos_desejados, textos_tts_norm, strict=True)
    ]
    textos_tts_efetivos_manifest = [
        texto_efetivo_para_tts_cue_narracao_transcribrothers(
            texto_legenda=m.texto,
            texto_tts=str(getattr(m, "texto_tts", "") or ""),
        )
        for m in manifest
    ]
    indices_texto_sujo = indices_cues_com_texto_diferente_do_manifest_transcribrothers(
        textos_manifest=textos_tts_efetivos_manifest,
        textos_desejados=textos_tts_efetivos_desejados,
    )

    if janelas_brutas is not None:
        if len(janelas_brutas) != len(cues_base):
            raise RuntimeError(
                "A quantidade de tempos de tela não bate com as cues "
                f"({len(janelas_brutas)} vs {len(cues_base)})."
            )
        cues_finais = []
        for cue, texto, texto_tts, janela, sem_narracao, voz in zip(
            cues_base,
            textos_desejados,
            textos_tts_norm,
            janelas_brutas,
            flags_sem_narracao,
            vozes_norm,
            strict=True,
        ):
            try:
                ini = float(janela["inicio_video_segundos"])
                fim = float(janela["fim_video_segundos"])
            except (KeyError, TypeError, ValueError) as exc:
                raise RuntimeError("Tempos de tela inválidos no payload.") from exc
            if fim + 1e-9 < ini:
                raise RuntimeError("Tempos de tela: fim anterior ao início.")
            cues_finais.append(
                CueNarracaoComJanelaVideoTranscribrothers(
                    texto=normalizar_texto_cue_para_comparacao_narracao_transcribrothers(texto),
                    inicio_video_segundos=ini,
                    fim_video_segundos=fim,
                    origem_ancora=cue.origem_ancora,
                    casado=cue.casado,
                    sem_narracao=bool(sem_narracao),
                    voz_tts=voz,
                    texto_tts=texto_tts,
                )
            )
    else:
        cues_finais = [
            CueNarracaoComJanelaVideoTranscribrothers(
                texto=normalizar_texto_cue_para_comparacao_narracao_transcribrothers(texto),
                inicio_video_segundos=cue.inicio_video_segundos,
                fim_video_segundos=cue.fim_video_segundos,
                origem_ancora=cue.origem_ancora,
                casado=cue.casado,
                sem_narracao=bool(sem_narracao),
                voz_tts=voz,
                texto_tts=texto_tts,
            )
            for cue, texto, texto_tts, sem_narracao, voz in zip(
                cues_base,
                textos_desejados,
                textos_tts_norm,
                flags_sem_narracao,
                vozes_norm,
                strict=True,
            )
        ]

    indices_tts: list[int] = []
    for i, cue in enumerate(cues_finais):
        if cue.sem_narracao:
            continue
        era_muda = bool(manifest[i].sem_narracao)
        texto_mudou = i in indices_texto_sujo
        voz_manifest = _normalizar_voz_tts_efetiva_para_cue_transcribrothers(
            str(getattr(manifest[i], "voz_tts", "") or ""),
            voz_padrao,
        )
        voz_mudou = voz_manifest != cue.voz_tts
        if era_muda or texto_mudou or voz_mudou:
            indices_tts.append(i)
    return cues_finais, indices_tts


async def executar_gerar_video_com_edicoes_do_modal_narrado_em_background(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    modelo_tts: str,
    cues_brutas: list[dict[str, Any]],
    janelas_brutas: list[dict[str, Any]] | None,
) -> None:
    data_dir = configuracao.transcribrothers_data_dir.resolve()
    work = _diretorio_trabalho_job(data_dir, job_id)
    assets = _diretorio_assets_do_job(data_dir, job_id)
    steps: dict[str, Any] = {}
    try:
        async with session_factory() as session:
            row = await session.get(JobPipelineTranscribrothers, job_id)
            if row is None:
                return
            steps = dict(row.steps_json or {})

        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_GERANDO_COM_EDICOES_MODAL
        await _atualizar_steps_job_transcribrothers(
            session_factory,
            job_id,
            steps=steps,
            status=StatusJobTranscribrothers.generating_tutorial,
            limpar_mensagem_erro=True,
        )

        cues_vtt = validar_e_normalizar_cues_legendas_editadas_para_vtt_transcribrothers(cues_brutas)
        resultado_salvar = salvar_legendas_documento_alinhadas_vtt_editadas_no_job_transcribrothers(
            job_id=job_id,
            diretorio_assets=assets,
            steps_json=steps,
            cues_brutas=[
                {
                    "inicio_segundos": c.inicio_segundos,
                    "fim_segundos": c.fim_segundos,
                    "texto": c.texto,
                    "sem_narracao": c.sem_narracao,
                    "voz_tts": c.voz_tts,
                    "texto_tts": getattr(c, "texto_tts", "") or "",
                    "forcar_regenerar_tts": bool(getattr(c, "forcar_regenerar_tts", False)),
                }
                for c in cues_vtt
            ],
        )
        steps = dict(resultado_salvar.steps_json_atualizado)

        textos = [c.texto for c in cues_vtt]
        textos_tts = [str(getattr(c, "texto_tts", "") or "") for c in cues_vtt]
        flags_sem_narracao = [bool(c.sem_narracao) for c in cues_vtt]
        from transcribrothers_backend.modulo_persistencia_runtime_config_voz_tts_narracao_sqlite_transcribrothers import (
            carregar_voz_tts_narracao_do_session_factory_transcribrothers,
        )
        from transcribrothers_backend.modulo_preferencias_voz_tts_gemini_narracao_transcribrothers import (
            VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS,
        )

        voz_padrao_job = str(
            steps.get("pipeline_video_narrado_voz_tts") or ""
        ).strip() or await carregar_voz_tts_narracao_do_session_factory_transcribrothers(
            session_factory
        )
        voz_padrao_job = voz_padrao_job or VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS
        vozes_desejadas = [str(getattr(c, "voz_tts", "") or "") for c in cues_vtt]
        cues_janela, indices_sujos = _resolver_cues_janela_a_partir_edicoes_modal_transcribrothers(
            work=work,
            textos_desejados=textos,
            textos_tts_desejados=textos_tts,
            flags_sem_narracao=flags_sem_narracao,
            vozes_desejadas=vozes_desejadas,
            voz_padrao=voz_padrao_job,
            janelas_brutas=janelas_brutas,
        )
        # Regenerar forçado na UI (botão «Regenerar») mesmo sem mudança de texto/voz.
        for i, c in enumerate(cues_vtt):
            if bool(getattr(c, "forcar_regenerar_tts", False)) and not c.sem_narracao:
                if i not in indices_sujos:
                    indices_sujos.append(i)
        indices_sujos = sorted(set(indices_sujos))

        video = _localizar_arquivo_video_entrada_no_diretorio_job(work)
        if video is None or not video.is_file():
            raise RuntimeError("Vídeo de entrada não encontrado.")
        duracao_video = await obter_duracao_video_segundos_via_ffprobe(video)
        if duracao_video <= 0:
            raise RuntimeError("Não foi possível obter a duração do vídeo (ffprobe).")

        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_VALIDANDO_LEGENDAS
        steps["video_narrado_edicoes_modal_cues_sujas"] = len(indices_sujos)
        await _atualizar_steps_job_transcribrothers(session_factory, job_id, steps=steps)

        resultado_cues = ResultadoCuesNarracaoComJanelasVideoTranscribrothers(
            cues=cues_janela,
            modo="edicoes_modal_narrado",
            quantidade_ancoras_markdown=0,
            quantidade_casadas=sum(1 for c in cues_janela if c.casado),
            quantidade_interpoladas=sum(1 for c in cues_janela if not c.casado),
        )
        validacao = validar_cues_janelas_video_antes_narracao_tts_transcribrothers(
            resultado_cues,
            duracao_video_segundos=duracao_video,
        )
        if not validacao.ok:
            raise RuntimeError(
                validacao.motivo_rejeicao
                or "Janelas de tela incompatíveis com o vídeo; geração abortada."
            )

        dir_wavs_cue = work / _NOME_SUBPASTA_WAVS_POR_CUE
        dir_wavs_cue.mkdir(parents=True, exist_ok=True)
        caminho_wav_concat = assets / NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS
        caminhos_wav_por_cue: list[Path | None] = [None] * len(cues_janela)

        if indices_sujos:
            from transcribrothers_backend.modulo_promover_preview_tts_cue_validada_para_wav_definitivo_narracao_transcribrothers import (
                promover_previews_validas_e_listar_indices_ainda_precisam_tts_transcribrothers,
            )

            # Só promove prévia→definitivo se a quantidade de cues não mudou (índices estáveis).
            manifest_antes = carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers(
                work
            )
            quantidade_estavel = (
                manifest_antes is not None and len(manifest_antes) == len(cues_janela)
            )
            vozes_por_cue = [c.voz_tts or voz_padrao_job for c in cues_janela]
            textos_tts_efetivos = [
                texto_efetivo_para_tts_cue_narracao_transcribrothers(
                    texto_legenda=c.texto,
                    texto_tts=c.texto_tts,
                )
                for c in cues_janela
            ]
            indices_ainda_tts, indices_promovidos, caminhos_promovidos = (
                promover_previews_validas_e_listar_indices_ainda_precisam_tts_transcribrothers(
                    work=work,
                    indices_sujos=list(indices_sujos),
                    textos_por_indice=textos_tts_efetivos,
                    vozes_por_indice=vozes_por_cue,
                    flags_sem_narracao=[bool(c.sem_narracao) for c in cues_janela],
                    quantidade_cues_estavel=quantidade_estavel,
                )
            )
            for i, caminho_prom in caminhos_promovidos.items():
                caminhos_wav_por_cue[i] = caminho_prom

            steps["pipeline_fase"] = FASE_VIDEO_NARRADO_GERANDO_TTS
            steps["video_narrado_tts_cue_indice"] = 0
            steps["video_narrado_tts_cue_total"] = len(cues_janela)
            steps["video_narrado_edicoes_modal_cues_previas_promovidas"] = len(indices_promovidos)
            steps["video_narrado_edicoes_modal_indices_previas_promovidas"] = list(
                indices_promovidos
            )
            await _atualizar_steps_job_transcribrothers(session_factory, job_id, steps=steps)

            async def _progresso_tts(sub: dict[str, Any]) -> None:
                steps.update(sub)
                await _atualizar_steps_job_transcribrothers(session_factory, job_id, steps=steps)

            steps["pipeline_video_narrado_voz_tts"] = voz_padrao_job
            # Mesmo sem cues a regenerar via LiteLLM, chama com set vazio para reutilizar
            # WAVs (incl. promovidos) e remontar o WAV concatenado do documento.
            resultado_tts = await gerar_narracao_tts_wavs_individuais_por_cue_e_concatenar_via_litellm_transcribrothers(
                trechos=textos_tts_efetivos,
                modelo=modelo_tts,
                configuracao=configuracao,
                diretorio_wavs_por_cue=dir_wavs_cue,
                caminho_wav_concatenado=caminho_wav_concat,
                atualizar_progresso=_progresso_tts,
                indices_a_regenerar=set(indices_ainda_tts),
                preservar_indices_da_entrada=True,
                voz=voz_padrao_job,
                vozes_por_cue=vozes_por_cue,
            )
            if not resultado_tts.ok:
                raise RuntimeError(resultado_tts.mensagem)
            for i, p in enumerate(resultado_tts.caminhos_wav_por_cue):
                caminhos_wav_por_cue[i] = p
            steps[CHAVE_STEPS_JSON_NARRACAO_TTS_TRANSCRIBROTHERS] = {
                "nome_arquivo": resultado_tts.nome_arquivo_concatenado,
                "url_asset": f"/api/jobs/{job_id}/assets/{resultado_tts.nome_arquivo_concatenado}",
                "modelo": resultado_tts.modelo,
                "texto_caracteres": resultado_tts.texto_caracteres,
                "texto_truncado": False,
                "quantidade_cues": resultado_tts.quantidade_cues,
                "quantidade_cues_regeneradas": len(indices_ainda_tts),
                "indices_cues_regeneradas": list(indices_ainda_tts),
                "quantidade_cues_previas_promovidas": len(indices_promovidos),
                "indices_cues_previas_promovidas": list(indices_promovidos),
                "gerado_em": datetime.now(timezone.utc).isoformat(),
                "edicoes_modal_narrado": True,
            }
        else:
            for i in range(len(cues_janela)):
                if cues_janela[i].sem_narracao:
                    continue
                caminho = obter_caminho_wav_narracao_por_cue_se_existir_transcribrothers(work, i)
                if caminho is None:
                    raise RuntimeError(
                        f"Falta o áudio da cue {i + 1}. Gere a narração antes de aplicar edições."
                    )
                caminhos_wav_por_cue[i] = caminho

        # Cues mudas: silêncio = duração da janela (sempre, barato e evita TTS/mux errado).
        indices_sem_narracao = [i for i, c in enumerate(cues_janela) if c.sem_narracao]
        for i in indices_sem_narracao:
            cue = cues_janela[i]
            caminho_silencio = dir_wavs_cue / f"cue_narracao_{i:04d}.wav"
            gravar_wav_silencio_para_cue_sem_narracao_com_duracao_da_janela_transcribrothers(
                caminho_wav_saida=caminho_silencio,
                inicio_video_segundos=cue.inicio_video_segundos,
                fim_video_segundos=cue.fim_video_segundos,
            )
            caminhos_wav_por_cue[i] = caminho_silencio

        caminhos_finais: list[Path] = []
        for i, p in enumerate(caminhos_wav_por_cue):
            if p is None or not p.is_file():
                raise RuntimeError(f"Falta o áudio da cue {i + 1} após preparar narração/silêncio.")
            caminhos_finais.append(p)
        caminhos_wav_por_cue_ok = caminhos_finais

        gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers(
            work=work,
            cues=cues_janela,
        )

        cues_montagem = [
            CueEdicaoModalNarradoParaMontagemTimelineVttTranscribrothers(
                inicio_vtt_segundos=c.inicio_segundos,
                fim_vtt_segundos=c.fim_segundos,
                inicio_video_segundos=j.inicio_video_segundos,
                fim_video_segundos=j.fim_video_segundos,
                caminho_wav=wav,
                texto=c.texto,
            )
            for c, j, wav in zip(cues_vtt, cues_janela, caminhos_wav_por_cue_ok, strict=True)
        ]
        dir_prep = work / _NOME_SUBPASTA_WAVS_TIMELINE_VTT
        montagem = montar_lista_segmentos_retarget_a_partir_cues_vtt_janelas_e_wavs_transcribrothers(
            cues=cues_montagem,
            diretorio_wavs_preparados=dir_prep,
        )
        segmentos = montagem.segmentos
        _concatenar_wavs_pcm16_mono_em_arquivo_transcribrothers(
            [s.caminho_wav for s in segmentos],
            caminho_wav_concat,
        )

        # VTT contíguo do MP4 denso (só cues, sem gaps) — igual ao play cue→cue do modal.
        cues_vtt_densas: list[CueLegendaAlinhadaTranscribrothers] = []
        t_cursor = 0.0
        for texto, dur in zip(
            montagem.textos_na_ordem,
            montagem.duracoes_audio_na_ordem,
            strict=True,
        ):
            d = max(0.05, float(dur))
            cues_vtt_densas.append(
                CueLegendaAlinhadaTranscribrothers(
                    texto=texto,
                    inicio_segundos=t_cursor,
                    fim_segundos=t_cursor + d,
                    casado=True,
                )
            )
            t_cursor += d
        caminho_vtt = gravar_arquivo_vtt_a_partir_cues_legendas_transcribrothers(
            diretorio_assets=assets,
            cues=cues_vtt_densas,
        )

        stamp_cache = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        url_vtt = f"/api/jobs/{job_id}/assets/{caminho_vtt.name}?v={stamp_cache}"
        steps[CHAVE_STEPS_JSON_NARRACAO_TTS_TRANSCRIBROTHERS] = {
            **dict(steps.get(CHAVE_STEPS_JSON_NARRACAO_TTS_TRANSCRIBROTHERS) or {}),
            "nome_arquivo": caminho_wav_concat.name,
            "url_asset": f"/api/jobs/{job_id}/assets/{caminho_wav_concat.name}?v={stamp_cache}",
            "timeline": "narracao_densa_edicoes_modal",
            "gerado_em": datetime.now(timezone.utc).isoformat(),
            "edicoes_modal_narrado": True,
        }
        steps[CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS] = {
            **dict(steps.get(CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS) or {}),
            "nome_arquivo": caminho_vtt.name,
            "url_asset": url_vtt,
            "quantidade_cues": len(cues_vtt_densas),
            "timeline": "narracao_densa_edicoes_modal",
            "edicoes_modal_em": datetime.now(timezone.utc).isoformat(),
        }

        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_MUX_FFMPEG
        steps["video_narrado_mux_segmento_indice"] = 0
        steps["video_narrado_mux_segmento_total"] = len(segmentos)
        await _atualizar_steps_job_transcribrothers(session_factory, job_id, steps=steps)

        async def _progresso_mux(sub: dict[str, Any]) -> None:
            steps.update(sub)
            await _atualizar_steps_job_transcribrothers(session_factory, job_id, steps=steps)

        from transcribrothers_backend.modulo_persistencia_runtime_config_encode_video_narrado_sqlite_transcribrothers import (
            carregar_preferencias_encode_video_narrado_do_session_factory_transcribrothers,
        )

        prefs_encode = await carregar_preferencias_encode_video_narrado_do_session_factory_transcribrothers(
            session_factory
        )
        steps["video_narrado_mux_encode_resolucao"] = prefs_encode.resolucao
        steps["video_narrado_mux_encode_fps"] = int(prefs_encode.fps)
        caminho_mp4 = await montar_video_narrado_por_segmentos_retarget_audio_via_ffmpeg_transcribrothers(
            caminho_video=video,
            segmentos=segmentos,
            diretorio_trabalho=work,
            diretorio_saida=work,
            atualizar_progresso=_progresso_mux,
            preferencias_encode=prefs_encode,
        )
        url_mp4 = f"/api/jobs/{job_id}/video-com-narracao-tts?v={stamp_cache}"
        steps[CHAVE_STEPS_JSON_VIDEO_COM_NARRACAO_TTS_TRANSCRIBROTHERS] = {
            "nome_arquivo": caminho_mp4.name,
            "url_download": url_mp4,
            "modo_montagem": "segmentos_retarget_denso_edicoes_modal",
            "quantidade_segmentos": len(segmentos),
            "gerado_em": datetime.now(timezone.utc).isoformat(),
            "edicoes_modal_narrado": True,
        }
        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_CONCLUIDO
        steps[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS] = {
            "ok": True,
            "mensagem": (
                "Vídeo narrado gerado com as edições do modal "
                f"({len(indices_sujos)} cue(s) com TTS novo; só trechos com cue, sem gaps)."
            ),
            "edicoes_modal_narrado": True,
            "quantidade_cues_regeneradas": len(indices_sujos),
            "quantidade_cues_reutilizadas": len(cues_janela) - len(indices_sujos),
            "concluido_em": datetime.now(timezone.utc).isoformat(),
        }
        from transcribrothers_backend.modulo_persistencia_versoes_video_narrado_job_transcribrothers import (
            tentar_criar_snapshot_versao_video_narrado_apos_sucesso_silencioso_transcribrothers,
        )

        versao_snap = tentar_criar_snapshot_versao_video_narrado_apos_sucesso_silencioso_transcribrothers(
            work=work,
            assets=assets,
            steps=steps,
            origem="edicoes_modal",
        )
        if versao_snap:
            steps[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS][
                "versao_video_narrado_id"
            ] = versao_snap
        await _atualizar_steps_job_transcribrothers(
            session_factory,
            job_id,
            steps=steps,
            status=StatusJobTranscribrothers.completed,
            limpar_mensagem_erro=True,
        )
    except (RuntimeError, ValueError, OSError, ErroFfmpegTranscribrothers) as exc:
        texto_erro = str(exc)
        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_FALHOU
        steps[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS] = {
            "ok": False,
            "mensagem": texto_erro,
            "edicoes_modal_narrado": True,
            "falhou_em": datetime.now(timezone.utc).isoformat(),
        }
        await _atualizar_steps_job_transcribrothers(
            session_factory,
            job_id,
            steps=steps,
            status=StatusJobTranscribrothers.failed,
            error=texto_erro,
        )
    except Exception as exc:  # noqa: BLE001 — pipeline em background
        texto_erro = f"{exc}\n{traceback.format_exc()}"
        steps["pipeline_fase"] = FASE_VIDEO_NARRADO_FALHOU
        steps[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS] = {
            "ok": False,
            "mensagem": str(exc),
            "edicoes_modal_narrado": True,
            "falhou_em": datetime.now(timezone.utc).isoformat(),
        }
        await _atualizar_steps_job_transcribrothers(
            session_factory,
            job_id,
            steps=steps,
            status=StatusJobTranscribrothers.failed,
            error=texto_erro,
        )


def agendar_gerar_video_com_edicoes_do_modal_narrado_em_task_assincrona(
    *,
    job_id: str,
    session_factory: async_sessionmaker[AsyncSession],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    modelo_tts: str,
    cues_brutas: list[dict[str, Any]],
    janelas_brutas: list[dict[str, Any]] | None,
) -> None:
    asyncio.create_task(
        executar_gerar_video_com_edicoes_do_modal_narrado_em_background(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=configuracao,
            modelo_tts=modelo_tts,
            cues_brutas=cues_brutas,
            janelas_brutas=janelas_brutas,
        )
        )
