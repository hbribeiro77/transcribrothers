"""Preferências de encode (resolução + FPS) do vídeo narrado."""

from __future__ import annotations

import pytest

from transcribrothers_backend.modulo_preferencias_encode_video_narrado_transcribrothers import (
    montar_cadeia_vf_scale_e_fps_encode_video_narrado_transcribrothers,
    montar_preferencias_encode_video_narrado_transcribrothers,
    preferencias_encode_video_narrado_padrao_transcribrothers,
)


def test_padrao_app_e_1080p_30fps() -> None:
    p = preferencias_encode_video_narrado_padrao_transcribrothers()
    assert p.resolucao == "1080p"
    assert p.fps == 30


def test_cadeia_vf_1080p_inclui_altura_e_fps() -> None:
    p = montar_preferencias_encode_video_narrado_transcribrothers(resolucao="1080p", fps=30)
    cadeia = montar_cadeia_vf_scale_e_fps_encode_video_narrado_transcribrothers(p)
    assert "1080" in cadeia
    assert "fps=30" in cadeia
    assert "format=yuv420p" in cadeia


def test_cadeia_vf_original_so_par_e_fps() -> None:
    p = montar_preferencias_encode_video_narrado_transcribrothers(resolucao="original", fps=30)
    cadeia = montar_cadeia_vf_scale_e_fps_encode_video_narrado_transcribrothers(p)
    assert "trunc(iw/2)*2" in cadeia
    assert "fps=30" in cadeia
    assert "1080" not in cadeia


def test_resolucao_invalida_levanta() -> None:
    with pytest.raises(ValueError, match="Resolução"):
        montar_preferencias_encode_video_narrado_transcribrothers(resolucao="4k", fps=30)
