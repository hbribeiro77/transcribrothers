from transcribrothers_backend.modulo_prompt_sistema_chat_agente_ferramentas_documento_job_transcribrothers import (
    montar_prompt_sistema_chat_agente_ferramentas_documento_job_transcribrothers,
)


def test_prompt_agente_pede_markdown_da_bolha_e_nao_reescrever_documento() -> None:
    prompt = montar_prompt_sistema_chat_agente_ferramentas_documento_job_transcribrothers()
    assert "Markdown da bolha" in prompt
    assert r"\n\n" in prompt
    assert "não junte vários pontos" in prompt.lower()
    assert "(1)" in prompt
    assert "Não reescreva o documento inteiro" in prompt
    assert '"texto"' in prompt


def test_prompt_agente_exige_reemitir_tools_quando_usuario_confirma_pendente() -> None:
    prompt = montar_prompt_sistema_chat_agente_ferramentas_documento_job_transcribrothers()
    assert "Propostas pendentes" in prompt
    assert "executar=true" in prompt
    assert "Não peça outra confirmação" in prompt
    assert "ferramentas vazias" in prompt.lower() or "ferramentas=[]" in prompt


def test_prompt_agente_pede_atalho_de_tempo_no_item_correspondente() -> None:
    prompt = montar_prompt_sistema_chat_agente_ferramentas_documento_job_transcribrothers()
    assert "[12:40](?t=" in prompt
    assert "junto do item" in prompt.lower() or "no item" in prompt.lower()
