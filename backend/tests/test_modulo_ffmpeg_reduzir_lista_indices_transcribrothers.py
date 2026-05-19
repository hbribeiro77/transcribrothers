from transcribrothers_backend.modulo_ffmpeg_extrair_audio_e_capturar_frames_por_timestamps import (
    reduzir_lista_indice_para_no_maximo_n_itens_transcribrothers,
)


def test_reduzir_lista_indices_zero_ou_negativo_nao_altera() -> None:
    assert reduzir_lista_indice_para_no_maximo_n_itens_transcribrothers([0, 1, 2, 3], 0) == [0, 1, 2, 3]
    assert reduzir_lista_indice_para_no_maximo_n_itens_transcribrothers([0, 1, 2, 3], -1) == [0, 1, 2, 3]


def test_reduzir_lista_indices_mantem_quando_abaixo_do_teto() -> None:
    assert reduzir_lista_indice_para_no_maximo_n_itens_transcribrothers([0, 5, 9], 10) == [0, 5, 9]


def test_reduzir_lista_indices_distribui_em_subconjunto() -> None:
    out = reduzir_lista_indice_para_no_maximo_n_itens_transcribrothers(list(range(10)), 3)
    assert len(out) <= 3
    assert out[0] == 0
    assert out[-1] == 9
