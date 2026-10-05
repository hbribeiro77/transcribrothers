from transcribrothers_backend.modulo_sanitizar_nome_arquivo_download_video_narrado_content_disposition_transcribrothers import (
    resolver_nome_arquivo_download_video_narrado_content_disposition_transcribrothers,
    sanitizar_nome_arquivo_download_video_narrado_content_disposition_transcribrothers,
)


def test_usa_o_nome_amigavel_e_rejeita_path() -> None:
    assert (
        sanitizar_nome_arquivo_download_video_narrado_content_disposition_transcribrothers(
            "Solicitação de documentos via WhatsApp legendado.mp4"
        )
        == "Solicitação de documentos via WhatsApp legendado.mp4"
    )
    assert (
        sanitizar_nome_arquivo_download_video_narrado_content_disposition_transcribrothers(
            "../../segredo.mp4"
        )
        == "segredo.mp4"
    )


def test_query_vence_titulo_persistido_e_acrescenta_legendado() -> None:
    assert (
        resolver_nome_arquivo_download_video_narrado_content_disposition_transcribrothers(
            nome_arquivo_query="Meu video legendado.mp4",
            titulo_persistido="Outro titulo",
            legendado=True,
            fallback="video_feio.mp4",
        )
        == "Meu video legendado.mp4"
    )
    assert (
        resolver_nome_arquivo_download_video_narrado_content_disposition_transcribrothers(
            nome_arquivo_query=None,
            titulo_persistido="Solicitação de documentos via WhatsApp",
            legendado=True,
            fallback="video_feio.mp4",
        )
        == "Solicitação de documentos via WhatsApp legendado.mp4"
    )
