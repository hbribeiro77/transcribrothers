"""Detecta screenshots visualmente duplicados no tutorial (visão LiteLLM, até 4 imagens por chamada)."""

from __future__ import annotations

import asyncio
import base64
import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any, Literal

import httpx
from pydantic import BaseModel, Field, field_validator

from transcribrothers_backend.modulo_cliente_litellm_geracao_tutorial_markdown import (
    extrair_texto_resposta_message_openai_compat_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_prompts_e_schema_json_plano_revisao_profunda_tutorial_transcribrothers import (
    extrair_primeiro_objeto_json_de_texto_llm_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1,
)
from transcribrothers_backend.modulo_util_extrair_caminhos_assets_png_referenciados_no_markdown_tutorial_transcribrothers import (
    listar_caminhos_assets_png_em_ordem_primeira_ocorrencia_no_markdown_transcribrothers,
    normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers,
)

MAX_IMAGENS_POR_LOTE_VISAO_VERIFICACAO_DUPLICATAS_TRANSCRIBROTHERS = 4
_PASSO_LOTES_SOBREPOSTOS_VERIFICACAO_DUPLICATAS_TRANSCRIBROTHERS = 3

_RE_IMAGEM_MARKDOWN_LINHA_TRANSCRIBROTHERS = re.compile(
    r"!\[[^\]]*\]\(\s*([^)]+?)\s*\)",
)

SYSTEM_PROMPT_VERIFICACAO_IMAGENS_DUPLICADAS_TUTORIAL_VISAO_TRANSCRIBROTHERS = """\
Você compara screenshots de um tutorial de software.

Receberá até 4 imagens PNG numeradas (1 = primeira imagem deste lote, 2 = segunda, etc.).

Tarefa: identificar quais imagens mostram essencialmente a MESMA tela/estado da interface \
(mesma informação para o leitor), mesmo que sejam arquivos diferentes ou capturas em segundos diferentes.

Regras:
1) Responda APENAS com um JSON válido (sem markdown à volta).
2) Campo obrigatório `grupos_visualmente_iguais`: lista de grupos; cada grupo é uma lista de inteiros \
(índices 1..N deste lote) com pelo menos 2 membros quando há duplicata visual.
3) Imagens únicas (sem duplicata neste lote) não entram em nenhum grupo.
4) `mensagem_resumo` em português, uma frase curta.
5) Se nenhuma duplicata neste lote, `grupos_visualmente_iguais` = [].

Exemplo: {"grupos_visualmente_iguais":[[1,3],[2,4]],"mensagem_resumo":"1≈3 e 2≈4."}
"""


class ResultadoLoteImagensDuplicadasVisaoJsonTranscribrothers(BaseModel):
    grupos_visualmente_iguais: list[list[int]] = Field(default_factory=list)
    mensagem_resumo: str = Field(default="", max_length=2000)

    @field_validator("grupos_visualmente_iguais")
    @classmethod
    def _normalizar_grupos(cls, v: list[list[int]]) -> list[list[int]]:
        out: list[list[int]] = []
        for g in v:
            if not isinstance(g, list) or len(g) < 2:
                continue
            nums = sorted({int(x) for x in g if isinstance(x, (int, float))})
            if len(nums) >= 2:
                out.append(nums)
        return out


def parsear_resultado_lote_imagens_duplicadas_visao_de_texto_resposta_llm_transcribrothers(
    texto_bruto: str,
) -> ResultadoLoteImagensDuplicadasVisaoJsonTranscribrothers:
    """`extrair_primeiro_objeto_json_*` devolve texto JSON; fazemos `json.loads` antes do Pydantic."""
    try:
        raw_json = extrair_primeiro_objeto_json_de_texto_llm_transcribrothers(texto_bruto)
        data = json.loads(raw_json)
    except (json.JSONDecodeError, ValueError) as e:
        trecho = (texto_bruto or "")[:1200]
        raise ValueError(
            "Resposta inválida na verificação de imagens duplicadas (JSON esperado). "
            f"Detalhe: {e}. Trecho: {trecho!r}"
        ) from e
    if not isinstance(data, dict):
        raise ValueError("JSON da verificação de imagens duplicadas deve ser um objeto na raiz.")
    return ResultadoLoteImagensDuplicadasVisaoJsonTranscribrothers.model_validate(data)


class _UnionFindCaminhosAssetsTranscribrothers:
    def __init__(self) -> None:
        self._pai: dict[str, str] = {}

    def _find(self, x: str) -> str:
        self._pai.setdefault(x, x)
        while self._pai[x] != x:
            self._pai[x] = self._pai[self._pai[x]]
            x = self._pai[x]
        return x

    def unir(self, a: str, b: str) -> None:
        ra, rb = self._find(a), self._find(b)
        if ra != rb:
            self._pai[rb] = ra

    def canonico_por_caminho(self, caminho: str) -> str:
        return self._find(caminho)


def listar_indices_lotes_sobrepostos_verificacao_imagens_duplicadas_transcribrothers(
    total_imagens: int,
    *,
    tamanho_lote: int = MAX_IMAGENS_POR_LOTE_VISAO_VERIFICACAO_DUPLICATAS_TRANSCRIBROTHERS,
    passo: int = _PASSO_LOTES_SOBREPOSTOS_VERIFICACAO_DUPLICATAS_TRANSCRIBROTHERS,
) -> list[list[int]]:
    """Janelas de índices 0-based com sobreposição para achar duplicatas entre lotes."""
    n = int(total_imagens)
    if n <= 0:
        return []
    tam = max(1, int(tamanho_lote))
    st = max(1, int(passo))
    if n <= tam:
        return [list(range(n))]
    lotes: list[list[int]] = []
    inicio = 0
    while inicio < n:
        fim = min(inicio + tam, n)
        lotes.append(list(range(inicio, fim)))
        if fim >= n:
            break
        inicio += st
    return lotes


def montar_mapa_canonico_assets_png_apos_uniao_grupos_duplicatas_transcribrothers(
    caminhos_em_ordem_markdown: list[str],
    grupos_pares_caminhos: list[tuple[str, str]],
) -> dict[str, str]:
    """Para cada path, devolve o representante (primeiro na ordem do markdown) do grupo visual."""
    uf = _UnionFindCaminhosAssetsTranscribrothers()
    for p in caminhos_em_ordem_markdown:
        uf._pai.setdefault(p, p)
    for a, b in grupos_pares_caminhos:
        if a in uf._pai or a in caminhos_em_ordem_markdown:
            uf._pai.setdefault(a, a)
        if b in uf._pai or b in caminhos_em_ordem_markdown:
            uf._pai.setdefault(b, b)
        uf.unir(a, b)
    ordem = {p: i for i, p in enumerate(caminhos_em_ordem_markdown)}
    componentes: dict[str, list[str]] = {}
    for p in caminhos_em_ordem_markdown:
        raiz = uf.canonico_por_caminho(p)
        componentes.setdefault(raiz, []).append(p)
    canonico: dict[str, str] = {}
    for membros in componentes.values():
        rep = min(membros, key=lambda x: ordem.get(x, 10**9))
        for p in membros:
            canonico[p] = rep
    return canonico


def remover_linhas_imagens_duplicadas_markdown_tutorial_transcribrothers(
    markdown: str,
    caminho_para_canonico: dict[str, str],
) -> tuple[str, int]:
    """Remove ocorrências de imagem cujo canônico já apareceu antes (mantém a primeira)."""
    if not markdown.strip() or not caminho_para_canonico:
        return markdown, 0
    vistos_canonicos: set[str] = set()
    removidas = 0
    linhas_out: list[str] = []

    for linha in markdown.splitlines(keepends=True):
        linha_sem_nl = linha.rstrip("\r\n")
        nl = linha[len(linha_sem_nl) :]
        matches = list(_RE_IMAGEM_MARKDOWN_LINHA_TRANSCRIBROTHERS.finditer(linha_sem_nl))
        if not matches:
            linhas_out.append(linha)
            continue
        remover_linha = False
        for m in matches:
            norm = normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers(m.group(1))
            if norm is None:
                continue
            can = caminho_para_canonico.get(norm, norm)
            if can in vistos_canonicos:
                remover_linha = True
                removidas += 1
                break
        if not remover_linha:
            for m in matches:
                norm = normalizar_caminho_relativo_asset_png_para_tutorial_transcribrothers(
                    m.group(1)
                )
                if norm is not None:
                    can = caminho_para_canonico.get(norm, norm)
                    vistos_canonicos.add(can)
            linhas_out.append(linha)
    return "".join(linhas_out), removidas


def _ler_bytes_png_assets_por_caminhos_relativos_sync_transcribrothers(
    diretorio_assets: Path,
    caminhos_relativos: list[str],
) -> list[bytes]:
    blobs: list[bytes] = []
    for rel in caminhos_relativos:
        nome = rel.strip().replace("\\", "/").split("/")[-1]
        p = diretorio_assets / nome
        if not p.is_file():
            raise FileNotFoundError(f"PNG ausente para verificação de duplicatas: {p}")
        blobs.append(p.read_bytes())
    return blobs


async def _chamar_litellm_visao_lote_imagens_duplicadas_transcribrothers(
    *,
    modelo: str,
    api_key: str,
    api_base: str | None,
    httpx_verify: bool | str,
    httpx_timeout_connect_segundos: float,
    httpx_timeout_read_segundos: float,
    caminhos_relativos_lote: list[str],
    blobs_png: list[bytes],
    indice_lote: int,
    total_lotes: int,
) -> ResultadoLoteImagensDuplicadasVisaoJsonTranscribrothers:
    n = len(caminhos_relativos_lote)
    lista_meta = [
        {"indice_no_lote": i + 1, "arquivo_relativo_markdown": rel}
        for i, rel in enumerate(caminhos_relativos_lote)
    ]
    texto_user = (
        f"Lote {indice_lote + 1} de {total_lotes}. Compare as {n} imagens anexadas.\n"
        f"Metadados: {json.dumps(lista_meta, ensure_ascii=False)}\n\n"
        "Responda só com o JSON pedido."
    )
    partes: list[dict[str, Any]] = [
        {"type": "text", "text": SYSTEM_PROMPT_VERIFICACAO_IMAGENS_DUPLICADAS_TUTORIAL_VISAO_TRANSCRIBROTHERS + "\n\n" + texto_user}
    ]
    for blob in blobs_png:
        b64 = base64.b64encode(blob).decode("ascii")
        partes.append(
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
        )
    base_v1 = normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1(api_base)
    if not base_v1:
        raise RuntimeError("LITELLM_ENDPOINT inválido para verificação de imagens duplicadas.")
    url = f"{base_v1}/chat/completions"
    timeout = httpx.Timeout(
        connect=max(5.0, float(httpx_timeout_connect_segundos)),
        read=max(60.0, float(httpx_timeout_read_segundos)),
        write=max(60.0, float(httpx_timeout_read_segundos)),
        pool=max(5.0, float(httpx_timeout_connect_segundos)),
    )
    async with httpx.AsyncClient(timeout=timeout, verify=httpx_verify) as client:
        http = await client.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": modelo,
                "messages": [{"role": "user", "content": partes}],
                "temperature": 0.1,
            },
        )
    if http.status_code >= 400:
        trecho = (http.text or "")[:1500]
        raise RuntimeError(
            f"Verificação de imagens duplicadas falhou (HTTP {http.status_code}): {trecho}"
        )
    body = http.json()
    msg = body["choices"][0]["message"]
    texto = extrair_texto_resposta_message_openai_compat_transcribrothers(msg)
    return parsear_resultado_lote_imagens_duplicadas_visao_de_texto_resposta_llm_transcribrothers(texto)


def blob_verificacao_imagens_duplicadas_omitida_transcribrothers(
    *,
    motivo: str,
) -> dict[str, Any]:
    return {
        "omitida": True,
        "motivo": motivo,
        "grupos_mesclados": [],
        "linhas_imagem_removidas": 0,
    }


async def executar_verificacao_imagens_duplicadas_tutorial_e_aplicar_no_markdown_transcribrothers(
    *,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    markdown_tutorial: str,
    diretorio_assets_absoluto: Path,
    modelo_litellm: str,
    api_key_litellm: str | None,
    api_base_litellm: str | None,
    http_verify_litellm: bool | str,
    levantar_se_cancelado: Callable[[], None] | None = None,
    steps_para_log_decisoes_ia: dict[str, Any] | None = None,
) -> tuple[str, dict[str, Any]]:
    """
    Devolve (markdown_atualizado, blob_para_steps_json).
    Remove linhas com imagens visualmente duplicadas (mantém a primeira ocorrência no texto).
    """
    if configuracao.verificacao_imagens_duplicadas_tutorial_desativada:
        return markdown_tutorial, blob_verificacao_imagens_duplicadas_omitida_transcribrothers(
            motivo="desativada_por_configuracao_ambiente"
        )

    caminhos = listar_caminhos_assets_png_em_ordem_primeira_ocorrencia_no_markdown_transcribrothers(
        markdown_tutorial
    )
    if len(caminhos) < 2:
        return markdown_tutorial, blob_verificacao_imagens_duplicadas_omitida_transcribrothers(
            motivo="menos_de_duas_imagens_no_markdown"
        )

    chave = (api_key_litellm or "").strip()
    if not chave:
        return markdown_tutorial, blob_verificacao_imagens_duplicadas_omitida_transcribrothers(
            motivo="sem_api_key_litellm"
        )

    assets_dir = diretorio_assets_absoluto.resolve()
    if not assets_dir.is_dir():
        return markdown_tutorial, blob_verificacao_imagens_duplicadas_omitida_transcribrothers(
            motivo="diretorio_assets_inexistente"
        )

    lotes_idx = listar_indices_lotes_sobrepostos_verificacao_imagens_duplicadas_transcribrothers(
        len(caminhos)
    )
    pares_uniao: list[tuple[str, str]] = []
    resumos_lotes: list[str] = []
    total_lotes = len(lotes_idx)

    for num_lote, indices in enumerate(lotes_idx):
        if levantar_se_cancelado:
            levantar_se_cancelado()
        caminhos_lote = [caminhos[i] for i in indices]
        blobs = await asyncio.to_thread(
            _ler_bytes_png_assets_por_caminhos_relativos_sync_transcribrothers,
            assets_dir,
            caminhos_lote,
        )
        resultado = await _chamar_litellm_visao_lote_imagens_duplicadas_transcribrothers(
            modelo=modelo_litellm,
            api_key=chave,
            api_base=api_base_litellm,
            httpx_verify=http_verify_litellm,
            httpx_timeout_connect_segundos=float(
                configuracao.litellm_http_timeout_connect_segundos
            ),
            httpx_timeout_read_segundos=float(configuracao.litellm_http_timeout_read_segundos),
            caminhos_relativos_lote=caminhos_lote,
            blobs_png=blobs,
            indice_lote=num_lote,
            total_lotes=total_lotes,
        )
        if resultado.mensagem_resumo.strip():
            resumos_lotes.append(resultado.mensagem_resumo.strip())
        for grupo in resultado.grupos_visualmente_iguais:
            paths_grupo = []
            for idx_1based in grupo:
                j = int(idx_1based) - 1
                if 0 <= j < len(caminhos_lote):
                    paths_grupo.append(caminhos_lote[j])
            for i in range(1, len(paths_grupo)):
                pares_uniao.append((paths_grupo[0], paths_grupo[i]))

        if steps_para_log_decisoes_ia is not None:
            from transcribrothers_backend.modulo_util_log_decisoes_ia_pipeline_steps_json_transcribrothers import (
                registrar_decisao_ia_em_steps_json_pipeline_transcribrothers,
            )

            registrar_decisao_ia_em_steps_json_pipeline_transcribrothers(
                steps_para_log_decisoes_ia,
                etapa=f"verificacao_imagens_duplicadas_lote_{num_lote + 1}",
                resumo=resultado.mensagem_resumo[:500]
                or f"Grupos: {resultado.grupos_visualmente_iguais}",
                detalhe=json.dumps(resultado.model_dump(), ensure_ascii=False)[:4000],
                modelo=modelo_litellm,
                metadados={
                    "indice_lote": num_lote + 1,
                    "total_lotes": total_lotes,
                    "imagens_no_lote": len(caminhos_lote),
                },
            )

    mapa_can = montar_mapa_canonico_assets_png_apos_uniao_grupos_duplicatas_transcribrothers(
        caminhos,
        pares_uniao,
    )
    grupos_finais: list[list[str]] = []
    vistos_rep: set[str] = set()
    for p in caminhos:
        rep = mapa_can.get(p, p)
        if rep in vistos_rep:
            continue
        vistos_rep.add(rep)
        membros = [x for x in caminhos if mapa_can.get(x, x) == rep]
        if len(membros) > 1:
            grupos_finais.append(membros)

    md_novo, n_removidas = remover_linhas_imagens_duplicadas_markdown_tutorial_transcribrothers(
        markdown_tutorial,
        mapa_can,
    )

    blob: dict[str, Any] = {
        "omitida": False,
        "total_imagens_analisadas": len(caminhos),
        "total_lotes_visao": total_lotes,
        "max_imagens_por_lote": MAX_IMAGENS_POR_LOTE_VISAO_VERIFICACAO_DUPLICATAS_TRANSCRIBROTHERS,
        "grupos_visualmente_iguais": grupos_finais,
        "pares_unidos": [{"a": a, "b": b} for a, b in pares_uniao],
        "linhas_imagem_removidas": int(n_removidas),
        "mensagem_resumo": " ".join(resumos_lotes)[:2000] if resumos_lotes else "",
    }
    return md_novo, blob
