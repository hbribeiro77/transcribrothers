"""Geração LiteLLM de notas de proposta (reunião de funcionalidade) em Markdown."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from transcribrothers_backend.constante_texto_instrucao_geracao_notas_proposta_funcionalidade_com_imagens_transcribrothers import (
    INSTRUCOES_REVISAO_LITELLM_INCORPORAR_FRAMES_APOS_CAPTURA_NOTAS_PROPOSTA_FUNCIONALIDADE_TRANSCRIBROTHERS,
    TEXTO_INSTRUCAO_GERACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_COM_IMAGENS_TRANSCRIBROTHERS,
)
from transcribrothers_backend.constante_texto_instrucao_geracao_notas_proposta_funcionalidade_rascunho_sem_imagens_transcribrothers import (
    TEXTO_INSTRUCAO_GERACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_RASCUNHO_SEM_IMAGENS_TRANSCRIBROTHERS,
)
from transcribrothers_backend.constante_texto_instrucao_regeneracao_notas_proposta_sem_video_transcribrothers import (
    TEXTO_INSTRUCAO_REGENERACAO_NOTAS_PROPOSTA_SEM_VIDEO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_cliente_litellm_geracao_tutorial_markdown import (
    gerar_tutorial_markdown_com_litellm_a_partir_de_transcricao_e_frames,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
)


def montar_instrucao_prefixo_litellm_notas_proposta_funcionalidade_transcribrothers(
    *,
    documento_autonomo_sem_video: bool = False,
    instrucoes_revisao_humana: str | None = None,
    rascunho_sem_imagens: bool = False,
) -> str:
    if rascunho_sem_imagens:
        partes = [TEXTO_INSTRUCAO_GERACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_RASCUNHO_SEM_IMAGENS_TRANSCRIBROTHERS]
    else:
        partes = [TEXTO_INSTRUCAO_GERACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_COM_IMAGENS_TRANSCRIBROTHERS]
    if documento_autonomo_sem_video:
        partes.append(TEXTO_INSTRUCAO_REGENERACAO_NOTAS_PROPOSTA_SEM_VIDEO_TRANSCRIBROTHERS)
    rev = (instrucoes_revisao_humana or "").strip()
    if rev:
        partes.append(f"Instruções adicionais do revisor humano:\n{rev}")
    return "\n\n".join(partes)


async def gerar_rascunho_notas_proposta_funcionalidade_com_litellm_transcribrothers(
    *,
    transcricao: ResultadoTranscricaoComSegmentos,
    modelo: str,
    api_key: str | None,
    api_base: str | None,
    httpx_verify: bool | str = True,
    httpx_timeout_connect_segundos: float = 120.0,
    httpx_timeout_read_segundos: float = 7200.0,
    steps_para_log_decisoes_ia: dict[str, Any] | None = None,
) -> str:
    return await gerar_tutorial_markdown_com_litellm_a_partir_de_transcricao_e_frames(
        transcricao=transcricao,
        caminhos_frames_rel_job=[],
        modelo=modelo,
        api_key=api_key,
        api_base=api_base,
        httpx_verify=httpx_verify,
        httpx_timeout_connect_segundos=httpx_timeout_connect_segundos,
        httpx_timeout_read_segundos=httpx_timeout_read_segundos,
        enviar_screenshots_png_como_imagens_multimodais=False,
        instrucao_prefixo_litellm_custom=montar_instrucao_prefixo_litellm_notas_proposta_funcionalidade_transcribrothers(
            rascunho_sem_imagens=True,
        ),
        steps_para_log_decisoes_ia=steps_para_log_decisoes_ia,
        log_etapa_geracao_tutorial="geracao_rascunho_notas_proposta",
    )


async def gerar_markdown_notas_proposta_funcionalidade_com_litellm_transcribrothers(
    *,
    transcricao: ResultadoTranscricaoComSegmentos,
    caminhos_frames_rel_job: list[tuple[float, str]],
    modelo: str,
    api_key: str | None,
    api_base: str | None,
    httpx_verify: bool | str = True,
    httpx_timeout_connect_segundos: float = 120.0,
    httpx_timeout_read_segundos: float = 7200.0,
    diretorio_assets_absoluto: Path,
    steps_para_log_decisoes_ia: dict[str, Any] | None = None,
    instrucoes_revisao_humana: str | None = None,
    markdown_atual_para_contexto: str | None = None,
    markdown_rascunho_para_contexto: str | None = None,
    documento_autonomo_sem_video: bool = False,
    log_etapa_geracao_tutorial: str = "geracao_markdown_notas_proposta",
) -> str:
    prefixo = montar_instrucao_prefixo_litellm_notas_proposta_funcionalidade_transcribrothers(
        documento_autonomo_sem_video=documento_autonomo_sem_video,
        instrucoes_revisao_humana=instrucoes_revisao_humana,
    )
    bloco_contexto = markdown_atual_para_contexto or markdown_rascunho_para_contexto
    instrucoes_revisao_final = instrucoes_revisao_humana
    if markdown_rascunho_para_contexto and not (instrucoes_revisao_humana or "").strip():
        instrucoes_revisao_final = (
            INSTRUCOES_REVISAO_LITELLM_INCORPORAR_FRAMES_APOS_CAPTURA_NOTAS_PROPOSTA_FUNCIONALIDADE_TRANSCRIBROTHERS
        )
    tem_frames = bool(caminhos_frames_rel_job)
    return await gerar_tutorial_markdown_com_litellm_a_partir_de_transcricao_e_frames(
        transcricao=transcricao,
        caminhos_frames_rel_job=caminhos_frames_rel_job,
        modelo=modelo,
        api_key=api_key,
        api_base=api_base,
        httpx_verify=httpx_verify,
        httpx_timeout_connect_segundos=httpx_timeout_connect_segundos,
        httpx_timeout_read_segundos=httpx_timeout_read_segundos,
        diretorio_assets_absoluto=diretorio_assets_absoluto,
        enviar_screenshots_png_como_imagens_multimodais=tem_frames,
        rels_png_anexo_ja_resolvidos=list(caminhos_frames_rel_job) if tem_frames else None,
        instrucao_prefixo_litellm_custom=prefixo,
        instrucoes_revisao_humana=instrucoes_revisao_final,
        bloco_markdown_tutorial_atual_para_contexto_em_revisao=bloco_contexto,
        steps_para_log_decisoes_ia=steps_para_log_decisoes_ia,
        log_etapa_geracao_tutorial=log_etapa_geracao_tutorial,
    )
