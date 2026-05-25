"""Staging temporário de vídeo importado pelo RecBrothers antes de criar job."""

from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import HTTPException, UploadFile

from transcribrothers_backend.modulo_armazenamento_sqlite_modelos_job_pipeline import novo_id_job
from transcribrothers_backend.modulo_validacao_extensao_nome_arquivo_video_upload_local import (
    ErroExtensaoVideoUploadTranscribrothers,
    extrair_extensao_video_sanitizada_para_upload_local,
)

NOME_ARQUIVO_META_STAGING_VIDEO_RECBROTHERS = "staging_meta.json"
NOME_ARQUIVO_EXTRAS_STAGING_RECBROTHERS = "staging_extras_recbrothers.json"
NOME_ARQUIVO_CLIQUES_STAGING_RECBROTHERS = "cliques_demonstracao_bug_recbrothers.json"
NOME_ARQUIVO_CLIQUES_NO_JOB_RECBROTHERS = "cliques_demonstracao_bug_recbrothers.json"
NOME_PREFIXO_ARQUIVO_VIDEO_STAGING = "video"


@dataclass(frozen=True)
class MetadadosStagingVideoRecbrothersTranscribrothers:
    staging_id: str
    filename: str
    size_bytes: int
    ext: str
    created_at: str
    expires_at: str


class ErroStagingVideoTranscribrothers(Exception):
    pass


def _diretorio_raiz_staging(data_dir: Path) -> Path:
    return data_dir / "staging"


def diretorio_staging_video(data_dir: Path, staging_id: str) -> Path:
    return _diretorio_raiz_staging(data_dir) / staging_id


def _caminho_arquivo_video_staging(work: Path, ext: str) -> Path:
    return work / f"{NOME_PREFIXO_ARQUIVO_VIDEO_STAGING}{ext}"


def _caminho_meta_staging(work: Path) -> Path:
    return work / NOME_ARQUIVO_META_STAGING_VIDEO_RECBROTHERS


def _caminho_extras_staging(work: Path) -> Path:
    return work / NOME_ARQUIVO_EXTRAS_STAGING_RECBROTHERS


def _caminho_cliques_staging(work: Path) -> Path:
    return work / NOME_ARQUIVO_CLIQUES_STAGING_RECBROTHERS


def ler_extras_staging_recbrothers_transcribrothers(work: Path) -> dict:
    caminho = _caminho_extras_staging(work)
    if not caminho.is_file():
        return {}
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        return dados if isinstance(dados, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _agora_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parsear_iso_utc(valor: str) -> datetime:
    return datetime.fromisoformat(valor.replace("Z", "+00:00"))


def _meta_de_dict(d: dict) -> MetadadosStagingVideoRecbrothersTranscribrothers:
    return MetadadosStagingVideoRecbrothersTranscribrothers(
        staging_id=str(d["staging_id"]),
        filename=str(d["filename"]),
        size_bytes=int(d["size_bytes"]),
        ext=str(d["ext"]),
        created_at=str(d["created_at"]),
        expires_at=str(d["expires_at"]),
    )


def _gravar_meta(work: Path, meta: MetadadosStagingVideoRecbrothersTranscribrothers) -> None:
    _caminho_meta_staging(work).write_text(
        json.dumps(asdict(meta), ensure_ascii=False),
        encoding="utf-8",
    )


def _ler_meta_ou_none(work: Path) -> MetadadosStagingVideoRecbrothersTranscribrothers | None:
    caminho = _caminho_meta_staging(work)
    if not caminho.is_file():
        return None
    try:
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        return _meta_de_dict(dados)
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        return None


def staging_video_expirado(meta: MetadadosStagingVideoRecbrothersTranscribrothers) -> bool:
    return _agora_utc() >= _parsear_iso_utc(meta.expires_at)


def apagar_diretorio_staging_se_existir(data_dir: Path, staging_id: str) -> None:
    work = diretorio_staging_video(data_dir, staging_id)
    if work.exists():
        shutil.rmtree(work, ignore_errors=True)


async def salvar_upload_video_em_staging_recbrothers_transcribrothers(
    data_dir: Path,
    video: UploadFile,
    max_video_bytes: int,
    ttl_horas: float,
    cliques_json: UploadFile | None = None,
    modo_recbrothers: str | None = None,
) -> tuple[MetadadosStagingVideoRecbrothersTranscribrothers, dict]:
    nome_original = video.filename or "video.webm"
    try:
        ext = extrair_extensao_video_sanitizada_para_upload_local(nome_original)
    except ErroExtensaoVideoUploadTranscribrothers as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    staging_id = novo_id_job()
    work = diretorio_staging_video(data_dir, staging_id)
    work.mkdir(parents=True, exist_ok=True)
    destino_video = _caminho_arquivo_video_staging(work, ext)

    chunk_size = 1024 * 1024
    total = 0
    try:
        with destino_video.open("wb") as f:
            while True:
                bloco = await video.read(chunk_size)
                if not bloco:
                    break
                total += len(bloco)
                if total > max_video_bytes:
                    await video.close()
                    shutil.rmtree(work, ignore_errors=True)
                    raise HTTPException(
                        status_code=413,
                        detail=f"Arquivo excede o limite de {max_video_bytes} bytes.",
                    )
                f.write(bloco)
    finally:
        await video.close()

    criado = _agora_utc()
    expira = criado + timedelta(hours=ttl_horas)
    meta = MetadadosStagingVideoRecbrothersTranscribrothers(
        staging_id=staging_id,
        filename=nome_original,
        size_bytes=total,
        ext=ext,
        created_at=criado.isoformat(),
        expires_at=expira.isoformat(),
    )
    _gravar_meta(work, meta)

    extras: dict = {"modo_recbrothers": (modo_recbrothers or "").strip() or None}
    total_cliques = 0
    if cliques_json is not None:
        conteudo_cliques = await cliques_json.read()
        await cliques_json.close()
        if len(conteudo_cliques) > 2 * 1024 * 1024:
            shutil.rmtree(work, ignore_errors=True)
            raise HTTPException(status_code=413, detail="JSON de cliques excede 2 MB.")
        try:
            parsed = json.loads(conteudo_cliques.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            shutil.rmtree(work, ignore_errors=True)
            raise HTTPException(status_code=400, detail="JSON de cliques inválido.") from e
        lista = parsed.get("cliques") if isinstance(parsed, dict) else parsed
        if not isinstance(lista, list):
            shutil.rmtree(work, ignore_errors=True)
            raise HTTPException(status_code=400, detail="JSON de cliques deve conter array 'cliques'.")
        total_cliques = len(lista)
        _caminho_cliques_staging(work).write_bytes(conteudo_cliques)
        extras["cliques_json_presente"] = True
        extras["total_cliques"] = total_cliques
    else:
        extras["cliques_json_presente"] = False
        extras["total_cliques"] = 0

    _caminho_extras_staging(work).write_text(
        json.dumps(extras, ensure_ascii=False),
        encoding="utf-8",
    )
    return meta, extras


def obter_metadados_staging_video_ou_erro_http(
    data_dir: Path,
    staging_id: str,
) -> MetadadosStagingVideoRecbrothersTranscribrothers:
    work = diretorio_staging_video(data_dir, staging_id)
    if not work.is_dir():
        raise HTTPException(status_code=404, detail="Staging não encontrado.")
    meta = _ler_meta_ou_none(work)
    if meta is None:
        raise HTTPException(status_code=404, detail="Metadados de staging inválidos ou ausentes.")
    if staging_video_expirado(meta):
        apagar_diretorio_staging_se_existir(data_dir, staging_id)
        raise HTTPException(status_code=410, detail="Staging expirado.")
    video_path = _caminho_arquivo_video_staging(work, meta.ext)
    if not video_path.is_file():
        raise HTTPException(status_code=404, detail="Arquivo de vídeo em staging não encontrado.")
    return meta


def resolver_caminho_video_staging(
    data_dir: Path,
    staging_id: str,
) -> tuple[MetadadosStagingVideoRecbrothersTranscribrothers, Path]:
    meta = obter_metadados_staging_video_ou_erro_http(data_dir, staging_id)
    work = diretorio_staging_video(data_dir, staging_id)
    return meta, _caminho_arquivo_video_staging(work, meta.ext)


def obter_metadados_extras_staging_recbrothers(
    data_dir: Path,
    staging_id: str,
) -> dict:
    meta = obter_metadados_staging_video_ou_erro_http(data_dir, staging_id)
    work = diretorio_staging_video(data_dir, meta.staging_id)
    return ler_extras_staging_recbrothers_transcribrothers(work)


def consumir_staging_video_para_destino_job(
    data_dir: Path,
    staging_id: str,
    destino_job_video: Path,
) -> tuple[str, int, str, dict]:
    """Move vídeo staged para o diretório do job, copia cliques se houver e remove staging."""
    meta, origem = resolver_caminho_video_staging(data_dir, staging_id)
    work = diretorio_staging_video(data_dir, staging_id)
    extras = ler_extras_staging_recbrothers_transcribrothers(work)
    destino_job_video.parent.mkdir(parents=True, exist_ok=True)
    if destino_job_video.exists():
        destino_job_video.unlink()
    shutil.move(str(origem), str(destino_job_video))
    cliques_origem = _caminho_cliques_staging(work)
    if cliques_origem.is_file():
        shutil.copy2(
            cliques_origem,
            destino_job_video.parent / NOME_ARQUIVO_CLIQUES_NO_JOB_RECBROTHERS,
        )
    apagar_diretorio_staging_se_existir(data_dir, staging_id)
    return meta.filename, meta.size_bytes, meta.ext, extras
