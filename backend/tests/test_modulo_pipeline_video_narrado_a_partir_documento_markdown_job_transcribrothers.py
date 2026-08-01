"""Orquestrador do pipeline vídeo narrado A+B com mocks de snapshot, TTS e ffmpeg."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import (
    StatusJobTranscribrothers,
)
from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS,
    ResultadoNarracaoTtsWavsPorCueTranscribrothers,
)
from transcribrothers_backend.modulo_limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers import (
    CHAVE_STEPS_JSON_LIMPEZA_LEGENDAS_IA_TRANSCRIBROTHERS,
    ResultadoLimpezaTextosCuesLegendasIaTranscribrothers,
)
from transcribrothers_backend.modulo_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers import (
    CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS,
    FASE_VIDEO_NARRADO_CONCLUIDO,
    executar_pipeline_video_narrado_a_partir_documento_markdown_em_background,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
    SegmentoTranscricaoComTempo,
)
from transcribrothers_backend.modulo_util_gerar_arquivo_vtt_a_partir_cues_legendas_transcribrothers import (
    NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
)


def _session_factory_com_row(row: MagicMock) -> MagicMock:
    session = AsyncMock()
    session.get = AsyncMock(return_value=row)
    session.commit = AsyncMock()
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)
    session_factory = MagicMock()
    session_factory.return_value = session
    return session_factory


@pytest.mark.asyncio
async def test_orquestrador_pipeline_video_narrado_sucesso_com_ancoras_markdown(tmp_path: Path) -> None:
    job_id = "job-video-narrado-teste"
    work = tmp_path / "jobs" / job_id
    assets = work / "assets_exportados_para_markdown"
    assets.mkdir(parents=True)
    video = work / "video_entrada_arquivo_local.mp4"
    video.write_bytes(b"vid")
    mp4_saida = work / "video_com_narracao_tts.mp4"

    row = MagicMock()
    row.result_markdown = (
        "# Tutorial\n\nOlá mundo.\n\n[00:02](?t=2)\n\nSegundo segmento.\n\n[00:08](?t=8)\n"
    )
    row.steps_json = {}
    session_factory = _session_factory_com_row(row)

    cfg = MagicMock()
    cfg.transcribrothers_data_dir = tmp_path

    async def _fake_tts(**kwargs):
        dir_wavs = kwargs["diretorio_wavs_por_cue"]
        dir_wavs.mkdir(parents=True, exist_ok=True)
        trechos = list(kwargs["trechos"])
        caminhos = []
        duracoes = []
        for i, _ in enumerate(trechos):
            p = dir_wavs / f"cue_narracao_{i:04d}.wav"
            p.write_bytes(b"RIFF")
            caminhos.append(p)
            duracoes.append(1.0 + 0.2 * i)
        kwargs["caminho_wav_concatenado"].write_bytes(b"RIFF")
        return ResultadoNarracaoTtsWavsPorCueTranscribrothers(
            ok=True,
            mensagem="ok",
            nome_arquivo_concatenado=NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS,
            caminhos_wav_por_cue=tuple(caminhos),
            duracoes_por_cue_segundos=tuple(duracoes),
            modelo="gemini/fake-tts",
            texto_caracteres=sum(len(t) for t in trechos),
            quantidade_cues=len(trechos),
            quantidade_pedidos_tts=len(trechos),
        )

    mock_tts = AsyncMock(side_effect=_fake_tts)
    mock_ffmpeg = AsyncMock(return_value=mp4_saida)

    with (
        patch(
            "transcribrothers_backend.modulo_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers."
            "obter_duracao_video_segundos_via_ffprobe",
            new_callable=AsyncMock,
            return_value=60.0,
        ),
        patch(
            "transcribrothers_backend.modulo_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers."
            "gerar_narracao_tts_wavs_individuais_por_cue_e_concatenar_via_litellm_transcribrothers",
            new=mock_tts,
        ),
        patch(
            "transcribrothers_backend.modulo_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers."
            "montar_video_narrado_por_segmentos_retarget_audio_via_ffmpeg_transcribrothers",
            new=mock_ffmpeg,
        ),
    ):
        await executar_pipeline_video_narrado_a_partir_documento_markdown_em_background(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=cfg,
            modelo_tts="gemini/fake-tts",
        )

    assert (assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS).is_file()
    assert row.status == StatusJobTranscribrothers.completed.value
    blob = row.steps_json[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS]
    assert blob["ok"] is True
    assert blob["modo_janelas"] == "markdown_ancoras"
    assert row.steps_json["pipeline_fase"] == FASE_VIDEO_NARRADO_CONCLUIDO
    assert row.steps_json["legendas_documento_alinhadas"]["validacao_ok"] is True
    assert mock_tts.await_count == 1
    trechos = mock_tts.await_args.kwargs["trechos"]
    assert len(trechos) >= 2
    mock_ffmpeg.assert_awaited_once()
    segmentos = mock_ffmpeg.await_args.kwargs["segmentos"]
    assert len(segmentos) == len(trechos)
    assert segmentos[0].caminho_wav.name.startswith("cue_narracao_")


@pytest.mark.asyncio
async def test_orquestrador_pipeline_video_narrado_falha_sem_snapshot_nem_ancoras(
    tmp_path: Path,
) -> None:
    job_id = "job-video-narrado-sem-snap"
    work = tmp_path / "jobs" / job_id
    work.mkdir(parents=True)
    (work / "video_entrada_arquivo_local.mp4").write_bytes(b"vid")

    row = MagicMock()
    row.result_markdown = "# Doc\n\nTexto sem ancora temporal."
    row.steps_json = {}
    session_factory = _session_factory_com_row(row)

    cfg = MagicMock()
    cfg.transcribrothers_data_dir = tmp_path

    with patch(
        "transcribrothers_backend.modulo_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers."
        "carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers",
        return_value=None,
    ):
        await executar_pipeline_video_narrado_a_partir_documento_markdown_em_background(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=cfg,
            modelo_tts="gemini/fake-tts",
        )

    assert row.status == StatusJobTranscribrothers.failed.value
    assert row.steps_json["pipeline_fase"] == "video_narrado_falhou"
    assert row.steps_json[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS]["ok"] is False


@pytest.mark.asyncio
async def test_orquestrador_validacao_stt_falha_nao_chama_tts_nem_ffmpeg(tmp_path: Path) -> None:
    job_id = "job-video-narrado-validacao-falha"
    work = tmp_path / "jobs" / job_id
    assets = work / "assets_exportados_para_markdown"
    assets.mkdir(parents=True)
    (work / "video_entrada_arquivo_local.mp4").write_bytes(b"vid")

    snap = ResultadoTranscricaoComSegmentos(
        texto_completo="alpha beta",
        segmentos=[SegmentoTranscricaoComTempo(0.0, 1.0, "alpha beta")],
        idioma_detectado="pt",
    )
    frases_md = "\n\n".join(f"Frase completamente diferente numero {i} xyzzy qwerty." for i in range(12))
    row = MagicMock()
    row.result_markdown = f"# Tutorial\n\n{frases_md}"
    row.steps_json = {}
    session_factory = _session_factory_com_row(row)

    cfg = MagicMock()
    cfg.transcribrothers_data_dir = tmp_path

    mock_tts = AsyncMock()
    mock_ffmpeg = AsyncMock()

    with (
        patch(
            "transcribrothers_backend.modulo_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers."
            "carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers",
            return_value=snap,
        ),
        patch(
            "transcribrothers_backend.modulo_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers."
            "obter_duracao_video_segundos_via_ffprobe",
            new_callable=AsyncMock,
            return_value=60.0,
        ),
        patch(
            "transcribrothers_backend.modulo_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers."
            "gerar_narracao_tts_wavs_individuais_por_cue_e_concatenar_via_litellm_transcribrothers",
            new=mock_tts,
        ),
        patch(
            "transcribrothers_backend.modulo_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers."
            "montar_video_narrado_por_segmentos_retarget_audio_via_ffmpeg_transcribrothers",
            new=mock_ffmpeg,
        ),
    ):
        await executar_pipeline_video_narrado_a_partir_documento_markdown_em_background(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=cfg,
            modelo_tts="gemini/fake-tts",
        )

    assert row.status == StatusJobTranscribrothers.failed.value
    assert row.steps_json["legendas_documento_alinhadas"]["validacao_ok"] is False
    mock_tts.assert_not_awaited()
    mock_ffmpeg.assert_not_awaited()


@pytest.mark.asyncio
async def test_pipeline_full_ignora_vtt_editado_sujo_e_chama_limpeza_ia(
    tmp_path: Path,
) -> None:
    """FAB / regeneração completa: Markdown + limpeza IA; não reusa VTT editado sujo."""
    from transcribrothers_backend.modulo_montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers import (
        montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers,
    )
    from transcribrothers_backend.modulo_util_filtrar_trechos_narraveis_para_tts_transcribrothers import (
        texto_e_narravel_para_tts_transcribrothers,
    )

    job_id = "job-video-narrado-ignora-vtt"
    work = tmp_path / "jobs" / job_id
    assets = work / "assets_exportados_para_markdown"
    assets.mkdir(parents=True)
    (work / "video_entrada_arquivo_local.mp4").write_bytes(b"vid")
    mp4_saida = work / "video_com_narracao_tts.mp4"

    markdown = (
        "# Tutorial\n\nOlá mundo limpo do markdown.\n\n[00:02](?t=2)\n\n"
        "Segundo segmento limpo do markdown.\n\n[00:08](?t=8)\n"
    )
    cues_md = montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers(
        markdown,
        duracao_video_segundos=60.0,
    ).cues
    cues_narraveis = [c for c in cues_md if texto_e_narravel_para_tts_transcribrothers(c.texto)]
    assert len(cues_narraveis) >= 2

    marcador_sujo = "TEXTO_SUJO_VTT_EDITADO_COM_LIXO [99:99]("
    blocos_vtt = ["WEBVTT", ""]
    for i in range(len(cues_narraveis)):
        blocos_vtt.append(str(i + 1))
        blocos_vtt.append(f"00:00:{i:02d}.000 --> 00:00:{i + 1:02d}.000")
        blocos_vtt.append(f"{marcador_sujo} cue {i}")
        blocos_vtt.append("")
    (assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS).write_text(
        "\n".join(blocos_vtt),
        encoding="utf-8",
    )

    row = MagicMock()
    row.result_markdown = markdown
    row.steps_json = {}
    session_factory = _session_factory_com_row(row)

    cfg = MagicMock()
    cfg.transcribrothers_data_dir = tmp_path

    async def _fake_tts(**kwargs):
        dir_wavs = kwargs["diretorio_wavs_por_cue"]
        dir_wavs.mkdir(parents=True, exist_ok=True)
        trechos = list(kwargs["trechos"])
        caminhos = []
        duracoes = []
        for i, _ in enumerate(trechos):
            p = dir_wavs / f"cue_narracao_{i:04d}.wav"
            p.write_bytes(b"RIFF")
            caminhos.append(p)
            duracoes.append(1.0)
        kwargs["caminho_wav_concatenado"].write_bytes(b"RIFF")
        return ResultadoNarracaoTtsWavsPorCueTranscribrothers(
            ok=True,
            mensagem="ok",
            nome_arquivo_concatenado=NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS,
            caminhos_wav_por_cue=tuple(caminhos),
            duracoes_por_cue_segundos=tuple(duracoes),
            modelo="gemini/fake-tts",
            texto_caracteres=sum(len(t) for t in trechos),
            quantidade_cues=len(trechos),
            quantidade_pedidos_tts=len(trechos),
        )

    mock_tts = AsyncMock(side_effect=_fake_tts)
    mock_ffmpeg = AsyncMock(return_value=mp4_saida)

    async def _fake_limpeza(**kwargs):
        textos = list(kwargs["textos"])
        return ResultadoLimpezaTextosCuesLegendasIaTranscribrothers(
            textos=textos,
            ok=True,
            mensagem="limpeza mock ok",
            modelo="chat/fake",
            quantidade_alteradas=0,
            usou_fallback_originais=False,
        )

    mock_limpeza = AsyncMock(side_effect=_fake_limpeza)

    with (
        patch(
            "transcribrothers_backend.modulo_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers."
            "obter_duracao_video_segundos_via_ffprobe",
            new_callable=AsyncMock,
            return_value=60.0,
        ),
        patch(
            "transcribrothers_backend.modulo_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers."
            "limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers",
            new=mock_limpeza,
        ),
        patch(
            "transcribrothers_backend.modulo_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers."
            "gerar_narracao_tts_wavs_individuais_por_cue_e_concatenar_via_litellm_transcribrothers",
            new=mock_tts,
        ),
        patch(
            "transcribrothers_backend.modulo_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers."
            "montar_video_narrado_por_segmentos_retarget_audio_via_ffmpeg_transcribrothers",
            new=mock_ffmpeg,
        ),
    ):
        await executar_pipeline_video_narrado_a_partir_documento_markdown_em_background(
            job_id=job_id,
            session_factory=session_factory,
            configuracao=cfg,
            modelo_tts="gemini/fake-tts",
        )

    assert row.status == StatusJobTranscribrothers.completed.value
    blob = row.steps_json[CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS]
    assert blob["ok"] is True
    assert blob.get("textos_origem_vtt_editado") is False

    limpeza_steps = row.steps_json[CHAVE_STEPS_JSON_LIMPEZA_LEGENDAS_IA_TRANSCRIBROTHERS]
    assert limpeza_steps.get("omitida") is not True
    assert limpeza_steps.get("motivo") != "vtt_editado"
    mock_limpeza.assert_awaited_once()

    trechos = mock_tts.await_args.kwargs["trechos"]
    assert trechos
    assert all(marcador_sujo not in t for t in trechos)
    assert any("markdown" in t.lower() or "mundo" in t.lower() for t in trechos)

    url_mp4 = row.steps_json.get("video_com_narracao_tts", {}).get("url_download", "")
    assert "?v=" in url_mp4
