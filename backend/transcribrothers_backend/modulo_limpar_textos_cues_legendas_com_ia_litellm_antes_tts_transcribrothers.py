"""Limpa artefatos de Markdown/pontuação órfã nos textos das cues via LiteLLM (antes do TTS)."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any

from transcribrothers_backend.modulo_cliente_litellm_chat_completions_texto_simples_transcribrothers import (
    litellm_chat_completions_texto_simples_transcribrothers,
)
from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    listar_modelos_litellm_provisionados_para_interface,
    resolver_api_key_e_api_base_para_chamada_litellm,
    resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm,
)
from transcribrothers_backend.modulo_verificar_modelo_litellm_chat_completions_probe_transcribrothers import (
    modelo_litellm_parece_tts_pelo_slug_transcribrothers,
)

CHAVE_STEPS_JSON_LIMPEZA_LEGENDAS_IA_TRANSCRIBROTHERS = "limpeza_legendas_ia_antes_tts"
FASE_VIDEO_NARRADO_LIMPANDO_LEGENDAS_IA = "video_narrado_limpando_legendas_ia"

_SYSTEM_LIMPEZA_CUES_LEGENDAS = """\
Você limpa textos de legendas/cues de narração em português do Brasil.

Tarefa: remover APENAS lixo de borda ou artefato de Markdown no início/fim de cada cue, por exemplo:
- pontuação órfã no início («).», «)», «].», «.,»)
- restos de link Markdown incompleto («[01:49](», «](», «[mm:ss](»)
- fragmentos de âncora temporal («?t=123») ou rótulos de tempo soltos no fim («[01:49]»)
- espaços/pontuação duplicada deixada após a remoção

Regras obrigatórias:
1) NÃO reescreva, NÃO resuma, NÃO melhore estilo, NÃO traduza.
2) NÃO altere o sentido, nomes, números úteis nem o miolo da frase.
3) Se estiver em dúvida, devolva o texto ORIGINAL da cue.
4) Mantenha a MESMA quantidade de cues e os MESMOS índices.
5) Responda SOMENTE JSON válido, sem markdown, no formato:
{"cues":[{"indice":0,"texto":"..."},{"indice":1,"texto":"..."}]}
"""

_RE_FENCE_JSON = re.compile(r"```(?:json)?\s*([\s\S]*?)```", re.IGNORECASE)
_FRACAO_MINIMA_COMPRIMENTO_APOS_LIMPEZA = 0.4
_CRESCIMENTO_MAXIMO_RELATIVO = 0.15
_CRESCIMENTO_MAXIMO_ABSOLUTO_CHARS = 24


@dataclass(frozen=True)
class AlteracaoLimpezaCueLegendaIaTranscribrothers:
    indice: int
    antes: str
    depois: str


@dataclass(frozen=True)
class ResultadoLimpezaTextosCuesLegendasIaTranscribrothers:
    textos: list[str]
    ok: bool
    mensagem: str
    modelo: str = ""
    quantidade_alteradas: int = 0
    indices_alterados: tuple[int, ...] = ()
    indices_rejeitados_guarda: tuple[int, ...] = ()
    usou_fallback_originais: bool = False
    alteracoes: tuple[AlteracaoLimpezaCueLegendaIaTranscribrothers, ...] = ()
    modelos_tentados: tuple[str, ...] = ()


def listar_modelos_chat_candidatos_para_limpeza_legendas_ia_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    modelo_solicitado: str | None = None,
) -> list[str]:
    """Ordem: solicitado → LITELLM_MODEL → demais provisionados (sem -tts), sem duplicar."""
    vistos: set[str] = set()
    ordenados: list[str] = []

    def _add(slug: str) -> None:
        m = (slug or "").strip()
        if not m or m in vistos:
            return
        if modelo_litellm_parece_tts_pelo_slug_transcribrothers(m):
            return
        vistos.add(m)
        ordenados.append(m)

    _add(modelo_solicitado or "")
    _add(cfg.litellm_model or "")
    for m in listar_modelos_litellm_provisionados_para_interface(cfg):
        _add(m)
    return ordenados


def resolver_modelo_chat_para_limpeza_legendas_ia_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    modelo_solicitado: str | None = None,
) -> str:
    candidatos = listar_modelos_chat_candidatos_para_limpeza_legendas_ia_transcribrothers(
        cfg,
        modelo_solicitado,
    )
    if candidatos:
        return candidatos[0]
    raise ValueError(
        "Nenhum modelo de chat configurado para limpeza de legendas "
        "(precisa de um slug sem -tts em LITELLM_MODELOS_PROVISIONADOS ou LITELLM_MODEL)."
    )


def montar_alteracoes_limpeza_cues_antes_depois_transcribrothers(
    originais: list[str],
    finais: list[str],
    indices_alterados: list[int] | tuple[int, ...],
) -> tuple[AlteracaoLimpezaCueLegendaIaTranscribrothers, ...]:
    alteracoes: list[AlteracaoLimpezaCueLegendaIaTranscribrothers] = []
    for i in indices_alterados:
        if i < 0 or i >= len(originais) or i >= len(finais):
            continue
        alteracoes.append(
            AlteracaoLimpezaCueLegendaIaTranscribrothers(
                indice=int(i),
                antes=_normalizar_espacos_texto_cue_transcribrothers(originais[i])
                or (originais[i] or ""),
                depois=_normalizar_espacos_texto_cue_transcribrothers(finais[i])
                or (finais[i] or ""),
            )
        )
    return tuple(alteracoes)


def _normalizar_espacos_texto_cue_transcribrothers(texto: str) -> str:
    return " ".join((texto or "").replace("\r\n", "\n").replace("\r", "\n").split())


def texto_limpo_ia_e_aceitavel_contra_original_transcribrothers(
    original: str,
    proposto: str,
) -> bool:
    """
    Guarda-corpo: rejeita vazio ou reescrita.
    Aceita se o texto limpo for substring do original (só removeu bordas/lixo)
    ou se o encolhimento/crescimento ficar dentro de limites seguros.
    """
    o = _normalizar_espacos_texto_cue_transcribrothers(original)
    p = _normalizar_espacos_texto_cue_transcribrothers(proposto)
    if not p:
        return False
    if not o:
        return True
    if p == o:
        return True
    # Caso típico: removeu «).» / «[01:49](» nas bordas — o miolo continua no original.
    if p in o:
        return True
    if len(p) < max(1, int(len(o) * _FRACAO_MINIMA_COMPRIMENTO_APOS_LIMPEZA)):
        return False
    crescimento = len(p) - len(o)
    if crescimento > _CRESCIMENTO_MAXIMO_ABSOLUTO_CHARS and crescimento > int(
        len(o) * _CRESCIMENTO_MAXIMO_RELATIVO
    ):
        return False
    # Sem substring e com alteração relevante: trate como reescrita e rejeite.
    return False


def extrair_json_objeto_da_resposta_limpeza_legendas_ia_transcribrothers(
    bruto: str,
) -> dict[str, Any]:
    t = (bruto or "").strip()
    if not t:
        raise ValueError("Resposta vazia da limpeza de legendas.")
    m = _RE_FENCE_JSON.search(t)
    if m:
        t = m.group(1).strip()
    inicio = t.find("{")
    fim = t.rfind("}")
    if inicio < 0 or fim <= inicio:
        raise ValueError("Resposta da limpeza sem objeto JSON.")
    obj = json.loads(t[inicio : fim + 1])
    if not isinstance(obj, dict):
        raise ValueError("JSON da limpeza não é um objeto.")
    return obj


def mesclar_textos_limpos_ia_com_originais_e_guardas_transcribrothers(
    textos_originais: list[str],
    resposta_bruta_ou_obj: str | dict[str, Any],
) -> tuple[list[str], list[int], list[int]]:
    """
    Devolve (textos_finais, indices_alterados, indices_rejeitados_pela_guarda).
    Exige a mesma quantidade de cues; falha com ValueError se a estrutura for inválida.
    """
    if isinstance(resposta_bruta_ou_obj, dict):
        obj = resposta_bruta_ou_obj
    else:
        obj = extrair_json_objeto_da_resposta_limpeza_legendas_ia_transcribrothers(
            str(resposta_bruta_ou_obj)
        )
    lista = obj.get("cues")
    if not isinstance(lista, list) or len(lista) != len(textos_originais):
        raise ValueError(
            "Quantidade de cues na resposta da IA não bate com a entrada "
            f"({0 if not isinstance(lista, list) else len(lista)} != {len(textos_originais)})."
        )
    por_indice: dict[int, str] = {}
    for item in lista:
        if not isinstance(item, dict):
            raise ValueError("Item de cue inválido na resposta da IA.")
        try:
            idx = int(item["indice"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("Cue sem índice válido na resposta da IA.") from exc
        texto = item.get("texto")
        if not isinstance(texto, str):
            raise ValueError(f"Cue {idx}: texto inválido na resposta da IA.")
        if idx in por_indice:
            raise ValueError(f"Índice duplicado na resposta da IA: {idx}.")
        por_indice[idx] = texto

    if set(por_indice.keys()) != set(range(len(textos_originais))):
        raise ValueError("Índices da resposta da IA não cobrem 0..N-1 sem buracos.")

    finais: list[str] = []
    alterados: list[int] = []
    rejeitados: list[int] = []
    for i, original in enumerate(textos_originais):
        proposto = por_indice[i]
        if not texto_limpo_ia_e_aceitavel_contra_original_transcribrothers(original, proposto):
            finais.append(_normalizar_espacos_texto_cue_transcribrothers(original) or original)
            rejeitados.append(i)
            continue
        limpo = _normalizar_espacos_texto_cue_transcribrothers(proposto)
        orig_norm = _normalizar_espacos_texto_cue_transcribrothers(original)
        finais.append(limpo)
        if limpo != orig_norm:
            alterados.append(i)
    return finais, alterados, rejeitados


def _montar_mensagens_limpeza_cues_transcribrothers(textos: list[str]) -> list[dict[str, str]]:
    payload = {
        "cues": [
            {"indice": i, "texto": _normalizar_espacos_texto_cue_transcribrothers(t) or (t or "")}
            for i, t in enumerate(textos)
        ]
    }
    user = (
        "Limpe apenas o lixo de borda/artefato Markdown destas cues. "
        "Devolva JSON com a mesma quantidade e índices.\n\n"
        + json.dumps(payload, ensure_ascii=False)
    )
    return [
        {"role": "system", "content": _SYSTEM_LIMPEZA_CUES_LEGENDAS},
        {"role": "user", "content": user},
    ]


async def limpar_textos_cues_legendas_com_ia_litellm_antes_tts_transcribrothers(
    *,
    textos: list[str],
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    modelo_chat: str | None = None,
    steps_para_log: dict[str, Any] | None = None,
) -> ResultadoLimpezaTextosCuesLegendasIaTranscribrothers:
    """
    Chama o proxy LiteLLM (chat) e devolve textos limpos.
    Se um modelo falhar (ex.: HTTP 400), tenta o próximo candidato de chat.
    Em falha total, devolve os originais (não aborta o pipeline).
    """
    originais = list(textos)
    if not originais:
        return ResultadoLimpezaTextosCuesLegendasIaTranscribrothers(
            textos=[],
            ok=True,
            mensagem="Nenhuma cue para limpar.",
            usou_fallback_originais=False,
        )

    candidatos = listar_modelos_chat_candidatos_para_limpeza_legendas_ia_transcribrothers(
        configuracao,
        modelo_chat,
    )
    if not candidatos:
        return ResultadoLimpezaTextosCuesLegendasIaTranscribrothers(
            textos=originais,
            ok=False,
            mensagem=(
                "Nenhum modelo de chat configurado para limpeza de legendas "
                "(precisa de um slug sem -tts)."
            ),
            usou_fallback_originais=True,
        )

    api_key, api_base = resolver_api_key_e_api_base_para_chamada_litellm(configuracao)
    httpx_verify = resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(configuracao)
    erros_por_modelo: list[str] = []
    modelos_tentados: list[str] = []

    for modelo in candidatos:
        modelos_tentados.append(modelo)
        if steps_para_log is not None:
            steps_para_log["video_narrado_limpeza_ia_status"] = "chamando_modelo"
            steps_para_log["video_narrado_limpeza_ia_modelo_atual"] = modelo
            steps_para_log["video_narrado_limpeza_ia_resumo"] = (
                f"Limpando {len(originais)} cue(s) com {modelo}…"
            )
        try:
            bruto = await litellm_chat_completions_texto_simples_transcribrothers(
                modelo=modelo,
                api_key=api_key,
                api_base=api_base,
                httpx_verify=httpx_verify,
                mensagens=_montar_mensagens_limpeza_cues_transcribrothers(originais),
                temperature=0.1,
                usar_response_format_json_object=True,
                httpx_timeout_connect_segundos=30.0,
                httpx_timeout_read_segundos=180.0,
                steps_para_log_decisoes_ia=steps_para_log,
                log_etapa="limpeza_legendas_ia_antes_tts",
                log_resumo_pedido=f"{len(originais)} cue(s) para limpeza de artefatos",
                log_metadados={
                    "quantidade_cues": len(originais),
                    "modelo_tentativa": modelo,
                    "tentativa": len(modelos_tentados),
                },
                log_incluir_detalhe_resposta=False,
            )
            finais, alterados, rejeitados = (
                mesclar_textos_limpos_ia_com_originais_e_guardas_transcribrothers(
                    originais,
                    bruto,
                )
            )
        except Exception as exc:
            erros_por_modelo.append(f"{modelo}: {exc}")
            if steps_para_log is not None:
                steps_para_log["video_narrado_limpeza_ia_status"] = "tentando_outro_modelo"
                steps_para_log["video_narrado_limpeza_ia_resumo"] = (
                    f"Modelo {modelo} falhou; tentando outro…"
                )
            continue

        alteracoes = montar_alteracoes_limpeza_cues_antes_depois_transcribrothers(
            originais,
            finais,
            alterados,
        )
        msg = (
            f"Limpeza IA ({modelo}): {len(alterados)} cue(s) ajustada(s)"
            + (f"; {len(rejeitados)} rejeitada(s) pela guarda." if rejeitados else ".")
        )
        if len(modelos_tentados) > 1:
            msg += f" Modelos tentados: {', '.join(modelos_tentados)}."
        return ResultadoLimpezaTextosCuesLegendasIaTranscribrothers(
            textos=finais,
            ok=True,
            mensagem=msg,
            modelo=modelo,
            quantidade_alteradas=len(alterados),
            indices_alterados=tuple(alterados),
            indices_rejeitados_guarda=tuple(rejeitados),
            usou_fallback_originais=False,
            alteracoes=alteracoes,
            modelos_tentados=tuple(modelos_tentados),
        )

    detalhe_erros = " | ".join(erros_por_modelo)[:2500]
    return ResultadoLimpezaTextosCuesLegendasIaTranscribrothers(
        textos=originais,
        ok=False,
        mensagem=(
            "Limpeza IA falhou em todos os modelos de chat; mantidos textos originais. "
            f"({detalhe_erros})"
        ),
        modelo=modelos_tentados[-1] if modelos_tentados else "",
        usou_fallback_originais=True,
        modelos_tentados=tuple(modelos_tentados),
    )


def aplicar_textos_limpos_nas_cues_janela_transcribrothers(
    cues: list[Any],
    textos_limpos: list[str],
) -> list[Any]:
    """Recria cues (dataclass frozen) com novos textos; exige mesma quantidade."""
    from transcribrothers_backend.modulo_montar_cues_narracao_com_janelas_video_a_partir_markdown_ancoras_temporais_transcribrothers import (
        CueNarracaoComJanelaVideoTranscribrothers,
    )

    if len(cues) != len(textos_limpos):
        raise ValueError("Quantidade de textos limpos ≠ cues.")
    return [
        CueNarracaoComJanelaVideoTranscribrothers(
            texto=texto,
            inicio_video_segundos=c.inicio_video_segundos,
            fim_video_segundos=c.fim_video_segundos,
            origem_ancora=c.origem_ancora,
            casado=c.casado,
            sem_narracao=bool(getattr(c, "sem_narracao", False)),
            voz_tts=str(getattr(c, "voz_tts", "") or ""),
            texto_tts=str(getattr(c, "texto_tts", "") or ""),
        )
        for c, texto in zip(cues, textos_limpos, strict=True)
    ]
