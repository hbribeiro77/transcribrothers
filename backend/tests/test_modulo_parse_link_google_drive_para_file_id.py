import pytest

from transcribrothers_backend.modulo_parse_link_google_drive_para_file_id import (
    ErroParseLinkGoogleDrive,
    extrair_file_id_google_drive_de_url,
    formatar_timestamp_segundos_para_mmss,
)


def test_extrair_file_id_formato_file_d_view() -> None:
    url = "https://drive.google.com/file/d/16ohFIxQ3e_iAV8R1UBC4gZIxd_fFXfYh/view?usp=sharing"
    r = extrair_file_id_google_drive_de_url(url)
    assert r.file_id == "16ohFIxQ3e_iAV8R1UBC4gZIxd_fFXfYh"


def test_extrair_file_id_rejeita_vazio() -> None:
    with pytest.raises(ErroParseLinkGoogleDrive):
        extrair_file_id_google_drive_de_url("")


def test_formatar_timestamp_mmss() -> None:
    assert formatar_timestamp_segundos_para_mmss(65) == "1:05"
    assert formatar_timestamp_segundos_para_mmss(3600) == "1:00:00"

