"""Um turno do chat Ask: contexto, LiteLLM, parse, imagens e histórico."""

from __future__ import annotations

import json
from collections.abc import Awaitable, Callable
from datetime import datetime, timezone
from pathlib import Path

from transcribrothers_backend.modulo_captura_frame_manual_video_tutorial_job_transcribrothers import (
    capturar_frame_manual_video_tutorial_para_assets_do_job_transcribrothers,
    listar_registros_frames_manuais_capturados_do_steps_json_transcribrothers,
)
from transcribrothers_backend.modulo_constante_chave_steps_json_frames_manuais_capturados_video_tutorial_transcribrothers import (
    CHAVE_STEPS_JSON_FRAMES_MANUAIS_CAPTURADOS_VIDEO_TUTORIAL_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_cliente_litellm_chat_completions_texto_simples_em_stream_transcribrothers import (
    obter_texto_bruto_chat_litellm_preferindo_stream_transcribrothers,
)
from transcribrothers_backend.modulo_montar_contexto_chat_ask_markdown_transcricao_e_catalogo_frames_transcribrothers import (
    ContextoChatAskDocumentoJobTranscribrothers,
    montar_contexto_chat_ask_documento_job_transcribrothers,
)
from transcribrothers_backend.modulo_parsear_resposta_json_chat_ask_litellm_transcribrothers import (
    CitacaoChatAskTranscribrothers,
    parsear_resposta_json_chat_ask_litellm_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_arquivo_json_snapshot_transcricao_finalizada_job_transcribrothers import (
    caminho_snapshot_transcricao_finalizada_no_work_transcribrothers,
    carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers,
)
from transcribrothers_backend.modulo_persistencia_historico_chat_ask_agente_documento_job_transcribrothers import (
    ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers,
    anexar_item_historico_chat_ask_agente_no_work_transcribrothers,
    carregar_historico_chat_ask_agente_do_work_transcribrothers,
)
from transcribrothers_backend.modulo_parse_link_google_drive_para_file_id import (
    formatar_timestamp_segundos_para_mmss,
)
from transcribrothers_backend.modulo_prompt_sistema_chat_ask_skills_documento_e_aplicacao_transcribrothers import (
    montar_prompt_sistema_chat_ask_documento_job_transcribrothers,
)
from transcribrothers_backend.modulo_resolver_imagem_chat_ask_galeria_ou_captura_frame_transcribrothers import (
    ImagemResolvidaChatAskTranscribrothers,
    resolver_imagens_chat_ask_por_instantes_transcribrothers,
)

PROMPT_SISTEMA_CHAT_ASK_DOCUMENTO_JOB_TRANSCRIBROTHERS = (
    montar_prompt_sistema_chat_ask_documento_job_transcribrothers()
)

_MENSAGEM_CHAT_ASK_SEM_FONTE_TRANSCRIBROTHERS = (
    "Não há Markdown nem transcrição neste job para o Ask."
)
_AVISO_TELA_CHAT_ASK_NAO_INCLUIDA_TRANSCRIBROTHERS = "Não foi possível incluir a tela pedida."


class ChatAskSemFonteError(Exception):
    """Job sem Markdown e sem snapshot de transcrição utilizável."""

    def __init__(self, mensagem: str = _MENSAGEM_CHAT_ASK_SEM_FONTE_TRANSCRIBROTHERS) -> None:
        super().__init__(mensagem)


_MENSAGEM_CHAT_ASK_RESOLVER_FRAME_SEM_VIDEO_TRANSCRIBROTHERS = (
    "Não há vídeo para anexar um frame."
)
_MENSAGEM_CHAT_ASK_RESOLVER_FRAME_CAPTURA_FALHOU_TRANSCRIBROTHERS = (
    "Não foi possível capturar o frame do vídeo."
)


class ChatAskResolverFrameSemVideoError(Exception):
    def __init__(
        self,
        mensagem: str = _MENSAGEM_CHAT_ASK_RESOLVER_FRAME_SEM_VIDEO_TRANSCRIBROTHERS,
    ) -> None:
        super().__init__(mensagem)


class ChatAskResolverFrameCapturaFalhouError(Exception):
    def __init__(
        self,
        mensagem: str = _MENSAGEM_CHAT_ASK_RESOLVER_FRAME_CAPTURA_FALHOU_TRANSCRIBROTHERS,
    ) -> None:
        super().__init__(mensagem)


def _ler_caminhos_frames_rel_job_do_snapshot_em_disco_transcribrothers(
    diretorio_trabalho_job: Path,
) -> list[tuple[float, str]]:
    path = caminho_snapshot_transcricao_finalizada_no_work_transcribrothers(diretorio_trabalho_job)
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, dict):
        return []
    rels: list[tuple[float, str]] = []
    for pair in data.get("caminhos_frames_rel_job") or []:
        if not isinstance(pair, (list, tuple)) or len(pair) < 2:
            continue
        try:
            rels.append((float(pair[0]), str(pair[1])))
        except (TypeError, ValueError):
            continue
    return rels


def _localizar_video_entrada_chat_ask_transcribrothers(work: Path) -> Path | None:
    if not work.is_dir():
        return None
    for pattern in ("video_entrada_arquivo_local.*", "video_entrada_google_drive.*"):
        for caminho in sorted(work.glob(pattern)):
            if caminho.is_file():
                return caminho
    return None


def _imagem_resolvida_para_dict_chat_ask_transcribrothers(
    imagem: ImagemResolvidaChatAskTranscribrothers,
    *,
    job_id: str,
) -> dict:
    nome = Path(imagem.caminho_relativo).name
    return {
        "caminho_relativo": imagem.caminho_relativo,
        "url": f"/api/jobs/{job_id}/assets/{nome}",
        "instante_segundos": imagem.instante_segundos,
        "origem": imagem.origem,
    }


def _citacao_para_dict_transcribrothers(citacao: CitacaoChatAskTranscribrothers) -> dict:
    return {
        "tipo": citacao.tipo,
        "rotulo": citacao.rotulo,
        "instante_segundos": citacao.instante_segundos,
        "heading": citacao.heading,
    }


def _montar_conteudo_usuario_chat_ask_transcribrothers(
    *,
    mensagem: str,
    contexto: ContextoChatAskDocumentoJobTranscribrothers,
) -> str:
    partes = [f"Pergunta:\n{(mensagem or '').strip()}"]
    if contexto.tem_markdown and contexto.markdown_para_prompt:
        partes.append("Markdown do documento:\n" + contexto.markdown_para_prompt)
    if contexto.tem_transcricao and contexto.transcricao_para_prompt:
        partes.append("Transcrição:\n" + contexto.transcricao_para_prompt)
    if contexto.catalogo_frames:
        linhas = [
            f"- {frame.instante_segundos:.3f}s {frame.caminho_relativo}"
            for frame in contexto.catalogo_frames
        ]
        partes.append("Catálogo de frames:\n" + "\n".join(linhas))
    return "\n\n".join(partes)


def _mensagens_litellm_chat_ask_transcribrothers(
    *,
    historico_anterior: list[ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers],
    conteudo_usuario: str,
) -> list[dict[str, str]]:
    mensagens: list[dict[str, str]] = [
        {"role": "system", "content": PROMPT_SISTEMA_CHAT_ASK_DOCUMENTO_JOB_TRANSCRIBROTHERS}
    ]
    for item in historico_anterior:
        texto = item.texto or ""
        if not texto.strip():
            continue
        if item.papel == "usuario":
            mensagens.append({"role": "user", "content": texto})
        elif item.papel in ("assistente", "agente"):
            mensagens.append({"role": "assistant", "content": texto})
    mensagens.append({"role": "user", "content": conteudo_usuario})
    return mensagens


def extrair_registros_frames_manuais_acrescentados_na_captura_chat_ask_transcribrothers(
    steps_json_antes: dict | None,
    steps_json_apos_captura: dict | None,
) -> list[dict]:
    """Registros de frame manual que a captura deste turno acrescentou à cópia antiga."""
    antes = listar_registros_frames_manuais_capturados_do_steps_json_transcribrothers(steps_json_antes)
    depois = listar_registros_frames_manuais_capturados_do_steps_json_transcribrothers(steps_json_apos_captura)
    if len(depois) <= len(antes):
        return []
    return depois[len(antes) :]


def mesclar_somente_frames_manuais_novos_no_steps_json_recente_transcribrothers(
    *,
    steps_json_recente: dict | None,
    registros_novos: list[dict],
) -> dict:
    """Copia o steps mais recente e anexa só os frames novos, sem repor o restante do JSON."""
    atual = dict(steps_json_recente or {})
    lista = listar_registros_frames_manuais_capturados_do_steps_json_transcribrothers(atual)
    ja_presentes = {
        (item.get("caminho_relativo"), item.get("timestamp_segundos_efetivo")) for item in lista
    }
    for registro in registros_novos:
        ident = (registro.get("caminho_relativo"), registro.get("timestamp_segundos_efetivo"))
        if ident in ja_presentes:
            continue
        lista.append(dict(registro))
        ja_presentes.add(ident)
    atual[CHAVE_STEPS_JSON_FRAMES_MANUAIS_CAPTURADOS_VIDEO_TUTORIAL_TRANSCRIBROTHERS] = lista
    return atual


def _novo_item_historico_ask_transcribrothers(
    *,
    papel: str,
    texto: str,
    citacoes: list[dict],
    imagens: list[dict],
) -> ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers:
    return ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers(
        papel=papel,
        modo="ask",
        texto=texto,
        criado_em=datetime.now(timezone.utc).isoformat(),
        citacoes=citacoes,
        imagens=imagens,
        estado=None,
        tipo_pipeline=None,
    )


async def resolver_frame_chat_ask_instante_job_transcribrothers(
    *,
    diretorio_trabalho_job: Path,
    markdown: str,
    steps_json: dict | None,
    instante_segundos: float,
) -> tuple[dict, dict | None]:
    """Resolve um frame para anexo no composer; levanta se não houver vídeo/galeria ou se a captura falhar."""
    transcricao = carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers(
        diretorio_trabalho_job
    )
    caminhos_frames = _ler_caminhos_frames_rel_job_do_snapshot_em_disco_transcribrothers(
        diretorio_trabalho_job
    )
    contexto = montar_contexto_chat_ask_documento_job_transcribrothers(
        markdown=markdown or "",
        transcricao=transcricao,
        pergunta="",
        caminhos_frames_rel_job=caminhos_frames,
        steps_json=steps_json,
    )
    caminho_video = _localizar_video_entrada_chat_ask_transcribrothers(diretorio_trabalho_job)
    steps_base = dict(steps_json or {})
    resolvidas, steps_depois = await resolver_imagens_chat_ask_por_instantes_transcribrothers(
        instantes_segundos=[float(instante_segundos)],
        catalogo=contexto.catalogo_frames,
        caminho_video=caminho_video,
        diretorio_trabalho_job=diretorio_trabalho_job,
        steps_json=steps_base,
        capturar_frame=capturar_frame_manual_video_tutorial_para_assets_do_job_transcribrothers,
    )
    if not resolvidas:
        if caminho_video is None or not caminho_video.is_file():
            raise ChatAskResolverFrameSemVideoError()
        raise ChatAskResolverFrameCapturaFalhouError()
    imagem = resolvidas[0]
    payload = _imagem_resolvida_para_dict_chat_ask_transcribrothers(
        imagem,
        job_id=diretorio_trabalho_job.name,
    )
    steps_atualizados = steps_depois if steps_depois != steps_base else None
    return payload, steps_atualizados


async def orquestrar_turno_chat_ask_job_transcribrothers(
    *,
    diretorio_trabalho_job: Path,
    markdown: str,
    steps_json: dict | None,
    mensagem: str,
    modelo: str,
    api_key: str | None,
    api_base: str | None,
    httpx_verify: bool | str,
    resolver_imagens: bool = False,
    instante_anexo_segundos: float | None = None,
    emitir_delta_texto: Callable[[str], Awaitable[None]] | None = None,
) -> tuple[
    str,
    list[dict],
    list[dict],
    list[ItemHistoricoChatAskAgenteDocumentoJobTranscribrothers],
    dict | None,
]:
    transcricao = carregar_snapshot_transcricao_finalizada_do_work_se_existir_transcribrothers(
        diretorio_trabalho_job
    )
    tem_markdown = bool((markdown or "").strip())
    if not tem_markdown and transcricao is None:
        raise ChatAskSemFonteError()

    historico_anterior = carregar_historico_chat_ask_agente_do_work_transcribrothers(diretorio_trabalho_job)
    caminhos_frames = _ler_caminhos_frames_rel_job_do_snapshot_em_disco_transcribrothers(diretorio_trabalho_job)
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
        _novo_item_historico_ask_transcribrothers(
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
        mensagens=_mensagens_litellm_chat_ask_transcribrothers(
            historico_anterior=historico_anterior,
            conteudo_usuario=conteudo_usuario,
        ),
        temperature=0.2,
        emitir_delta_texto=emitir_delta_texto,
    )
    resposta = parsear_resposta_json_chat_ask_litellm_transcribrothers(bruto)
    citacoes = [_citacao_para_dict_transcribrothers(c) for c in resposta.citacoes]
    imagens: list[dict] = []
    texto = resposta.texto
    steps_atualizados: dict | None = steps_atualizados_instante
    if resolver_imagens and resposta.instantes_imagem_segundos:
        steps_base = dict(steps_work)
        resolvidas, steps_depois = await resolver_imagens_chat_ask_por_instantes_transcribrothers(
            instantes_segundos=resposta.instantes_imagem_segundos,
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
        if steps_depois != steps_base:
            steps_atualizados = steps_depois
        if len(imagens) < len(resposta.instantes_imagem_segundos):
            texto = f"{texto.rstrip()}\n\n{_AVISO_TELA_CHAT_ASK_NAO_INCLUIDA_TRANSCRIBROTHERS}"
    historico = anexar_item_historico_chat_ask_agente_no_work_transcribrothers(
        diretorio_trabalho_job,
        _novo_item_historico_ask_transcribrothers(
            papel="assistente",
            texto=texto,
            citacoes=citacoes,
            imagens=imagens,
        ),
    )
    return texto, citacoes, imagens, historico, steps_atualizados
