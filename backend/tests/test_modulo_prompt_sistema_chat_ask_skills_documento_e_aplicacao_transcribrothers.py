from transcribrothers_backend.modulo_orquestrar_turno_chat_ask_job_transcribrothers import (
    _mensagens_litellm_chat_ask_transcribrothers,
)
from transcribrothers_backend.modulo_prompt_sistema_chat_ask_skills_documento_e_aplicacao_transcribrothers import (
    montar_prompt_sistema_chat_ask_documento_job_transcribrothers,
)


def test_prompt_sistema_ask_tem_duas_skills_e_roteamento() -> None:
    prompt = montar_prompt_sistema_chat_ask_documento_job_transcribrothers()
    assert "skill_documento" in prompt
    assert "skill_aplicacao" in prompt
    assert "escolha uma skill" in prompt.lower() or "escolha só uma skill" in prompt.lower()
    assert "não misture" in prompt.lower() or "nao misture" in prompt.lower()


def test_prompt_skill_aplicacao_explica_chips_do_agente() -> None:
    prompt = montar_prompt_sistema_chat_ask_documento_job_transcribrothers()
    assert "Sem vídeo" in prompt
    assert "Revisão profunda" in prompt
    assert "Edição parcial" in prompt
    assert "Ask" in prompt
    assert "Agente" in prompt


def test_prompt_skill_documento_ainda_pede_json_e_nao_reescrever() -> None:
    prompt = montar_prompt_sistema_chat_ask_documento_job_transcribrothers()
    assert '"texto"' in prompt
    assert "instantes_imagem_segundos" in prompt
    assert "Não gere um tutorial novo" in prompt


def test_prompt_ask_pede_markdown_da_bolha_e_nao_paragrafo_unico_com_numeracao() -> None:
    prompt = montar_prompt_sistema_chat_ask_documento_job_transcribrothers()
    assert "Markdown da bolha" in prompt
    assert r"\n\n" in prompt
    assert "não junte vários pontos" in prompt.lower()
    assert "(1)" in prompt
    assert "Não gere um tutorial novo" in prompt


def test_prompt_ask_pede_atalho_de_tempo_no_item_correspondente() -> None:
    prompt = montar_prompt_sistema_chat_ask_documento_job_transcribrothers()
    assert "[12:40](?t=" in prompt
    assert "junto do item" in prompt.lower() or "no item" in prompt.lower()


def test_orquestrador_ask_envia_prompt_com_skills_no_system() -> None:
    mensagens = _mensagens_litellm_chat_ask_transcribrothers(
        historico_anterior=[],
        conteudo_usuario="o que é revisão profunda?",
    )
    assert mensagens[0]["role"] == "system"
    assert mensagens[0]["content"] == montar_prompt_sistema_chat_ask_documento_job_transcribrothers()
    assert "skill_aplicacao" in mensagens[0]["content"]
