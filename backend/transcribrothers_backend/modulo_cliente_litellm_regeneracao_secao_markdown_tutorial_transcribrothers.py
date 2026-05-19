from __future__ import annotations

import asyncio
import base64
import json
import re
from pathlib import Path
from typing import Any

import httpx

from transcribrothers_backend.modulo_cliente_litellm_geracao_tutorial_markdown import (
    _ler_bytes_pngs_assets_em_ordem_dos_rels_sync_transcribrothers,
    _serializar_segmentos,
    extrair_texto_resposta_message_openai_compat_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
)
from transcribrothers_backend.modulo_util_escopo_trecho_edicao_secao_markdown_tutorial_transcribrothers import (
    FatiaEscopoEdicaoSecaoMarkdownTutorialTranscribrothers,
    ModoEscopoEdicaoSecaoMarkdownTutorialTranscribrothers,
)
from transcribrothers_backend.modulo_util_extrair_caminhos_assets_png_referenciados_no_markdown_tutorial_transcribrothers import (
    extrair_timestamps_segundos_do_markdown_para_frames_edicao_secao_transcribrothers,
    montar_rels_png_visao_e_catalogo_frames_edicao_secao_markdown_transcribrothers,
)

_RE_LINK_TEMPO_MARKDOWN_TRANSCRIBROTHERS = re.compile(r"\?t=(\d+(?:\.\d+)?)")

SYSTEM_PROMPT_REGENERACAO_ZONA_ESCOPO_SECAO_MARKDOWN_TUTORIAL_TRANSCRIBROTHERS = """\
Você é um editor técnico. Reescreve APENAS a zona editável indicada de uma seção de tutorial em Markdown.

Regras obrigatórias:
1) Responda somente com o Markdown da zona editável — não inclua o prefixo nem o sufixo marcados como somente leitura.
2) Não adicione nem altere o heading «## » da seção inteira — a linha «## Título» da seção já está fora da zona e não deve aparecer na resposta.
3) Pode usar «###», listas e parágrafos dentro da zona.
4) Mantenha imagens existentes com os mesmos caminhos `![](assets/….png)` quando ainda fizerem sentido.
5) Para screenshot novo: copie o valor literal de `arquivo_relativo_markdown` de `frames_extraidos_disponiveis` — nunca invente nomes. O padrão real termina em `_indice_NNNN.png` (ex.: `assets/screenshot_tutorial_transcribrothers_frame_no_offset_ms_0000031700_indice_0004.png`). Proibido sufixos como `_exemplo_…` ou nomes que não estejam no catálogo.
6) As imagens anexadas seguem `frames_enviados_com_visao` (subconjunto com pixel).
7) Links temporais [MM:SS](?t=SEGUNDOS) só se o contexto suportar; use `t_segundos` do catálogo.
8) Não altere o significado factual fora do pedido do revisor.
9) Não envolva a resposta em blocos de código; só Markdown da zona.
"""

SYSTEM_PROMPT_REGENERACAO_SECAO_MARKDOWN_TUTORIAL_TRANSCRIBROTHERS = """\
Você é um editor técnico. Reescreve APENAS uma seção de um tutorial em Markdown.

Regras obrigatórias:
1) Responda somente com o Markdown da seção pedida — incluindo a linha de título que começa com «## » (mesmo texto do título original).
2) Não inclua o título H1 do documento, outras seções «## », prefácio nem rodapé.
3) Pode usar «###» e listas dentro da seção.
4) Mantenha imagens existentes com os mesmos caminhos `![](assets/….png)` quando ainda fizerem sentido.
5) Para screenshot novo: copie o valor literal de `arquivo_relativo_markdown` de `frames_extraidos_disponiveis` — nunca invente nomes. O padrão real termina em `_indice_NNNN.png` (ex.: `assets/screenshot_tutorial_transcribrothers_frame_no_offset_ms_0000031700_indice_0004.png`). Proibido sufixos como `_exemplo_…` ou nomes que não estejam no catálogo.
6) As imagens anexadas seguem `frames_enviados_com_visao` (subconjunto com pixel).
7) Links temporais [MM:SS](?t=SEGUNDOS) só se o contexto suportar; use `t_segundos` do catálogo.
8) Não envolva a resposta em blocos de código; só Markdown da seção.
"""


def extrair_timestamps_segundos_do_markdown_secao_transcribrothers(markdown_secao: str) -> list[float]:
    out: list[float] = []
    for m in _RE_LINK_TEMPO_MARKDOWN_TRANSCRIBROTHERS.finditer(markdown_secao or ""):
        try:
            out.append(float(m.group(1)))
        except ValueError:
            continue
    return out


def filtrar_segmentos_transcricao_proximos_a_timestamps_secao_transcribrothers(
    transcricao: ResultadoTranscricaoComSegmentos,
    timestamps_secundos: list[float],
    *,
    margem_segundos: float = 45.0,
) -> list:
    if not timestamps_secundos:
        return list(transcricao.segmentos)
    tmin = min(timestamps_secundos) - margem_segundos
    tmax = max(timestamps_secundos) + margem_segundos
    filtrados = [
        s
        for s in transcricao.segmentos
        if s.fim_segundos >= tmin and s.inicio_segundos <= tmax
    ]
    return filtrados if filtrados else list(transcricao.segmentos)


def _enriquecer_payload_json_com_frames_extraidos_edicao_secao_transcribrothers(
    payload_json: dict[str, object],
    *,
    markdown_tutorial_completo: str,
    markdown_escopo_edicao: str,
    instrucoes_revisor: str,
    rels_completos_snapshot: list[tuple[float, str]],
    timestamps_escopo_segundos: list[float] | None,
) -> list[tuple[float, str]]:
    rels_visao, catalogo = montar_rels_png_visao_e_catalogo_frames_edicao_secao_markdown_transcribrothers(
        markdown_tutorial_completo=markdown_tutorial_completo,
        markdown_escopo_edicao=markdown_escopo_edicao,
        instrucoes_revisor=instrucoes_revisor,
        rels_completos_com_tempos=rels_completos_snapshot,
        timestamps_escopo_segundos=timestamps_escopo_segundos,
    )
    if catalogo:
        payload_json["frames_extraidos_disponiveis"] = catalogo
    if rels_visao:
        payload_json["frames_enviados_com_visao"] = [
            {"t_segundos": t, "arquivo_relativo_markdown": rel} for t, rel in rels_visao
        ]
    return rels_visao


async def regenerar_markdown_secao_tutorial_com_litellm_transcribrothers(
    *,
    markdown_secao_atual: str,
    markdown_tutorial_completo: str,
    linha_heading_secao: str,
    instrucoes_revisor: str,
    transcricao: ResultadoTranscricaoComSegmentos,
    rels_completos_snapshot: list[tuple[float, str]],
    diretorio_assets_absoluto: Path | None,
    titulos_outras_secoes_markdown_nivel2: list[str] | None = None,
    modelo: str,
    api_key: str | None,
    api_base: str | None,
    httpx_verify: bool | str = True,
    httpx_timeout_connect_segundos: float = 120.0,
    httpx_timeout_read_segundos: float = 7200.0,
    steps_para_log_decisoes_ia: dict[str, Any] | None = None,
) -> str:
    timestamps = extrair_timestamps_segundos_do_markdown_secao_transcribrothers(markdown_secao_atual)
    segmentos_ctx = filtrar_segmentos_transcricao_proximos_a_timestamps_secao_transcribrothers(
        transcricao, timestamps
    )
    payload_json = {
        "texto_completo_resumo": transcricao.texto_completo[:8000]
        if len(transcricao.texto_completo) > 8000
        else transcricao.texto_completo,
        "idioma": transcricao.idioma_detectado,
        "segmentos_relevantes": _serializar_segmentos(segmentos_ctx),
        "secao_heading": linha_heading_secao.strip(),
    }

    rels_anexo = _enriquecer_payload_json_com_frames_extraidos_edicao_secao_transcribrothers(
        payload_json,
        markdown_tutorial_completo=markdown_tutorial_completo,
        markdown_escopo_edicao=markdown_secao_atual,
        instrucoes_revisor=instrucoes_revisor,
        rels_completos_snapshot=rels_completos_snapshot,
        timestamps_escopo_segundos=timestamps,
    )
    usar_visao = bool(rels_anexo) and diretorio_assets_absoluto is not None

    outras = [t.strip() for t in (titulos_outras_secoes_markdown_nivel2 or []) if t.strip()]
    bloco_outras = ""
    if outras:
        bloco_outras = (
            "\n\nOutras seções do tutorial (NÃO repita os temas que já cobrem — aprofunde só o escopo desta seção):\n"
            + "\n".join(f"- {t}" for t in outras)
        )

    partes_user: list[str] = [
        "Transcrição (JSON, trechos relevantes):\n",
        json.dumps(payload_json, ensure_ascii=False, indent=2),
        bloco_outras,
        "\n\n---\n## Seção atual (reescreva só isto)\n\n",
        markdown_secao_atual.strip(),
        "\n---\n\nInstruções do revisor:\n",
        (instrucoes_revisor or "").strip() or "(melhorar clareza e detalhe, sem alterar o significado factual)",
    ]
    texto_user = "".join(partes_user)

    chave = (api_key or "").strip()
    if not chave:
        raise RuntimeError("LITELLM_API_KEY ausente no servidor.")
    base_v1 = normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1(api_base)
    if not base_v1:
        raise RuntimeError("LITELLM_ENDPOINT ausente no servidor.")
    url_chat = f"{base_v1}/chat/completions"

    if usar_visao:
        assert diretorio_assets_absoluto is not None
        png_blobs = await asyncio.to_thread(
            _ler_bytes_pngs_assets_em_ordem_dos_rels_sync_transcribrothers,
            diretorio_assets_absoluto,
            rels_anexo,
        )
        partes_conteudo: list[dict] = [
            {
                "type": "text",
                "text": texto_user
                + "\n\nAs imagens PNG seguem a ordem de frames_enviados_com_visao no JSON "
                "(catálogo completo em frames_extraidos_disponiveis).",
            }
        ]
        for blob in png_blobs:
            b64 = base64.b64encode(blob).decode("ascii")
            partes_conteudo.append(
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
            )
        corpo_user_content: str | list[dict] = partes_conteudo
    else:
        corpo_user_content = texto_user

    corpo_requisicao = {
        "model": modelo,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT_REGENERACAO_SECAO_MARKDOWN_TUTORIAL_TRANSCRIBROTHERS},
            {"role": "user", "content": corpo_user_content},
        ],
        "temperature": 0.3,
    }
    headers = {"Authorization": f"Bearer {chave}", "Content-Type": "application/json"}
    timeout = httpx.Timeout(
        connect=max(5.0, float(httpx_timeout_connect_segundos)),
        read=max(60.0, float(httpx_timeout_read_segundos)),
        write=max(60.0, float(httpx_timeout_read_segundos)),
        pool=max(5.0, float(httpx_timeout_connect_segundos)),
    )
    async with httpx.AsyncClient(timeout=timeout, verify=httpx_verify) as client:
        http = await client.post(url_chat, headers=headers, json=corpo_requisicao)
    if http.status_code >= 400:
        trecho = (http.text or "")[:2000]
        raise RuntimeError(
            f"Regeneração da seção falhou (HTTP {http.status_code}). Trecho: {trecho}"
        )
    body = http.json()
    try:
        choice = body["choices"][0]["message"]
        conteudo = extrair_texto_resposta_message_openai_compat_transcribrothers(choice)
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Resposta inesperada do gateway: {body!r}") from exc
    if not isinstance(conteudo, str) or not conteudo.strip():
        raise RuntimeError("O modelo devolveu conteúdo vazio para a seção.")
    texto = conteudo.strip()
    if texto.startswith("```"):
        linhas = texto.splitlines()
        if linhas and linhas[0].startswith("```"):
            linhas = linhas[1:]
        if linhas and linhas[-1].strip() == "```":
            linhas = linhas[:-1]
        texto = "\n".join(linhas).strip()
    if steps_para_log_decisoes_ia is not None:
        from transcribrothers_backend.modulo_util_log_decisoes_ia_pipeline_steps_json_transcribrothers import (
            registrar_decisao_ia_em_steps_json_pipeline_transcribrothers,
            resumir_texto_resposta_ia_para_log_decisoes_pipeline_transcribrothers,
        )

        registrar_decisao_ia_em_steps_json_pipeline_transcribrothers(
            steps_para_log_decisoes_ia,
            etapa="regeneracao_secao_markdown",
            resumo=resumir_texto_resposta_ia_para_log_decisoes_pipeline_transcribrothers(texto),
            detalhe=texto[:6000],
            modelo=modelo,
            metadados={
                "secao_heading": linha_heading_secao.strip(),
                "com_visao": usar_visao,
                "frames_visao": len(rels_anexo),
            },
        )
    return texto


async def regenerar_markdown_zona_escopo_secao_tutorial_com_litellm_transcribrothers(
    *,
    markdown_secao_completa_para_contexto: str,
    markdown_tutorial_completo: str,
    linha_heading_secao: str,
    fatia: FatiaEscopoEdicaoSecaoMarkdownTutorialTranscribrothers,
    modo_escopo: ModoEscopoEdicaoSecaoMarkdownTutorialTranscribrothers,
    instrucoes_revisor: str,
    transcricao: ResultadoTranscricaoComSegmentos,
    rels_completos_snapshot: list[tuple[float, str]],
    diretorio_assets_absoluto: Path | None,
    titulos_outras_secoes_markdown_nivel2: list[str] | None = None,
    modelo: str,
    api_key: str | None,
    api_base: str | None,
    httpx_verify: bool | str = True,
    httpx_timeout_connect_segundos: float = 120.0,
    httpx_timeout_read_segundos: float = 7200.0,
    steps_para_log_decisoes_ia: dict[str, Any] | None = None,
) -> str:
    md_ctx = markdown_secao_completa_para_contexto.strip()
    timestamps = extrair_timestamps_segundos_do_markdown_secao_transcribrothers(md_ctx)
    segmentos_ctx = filtrar_segmentos_transcricao_proximos_a_timestamps_secao_transcribrothers(
        transcricao, timestamps
    )
    payload_json = {
        "texto_completo_resumo": transcricao.texto_completo[:8000]
        if len(transcricao.texto_completo) > 8000
        else transcricao.texto_completo,
        "idioma": transcricao.idioma_detectado,
        "segmentos_relevantes": _serializar_segmentos(segmentos_ctx),
        "secao_heading": linha_heading_secao.strip(),
        "modo_escopo_edicao": modo_escopo,
    }

    timestamps_ctx = extrair_timestamps_segundos_do_markdown_para_frames_edicao_secao_transcribrothers(md_ctx)
    rels_anexo = _enriquecer_payload_json_com_frames_extraidos_edicao_secao_transcribrothers(
        payload_json,
        markdown_tutorial_completo=markdown_tutorial_completo,
        markdown_escopo_edicao=md_ctx,
        instrucoes_revisor=instrucoes_revisor,
        rels_completos_snapshot=rels_completos_snapshot,
        timestamps_escopo_segundos=timestamps_ctx,
    )
    usar_visao = bool(rels_anexo) and diretorio_assets_absoluto is not None

    outras = [t.strip() for t in (titulos_outras_secoes_markdown_nivel2 or []) if t.strip()]
    bloco_outras = ""
    if outras:
        bloco_outras = (
            "\n\nOutras seções do tutorial (NÃO repita os temas que já cobrem):\n"
            + "\n".join(f"- {t}" for t in outras)
        )

    rotulo_modo = {
        "trecho_local": "Nesta parte (somente o bloco entre prefixo e sufixo pode mudar)",
        "a_partir_de": "A partir daqui (da zona editável até o fim da seção; o prefixo é intocável)",
    }.get(modo_escopo, modo_escopo)

    partes_user: list[str] = [
        "Transcrição (JSON, trechos relevantes):\n",
        json.dumps(payload_json, ensure_ascii=False, indent=2),
        bloco_outras,
        f"\n\n---\nModo de escopo: {rotulo_modo}\n",
        "\n### Prefixo imutável (NÃO inclua na resposta)\n\n",
        fatia.prefixo_imutavel.strip() or "(vazio)",
        "\n\n### Zona editável (reescreva SOMENTE isto)\n\n",
        fatia.zona_editavel.strip(),
        "\n\n### Sufixo imutável (NÃO inclua na resposta)\n\n",
        fatia.sufixo_imutavel.strip() or "(vazio)",
        "\n---\n\nInstruções do revisor:\n",
        (instrucoes_revisor or "").strip() or "(melhorar conforme o escopo, sem alterar o significado factual)",
    ]
    texto_user = "".join(partes_user)

    chave = (api_key or "").strip()
    if not chave:
        raise RuntimeError("LITELLM_API_KEY ausente no servidor.")
    base_v1 = normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1(api_base)
    if not base_v1:
        raise RuntimeError("LITELLM_ENDPOINT ausente no servidor.")
    url_chat = f"{base_v1}/chat/completions"

    if usar_visao:
        assert diretorio_assets_absoluto is not None
        png_blobs = await asyncio.to_thread(
            _ler_bytes_pngs_assets_em_ordem_dos_rels_sync_transcribrothers,
            diretorio_assets_absoluto,
            rels_anexo,
        )
        partes_conteudo: list[dict] = [
            {
                "type": "text",
                "text": texto_user
                + "\n\nAs imagens PNG seguem a ordem de frames_enviados_com_visao no JSON "
                "(catálogo completo em frames_extraidos_disponiveis).",
            }
        ]
        for blob in png_blobs:
            b64 = base64.b64encode(blob).decode("ascii")
            partes_conteudo.append(
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
            )
        corpo_user_content: str | list[dict] = partes_conteudo
    else:
        corpo_user_content = texto_user

    corpo_requisicao = {
        "model": modelo,
        "messages": [
            {
                "role": "system",
                "content": SYSTEM_PROMPT_REGENERACAO_ZONA_ESCOPO_SECAO_MARKDOWN_TUTORIAL_TRANSCRIBROTHERS,
            },
            {"role": "user", "content": corpo_user_content},
        ],
        "temperature": 0.3,
    }
    headers = {"Authorization": f"Bearer {chave}", "Content-Type": "application/json"}
    timeout = httpx.Timeout(
        connect=max(5.0, float(httpx_timeout_connect_segundos)),
        read=max(60.0, float(httpx_timeout_read_segundos)),
        write=max(60.0, float(httpx_timeout_read_segundos)),
        pool=max(5.0, float(httpx_timeout_connect_segundos)),
    )
    async with httpx.AsyncClient(timeout=timeout, verify=httpx_verify) as client:
        http = await client.post(url_chat, headers=headers, json=corpo_requisicao)
    if http.status_code >= 400:
        trecho = (http.text or "")[:2000]
        raise RuntimeError(
            f"Regeneração da zona editável falhou (HTTP {http.status_code}). Trecho: {trecho}"
        )
    body = http.json()
    try:
        choice = body["choices"][0]["message"]
        conteudo = extrair_texto_resposta_message_openai_compat_transcribrothers(choice)
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"Resposta inesperada do gateway: {body!r}") from exc
    if not isinstance(conteudo, str) or not conteudo.strip():
        raise RuntimeError("O modelo devolveu conteúdo vazio para a zona editável.")
    texto = conteudo.strip()
    if texto.startswith("```"):
        linhas = texto.splitlines()
        if linhas and linhas[0].startswith("```"):
            linhas = linhas[1:]
        if linhas and linhas[-1].strip() == "```":
            linhas = linhas[:-1]
        texto = "\n".join(linhas).strip()
    if steps_para_log_decisoes_ia is not None:
        from transcribrothers_backend.modulo_util_log_decisoes_ia_pipeline_steps_json_transcribrothers import (
            registrar_decisao_ia_em_steps_json_pipeline_transcribrothers,
            resumir_texto_resposta_ia_para_log_decisoes_pipeline_transcribrothers,
        )

        registrar_decisao_ia_em_steps_json_pipeline_transcribrothers(
            steps_para_log_decisoes_ia,
            etapa="regeneracao_zona_escopo_secao",
            resumo=resumir_texto_resposta_ia_para_log_decisoes_pipeline_transcribrothers(texto),
            detalhe=texto[:6000],
            modelo=modelo,
            metadados={
                "modo_escopo": modo_escopo,
                "secao_heading": linha_heading_secao.strip(),
                "com_visao": usar_visao,
                "frames_visao": len(rels_anexo),
            },
        )
    return texto
