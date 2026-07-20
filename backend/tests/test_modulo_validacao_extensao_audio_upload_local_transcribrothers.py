import pytest

from transcribrothers_backend.modulo_validacao_extensao_nome_arquivo_audio_upload_local_transcribrothers import (
    ErroExtensaoAudioUploadTranscribrothers,
    classificar_tipo_entrada_midia_por_nome_arquivo_transcribrothers,
    extrair_extensao_audio_sanitizada_para_upload_local,
)


def test_extensao_wav_ok_transcribrothers() -> None:
    assert extrair_extensao_audio_sanitizada_para_upload_local("fala.WAV") == ".wav"


def test_extensao_mp3_ok_transcribrothers() -> None:
    assert extrair_extensao_audio_sanitizada_para_upload_local("track.mp3") == ".mp3"


def test_extensao_exe_rejeita_como_audio_transcribrothers() -> None:
    with pytest.raises(ErroExtensaoAudioUploadTranscribrothers):
        extrair_extensao_audio_sanitizada_para_upload_local("malware.exe")


def test_classificar_tipo_entrada_video_e_audio_transcribrothers() -> None:
    assert classificar_tipo_entrada_midia_por_nome_arquivo_transcribrothers("a.webm") == "video"
    assert classificar_tipo_entrada_midia_por_nome_arquivo_transcribrothers("b.flac") == "audio"


def test_classificar_tipo_entrada_extensao_desconhecida_transcribrothers() -> None:
    with pytest.raises(ValueError, match="Extensão não permitida"):
        classificar_tipo_entrada_midia_por_nome_arquivo_transcribrothers("x.txt")
