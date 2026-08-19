"""Persiste o estado do editor de vídeo narrado (VTT + manifesto) sem gerar MP4."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_api_janelas_video_e_wavs_por_cue_narracao_job_transcribrothers import (
    diretorio_wavs_narracao_por_cue_do_work_transcribrothers,
)
from transcribrothers_backend.modulo_api_salvar_legendas_documento_alinhadas_vtt_editadas_job_transcribrothers import (
    salvar_legendas_documento_alinhadas_vtt_editadas_no_job_transcribrothers,
    validar_e_normalizar_cues_legendas_editadas_para_vtt_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_manifest_cues_narracao_janelas_video_job_transcribrothers import (
    carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers,
    gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers,
)
from transcribrothers_backend.modulo_pipeline_gerar_video_com_edicoes_do_modal_narrado_job_transcribrothers import (
    _resolver_cues_janela_a_partir_edicoes_modal_transcribrothers,
    gravar_wav_silencio_para_cue_sem_narracao_com_duracao_da_janela_transcribrothers,
    remapar_arquivos_wav_narracao_por_mapa_indices_transcribrothers,
)
from transcribrothers_backend.modulo_preferencias_voz_tts_gemini_narracao_transcribrothers import (
    VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_promover_preview_tts_cue_validada_para_wav_definitivo_narracao_transcribrothers import (
    promover_previews_validas_e_listar_indices_ainda_precisam_tts_transcribrothers,
)
from transcribrothers_backend.modulo_util_texto_efetivo_para_tts_cue_legenda_ou_override_transcribrothers import (
    texto_efetivo_para_tts_cue_narracao_transcribrothers,
)
from transcribrothers_backend.modulo_validar_e_ajustar_janelas_video_cues_sem_sobreposicao_transcribrothers import (
    resolver_caminho_wav_narracao_por_indice_cue_transcribrothers,
)

CHAVE_STEPS_EDITOR_VIDEO_NARRADO_AUDIO_MP4_DESATUALIZADO_TRANSCRIBROTHERS = (
    "editor_video_narrado_audio_mp4_desatualizado"
)


def marcar_audio_mp4_sincronizado_com_projeto_editor_apos_remux_transcribrothers(
    steps: dict[str, Any],
) -> None:
    """Após gerar/remux do MP4, o áudio embutido volta a refletir os WAVs do projeto."""
    steps[CHAVE_STEPS_EDITOR_VIDEO_NARRADO_AUDIO_MP4_DESATUALIZADO_TRANSCRIBROTHERS] = False


@dataclass(frozen=True)
class ResultadoSalvarEstadoEditorVideoNarradoEdicoesModalTranscribrothers:
    quantidade_cues: int
    nome_arquivo_vtt: str
    url_asset_vtt: str
    steps_json_atualizado: dict[str, Any]
    wavs_remapeados: int
    previews_promovidas: int = 0
    indices_previews_promovidas: tuple[int, ...] = ()


def salvar_estado_editor_video_narrado_edicoes_modal_sem_gerar_mp4_transcribrothers(
    *,
    job_id: str,
    work: Path,
    diretorio_assets: Path,
    steps_json: dict[str, Any] | None,
    cues_brutas: list[dict[str, Any]],
    janelas_brutas: list[dict[str, Any]],
    voz_padrao_job: str | None = None,
) -> ResultadoSalvarEstadoEditorVideoNarradoEdicoesModalTranscribrothers:
    """
    Checkpoint do editor: grava VTT + manifesto (tempos, fonte, sem narração, voz, texto_tts),
    remapeia WAVs quando a lista muda e promove prévias TTS válidas a WAV definitivo.
    Não remonta o MP4 nem chama TTS novo.
    """
    if not janelas_brutas:
        raise ValueError("Informe os tempos de tela de cada cue.")
    cues_vtt = validar_e_normalizar_cues_legendas_editadas_para_vtt_transcribrothers(cues_brutas)
    if len(janelas_brutas) != len(cues_vtt):
        raise ValueError(
            "Quantidade de tempos de tela não bate com as cues "
            f"({len(janelas_brutas)} vs {len(cues_vtt)})."
        )
    manifest_antes = carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers(work)
    if manifest_antes is None:
        raise ValueError(
            "Não há manifesto de janelas de tela. Gere o vídeo narrado antes de salvar o projeto."
        )

    voz_padrao = (
        (voz_padrao_job or "").strip()
        or str((steps_json or {}).get("pipeline_video_narrado_voz_tts") or "").strip()
        or VOZ_TTS_GEMINI_PADRAO_TRANSCRIBROTHERS
    )
    textos = [c.texto for c in cues_vtt]
    textos_tts = [str(getattr(c, "texto_tts", "") or "") for c in cues_vtt]
    flags_sem_narracao = [bool(c.sem_narracao) for c in cues_vtt]
    vozes_desejadas = [str(getattr(c, "voz_tts", "") or "") for c in cues_vtt]

    cues_janela, _indices_sujos, mapa_reuso_wav = (
        _resolver_cues_janela_a_partir_edicoes_modal_transcribrothers(
            work=work,
            textos_desejados=textos,
            textos_tts_desejados=textos_tts,
            flags_sem_narracao=flags_sem_narracao,
            vozes_desejadas=vozes_desejadas,
            voz_padrao=voz_padrao,
            janelas_brutas=janelas_brutas,
        )
    )

    resultado_salvar = salvar_legendas_documento_alinhadas_vtt_editadas_no_job_transcribrothers(
        job_id=job_id,
        diretorio_assets=diretorio_assets,
        steps_json=steps_json,
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

    remapar_arquivos_wav_narracao_por_mapa_indices_transcribrothers(work, mapa_reuso_wav)

    quantidade_estavel = len(manifest_antes) == len(cues_janela)
    textos_tts_efetivos = [
        texto_efetivo_para_tts_cue_narracao_transcribrothers(
            texto_legenda=c.texto,
            texto_tts=c.texto_tts,
        )
        for c in cues_janela
    ]
    vozes_por_cue = [c.voz_tts or voz_padrao for c in cues_janela]
    # Tenta promover prévia→definitivo em todas as cues com narração (só se índices estáveis).
    indices_candidatos = [i for i, sn in enumerate(flags_sem_narracao) if not sn]
    _ainda_tts, indices_promovidos, _caminhos = (
        promover_previews_validas_e_listar_indices_ainda_precisam_tts_transcribrothers(
            work=work,
            indices_sujos=indices_candidatos,
            textos_por_indice=textos_tts_efetivos,
            vozes_por_indice=vozes_por_cue,
            flags_sem_narracao=flags_sem_narracao,
            quantidade_cues_estavel=quantidade_estavel,
        )
    )

    dir_wavs = diretorio_wavs_narracao_por_cue_do_work_transcribrothers(work)
    dir_wavs.mkdir(parents=True, exist_ok=True)
    for i, cue in enumerate(cues_janela):
        if not cue.sem_narracao:
            continue
        caminho_silencio = resolver_caminho_wav_narracao_por_indice_cue_transcribrothers(
            dir_wavs, i
        )
        gravar_wav_silencio_para_cue_sem_narracao_com_duracao_da_janela_transcribrothers(
            caminho_wav_saida=caminho_silencio,
            inicio_video_segundos=cue.inicio_video_segundos,
            fim_video_segundos=cue.fim_video_segundos,
        )

    gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers(
        work=work,
        cues=cues_janela,
    )

    steps["editor_video_narrado_projeto_salvo_em"] = datetime.now(timezone.utc).isoformat()
    steps["editor_video_narrado_projeto_quantidade_cues"] = len(cues_janela)
    steps["editor_video_narrado_projeto_previews_promovidas"] = len(indices_promovidos)
    steps["editor_video_narrado_projeto_indices_previews_promovidas"] = list(indices_promovidos)
    # Qualquer checkpoint pode mudar fonte/tempos/texto sem remux — player usa preview/WAV.
    steps[CHAVE_STEPS_EDITOR_VIDEO_NARRADO_AUDIO_MP4_DESATUALIZADO_TRANSCRIBROTHERS] = True

    return ResultadoSalvarEstadoEditorVideoNarradoEdicoesModalTranscribrothers(
        quantidade_cues=len(cues_janela),
        nome_arquivo_vtt=resultado_salvar.nome_arquivo,
        url_asset_vtt=resultado_salvar.url_asset,
        steps_json_atualizado=steps,
        wavs_remapeados=len(mapa_reuso_wav),
        previews_promovidas=len(indices_promovidos),
        indices_previews_promovidas=tuple(indices_promovidos),
    )
