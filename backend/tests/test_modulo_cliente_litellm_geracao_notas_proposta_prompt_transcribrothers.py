"""Testes dos prefixos/prompts LiteLLM para notas de proposta."""

from transcribrothers_backend.constante_texto_instrucao_geracao_notas_proposta_funcionalidade_com_imagens_transcribrothers import (
    TEXTO_INSTRUCAO_GERACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_COM_IMAGENS_TRANSCRIBROTHERS,
)
from transcribrothers_backend.constante_texto_instrucao_geracao_notas_proposta_funcionalidade_rascunho_sem_imagens_transcribrothers import (
    TEXTO_INSTRUCAO_GERACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_RASCUNHO_SEM_IMAGENS_TRANSCRIBROTHERS,
)
from transcribrothers_backend.constante_texto_instrucao_regeneracao_notas_proposta_sem_video_transcribrothers import (
    TEXTO_INSTRUCAO_REGENERACAO_NOTAS_PROPOSTA_SEM_VIDEO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_cliente_litellm_geracao_notas_proposta_funcionalidade_markdown_transcribrothers import (
    montar_instrucao_prefixo_litellm_notas_proposta_funcionalidade_transcribrothers,
)
from transcribrothers_backend.modulo_cliente_litellm_planejamento_instantes_captura_frames_tutorial_transcribrothers import (
    SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_NOTAS_PROPOSTA_FUNCIONALIDADE_TRANSCRIBROTHERS,
)


def test_prefixo_rascunho_contem_secoes_notas_proposta() -> None:
    prefixo = montar_instrucao_prefixo_litellm_notas_proposta_funcionalidade_transcribrothers(
        rascunho_sem_imagens=True,
    )
    assert TEXTO_INSTRUCAO_GERACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_RASCUNHO_SEM_IMAGENS_TRANSCRIBROTHERS in prefixo
    assert "Decisões tomadas" in prefixo
    assert "![](assets/" in prefixo or "NÃO inclua imagens" in prefixo


def test_prefixo_final_com_imagens_e_sem_video() -> None:
    prefixo = montar_instrucao_prefixo_litellm_notas_proposta_funcionalidade_transcribrothers(
        documento_autonomo_sem_video=True,
    )
    assert TEXTO_INSTRUCAO_GERACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_COM_IMAGENS_TRANSCRIBROTHERS in prefixo
    assert TEXTO_INSTRUCAO_REGENERACAO_NOTAS_PROPOSTA_SEM_VIDEO_TRANSCRIBROTHERS in prefixo


def test_system_prompt_planejador_notas_prioriza_slides() -> None:
    assert "slides" in SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_NOTAS_PROPOSTA_FUNCIONALIDADE_TRANSCRIBROTHERS.lower()
    assert "mockup" in SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_NOTAS_PROPOSTA_FUNCIONALIDADE_TRANSCRIBROTHERS.lower()
