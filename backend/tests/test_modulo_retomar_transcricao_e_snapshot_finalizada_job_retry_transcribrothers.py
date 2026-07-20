"""Retomada de pipeline: snapshot de transcrição e rascunho de notas no disco."""

from pathlib import Path

from transcribrothers_backend.modulo_persistencia_arquivo_json_snapshot_transcricao_finalizada_job_transcribrothers import (
    carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers,
    gravar_rascunho_notas_proposta_sem_imagens_no_work_transcribrothers,
    gravar_snapshot_transcricao_finalizada_no_work_transcribrothers,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
    SegmentoTranscricaoComTempo,
)
from transcribrothers_backend.modulo_util_reutilizar_artefatos_midia_pipeline_job_retry_transcribrothers import (
    deve_reutilizar_video_entrada_pipeline_sem_redownload_transcribrothers,
)
from transcribrothers_backend.modulo_util_retomar_transcricao_e_rascunho_pipeline_retry_transcribrothers import (
    tentar_carregar_rascunho_notas_proposta_para_retry_pipeline_transcribrothers,
    tentar_carregar_transcricao_finalizada_para_retry_pipeline_transcribrothers,
)


def test_snapshot_transcricao_grava_e_carrega_no_retry(tmp_path: Path) -> None:
    transcricao = ResultadoTranscricaoComSegmentos(
        texto_completo="reunião de produto",
        segmentos=[
            SegmentoTranscricaoComTempo(inicio_segundos=0.0, fim_segundos=2.0, texto="olá"),
        ],
        idioma_detectado="pt",
    )
    gravar_snapshot_transcricao_finalizada_no_work_transcribrothers(tmp_path, transcricao)
    steps = {"transcricao_segmentos": 1, "pipeline_fase": "transcricao_concluida"}
    carregado = tentar_carregar_transcricao_finalizada_para_retry_pipeline_transcribrothers(
        tmp_path,
        steps,
    )
    assert carregado is not None
    assert carregado.texto_completo == "reunião de produto"
    assert len(carregado.segmentos) == 1


def test_carrega_snapshot_do_disco_mesmo_sem_steps_de_conclusao(tmp_path: Path) -> None:
    transcricao = ResultadoTranscricaoComSegmentos(
        texto_completo="x",
        segmentos=[],
        idioma_detectado=None,
    )
    gravar_snapshot_transcricao_finalizada_no_work_transcribrothers(tmp_path, transcricao)
    carregado = tentar_carregar_transcricao_finalizada_para_retry_pipeline_transcribrothers(
        tmp_path,
        {},
    )
    assert carregado is not None
    assert carregado.texto_completo == "x"


def test_rascunho_notas_reutilizado_quando_arquivo_e_flag_existem(tmp_path: Path) -> None:
    gravar_rascunho_notas_proposta_sem_imagens_no_work_transcribrothers(tmp_path, "# Notas\n\nCorpo.")
    steps = {"notas_proposta_rascunho_sem_imagens_ok": True}
    texto = tentar_carregar_rascunho_notas_proposta_para_retry_pipeline_transcribrothers(
        tmp_path,
        steps,
    )
    assert texto is not None
    assert "Notas" in texto


def test_reutiliza_video_upload_local_por_bytes_written(tmp_path: Path) -> None:
    vid = tmp_path / "video_entrada_arquivo_local.mp4"
    vid.write_bytes(b"\x00" * 2048)
    assert (
        deve_reutilizar_video_entrada_pipeline_sem_redownload_transcribrothers(
            vid,
            {"bytes_written": 5000, "source": "upload_local"},
        )
        is True
    )


def test_carregar_snapshot_direto_do_arquivo(tmp_path: Path) -> None:
    transcricao = ResultadoTranscricaoComSegmentos(
        texto_completo="ok",
        segmentos=[],
        idioma_detectado=None,
    )
    gravar_snapshot_transcricao_finalizada_no_work_transcribrothers(tmp_path, transcricao)
    assert carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers(tmp_path) is not None
