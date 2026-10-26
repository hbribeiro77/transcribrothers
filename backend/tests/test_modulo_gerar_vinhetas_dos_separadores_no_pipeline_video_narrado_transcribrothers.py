"""Gera o MP4 de cada intercalário e anexa a fonte na cue."""

from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from transcribrothers_backend.modulo_gerar_vinhetas_dos_separadores_no_pipeline_video_narrado_transcribrothers import (
    aplicar_vinhetas_nos_separadores_de_secao_das_cues_transcribrothers,
)
from transcribrothers_backend.modulo_montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers import (
    CueNarracaoComJanelaVideoTranscribrothers,
)


def _cue(**kwargs) -> CueNarracaoComJanelaVideoTranscribrothers:
    base = dict(
        texto="fala",
        inicio_video_segundos=1.0,
        fim_video_segundos=4.0,
        origem_ancora="markdown_t",
        casado=True,
    )
    base.update(kwargs)
    return CueNarracaoComJanelaVideoTranscribrothers(**base)


@pytest.mark.asyncio
async def test_publica_vinheta_do_separador_e_anexa_id_fonte(tmp_path: Path) -> None:
    cues = [
        _cue(texto="antes", inicio_video_segundos=2.0, fim_video_segundos=8.0),
        _cue(
            texto="Nova funcionalidade",
            inicio_video_segundos=0.0,
            fim_video_segundos=2.0,
            sem_narracao=True,
            eh_separador_secao=True,
            titulo_secao_heading="Nova funcionalidade",
            receita_vinheta_separador={
                "titulo": "Nova funcionalidade",
                "efeito": "linhas-que-desenham-o-lugar",
                "vinheta_id": None,
                "duracao_segundos": 2.0,
                "presenca_da_imagem": 60,
            },
        ),
        _cue(texto="depois", inicio_video_segundos=10.0, fim_video_segundos=14.0),
    ]
    publicar = AsyncMock(
        return_value={"id": "mabc123", "duracao_segundos": 2.0},
    )
    video = tmp_path / "video_entrada_arquivo_local.mp4"
    video.write_bytes(b"vid")
    saida = await aplicar_vinhetas_nos_separadores_de_secao_das_cues_transcribrothers(
        cues,
        work=tmp_path,
        job_id="job-1",
        caminho_video=video,
        preferencias_encode=None,
        publicar=publicar,
    )
    sep = saida[1]
    assert sep.id_fonte_video == "mabc123"
    assert sep.inicio_video_segundos == 0.0
    assert sep.fim_video_segundos == 2.0
    kwargs = publicar.await_args.kwargs
    assert kwargs["titulo"] == "Nova funcionalidade"
    assert kwargs["efeito"] == "linhas-que-desenham-o-lugar"
    assert kwargs["instante_quadro_anterior"] == pytest.approx(7.95)
    assert kwargs["instante_quadro_seguinte"] == pytest.approx(10.0)
    assert kwargs["presenca_da_imagem"] == 60
    assert kwargs["cores"] is None
    assert publicar.await_count == 1


@pytest.mark.asyncio
async def test_vinheta_salva_nao_sobrescreve_presenca_nem_paleta(tmp_path: Path) -> None:
    cues = [
        _cue(
            texto="Nova funcionalidade",
            inicio_video_segundos=0.0,
            fim_video_segundos=2.0,
            eh_separador_secao=True,
            titulo_secao_heading="Nova funcionalidade",
            receita_vinheta_separador={
                "titulo": "Nova funcionalidade",
                "efeito": "barras-que-se-cruzam",
                "vinheta_id": "abc-salva",
                "duracao_segundos": 2.0,
            },
        ),
        _cue(texto="depois", inicio_video_segundos=10.0, fim_video_segundos=14.0),
    ]
    publicar = AsyncMock(return_value={"id": "mabc123", "duracao_segundos": 2.0})
    video = tmp_path / "video_entrada_arquivo_local.mp4"
    video.write_bytes(b"vid")
    await aplicar_vinhetas_nos_separadores_de_secao_das_cues_transcribrothers(
        cues,
        work=tmp_path,
        job_id="job-1",
        caminho_video=video,
        preferencias_encode=None,
        publicar=publicar,
    )
    kwargs = publicar.await_args.kwargs
    assert kwargs["vinheta_id"] == "abc-salva"
    assert kwargs["presenca_da_imagem"] is None
    assert kwargs["cores"] is None


@pytest.mark.asyncio
async def test_ajuste_na_cue_ainda_manda_presenca_e_paleta_da_receita(tmp_path: Path) -> None:
    cues = [
        _cue(
            texto="Nova funcionalidade",
            inicio_video_segundos=0.0,
            fim_video_segundos=2.0,
            eh_separador_secao=True,
            receita_vinheta_separador={
                "titulo": "Nova funcionalidade",
                "efeito": None,
                "vinheta_id": "abc-salva",
                "duracao_segundos": 2.0,
                "presenca_da_imagem": 40,
                "cores": {
                    "fundo": "#111111",
                    "plano_principal": "#222222",
                    "plano_destaque": "#333333",
                    "texto": "#ffffff",
                },
            },
        ),
    ]
    publicar = AsyncMock(return_value={"id": "mabc123", "duracao_segundos": 2.0})
    await aplicar_vinhetas_nos_separadores_de_secao_das_cues_transcribrothers(
        cues,
        work=tmp_path,
        job_id="job-1",
        caminho_video=None,
        preferencias_encode=None,
        publicar=publicar,
    )
    kwargs = publicar.await_args.kwargs
    assert kwargs["presenca_da_imagem"] == 40
    assert kwargs["cores"]["texto"] == "#ffffff"
