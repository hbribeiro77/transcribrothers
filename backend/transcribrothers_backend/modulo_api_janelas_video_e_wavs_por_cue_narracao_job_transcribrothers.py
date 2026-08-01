"""Leitura/gravação de janelas de vídeo do manifesto e localização de WAVs por cue."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from transcribrothers_backend.modulo_montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers import (
    CueNarracaoComJanelaVideoTranscribrothers,
)
from transcribrothers_backend.modulo_persistencia_manifest_cues_narracao_janelas_video_job_transcribrothers import (
    ItemManifestCueNarracaoJanelaVideoTranscribrothers,
    carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers,
    cues_janela_a_partir_manifest_transcribrothers,
    gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers,
)
from transcribrothers_backend.modulo_validar_e_ajustar_janelas_video_cues_sem_sobreposicao_transcribrothers import (
    ErroValidacaoJanelasVideoCuesTranscribrothers,
    JanelaVideoCueEntradaTranscribrothers,
    listar_indices_wavs_narracao_por_cue_disponiveis_transcribrothers,
    nome_subpasta_wavs_narracao_por_cue_transcribrothers,
    resolver_caminho_wav_narracao_por_indice_cue_transcribrothers,
    validar_janelas_video_cues_sem_sobreposicao_transcribrothers,
)


@dataclass(frozen=True)
class ResumoJanelaVideoCueApiTranscribrothers:
    indice: int
    texto: str
    inicio_video_segundos: float
    fim_video_segundos: float
    tem_wav: bool
    url_wav: str | None
    sem_narracao: bool = False
    voz_tts: str = ""
    texto_tts: str = ""


def diretorio_wavs_narracao_por_cue_do_work_transcribrothers(work: Path) -> Path:
    return work / nome_subpasta_wavs_narracao_por_cue_transcribrothers()


def montar_resumo_janelas_video_e_wavs_do_job_transcribrothers(
    *,
    job_id: str,
    work: Path,
) -> list[ResumoJanelaVideoCueApiTranscribrothers]:
    manifest = carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers(work)
    if not manifest:
        return []
    dir_wavs = diretorio_wavs_narracao_por_cue_do_work_transcribrothers(work)
    indices_wav = set(listar_indices_wavs_narracao_por_cue_disponiveis_transcribrothers(dir_wavs))
    saida: list[ResumoJanelaVideoCueApiTranscribrothers] = []
    for i, item in enumerate(manifest):
        tem = i in indices_wav
        saida.append(
            ResumoJanelaVideoCueApiTranscribrothers(
                indice=i,
                texto=item.texto,
                inicio_video_segundos=item.inicio_video_segundos,
                fim_video_segundos=item.fim_video_segundos,
                tem_wav=tem,
                url_wav=(f"/api/jobs/{job_id}/wavs-narracao-por-cue/{i}" if tem else None),
                sem_narracao=bool(item.sem_narracao),
                voz_tts=str(getattr(item, "voz_tts", "") or "").strip(),
                texto_tts=str(getattr(item, "texto_tts", "") or "").strip(),
            )
        )
    return saida


def salvar_janelas_video_no_manifest_validando_sobreposicao_transcribrothers(
    *,
    work: Path,
    janelas_brutas: list[dict[str, Any]],
    duracao_video_segundos: float | None = None,
) -> list[ItemManifestCueNarracaoJanelaVideoTranscribrothers]:
    manifest = carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers(work)
    if not manifest:
        raise ErroValidacaoJanelasVideoCuesTranscribrothers(
            "Manifesto de janelas não encontrado. Gere o vídeo narrado antes de editar tempos."
        )
    if len(janelas_brutas) != len(manifest):
        raise ErroValidacaoJanelasVideoCuesTranscribrothers(
            "Quantidade de janelas enviada não bate com o manifesto "
            f"({len(janelas_brutas)} != {len(manifest)})."
        )
    janelas: list[JanelaVideoCueEntradaTranscribrothers] = []
    for i, raw in enumerate(janelas_brutas):
        try:
            ini = float(raw["inicio_video_segundos"])
            fim = float(raw["fim_video_segundos"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ErroValidacaoJanelasVideoCuesTranscribrothers(
                f"Cue {i + 1}: tempos de janela inválidos."
            ) from exc
        janelas.append(JanelaVideoCueEntradaTranscribrothers(inicio_video_segundos=ini, fim_video_segundos=fim))

    validar_janelas_video_cues_sem_sobreposicao_transcribrothers(
        janelas,
        duracao_video_segundos=duracao_video_segundos,
    )

    cues_novas = [
        CueNarracaoComJanelaVideoTranscribrothers(
            texto=m.texto,
            inicio_video_segundos=j.inicio_video_segundos,
            fim_video_segundos=j.fim_video_segundos,
            origem_ancora=m.origem_ancora,
            casado=m.casado,
            sem_narracao=m.sem_narracao,
            voz_tts=m.voz_tts,
            texto_tts=m.texto_tts,
        )
        for m, j in zip(manifest, janelas, strict=True)
    ]
    gravar_manifest_cues_narracao_janelas_video_no_work_transcribrothers(work=work, cues=cues_novas)
    return [
        ItemManifestCueNarracaoJanelaVideoTranscribrothers(
            texto=c.texto,
            inicio_video_segundos=c.inicio_video_segundos,
            fim_video_segundos=c.fim_video_segundos,
            origem_ancora=c.origem_ancora,
            casado=c.casado,
            sem_narracao=c.sem_narracao,
            voz_tts=c.voz_tts,
            texto_tts=c.texto_tts,
        )
        for c in cues_novas
    ]


def obter_caminho_wav_narracao_por_cue_se_existir_transcribrothers(
    work: Path,
    indice_zero_based: int,
) -> Path | None:
    dir_wavs = diretorio_wavs_narracao_por_cue_do_work_transcribrothers(work)
    caminho = resolver_caminho_wav_narracao_por_indice_cue_transcribrothers(dir_wavs, indice_zero_based)
    if caminho.is_file() and caminho.stat().st_size > 44:
        return caminho
    return None


def cues_janela_do_manifest_ou_erro_transcribrothers(
    work: Path,
) -> list[CueNarracaoComJanelaVideoTranscribrothers]:
    manifest = carregar_manifest_cues_narracao_janelas_video_do_work_transcribrothers(work)
    if not manifest:
        raise ValueError("Manifesto de janelas não encontrado.")
    return cues_janela_a_partir_manifest_transcribrothers(manifest)
