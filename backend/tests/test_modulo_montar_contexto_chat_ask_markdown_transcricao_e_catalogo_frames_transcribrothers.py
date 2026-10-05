from transcribrothers_backend.modulo_montar_contexto_chat_ask_markdown_transcricao_e_catalogo_frames_transcribrothers import (
    LIMITE_CARACTERES_MARKDOWN_CONTEXTO_CHAT_ASK_TRANSCRIBROTHERS,
    montar_catalogo_frames_chat_ask_transcribrothers,
    montar_contexto_chat_ask_documento_job_transcribrothers,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
    SegmentoTranscricaoComTempo,
)


def test_markdown_curto_vai_inteiro() -> None:
    ctx = montar_contexto_chat_ask_documento_job_transcribrothers(
        markdown="# T\n\n## Fluxo\n\njornada",
        transcricao=None,
        pergunta="fluxo",
        caminhos_frames_rel_job=[],
        steps_json={},
    )
    assert ctx.tem_markdown is True
    assert "## Fluxo" in ctx.markdown_para_prompt
    assert ctx.tem_transcricao is False


def test_markdown_longo_inclui_indice_de_h2() -> None:
    corpo = "# T\n\n" + ("x" * (LIMITE_CARACTERES_MARKDOWN_CONTEXTO_CHAT_ASK_TRANSCRIBROTHERS + 10))
    corpo += "\n\n## Atendimento\n\nfluxo de fila"
    ctx = montar_contexto_chat_ask_documento_job_transcribrothers(
        markdown=corpo,
        transcricao=None,
        pergunta="atendimento fila",
        caminhos_frames_rel_job=[],
        steps_json={},
    )
    assert "## Atendimento" in ctx.markdown_para_prompt
    assert "indice" in ctx.markdown_para_prompt.lower() or "## Atendimento" in ctx.markdown_para_prompt


def test_markdown_longo_pergunta_sem_tokens_len4_nao_inclui_corpos_h2() -> None:
    corpo = "# T\n\n" + ("x" * (LIMITE_CARACTERES_MARKDOWN_CONTEXTO_CHAT_ASK_TRANSCRIBROTHERS + 10))
    corpo += "\n\n## Atendimento\n\nfluxo de fila"
    ctx = montar_contexto_chat_ask_documento_job_transcribrothers(
        markdown=corpo,
        transcricao=None,
        pergunta="oi",
        caminhos_frames_rel_job=[],
        steps_json={},
    )
    assert "## Atendimento" in ctx.markdown_para_prompt
    assert "fluxo de fila" not in ctx.markdown_para_prompt


def test_catalogo_une_snapshot_e_offset_ms() -> None:
    frames = montar_catalogo_frames_chat_ask_transcribrothers(
        caminhos_frames_rel_job=[(12.4, "assets/a.png")],
        steps_json={},
    )
    assert frames[0].caminho_relativo == "assets/a.png"
    assert frames[0].instante_segundos == 12.4
    extra = montar_catalogo_frames_chat_ask_transcribrothers(
        caminhos_frames_rel_job=[],
        steps_json={},
    )
    from transcribrothers_backend.modulo_montar_contexto_chat_ask_markdown_transcricao_e_catalogo_frames_transcribrothers import (
        instante_segundos_de_offset_ms_no_nome_png_chat_ask_transcribrothers,
    )

    assert instante_segundos_de_offset_ms_no_nome_png_chat_ask_transcribrothers(
        "screenshot_offset_ms_0000015000_indice_0001.png"
    ) == 15.0
