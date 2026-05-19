from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    amostrar_indices_por_limite_por_minuto,
    amostrar_timestamps_por_limite_por_minuto,
)


def test_amostrar_indices_nao_ultrapassa_limite_por_minuto() -> None:
    n = 200
    dur = 600.0
    max_por_minuto = 12
    idx = amostrar_indices_por_limite_por_minuto(
        n_itens=n,
        max_por_minuto=max_por_minuto,
        duracao_video_segundos=dur,
    )
    max_total = int((dur / 60.0) * max_por_minuto)
    assert len(idx) <= max(1, max_total)
    assert all(0 <= i < n for i in idx)


def test_amostrar_timestamps_consistente_com_indices() -> None:
    ts = [float(i) for i in range(50)]
    dur = 120.0
    out = amostrar_timestamps_por_limite_por_minuto(
        ts,
        max_por_minuto=12,
        duracao_video_segundos=dur,
    )
    assert len(out) >= 1
    assert all(t in ts for t in out)

