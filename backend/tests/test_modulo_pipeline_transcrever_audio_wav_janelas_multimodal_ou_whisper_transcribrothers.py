"""Garante que pipelines de destino distintos usam o helper unificado de transcrição em janelas."""

from pathlib import Path


def test_modulo_pipeline_transcrever_audio_wav_exporta_helper_unificado() -> None:
    from transcribrothers_backend.modulo_pipeline_transcrever_audio_wav_janelas_multimodal_ou_whisper_transcribrothers import (
        transcrever_audio_wav_com_logica_janelas_multimodal_ou_whisper_pipeline_transcribrothers,
    )

    assert callable(transcrever_audio_wav_com_logica_janelas_multimodal_ou_whisper_pipeline_transcribrothers)


def test_pipelines_importam_helper_unificado_de_transcricao() -> None:
    import inspect

    from transcribrothers_backend import (
        modulo_pipeline_job_notas_proposta_funcionalidade_transcribrothers as notas,
        modulo_pipeline_job_reproducao_bug_recbrothers_transcribrothers as bug,
        modulo_pipeline_job_transcricao_tutorial as tutorial,
    )

    helper = "transcrever_audio_wav_com_logica_janelas_multimodal_ou_whisper_pipeline_transcribrothers"
    for mod in (tutorial, bug, notas):
        src = Path(inspect.getfile(mod)).read_text(encoding="utf-8")
        assert helper in src
