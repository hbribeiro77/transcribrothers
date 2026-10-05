"""Parâmetros do tutorial Markdown: modo ilustrativo (esparso) vs passo a passo de software (denso)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from transcribrothers_backend.modulo_cliente_litellm_geracao_tutorial_markdown import (
    INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_COM_IMAGENS_PADRAO_TRANSCRIBROTHERS,
    INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_SEM_IMAGENS_PADRAO_TRANSCRIBROTHERS,
    INSTRUCAO_LITELLM_TUTORIAL_PASSO_A_PASSO_SOFTWARE_MARKDOWN_COM_IMAGENS_PADRAO_TRANSCRIBROTHERS,
    INSTRUCAO_LITELLM_TUTORIAL_PASSO_A_PASSO_SOFTWARE_MARKDOWN_SEM_IMAGENS_PADRAO_TRANSCRIBROTHERS,
    INSTRUCAO_LITELLM_TUTORIAL_PASSO_A_PASSO_SOFTWARE_RASCUNHO_SEM_IMAGENS_CAPTURA_FRAMES_SOB_DEMANDA_TRANSCRIBROTHERS,
    INSTRUCAO_LITELLM_TUTORIAL_RASCUNHO_SEM_IMAGENS_CAPTURA_FRAMES_SOB_DEMANDA_TRANSCRIBROTHERS,
    INSTRUCOES_REVISAO_LITELLM_INCORPORAR_FRAMES_APOS_CAPTURA_SOB_DEMANDA_TRANSCRIBROTHERS,
    INSTRUCOES_REVISAO_LITELLM_INCORPORAR_FRAMES_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_cliente_litellm_planejamento_instantes_captura_frames_tutorial_transcribrothers import (
    SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS,
    SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_TUTORIAL_TRANSCRIBROTHERS,
)

ID_DESTINO_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS = "tutorial_passo_a_passo_software"
ID_PIPELINE_INICIAL_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS = (
    "pipeline_inicial_tutorial_passo_a_passo_software"
)

MAX_FRAMES_POR_MINUTO_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS = 30
MAX_FRAMES_TOTAL_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS = 192
MARGEM_MINIMA_SEGUNDOS_LINKS_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS = 0.5
MAX_INSTANTES_PLANEJAMENTO_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS = 192
MAX_INSTANTES_PLANEJAMENTO_TUTORIAL_ESPARSO_TRANSCRIBROTHERS = 64


@dataclass(frozen=True)
class ParametrosCapturaTutorialMarkdownTranscribrothers:
    denso: bool
    handler_rascunho: str
    handler_plano: str
    handler_gerador: str
    instrucao_rascunho_sem_imagens: str
    system_planejamento_instantes: str
    instrucao_incorporar_frames: str
    instrucao_gerador_sem_imagens: str
    instrucao_gerador_com_imagens: str
    max_frames_per_minute_override: int | None
    tutorial_max_frames_total_override: int | None
    margem_minima_segundos_entre_links_override: float | None
    max_instantes_planejamento: int


def job_steps_indicam_tutorial_passo_a_passo_software_transcribrothers(
    steps: dict[str, Any] | None,
) -> bool:
    if not steps:
        return False
    destino = str(steps.get("destino_apos_transcricao") or "").strip()
    if destino == ID_DESTINO_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS:
        return True
    copiado_de = str(steps.get("pipeline_custom_copiado_de") or "").strip()
    return copiado_de == ID_PIPELINE_INICIAL_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS


def resolver_parametros_captura_tutorial_markdown_transcribrothers(
    steps: dict[str, Any] | None,
) -> ParametrosCapturaTutorialMarkdownTranscribrothers:
    if job_steps_indicam_tutorial_passo_a_passo_software_transcribrothers(steps):
        return ParametrosCapturaTutorialMarkdownTranscribrothers(
            denso=True,
            handler_rascunho="rascunho_tutorial_passo_a_passo_software",
            handler_plano="plano_capturas_tutorial_passo_a_passo_software",
            handler_gerador="gerador_tutorial_passo_a_passo_software",
            instrucao_rascunho_sem_imagens=(
                INSTRUCAO_LITELLM_TUTORIAL_PASSO_A_PASSO_SOFTWARE_RASCUNHO_SEM_IMAGENS_CAPTURA_FRAMES_SOB_DEMANDA_TRANSCRIBROTHERS
            ),
            system_planejamento_instantes=(
                SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS
            ),
            instrucao_incorporar_frames=(
                INSTRUCOES_REVISAO_LITELLM_INCORPORAR_FRAMES_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS
            ),
            instrucao_gerador_sem_imagens=(
                INSTRUCAO_LITELLM_TUTORIAL_PASSO_A_PASSO_SOFTWARE_MARKDOWN_SEM_IMAGENS_PADRAO_TRANSCRIBROTHERS
            ),
            instrucao_gerador_com_imagens=(
                INSTRUCAO_LITELLM_TUTORIAL_PASSO_A_PASSO_SOFTWARE_MARKDOWN_COM_IMAGENS_PADRAO_TRANSCRIBROTHERS
            ),
            max_frames_per_minute_override=MAX_FRAMES_POR_MINUTO_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS,
            tutorial_max_frames_total_override=MAX_FRAMES_TOTAL_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS,
            margem_minima_segundos_entre_links_override=(
                MARGEM_MINIMA_SEGUNDOS_LINKS_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS
            ),
            max_instantes_planejamento=MAX_INSTANTES_PLANEJAMENTO_TUTORIAL_PASSO_A_PASSO_SOFTWARE_TRANSCRIBROTHERS,
        )
    return ParametrosCapturaTutorialMarkdownTranscribrothers(
        denso=False,
        handler_rascunho="rascunho_tutorial_sob_demanda",
        handler_plano="plano_capturas_tutorial",
        handler_gerador="gerador_tutorial_markdown",
        instrucao_rascunho_sem_imagens=(
            INSTRUCAO_LITELLM_TUTORIAL_RASCUNHO_SEM_IMAGENS_CAPTURA_FRAMES_SOB_DEMANDA_TRANSCRIBROTHERS
        ),
        system_planejamento_instantes=SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_TUTORIAL_TRANSCRIBROTHERS,
        instrucao_incorporar_frames=INSTRUCOES_REVISAO_LITELLM_INCORPORAR_FRAMES_APOS_CAPTURA_SOB_DEMANDA_TRANSCRIBROTHERS,
        instrucao_gerador_sem_imagens=INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_SEM_IMAGENS_PADRAO_TRANSCRIBROTHERS,
        instrucao_gerador_com_imagens=INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_COM_IMAGENS_PADRAO_TRANSCRIBROTHERS,
        max_frames_per_minute_override=None,
        tutorial_max_frames_total_override=None,
        margem_minima_segundos_entre_links_override=None,
        max_instantes_planejamento=MAX_INSTANTES_PLANEJAMENTO_TUTORIAL_ESPARSO_TRANSCRIBROTHERS,
    )
