"""Extrai o texto do primeiro título ATX nível 1 (`# …`) de um Markdown para resumo em listas (ex.: jobs)."""


def extrair_titulo_h1_markdown_para_listagem_jobs_pipeline_transcribrothers(
    markdown: str | None,
    *,
    max_caracteres: int = 200,
) -> str | None:
    """Devolve o texto do primeiro `# título` (não `##`), ou None se não houver."""
    if not isinstance(markdown, str):
        return None
    texto = markdown.replace("\r\n", "\n")
    for raw in texto.split("\n"):
        linha = raw.strip()
        if not linha or linha[0] != "#":
            continue
        nivel = 0
        while nivel < len(linha) and linha[nivel] == "#":
            nivel += 1
        if nivel != 1:
            continue
        resto = linha[1:].lstrip(" \t")
        if not resto:
            continue
        titulo = resto.rstrip()
        while titulo.endswith("#"):
            titulo = titulo[:-1].rstrip()
        if not titulo:
            continue
        if len(titulo) > max_caracteres:
            return titulo[: max_caracteres - 1].rstrip() + "…"
        return titulo
    return None
