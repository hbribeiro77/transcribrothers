from transcribrothers_backend.modulo_normalizar_receita_transicoes_secao_pipeline_video_narrado_transcribrothers import (
    normalizar_receita_transicoes_secao_pipeline_video_narrado_transcribrothers,
)


def test_sem_corpo_nao_inclui_transicoes() -> None:
    rec = normalizar_receita_transicoes_secao_pipeline_video_narrado_transcribrothers(None)
    assert rec["incluir"] is False


def test_incluir_usa_efeito_e_duracao_de_2s() -> None:
    rec = normalizar_receita_transicoes_secao_pipeline_video_narrado_transcribrothers(
        {
            "incluir": True,
            "efeito": "barras-que-se-cruzam",
            "duracao_segundos": 2,
        }
    )
    assert rec["incluir"] is True
    assert rec["efeito"] == "barras-que-se-cruzam"
    assert rec["duracao_segundos"] == 2.0


def test_duracao_invalida_cai_em_2s_e_efeito_desconhecido_em_linhas() -> None:
    rec = normalizar_receita_transicoes_secao_pipeline_video_narrado_transcribrothers(
        {"incluir": True, "efeito": "nao-existe", "duracao_segundos": 99}
    )
    assert rec["efeito"] == "linhas-que-desenham-o-lugar"
    assert rec["duracao_segundos"] == 2.0
    assert rec["vinheta_id"] is None


def test_preserva_vinheta_id_da_vinheta_salva() -> None:
    rec = normalizar_receita_transicoes_secao_pipeline_video_narrado_transcribrothers(
        {
            "incluir": True,
            "efeito": "barras-que-se-cruzam",
            "duracao_segundos": 2,
            "vinheta_id": "  abc-salva  ",
        }
    )
    assert rec["vinheta_id"] == "abc-salva"
    assert rec["efeito"] == "barras-que-se-cruzam"
