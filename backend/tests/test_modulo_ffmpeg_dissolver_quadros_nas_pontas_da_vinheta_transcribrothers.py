import pytest

from transcribrothers_backend.modulo_ffmpeg_dissolver_quadros_nas_pontas_da_vinheta_transcribrothers import (
    filtro_de_dissolucao_dos_quadros_nas_pontas_da_vinheta,
)


def test_a_dissolucao_entra_no_comeco_e_sai_no_fim_sem_encurtar_o_clipe():
    filtro, saida = filtro_de_dissolucao_dos_quadros_nas_pontas_da_vinheta(
        5,
        tem_quadro_anterior=True,
        tem_quadro_seguinte=True,
    )

    assert "fade=t=out:st=0:d=0.300:alpha=1" in filtro
    assert "fade=t=in:st=4.700:d=0.300:alpha=1" in filtro
    assert saida == "com_seguinte"


def test_a_dissolucao_encaixa_os_quadros_no_tamanho_do_video_sem_cortar():
    filtro, _ = filtro_de_dissolucao_dos_quadros_nas_pontas_da_vinheta(
        5,
        tem_quadro_anterior=True,
        tem_quadro_seguinte=True,
        largura=1366,
        altura=768,
    )

    assert "scale=1366:768:force_original_aspect_ratio=decrease" in filtro
    assert "pad=1366:768:(ow-iw)/2:(oh-ih)/2" in filtro
    assert "1920:1080" not in filtro
    assert "force_original_aspect_ratio=increase" not in filtro


@pytest.mark.asyncio
async def test_a_dissolucao_usa_preset_veryfast(monkeypatch, tmp_path):
    from pathlib import Path

    from transcribrothers_backend.modulo_ffmpeg_dissolver_quadros_nas_pontas_da_vinheta_transcribrothers import (
        aplicar_dissolucao_dos_quadros_nas_pontas_da_vinheta,
    )

    visto: dict[str, list[str]] = {}

    async def fake_ffmpeg(argumentos):
        visto["argumentos"] = list(argumentos)
        Path(argumentos[-1]).write_bytes(b"mp4")

    monkeypatch.setattr(
        "transcribrothers_backend.modulo_ffmpeg_dissolver_quadros_nas_pontas_da_vinheta_transcribrothers.executar_ffmpeg_com_argumentos",
        fake_ffmpeg,
    )
    mp4 = tmp_path / "vinheta.mp4"
    mp4.write_bytes(b"mp4")
    quadro = tmp_path / "quadro.png"
    quadro.write_bytes(b"png")

    await aplicar_dissolucao_dos_quadros_nas_pontas_da_vinheta(
        mp4,
        duracao_segundos=5,
        quadro_seguinte=quadro,
    )

    assert visto["argumentos"][visto["argumentos"].index("-preset") + 1] == "veryfast"
