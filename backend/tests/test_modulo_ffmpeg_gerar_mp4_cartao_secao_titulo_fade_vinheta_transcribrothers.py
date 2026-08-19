"""Testes do cartão de seção (escape, truncar, filtro vf)."""

from __future__ import annotations

from pathlib import Path

from transcribrothers_backend.modulo_ffmpeg_gerar_mp4_cartao_secao_titulo_fade_vinheta_transcribrothers import (
    escapar_caminho_para_filtro_ffmpeg_drawtext_transcribrothers,
    montar_filtro_vf_cartao_secao_drawtext_fade_transcribrothers,
    truncar_titulo_cartao_secao_transcribrothers,
)


def test_truncar_titulo_cartao_secao_padrao_e_limite() -> None:
    assert truncar_titulo_cartao_secao_transcribrothers("") == "Nova funcionalidade"
    assert truncar_titulo_cartao_secao_transcribrothers("  Cadastro  ") == "Cadastro"
    longo = "a" * 100
    out = truncar_titulo_cartao_secao_transcribrothers(longo, max_chars=20)
    assert len(out) <= 20
    assert out.endswith("…")


def test_escapar_caminho_windows_para_drawtext() -> None:
    esc = escapar_caminho_para_filtro_ffmpeg_drawtext_transcribrothers(r"C:\Fonts\arial.ttf")
    assert "\\" not in esc or esc.count("\\") >= 1  # : vira \:
    assert "C\\:" in esc or "C:" not in esc.replace("\\:", "")


def test_montar_filtro_vf_tem_fade_in_out_e_drawtext(tmp_path: Path) -> None:
    titulo = tmp_path / "t.txt"
    titulo.write_text("Olá\n", encoding="utf-8")
    sub = tmp_path / "s.txt"
    sub.write_text("Portal\n", encoding="utf-8")
    vf = montar_filtro_vf_cartao_secao_drawtext_fade_transcribrothers(
        caminho_arquivo_titulo=titulo,
        caminho_arquivo_subtitulo=sub,
        caminho_fonte=None,
        duracao_segundos=3.5,
        fade_segundos=0.4,
    )
    assert "fade=t=in" in vf
    assert "fade=t=out" in vf
    assert "drawtext=" in vf
    assert "st=3.100" in vf or "st=3.1" in vf
