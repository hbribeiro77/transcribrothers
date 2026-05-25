"""Bloco de instrução para regeneração de roteiro de reprodução de bug sem depender do vídeo."""

TEXTO_INSTRUCAO_REGENERACAO_REPRODUCAO_BUG_SEM_VIDEO_TRANSCRIBROTHERS = """
Modo documento autônomo (sem vídeo):
- O leitor NÃO terá o vídeo nem o player; o roteiro deve bastar com texto e imagens em assets/.
- Remova ou substitua links [MM:SS](?t=SEGUNDOS) e menções a assistir/gravar/reproduzir o vídeo.
- Cada passo relevante deve ter ação clara (clique, campo, URL) e a imagem correspondente com ![](assets/…png) do frame do clique.
- Não invente cliques que não constem do JSON de cliques.
- Mantenha ou complete a seção "## Resultado observado" com o comportamento incorreto, usando transcrição e imagens quando existirem.
""".strip()
