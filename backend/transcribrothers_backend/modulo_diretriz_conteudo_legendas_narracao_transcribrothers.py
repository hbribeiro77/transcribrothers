"""
Diretriz de conteúdo das legendas/narração (etapa de limpeza IA).

Controla *como* o texto do Markdown vira cue (legenda = TTS).
Não altera voz, temperatura nem ritmo do motor TTS.
"""

from __future__ import annotations

from dataclasses import dataclass

CHAVE_STEPS_PIPELINE_VIDEO_NARRADO_DIRETRIZ_CONTEUDO_LEGENDAS_TRANSCRIBROTHERS = (
    "pipeline_video_narrado_diretriz_conteudo_legendas"
)

DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS = "conservador"
DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_FALAVEL_TRANSCRIBROTHERS = "mais_falavel"
DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DIDATICO_TRANSCRIBROTHERS = "mais_didatico"
DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS = "mais_descontraido"
DIRETRIZ_CONTEUDO_LEGENDAS_PADRAO_TRANSCRIBROTHERS = (
    DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS
)

_IDS_DIRETRIZ = frozenset(
    {
        DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS,
        DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_FALAVEL_TRANSCRIBROTHERS,
        DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DIDATICO_TRANSCRIBROTHERS,
        DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS,
    }
)

# Limites de crescimento da guarda (conservador = histórico).
_CRESCIMENTO_RELATIVO_POR_DIRETRIZ: dict[str, float] = {
    DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS: 0.4,
    DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_FALAVEL_TRANSCRIBROTHERS: 1.2,
    DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DIDATICO_TRANSCRIBROTHERS: 1.2,
    DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS: 1.4,
}
_CRESCIMENTO_ABSOLUTO_POR_DIRETRIZ: dict[str, int] = {
    DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS: 48,
    DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_FALAVEL_TRANSCRIBROTHERS: 120,
    DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DIDATICO_TRANSCRIBROTHERS: 120,
    DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS: 140,
}

# Texto anexado ao system da limpeza IA (conservador = vazio = comportamento histórico).
_TEXTO_EXTRA_PROMPT_POR_DIRETRIZ: dict[str, str] = {
    DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS: "",
    DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_FALAVEL_TRANSCRIBROTHERS: (
        "\n### DIRETRIZ ATIVA: mais falável (OBRIGATÓRIA — prevalece sobre «mudanças mínimas»)\n"
        "Além de limpar lixo Markdown/âncoras, REESCREVA cada cue para soar natural "
        "quando lida em voz alta.\n"
        "- Transforme títulos e rótulos secos em frase falada completa.\n"
        "- Exemplos (mesmo sentido):\n"
        "  · «Validação de Nome Social no Portal» → "
        "«Agora vamos ver a validação de nome social no portal.»\n"
        "  · «Confirmar: Valida que o dado…» → "
        "«Em Confirmar, o sistema valida que o dado…»\n"
        "  · «Opções de Ação:» → «Veja as opções de ação.»\n"
        "- Pode acrescentar conectores curtos («agora», «neste passo», «veja») "
        "sem inventar passos novos.\n"
        "- Mantenha nomes de campos/botões reconhecíveis.\n"
        "- NÃO resuma o tutorial, NÃO invente conteúdo, NÃO traduza.\n"
    ),
    DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DIDATICO_TRANSCRIBROTHERS: (
        "\n### DIRETRIZ ATIVA: mais didático (OBRIGATÓRIA — prevalece sobre «mudanças mínimas»)\n"
        "Além de limpar lixo, REESCREVA cada cue no tom de tutorial passo a passo: "
        "claro, acolhedor e orientado à ação.\n"
        "- Exemplos (mesmo sentido):\n"
        "  · «Novo Cadastro:» → «Abra Novo cadastro.»\n"
        "  · «Processo de Validação» → "
        "«Neste passo, acompanhe o processo de validação.»\n"
        "  · «Não é nome social: Permite mover…» → "
        "«Se não for nome social, você pode mover a informação…»\n"
        "- Oriente o ouvinte sem inventar passos que não estavam no texto.\n"
        "- NÃO resuma o tutorial e NÃO traduza.\n"
    ),
    DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS: (
        "\n### DIRETRIZ ATIVA: mais descontraído (OBRIGATÓRIA — prevalece sobre «mudanças mínimas»)\n"
        "Além de limpar lixo, REESCREVA cada cue com tom leve e conversacional, "
        "como alguém explicando o sistema para um colega — sem gíria ofensiva "
        "e sem perder o profissionalismo institucional.\n"
        "- Exemplos (mesmo sentido):\n"
        "  · «Validação de Nome Social no Portal» → "
        "«Beleza: vamos ver a validação de nome social no portal.»\n"
        "  · «Aviso de Uso: O sistema reforça…» → "
        "«Só um aviso: o sistema reforça…»\n"
        "  · «Fechar: Caso não se sinta confortável…» → "
        "«Se preferir, dá para fechar — mas…»\n"
        "- Pode usar «beleza», «só um aviso», «dá para» com moderação.\n"
        "- Mantenha nomes de campos/botões; NÃO invente passos; NÃO resuma; NÃO traduza.\n"
    ),
}


@dataclass(frozen=True)
class OpcaoDiretrizConteudoLegendasUiTranscribrothers:
    id: str
    rotulo: str
    descricao: str


def listar_opcoes_diretriz_conteudo_legendas_para_ui_transcribrothers() -> list[
    OpcaoDiretrizConteudoLegendasUiTranscribrothers
]:
    return [
        OpcaoDiretrizConteudoLegendasUiTranscribrothers(
            id=DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS,
            rotulo="Conservador (padrão)",
            descricao="Limpeza mínima: remove lixo e deixa forma narrável.",
        ),
        OpcaoDiretrizConteudoLegendasUiTranscribrothers(
            id=DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_FALAVEL_TRANSCRIBROTHERS,
            rotulo="Mais falável",
            descricao="Reescreve para frases naturais de narração em voz alta.",
        ),
        OpcaoDiretrizConteudoLegendasUiTranscribrothers(
            id=DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DIDATICO_TRANSCRIBROTHERS,
            rotulo="Mais didático",
            descricao="Tom de tutorial passo a passo, orientando a ação.",
        ),
        OpcaoDiretrizConteudoLegendasUiTranscribrothers(
            id=DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS,
            rotulo="Mais descontraído",
            descricao="Tom leve e conversacional, ainda institucional.",
        ),
    ]


def normalizar_diretriz_conteudo_legendas_transcribrothers(valor: object) -> str:
    """None/vazio/inválido → conservador. Aceita aliases comuns."""
    if valor is None or (isinstance(valor, str) and not valor.strip()):
        return DIRETRIZ_CONTEUDO_LEGENDAS_PADRAO_TRANSCRIBROTHERS
    texto = str(valor).strip().lower().replace("-", "_").replace(" ", "_")
    aliases = {
        "conservador": DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS,
        "padrao": DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS,
        "padrão": DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS,
        "default": DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS,
        "minimo": DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS,
        "mínimo": DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS,
        "mais_falavel": DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_FALAVEL_TRANSCRIBROTHERS,
        "mais_falável": DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_FALAVEL_TRANSCRIBROTHERS,
        "falavel": DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_FALAVEL_TRANSCRIBROTHERS,
        "falável": DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_FALAVEL_TRANSCRIBROTHERS,
        "natural": DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_FALAVEL_TRANSCRIBROTHERS,
        "mais_didatico": DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DIDATICO_TRANSCRIBROTHERS,
        "mais_didático": DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DIDATICO_TRANSCRIBROTHERS,
        "didatico": DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DIDATICO_TRANSCRIBROTHERS,
        "didático": DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DIDATICO_TRANSCRIBROTHERS,
        "tutorial": DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DIDATICO_TRANSCRIBROTHERS,
        "mais_descontraido": DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS,
        "mais_descontraído": DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS,
        "descontraido": DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS,
        "descontraído": DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS,
        "leve": DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS,
        "casual": DIRETRIZ_CONTEUDO_LEGENDAS_MAIS_DESCONTRAIDO_TRANSCRIBROTHERS,
    }
    if texto in aliases:
        return aliases[texto]
    if texto in _IDS_DIRETRIZ:
        return texto
    return DIRETRIZ_CONTEUDO_LEGENDAS_PADRAO_TRANSCRIBROTHERS


def texto_extra_prompt_limpeza_pela_diretriz_conteudo_legendas_transcribrothers(
    diretriz: object,
) -> str:
    """Trecho a anexar ao system da limpeza; vazio no conservador."""
    did = normalizar_diretriz_conteudo_legendas_transcribrothers(diretriz)
    return _TEXTO_EXTRA_PROMPT_POR_DIRETRIZ.get(did, "")


def diretriz_conteudo_permite_reescrever_texto_transcribrothers(diretriz: object) -> bool:
    """True quando o preset pede reescrita além da limpeza mínima."""
    did = normalizar_diretriz_conteudo_legendas_transcribrothers(diretriz)
    return did != DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS


def limites_crescimento_guarda_limpeza_pela_diretriz_transcribrothers(
    diretriz: object,
) -> tuple[float, int]:
    """(crescimento_relativo, crescimento_absoluto_chars) para a guarda da limpeza."""
    did = normalizar_diretriz_conteudo_legendas_transcribrothers(diretriz)
    rel = _CRESCIMENTO_RELATIVO_POR_DIRETRIZ.get(
        did,
        _CRESCIMENTO_RELATIVO_POR_DIRETRIZ[DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS],
    )
    abs_chars = _CRESCIMENTO_ABSOLUTO_POR_DIRETRIZ.get(
        did,
        _CRESCIMENTO_ABSOLUTO_POR_DIRETRIZ[DIRETRIZ_CONTEUDO_LEGENDAS_CONSERVADOR_TRANSCRIBROTHERS],
    )
    return float(rel), int(abs_chars)


def rotulo_diretriz_conteudo_legendas_para_ui_transcribrothers(diretriz: object) -> str:
    did = normalizar_diretriz_conteudo_legendas_transcribrothers(diretriz)
    for op in listar_opcoes_diretriz_conteudo_legendas_para_ui_transcribrothers():
        if op.id == did:
            return op.rotulo
    return did
