"""Geração LiteLLM de roteiro Markdown para reproduzir bug (RecBrothers + cliques + frames)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from transcribrothers_backend.constante_texto_instrucao_reproducao_bug_sem_json_cliques_transcribrothers import (
    TEXTO_INSTRUCAO_REPRODUCAO_BUG_SEM_JSON_CLIQUES_TRANSCRIBROTHERS,
)
from transcribrothers_backend.constante_texto_instrucao_regeneracao_reproducao_bug_sem_video_transcribrothers import (
    TEXTO_INSTRUCAO_REGENERACAO_REPRODUCAO_BUG_SEM_VIDEO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_cliente_litellm_geracao_tutorial_markdown import (
    gerar_tutorial_markdown_com_litellm_a_partir_de_transcricao_e_frames,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
)

INSTRUCAO_LITELLM_REPRODUCAO_BUG_RECBROTHERS_TRANSCRIBROTHERS = """Você é um analista de QA/documentação técnica. Você recebe:
(1) JSON com eventos de clique registrados durante a gravação do bug (tempos relativos, URL da página, coordenadas normalizadas na viewport);
(2) transcrição do áudio do vídeo (pode estar vazia se a gravação não tinha áudio);
(3) lista `frames` com screenshots capturados no instante de cada clique (caminhos em assets/);
(4) as imagens PNG anexadas nesta mensagem, na mesma ordem de `frames`.

Objetivo: produzir um tutorial em Markdown para **outra pessoa reproduzir o bug**, passo a passo.

Regras obrigatórias:
1) Título H1 curto descrevendo o problema reproduzido (não use "Tutorial de produto").
2) Seção inicial breve: contexto (URL inicial se houver), duração aproximada, pré-requisitos se mencionados na transcrição.
3) Um passo numerado por clique relevante em `cliques`, na ordem temporal. Não invente cliques que não estão no JSON.
4) Em cada passo: descreva a ação (clique, navegação), cite a URL quando mudar, use [MM:SS](?t=SEGUNDOS) com SEGUNDOS = tRelativoMs/1000.
5) Incorpore a imagem do passo com `![](caminho_exato)` usando frames[].arquivo_relativo_markdown correspondente ao clique.
6) Use a transcrição apenas como complemento (o que o gravador disse naquele momento); não contradiga os cliques.
7) Se não houver áudio/transcrição, baseie-se só nos cliques e nas imagens.
8) Finalize com seção "## Resultado observado" resumindo o comportamento incorreto se estiver explícito na transcrição ou nas telas; senão indique que o gravador deve descrever o bug.
9) Markdown normal, sem envolver tudo em um único bloco de código.

JSON de entrada:
"""


def montar_instrucao_prefixo_litellm_reproducao_bug_transcribrothers(
    *,
    documento_autonomo_sem_video: bool = False,
    sem_json_cliques_recbrothers: bool = False,
    instrucoes_revisao_humana: str | None = None,
) -> str:
    partes = [INSTRUCAO_LITELLM_REPRODUCAO_BUG_RECBROTHERS_TRANSCRIBROTHERS]
    if sem_json_cliques_recbrothers:
        partes.append(TEXTO_INSTRUCAO_REPRODUCAO_BUG_SEM_JSON_CLIQUES_TRANSCRIBROTHERS)
    if documento_autonomo_sem_video:
        partes.append(TEXTO_INSTRUCAO_REGENERACAO_REPRODUCAO_BUG_SEM_VIDEO_TRANSCRIBROTHERS)
    rev = (instrucoes_revisao_humana or "").strip()
    if rev:
        partes.append(f"Instruções adicionais do revisor humano:\n{rev}")
    return "\n\n".join(partes)


async def gerar_markdown_reproducao_bug_recbrothers_com_litellm_transcribrothers(
    *,
    cliques: list[dict[str, Any]],
    transcricao: ResultadoTranscricaoComSegmentos,
    caminhos_frames_rel_job: list[tuple[float, str]],
    modelo: str,
    api_key: str | None,
    api_base: str | None,
    httpx_verify: bool | str = True,
    httpx_timeout_connect_segundos: float = 120.0,
    httpx_timeout_read_segundos: float = 7200.0,
    diretorio_assets_absoluto: Path,
    steps_para_log_decisoes_ia: dict[str, Any] | None = None,
    instrucoes_revisao_humana: str | None = None,
    markdown_atual_para_contexto: str | None = None,
    documento_autonomo_sem_video: bool = False,
    sem_json_cliques_recbrothers: bool = False,
    log_etapa_geracao_tutorial: str = "geracao_reproducao_bug_markdown",
) -> str:
    segmentos_serializados = [
        {
            "inicio_segundos": s.inicio_segundos,
            "fim_segundos": s.fim_segundos,
            "texto": s.texto,
        }
        for s in transcricao.segmentos
    ]
    payload_cliques = {
        "cliques": cliques,
        "transcricao": {
            "texto_completo": transcricao.texto_completo,
            "idioma": transcricao.idioma_detectado,
            "segmentos": segmentos_serializados,
        },
        "frames": [
            {"t_segundos": t, "arquivo_relativo_markdown": rel}
            for t, rel in caminhos_frames_rel_job
        ],
    }

    prefixo = montar_instrucao_prefixo_litellm_reproducao_bug_transcribrothers(
        documento_autonomo_sem_video=documento_autonomo_sem_video,
        sem_json_cliques_recbrothers=sem_json_cliques_recbrothers,
        instrucoes_revisao_humana=instrucoes_revisao_humana,
    )

    return await gerar_tutorial_markdown_com_litellm_a_partir_de_transcricao_e_frames(
        transcricao=transcricao,
        caminhos_frames_rel_job=caminhos_frames_rel_job,
        modelo=modelo,
        api_key=api_key,
        api_base=api_base,
        httpx_verify=httpx_verify,
        httpx_timeout_connect_segundos=httpx_timeout_connect_segundos,
        httpx_timeout_read_segundos=httpx_timeout_read_segundos,
        diretorio_assets_absoluto=diretorio_assets_absoluto,
        enviar_screenshots_png_como_imagens_multimodais=bool(caminhos_frames_rel_job),
        rels_png_anexo_ja_resolvidos=list(caminhos_frames_rel_job),
        instrucao_prefixo_litellm_custom=prefixo,
        payload_json_substituto=payload_cliques,
        instrucoes_revisao_humana=instrucoes_revisao_humana,
        bloco_markdown_tutorial_atual_para_contexto_em_revisao=markdown_atual_para_contexto,
        steps_para_log_decisoes_ia=steps_para_log_decisoes_ia,
        log_etapa_geracao_tutorial=log_etapa_geracao_tutorial,
    )
