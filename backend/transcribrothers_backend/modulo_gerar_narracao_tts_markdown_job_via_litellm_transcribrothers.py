"""Gera WAV de narração TTS a partir de texto plano via proxy LiteLLM (Gemini TTS)."""

from __future__ import annotations

import asyncio
import base64
import wave
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import httpx

from transcribrothers_backend.modulo_configuracao_ambiente_transcribrothers import (
    ConfiguracaoAmbienteTranscribrothers,
)
from transcribrothers_backend.modulo_resolver_credenciais_e_modelo_litellm_transcribrothers import (
    listar_modelos_litellm_provisionados_para_interface,
    normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1,
    resolver_api_key_e_api_base_para_chamada_litellm,
    resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm,
)
from transcribrothers_backend.modulo_util_filtrar_trechos_narraveis_para_tts_transcribrothers import (
    filtrar_trechos_narraveis_para_tts_transcribrothers,
    preview_trecho_tts_para_progresso_ui_transcribrothers,
    texto_e_narravel_para_tts_transcribrothers,
)
from transcribrothers_backend.modulo_verificar_modelo_litellm_chat_completions_probe_transcribrothers import (
    modelo_litellm_parece_tts_pelo_slug_transcribrothers,
)

NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS = "narracao_tts_documento.wav"
CHAVE_STEPS_JSON_NARRACAO_TTS_TRANSCRIBROTHERS = "narracao_tts_documento"

_TTS_VOICE = "Kore"
_TTS_AUDIO_FORMAT = "pcm16"
_TTS_SAMPLE_RATE_HZ = 24000
_TTS_TIMEOUT_CONNECT_SEGUNDOS = 15.0
_TTS_TIMEOUT_READ_SEGUNDOS = 180.0
# Limite pragmático do MVP (um único pedido); textos maiores são truncados com aviso.
_TTS_MAX_CHARS_TEXTO = 3500
_TTS_MAX_CHARS_CHUNK_PIPELINE = 3000
# Pipeline vídeo narrado: um pedido por cue/trecho curto (Gemini tende a truncar blobs longos).
_TTS_MAX_CHARS_TRECHO_CUE_PIPELINE = 400
_TTS_SEGUNDOS_MINIMOS_POR_CHAR = 0.035
_TTS_DURACAO_WAV_MINIMA_ABSOLUTA_SEGUNDOS = 2.0
# Gemini TTS preview às vezes devolve choices vazio; retry + prompt mínimo ajudam.
_TTS_MAX_TENTATIVAS_POR_TRECHO = 3
_TTS_BACKOFF_BASE_ENTRE_TENTATIVAS_SEGUNDOS = 0.7
_TTS_PAUSA_ENTRE_TRECHOS_SEGUNDOS = 0.35
_TTS_SILENCIO_CUE_PULADA_SEGUNDOS = 0.35
_TTS_FRACAO_MAXIMA_CUES_PULADAS = 0.4
# Pedidos TTS ao proxy em paralelo (evita 429; 3 costuma equilibrar velocidade vs rate limit).
_TTS_PARALELISMO_CUES = 3

AtualizarProgressoNarracaoTtsCueTranscribrothers = Callable[[dict[str, Any]], Awaitable[None]]


class ErroTtsRespostaVaziaRetryavelTranscribrothers(RuntimeError):
    """Falha transitória de TTS (choices vazio, HTTP 5xx/429) — vale tentar de novo ou pular a cue."""


def _http_status_proxy_tts_e_retryavel_transcribrothers(status_code: int) -> bool:
    """429 (rate limit) e 5xx do proxy/Gemini costumam ser intermitentes."""
    code = int(status_code)
    return code == 429 or code >= 500


def _pcm16_silencio_mono_segundos_transcribrothers(
    segundos: float,
    *,
    sample_rate_hz: int = _TTS_SAMPLE_RATE_HZ,
) -> bytes:
    n_frames = max(1, int(round(max(0.05, float(segundos)) * int(sample_rate_hz))))
    return b"\x00\x00" * n_frames


@dataclass(frozen=True)
class ResultadoNarracaoTtsWavTranscribrothers:
    ok: bool
    mensagem: str
    nome_arquivo: str = NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS
    modelo: str = ""
    texto_caracteres: int = 0
    texto_truncado: bool = False
    quantidade_chunks: int = 1


def partir_texto_em_chunks_para_narracao_tts_transcribrothers(
    texto: str,
    *,
    max_chars: int = _TTS_MAX_CHARS_CHUNK_PIPELINE,
) -> list[str]:
    """Quebra texto longo em trechos ≤ max_chars, preferindo limites de frase/espaço."""
    bruto = (texto or "").strip()
    if not bruto:
        return []
    if len(bruto) <= max_chars:
        return [bruto]
    chunks: list[str] = []
    resto = bruto
    while resto:
        if len(resto) <= max_chars:
            chunks.append(resto)
            break
        janela = resto[:max_chars]
        corte = max(janela.rfind(". "), janela.rfind("! "), janela.rfind("? "), janela.rfind("\n"))
        if corte < max_chars // 3:
            corte = janela.rfind(" ")
        if corte < 1:
            corte = max_chars
        else:
            corte = corte + 1
        pedaco = resto[:corte].strip()
        if pedaco:
            chunks.append(pedaco)
        resto = resto[corte:].strip()
    return chunks


def resolver_modelo_tts_para_narracao_documento_transcribrothers(
    cfg: ConfiguracaoAmbienteTranscribrothers,
    modelo_solicitado: str | None,
) -> str:
    """Usa o modelo pedido se for TTS; senão o primeiro provisionado com -tts; senão LITELLM_MODEL se TTS."""
    pedido = (modelo_solicitado or "").strip()
    if pedido:
        if not modelo_litellm_parece_tts_pelo_slug_transcribrothers(pedido):
            raise ValueError(
                f"O modelo «{pedido}» não parece TTS (slug sem -tts). "
                "Escolha um modelo como gemini/gemini-2.5-flash-preview-tts."
            )
        return pedido
    for m in listar_modelos_litellm_provisionados_para_interface(cfg):
        if modelo_litellm_parece_tts_pelo_slug_transcribrothers(m):
            return m
    padrao = (cfg.litellm_model or "").strip()
    if modelo_litellm_parece_tts_pelo_slug_transcribrothers(padrao):
        return padrao
    raise ValueError(
        "Nenhum modelo TTS configurado. Informe um modelo com -tts no pedido "
        "ou inclua um na lista LITELLM_MODELOS_PROVISIONADOS."
    )


def _gravar_pcm16_mono_como_wav_transcribrothers(
    caminho_wav: Path,
    pcm_bytes: bytes,
    *,
    sample_rate_hz: int = _TTS_SAMPLE_RATE_HZ,
) -> None:
    caminho_wav.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(caminho_wav), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(int(sample_rate_hz))
        wf.writeframes(pcm_bytes)


def _extrair_pcm16_base64_da_mensagem_chat_tts_transcribrothers(message: dict[str, Any]) -> bytes:
    audio = message.get("audio")
    if isinstance(audio, dict):
        data = audio.get("data")
        if isinstance(data, str) and data.strip():
            return base64.b64decode(data.strip())
    conteudo = message.get("content")
    if isinstance(conteudo, list):
        for parte in conteudo:
            if not isinstance(parte, dict):
                continue
            inline = parte.get("inline_data") or parte.get("inlineData")
            if isinstance(inline, dict) and isinstance(inline.get("data"), str):
                mime = str(inline.get("mime_type") or inline.get("mimeType") or "").lower()
                if mime.startswith("audio/") or not mime:
                    return base64.b64decode(inline["data"].strip())
            data = parte.get("data")
            if isinstance(data, str) and data.strip() and "audio" in str(parte.get("type") or "").lower():
                return base64.b64decode(data.strip())
    raise ValueError("Resposta TTS sem payload de áudio pcm16 (base64).")


async def _sintetizar_pcm16_trecho_tts_via_litellm_transcribrothers(
    *,
    texto: str,
    modelo: str,
    api_key: str,
    base_v1: str,
    httpx_verify: bool | str,
    voz: str,
) -> bytes:
    """Uma tentativa: prompt = só o texto a narrar (modelo TTS costuma falhar com instruções longas)."""
    texto_narrar = (texto or "").strip()
    if not texto_narrar:
        raise ValueError("Trecho TTS vazio.")
    url_chat = f"{base_v1}/chat/completions"
    corpo = {
        "model": modelo,
        # Prompt mínimo: Gemini TTS responde melhor com o texto puro a ser falado.
        "messages": [{"role": "user", "content": texto_narrar}],
        "modalities": ["audio"],
        "audio": {"voice": (voz or _TTS_VOICE).strip() or _TTS_VOICE, "format": _TTS_AUDIO_FORMAT},
        "allowed_openai_params": ["audio", "modalities"],
        "temperature": 0.4,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    timeout = httpx.Timeout(
        connect=_TTS_TIMEOUT_CONNECT_SEGUNDOS,
        read=_TTS_TIMEOUT_READ_SEGUNDOS,
        write=_TTS_TIMEOUT_READ_SEGUNDOS,
        pool=_TTS_TIMEOUT_CONNECT_SEGUNDOS,
    )
    async with httpx.AsyncClient(timeout=timeout, verify=httpx_verify) as client:
        http = await client.post(url_chat, headers=headers, json=corpo)
    if http.status_code >= 400:
        trecho = (http.text or "").strip().replace("\n", " ")[:400]
        msg = (
            f"Proxy rejeitou a narração TTS (HTTP {http.status_code})"
            + (f" — {trecho}" if trecho else "")
        )
        if _http_status_proxy_tts_e_retryavel_transcribrothers(http.status_code):
            raise ErroTtsRespostaVaziaRetryavelTranscribrothers(msg)
        raise RuntimeError(msg)
    try:
        body = http.json()
    except ValueError as exc:
        raise RuntimeError(
            f"Resposta TTS não é JSON válido (HTTP {http.status_code})."
        ) from exc
    if not isinstance(body, dict):
        raise RuntimeError("Resposta TTS inválida (corpo não é objeto JSON).")
    choices = body.get("choices")
    if not isinstance(choices, list) or not choices:
        preview = (http.text or "").strip().replace("\n", " ")[:280]
        raise ErroTtsRespostaVaziaRetryavelTranscribrothers(
            "Resposta TTS sem choices (proxy/modelo devolveu lista vazia ou ausente)."
            + (f" Corpo: {preview}" if preview else "")
        )
    first = choices[0]
    if not isinstance(first, dict):
        raise RuntimeError("Resposta TTS com choice inválida.")
    message = first.get("message")
    if not isinstance(message, dict):
        raise ErroTtsRespostaVaziaRetryavelTranscribrothers("Resposta TTS sem message na choice.")
    try:
        pcm = _extrair_pcm16_base64_da_mensagem_chat_tts_transcribrothers(message)
    except ValueError as exc:
        raise ErroTtsRespostaVaziaRetryavelTranscribrothers(str(exc)) from exc
    if not pcm:
        raise ErroTtsRespostaVaziaRetryavelTranscribrothers("Áudio TTS vazio.")
    return pcm


async def _sintetizar_pcm16_trecho_tts_com_retry_via_litellm_transcribrothers(
    *,
    texto: str,
    modelo: str,
    api_key: str,
    base_v1: str,
    httpx_verify: bool | str,
    voz: str,
    max_tentativas: int = _TTS_MAX_TENTATIVAS_POR_TRECHO,
) -> bytes:
    """Retry com backoff em choices vazio, HTTP 5xx/429 e timeout."""
    tentativas = max(1, int(max_tentativas))
    ultimo_erro: Exception | None = None
    for tentativa in range(1, tentativas + 1):
        try:
            return await _sintetizar_pcm16_trecho_tts_via_litellm_transcribrothers(
                texto=texto,
                modelo=modelo,
                api_key=api_key,
                base_v1=base_v1,
                httpx_verify=httpx_verify,
                voz=voz,
            )
        except ErroTtsRespostaVaziaRetryavelTranscribrothers as exc:
            ultimo_erro = exc
            if tentativa >= tentativas:
                break
            await asyncio.sleep(_TTS_BACKOFF_BASE_ENTRE_TENTATIVAS_SEGUNDOS * tentativa)
        except httpx.TimeoutException as exc:
            ultimo_erro = exc
            if tentativa >= tentativas:
                break
            await asyncio.sleep(_TTS_BACKOFF_BASE_ENTRE_TENTATIVAS_SEGUNDOS * tentativa)
    assert ultimo_erro is not None
    if isinstance(ultimo_erro, httpx.TimeoutException):
        raise ultimo_erro
    if isinstance(ultimo_erro, ErroTtsRespostaVaziaRetryavelTranscribrothers):
        raise ErroTtsRespostaVaziaRetryavelTranscribrothers(
            f"Após {tentativas} tentativa(s): {ultimo_erro}"
        ) from ultimo_erro
    raise RuntimeError(
        f"Após {tentativas} tentativa(s): {ultimo_erro}"
    ) from ultimo_erro


async def gerar_narracao_tts_wav_a_partir_texto_plano_via_litellm_transcribrothers(
    *,
    texto_plano: str,
    modelo: str,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    caminho_wav_saida: Path,
    voz: str = _TTS_VOICE,
) -> ResultadoNarracaoTtsWavTranscribrothers:
    """MVP avulso: um pedido; trunca em `_TTS_MAX_CHARS_TEXTO` se necessário."""
    texto = (texto_plano or "").strip()
    if not texto:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem="Não há texto narrável no documento (Markdown vazio após limpeza).",
            modelo=(modelo or "").strip(),
        )

    truncado = False
    if len(texto) > _TTS_MAX_CHARS_TEXTO:
        texto = texto[:_TTS_MAX_CHARS_TEXTO].rsplit(" ", 1)[0].strip() or texto[:_TTS_MAX_CHARS_TEXTO]
        truncado = True

    modelo_norm = (modelo or "").strip()
    if not modelo_norm:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem="Informe o modelo TTS.",
        )

    api_key, api_base = resolver_api_key_e_api_base_para_chamada_litellm(configuracao)
    if not api_key or not api_base:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem="Proxy LiteLLM não configurado (LITELLM_API_KEY e LITELLM_ENDPOINT).",
            modelo=modelo_norm,
            texto_caracteres=len(texto),
            texto_truncado=truncado,
        )

    base_v1 = normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1(api_base)
    if not base_v1:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem="LITELLM_ENDPOINT inválido.",
            modelo=modelo_norm,
            texto_caracteres=len(texto),
            texto_truncado=truncado,
        )

    httpx_verify = resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(configuracao)
    try:
        pcm = await _sintetizar_pcm16_trecho_tts_com_retry_via_litellm_transcribrothers(
            texto=texto,
            modelo=modelo_norm,
            api_key=api_key,
            base_v1=base_v1,
            httpx_verify=httpx_verify,
            voz=voz,
        )
    except httpx.TimeoutException:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem=f"Tempo esgotado na narração TTS (limite {_TTS_TIMEOUT_READ_SEGUNDOS:.0f}s).",
            modelo=modelo_norm,
            texto_caracteres=len(texto),
            texto_truncado=truncado,
        )
    except httpx.HTTPError as exc:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem=f"Falha de rede no proxy TTS: {exc}",
            modelo=modelo_norm,
            texto_caracteres=len(texto),
            texto_truncado=truncado,
        )
    except (RuntimeError, KeyError, IndexError, TypeError, ValueError) as exc:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem=str(exc),
            modelo=modelo_norm,
            texto_caracteres=len(texto),
            texto_truncado=truncado,
        )

    _gravar_pcm16_mono_como_wav_transcribrothers(caminho_wav_saida, pcm)
    msg = "Narração TTS gerada com sucesso."
    if truncado:
        msg += f" Texto truncado em {_TTS_MAX_CHARS_TEXTO} caracteres (MVP)."
    return ResultadoNarracaoTtsWavTranscribrothers(
        ok=True,
        mensagem=msg,
        nome_arquivo=caminho_wav_saida.name,
        modelo=modelo_norm,
        texto_caracteres=len(texto),
        texto_truncado=truncado,
        quantidade_chunks=1,
    )


async def gerar_narracao_tts_wav_em_chunks_concatenados_via_litellm_transcribrothers(
    *,
    texto_plano: str,
    modelo: str,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    caminho_wav_saida: Path,
    voz: str = _TTS_VOICE,
    max_chars_chunk: int = _TTS_MAX_CHARS_CHUNK_PIPELINE,
) -> ResultadoNarracaoTtsWavTranscribrothers:
    """Pipeline vídeo narrado: narra todos os trechos e concatena PCM num único WAV."""
    texto = (texto_plano or "").strip()
    if not texto:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem="Não há texto narrável no documento (Markdown vazio após limpeza).",
            modelo=(modelo or "").strip(),
            quantidade_chunks=0,
        )

    modelo_norm = (modelo or "").strip()
    if not modelo_norm:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem="Informe o modelo TTS.",
            quantidade_chunks=0,
        )

    api_key, api_base = resolver_api_key_e_api_base_para_chamada_litellm(configuracao)
    if not api_key or not api_base:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem="Proxy LiteLLM não configurado (LITELLM_API_KEY e LITELLM_ENDPOINT).",
            modelo=modelo_norm,
            texto_caracteres=len(texto),
            quantidade_chunks=0,
        )
    base_v1 = normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1(api_base)
    if not base_v1:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem="LITELLM_ENDPOINT inválido.",
            modelo=modelo_norm,
            texto_caracteres=len(texto),
            quantidade_chunks=0,
        )

    chunks = partir_texto_em_chunks_para_narracao_tts_transcribrothers(texto, max_chars=max_chars_chunk)
    httpx_verify = resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(configuracao)
    pcm_total = bytearray()
    try:
        for i, trecho in enumerate(chunks):
            if i > 0 and _TTS_PAUSA_ENTRE_TRECHOS_SEGUNDOS > 0:
                await asyncio.sleep(_TTS_PAUSA_ENTRE_TRECHOS_SEGUNDOS)
            pcm = await _sintetizar_pcm16_trecho_tts_com_retry_via_litellm_transcribrothers(
                texto=trecho,
                modelo=modelo_norm,
                api_key=api_key,
                base_v1=base_v1,
                httpx_verify=httpx_verify,
                voz=voz,
            )
            pcm_total.extend(pcm)
    except httpx.TimeoutException:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem=f"Tempo esgotado na narração TTS (limite {_TTS_TIMEOUT_READ_SEGUNDOS:.0f}s).",
            modelo=modelo_norm,
            texto_caracteres=len(texto),
            quantidade_chunks=len(chunks),
        )
    except httpx.HTTPError as exc:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem=f"Falha de rede no proxy TTS: {exc}",
            modelo=modelo_norm,
            texto_caracteres=len(texto),
            quantidade_chunks=len(chunks),
        )
    except (RuntimeError, KeyError, IndexError, TypeError, ValueError) as exc:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem=str(exc),
            modelo=modelo_norm,
            texto_caracteres=len(texto),
            quantidade_chunks=len(chunks),
        )

    _gravar_pcm16_mono_como_wav_transcribrothers(caminho_wav_saida, bytes(pcm_total))
    return ResultadoNarracaoTtsWavTranscribrothers(
        ok=True,
        mensagem=f"Narração TTS gerada em {len(chunks)} trecho(s) concatenado(s).",
        nome_arquivo=caminho_wav_saida.name,
        modelo=modelo_norm,
        texto_caracteres=len(texto),
        texto_truncado=False,
        quantidade_chunks=len(chunks),
    )


def expandir_trechos_cues_para_narracao_tts_respeitando_limite_chars_transcribrothers(
    trechos: list[str],
    *,
    max_chars: int = _TTS_MAX_CHARS_TRECHO_CUE_PIPELINE,
) -> list[str]:
    """Expande lista de cues: trechos longos são partidos; vazios são ignorados."""
    out: list[str] = []
    for bruto in trechos:
        t = (bruto or "").strip()
        if not t:
            continue
        if len(t) <= max_chars:
            out.append(t)
            continue
        out.extend(partir_texto_em_chunks_para_narracao_tts_transcribrothers(t, max_chars=max_chars))
    return out


def obter_duracao_wav_pcm16_mono_segundos_transcribrothers(caminho_wav: Path) -> float:
    with wave.open(str(caminho_wav), "rb") as wf:
        rate = int(wf.getframerate() or 0)
        frames = int(wf.getnframes() or 0)
    if rate <= 0:
        return 0.0
    return float(frames) / float(rate)


def validar_duracao_wav_narracao_compativel_com_texto_transcribrothers(
    *,
    caminho_wav: Path,
    texto_caracteres: int,
) -> str | None:
    """
    Retorna mensagem de erro se o WAV for curto demais para o texto;
    None se a duração for plausível.
    """
    if not caminho_wav.is_file():
        return "Arquivo WAV de narração não encontrado após a síntese."
    dur = obter_duracao_wav_pcm16_mono_segundos_transcribrothers(caminho_wav)
    minimo = max(
        _TTS_DURACAO_WAV_MINIMA_ABSOLUTA_SEGUNDOS,
        _TTS_SEGUNDOS_MINIMOS_POR_CHAR * max(0, int(texto_caracteres)),
    )
    if dur < minimo:
        return (
            f"Narração curta demais para o texto ({dur:.1f}s < {minimo:.1f}s esperados "
            f"para {texto_caracteres} caracteres). "
            "O modelo TTS provavelmente truncou a leitura."
        )
    return None


async def gerar_narracao_tts_wav_a_partir_lista_trechos_via_litellm_transcribrothers(
    *,
    trechos: list[str],
    modelo: str,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    caminho_wav_saida: Path,
    voz: str = _TTS_VOICE,
    max_chars_trecho: int = _TTS_MAX_CHARS_TRECHO_CUE_PIPELINE,
) -> ResultadoNarracaoTtsWavTranscribrothers:
    """Pipeline vídeo narrado: narra cada cue/trecho curto e concatena PCM num único WAV."""
    chunks = expandir_trechos_cues_para_narracao_tts_respeitando_limite_chars_transcribrothers(
        trechos,
        max_chars=max_chars_trecho,
    )
    texto_total = " ".join(chunks)
    if not chunks:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem="Não há trechos narráveis nas legendas alinhadas.",
            modelo=(modelo or "").strip(),
            quantidade_chunks=0,
        )

    modelo_norm = (modelo or "").strip()
    if not modelo_norm:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem="Informe o modelo TTS.",
            quantidade_chunks=0,
        )

    api_key, api_base = resolver_api_key_e_api_base_para_chamada_litellm(configuracao)
    if not api_key or not api_base:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem="Proxy LiteLLM não configurado (LITELLM_API_KEY e LITELLM_ENDPOINT).",
            modelo=modelo_norm,
            texto_caracteres=len(texto_total),
            quantidade_chunks=0,
        )
    base_v1 = normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1(api_base)
    if not base_v1:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem="LITELLM_ENDPOINT inválido.",
            modelo=modelo_norm,
            texto_caracteres=len(texto_total),
            quantidade_chunks=0,
        )

    httpx_verify = resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(configuracao)
    pcm_total = bytearray()
    try:
        for indice, trecho in enumerate(chunks, start=1):
            if indice > 1 and _TTS_PAUSA_ENTRE_TRECHOS_SEGUNDOS > 0:
                await asyncio.sleep(_TTS_PAUSA_ENTRE_TRECHOS_SEGUNDOS)
            try:
                pcm = await _sintetizar_pcm16_trecho_tts_com_retry_via_litellm_transcribrothers(
                    texto=trecho,
                    modelo=modelo_norm,
                    api_key=api_key,
                    base_v1=base_v1,
                    httpx_verify=httpx_verify,
                    voz=voz,
                )
            except (RuntimeError, KeyError, IndexError, TypeError, ValueError) as exc:
                preview = (trecho or "").replace("\n", " ").strip()
                if len(preview) > 80:
                    preview = preview[:80] + "…"
                raise RuntimeError(
                    f"Falha na narração TTS do trecho {indice}/{len(chunks)}"
                    + (f" («{preview}»)" if preview else "")
                    + f": {exc}"
                ) from exc
            pcm_total.extend(pcm)
    except httpx.TimeoutException:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem=f"Tempo esgotado na narração TTS (limite {_TTS_TIMEOUT_READ_SEGUNDOS:.0f}s).",
            modelo=modelo_norm,
            texto_caracteres=len(texto_total),
            quantidade_chunks=len(chunks),
        )
    except httpx.HTTPError as exc:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem=f"Falha de rede no proxy TTS: {exc}",
            modelo=modelo_norm,
            texto_caracteres=len(texto_total),
            quantidade_chunks=len(chunks),
        )
    except (RuntimeError, KeyError, IndexError, TypeError, ValueError) as exc:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem=str(exc),
            modelo=modelo_norm,
            texto_caracteres=len(texto_total),
            quantidade_chunks=len(chunks),
        )

    _gravar_pcm16_mono_como_wav_transcribrothers(caminho_wav_saida, bytes(pcm_total))
    erro_dur = validar_duracao_wav_narracao_compativel_com_texto_transcribrothers(
        caminho_wav=caminho_wav_saida,
        texto_caracteres=len(texto_total),
    )
    if erro_dur:
        return ResultadoNarracaoTtsWavTranscribrothers(
            ok=False,
            mensagem=erro_dur,
            nome_arquivo=caminho_wav_saida.name,
            modelo=modelo_norm,
            texto_caracteres=len(texto_total),
            texto_truncado=False,
            quantidade_chunks=len(chunks),
        )

    return ResultadoNarracaoTtsWavTranscribrothers(
        ok=True,
        mensagem=f"Narração TTS gerada em {len(chunks)} trecho(s) (por cue).",
        nome_arquivo=caminho_wav_saida.name,
        modelo=modelo_norm,
        texto_caracteres=len(texto_total),
        texto_truncado=False,
        quantidade_chunks=len(chunks),
    )


@dataclass(frozen=True)
class ResultadoNarracaoTtsWavsPorCueTranscribrothers:
    ok: bool
    mensagem: str
    nome_arquivo_concatenado: str = NOME_ARQUIVO_NARRACAO_TTS_DOCUMENTO_WAV_TRANSCRIBROTHERS
    caminhos_wav_por_cue: tuple[Path, ...] = ()
    duracoes_por_cue_segundos: tuple[float, ...] = ()
    modelo: str = ""
    texto_caracteres: int = 0
    quantidade_cues: int = 0
    quantidade_pedidos_tts: int = 0
    quantidade_cues_puladas: int = 0
    quantidade_cues_reutilizadas: int = 0
    previews_cues_puladas: tuple[str, ...] = ()
    quantidade_trechos_descartados_antes_tts: int = 0


async def gerar_narracao_tts_wavs_individuais_por_cue_e_concatenar_via_litellm_transcribrothers(
    *,
    trechos: list[str],
    modelo: str,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    diretorio_wavs_por_cue: Path,
    caminho_wav_concatenado: Path,
    voz: str = _TTS_VOICE,
    vozes_por_cue: list[str] | None = None,
    max_chars_trecho: int = _TTS_MAX_CHARS_TRECHO_CUE_PIPELINE,
    atualizar_progresso: AtualizarProgressoNarracaoTtsCueTranscribrothers | None = None,
    indices_a_regenerar: set[int] | frozenset[int] | None = None,
    preservar_indices_da_entrada: bool = False,
) -> ResultadoNarracaoTtsWavsPorCueTranscribrothers:
    """
    Narra cada cue num WAV próprio (para retarget A) e também concatena tudo num WAV único.
    Descarta lixo não narrável; se o modelo devolver choices vazio após retries, pula com silêncio.

    Com `preservar_indices_da_entrada=True` e `indices_a_regenerar`, reutiliza WAVs existentes
    nas cues limpas (índices 0-based na lista de entrada).
    """
    if preservar_indices_da_entrada:
        # Mantém 1:1 com a entrada; vazias/não narráveis viram silêncio no loop (não dropa índice).
        cues_texto = [(t or "").strip() for t in trechos]
        descartados = [
            t
            for t in cues_texto
            if t and not texto_e_narravel_para_tts_transcribrothers(t)
        ]
        if not cues_texto:
            return ResultadoNarracaoTtsWavsPorCueTranscribrothers(
                ok=False,
                mensagem="Lista de cues vazia para narração TTS.",
                modelo=(modelo or "").strip(),
            )
    else:
        cues_texto, descartados = filtrar_trechos_narraveis_para_tts_transcribrothers(
            [(t or "").strip() for t in trechos if (t or "").strip()]
        )
        if not cues_texto:
            return ResultadoNarracaoTtsWavsPorCueTranscribrothers(
                ok=False,
                mensagem="Não há trechos narráveis nas cues (só pontuação/lixo residual?).",
                modelo=(modelo or "").strip(),
                quantidade_trechos_descartados_antes_tts=len(descartados),
            )

    modelo_norm = (modelo or "").strip()
    if not modelo_norm:
        return ResultadoNarracaoTtsWavsPorCueTranscribrothers(
            ok=False,
            mensagem="Informe o modelo TTS.",
            quantidade_trechos_descartados_antes_tts=len(descartados),
        )

    api_key, api_base = resolver_api_key_e_api_base_para_chamada_litellm(configuracao)
    if not api_key or not api_base:
        return ResultadoNarracaoTtsWavsPorCueTranscribrothers(
            ok=False,
            mensagem="Proxy LiteLLM não configurado (LITELLM_API_KEY e LITELLM_ENDPOINT).",
            modelo=modelo_norm,
            texto_caracteres=sum(len(t) for t in cues_texto),
            quantidade_cues=len(cues_texto),
            quantidade_trechos_descartados_antes_tts=len(descartados),
        )
    base_v1 = normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1(api_base)
    if not base_v1:
        return ResultadoNarracaoTtsWavsPorCueTranscribrothers(
            ok=False,
            mensagem="LITELLM_ENDPOINT inválido.",
            modelo=modelo_norm,
            texto_caracteres=sum(len(t) for t in cues_texto),
            quantidade_cues=len(cues_texto),
            quantidade_trechos_descartados_antes_tts=len(descartados),
        )

    diretorio_wavs_por_cue.mkdir(parents=True, exist_ok=True)
    httpx_verify = resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(configuracao)
    caminhos: list[Path | None] = [None] * len(cues_texto)
    duracoes: list[float] = [0.0] * len(cues_texto)
    pedidos = 0
    texto_total_chars = 0
    previews_puladas: list[str] = []
    reutilizadas = 0
    cues_concluidas = 0
    total_cues = len(cues_texto)
    regenerar_todas = indices_a_regenerar is None
    indices_regen = frozenset(indices_a_regenerar or ())
    paralelismo = max(1, int(_TTS_PARALELISMO_CUES))
    semaforo_tts = asyncio.Semaphore(paralelismo)
    lock_estado = asyncio.Lock()
    abortar_demasiadas_puladas: ResultadoNarracaoTtsWavsPorCueTranscribrothers | None = None
    voz_padrao = (voz or _TTS_VOICE).strip() or _TTS_VOICE
    if vozes_por_cue is not None and len(vozes_por_cue) != len(cues_texto):
        return ResultadoNarracaoTtsWavsPorCueTranscribrothers(
            ok=False,
            mensagem=(
                "Lista de vozes por cue não bate com a quantidade de cues "
                f"({len(vozes_por_cue)} vs {len(cues_texto)})."
            ),
            modelo=modelo_norm,
            texto_caracteres=sum(len(t) for t in cues_texto),
            quantidade_cues=len(cues_texto),
            quantidade_trechos_descartados_antes_tts=len(descartados),
        )

    def _voz_da_cue(indice_zero_based: int) -> str:
        if vozes_por_cue is None:
            return voz_padrao
        candidata = str(vozes_por_cue[indice_zero_based] or "").strip()
        return candidata or voz_padrao

    async def _emitir_progresso(
        *,
        indice_cue: int,
        texto_cue: str,
        fase_cue: str,
    ) -> None:
        if atualizar_progresso is None:
            return
        await atualizar_progresso(
            {
                "video_narrado_tts_cue_indice": indice_cue,
                "video_narrado_tts_cue_total": total_cues,
                "video_narrado_tts_cue_preview": preview_trecho_tts_para_progresso_ui_transcribrothers(
                    texto_cue
                ),
                "video_narrado_tts_cue_fase": fase_cue,
                "video_narrado_tts_pedidos_feitos": pedidos,
                "video_narrado_tts_cues_puladas": len(previews_puladas),
                "video_narrado_tts_cues_reutilizadas": reutilizadas,
                "video_narrado_tts_trechos_descartados": len(descartados),
                "video_narrado_tts_paralelismo": paralelismo,
            }
        )

    async def _processar_uma_cue_transcribrothers(indice_cue: int, texto_cue: str) -> None:
        nonlocal pedidos, texto_total_chars, reutilizadas, cues_concluidas
        nonlocal abortar_demasiadas_puladas
        if abortar_demasiadas_puladas is not None:
            return
        idx0 = indice_cue - 1
        caminho_cue = diretorio_wavs_por_cue / f"cue_narracao_{idx0:04d}.wav"
        pode_reutilizar = (
            preservar_indices_da_entrada
            and not regenerar_todas
            and idx0 not in indices_regen
            and caminho_cue.is_file()
        )
        if pode_reutilizar:
            dur = obter_duracao_wav_pcm16_mono_segundos_transcribrothers(caminho_cue)
            if dur > 0.05:
                async with lock_estado:
                    caminhos[idx0] = caminho_cue
                    duracoes[idx0] = dur
                    reutilizadas += 1
                    texto_total_chars += len(texto_cue)
                    cues_concluidas += 1
                    progresso_indice = cues_concluidas
                await _emitir_progresso(
                    indice_cue=progresso_indice,
                    texto_cue=texto_cue,
                    fase_cue="reutilizada",
                )
                return

        # Com preservar_indices: lixo/vazio vira silêncio sem abortar por «demasiadas puladas».
        if preservar_indices_da_entrada and not texto_e_narravel_para_tts_transcribrothers(
            texto_cue
        ):
            pcm_silencio = _pcm16_silencio_mono_segundos_transcribrothers(
                _TTS_SILENCIO_CUE_PULADA_SEGUNDOS
            )
            _gravar_pcm16_mono_como_wav_transcribrothers(caminho_cue, pcm_silencio)
            dur = obter_duracao_wav_pcm16_mono_segundos_transcribrothers(caminho_cue)
            async with lock_estado:
                caminhos[idx0] = caminho_cue
                duracoes[idx0] = dur
                cues_concluidas += 1
                progresso_indice = cues_concluidas
            await _emitir_progresso(
                indice_cue=progresso_indice,
                texto_cue=texto_cue,
                fase_cue="silencio_nao_narravel",
            )
            return

        async with semaforo_tts:
            if abortar_demasiadas_puladas is not None:
                return
            await _emitir_progresso(
                indice_cue=indice_cue,
                texto_cue=texto_cue,
                fase_cue="narrando",
            )
            pedacos = expandir_trechos_cues_para_narracao_tts_respeitando_limite_chars_transcribrothers(
                [texto_cue],
                max_chars=max_chars_trecho,
            )
            pcm_cue = bytearray()
            pulou_cue = False
            pedidos_nesta_cue = 0
            for pedaco in pedacos:
                if abortar_demasiadas_puladas is not None:
                    return
                if not texto_e_narravel_para_tts_transcribrothers(pedaco):
                    continue
                if pedidos_nesta_cue > 0 and _TTS_PAUSA_ENTRE_TRECHOS_SEGUNDOS > 0:
                    await asyncio.sleep(_TTS_PAUSA_ENTRE_TRECHOS_SEGUNDOS)
                async with lock_estado:
                    pedidos += 1
                pedidos_nesta_cue += 1
                try:
                    pcm = await _sintetizar_pcm16_trecho_tts_com_retry_via_litellm_transcribrothers(
                        texto=pedaco,
                        modelo=modelo_norm,
                        api_key=api_key,
                        base_v1=base_v1,
                        httpx_verify=httpx_verify,
                        voz=_voz_da_cue(idx0),
                    )
                except ErroTtsRespostaVaziaRetryavelTranscribrothers:
                    pcm_cue = bytearray(
                        _pcm16_silencio_mono_segundos_transcribrothers(
                            _TTS_SILENCIO_CUE_PULADA_SEGUNDOS
                        )
                    )
                    async with lock_estado:
                        previews_puladas.append(
                            preview_trecho_tts_para_progresso_ui_transcribrothers(texto_cue)
                        )
                    pulou_cue = True
                    break
                except (RuntimeError, KeyError, IndexError, TypeError, ValueError) as exc:
                    preview = preview_trecho_tts_para_progresso_ui_transcribrothers(texto_cue)
                    raise RuntimeError(
                        f"Falha na narração TTS da cue {indice_cue}/{total_cues}"
                        + (f" («{preview}»)" if preview else "")
                        + f": {exc}"
                    ) from exc
                pcm_cue.extend(pcm)

            if not pcm_cue:
                pcm_cue = bytearray(
                    _pcm16_silencio_mono_segundos_transcribrothers(_TTS_SILENCIO_CUE_PULADA_SEGUNDOS)
                )
                if not pulou_cue:
                    async with lock_estado:
                        previews_puladas.append(
                            preview_trecho_tts_para_progresso_ui_transcribrothers(texto_cue)
                        )
                    pulou_cue = True

            _gravar_pcm16_mono_como_wav_transcribrothers(caminho_cue, bytes(pcm_cue))
            dur = obter_duracao_wav_pcm16_mono_segundos_transcribrothers(caminho_cue)
            if not pulou_cue:
                minimo_cue = max(0.25, _TTS_SEGUNDOS_MINIMOS_POR_CHAR * len(texto_cue))
                if dur < minimo_cue:
                    pcm_cue = bytearray(
                        _pcm16_silencio_mono_segundos_transcribrothers(
                            _TTS_SILENCIO_CUE_PULADA_SEGUNDOS
                        )
                    )
                    _gravar_pcm16_mono_como_wav_transcribrothers(caminho_cue, bytes(pcm_cue))
                    dur = obter_duracao_wav_pcm16_mono_segundos_transcribrothers(caminho_cue)
                    async with lock_estado:
                        previews_puladas.append(
                            preview_trecho_tts_para_progresso_ui_transcribrothers(texto_cue)
                        )
                    pulou_cue = True

            async with lock_estado:
                caminhos[idx0] = caminho_cue
                duracoes[idx0] = dur
                if not pulou_cue:
                    texto_total_chars += len(texto_cue)
                cues_concluidas += 1
                progresso_indice = cues_concluidas
                fracao_pulada = len(previews_puladas) / float(total_cues)
                if (
                    abortar_demasiadas_puladas is None
                    and fracao_pulada > _TTS_FRACAO_MAXIMA_CUES_PULADAS
                    and len(previews_puladas) >= 3
                ):
                    abortar_demasiadas_puladas = ResultadoNarracaoTtsWavsPorCueTranscribrothers(
                        ok=False,
                        mensagem=(
                            f"Demasiadas cues sem áudio TTS "
                            f"({len(previews_puladas)}/{total_cues} puladas). "
                            "Verifique o modelo/proxy ou o texto do documento."
                        ),
                        modelo=modelo_norm,
                        texto_caracteres=texto_total_chars,
                        quantidade_cues=total_cues,
                        quantidade_pedidos_tts=pedidos,
                        quantidade_cues_puladas=len(previews_puladas),
                        previews_cues_puladas=tuple(previews_puladas[:12]),
                        quantidade_trechos_descartados_antes_tts=len(descartados),
                    )

            await _emitir_progresso(
                indice_cue=progresso_indice,
                texto_cue=texto_cue,
                fase_cue="pulada" if pulou_cue else "ok",
            )

    try:
        await asyncio.gather(
            *[
                _processar_uma_cue_transcribrothers(indice_cue, texto_cue)
                for indice_cue, texto_cue in enumerate(cues_texto, start=1)
            ]
        )
        if abortar_demasiadas_puladas is not None:
            return abortar_demasiadas_puladas
        if any(c is None for c in caminhos):
            return ResultadoNarracaoTtsWavsPorCueTranscribrothers(
                ok=False,
                mensagem="Narração TTS incompleta: algumas cues não foram geradas.",
                modelo=modelo_norm,
                texto_caracteres=texto_total_chars,
                quantidade_cues=total_cues,
                quantidade_pedidos_tts=pedidos,
                quantidade_cues_puladas=len(previews_puladas),
                previews_cues_puladas=tuple(previews_puladas[:12]),
                quantidade_trechos_descartados_antes_tts=len(descartados),
            )
    except httpx.TimeoutException:
        return ResultadoNarracaoTtsWavsPorCueTranscribrothers(
            ok=False,
            mensagem=f"Tempo esgotado na narração TTS (limite {_TTS_TIMEOUT_READ_SEGUNDOS:.0f}s).",
            modelo=modelo_norm,
            texto_caracteres=texto_total_chars,
            quantidade_cues=total_cues,
            quantidade_pedidos_tts=pedidos,
            quantidade_cues_puladas=len(previews_puladas),
            previews_cues_puladas=tuple(previews_puladas[:12]),
            quantidade_trechos_descartados_antes_tts=len(descartados),
        )
    except httpx.HTTPError as exc:
        return ResultadoNarracaoTtsWavsPorCueTranscribrothers(
            ok=False,
            mensagem=f"Falha de rede no proxy TTS: {exc}",
            modelo=modelo_norm,
            texto_caracteres=texto_total_chars,
            quantidade_cues=total_cues,
            quantidade_pedidos_tts=pedidos,
            quantidade_cues_puladas=len(previews_puladas),
            previews_cues_puladas=tuple(previews_puladas[:12]),
            quantidade_trechos_descartados_antes_tts=len(descartados),
        )
    except (RuntimeError, KeyError, IndexError, TypeError, ValueError) as exc:
        return ResultadoNarracaoTtsWavsPorCueTranscribrothers(
            ok=False,
            mensagem=str(exc),
            modelo=modelo_norm,
            texto_caracteres=texto_total_chars,
            quantidade_cues=total_cues,
            quantidade_pedidos_tts=pedidos,
            quantidade_cues_puladas=len(previews_puladas),
            previews_cues_puladas=tuple(previews_puladas[:12]),
            quantidade_trechos_descartados_antes_tts=len(descartados),
        )

    caminhos_ok = [c for c in caminhos if c is not None]
    # pcm_total: reconstruir a partir dos WAVs gravados para garantir silêncios incluídos
    pcm_total = bytearray()
    for caminho_cue in caminhos_ok:
        with wave.open(str(caminho_cue), "rb") as wf:
            pcm_total.extend(wf.readframes(wf.getnframes()))

    _gravar_pcm16_mono_como_wav_transcribrothers(caminho_wav_concatenado, bytes(pcm_total))
    msg = (
        f"Narração TTS gerada em {total_cues} cue(s) "
        f"({pedidos} pedido(s) ao modelo, paralelismo {paralelismo})."
    )
    if reutilizadas:
        msg += f" {reutilizadas} cue(s) reutilizada(s) sem novo TTS."
    if previews_puladas:
        msg += f" {len(previews_puladas)} cue(s) pulada(s) (silêncio)."
    if descartados:
        msg += f" {len(descartados)} trecho(s) descartado(s) antes do TTS."
    return ResultadoNarracaoTtsWavsPorCueTranscribrothers(
        ok=True,
        mensagem=msg,
        nome_arquivo_concatenado=caminho_wav_concatenado.name,
        caminhos_wav_por_cue=tuple(caminhos_ok),
        duracoes_por_cue_segundos=tuple(duracoes),
        modelo=modelo_norm,
        texto_caracteres=texto_total_chars,
        quantidade_cues=total_cues,
        quantidade_pedidos_tts=pedidos,
        quantidade_cues_puladas=len(previews_puladas),
        quantidade_cues_reutilizadas=reutilizadas,
        previews_cues_puladas=tuple(previews_puladas[:12]),
        quantidade_trechos_descartados_antes_tts=len(descartados),
    )


@dataclass(frozen=True)
class ResultadoPreviewTtsCueNarracaoTranscribrothers:
    ok: bool
    mensagem: str
    caminho_wav: Path | None = None
    modelo: str = ""
    texto_caracteres: int = 0


async def gerar_preview_tts_wav_de_uma_cue_via_litellm_transcribrothers(
    *,
    texto: str,
    modelo: str,
    configuracao: ConfiguracaoAmbienteTranscribrothers,
    caminho_wav_saida: Path,
    voz: str = _TTS_VOICE,
    max_chars_trecho: int = _TTS_MAX_CHARS_TRECHO_CUE_PIPELINE,
) -> ResultadoPreviewTtsCueNarracaoTranscribrothers:
    """Sintetiza só uma cue para prévia na UI (não altera o WAV definitivo da narração)."""
    texto_norm = " ".join((texto or "").split())
    if not texto_norm:
        return ResultadoPreviewTtsCueNarracaoTranscribrothers(
            ok=False,
            mensagem="Informe o texto da cue para a prévia.",
        )
    if not texto_e_narravel_para_tts_transcribrothers(texto_norm):
        return ResultadoPreviewTtsCueNarracaoTranscribrothers(
            ok=False,
            mensagem="Texto sem conteúdo narrável para TTS.",
        )
    modelo_norm = (modelo or "").strip()
    if not modelo_norm:
        return ResultadoPreviewTtsCueNarracaoTranscribrothers(
            ok=False,
            mensagem="Informe o modelo TTS.",
        )
    api_key, api_base = resolver_api_key_e_api_base_para_chamada_litellm(configuracao)
    if not api_key or not api_base:
        return ResultadoPreviewTtsCueNarracaoTranscribrothers(
            ok=False,
            mensagem="Proxy LiteLLM não configurado (LITELLM_API_KEY e LITELLM_ENDPOINT).",
            modelo=modelo_norm,
        )
    base_v1 = normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1(api_base)
    if not base_v1:
        return ResultadoPreviewTtsCueNarracaoTranscribrothers(
            ok=False,
            mensagem="LITELLM_ENDPOINT inválido.",
            modelo=modelo_norm,
        )
    httpx_verify = resolver_parametro_httpx_verify_ssl_para_chamadas_ao_proxy_litellm(configuracao)
    pedacos = expandir_trechos_cues_para_narracao_tts_respeitando_limite_chars_transcribrothers(
        [texto_norm],
        max_chars=max_chars_trecho,
    )
    pcm_cue = bytearray()
    try:
        for pedaco in pedacos:
            if not texto_e_narravel_para_tts_transcribrothers(pedaco):
                continue
            pcm = await _sintetizar_pcm16_trecho_tts_com_retry_via_litellm_transcribrothers(
                texto=pedaco,
                modelo=modelo_norm,
                api_key=api_key,
                base_v1=base_v1,
                httpx_verify=httpx_verify,
                voz=voz,
            )
            pcm_cue.extend(pcm)
    except ErroTtsRespostaVaziaRetryavelTranscribrothers as exc:
        return ResultadoPreviewTtsCueNarracaoTranscribrothers(
            ok=False,
            mensagem=f"Prévia TTS indisponível: {exc}",
            modelo=modelo_norm,
            texto_caracteres=len(texto_norm),
        )
    except (RuntimeError, httpx.HTTPError, httpx.TimeoutException) as exc:
        return ResultadoPreviewTtsCueNarracaoTranscribrothers(
            ok=False,
            mensagem=f"Falha na prévia TTS: {exc}",
            modelo=modelo_norm,
            texto_caracteres=len(texto_norm),
        )
    if not pcm_cue:
        return ResultadoPreviewTtsCueNarracaoTranscribrothers(
            ok=False,
            mensagem="Prévia TTS vazia.",
            modelo=modelo_norm,
            texto_caracteres=len(texto_norm),
        )
    caminho_wav_saida.parent.mkdir(parents=True, exist_ok=True)
    _gravar_pcm16_mono_como_wav_transcribrothers(caminho_wav_saida, bytes(pcm_cue))
    return ResultadoPreviewTtsCueNarracaoTranscribrothers(
        ok=True,
        mensagem="Prévia TTS gerada.",
        caminho_wav=caminho_wav_saida,
        modelo=modelo_norm,
        texto_caracteres=len(texto_norm),
    )
