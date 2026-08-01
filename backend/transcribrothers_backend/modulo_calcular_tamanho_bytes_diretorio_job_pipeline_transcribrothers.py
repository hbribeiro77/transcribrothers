"""Calcula o tamanho em bytes da pasta de trabalho de um job."""

from __future__ import annotations

import os
from pathlib import Path


def calcular_tamanho_bytes_diretorio_recursivo_transcribrothers(raiz: Path) -> int:
    """Soma o tamanho dos arquivos sob ``raiz``. Pastas inexistentes → 0."""
    if not raiz.is_dir():
        return 0
    total = 0
    stack = [raiz]
    while stack:
        atual = stack.pop()
        try:
            with os.scandir(atual) as it:
                for entry in it:
                    try:
                        if entry.is_symlink():
                            continue
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(Path(entry.path))
                        elif entry.is_file(follow_symlinks=False):
                            total += int(entry.stat(follow_symlinks=False).st_size)
                    except OSError:
                        continue
        except OSError:
            continue
    return total
