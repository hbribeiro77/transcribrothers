"""Biblioteca de vídeos de tela extras por job (B-roll), sem concatenar no video_entrada."""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

NOME_PASTA_BIBLIOTECA_MIDIAS_TELA_TRANSCRIBROTHERS = "biblioteca_midias_tela"
NOME_ARQUIVO_MANIFESTO_BIBLIOTECA_MIDIAS_TELA_TRANSCRIBROTHERS = "manifesto.json"
ID_FONTE_VIDEO_ENTRADA_TRANSCRIBROTHERS = "entrada"

_RE_ID_MIDIA_TELA = re.compile(r"^m[a-f0-9]{8,32}$", re.IGNORECASE)
_RE_NOME_ARQUIVO_SEGURO = re.compile(r"^[a-zA-Z0-9._-]+$")


class ErroBibliotecaMidiasTelaTranscribrothers(Exception):
    """Erro de domínio da biblioteca de mídias de tela."""


@dataclass(frozen=True)
class ItemBibliotecaMidiaTelaTranscribrothers:
    id: str
    nome_arquivo: str
    nome_original: str
    criado_em: str
    tamanho_bytes: int
    duracao_segundos: float | None = None

    def para_dict(self, *, job_id: str) -> dict[str, Any]:
        return {
            "id": self.id,
            "nome_arquivo": self.nome_arquivo,
            "nome_original": self.nome_original,
            "criado_em": self.criado_em,
            "tamanho_bytes": self.tamanho_bytes,
            "duracao_segundos": self.duracao_segundos,
            "url_arquivo": (
                f"/api/jobs/{job_id}/biblioteca-midias-tela/arquivo/{self.id}"
            ),
        }


def diretorio_biblioteca_midias_tela_do_work_transcribrothers(work: Path) -> Path:
    return work / NOME_PASTA_BIBLIOTECA_MIDIAS_TELA_TRANSCRIBROTHERS


def normalizar_id_fonte_video_transcribrothers(id_fonte: str | None) -> str:
    bruto = (id_fonte or "").strip()
    if not bruto or bruto == ID_FONTE_VIDEO_ENTRADA_TRANSCRIBROTHERS:
        return ID_FONTE_VIDEO_ENTRADA_TRANSCRIBROTHERS
    return bruto


def _caminho_manifesto_biblioteca_transcribrothers(work: Path) -> Path:
    return diretorio_biblioteca_midias_tela_do_work_transcribrothers(work) / (
        NOME_ARQUIVO_MANIFESTO_BIBLIOTECA_MIDIAS_TELA_TRANSCRIBROTHERS
    )


def _ler_itens_manifesto_brutos_transcribrothers(work: Path) -> list[dict[str, Any]]:
    caminho = _caminho_manifesto_biblioteca_transcribrothers(work)
    if not caminho.is_file():
        return []
    try:
        raw = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(raw, dict):
        return []
    lista = raw.get("itens")
    if not isinstance(lista, list):
        return []
    saida: list[dict[str, Any]] = []
    for item in lista:
        if isinstance(item, dict) and str(item.get("id") or "").strip():
            saida.append(item)
    return saida


def _gravar_itens_manifesto_transcribrothers(work: Path, itens: list[dict[str, Any]]) -> None:
    pasta = diretorio_biblioteca_midias_tela_do_work_transcribrothers(work)
    pasta.mkdir(parents=True, exist_ok=True)
    payload = {"versao": 1, "quantidade": len(itens), "itens": itens}
    _caminho_manifesto_biblioteca_transcribrothers(work).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _item_de_dict_transcribrothers(raw: dict[str, Any], pasta: Path) -> ItemBibliotecaMidiaTelaTranscribrothers | None:
    id_item = str(raw.get("id") or "").strip()
    nome_arquivo = str(raw.get("nome_arquivo") or "").strip()
    if not id_item or not nome_arquivo:
        return None
    if not _RE_ID_MIDIA_TELA.match(id_item):
        return None
    if not _RE_NOME_ARQUIVO_SEGURO.match(nome_arquivo):
        return None
    caminho = pasta / nome_arquivo
    if not caminho.is_file():
        return None
    tamanho = int(raw.get("tamanho_bytes") or 0)
    if tamanho <= 0:
        try:
            tamanho = caminho.stat().st_size
        except OSError:
            tamanho = 0
    dur_raw = raw.get("duracao_segundos")
    duracao: float | None
    try:
        duracao = float(dur_raw) if dur_raw is not None else None
        if duracao is not None and not (duracao > 0):
            duracao = None
    except (TypeError, ValueError):
        duracao = None
    return ItemBibliotecaMidiaTelaTranscribrothers(
        id=id_item,
        nome_arquivo=nome_arquivo,
        nome_original=str(raw.get("nome_original") or nome_arquivo),
        criado_em=str(raw.get("criado_em") or ""),
        tamanho_bytes=tamanho,
        duracao_segundos=duracao,
    )


def listar_itens_biblioteca_midias_tela_do_work_transcribrothers(
    work: Path,
) -> list[ItemBibliotecaMidiaTelaTranscribrothers]:
    pasta = diretorio_biblioteca_midias_tela_do_work_transcribrothers(work)
    if not pasta.is_dir():
        return []
    saida: list[ItemBibliotecaMidiaTelaTranscribrothers] = []
    for raw in _ler_itens_manifesto_brutos_transcribrothers(work):
        item = _item_de_dict_transcribrothers(raw, pasta)
        if item is not None:
            saida.append(item)
    return saida


def alocar_destino_novo_item_biblioteca_midias_tela_transcribrothers(
    *,
    work: Path,
    nome_original: str,
    extensao_com_ponto: str,
) -> tuple[ItemBibliotecaMidiaTelaTranscribrothers, Path]:
    """Gera id/nome de arquivo e devolve o Path de destino (ainda sem manifesto)."""
    ext = (extensao_com_ponto or ".mp4").lower()
    if not ext.startswith("."):
        ext = f".{ext}"
    id_item = f"m{uuid.uuid4().hex[:12]}"
    nome_arquivo = f"{id_item}{ext}"
    pasta = diretorio_biblioteca_midias_tela_do_work_transcribrothers(work)
    pasta.mkdir(parents=True, exist_ok=True)
    criado_em = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    item = ItemBibliotecaMidiaTelaTranscribrothers(
        id=id_item,
        nome_arquivo=nome_arquivo,
        nome_original=(nome_original or nome_arquivo).strip() or nome_arquivo,
        criado_em=criado_em,
        tamanho_bytes=0,
        duracao_segundos=None,
    )
    return item, pasta / nome_arquivo


def confirmar_item_biblioteca_midias_tela_no_manifesto_transcribrothers(
    *,
    work: Path,
    item: ItemBibliotecaMidiaTelaTranscribrothers,
    tamanho_bytes: int,
    duracao_segundos: float | None = None,
) -> ItemBibliotecaMidiaTelaTranscribrothers:
    confirmado = ItemBibliotecaMidiaTelaTranscribrothers(
        id=item.id,
        nome_arquivo=item.nome_arquivo,
        nome_original=item.nome_original,
        criado_em=item.criado_em,
        tamanho_bytes=max(0, int(tamanho_bytes)),
        duracao_segundos=duracao_segundos if (duracao_segundos or 0) > 0 else None,
    )
    itens = _ler_itens_manifesto_brutos_transcribrothers(work)
    itens = [r for r in itens if str(r.get("id") or "") != confirmado.id]
    itens.append(
        {
            "id": confirmado.id,
            "nome_arquivo": confirmado.nome_arquivo,
            "nome_original": confirmado.nome_original,
            "criado_em": confirmado.criado_em,
            "tamanho_bytes": confirmado.tamanho_bytes,
            "duracao_segundos": confirmado.duracao_segundos,
        }
    )
    _gravar_itens_manifesto_transcribrothers(work, itens)
    return confirmado


def atualizar_tamanho_item_biblioteca_midias_tela_transcribrothers(
    work: Path,
    id_item: str,
    tamanho_bytes: int,
) -> None:
    itens = _ler_itens_manifesto_brutos_transcribrothers(work)
    mudou = False
    for raw in itens:
        if str(raw.get("id") or "") == id_item:
            raw["tamanho_bytes"] = max(0, int(tamanho_bytes))
            mudou = True
            break
    if mudou:
        _gravar_itens_manifesto_transcribrothers(work, itens)


def resolver_caminho_arquivo_biblioteca_midias_tela_por_id_transcribrothers(
    work: Path,
    id_item: str,
) -> Path:
    id_limpo = (id_item or "").strip()
    if not _RE_ID_MIDIA_TELA.match(id_limpo):
        raise ErroBibliotecaMidiasTelaTranscribrothers("Identificador de mídia inválido.")
    for item in listar_itens_biblioteca_midias_tela_do_work_transcribrothers(work):
        if item.id == id_limpo:
            caminho = diretorio_biblioteca_midias_tela_do_work_transcribrothers(work) / item.nome_arquivo
            if not caminho.is_file():
                raise ErroBibliotecaMidiasTelaTranscribrothers("Arquivo da mídia não encontrado.")
            # Evita path traversal: nome já validado no manifesto.
            return caminho
    raise ErroBibliotecaMidiasTelaTranscribrothers("Mídia de tela não encontrada.")


def apagar_item_biblioteca_midias_tela_por_id_transcribrothers(work: Path, id_item: str) -> None:
    id_limpo = (id_item or "").strip()
    if not _RE_ID_MIDIA_TELA.match(id_limpo):
        raise ErroBibliotecaMidiasTelaTranscribrothers("Identificador de mídia inválido.")
    pasta = diretorio_biblioteca_midias_tela_do_work_transcribrothers(work)
    itens = _ler_itens_manifesto_brutos_transcribrothers(work)
    restantes: list[dict[str, Any]] = []
    removido: dict[str, Any] | None = None
    for raw in itens:
        if str(raw.get("id") or "") == id_limpo:
            removido = raw
        else:
            restantes.append(raw)
    if removido is None:
        raise ErroBibliotecaMidiasTelaTranscribrothers("Mídia de tela não encontrada.")
    nome_arquivo = str(removido.get("nome_arquivo") or "").strip()
    if nome_arquivo and _RE_NOME_ARQUIVO_SEGURO.match(nome_arquivo):
        caminho = pasta / nome_arquivo
        try:
            if caminho.is_file():
                caminho.unlink()
        except OSError as exc:
            raise ErroBibliotecaMidiasTelaTranscribrothers(
                "Não foi possível apagar o arquivo da mídia."
            ) from exc
    _gravar_itens_manifesto_transcribrothers(work, restantes)


def resolver_caminho_video_fonte_por_id_no_work_transcribrothers(
    *,
    work: Path,
    id_fonte_video: str | None,
    caminho_video_entrada: Path,
) -> Path:
    """Resolve o Path de tela para uma cue: entrada ou item da biblioteca."""
    id_norm = normalizar_id_fonte_video_transcribrothers(id_fonte_video)
    if id_norm == ID_FONTE_VIDEO_ENTRADA_TRANSCRIBROTHERS:
        if not caminho_video_entrada.is_file():
            raise ErroBibliotecaMidiasTelaTranscribrothers(
                "Vídeo de entrada do projeto não encontrado."
            )
        return caminho_video_entrada
    return resolver_caminho_arquivo_biblioteca_midias_tela_por_id_transcribrothers(work, id_norm)
