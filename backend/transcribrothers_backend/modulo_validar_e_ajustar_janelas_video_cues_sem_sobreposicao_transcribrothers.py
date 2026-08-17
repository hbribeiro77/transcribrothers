"""Valida janelas de vídeo por cue: início < fim e sem sobreposição entre vizinhas da mesma origem."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

_FOLGA_MINIMA_ENTRE_CUES_SEGUNDOS = 0.05
_DURACAO_MINIMA_JANELA_SEGUNDOS = 0.05
_NOME_SUBPASTA_WAVS_POR_CUE = "wavs_narracao_por_cue"


@dataclass(frozen=True)
class JanelaVideoCueEntradaTranscribrothers:
    inicio_video_segundos: float
    fim_video_segundos: float


class ErroValidacaoJanelasVideoCuesTranscribrothers(ValueError):
    """Janelas inválidas ou sobrepostas."""


def validar_janelas_video_cues_sem_sobreposicao_transcribrothers(
    janelas: list[JanelaVideoCueEntradaTranscribrothers],
    *,
    duracao_video_segundos: float | None = None,
    duracoes_video_por_indice: list[float | None] | None = None,
    ids_fonte_video: list[str] | None = None,
    folga_minima_segundos: float = _FOLGA_MINIMA_ENTRE_CUES_SEGUNDOS,
) -> None:
    if not janelas:
        raise ErroValidacaoJanelasVideoCuesTranscribrothers("Informe ao menos uma janela de vídeo.")
    folga = max(0.0, float(folga_minima_segundos))
    dur_global = None if duracao_video_segundos is None else max(0.0, float(duracao_video_segundos))
    if duracoes_video_por_indice is not None and len(duracoes_video_por_indice) != len(janelas):
        raise ErroValidacaoJanelasVideoCuesTranscribrothers(
            "Lista de durações por índice não bate com a quantidade de janelas."
        )
    if ids_fonte_video is not None and len(ids_fonte_video) != len(janelas):
        raise ErroValidacaoJanelasVideoCuesTranscribrothers(
            "Lista de ids de fonte não bate com a quantidade de janelas."
        )

    def _dur_indice(i: int) -> float | None:
        if duracoes_video_por_indice is not None:
            d = duracoes_video_por_indice[i]
            if d is None:
                return dur_global
            return max(0.0, float(d))
        return dur_global

    def _id_fonte(i: int) -> str:
        if ids_fonte_video is None:
            return ""
        return str(ids_fonte_video[i] or "").strip()

    for i, j in enumerate(janelas):
        ini = float(j.inicio_video_segundos)
        fim = float(j.fim_video_segundos)
        if ini < 0 or fim < 0:
            raise ErroValidacaoJanelasVideoCuesTranscribrothers(
                f"Cue {i + 1}: tempos da janela de vídeo não podem ser negativos."
            )
        if fim + 1e-9 < ini + _DURACAO_MINIMA_JANELA_SEGUNDOS:
            raise ErroValidacaoJanelasVideoCuesTranscribrothers(
                f"Cue {i + 1}: o fim da janela deve ser maior que o início "
                f"(mínimo {_DURACAO_MINIMA_JANELA_SEGUNDOS:.2f}s)."
            )
        dur = _dur_indice(i)
        if dur is not None and ini > dur + 1e-6:
            raise ErroValidacaoJanelasVideoCuesTranscribrothers(
                f"Cue {i + 1}: início ({ini:.3f}s) ultrapassa a duração do vídeo ({dur:.3f}s)."
            )
        if dur is not None and fim > dur + 0.25:
            raise ErroValidacaoJanelasVideoCuesTranscribrothers(
                f"Cue {i + 1}: fim ({fim:.3f}s) ultrapassa demais a duração do vídeo ({dur:.3f}s)."
            )
        if i > 0:
            id_atual = _id_fonte(i)
            # Com ids de fonte: só compara com a vizinha anterior da mesma origem.
            if ids_fonte_video is not None:
                prev_idx = None
                for k in range(i - 1, -1, -1):
                    if _id_fonte(k) == id_atual:
                        prev_idx = k
                        break
                if prev_idx is None:
                    continue
                prev = janelas[prev_idx]
                limite = float(prev.fim_video_segundos) + folga
                if ini + 1e-9 < limite:
                    raise ErroValidacaoJanelasVideoCuesTranscribrothers(
                        f"Cue {i + 1} sobrepõe a cue {prev_idx + 1}: início {ini:.3f}s < "
                        f"fim da anterior na mesma origem {prev.fim_video_segundos:.3f}s "
                        f"(folga mínima {folga:.2f}s)."
                    )
            else:
                prev = janelas[i - 1]
                limite = float(prev.fim_video_segundos) + folga
                if ini + 1e-9 < limite:
                    raise ErroValidacaoJanelasVideoCuesTranscribrothers(
                        f"Cue {i + 1} sobrepõe a cue {i}: início {ini:.3f}s < "
                        f"fim da anterior {prev.fim_video_segundos:.3f}s "
                        f"(folga mínima {folga:.2f}s)."
                    )


def nome_subpasta_wavs_narracao_por_cue_transcribrothers() -> str:
    return _NOME_SUBPASTA_WAVS_POR_CUE


def resolver_caminho_wav_narracao_por_indice_cue_transcribrothers(
    diretorio_wavs: Path,
    indice_zero_based: int,
) -> Path:
    if indice_zero_based < 0:
        raise ValueError("Índice de cue inválido.")
    return diretorio_wavs / f"cue_narracao_{indice_zero_based:04d}.wav"


def listar_indices_wavs_narracao_por_cue_disponiveis_transcribrothers(
    diretorio_wavs: Path,
) -> list[int]:
    if not diretorio_wavs.is_dir():
        return []
    indices: list[int] = []
    for p in sorted(diretorio_wavs.glob("cue_narracao_*.wav")):
        stem = p.stem  # cue_narracao_0003
        try:
            idx = int(stem.rsplit("_", 1)[-1])
        except ValueError:
            continue
        if idx >= 0 and p.is_file() and p.stat().st_size > 44:
            indices.append(idx)
    return indices
