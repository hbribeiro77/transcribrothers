"""Instrução LiteLLM quando não há JSON de cliques RecBrothers (timestamps inferidos)."""

TEXTO_INSTRUCAO_REPRODUCAO_BUG_SEM_JSON_CLIQUES_TRANSCRIBROTHERS = """
Modo sem JSON de cliques RecBrothers:
- Não há registro automático de cliques; os instantes dos screenshots foram inferidos da transcrição e/ou da duração do vídeo.
- Derive passos de reprodução do bug a partir da transcrição (quando houver) e das imagens anexadas, na ordem temporal dos frames.
- Um passo numerado por momento relevante; alinhe cada passo ao frame correspondente quando possível.
- Não invente URLs, coordenadas ou cliques específicos que não apareçam na transcrição ou nas telas.
- Use links temporais [MM:SS](?t=SEGUNDOS) com SEGUNDOS coerentes com o instante do frame/pseudo-clique.
- Incorpore cada imagem com ![](caminho_exato) do frame do passo.
- Finalize com "## Resultado observado" descrevendo o comportamento incorreto quando inferível da transcrição ou das telas.
""".strip()
