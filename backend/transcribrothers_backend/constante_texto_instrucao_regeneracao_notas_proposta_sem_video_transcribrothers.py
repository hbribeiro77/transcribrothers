"""Bloco de instrução para regeneração de notas de proposta sem depender do vídeo."""

TEXTO_INSTRUCAO_REGENERACAO_NOTAS_PROPOSTA_SEM_VIDEO_TRANSCRIBROTHERS = """
Modo documento autônomo (sem vídeo):
- O leitor NÃO terá o vídeo nem o player; as notas devem bastar com texto e imagens em assets/.
- Remova ou substitua links [MM:SS](?t=SEGUNDOS) e menções a assistir à gravação.
- Mantenha seções de decisões, pendências e próximos passos claras.
- Não invente decisões que não constem do documento ou das imagens.
""".strip()
