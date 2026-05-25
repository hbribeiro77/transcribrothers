"""Extrai texto de PDF/MD/TXT para anexo de contexto no FAB (projeto em branco)."""

from __future__ import annotations

import io
from pathlib import PurePosixPath

from transcribrothers_backend.modulo_util_validar_e_normalizar_contexto_anexos_fab_pedido_transcribrothers import (
    LIMITE_CARACTERES_POR_TEXTO_CONTEXTO_FAB_PEDIDO_TRANSCRIBROTHERS,
)

EXTENSOES_DOCUMENTO_TEXTO_ANEXO_FAB_TRANSCRIBROTHERS = frozenset({".md", ".txt", ".pdf"})
LIMITE_BYTES_DOCUMENTO_ANEXO_FAB_TRANSCRIBROTHERS = 8 * 1024 * 1024


def _extensao_arquivo_documento_anexo_fab_transcribrothers(nome_arquivo: str) -> str:
    return PurePosixPath((nome_arquivo or "").strip()).suffix.lower()


def _extrair_texto_pdf_bytes_transcribrothers(conteudo: bytes) -> str:
    from pypdf import PdfReader

    leitor = PdfReader(io.BytesIO(conteudo))
    partes: list[str] = []
    for pagina in leitor.pages:
        trecho = (pagina.extract_text() or "").strip()
        if trecho:
            partes.append(trecho)
    return "\n\n".join(partes).strip()


def extrair_texto_documento_anexo_contexto_fab_transcribrothers(
    *,
    nome_arquivo: str,
    conteudo_bytes: bytes,
    tipo_mime: str | None = None,
) -> str:
    """Levanta ValueError se tipo não suportado ou conteúdo inválido."""
    if not conteudo_bytes:
        raise ValueError("Arquivo vazio.")
    if len(conteudo_bytes) > LIMITE_BYTES_DOCUMENTO_ANEXO_FAB_TRANSCRIBROTHERS:
        raise ValueError(
            f"Arquivo muito grande (máx. {LIMITE_BYTES_DOCUMENTO_ANEXO_FAB_TRANSCRIBROTHERS // (1024 * 1024)} MB)."
        )

    ext = _extensao_arquivo_documento_anexo_fab_transcribrothers(nome_arquivo)
    mime = (tipo_mime or "").strip().lower()

    if ext in {".md", ".txt"} or mime in {"text/plain", "text/markdown", "text/x-markdown"}:
        try:
            texto = conteudo_bytes.decode("utf-8")
        except UnicodeDecodeError:
            texto = conteudo_bytes.decode("utf-8", errors="replace")
        texto = texto.replace("\r\n", "\n").strip()
        if not texto:
            raise ValueError("O arquivo não contém texto legível.")
        return texto

    if ext == ".pdf" or mime == "application/pdf":
        texto = _extrair_texto_pdf_bytes_transcribrothers(conteudo_bytes)
        if not texto:
            raise ValueError(
                "Não foi possível extrair texto do PDF (pode ser só imagem ou estar protegido)."
            )
        return texto

    raise ValueError(
        "Formato não suportado. Use .md, .txt ou .pdf."
    )


def truncar_texto_documento_para_limite_anexo_fab_transcribrothers(texto: str) -> tuple[str, bool]:
    t = (texto or "").replace("\r\n", "\n").strip()
    limite = LIMITE_CARACTERES_POR_TEXTO_CONTEXTO_FAB_PEDIDO_TRANSCRIBROTHERS
    if len(t) <= limite:
        return t, False
    return t[:limite] + "…", True
