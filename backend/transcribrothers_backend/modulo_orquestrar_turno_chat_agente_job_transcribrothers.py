"""Um turno do chat Agente: contexto, LiteLLM, proposta de ferramenta e histórico."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from pathlib import Path

from transcribrothers_backend.modulo_captura_frame_manual_video_tutorial_job_transcribrothers import (
    capturar_frame_manual_video_tutorial_para_assets_do_job_transcribrothers,
)
from transcribrothers_backend.modulo_catalogo_ferramentas_chat_agente_documento_job_transcribrothers import (
    anexar_caminhos_imagens_na_proposta_edicao_parcial_chat_agente_transcribrothers,
    decidir_executar_proposta_resposta_modelo_chat_agente_transcribrothers,
    escolher_propostas_ferramenta_chat_agente_transcribrothers,
    limpar_texto_visivel_se_vier_json_embutido_chat_agente_transcribrothers,
    extrair_caminhos_relativos_de_imagens_historico_chat_agente_transcribrothers,
    parsear_ferramentas_de_texto_resposta_modelo_chat_agente_transcribrothers,
    parsear_flag_executar_resposta_modelo_chat_agente_transcribrothers,
)
from transcribrothers_backend.modulo_detectar_confirmacao_e_instantes_pedido_chat_agente_transcribrothers import (
    extrair_instantes_segundos_mencionados_no_texto_chat_agente_transcribrothers,
    sintetizar_proposta_edicao_parcial_do_texto_agente_transcribrothers,
)
from transcribrothers_backend.modulo_cliente_litellm_chat_completions_texto_simples_em_stream_transcribrothers import (
    obter_texto_bruto_chat_litellm_preferindo_stream_transcribrothers,
)
from transcribrothers_backend.modulo_montar_contexto_chat_ask_markdown_transcricao_e_catalogo_frames_transcribrothers import (
    montar_contexto_chat_ask_documento_job_transcribrothers,
)
from transcribrothers_backend.modulo_orquestrar_turno_chat_ask_job_transcribrothers import (
    ChatAskSemFonteError,
    _AVISO_TELA_CHAT_ASK_NAO_INCLUIDA_TRANSCRIBROTHERS,
    _citacao_para_dict_transcribrothers,
    _imagem_resolvida_para_dict_chat_ask_transcribrothers,
    _ler_caminhos_frames_rel_job_do_snapshot_em_disco_transcribrothers,
    _localizar_video_entrada_chat_ask_transcribrothers,
    _montar_conteudo_usuario_chat_ask_transcribrothers,
)
from transcribrothers_backend.modulo_parse_link_google_drive_para_file_id import (
    formatar_timestamp_segundos_para_mmss,
)
from transcribrothers_backend.modulo_parsear_resposta_json_chat_ask_litellm_transcribrothers import (
    parsear_resposta_json_chat_ask_litellm_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_arquivo_json_snapshot_transcricao_finalizada_job_transcribrothers import (
    carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_historico_chat_ask_agente_documento_job_transcribrothers import (
    ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers,
    anexar_item_historico_chat_ask_agente_no_work_transcribrothers,
    carregar_historico_chat_ask_agente_do_work_transcribrothers,
)
from transcribrothers_backend.modulo_prompt_sistema_chat_agente_ferramentas_documento_job_transcribrothers import (
    montar_prompt_sistema_chat_agente_ferramentas_documento_job_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_imagem_chat_ask_galeria_ou_captura_frame_transcribrothers import (
    resolver_imagens_chat_ask_por_instantes_transcribrothers,
)


def _novo_item_historico_agente_transcribrothers(
    *,
    papel: str,
    texto: str,
    citacoes: list[dict],
    imagens: list[dict],
    proposta_ferramenta: dict | None = None,
    propostas_ferramenta: list[dict] | None = None,
    executar_proposta: bool = False,
) -> ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers:
    return ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers(
        papel=papel,
        modo="agente",
        texto=texto,
        criado_em=datetime.now(timezone.utc).isoformat(),
        citacoes=citacoes,
        imagens=imagens,
        estado=None,
        tipo_pipeline=None,
        proposta_ferramenta=proposta_ferramenta,
        propostas_ferramenta=propostas_ferramenta,
        executar_proposta=executar_proposta,
    )


def _mensagens_litellm_chat_agente_transcribrothers(
    *,
    historico_anterior: list[ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers],
    conteudo_usuario: str,
    forcar_ferramenta: str | None,
) -> list[dict[str, str]]:
    mensagens: list[dict[str, str]] = [
        {
            "role": "system",
            "content": montar_prompt_sistema_chat_agente_ferramentas_documento_job_transcribrothers(
                forcar_ferramenta=forcar_ferramenta,
            ),
        }
    ]
    for item in historico_anterior:
        if item.papel == "usuario":
            texto = (item.texto or "").strip()
            if not texto:
                continue
            mensagens.append({"role": "user", "content": texto})
        elif item.papel in ("assistente", "agente"):
            texto_assistente = _texto_assistente_com_propostas_pendentes_chat_agente_transcribrothers(
                item
            )
            if not texto_assistente.strip():
                continue
            mensagens.append({"role": "assistant", "content": texto_assistente})
    mensagens.append({"role": "user", "content": conteudo_usuario})
    return mensagens


def _texto_assistente_com_propostas_pendentes_chat_agente_transcribrothers(item) -> str:
    texto = (getattr(item, "texto", None) or "").strip()
    if getattr(item, "executar_proposta", False) is True:
        return texto
    propostas = getattr(item, "propostas_ferramenta", None)
    if not isinstance(propostas, list) or not propostas:
        unica = getattr(item, "proposta_ferramenta", None)
        propostas = [unica] if isinstance(unica, dict) and unica.get("nome") else []
    if not propostas:
        return texto
    bloco = json.dumps(propostas, ensure_ascii=False)
    if texto:
        return f"{texto}\n\nPropostas pendentes (JSON):\n{bloco}"
    return f"Propostas pendentes (JSON):\n{bloco}"


async def _resolver_imagens_instantes_chat_agente_transcribrothers(
    *,
    instantes: list[float],
    contexto,
    diretorio_trabalho_job: Path,
    steps_work: dict,
) -> tuple[list[dict], dict | None]:
    if not instantes:
        return [], None
    steps_base = dict(steps_work)
    resolvidas, steps_depois = await resolver_imagens_chat_ask_por_instantes_transcribrothers(
        instantes_segundos=instantes,
        catalogo=contexto.catalogo_frames,
        caminho_video=_localizar_video_entrada_chat_ask_transcribrothers(diretorio_trabalho_job),
        diretorio_trabalho_job=diretorio_trabalho_job,
        steps_json=steps_base,
        capturar_frame=capturar_frame_manual_video_tutorial_para_assets_do_job_transcribrothers,
    )
    imagens = [
        _imagem_resolvida_para_dict_chat_ask_transcribrothers(
            imagem,
            job_id=diretorio_trabalho_job.name,
        )
        for imagem in resolvidas
    ]
    steps_atualizados = steps_depois if steps_depois != steps_base else None
    return imagens, steps_atualizados


async def orquestrar_turno_chat_agente_job_transcribrothers(
    *,
    diretorio_trabalho_job: Path,
    markdown: str,
    steps_json: dict | None,
    mensagem: str,
    modelo: str,
    api_key: str | None,
    api_base: str | None,
    httpx_verify: bool | str,
    instante_anexo_segundos: float | None = None,
    forcar_ferramenta: str | None = None,
    emitir_delta_texto: Callable[[str], Awaitable[None]] | None = None,
) -> tuple[
    str,
    list[dict],
    list[dict],
    dict | None,
    list[dict],
    list[ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers],
    dict | None,
    bool,
]:
    transcricao = carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers(
        diretorio_trabalho_job
    )
    tem_markdown = bool((markdown or "").strip())
    if not tem_markdown and transcricao is None:
        raise ChatAskSemFonteError()

    historico_anterior = carregar_historico_chat_ask_agente_do_work_transcribrothers(
        diretorio_trabalho_job
    )
    caminhos_frames = _ler_caminhos_frames_rel_job_do_snapshot_em_disco_transcribrothers(
        diretorio_trabalho_job
    )
    contexto = montar_contexto_chat_ask_documento_job_transcribrothers(
        markdown=markdown or "",
        transcricao=transcricao,
        pergunta=mensagem,
        caminhos_frames_rel_job=caminhos_frames,
        steps_json=steps_json,
    )
    steps_work = dict(steps_json or {})
    imagens_turno_usuario: list[dict] = []
    steps_atualizados_instante: dict | None = None
    mensagem_para_prompt = mensagem
    if instante_anexo_segundos is not None:
        resolvidas_anexo, steps_depois_anexo = await resolver_imagens_chat_ask_por_instantes_transcribrothers(
            instantes_segundos=[float(instante_anexo_segundos)],
            catalogo=contexto.catalogo_frames,
            caminho_video=_localizar_video_entrada_chat_ask_transcribrothers(diretorio_trabalho_job),
            diretorio_trabalho_job=diretorio_trabalho_job,
            steps_json=steps_work,
            capturar_frame=capturar_frame_manual_video_tutorial_para_assets_do_job_transcribrothers,
        )
        if resolvidas_anexo:
            imagens_turno_usuario = [
                _imagem_resolvida_para_dict_chat_ask_transcribrothers(
                    imagem,
                    job_id=diretorio_trabalho_job.name,
                )
                for imagem in resolvidas_anexo
            ]
            mensagem_para_prompt = (
                f"{mensagem.rstrip()}\n\n"
                f"Frame anexado em {formatar_timestamp_segundos_para_mmss(float(instante_anexo_segundos))}."
            )
            if steps_depois_anexo != steps_work:
                steps_atualizados_instante = steps_depois_anexo
                steps_work = steps_depois_anexo
    conteudo_usuario = _montar_conteudo_usuario_chat_ask_transcribrothers(
        mensagem=mensagem_para_prompt,
        contexto=contexto,
    )
    anexar_item_historico_chat_ask_agente_no_work_transcribrothers(
        diretorio_trabalho_job,
        _novo_item_historico_agente_transcribrothers(
            papel="usuario",
            texto=mensagem,
            citacoes=[],
            imagens=imagens_turno_usuario,
        ),
    )
    bruto = await obter_texto_bruto_chat_litellm_preferindo_stream_transcribrothers(
        modelo=modelo,
        api_key=api_key,
        api_base=api_base,
        httpx_verify=httpx_verify,
        mensagens=_mensagens_litellm_chat_agente_transcribrothers(
            historico_anterior=historico_anterior,
            conteudo_usuario=conteudo_usuario,
            forcar_ferramenta=forcar_ferramenta,
        ),
        temperature=0.2,
        emitir_delta_texto=emitir_delta_texto,
    )
    resposta = parsear_resposta_json_chat_ask_litellm_transcribrothers(bruto)
    citacoes = [_citacao_para_dict_transcribrothers(c) for c in resposta.citacoes]
    ferramentas = parsear_ferramentas_de_texto_resposta_modelo_chat_agente_transcribrothers(bruto)
    propostas = escolher_propostas_ferramenta_chat_agente_transcribrothers(
        ferramentas=ferramentas,
        forcar_ferramenta=forcar_ferramenta,
        mensagem_usuario=mensagem,
    )
    proposta = propostas[0] if propostas else None
    if proposta is None and any(
        chave in mensagem.lower()
        for chave in ("frame", "bolar", "encaixar", "adicionar", "incluir", "rascunho")
    ):
        proposta = sintetizar_proposta_edicao_parcial_do_texto_agente_transcribrothers(resposta.texto)
        if proposta is not None:
            propostas = [proposta]
    instantes = list(resposta.instantes_imagem_segundos)
    if not instantes:
        instantes = extrair_instantes_segundos_mencionados_no_texto_chat_agente_transcribrothers(
            resposta.texto
        )
    texto = limpar_texto_visivel_se_vier_json_embutido_chat_agente_transcribrothers(
        resposta.texto,
        bruto,
    )
    imagens, steps_imagens = await _resolver_imagens_instantes_chat_agente_transcribrothers(
        instantes=instantes,
        contexto=contexto,
        diretorio_trabalho_job=diretorio_trabalho_job,
        steps_work=steps_work,
    )
    steps_atualizados: dict | None = steps_atualizados_instante or steps_imagens
    if steps_imagens is not None:
        steps_atualizados = steps_imagens
    if instantes and len(imagens) < len(instantes):
        texto = f"{texto.rstrip()}\n\n{_AVISO_TELA_CHAT_ASK_NAO_INCLUIDA_TRANSCRIBROTHERS}"
    fontes_imagens = (
        extrair_caminhos_relativos_de_imagens_historico_chat_agente_transcribrothers(imagens),
        extrair_caminhos_relativos_de_imagens_historico_chat_agente_transcribrothers(
            imagens_turno_usuario
        ),
    )
    propostas = [
        anexar_caminhos_imagens_na_proposta_edicao_parcial_chat_agente_transcribrothers(
            item,
            *fontes_imagens,
        )
        or item
        for item in propostas
    ]
    proposta = anexar_caminhos_imagens_na_proposta_edicao_parcial_chat_agente_transcribrothers(
        proposta,
        *fontes_imagens,
    )
    executar_proposta = decidir_executar_proposta_resposta_modelo_chat_agente_transcribrothers(
        flag_executar=parsear_flag_executar_resposta_modelo_chat_agente_transcribrothers(bruto),
        quantidade_propostas=len(propostas),
    )
    historico = anexar_item_historico_chat_ask_agente_no_work_transcribrothers(
        diretorio_trabalho_job,
        _novo_item_historico_agente_transcribrothers(
            papel="agente",
            texto=texto,
            citacoes=citacoes,
            imagens=imagens,
            proposta_ferramenta=proposta,
            propostas_ferramenta=propostas or None,
            executar_proposta=executar_proposta,
        ),
    )
    return texto, citacoes, imagens, proposta, propostas, historico, steps_atualizados, executar_proposta
