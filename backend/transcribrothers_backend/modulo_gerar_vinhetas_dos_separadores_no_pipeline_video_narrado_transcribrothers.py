"""Gera o MP4 de cada intercalário do pipeline e anexa o id da biblioteca na cue."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_gerar_vinheta_de_separador_com_quadro_do_video_transcribrothers import (
    publicar_vinheta_na_biblioteca_de_midias_do_job_transcribrothers,
)
from transcribrothers_backend.modulo_montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers import (
    CueNarracaoComJanelaVideoTranscribrothers,
    substituir_campos_da_cue_narracao_com_janela_transcribrothers,
)
from transcribrothers_backend.modulo_preferencias_encode_video_narrado_transcribrothers import (
    PreferenciasEncodeVideoNarradoTranscribrothers,
)

PublicarVinhetaSeparadorTranscribrothers = Callable[..., Awaitable[dict[str, object]]]
AtualizarProgressoTransicoesTranscribrothers = Callable[[dict[str, Any]], Awaitable[None]]
PRESENCA_PADRAO_IMAGEM_MODELO_SEPARADOR_SECAO = 60


def presenca_e_cores_para_render_da_vinheta_do_separador_transcribrothers(
    receita: dict[str, Any],
    *,
    vinheta_id: str | None,
) -> tuple[int | None, dict[str, str] | None]:
    cores = receita.get("cores") if isinstance(receita.get("cores"), dict) else None
    bruto = receita.get("presenca_da_imagem")
    if bruto is not None:
        try:
            return int(bruto), cores
        except (TypeError, ValueError):
            pass
    if vinheta_id:
        return None, cores
    return PRESENCA_PADRAO_IMAGEM_MODELO_SEPARADOR_SECAO, cores


def _fonte_e_o_video_de_entrada_transcribrothers(id_fonte: str) -> bool:
    bruto = (id_fonte or "").strip()
    return not bruto or bruto == "entrada"


def instantes_dos_quadros_da_transicao_do_separador_nas_cues_transcribrothers(
    cues: list[CueNarracaoComJanelaVideoTranscribrothers],
    indice_separador: int,
) -> tuple[float, float | None]:
    anterior = cues[indice_separador - 1] if indice_separador > 0 else None
    seguinte = cues[indice_separador + 1] if indice_separador + 1 < len(cues) else None
    instante_seguinte = 0.0
    if seguinte is not None and _fonte_e_o_video_de_entrada_transcribrothers(
        str(getattr(seguinte, "id_fonte_video", "") or "")
    ):
        instante_seguinte = max(0.0, float(seguinte.inicio_video_segundos))
    instante_anterior = None
    if anterior is not None and _fonte_e_o_video_de_entrada_transcribrothers(
        str(getattr(anterior, "id_fonte_video", "") or "")
    ):
        instante_anterior = max(0.0, float(anterior.fim_video_segundos) - 0.05)
    return instante_seguinte, instante_anterior


async def aplicar_vinhetas_nos_separadores_de_secao_das_cues_transcribrothers(
    cues: list[CueNarracaoComJanelaVideoTranscribrothers],
    *,
    work: Path,
    job_id: str,
    caminho_video: Path | None,
    preferencias_encode: PreferenciasEncodeVideoNarradoTranscribrothers | None = None,
    publicar: PublicarVinhetaSeparadorTranscribrothers | None = None,
    atualizar_progresso: AtualizarProgressoTransicoesTranscribrothers | None = None,
) -> list[CueNarracaoComJanelaVideoTranscribrothers]:
    publicar_efetivo = publicar or publicar_vinheta_na_biblioteca_de_midias_do_job_transcribrothers
    indices = [i for i, c in enumerate(cues) if bool(getattr(c, "eh_separador_secao", False))]
    if not indices:
        return list(cues)
    saida = list(cues)
    total = len(indices)
    for ordem, indice in enumerate(indices, start=1):
        if atualizar_progresso is not None:
            await atualizar_progresso(
                {
                    "video_narrado_transicao_indice": ordem,
                    "video_narrado_transicao_total": total,
                    "video_narrado_transicao_titulo": saida[indice].texto,
                }
            )
        cue = saida[indice]
        receita = dict(getattr(cue, "receita_vinheta_separador", None) or {})
        vinheta_id = str(receita.get("vinheta_id") or "").strip() or None
        presenca, cores = presenca_e_cores_para_render_da_vinheta_do_separador_transcribrothers(
            receita,
            vinheta_id=vinheta_id,
        )
        seguinte, anterior = instantes_dos_quadros_da_transicao_do_separador_nas_cues_transcribrothers(
            saida,
            indice,
        )
        item = await publicar_efetivo(
            work=work,
            job_id=job_id,
            titulo=str(receita.get("titulo") or cue.texto or "Seção"),
            efeito=str(receita.get("efeito") or "").strip() or None,
            vinheta_id=vinheta_id,
            caminho_video=caminho_video,
            instante_quadro_seguinte=seguinte,
            instante_quadro_anterior=anterior,
            duracao_segundos=float(receita.get("duracao_segundos") or cue.fim_video_segundos or 2.0),
            presenca_da_imagem=presenca,
            cores=cores,
            preferencias_encode=preferencias_encode,
        )
        id_midia = str((item or {}).get("id") or "").strip()
        try:
            duracao = float((item or {}).get("duracao_segundos") or 0.0)
        except (TypeError, ValueError):
            duracao = 0.0
        if duracao <= 0:
            duracao = float(receita.get("duracao_segundos") or 2.0)
        receita = {**receita, "duracao_segundos": duracao}
        saida[indice] = substituir_campos_da_cue_narracao_com_janela_transcribrothers(
            cue,
            id_fonte_video=id_midia,
            inicio_video_segundos=0.0,
            fim_video_segundos=duracao,
            receita_vinheta_separador=receita,
        )
    return saida
