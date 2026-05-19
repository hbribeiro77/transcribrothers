from __future__ import annotations

import asyncio
import base64
import json
import re
from pathlib import Path
from typing import Any

import httpx

from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1,
)
from transcribrothers_backend.modulo_speech_to_text_com_segmentos_openai_compat import (
    ResultadoTranscricaoComSegmentos,
    SegmentoTranscricaoComTempo,
)

_PROMPT_TRANSCRICAO_JSON_PT = """Você recebeu um áudio em WAV (fala em português do Brasil, se houver fala).
Transcreva o conteúdo falado de forma fiel.

Responda APENAS com um JSON válido (sem markdown, sem texto antes ou depois), neste formato exato:
{"idioma":"pt","segmentos":[{"inicio_segundos":0.0,"fim_segundos":4.5,"texto":"primeira frase ou trecho"},{"inicio_segundos":4.5,"fim_segundos":9.0,"texto":"segundo trecho"}]}

Regras:
- "segmentos" é uma lista ordenada no tempo; estime inicio_segundos e fim_segundos por trechos coerentes (aproximado).
- Se não houver fala detectável, use um único segmento com texto explicando brevemente (ex.: "Sem fala detectável no áudio.").
- Use ponto flutuante para os tempos (segundos).
- Dentro de cada "texto", use uma única linha: sem quebra de linha literal; sem aspas duplas ASCII — use ' ou reformule.
- Não use vírgula após o último item de um array ou objeto (JSON estrito).
- Nunca repita a mesma palavra ou frase muitas vezes seguidas; se o áudio for confuso ou inaudível, escreva uma vez "[trecho inaudível]" em vez de repetir sílabas ou palavras.
- Prefira segmentos concisos (evite listas enormes de segmentos muito curtos no mesmo trecho).
"""

_PROMPT_TRANSCRICAO_JSON_RETRY_PT = """Repetição: a transcrição anterior falhou (JSON inválido ou resposta cortada).
Transcreva de novo o mesmo áudio com fidelidade, mas:
- Responda APENAS com JSON válido no formato pedido antes (sem markdown).
- Não repita palavras em loop; se não entender o áudio, use "[trecho inaudível]" uma única vez no segmento.
- Use no máximo ~15 segmentos nesta janela; textos curtos por segmento.
"""

_REGEX_SEGMENTO_JSON_TRANSCRICAO_COMPLETO = re.compile(
    r'\{\s*"inicio_segundos"\s*:\s*([0-9]+(?:\.[0-9]+)?)\s*,\s*"fim_segundos"\s*:\s*([0-9]+(?:\.[0-9]+)?)\s*,\s*"texto"\s*:\s*"((?:[^"\\]|\\.)*)"\s*\}',
)

_MAX_TENTATIVAS_HTTP_TRANSCRICAO_JSON = 3


def _recortar_primeiro_objeto_json_por_chaves_balanceadas(texto: str) -> str:
    """Se houver texto antes/depois do objeto, ou múltiplos blocos, tenta isolar o primeiro `{ ... }` com chaves balanceadas."""
    t = texto.strip()
    i0 = t.find("{")
    if i0 < 0:
        return t
    depth = 0
    in_string = False
    escape = False
    for i in range(i0, len(t)):
        c = t[i]
        if in_string:
            if escape:
                escape = False
                continue
            if c == "\\":
                escape = True
                continue
            if c == '"':
                in_string = False
            continue
        if c == '"':
            in_string = True
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return t[i0 : i + 1]
    return t[i0:]


def _remover_virgulas_trailing_em_objetos_e_arrays_json(s: str) -> str:
    s2 = s.strip()
    for _ in range(48):
        prev = s2
        s2 = re.sub(r",\s*}", "}", s2)
        s2 = re.sub(r",\s*]", "]", s2)
        if s2 == prev:
            break
    return s2


def _escapar_quebras_de_linha_dentro_de_strings_json_aproximado(s: str) -> str:
    """Modelos costumam inserir \\n literal dentro de "texto", quebrando json.loads; converte para \\n escapado."""
    out: list[str] = []
    i = 0
    n = len(s)
    in_string = False
    escape = False
    while i < n:
        c = s[i]
        if escape:
            out.append(c)
            escape = False
            i += 1
            continue
        if in_string:
            if c == "\\":
                out.append(c)
                escape = True
                i += 1
                continue
            if c == '"':
                in_string = False
                out.append(c)
                i += 1
                continue
            if c == "\r":
                if i + 1 < n and s[i + 1] == "\n":
                    out.append("\\n")
                    i += 2
                else:
                    out.append("\\n")
                    i += 1
                continue
            if c == "\n":
                out.append("\\n")
                i += 1
                continue
            out.append(c)
            i += 1
            continue
        if c == '"':
            in_string = True
            out.append(c)
            i += 1
            continue
        out.append(c)
        i += 1
    return "".join(out)


def _colapsar_repeticao_palavra_consecutiva_em_texto_segmento_transcricao(
    texto: str,
    *,
    min_repeticoes: int = 6,
) -> str:
    """Reduz alucinações do tipo 'não, não, não…' que estouram o limite de tokens e truncam o JSON."""
    if not texto or len(texto) < 24:
        return texto
    lim = max(3, int(min_repeticoes))
    padrao = re.compile(
        rf"(\b[\wáàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ]+(?:\s+e)?\b)(?:\s*,\s*\1\b){{{lim - 1},}}",
        re.IGNORECASE,
    )
    return padrao.sub(r"\1", texto)


def _decodificar_string_json_escapada_transcricao(valor_bruto: str) -> str:
    try:
        return json.loads(f'"{valor_bruto}"')
    except json.JSONDecodeError:
        return valor_bruto.replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")


def _extrair_objeto_transcricao_de_json_possivelmente_truncado(texto: str) -> dict[str, Any] | None:
    """Quando o modelo corta a resposta no meio de um segmento, recupera os objetos completos já emitidos."""
    t = _recortar_primeiro_objeto_json_por_chaves_balanceadas((texto or "").strip())
    if not t or '"segmentos"' not in t:
        return None
    m_idioma = re.search(r'"idioma"\s*:\s*"([^"\\]*)"\s*,', t)
    idioma = m_idioma.group(1) if m_idioma else "pt"
    segmentos: list[dict[str, Any]] = []
    for m in _REGEX_SEGMENTO_JSON_TRANSCRICAO_COMPLETO.finditer(t):
        try:
            ini = float(m.group(1))
            fim = float(m.group(2))
        except ValueError:
            continue
        tx = _colapsar_repeticao_palavra_consecutiva_em_texto_segmento_transcricao(
            _decodificar_string_json_escapada_transcricao(m.group(3)).strip()
        )
        if tx:
            segmentos.append(
                {"inicio_segundos": ini, "fim_segundos": max(ini, fim), "texto": tx}
            )
    if not segmentos:
        return None
    return {"idioma": idioma, "segmentos": segmentos}


def _variantes_texto_para_parse_json_resposta_llm(s: str) -> list[str]:
    """Ordem: menos invasiva primeiro."""
    v: list[str] = []
    seen: set[str] = set()

    def add(x: str) -> None:
        t = x.strip()
        if t and t not in seen:
            seen.add(t)
            v.append(t)

    base = s.strip()
    add(base)
    add(_remover_virgulas_trailing_em_objetos_e_arrays_json(base))
    add(_escapar_quebras_de_linha_dentro_de_strings_json_aproximado(base))
    add(
        _escapar_quebras_de_linha_dentro_de_strings_json_aproximado(
            _remover_virgulas_trailing_em_objetos_e_arrays_json(base)
        )
    )
    return v


def _extrair_json_do_texto_resposta_llm(texto: str) -> dict:
    t = (texto or "").strip()
    if not t:
        raise ValueError("Resposta vazia do modelo de transcrição.")
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", t, re.IGNORECASE)
    if fence:
        t = fence.group(1).strip()
    recortado = _recortar_primeiro_objeto_json_por_chaves_balanceadas(t)
    blocos = [recortado]
    if recortado.strip() != t.strip():
        blocos.append(t.strip())
    ultimo_erro: json.JSONDecodeError | None = None
    for bloco in blocos:
        for candidato in _variantes_texto_para_parse_json_resposta_llm(bloco):
            try:
                obj = json.loads(candidato)
            except json.JSONDecodeError as exc:
                ultimo_erro = exc
                continue
            if not isinstance(obj, dict):
                raise ValueError(
                    f"JSON da transcrição deve ser um objeto na raiz; veio {type(obj).__name__}."
                )
            return _normalizar_objeto_transcricao_json_parseado(obj)
    for bloco in blocos:
        recuperado = _extrair_objeto_transcricao_de_json_possivelmente_truncado(bloco)
        if recuperado is not None:
            return recuperado
    trecho = recortado[:900] + ("…" if len(recortado) > 900 else "")
    msg_extra = f" ({ultimo_erro!s})" if ultimo_erro else ""
    raise ValueError(
        "Não foi possível interpretar o JSON retornado pelo modelo de transcrição"
        f"{msg_extra}. Trecho: {trecho}"
    )


def _normalizar_objeto_transcricao_json_parseado(obj: dict) -> dict:
    """Sanitiza segmentos após parse bem-sucedido (repetição lexical, tipos)."""
    raw_segs = obj.get("segmentos")
    if not isinstance(raw_segs, list):
        return obj
    limpos: list[dict[str, Any]] = []
    for s in raw_segs:
        if not isinstance(s, dict):
            continue
        try:
            ini = float(s.get("inicio_segundos", 0.0) or 0.0)
            fim = float(s.get("fim_segundos", ini) or ini)
        except (TypeError, ValueError):
            continue
        tx = _colapsar_repeticao_palavra_consecutiva_em_texto_segmento_transcricao(
            str(s.get("texto", "") or "").strip()
        )
        if tx:
            limpos.append(
                {"inicio_segundos": ini, "fim_segundos": max(ini, fim), "texto": tx}
            )
    out = dict(obj)
    out["segmentos"] = limpos
    return out


def _http_indica_rejeicao_response_format_json_object(http: httpx.Response) -> bool:
    """Alguns proxies/modelos rejeitam `response_format`; nesse caso repetimos o POST sem o campo."""
    if http.status_code not in (400, 422):
        return False
    t = (http.text or "").lower()
    for needle in (
        "response_format",
        "json_object",
        "json schema",
        "json_schema",
        "json mode",
        "response format",
        "invalid_parameter",
        "unknown parameter",
    ):
        if needle in t:
            return True
    return False


def _trecho_corpo_http_gateway_para_mensagem_erro_transcricao_multimodal(corpo: str, lim: int = 400) -> str:
    """Evita poluir o log/UI com HTML inteiro do nginx; tenta extrair o título."""
    t = (corpo or "").strip()
    if not t:
        return "(corpo vazio)"
    low = t.lower()
    if "<html" in low or "<!doctype" in low:
        m = re.search(r"<title>\s*([^<]+?)\s*</title>", t, re.IGNORECASE | re.DOTALL)
        if m:
            return f"[resposta HTML do proxy] {m.group(1).strip()}"
        return "[resposta HTML do proxy; típico de timeout nginx — ver proxy_read_timeout]"
    if len(t) <= lim:
        return t
    return t[:lim] + "…"


def _mensagem_runtime_erro_http_gateway_transcricao_multimodal(
    *,
    status_code: int,
    url: str,
    corpo: str,
    httpx_timeout_read_segundos: float,
) -> str:
    trecho = _trecho_corpo_http_gateway_para_mensagem_erro_transcricao_multimodal(corpo, lim=600)
    tr = max(60.0, float(httpx_timeout_read_segundos))
    if status_code == 504:
        return (
            "HTTP 504 Gateway Time-out: o nginx (ou outro proxy na frente do LiteLLM) encerrou a conexão porque o "
            "upstream não respondeu a tempo — em geral **não** é o timeout do cliente Python httpx "
            f"(leitura configurada em ~{tr:.0f}s no backend). "
            "Ajuste no proxy: `proxy_read_timeout`, `proxy_send_timeout` (e equivalentes) para um valor maior que o "
            "pior tempo de resposta do modelo; confira também timeouts do LiteLLM e do provedor do modelo. "
            "No Transcribrothers: reduza `TRANSCRICAO_MULTIMODAL_JANELA_SEGUNDOS` (ou na gaveta) para trechos menores "
            "e/ou `TRANSCRICAO_MULTIMODAL_JANELAS_PARALELAS_MAXIMA` para menos carga simultânea. "
            f"URL: {url}. Resumo do corpo: {trecho}"
        )
    if status_code == 502:
        return (
            "HTTP 502 Bad Gateway: o proxy não obteve resposta válida do upstream (LiteLLM fora do ar, reset de "
            f"conexão ou erro transitório). URL: {url}. Resumo: {trecho}"
        )
    if status_code == 503:
        return (
            "HTTP 503 Service Unavailable: upstream sobrecarregado ou em manutenção. "
            f"URL: {url}. Resumo: {trecho}"
        )
    return (
        f"Gateway de transcrição retornou HTTP {status_code}. URL: {url}. Corpo (trecho): {trecho}"
    )


class TranscriberLiteLLmMultimodalAudioJsonSegmentos:
    """Transcrição por áudio no chat contra o proxy LiteLLM (POST /v1/chat/completions), com saída JSON."""

    def __init__(
        self,
        *,
        model: str,
        api_key: str,
        api_base: str | None,
        httpx_verify: bool | str = True,
        httpx_timeout_connect_segundos: float = 120.0,
        httpx_timeout_read_segundos: float = 7200.0,
        usar_response_format_json_object: bool = True,
        formato_input_audio_inline: str = "wav",
    ) -> None:
        if not model.strip():
            raise ValueError("Modelo de transcrição multimodal é obrigatório.")
        if not (api_key or "").strip():
            raise ValueError("Chave API (LITELLM_API_KEY) é obrigatória para transcrição multimodal.")
        base = (api_base or "").strip()
        if not base:
            raise ValueError(
                "LITELLM_ENDPOINT é obrigatório para transcrição multimodal: "
                "o envio usa POST /v1/chat/completions no seu LiteLLM proxy."
            )
        self._model = model.strip()
        self._api_key = api_key.strip()
        base_v1 = normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1(base)
        if not base_v1:
            raise ValueError("Endpoint inválido após normalização (LITELLM_ENDPOINT).")
        self._url_chat_completions = f"{base_v1}/chat/completions"
        self._httpx_verify = httpx_verify
        self._httpx_timeout = httpx.Timeout(
            connect=max(5.0, float(httpx_timeout_connect_segundos)),
            read=max(60.0, float(httpx_timeout_read_segundos)),
            write=max(60.0, float(httpx_timeout_read_segundos)),
            pool=max(5.0, float(httpx_timeout_connect_segundos)),
        )
        self._httpx_timeout_read_segundos = max(60.0, float(httpx_timeout_read_segundos))
        self._usar_response_format_json_object = bool(usar_response_format_json_object)
        fmt = str(formato_input_audio_inline or "wav").strip().lower()
        self._formato_input_audio_inline = fmt if fmt in ("wav", "mp3", "opus", "aac") else "wav"

    async def transcrever_arquivo_audio_com_segmentos(
        self,
        caminho_audio: Path,
    ) -> ResultadoTranscricaoComSegmentos:
        def _ler_arquivo_e_base64() -> str:
            dados = caminho_audio.read_bytes()
            return base64.standard_b64encode(dados).decode("ascii")

        # Evita bloquear o event loop: com vários trechos em paralelo, read+I/O+base64 grandes
        # atrasavam o início dos POSTs uns dos outros (não serializa o HTTP, mas atrasa o overlap).
        b64 = await asyncio.to_thread(_ler_arquivo_e_base64)
        audio_part = {
            "type": "input_audio",
            "input_audio": {
                "data": b64,
                "format": self._formato_input_audio_inline,
            },
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        obj: dict[str, Any] | None = None
        ultimo_erro_parse: ValueError | None = None
        async with httpx.AsyncClient(timeout=self._httpx_timeout, verify=self._httpx_verify) as client:
            for tentativa in range(_MAX_TENTATIVAS_HTTP_TRANSCRICAO_JSON):
                prompt = (
                    _PROMPT_TRANSCRICAO_JSON_PT
                    if tentativa == 0
                    else _PROMPT_TRANSCRICAO_JSON_RETRY_PT
                )
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            audio_part,
                        ],
                    }
                ]
                payload_base: dict[str, Any] = {
                    "model": self._model,
                    "messages": messages,
                    "temperature": 0.05 if tentativa else 0.1,
                    "max_tokens": 32768,
                }
                if self._usar_response_format_json_object:
                    http = await client.post(
                        self._url_chat_completions,
                        headers=headers,
                        json={**payload_base, "response_format": {"type": "json_object"}},
                    )
                    if not http.is_success and _http_indica_rejeicao_response_format_json_object(http):
                        http = await client.post(
                            self._url_chat_completions,
                            headers=headers,
                            json=payload_base,
                        )
                else:
                    http = await client.post(
                        self._url_chat_completions,
                        headers=headers,
                        json=payload_base,
                    )
                if not http.is_success:
                    corpo = http.text or ""
                    raise RuntimeError(
                        _mensagem_runtime_erro_http_gateway_transcricao_multimodal(
                            status_code=http.status_code,
                            url=self._url_chat_completions,
                            corpo=corpo,
                            httpx_timeout_read_segundos=self._httpx_timeout_read_segundos,
                        )
                    )
                body = http.json()
                try:
                    choice = body["choices"][0]
                    msg = choice["message"]
                    conteudo = msg.get("content", "")
                    finish_reason = choice.get("finish_reason")
                except (KeyError, IndexError, TypeError) as exc:
                    raise RuntimeError(
                        f"Resposta inesperada do gateway de transcrição (JSON sem choices[0].message): {body!r}"
                    ) from exc
                if not isinstance(conteudo, str) or not conteudo.strip():
                    raise RuntimeError("Modelo multimodal retornou conteúdo vazio na transcrição.")
                try:
                    obj = _extrair_json_do_texto_resposta_llm(conteudo)
                    break
                except ValueError as exc:
                    ultimo_erro_parse = exc
                    if tentativa + 1 >= _MAX_TENTATIVAS_HTTP_TRANSCRICAO_JSON:
                        raise
                    if finish_reason not in ("length", "max_tokens", None):
                        # JSON inválido sem corte por tamanho: ainda vale nova tentativa com prompt restrito.
                        pass
        if obj is None:
            raise ultimo_erro_parse or ValueError("Falha ao interpretar JSON da transcrição.")
        idioma = str(obj.get("idioma") or "pt") if isinstance(obj.get("idioma"), str) else None
        raw_segs = obj.get("segmentos") or []
        segmentos: list[SegmentoTranscricaoComTempo] = []
        if isinstance(raw_segs, list):
            for s in raw_segs:
                if not isinstance(s, dict):
                    continue
                try:
                    ini = float(s.get("inicio_segundos", 0.0) or 0.0)
                    fim = float(s.get("fim_segundos", ini) or ini)
                    tx = str(s.get("texto", "") or "").strip()
                except (TypeError, ValueError):
                    continue
                if tx:
                    segmentos.append(
                        SegmentoTranscricaoComTempo(
                            inicio_segundos=max(0.0, ini),
                            fim_segundos=max(ini, fim),
                            texto=tx,
                        )
                    )
        texto_completo = " ".join(s.texto for s in segmentos).strip()
        if not segmentos:
            texto_completo = str(obj.get("texto_completo") or conteudo).strip() or conteudo.strip()
            segmentos.append(
                SegmentoTranscricaoComTempo(
                    inicio_segundos=0.0,
                    fim_segundos=0.0,
                    texto=texto_completo,
                )
            )
        return ResultadoTranscricaoComSegmentos(
            texto_completo=texto_completo,
            segmentos=segmentos,
            idioma_detectado=idioma,
        )
