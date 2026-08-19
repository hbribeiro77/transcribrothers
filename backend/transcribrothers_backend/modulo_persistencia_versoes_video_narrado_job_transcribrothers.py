"""Versiona snapshots do vídeo narrado (MP4 + VTT + WAV + cues) por job."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_ffmpeg_substituir_audio_video_por_narracao_tts_wav_transcribrothers import (
    CHAVE_STEPS_JSON_VIDEO_COM_NARRACAO_TTS_TRANSCRIBROTHERS,
    NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_gerar_narracao_tts_markdown_job_via_litellm_transcribrothers import (
    CHAVE_STEPS_JSON_NARRACAO_TTS_TRANSCRIBROTHERS,
    NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_obter_duracao_midia_segundos_via_ffprobe import (
    _obter_duracao_video_segundos_via_ffprobe_sync,
)
from transcribrothers_backend.modulo_persistencia_manifest_cues_narracao_janelas_video_job_transcribrothers import (
    NOME_ARQUIVO_MANIFEST_CUES_NARRACAO_JANELAS_VIDEO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_resolver_executavel_ffmpeg_ffprobe_transcribrothers import (
    resolver_caminho_ffmpeg_transcribrothers,
)
from transcribrothers_backend.modulo_util_gerar_arquivo_vtt_a_partir_cues_legendas_transcribrothers import (
    CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS,
    NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_util_resolver_markdown_escopo_pipeline_video_narrado_transcribrothers import (
    CHAVE_STEPS_MARKDOWN_ESCOPO_VIDEO_NARRADO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_validar_e_ajustar_janelas_video_cues_sem_sobreposicao_transcribrothers import (
    nome_subpasta_wavs_narracao_por_cue_transcribrothers,
)

NOME_PASTA_VIDEOS_NARRADOS_TRANSCRIBROTHERS = "videos_narrados"
NOME_ARQUIVO_MANIFESTO_VERSOES_VIDEO_NARRADO_TRANSCRIBROTHERS = "manifesto.json"
NOME_ARQUIVO_META_VERSAO_VIDEO_NARRADO_TRANSCRIBROTHERS = "meta.json"
NOME_ARQUIVO_THUMBNAIL_VERSAO_VIDEO_NARRADO_TRANSCRIBROTHERS = "thumbnail.jpg"

_RE_ID_VERSAO = re.compile(r"^v(\d{4,})$")


class ErroVersaoVideoNarradoTranscribrothers(ValueError):
    """Operação inválida sobre versões do vídeo narrado."""


@dataclass(frozen=True)
class MetaVersaoVideoNarradoTranscribrothers:
    id: str
    criado_em: str
    origem: str
    escopo_modo: str
    escopo_titulos: list[str]
    voz_tts: str
    duracao_segundos: float
    tem_thumbnail: bool

    def para_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "criado_em": self.criado_em,
            "origem": self.origem,
            "escopo_modo": self.escopo_modo,
            "escopo_titulos": list(self.escopo_titulos),
            "voz_tts": self.voz_tts,
            "duracao_segundos": float(self.duracao_segundos),
            "tem_thumbnail": bool(self.tem_thumbnail),
        }


@dataclass(frozen=True)
class ResultadoSnapshotVersaoVideoNarradoTranscribrothers:
    meta: MetaVersaoVideoNarradoTranscribrothers
    caminho_pasta: Path


def diretorio_videos_narrados_do_work_transcribrothers(work: Path) -> Path:
    return work / NOME_PASTA_VIDEOS_NARRADOS_TRANSCRIBROTHERS


def caminho_manifesto_versoes_video_narrado_transcribrothers(work: Path) -> Path:
    return (
        diretorio_videos_narrados_do_work_transcribrothers(work)
        / NOME_ARQUIVO_MANIFESTO_VERSOES_VIDEO_NARRADO_TRANSCRIBROTHERS
    )


def caminho_pasta_versao_video_narrado_transcribrothers(work: Path, versao_id: str) -> Path:
    vid = (versao_id or "").strip()
    if not _RE_ID_VERSAO.match(vid):
        raise ErroVersaoVideoNarradoTranscribrothers(f"Identificador de versão inválido: {versao_id!r}.")
    return diretorio_videos_narrados_do_work_transcribrothers(work) / vid


def _carregar_manifesto_bruto_transcribrothers(work: Path) -> dict[str, Any]:
    caminho = caminho_manifesto_versoes_video_narrado_transcribrothers(work)
    if not caminho.is_file():
        return {"versao": 1, "versao_atual_id": None, "versoes": []}
    try:
        raw = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"versao": 1, "versao_atual_id": None, "versoes": []}
    if not isinstance(raw, dict):
        return {"versao": 1, "versao_atual_id": None, "versoes": []}
    versoes = raw.get("versoes")
    if not isinstance(versoes, list):
        versoes = []
    return {
        "versao": int(raw.get("versao") or 1),
        "versao_atual_id": str(raw.get("versao_atual_id") or "").strip() or None,
        "versoes": [v for v in versoes if isinstance(v, dict)],
    }


def _gravar_manifesto_bruto_transcribrothers(work: Path, manifesto: dict[str, Any]) -> None:
    pasta = diretorio_videos_narrados_do_work_transcribrothers(work)
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = caminho_manifesto_versoes_video_narrado_transcribrothers(work)
    caminho.write_text(json.dumps(manifesto, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _proximo_id_versao_transcribrothers(manifesto: dict[str, Any]) -> str:
    maior = 0
    for item in manifesto.get("versoes") or []:
        if not isinstance(item, dict):
            continue
        m = _RE_ID_VERSAO.match(str(item.get("id") or ""))
        if m:
            maior = max(maior, int(m.group(1)))
    return f"v{maior + 1:04d}"


def _escopo_de_steps_transcribrothers(steps: dict[str, Any] | None) -> tuple[str, list[str]]:
    if not steps:
        return "documento", []
    bruto = steps.get(CHAVE_STEPS_MARKDOWN_ESCOPO_VIDEO_NARRADO_TRANSCRIBROTHERS)
    if not isinstance(bruto, dict):
        return "documento", []
    modo = str(bruto.get("modo") or "").strip().lower()
    if modo != "secoes":
        return "documento", []
    titulos_raw = bruto.get("titulos")
    titulos: list[str] = []
    if isinstance(titulos_raw, list):
        for t in titulos_raw:
            s = str(t or "").strip()
            if s:
                titulos.append(s)
    return "secoes", titulos


def _copiar_se_existir_transcribrothers(origem: Path, destino: Path) -> bool:
    if not origem.is_file():
        return False
    destino.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(origem, destino)
    return True


def _gerar_thumbnail_jpg_do_mp4_transcribrothers(caminho_mp4: Path, caminho_jpg: Path) -> bool:
    if not caminho_mp4.is_file():
        return False
    ffmpeg = resolver_caminho_ffmpeg_transcribrothers()
    if not ffmpeg:
        return False
    caminho_jpg.parent.mkdir(parents=True, exist_ok=True)
    try:
        proc = subprocess.run(
            [
                ffmpeg,
                "-y",
                "-ss",
                "0.5",
                "-i",
                str(caminho_mp4),
                "-frames:v",
                "1",
                "-q:v",
                "4",
                str(caminho_jpg),
            ],
            capture_output=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return proc.returncode == 0 and caminho_jpg.is_file() and caminho_jpg.stat().st_size > 0


def criar_snapshot_versao_video_narrado_apos_sucesso_transcribrothers(
    *,
    work: Path,
    assets: Path,
    steps: dict[str, Any] | None,
    origem: str,
) -> ResultadoSnapshotVersaoVideoNarradoTranscribrothers:
    """
    Copia o conjunto de trabalho atual para ``videos_narrados/vNNNN`` e marca como atual.
    Exige o MP4 canônico no work.
    """
    mp4 = work / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS
    if not mp4.is_file() or mp4.stat().st_size < 100:
        raise ErroVersaoVideoNarradoTranscribrothers(
            "MP4 do vídeo narrado não encontrado para criar snapshot."
        )

    manifesto = _carregar_manifesto_bruto_transcribrothers(work)
    versao_id = _proximo_id_versao_transcribrothers(manifesto)
    while caminho_pasta_versao_video_narrado_transcribrothers(work, versao_id).exists():
        n = int(versao_id[1:]) + 1
        versao_id = f"v{n:04d}"

    destino = caminho_pasta_versao_video_narrado_transcribrothers(work, versao_id)
    destino.mkdir(parents=True, exist_ok=True)

    _copiar_se_existir_transcribrothers(mp4, destino / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS)
    _copiar_se_existir_transcribrothers(
        assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
        destino / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
    )
    _copiar_se_existir_transcribrothers(
        assets / NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS,
        destino / NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS,
    )
    _copiar_se_existir_transcribrothers(
        work / NOME_ARQUIVO_MANIFEST_CUES_NARRACAO_JANELAS_VIDEO_TRANSCRIBROTHERS,
        destino / NOME_ARQUIVO_MANIFEST_CUES_NARRACAO_JANELAS_VIDEO_TRANSCRIBROTHERS,
    )
    dir_wavs = work / nome_subpasta_wavs_narracao_por_cue_transcribrothers()
    if dir_wavs.is_dir():
        destino_wavs = destino / nome_subpasta_wavs_narracao_por_cue_transcribrothers()
        if destino_wavs.exists():
            shutil.rmtree(destino_wavs)
        shutil.copytree(dir_wavs, destino_wavs)

    thumb = destino / NOME_ARQUIVO_THUMBNAIL_VERSAO_VIDEO_NARRADO_TRANSCRIBROTHERS
    tem_thumb = _gerar_thumbnail_jpg_do_mp4_transcribrothers(mp4, thumb)

    try:
        duracao = float(_obter_duracao_video_segundos_via_ffprobe_sync(mp4) or 0.0)
    except Exception:  # noqa: BLE001
        duracao = 0.0

    escopo_modo, escopo_titulos = _escopo_de_steps_transcribrothers(steps)
    voz = ""
    if steps:
        voz = str(steps.get("pipeline_video_narrado_voz_tts") or "").strip()

    meta = MetaVersaoVideoNarradoTranscribrothers(
        id=versao_id,
        criado_em=datetime.now(timezone.utc).isoformat(),
        origem=(origem or "pipeline").strip() or "pipeline",
        escopo_modo=escopo_modo,
        escopo_titulos=escopo_titulos,
        voz_tts=voz,
        duracao_segundos=max(0.0, duracao),
        tem_thumbnail=tem_thumb,
    )
    (destino / NOME_ARQUIVO_META_VERSAO_VIDEO_NARRADO_TRANSCRIBROTHERS).write_text(
        json.dumps(meta.para_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    resumos = list(manifesto.get("versoes") or [])
    resumos.append(
        {
            "id": meta.id,
            "criado_em": meta.criado_em,
            "origem": meta.origem,
            "escopo_modo": meta.escopo_modo,
            "escopo_titulos": meta.escopo_titulos,
            "voz_tts": meta.voz_tts,
            "duracao_segundos": meta.duracao_segundos,
            "tem_thumbnail": meta.tem_thumbnail,
        }
    )
    manifesto["versoes"] = resumos
    manifesto["versao_atual_id"] = meta.id
    _gravar_manifesto_bruto_transcribrothers(work, manifesto)
    return ResultadoSnapshotVersaoVideoNarradoTranscribrothers(meta=meta, caminho_pasta=destino)


def listar_versoes_video_narrado_do_work_transcribrothers(
    work: Path,
) -> tuple[str | None, list[MetaVersaoVideoNarradoTranscribrothers]]:
    manifesto = _carregar_manifesto_bruto_transcribrothers(work)
    atual = manifesto.get("versao_atual_id")
    atual_s = str(atual).strip() if atual else None
    saida: list[MetaVersaoVideoNarradoTranscribrothers] = []
    for item in manifesto.get("versoes") or []:
        if not isinstance(item, dict):
            continue
        vid = str(item.get("id") or "").strip()
        if not _RE_ID_VERSAO.match(vid):
            continue
        pasta = caminho_pasta_versao_video_narrado_transcribrothers(work, vid)
        meta_path = pasta / NOME_ARQUIVO_META_VERSAO_VIDEO_NARRADO_TRANSCRIBROTHERS
        dados = dict(item)
        if meta_path.is_file():
            try:
                carregado = json.loads(meta_path.read_text(encoding="utf-8"))
                if isinstance(carregado, dict):
                    dados.update(carregado)
            except (OSError, json.JSONDecodeError):
                pass
        titulos = dados.get("escopo_titulos")
        if not isinstance(titulos, list):
            titulos = []
        saida.append(
            MetaVersaoVideoNarradoTranscribrothers(
                id=vid,
                criado_em=str(dados.get("criado_em") or ""),
                origem=str(dados.get("origem") or ""),
                escopo_modo=str(dados.get("escopo_modo") or "documento"),
                escopo_titulos=[str(t).strip() for t in titulos if str(t).strip()],
                voz_tts=str(dados.get("voz_tts") or ""),
                duracao_segundos=float(dados.get("duracao_segundos") or 0.0),
                tem_thumbnail=bool(
                    dados.get("tem_thumbnail")
                    or (pasta / NOME_ARQUIVO_THUMBNAIL_VERSAO_VIDEO_NARRADO_TRANSCRIBROTHERS).is_file()
                ),
            )
        )
    saida.sort(key=lambda m: m.criado_em, reverse=True)
    return atual_s, saida


def resolver_arquivo_versao_video_narrado_transcribrothers(
    work: Path,
    versao_id: str,
    nome_arquivo: str,
) -> Path:
    permitidos = {
        NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS,
        NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
        NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS,
        NOME_ARQUIVO_THUMBNAIL_VERSAO_VIDEO_NARRADO_TRANSCRIBROTHERS,
        NOME_ARQUIVO_MANIFEST_CUES_NARRACAO_JANELAS_VIDEO_TRANSCRIBROTHERS,
        NOME_ARQUIVO_META_VERSAO_VIDEO_NARRADO_TRANSCRIBROTHERS,
    }
    nome = Path(nome_arquivo).name
    if nome not in permitidos:
        raise ErroVersaoVideoNarradoTranscribrothers(f"Arquivo não permitido: {nome}.")
    caminho = caminho_pasta_versao_video_narrado_transcribrothers(work, versao_id) / nome
    if not caminho.is_file():
        raise ErroVersaoVideoNarradoTranscribrothers(f"Arquivo não encontrado na versão {versao_id}.")
    return caminho


def tornar_versao_video_narrado_atual_transcribrothers(
    *,
    work: Path,
    assets: Path,
    job_id: str,
    versao_id: str,
    steps: dict[str, Any],
) -> dict[str, Any]:
    """Restaura snapshot para work/assets e atualiza URLs em steps_json. Retorna steps atualizado."""
    pasta = caminho_pasta_versao_video_narrado_transcribrothers(work, versao_id)
    mp4_src = pasta / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS
    if not mp4_src.is_file():
        raise ErroVersaoVideoNarradoTranscribrothers(
            f"Versão {versao_id} sem MP4; não é possível tornar atual."
        )

    assets.mkdir(parents=True, exist_ok=True)
    shutil.copy2(mp4_src, work / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS)

    vtt_src = pasta / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS
    if vtt_src.is_file():
        shutil.copy2(vtt_src, assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS)

    wav_src = pasta / NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS
    if wav_src.is_file():
        shutil.copy2(wav_src, assets / NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS)

    man_src = pasta / NOME_ARQUIVO_MANIFEST_CUES_NARRACAO_JANELAS_VIDEO_TRANSCRIBROTHERS
    if man_src.is_file():
        shutil.copy2(man_src, work / NOME_ARQUIVO_MANIFEST_CUES_NARRACAO_JANELAS_VIDEO_TRANSCRIBROTHERS)

    wavs_src = pasta / nome_subpasta_wavs_narracao_por_cue_transcribrothers()
    wavs_dst = work / nome_subpasta_wavs_narracao_por_cue_transcribrothers()
    if wavs_src.is_dir():
        if wavs_dst.exists():
            shutil.rmtree(wavs_dst)
        shutil.copytree(wavs_src, wavs_dst)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    url_mp4 = f"/api/jobs/{job_id}/video-com-narracao-tts?v={stamp}"
    steps_novo = dict(steps)
    steps_novo[CHAVE_STEPS_JSON_VIDEO_COM_NARRACAO_TTS_TRANSCRIBROTHERS] = {
        **dict(steps_novo.get(CHAVE_STEPS_JSON_VIDEO_COM_NARRACAO_TTS_TRANSCRIBROTHERS) or {}),
        "nome_arquivo": NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS,
        "url_download": url_mp4,
        "restaurado_de_versao": versao_id,
        "gerado_em": datetime.now(timezone.utc).isoformat(),
    }
    from transcribrothers_backend.modulo_salvar_estado_editor_video_narrado_edicoes_modal_sem_gerar_mp4_transcribrothers import (
        marcar_audio_mp4_sincronizado_com_projeto_editor_apos_remux_transcribrothers,
    )

    marcar_audio_mp4_sincronizado_com_projeto_editor_apos_remux_transcribrothers(steps_novo)
    if vtt_src.is_file():
        url_vtt = (
            f"/api/jobs/{job_id}/assets/{NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS}"
            f"?v={stamp}"
        )
        steps_novo[CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS] = {
            **dict(steps_novo.get(CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS) or {}),
            "nome_arquivo": NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
            "url_asset": url_vtt,
        }
        # Mantém o resumo do pipeline alinhado ao VTT restaurado (a UI pode ler url_asset_vtt daqui).
        pipe_raw = steps_novo.get("pipeline_video_narrado_documento")
        if isinstance(pipe_raw, dict):
            steps_novo["pipeline_video_narrado_documento"] = {
                **pipe_raw,
                "url_asset_vtt": url_vtt,
                "nome_arquivo_vtt": NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
            }
    if wav_src.is_file():
        url_wav = (
            f"/api/jobs/{job_id}/assets/{NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS}"
            f"?v={stamp}"
        )
        steps_novo[CHAVE_STEPS_JSON_NARRACAO_TTS_TRANSCRIBROTHERS] = {
            **dict(steps_novo.get(CHAVE_STEPS_JSON_NARRACAO_TTS_TRANSCRIBROTHERS) or {}),
            "nome_arquivo": NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS,
            "url_asset": url_wav,
        }

    manifesto = _carregar_manifesto_bruto_transcribrothers(work)
    ids = {str(v.get("id") or "") for v in (manifesto.get("versoes") or []) if isinstance(v, dict)}
    if versao_id not in ids:
        raise ErroVersaoVideoNarradoTranscribrothers(f"Versão {versao_id} não está no manifesto.")
    manifesto["versao_atual_id"] = versao_id
    _gravar_manifesto_bruto_transcribrothers(work, manifesto)
    return steps_novo


@dataclass(frozen=True)
class ResultadoApagarVersaoVideoNarradoTranscribrothers:
    steps: dict[str, Any]
    steps_alterados: bool
    versao_atual_id: str | None


def _remover_pasta_e_entrada_manifesto_versao_transcribrothers(
    *,
    work: Path,
    versao_id: str,
    manifesto: dict[str, Any],
) -> dict[str, Any]:
    pasta = caminho_pasta_versao_video_narrado_transcribrothers(work, versao_id)
    if pasta.is_dir():
        shutil.rmtree(pasta)
    manifesto = dict(manifesto)
    manifesto["versoes"] = [
        v
        for v in (manifesto.get("versoes") or [])
        if isinstance(v, dict) and str(v.get("id") or "") != versao_id
    ]
    return manifesto


def _limpar_artefatos_working_set_video_narrado_transcribrothers(*, work: Path, assets: Path) -> None:
    for caminho in (
        work / NOME_ARQUIVO_VIDEO_COM_NARRACAO_TTS_MP4_TRANSCRIBROTHERS,
        work / NOME_ARQUIVO_MANIFEST_CUES_NARRACAO_JANELAS_VIDEO_TRANSCRIBROTHERS,
        assets / NOME_ARQUIVO_LEGENDAS_DOCUMENTO_ALINHADAS_VTT_TRANSCRIBROTHERS,
        assets / NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS,
    ):
        try:
            if caminho.is_file():
                caminho.unlink()
        except OSError:
            pass
    wavs = work / nome_subpasta_wavs_narracao_por_cue_transcribrothers()
    if wavs.is_dir():
        shutil.rmtree(wavs, ignore_errors=True)


def _limpar_steps_video_narrado_transcribrothers(steps: dict[str, Any]) -> dict[str, Any]:
    from transcribrothers_backend.modulo_pipeline_video_narrado_a_partir_documento_markdown_job_transcribrothers import (
        CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS,
    )

    steps_novo = dict(steps)
    for chave in (
        CHAVE_STEPS_JSON_VIDEO_COM_NARRACAO_TTS_TRANSCRIBROTHERS,
        CHAVE_STEPS_JSON_LEGENDAS_DOCUMENTO_ALINHADAS_TRANSCRIBROTHERS,
        CHAVE_STEPS_JSON_NARRACAO_TTS_TRANSCRIBROTHERS,
        CHAVE_STEPS_JSON_PIPELINE_VIDEO_NARRADO_DOCUMENTO_TRANSCRIBROTHERS,
    ):
        steps_novo.pop(chave, None)
    return steps_novo


def apagar_versao_video_narrado_transcribrothers(
    *,
    work: Path,
    assets: Path,
    job_id: str,
    versao_id: str,
    steps: dict[str, Any],
) -> ResultadoApagarVersaoVideoNarradoTranscribrothers:
    """
    Apaga uma versão. Se for a atual e houver outras, promove a mais recente restante.
    Se for a única, limpa o working set e as chaves de vídeo narrado em steps.
    """
    manifesto = _carregar_manifesto_bruto_transcribrothers(work)
    ids = {
        str(v.get("id") or "").strip()
        for v in (manifesto.get("versoes") or [])
        if isinstance(v, dict) and str(v.get("id") or "").strip()
    }
    if versao_id not in ids:
        raise ErroVersaoVideoNarradoTranscribrothers(f"Versão {versao_id} não encontrada.")

    atual = str(manifesto.get("versao_atual_id") or "").strip()
    steps_base = dict(steps)

    if versao_id != atual:
        manifesto = _remover_pasta_e_entrada_manifesto_versao_transcribrothers(
            work=work,
            versao_id=versao_id,
            manifesto=manifesto,
        )
        _gravar_manifesto_bruto_transcribrothers(work, manifesto)
        return ResultadoApagarVersaoVideoNarradoTranscribrothers(
            steps=steps_base,
            steps_alterados=False,
            versao_atual_id=atual or None,
        )

    # Versão atual: promove outra ou limpa tudo.
    restantes = [
        v
        for v in (manifesto.get("versoes") or [])
        if isinstance(v, dict) and str(v.get("id") or "").strip() not in ("", versao_id)
    ]
    if restantes:
        restantes.sort(key=lambda v: str(v.get("criado_em") or ""), reverse=True)
        proxima = str(restantes[0].get("id") or "").strip()
        if not proxima:
            raise ErroVersaoVideoNarradoTranscribrothers("Não foi possível promover outra versão.")
        steps_novo = tornar_versao_video_narrado_atual_transcribrothers(
            work=work,
            assets=assets,
            job_id=job_id,
            versao_id=proxima,
            steps=steps_base,
        )
        manifesto2 = _carregar_manifesto_bruto_transcribrothers(work)
        manifesto2 = _remover_pasta_e_entrada_manifesto_versao_transcribrothers(
            work=work,
            versao_id=versao_id,
            manifesto=manifesto2,
        )
        manifesto2["versao_atual_id"] = proxima
        _gravar_manifesto_bruto_transcribrothers(work, manifesto2)
        return ResultadoApagarVersaoVideoNarradoTranscribrothers(
            steps=steps_novo,
            steps_alterados=True,
            versao_atual_id=proxima,
        )

    manifesto = _remover_pasta_e_entrada_manifesto_versao_transcribrothers(
        work=work,
        versao_id=versao_id,
        manifesto=manifesto,
    )
    manifesto["versao_atual_id"] = None
    manifesto["versoes"] = []
    _gravar_manifesto_bruto_transcribrothers(work, manifesto)
    _limpar_artefatos_working_set_video_narrado_transcribrothers(work=work, assets=assets)
    steps_limpo = _limpar_steps_video_narrado_transcribrothers(steps_base)
    return ResultadoApagarVersaoVideoNarradoTranscribrothers(
        steps=steps_limpo,
        steps_alterados=True,
        versao_atual_id=None,
    )


def tentar_criar_snapshot_versao_video_narrado_apos_sucesso_silencioso_transcribrothers(
    *,
    work: Path,
    assets: Path,
    steps: dict[str, Any] | None,
    origem: str,
) -> str | None:
    """Wrapper que não quebra o pipeline se o snapshot falhar; devolve o id ou None."""
    try:
        r = criar_snapshot_versao_video_narrado_apos_sucesso_transcribrothers(
            work=work,
            assets=assets,
            steps=steps,
            origem=origem,
        )
        return r.meta.id
    except Exception:  # noqa: BLE001 — não derruba geração por falha de arquivo
        return None
