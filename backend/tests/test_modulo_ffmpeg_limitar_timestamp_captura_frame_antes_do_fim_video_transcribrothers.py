from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    limitar_timestamp_segundos_para_captura_de_frame_sem_ultrapassar_o_fim_do_video_transcribrothers,
)


def test_limitar_timestamp_sem_duracao_conhecida_mantem_valor() -> None:
    assert (
        limitar_timestamp_segundos_para_captura_de_frame_sem_ultrapassar_o_fim_do_video_transcribrothers(
            150.5,
            0.0,
        )
        == 150.5
    )


def test_limitar_timestamp_abaixo_do_fim_mantem_valor() -> None:
    assert (
        limitar_timestamp_segundos_para_captura_de_frame_sem_ultrapassar_o_fim_do_video_transcribrothers(
            10.0,
            150.41,
        )
        == 10.0
    )


def test_limitar_timestamp_alem_do_fim_encosta_antes_da_margem() -> None:
    """Caso real: último segmento ~150,41 s, meio 150,5 s — seek deve recuar."""
    t = limitar_timestamp_segundos_para_captura_de_frame_sem_ultrapassar_o_fim_do_video_transcribrothers(
        150.5,
        150.41,
        margem_segundos_antes_do_fim=0.05,
    )
    assert abs(t - 150.36) < 1e-9
