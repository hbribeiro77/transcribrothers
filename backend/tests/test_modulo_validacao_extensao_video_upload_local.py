import pytest

from transcribrothers_backend.modulo_validacao_extensao_nome_arquivo_video_upload_local import (
    ErroExtensaoVideoUploadTranscribrothers,
    extrair_extensao_video_sanitizada_para_upload_local,
)


def test_extensao_mp4_ok() -> None:
    assert extrair_extensao_video_sanitizada_para_upload_local("meu.video.MP4") == ".mp4"


def test_extensao_exe_rejeita() -> None:
    with pytest.raises(ErroExtensaoVideoUploadTranscribrothers):
        extrair_extensao_video_sanitizada_para_upload_local("malware.exe")
