from types import SimpleNamespace
from pathlib import Path

import pytest

from transcribrothers_backend.modulo_gerar_vinheta_de_separador_com_quadro_do_video_transcribrothers import (
    gerar_mp4_de_vinheta_com_quadro_do_video_transcribrothers,
    normalizar_dimensoes_pares_do_canvas_da_vinheta_ao_video_fonte,
)
from transcribrothers_backend.modulo_preferencias_encode_video_narrado_transcribrothers import (
    montar_preferencias_encode_video_narrado_transcribrothers,
)
from transcribrothers_backend.modulo_persistir_debug_ultima_geracao_vinheta_separador_transcribrothers import (
    ler_debug_ultima_geracao_vinheta_separador_transcribrothers,
)


def test_dimensoes_do_canvas_ficam_pares_para_yuv420p():
    assert normalizar_dimensoes_pares_do_canvas_da_vinheta_ao_video_fonte(1365, 767) == (1364, 766)
    assert normalizar_dimensoes_pares_do_canvas_da_vinheta_ao_video_fonte(1280, 720) == (1280, 720)
    assert normalizar_dimensoes_pares_do_canvas_da_vinheta_ao_video_fonte(1, 1) == (2, 2)


@pytest.mark.asyncio
async def test_manda_o_tamanho_do_video_para_a_api_e_para_a_dissolucao(monkeypatch, tmp_path: Path):
    visto: dict[str, object] = {}
    video = tmp_path / "fonte.mp4"
    video.write_bytes(b"fake-mp4")

    async def fake_png(caminho_video, instante, pasta, nome):
        destino = pasta / f"{nome}.png"
        destino.write_bytes(b"png")
        return destino

    async def fake_baixar(**kwargs):
        visto["baixar"] = kwargs
        return b"mp4", {"amostragem_ms": 1200, "desenho_ms": 8000, "encode_ms": 3000, "quantidade_quadros": 150, "fps": 30}

    async def fake_perfil(_caminho):
        return SimpleNamespace(largura=1366, altura=768)

    async def fake_duracao(_caminho):
        return 5.0

    monkeypatch.setattr(
        "transcribrothers_backend.modulo_gerar_vinheta_de_separador_com_quadro_do_video_transcribrothers._png_do_instante",
        fake_png,
    )
    monkeypatch.setattr(
        "transcribrothers_backend.modulo_gerar_vinheta_de_separador_com_quadro_do_video_transcribrothers.baixar_mp4_renderizado_da_vinheta_com_debug",
        fake_baixar,
    )
    monkeypatch.setattr(
        "transcribrothers_backend.modulo_gerar_vinheta_de_separador_com_quadro_do_video_transcribrothers.obter_perfil_streams_midia_entrada_via_ffprobe_transcribrothers",
        fake_perfil,
    )
    monkeypatch.setattr(
        "transcribrothers_backend.modulo_gerar_vinheta_de_separador_com_quadro_do_video_transcribrothers.obter_duracao_video_segundos_via_ffprobe",
        fake_duracao,
    )

    work = tmp_path / "job"
    work.mkdir()
    conteudo, _duracao = await gerar_mp4_de_vinheta_com_quadro_do_video_transcribrothers(
        titulo="Consulta",
        efeito="planos-que-abrem-espaco",
        vinheta_id=None,
        caminho_video=video,
        instante_quadro_seguinte=1.2,
        instante_quadro_anterior=0.8,
        work=work,
    )

    assert conteudo == b"mp4"
    assert visto["baixar"]["largura"] == 1366
    assert visto["baixar"]["altura"] == 768
    assert visto["baixar"]["imagem_quadro_anterior_base64"] is not None
    assert "dissolver" not in visto
    relatorio = ler_debug_ultima_geracao_vinheta_separador_transcribrothers(work)
    assert relatorio is not None
    assert relatorio["titulo"] == "Consulta"
    assert relatorio["largura"] == 1366
    assert relatorio["tempos_ms"]["total"] >= 0
    assert relatorio["tempos_ms"]["amostragem_vite_node"] == 1200
    assert relatorio["tempos_ms"]["desenho_pil"] == 8000
    assert relatorio["quantidade_quadros"] == 150
    assert relatorio["resolucao_encode"] == "1080p"


@pytest.mark.asyncio
async def test_o_canvas_da_vinheta_usa_o_alvo_do_encode_1080p(monkeypatch, tmp_path: Path):
    visto: dict[str, object] = {}
    video = tmp_path / "fonte.mp4"
    video.write_bytes(b"fake-mp4")

    async def fake_png(caminho_video, instante, pasta, nome):
        destino = pasta / f"{nome}.png"
        destino.write_bytes(b"png")
        return destino

    async def fake_baixar(**kwargs):
        visto["baixar"] = kwargs
        return b"mp4", {}

    async def fake_perfil(_caminho):
        return SimpleNamespace(largura=2960, altura=1848)

    async def fake_duracao(_caminho):
        return 5.0

    monkeypatch.setattr(
        "transcribrothers_backend.modulo_gerar_vinheta_de_separador_com_quadro_do_video_transcribrothers._png_do_instante",
        fake_png,
    )
    monkeypatch.setattr(
        "transcribrothers_backend.modulo_gerar_vinheta_de_separador_com_quadro_do_video_transcribrothers.baixar_mp4_renderizado_da_vinheta_com_debug",
        fake_baixar,
    )
    monkeypatch.setattr(
        "transcribrothers_backend.modulo_gerar_vinheta_de_separador_com_quadro_do_video_transcribrothers.obter_perfil_streams_midia_entrada_via_ffprobe_transcribrothers",
        fake_perfil,
    )
    monkeypatch.setattr(
        "transcribrothers_backend.modulo_gerar_vinheta_de_separador_com_quadro_do_video_transcribrothers.obter_duracao_video_segundos_via_ffprobe",
        fake_duracao,
    )

    work = tmp_path / "job"
    work.mkdir()
    await gerar_mp4_de_vinheta_com_quadro_do_video_transcribrothers(
        titulo="Consulta",
        efeito="linhas-que-desenham-o-lugar",
        vinheta_id=None,
        caminho_video=video,
        instante_quadro_seguinte=1.2,
        instante_quadro_anterior=0.8,
        work=work,
        preferencias_encode=montar_preferencias_encode_video_narrado_transcribrothers(
            resolucao="1080p",
            fps=30,
        ),
    )

    assert visto["baixar"]["largura"] == 1728
    assert visto["baixar"]["altura"] == 1080
    relatorio = ler_debug_ultima_geracao_vinheta_separador_transcribrothers(work)
    assert relatorio is not None
    assert relatorio["largura"] == 1728
    assert relatorio["altura"] == 1080
    assert relatorio["largura_fonte"] == 2960
    assert relatorio["altura_fonte"] == 1848
    assert relatorio["resolucao_encode"] == "1080p"


@pytest.mark.asyncio
async def test_nao_sonda_a_duracao_quando_ela_ja_veio_no_pedido(monkeypatch, tmp_path: Path):
    video = tmp_path / "fonte.mp4"
    video.write_bytes(b"fake-mp4")

    async def fake_png(caminho_video, instante, pasta, nome):
        destino = pasta / f"{nome}.png"
        destino.write_bytes(b"png")
        return destino

    async def fake_baixar(**kwargs):
        return b"mp4", {}

    async def fake_perfil(_caminho):
        return SimpleNamespace(largura=1280, altura=720)

    async def fake_duracao(_caminho):
        raise AssertionError("a duração pedida já basta")

    monkeypatch.setattr(
        "transcribrothers_backend.modulo_gerar_vinheta_de_separador_com_quadro_do_video_transcribrothers._png_do_instante",
        fake_png,
    )
    monkeypatch.setattr(
        "transcribrothers_backend.modulo_gerar_vinheta_de_separador_com_quadro_do_video_transcribrothers.baixar_mp4_renderizado_da_vinheta_com_debug",
        fake_baixar,
    )
    monkeypatch.setattr(
        "transcribrothers_backend.modulo_gerar_vinheta_de_separador_com_quadro_do_video_transcribrothers.obter_perfil_streams_midia_entrada_via_ffprobe_transcribrothers",
        fake_perfil,
    )
    monkeypatch.setattr(
        "transcribrothers_backend.modulo_gerar_vinheta_de_separador_com_quadro_do_video_transcribrothers.obter_duracao_video_segundos_via_ffprobe",
        fake_duracao,
    )

    work = tmp_path / "job"
    work.mkdir()
    _conteudo, duracao = await gerar_mp4_de_vinheta_com_quadro_do_video_transcribrothers(
        titulo="Consulta",
        efeito="linhas-que-desenham-o-lugar",
        vinheta_id=None,
        caminho_video=video,
        instante_quadro_seguinte=1.2,
        instante_quadro_anterior=0.8,
        duracao_segundos=2.0,
        work=work,
    )

    assert duracao == 2.0
    relatorio = ler_debug_ultima_geracao_vinheta_separador_transcribrothers(work)
    assert relatorio is not None
    assert relatorio["tempos_ms"]["sonda_duracao"] == 0
