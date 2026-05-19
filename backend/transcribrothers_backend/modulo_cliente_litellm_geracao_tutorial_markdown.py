from __future__ import annotations

import asyncio
import base64
import json
from dataclasses import asdict
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
from transcribrothers_backend.modulo_util_extrair_caminhos_assets_png_referenciados_no_markdown_tutorial_transcribrothers import (
    montar_rels_tutorial_apenas_imagens_referenciadas_no_markdown_em_ordem_transcribrothers,
)

_LIMITE_TAMANHO_BYTES_POR_PNG_TUTORIAL_TRANSCRIBROTHERS = 20 * 1024 * 1024

_LIMITE_BYTES_INSTRUCAO_PREFIXO_LITELLM_TUTORIAL_CUSTOM_TRANSCRIBROTHERS = 256 * 1024

INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_SEM_IMAGENS_PADRAO_TRANSCRIBROTHERS = """Você é um editor técnico. Você recebe o JSON abaixo com a transcrição (áudio já transcrito),
tempos e a lista `frames` com caminhos relativos dos screenshots que o sistema capturou no disco.

Você NÃO recebe os pixels das imagens — só metadados. Escolha quais screenshots incorporar no tutorial usando
`![](caminho_exato)` conforme frames[].arquivo_relativo_markdown, priorizando passos principais e momentos
citados na transcrição (em geral poucas imagens bastam).

Regras obrigatórias:
1) Comece com um título H1 curto.
2) Organize em passos claros (## e listas quando fizer sentido).
3) Momentos do vídeo: [MM:SS](?t=SEGUNDOS) com SEGUNDOS inteiro ou decimal.
4) Inclua imagens usando caminhos relativos exatamente como em frames[].arquivo_relativo_markdown.
5) Não invente conteúdo que contradiga a transcrição. Se algo estiver ambíguo, diga de forma neutra.
6) Não envolva o tutorial inteiro em um único bloco de código; só Markdown normal.

JSON de entrada:
"""

INSTRUCAO_LITELLM_TUTORIAL_RASCUNHO_SEM_IMAGENS_CAPTURA_FRAMES_SOB_DEMANDA_TRANSCRIBROTHERS = """Você é um editor técnico. Você recebe o JSON abaixo com a transcrição (áudio já transcrito) e tempos por segmento.
A lista `frames` está vazia: ainda NÃO existem screenshots — eles serão capturados depois com base nos momentos que você indicar.

Regras obrigatórias para este rascunho:
1) Comece com um título H1 curto.
2) Organize em passos claros (## e listas quando fizer sentido).
3) Em cada passo que corresponda a um momento do vídeo, use link temporal [MM:SS](?t=SEGUNDOS) com SEGUNDOS inteiro ou decimal.
4) NÃO use `![](assets/....png)` nem invente caminhos de imagem.
5) Use `?t=` nos instantes em que a interface mudar de forma importante; nem todo link temporal vira screenshot — outro passo do pipeline escolhe quais merecem captura.
6) Não invente conteúdo que contradiga a transcrição.
7) Não envolva o tutorial inteiro em um único bloco de código; só Markdown normal.

JSON de entrada:
"""

INSTRUCOES_REVISAO_LITELLM_INCORPORAR_FRAMES_APOS_CAPTURA_SOB_DEMANDA_TRANSCRIBROTHERS = (
    "O bloco «Tutorial Markdown atual» abaixo é um rascunho sem imagens. Produza a versão final completa "
    "incorporando screenshots com `![](caminho_exato)` usando APENAS caminhos de frames[].arquivo_relativo_markdown "
    "(você não recebe os pixels — só metadados e caminhos). "
    "Mantenha o texto útil do rascunho; acrescente imagens onde a UI for importante. "
    "Mantenha links [MM:SS](?t=...) onde ainda fizer sentido."
)

INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_COM_IMAGENS_PADRAO_TRANSCRIBROTHERS = """Você é um editor técnico. Você recebe (1) o JSON abaixo (transcrição e a lista `frames`
dos screenshots anexados a esta mensagem) e (2) as imagens PNG na mesma ordem de `frames`
(primeira imagem = frames[0], etc.).

Use a transcrição, o Markdown atual (se fornecido abaixo) e o que aparece nas imagens. Quando citar rótulos de
botões, menus, títulos de janelas ou textos fixos de UI legíveis no screenshot, reproduza-os na literalidade
entre aspas ou em bloco de citação Markdown, sem parafrasear, salvo se estiver ilegível.

Regras obrigatórias:
1) Comece com um título H1 curto (ou mantenha o foco se for revisão pontual).
2) Organize em passos claros (## e listas quando fizer sentido).
3) Momentos do vídeo: [MM:SS](?t=SEGUNDOS) com SEGUNDOS inteiro ou decimal.
4) Inclua imagens com caminhos exatamente como em frames[].arquivo_relativo_markdown, ex.: ![](assets/arquivo.png).
5) Não invente conteúdo que contradiga a transcrição nem o visível nas imagens.
6) Não envolva o tutorial inteiro em um único bloco de código; só Markdown normal.

JSON de entrada:
"""

INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_SEM_IMAGENS_DOCUMENTO_AUTONOMO_SEM_VIDEO_PADRAO_TRANSCRIBROTHERS = """Você é um editor técnico. O leitor NÃO tem acesso ao vídeo nem deve precisar dele: o tutorial deve ser autocontido e compreensível apenas com o texto e com as imagens que você incluir no Markdown.

Você recebe o JSON abaixo com a transcrição (áudio já transcrito), tempos por segmento na transcrição e a lista `frames` com caminhos relativos dos screenshots no disco. Os tempos no JSON servem só para alinhar fala e passos; não os transforme em atalhos para reproduzir vídeo.

Você NÃO recebe os pixels das imagens — só metadados. Incorpore mais screenshots do que no estilo “acompanhar o vídeo”: use `![](caminho_exato)` com frames[].arquivo_relativo_markdown sempre que uma imagem substituir o que seria óbvio ao assistir (telas de confirmação, formulários, estados da interface, momentos citados na fala mas pouco claros só por texto).

Regras obrigatórias:
1) Comece com um título H1 curto.
2) Organize em passos claros (## e listas). Em cada passo explique contexto, objetivo, o que fazer e o resultado esperado; não pressuponha que o leitor viu ou vai abrir o vídeo.
3) Proibido usar links temporais para vídeo: não escreva `[MM:SS](?t=...)` nem qualquer URL ou query `?t=` que pressuponha reprodução. Não diga “veja no minuto X” como substituto de explicação. Use ordem lógica, títulos de passo e linguagem natural (“em seguida”, “depois de gravar…”).
4) Inclua imagens com caminhos relativos exatamente como em frames[].arquivo_relativo_markdown; junto de cada imagem, texto que descreva o que importa sem depender do vídeo.
5) Não invente conteúdo que contradiga a transcrição. Se algo estiver ambíguo, explique de forma neutra o que é certo e o que é incerto.
6) Não envolva o tutorial inteiro em um único bloco de código; só Markdown normal.

JSON de entrada:
"""

INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_COM_IMAGENS_DOCUMENTO_AUTONOMO_SEM_VIDEO_PADRAO_TRANSCRIBROTHERS = """Você é um editor técnico. O leitor NÃO reproduz o vídeo nem deve precisar dele: o tutorial deve ser autocontido com texto detalhado e imagens.

Você recebe (1) o JSON abaixo (transcrição e a lista `frames` dos screenshots anexados a esta mensagem) e (2) as imagens PNG na mesma ordem de `frames` (primeira imagem = frames[0], etc.). Tempos no JSON são metadados para alinhar fala e UI; não os exponha como atalhos para vídeo.

Use a transcrição, o Markdown atual (se fornecido abaixo) e o que aparece nas imagens. Redija parágrafos explicativos suficientes para quem não tem o vídeo: motivação de cada ação, consequências na UI e verificações (“deve aparecer…”, “se não aparecer…”). Quando citar rótulos de botões, menus, títulos de janelas ou textos fixos de UI legíveis no screenshot, reproduza-os na literalidade entre aspas ou em bloco de citação Markdown, salvo se estiver ilegível.

Regras obrigatórias:
1) Comece com um título H1 curto (ou mantenha o foco se for revisão pontual).
2) Organize em passos claros (## e listas). Cada passo deve bastar sem o vídeo.
3) Proibido links temporais para vídeo: não use `[MM:SS](?t=...)` nem `?t=` nem convites a “pular para o trecho no vídeo”. A explicação tem de substituir totalmente o vídeo.
4) Inclua imagens com caminhos exatamente como em frames[].arquivo_relativo_markdown, ex.: ![](assets/arquivo.png).
5) Não invente conteúdo que contradiga a transcrição nem o visível nas imagens.
6) Não envolva o tutorial inteiro em um único bloco de código; só Markdown normal.

JSON de entrada:
"""


def normalizar_instrucao_prefixo_litellm_tutorial_custom_transcribrothers(
    texto: str | None,
) -> str | None:
    """Devolve texto pronto para prefixar o JSON, ou None se vazio. Garante marcador `JSON de entrada:` e limite."""
    if texto is None:
        return None
    s = texto.replace("\r\n", "\n").strip()
    if not s:
        return None
    raw_bytes = len(s.encode("utf-8"))
    if raw_bytes > _LIMITE_BYTES_INSTRUCAO_PREFIXO_LITELLM_TUTORIAL_CUSTOM_TRANSCRIBROTHERS:
        raise ValueError(
            "Instrução do tutorial muito longa (limite "
            f"{_LIMITE_BYTES_INSTRUCAO_PREFIXO_LITELLM_TUTORIAL_CUSTOM_TRANSCRIBROTHERS // 1024} KiB UTF-8)."
        )
    if "JSON de entrada" not in s:
        s = s.rstrip() + "\n\nJSON de entrada:\n"
    if not s.endswith("\n"):
        s += "\n"
    return s


def resolver_instrucao_prefixo_litellm_para_corpo_user_tutorial_markdown_transcribrothers(
    *,
    usar_visao: bool,
    instrucao_prefixo_litellm_custom: str | None,
) -> str:
    c = normalizar_instrucao_prefixo_litellm_tutorial_custom_transcribrothers(instrucao_prefixo_litellm_custom)
    if c is not None:
        return c
    return (
        INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_COM_IMAGENS_PADRAO_TRANSCRIBROTHERS
        if usar_visao
        else INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_SEM_IMAGENS_PADRAO_TRANSCRIBROTHERS
    )


def _serializar_segmentos(segmentos: list[SegmentoTranscricaoComTempo]) -> list[dict]:
    return [asdict(s) for s in segmentos]


def extrair_texto_resposta_message_openai_compat_transcribrothers(message: dict) -> str:
    """Alguns gateways devolvem `content` string; outros, lista de partes (texto / refusal)."""
    raw = message.get("content", "")
    if isinstance(raw, str):
        return raw
    if isinstance(raw, list):
        partes: list[str] = []
        for item in raw:
            if isinstance(item, str):
                partes.append(item)
            elif isinstance(item, dict):
                if item.get("type") == "text" and isinstance(item.get("text"), str):
                    partes.append(item["text"])
        return "".join(partes)
    return ""


_extrair_texto_resposta_message_openai_compat_transcribrothers = (
    extrair_texto_resposta_message_openai_compat_transcribrothers
)


def _ler_bytes_pngs_assets_em_ordem_dos_rels_sync_transcribrothers(
    diretorio_assets_absoluto: Path,
    caminhos_frames_rel_job: list[tuple[float, str]],
) -> list[bytes]:
    diretorio_assets_absoluto = diretorio_assets_absoluto.resolve()
    if not diretorio_assets_absoluto.is_dir():
        raise RuntimeError(
            "Diretório de assets do tutorial inexistente ou inválido: "
            f"{diretorio_assets_absoluto} (necessário para envio multimodal com screenshots)."
        )
    blobs: list[bytes] = []
    for _t, rel in caminhos_frames_rel_job:
        nome = rel.strip().replace("\\", "/").split("/")[-1]
        if not nome:
            raise RuntimeError(f"Caminho de frame inválido no tutorial: {rel!r}")
        p = diretorio_assets_absoluto / nome
        if not p.is_file():
            raise RuntimeError(f"PNG do tutorial ausente em assets: {p}")
        data = p.read_bytes()
        if len(data) > _LIMITE_TAMANHO_BYTES_POR_PNG_TUTORIAL_TRANSCRIBROTHERS:
            raise RuntimeError(
                f"PNG do tutorial excede {_LIMITE_TAMANHO_BYTES_POR_PNG_TUTORIAL_TRANSCRIBROTHERS // (1024 * 1024)} MiB: {nome}"
            )
        blobs.append(data)
    return blobs


def _resolver_rels_para_anexar_pngs_multimodal_transcribrothers(
    *,
    enviar_screenshots_png_como_imagens_multimodais: bool,
    markdown_para_decidir_quais_pngs_anexar: str | None,
    caminhos_frames_rel_job_completos: list[tuple[float, str]],
    rels_png_anexo_ja_resolvidos: list[tuple[float, str]] | None,
) -> list[tuple[float, str]]:
    if not enviar_screenshots_png_como_imagens_multimodais:
        return []
    if rels_png_anexo_ja_resolvidos is not None:
        return list(rels_png_anexo_ja_resolvidos)
    md = (markdown_para_decidir_quais_pngs_anexar or "").strip()
    if md:
        return montar_rels_tutorial_apenas_imagens_referenciadas_no_markdown_em_ordem_transcribrothers(
            markdown=md,
            rels_completos_com_tempos=caminhos_frames_rel_job_completos,
        )
    return list(caminhos_frames_rel_job_completos)


async def gerar_tutorial_markdown_com_litellm_a_partir_de_transcricao_e_frames(
    *,
    transcricao: ResultadoTranscricaoComSegmentos,
    caminhos_frames_rel_job: list[tuple[float, str]],
    modelo: str,
    api_key: str | None,
    api_base: str | None,
    httpx_verify: bool | str = True,
    instrucoes_revisao_humana: str | None = None,
    httpx_timeout_connect_segundos: float = 120.0,
    httpx_timeout_read_segundos: float = 7200.0,
    diretorio_assets_absoluto: Path | None = None,
    enviar_screenshots_png_como_imagens_multimodais: bool = False,
    markdown_para_decidir_quais_pngs_anexar: str | None = None,
    rels_png_anexo_ja_resolvidos: list[tuple[float, str]] | None = None,
    bloco_markdown_tutorial_atual_para_contexto_em_revisao: str | None = None,
    instrucao_prefixo_litellm_custom: str | None = None,
    steps_para_log_decisoes_ia: dict[str, Any] | None = None,
    log_etapa_geracao_tutorial: str = "geracao_tutorial_markdown",
) -> str:
    """Retorna Markdown com timestamps [mm:ss](?t=segundos) e imagens relativas ./assets/...

    - Geração inicial e final do pipeline (incl. captura sob demanda): use
      `enviar_screenshots_png_como_imagens_multimodais=False` — só texto + JSON (transcrição e lista de frames);
      o modelo não recebe pixels.
    - Regeneração (FAB): `enviar_screenshots_png_como_imagens_multimodais=True` e `rels_png_anexo_ja_resolvidos`
      com a lista já filtrada (Markdown + referências nas instruções, ex. «Figura 2» ou `assets/....png`).
    """
    linhas_frames_completas = [
        {"t_segundos": t, "arquivo_relativo_markdown": rel} for t, rel in caminhos_frames_rel_job
    ]
    rels_anexo = _resolver_rels_para_anexar_pngs_multimodal_transcribrothers(
        enviar_screenshots_png_como_imagens_multimodais=enviar_screenshots_png_como_imagens_multimodais,
        markdown_para_decidir_quais_pngs_anexar=markdown_para_decidir_quais_pngs_anexar,
        caminhos_frames_rel_job_completos=caminhos_frames_rel_job,
        rels_png_anexo_ja_resolvidos=rels_png_anexo_ja_resolvidos,
    )
    usar_visao = bool(rels_anexo) and diretorio_assets_absoluto is not None
    if enviar_screenshots_png_como_imagens_multimodais and rels_anexo and diretorio_assets_absoluto is None:
        raise RuntimeError(
            "diretorio_assets_absoluto é obrigatório quando há screenshots a anexar em multimodal."
        )

    linhas_frames_no_json = (
        [{"t_segundos": t, "arquivo_relativo_markdown": rel} for t, rel in rels_anexo]
        if usar_visao
        else linhas_frames_completas
    )
    payload_json = {
        "texto_completo": transcricao.texto_completo,
        "idioma": transcricao.idioma_detectado,
        "segmentos": _serializar_segmentos(transcricao.segmentos),
        "frames": linhas_frames_no_json,
    }
    instrucao = resolver_instrucao_prefixo_litellm_para_corpo_user_tutorial_markdown_transcribrothers(
        usar_visao=usar_visao,
        instrucao_prefixo_litellm_custom=instrucao_prefixo_litellm_custom,
    )
    prompt = instrucao + json.dumps(payload_json, ensure_ascii=False, indent=2)
    ctx = (bloco_markdown_tutorial_atual_para_contexto_em_revisao or "").strip()
    if ctx:
        prompt += (
            "\n\n---\n## Tutorial Markdown atual (contexto — produza a nova versão completa em Markdown)\n\n"
            + ctx
            + "\n---"
        )
    rev = (instrucoes_revisao_humana or "").strip()
    if rev:
        prompt += (
            "\n\nInstruções adicionais do revisor humano (obedeça quando forem compatíveis com as regras acima):\n"
            + rev
        )

    chave = (api_key or "").strip()
    if not chave:
        raise RuntimeError(
            "Chave do proxy ausente: defina LITELLM_API_KEY no servidor (a mesma credencial que o LiteLLM espera)."
        )

    base_v1 = normalizar_endpoint_litellm_para_base_url_cliente_http_openai_v1(api_base)
    if not base_v1:
        raise RuntimeError(
            "LITELLM_ENDPOINT é obrigatório para gerar o tutorial: o backend só chama o seu proxy LiteLLM "
            "(POST …/v1/chat/completions), não há fallback para outro provedor."
        )
    url_chat = f"{base_v1}/chat/completions"

    if usar_visao:
        assert diretorio_assets_absoluto is not None
        png_blobs = await asyncio.to_thread(
            _ler_bytes_pngs_assets_em_ordem_dos_rels_sync_transcribrothers,
            diretorio_assets_absoluto,
            rels_anexo,
        )
        texto_apos_json = (
            "\n\nAs imagens PNG desta mensagem seguem a ordem de `frames` no JSON acima. "
            "Use um modelo com suporte a visão (multimodal).\n"
            "Se o revisor citar «Figura N», «imagem N» ou «img N», interprete como a N-ésima imagem na ordem em que "
            "cada `![](assets/....png)` aparece pela primeira vez no bloco «Tutorial Markdown atual» acima "
            "(N=1 = primeira dessa ordem). Alinhe com os ficheiros em `frames` pelo campo arquivo_relativo_markdown."
        )
        partes_conteudo: list[dict] = [{"type": "text", "text": prompt + texto_apos_json}]
        for blob in png_blobs:
            b64 = base64.b64encode(blob).decode("ascii")
            partes_conteudo.append(
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{b64}"},
                }
            )
        corpo_user_content: str | list[dict] = partes_conteudo
    else:
        corpo_user_content = prompt

    corpo_requisicao = {
        "model": modelo,
        "messages": [
            {
                "role": "user",
                "content": corpo_user_content,
            }
        ],
        "temperature": 0.3,
    }
    headers = {
        "Authorization": f"Bearer {chave}",
        "Content-Type": "application/json",
    }
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
            f"Geração do tutorial falhou (HTTP {http.status_code}). URL: {url_chat}. Trecho: {trecho}"
        )
    body = http.json()
    try:
        choice = body["choices"][0]["message"]
        conteudo = extrair_texto_resposta_message_openai_compat_transcribrothers(choice)
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(
            f"Resposta inesperada do gateway na geração do tutorial: {body!r}"
        ) from exc
    if not isinstance(conteudo, str) or not conteudo.strip():
        raise RuntimeError("O modelo retornou conteúdo vazio para o tutorial.")
    texto_md = conteudo.strip()
    if steps_para_log_decisoes_ia is not None:
        from transcribrothers_backend.modulo_util_log_decisoes_ia_pipeline_steps_json_transcribrothers import (
            registrar_decisao_ia_em_steps_json_pipeline_transcribrothers,
            resumir_texto_resposta_ia_para_log_decisoes_pipeline_transcribrothers,
        )

        registrar_decisao_ia_em_steps_json_pipeline_transcribrothers(
            steps_para_log_decisoes_ia,
            etapa=log_etapa_geracao_tutorial,
            resumo=resumir_texto_resposta_ia_para_log_decisoes_pipeline_transcribrothers(texto_md),
            detalhe=texto_md[:6000],
            modelo=modelo,
            metadados={
                "com_visao": bool(enviar_screenshots_png_como_imagens_multimodais),
                "total_imagens_anexo": len(rels_anexo) if enviar_screenshots_png_como_imagens_multimodais else 0,
            },
        )
    return texto_md
