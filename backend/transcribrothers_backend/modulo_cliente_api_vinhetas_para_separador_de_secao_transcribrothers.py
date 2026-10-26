"""Cliente HTTP do app de vinhetas para o separador de seção."""

from __future__ import annotations

import json
import os
from typing import Any, Mapping

import httpx

NOME_CABECALHO_DEBUG_DA_VINHETA = "X-Vinheta-Debug"

URL_PADRAO_DA_API_DE_VINHETAS = "http://127.0.0.1:5090"

MODELOS_DE_VINHETA_PARA_O_SEPARADOR = (
    {"id": "planos-que-abrem-espaco", "nome": "Planos que abrem um espaço"},
    {"id": "linhas-que-desenham-o-lugar", "nome": "Linhas que desenham o lugar"},
    {"id": "barras-que-se-cruzam", "nome": "Barras que se cruzam"},
)


def url_da_api_de_vinhetas() -> str:
    return os.environ.get("VINHETAS_API_BASE", URL_PADRAO_DA_API_DE_VINHETAS).rstrip("/")


def _mensagem_de_erro(resposta: httpx.Response, reserva: str) -> str:
    try:
        detalhe = resposta.json().get("detail")
    except Exception:
        detalhe = None
    if isinstance(detalhe, str) and detalhe.strip():
        return detalhe.strip()
    return reserva


async def listar_vinhetas_para_o_separador(
    url_base: str | None = None,
) -> dict[str, object]:
    base = (url_base or url_da_api_de_vinhetas()).rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=10) as cliente:
            resposta = await cliente.get(f"{base}/api/vinhetas")
    except httpx.HTTPError as erro:
        raise RuntimeError("O app de vinhetas não está no ar.") from erro
    if resposta.status_code >= 400:
        raise RuntimeError(_mensagem_de_erro(resposta, "Não foi possível listar as vinhetas."))
    projetos = resposta.json()
    if not isinstance(projetos, list):
        projetos = []
    return {"modelos": list(MODELOS_DE_VINHETA_PARA_O_SEPARADOR), "projetos": projetos}


def interpretar_cabecalho_debug_da_vinheta(cabecalhos: Mapping[str, str] | None) -> dict[str, Any]:
    if not cabecalhos:
        return {}
    bruto = None
    getter = getattr(cabecalhos, "get", None)
    if callable(getter):
        bruto = getter(NOME_CABECALHO_DEBUG_DA_VINHETA) or getter("x-vinheta-debug")
    if not isinstance(bruto, str) or not bruto.strip():
        return {}
    try:
        dados = json.loads(bruto)
    except json.JSONDecodeError:
        return {}
    return dados if isinstance(dados, dict) else {}


async def baixar_mp4_renderizado_da_vinheta_com_debug(
    **kwargs: Any,
) -> tuple[bytes, dict[str, Any]]:
    conteudo, debug = await _baixar_mp4_renderizado_da_vinheta(devolver_debug=True, **kwargs)
    return conteudo, debug


async def baixar_mp4_renderizado_da_vinheta(
    *,
    titulo: str,
    efeito: str | None = None,
    vinheta_id: str | None = None,
    imagem_de_fundo_base64: str | None = None,
    imagem_quadro_anterior_base64: str | None = None,
    duracao_segundos: float | None = None,
    presenca_da_imagem: int | None = None,
    cores: dict[str, str] | None = None,
    largura: int | None = None,
    altura: int | None = None,
    url_base: str | None = None,
) -> bytes:
    conteudo, _debug = await _baixar_mp4_renderizado_da_vinheta(
        titulo=titulo,
        efeito=efeito,
        vinheta_id=vinheta_id,
        imagem_de_fundo_base64=imagem_de_fundo_base64,
        imagem_quadro_anterior_base64=imagem_quadro_anterior_base64,
        duracao_segundos=duracao_segundos,
        presenca_da_imagem=presenca_da_imagem,
        cores=cores,
        largura=largura,
        altura=altura,
        url_base=url_base,
        devolver_debug=False,
    )
    return conteudo


async def _baixar_mp4_renderizado_da_vinheta(
    *,
    titulo: str,
    efeito: str | None = None,
    vinheta_id: str | None = None,
    imagem_de_fundo_base64: str | None = None,
    imagem_quadro_anterior_base64: str | None = None,
    duracao_segundos: float | None = None,
    presenca_da_imagem: int | None = None,
    cores: dict[str, str] | None = None,
    largura: int | None = None,
    altura: int | None = None,
    url_base: str | None = None,
    devolver_debug: bool = False,
) -> tuple[bytes, dict[str, Any]]:
    base = (url_base or url_da_api_de_vinhetas()).rstrip("/")
    corpo: dict[str, object] = {"titulo": titulo}
    if vinheta_id:
        corpo["id"] = vinheta_id
    elif efeito:
        corpo["efeito"] = efeito
    if imagem_de_fundo_base64:
        corpo["imagem_de_fundo_base64"] = imagem_de_fundo_base64
    if imagem_quadro_anterior_base64:
        corpo["imagem_quadro_anterior_base64"] = imagem_quadro_anterior_base64
    if duracao_segundos is not None:
        corpo["duracao_segundos"] = duracao_segundos
    if presenca_da_imagem is not None:
        corpo["presenca_da_imagem"] = presenca_da_imagem
    if cores:
        corpo["cores"] = cores
    if largura is not None:
        corpo["largura"] = largura
    if altura is not None:
        corpo["altura"] = altura
    try:
        async with httpx.AsyncClient(timeout=120) as cliente:
            resposta = await cliente.post(f"{base}/api/vinhetas/renderizar-mp4", json=corpo)
    except httpx.HTTPError as erro:
        raise RuntimeError("O app de vinhetas não está no ar.") from erro
    if resposta.status_code >= 400:
        raise RuntimeError(_mensagem_de_erro(resposta, "Não foi possível gerar a vinheta."))
    if not resposta.content:
        raise RuntimeError("A vinheta veio sem vídeo.")
    debug = interpretar_cabecalho_debug_da_vinheta(getattr(resposta, "headers", None))
    if devolver_debug:
        return resposta.content, debug
    return resposta.content, debug
