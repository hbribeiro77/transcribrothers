"""Lista arquivos PNG originais (exclui `.anotado.png`) na pasta de assets do job."""

from __future__ import annotations

from pathlib import Path

from transcribrothers_backend.modulo_util_nomenclatura_e_metadados_anotacao_imagens_tutorial_assets_png_transcribrothers import (
    nome_arquivo_png_original_eh_valido_para_anotacao_transcribrothers,
)


def listar_nomes_arquivo_png_original_na_pasta_assets_tutorial_transcribrothers(
    assets_dir: Path,
) -> list[str]:
    if not assets_dir.is_dir():
        return []
    nomes: list[str] = []
    for p in sorted(assets_dir.iterdir(), key=lambda x: x.name.lower()):
        if not p.is_file():
            continue
        nome = p.name
        if nome_arquivo_png_original_eh_valido_para_anotacao_transcribrothers(nome):
            nomes.append(nome)
    return nomes
