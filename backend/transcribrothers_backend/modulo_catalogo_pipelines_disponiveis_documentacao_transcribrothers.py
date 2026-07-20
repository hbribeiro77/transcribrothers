"""Catálogo estático das pipelines do produto (agentes, passos e prompts fixos) para a UI de documentação."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from transcribrothers_backend.constante_texto_instrucao_geracao_notas_proposta_funcionalidade_com_imagens_transcribrothers import (
    TEXTO_INSTRUCAO_GERACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_COM_IMAGENS_TRANSCRIBROTHERS,
)
from transcribrothers_backend.constante_texto_instrucao_geracao_notas_proposta_funcionalidade_rascunho_sem_imagens_transcribrothers import (
    TEXTO_INSTRUCAO_GERACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_RASCUNHO_SEM_IMAGENS_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_cliente_litellm_geracao_reproducao_bug_markdown_transcribrothers import (
    INSTRUCAO_LITELLM_REPRODUCAO_BUG_RECBROTHERS_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_cliente_litellm_geracao_tutorial_markdown import (
    INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_COM_IMAGENS_PADRAO_TRANSCRIBROTHERS,
    INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_SEM_IMAGENS_PADRAO_TRANSCRIBROTHERS,
    INSTRUCAO_LITELLM_TUTORIAL_RASCUNHO_SEM_IMAGENS_CAPTURA_FRAMES_SOB_DEMANDA_TRANSCRIBROTHERS,
    INSTRUCOES_REVISAO_LITELLM_INCORPORAR_FRAMES_APOS_CAPTURA_SOB_DEMANDA_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_cliente_litellm_planejamento_instantes_captura_frames_tutorial_transcribrothers import (
    SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_NOTAS_PROPOSTA_FUNCIONALIDADE_TRANSCRIBROTHERS,
    SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_TUTORIAL_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_cliente_litellm_regeneracao_secao_markdown_tutorial_transcribrothers import (
    SYSTEM_PROMPT_REGENERACAO_SECAO_MARKDOWN_TUTORIAL_TRANSCRIBROTHERS,
    SYSTEM_PROMPT_REGENERACAO_ZONA_ESCOPO_SECAO_MARKDOWN_TUTORIAL_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_constante_identificador_versao_pipeline_diagnostico_transcribrothers import (
    IDENTIFICADOR_VERSAO_PIPELINE_DIAGNOSTICO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_interpretacao_pedido_edicao_secao_markdown_linguagem_natural_litellm_transcribrothers import (
    SYSTEM_PROMPT_INTERPRETACAO_PEDIDO_EDICAO_SECAO_MARKDOWN_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_prompts_e_schema_json_plano_revisao_profunda_tutorial_transcribrothers import (
    INSTRUCAO_EDITOR_FINAL_REVISAO_PROFUNDA_CONSOLIDACAO_MARKDOWN_TRANSCRIBROTHERS,
    SYSTEM_PROMPT_ANALISTA_PLANO_REVISAO_PROFUNDA_TUTORIAL_TRANSCRIBROTHERS,
    SYSTEM_PROMPT_RESUMO_PLANO_PARA_EDITOR_FINAL_TRANSCRIBROTHERS,
    SYSTEM_PROMPT_WORKER_ITEM_PLANO_REVISAO_PROFUNDA_TUTORIAL_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_resolver_escopo_edicao_secao_markdown_validacao_e_refinamento_litellm_transcribrothers import (
    SYSTEM_PROMPT_REFINAMENTO_ESCOPO_EDICAO_SECAO_MARKDOWN_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_speech_to_text_litellm_multimodal_audio_json_segmentos import (
    _PROMPT_TRANSCRICAO_JSON_PT,
    _PROMPT_TRANSCRICAO_JSON_RETRY_PT,
)
from transcribrothers_backend.modulo_verificacao_imagens_duplicadas_tutorial_markdown_litellm_visao_lotes_transcribrothers import (
    SYSTEM_PROMPT_VERIFICACAO_IMAGENS_DUPLICADAS_TUTORIAL_VISAO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_verificacao_redundancia_secao_markdown_entre_secoes_litellm_transcribrothers import (
    SYSTEM_PROMPT_CORRECAO_REDUNDANCIA_SECAO_MARKDOWN_TRANSCRIBROTHERS,
    SYSTEM_PROMPT_VERIFICACAO_REDUNDANCIA_SECAO_MARKDOWN_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_verificacao_sustentacao_notas_proposta_funcionalidade_markdown_litellm_transcribrothers import (
    SYSTEM_PROMPT_VERIFICACAO_SUSTENTACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_VS_TRANSCRICAO_TRANSCRIBROTHERS,
)
from transcribrothers_backend.modulo_verificacao_sustentacao_tutorial_markdown_litellm_transcribrothers import (
    SYSTEM_PROMPT_VERIFICACAO_SUSTENTACAO_TUTORIAL_MARKDOWN_VS_TRANSCRICAO_TRANSCRIBROTHERS,
)

TipoPromptCatalogoPipelineTranscribrothers = Literal["system", "user", "instrucao", "observacao"]


class PromptCatalogoPassoPipelineTranscribrothers(BaseModel):
    chave: str
    tipo: TipoPromptCatalogoPipelineTranscribrothers
    rotulo: str
    texto: str = ""
    observacao: str | None = None
    fonte_modulo: str | None = None


class AgenteCatalogoDocumentacaoTranscribrothers(BaseModel):
    id: str
    rotulo: str
    descricao: str
    handler_chave: str | None = None
    origem: Literal["sistema", "usuario"] = "sistema"
    editavel: bool = False
    copiado_de: str | None = None
    modelo_litellm: str | None = None
    prompts: list[PromptCatalogoPassoPipelineTranscribrothers] = Field(default_factory=list)
    pipelines_ids: list[str] = Field(default_factory=list)


class PassoCatalogoPipelineTranscribrothers(BaseModel):
    id: str
    agente_id: str
    rotulo: str
    descricao: str


TipoEntradaMidiaCatalogoTranscribrothers = Literal["video", "audio"]


class PipelineCatalogoDocumentacaoTranscribrothers(BaseModel):
    id: str
    titulo: str
    descricao: str
    origem: Literal["sistema", "usuario"] = "sistema"
    editavel: bool = False
    executavel: bool = True
    copiado_de: str | None = None
    ordem: int | None = None
    entradas_aceitas: list[TipoEntradaMidiaCatalogoTranscribrothers] = Field(
        default_factory=lambda: ["video"]
    )
    passos: list[PassoCatalogoPipelineTranscribrothers] = Field(default_factory=list)


class RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers(BaseModel):
    pipeline_identificador: str
    agentes: list[AgenteCatalogoDocumentacaoTranscribrothers] = Field(default_factory=list)
    pipelines: list[PipelineCatalogoDocumentacaoTranscribrothers] = Field(default_factory=list)


def _prompt(
    tipo: TipoPromptCatalogoPipelineTranscribrothers,
    rotulo: str,
    texto: str,
    *,
    chave: str,
    observacao: str | None = None,
    fonte_modulo: str | None = None,
) -> PromptCatalogoPassoPipelineTranscribrothers:
    return PromptCatalogoPassoPipelineTranscribrothers(
        chave=chave,
        tipo=tipo,
        rotulo=rotulo,
        texto=texto,
        observacao=observacao,
        fonte_modulo=fonte_modulo,
    )


def _agente(
    id_agente: str,
    rotulo: str,
    descricao: str,
    prompts: list[PromptCatalogoPassoPipelineTranscribrothers] | None = None,
) -> AgenteCatalogoDocumentacaoTranscribrothers:
    return AgenteCatalogoDocumentacaoTranscribrothers(
        id=id_agente,
        rotulo=rotulo,
        descricao=descricao,
        handler_chave=id_agente,
        origem="sistema",
        editavel=False,
        prompts=prompts or [],
    )


def _passo(
    id_passo: str,
    agente_id: str,
    rotulo: str,
    descricao: str,
) -> PassoCatalogoPipelineTranscribrothers:
    return PassoCatalogoPipelineTranscribrothers(
        id=id_passo,
        agente_id=agente_id,
        rotulo=rotulo,
        descricao=descricao,
    )


PIPELINES_SISTEMA_EXECUTAVEIS_UPLOAD_TRANSCRIBROTHERS = frozenset(
    {
        "pipeline_inicial_tutorial",
        "pipeline_inicial_notas_proposta",
        "pipeline_inicial_reproducao_bug",
        "pipeline_inicial_so_transcricao",
    }
)


def normalizar_entradas_aceitas_pipeline_catalogo_transcribrothers(
    raw: object,
    *,
    padrao: list[TipoEntradaMidiaCatalogoTranscribrothers] | None = None,
) -> list[TipoEntradaMidiaCatalogoTranscribrothers]:
    """Normaliza lista de entradas; exige ao menos um de video|audio."""
    fallback: list[TipoEntradaMidiaCatalogoTranscribrothers] = (
        list(padrao) if padrao is not None else ["video"]
    )
    if not isinstance(raw, list):
        return fallback
    out: list[TipoEntradaMidiaCatalogoTranscribrothers] = []
    vistos: set[str] = set()
    for item in raw:
        if item not in ("video", "audio") or item in vistos:
            continue
        vistos.add(item)
        out.append(item)  # type: ignore[arg-type]
    return out if out else fallback


def _prompts_preparacao_transcricao_comuns_transcribrothers() -> list[PromptCatalogoPassoPipelineTranscribrothers]:
    return [
        _prompt(
            "observacao",
            "Sem prompt único",
            "",
            chave="observacao_sem_prompt_unico",
            observacao=(
                "Extração de áudio (ffmpeg) e capturas PNG não usam LiteLLM. "
                "A transcrição usa Whisper (`POST /v1/audio/transcriptions`) ou multimodal "
                "(`POST /v1/chat/completions` com áudio inline), conforme `TRANSCRICAO_BACKEND` e Configurações."
            ),
        ),
        _prompt(
            "user",
            "Transcrição multimodal (janela)",
            _PROMPT_TRANSCRICAO_JSON_PT,
            chave="transcricao_multimodal_janela",
            fonte_modulo="modulo_speech_to_text_litellm_multimodal_audio_json_segmentos",
        ),
        _prompt(
            "user",
            "Transcrição multimodal (retry JSON)",
            _PROMPT_TRANSCRICAO_JSON_RETRY_PT,
            chave="transcricao_multimodal_retry",
            observacao="Usado na 2ª e 3ª tentativa se o JSON da transcrição vier inválido.",
            fonte_modulo="modulo_speech_to_text_litellm_multimodal_audio_json_segmentos",
        ),
    ]


def _montar_agentes_catalogo_transcribrothers() -> dict[str, AgenteCatalogoDocumentacaoTranscribrothers]:
    return {
        "preparacao_transcricao": _agente(
            "preparacao_transcricao",
            "Preparação",
            "Metadados do job, extração de áudio (ffmpeg) e transcrição do vídeo.",
            _prompts_preparacao_transcricao_comuns_transcribrothers(),
        ),
        "preparacao_reutilizacao_snapshot_regeneracao": _agente(
            "preparacao_reutilizacao_snapshot_regeneracao",
            "Preparação (reutilização)",
            "Reutiliza transcrição, frames e snapshot já gravados no job (sem reprocessar o vídeo).",
            [
                _prompt(
                    "observacao",
                    "Sem nova transcrição",
                    "",
                    chave="observacao_sem_nova_transcricao",
                    observacao="Usa `regeneracao_tutorial_snapshot` gravado no job.",
                ),
            ],
        ),
        "preparacao_reutilizacao_snapshot_revisao": _agente(
            "preparacao_reutilizacao_snapshot_revisao",
            "Preparação (reutilização)",
            "Usa snapshot e tutorial já existentes (sem nova transcrição nem capturas).",
            [
                _prompt(
                    "observacao",
                    "Snapshot existente",
                    "",
                    chave="observacao_snapshot_existente",
                    observacao="Reutiliza transcrição e frames do job.",
                ),
            ],
        ),
        "rascunho_tutorial_sob_demanda": _agente(
            "rascunho_tutorial_sob_demanda",
            "Rascunho (tutorial)",
            "Gera um tutorial provisório só com texto e links ?t= para decidir onde tirar screenshots, antes das capturas reais.",
            [
                _prompt(
                    "instrucao",
                    "Rascunho sem imagens (user)",
                    INSTRUCAO_LITELLM_TUTORIAL_RASCUNHO_SEM_IMAGENS_CAPTURA_FRAMES_SOB_DEMANDA_TRANSCRIBROTHERS,
                    chave="instrucao_rascunho_sem_imagens",
                    fonte_modulo="modulo_cliente_litellm_geracao_tutorial_markdown",
                ),
            ],
        ),
        "rascunho_notas_proposta": _agente(
            "rascunho_notas_proposta",
            "Rascunho (notas)",
            "Notas provisórias com links temporais, sem imagens, para orientar quais slides ou telas capturar.",
            [
                _prompt(
                    "instrucao",
                    "Rascunho notas sem imagens (user)",
                    TEXTO_INSTRUCAO_GERACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_RASCUNHO_SEM_IMAGENS_TRANSCRIBROTHERS,
                    chave="instrucao_rascunho_notas_sem_imagens",
                    fonte_modulo="constante_texto_instrucao_geracao_notas_proposta_funcionalidade_rascunho_sem_imagens_transcribrothers",
                ),
            ],
        ),
        "plano_capturas_tutorial": _agente(
            "plano_capturas_tutorial",
            "Plano capturas (tutorial)",
            "Planejamento (LiteLLM) dos instantes de captura a partir do rascunho e da transcrição, respeitando margem mínima entre links temporais.",
            [
                _prompt(
                    "system",
                    "Planejamento de instantes (tutorial)",
                    SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_TUTORIAL_TRANSCRIBROTHERS,
                    chave="system_planejamento_instantes_tutorial",
                    fonte_modulo="modulo_cliente_litellm_planejamento_instantes_captura_frames_tutorial_transcribrothers",
                ),
            ],
        ),
        "plano_capturas_notas": _agente(
            "plano_capturas_notas",
            "Plano capturas (notas)",
            "Escolhe instantes com slides, mockups ou demos na tela compartilhada.",
            [
                _prompt(
                    "system",
                    "Planejamento de instantes (notas)",
                    SYSTEM_PROMPT_PLANEJAMENTO_INSTANTES_CAPTURA_FRAMES_NOTAS_PROPOSTA_FUNCIONALIDADE_TRANSCRIBROTHERS,
                    chave="system_planejamento_instantes_notas",
                    fonte_modulo="modulo_cliente_litellm_planejamento_instantes_captura_frames_tutorial_transcribrothers",
                ),
            ],
        ),
        "capturas_ffmpeg_plano": _agente(
            "capturas_ffmpeg_plano",
            "Capturas",
            "Screenshots PNG do vídeo (ffmpeg), gravados em assets/ e referenciados no documento.",
            [
                _prompt(
                    "observacao",
                    "Sem prompt LLM",
                    "",
                    chave="observacao_sem_prompt_llm",
                    observacao="Captura determinística via ffmpeg nos instantes escolhidos (segmentos da transcrição ou plano do passo anterior).",
                ),
            ],
        ),
        "capturas_ffmpeg_rec_brothers": _agente(
            "capturas_ffmpeg_rec_brothers",
            "Capturas (RecBrothers)",
            "Screenshots nos instantes dos cliques registrados (e deduplicação temporal).",
            [
                _prompt(
                    "observacao",
                    "Sem prompt LLM",
                    "",
                    chave="observacao_sem_prompt_llm_rec",
                    observacao="Timestamps derivados do JSON de cliques RecBrothers; captura via ffmpeg.",
                ),
            ],
        ),
        "gerador_tutorial_markdown": _agente(
            "gerador_tutorial_markdown",
            "Gerador (tutorial)",
            "Gera o tutorial em Markdown final (transcrição + imagens). Com captura sob demanda, incorpora o rascunho e as capturas já feitas.",
            [
                _prompt(
                    "instrucao",
                    "Tutorial sem imagens anexadas (user)",
                    INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_SEM_IMAGENS_PADRAO_TRANSCRIBROTHERS,
                    chave="instrucao_tutorial_sem_imagens",
                    fonte_modulo="modulo_cliente_litellm_geracao_tutorial_markdown",
                ),
                _prompt(
                    "instrucao",
                    "Tutorial com imagens anexadas (user)",
                    INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_COM_IMAGENS_PADRAO_TRANSCRIBROTHERS,
                    chave="instrucao_tutorial_com_imagens",
                    fonte_modulo="modulo_cliente_litellm_geracao_tutorial_markdown",
                ),
                _prompt(
                    "instrucao",
                    "Incorporar frames após captura sob demanda",
                    INSTRUCOES_REVISAO_LITELLM_INCORPORAR_FRAMES_APOS_CAPTURA_SOB_DEMANDA_TRANSCRIBROTHERS,
                    chave="instrucao_incorporar_frames_sob_demanda",
                    fonte_modulo="modulo_cliente_litellm_geracao_tutorial_markdown",
                ),
                _prompt(
                    "observacao",
                    "Prefixo opcional na UI",
                    "",
                    chave="observacao_prefixo_opcional_ui",
                    observacao="O usuário pode acrescentar instrução/prefixo customizado no formulário antes de iniciar o job.",
                ),
            ],
        ),
        "gerador_notas_proposta": _agente(
            "gerador_notas_proposta",
            "Gerador (notas)",
            "Gera o documento final de notas de proposta com imagens incorporadas.",
            [
                _prompt(
                    "instrucao",
                    "Notas com imagens (user)",
                    TEXTO_INSTRUCAO_GERACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_COM_IMAGENS_TRANSCRIBROTHERS,
                    chave="instrucao_notas_com_imagens",
                    fonte_modulo="constante_texto_instrucao_geracao_notas_proposta_funcionalidade_com_imagens_transcribrothers",
                ),
            ],
        ),
        "gerador_reproducao_bug": _agente(
            "gerador_reproducao_bug",
            "Gerador (bug)",
            "Produz roteiro passo a passo para outra pessoa reproduzir o bug.",
            [
                _prompt(
                    "instrucao",
                    "Reprodução de bug (user)",
                    INSTRUCAO_LITELLM_REPRODUCAO_BUG_RECBROTHERS_TRANSCRIBROTHERS,
                    chave="instrucao_reproducao_bug",
                    fonte_modulo="modulo_cliente_litellm_geracao_reproducao_bug_markdown_transcribrothers",
                ),
            ],
        ),
        "gerador_regeneracao_documento": _agente(
            "gerador_regeneracao_documento",
            "Gerador (regeneração)",
            "Regenera o documento inteiro em um passe ao modelo (Markdown atual + transcrição + imagens anexadas conforme instruções).",
            [
                _prompt(
                    "instrucao",
                    "Mesmas instruções do gerador inicial",
                    INSTRUCAO_LITELLM_TUTORIAL_MARKDOWN_COM_IMAGENS_PADRAO_TRANSCRIBROTHERS,
                    chave="instrucao_regeneracao_documento",
                    observacao="Também aceita prefixo/instrução opcional enviada pelo FAB de regeneração.",
                    fonte_modulo="modulo_cliente_litellm_geracao_tutorial_markdown",
                ),
            ],
        ),
        "verificacao_imagens_duplicadas": _agente(
            "verificacao_imagens_duplicadas",
            "Imagens (duplicadas)",
            "Verificação por visão: remove ou funde referências a screenshots visualmente duplicadas no Markdown.",
            [
                _prompt(
                    "system",
                    "Verificação imagens duplicadas (visão)",
                    SYSTEM_PROMPT_VERIFICACAO_IMAGENS_DUPLICADAS_TUTORIAL_VISAO_TRANSCRIBROTHERS,
                    chave="system_verificacao_imagens_duplicadas",
                    fonte_modulo="modulo_verificacao_imagens_duplicadas_tutorial_markdown_litellm_visao_lotes_transcribrothers",
                ),
            ],
        ),
        "auditor_sustentacao_tutorial": _agente(
            "auditor_sustentacao_tutorial",
            "Auditor (tutorial)",
            "Verificação automática do tutorial em relação à transcrição (inconsistências). Pode ser desligada no servidor ou em Configurações.",
            [
                _prompt(
                    "system",
                    "Verificação de sustentação",
                    SYSTEM_PROMPT_VERIFICACAO_SUSTENTACAO_TUTORIAL_MARKDOWN_VS_TRANSCRICAO_TRANSCRIBROTHERS,
                    chave="system_verificacao_sustentacao_tutorial",
                    fonte_modulo="modulo_verificacao_sustentacao_tutorial_markdown_litellm_transcribrothers",
                ),
            ],
        ),
        "auditor_sustentacao_notas": _agente(
            "auditor_sustentacao_notas",
            "Auditor (notas)",
            "Verifica se as notas estão sustentadas pela transcrição da reunião.",
            [
                _prompt(
                    "system",
                    "Verificação sustentação (notas)",
                    SYSTEM_PROMPT_VERIFICACAO_SUSTENTACAO_NOTAS_PROPOSTA_FUNCIONALIDADE_VS_TRANSCRICAO_TRANSCRIBROTHERS,
                    chave="system_verificacao_sustentacao_notas",
                    fonte_modulo="modulo_verificacao_sustentacao_notas_proposta_funcionalidade_markdown_litellm_transcribrothers",
                ),
            ],
        ),
        "resultado_transcricao_markdown": _agente(
            "resultado_transcricao_markdown",
            "Resultado (transcrição)",
            "Publica a transcrição como documento Markdown do job (sem gerar tutorial, notas ou roteiro de bug).",
            [
                _prompt(
                    "observacao",
                    "Sem prompt LLM",
                    "",
                    chave="observacao_resultado_transcricao",
                    observacao="Após a preparação/transcrição, o texto com segmentos vira o result_markdown do job.",
                ),
            ],
        ),
        "preview_documento_ui": _agente(
            "preview_documento_ui",
            "Preview (documento)",
            "Documento proposto pronto para comparar antes/depois. Aplique para gravar no job ou descarte para manter o tutorial atual.",
            [
                _prompt(
                    "observacao",
                    "Sem prompt LLM",
                    "",
                    chave="observacao_preview_documento_ui",
                    observacao="Passo de UI: comparativo antes/depois; não há nova chamada ao modelo.",
                ),
            ],
        ),
        "preview_secao_ui": _agente(
            "preview_secao_ui",
            "Preview (seção)",
            "Pré-visualização pronta no editor: aplique para gravar no job ou descarte.",
            [
                _prompt(
                    "observacao",
                    "Sem prompt LLM",
                    "",
                    chave="observacao_preview_secao_ui",
                    observacao="Passo de UI no editor de Markdown.",
                ),
            ],
        ),
        "planejador_revisao_profunda": _agente(
            "planejador_revisao_profunda",
            "Planejador (revisão)",
            "Analista lê transcrição, frames e tutorial atual e devolve um plano estruturado (JSON) com tópicos a aprofundar.",
            [
                _prompt(
                    "system",
                    "Analista — plano JSON",
                    SYSTEM_PROMPT_ANALISTA_PLANO_REVISAO_PROFUNDA_TUTORIAL_TRANSCRIBROTHERS,
                    chave="system_analista_plano_revisao",
                    fonte_modulo="modulo_prompts_e_schema_json_plano_revisao_profunda_tutorial_transcribrothers",
                ),
            ],
        ),
        "editor_topico_revisao_profunda": _agente(
            "editor_topico_revisao_profunda",
            "Editor por tópico",
            "Um passe ao modelo por tópico do plano de revisão profunda.",
            [
                _prompt(
                    "system",
                    "Worker por tópico",
                    SYSTEM_PROMPT_WORKER_ITEM_PLANO_REVISAO_PROFUNDA_TUTORIAL_TRANSCRIBROTHERS,
                    chave="system_worker_topico_revisao",
                    fonte_modulo="modulo_prompts_e_schema_json_plano_revisao_profunda_tutorial_transcribrothers",
                ),
            ],
        ),
        "consolidador_revisao_profunda": _agente(
            "consolidador_revisao_profunda",
            "Consolidador (revisão)",
            "Harmoniza o Markdown completo após os passes por tópico (editor final multimodal).",
            [
                _prompt(
                    "system",
                    "Resumo do plano (auxiliar)",
                    SYSTEM_PROMPT_RESUMO_PLANO_PARA_EDITOR_FINAL_TRANSCRIBROTHERS,
                    chave="system_resumo_plano_editor_final",
                    fonte_modulo="modulo_prompts_e_schema_json_plano_revisao_profunda_tutorial_transcribrothers",
                ),
                _prompt(
                    "instrucao",
                    "Editor final — consolidação",
                    INSTRUCAO_EDITOR_FINAL_REVISAO_PROFUNDA_CONSOLIDACAO_MARKDOWN_TRANSCRIBROTHERS,
                    chave="instrucao_editor_final_consolidacao",
                    fonte_modulo="modulo_prompts_e_schema_json_plano_revisao_profunda_tutorial_transcribrothers",
                ),
            ],
        ),
        "escopo_edicao_secao": _agente(
            "escopo_edicao_secao",
            "Escopo (edição parcial)",
            "Interpreta ou valida o pedido em linguagem natural: qual seção ##, trecho ou «a partir de» será editado.",
            [
                _prompt(
                    "system",
                    "Interpretação do pedido (NL)",
                    SYSTEM_PROMPT_INTERPRETACAO_PEDIDO_EDICAO_SECAO_MARKDOWN_TRANSCRIBROTHERS,
                    chave="system_interpretacao_pedido_edicao",
                    fonte_modulo="modulo_interpretacao_pedido_edicao_secao_markdown_linguagem_natural_litellm_transcribrothers",
                ),
                _prompt(
                    "system",
                    "Refinamento de escopo",
                    SYSTEM_PROMPT_REFINAMENTO_ESCOPO_EDICAO_SECAO_MARKDOWN_TRANSCRIBROTHERS,
                    chave="system_refinamento_escopo_edicao",
                    fonte_modulo="modulo_resolver_escopo_edicao_secao_markdown_validacao_e_refinamento_litellm_transcribrothers",
                ),
                _prompt(
                    "system",
                    "Zona de escopo (regeneração)",
                    SYSTEM_PROMPT_REGENERACAO_ZONA_ESCOPO_SECAO_MARKDOWN_TUTORIAL_TRANSCRIBROTHERS,
                    chave="system_zona_escopo_regeneracao",
                    fonte_modulo="modulo_cliente_litellm_regeneracao_secao_markdown_tutorial_transcribrothers",
                ),
            ],
        ),
        "regeneracao_secao_parcial": _agente(
            "regeneracao_secao_parcial",
            "Regeneração de seção",
            "Chamada ao modelo para reescrever só a região delimitada, mantendo o restante do tutorial.",
            [
                _prompt(
                    "system",
                    "Regeneração da seção",
                    SYSTEM_PROMPT_REGENERACAO_SECAO_MARKDOWN_TUTORIAL_TRANSCRIBROTHERS,
                    chave="system_regeneracao_secao",
                    fonte_modulo="modulo_cliente_litellm_regeneracao_secao_markdown_tutorial_transcribrothers",
                ),
            ],
        ),
        "verificacao_redundancia_secao": _agente(
            "verificacao_redundancia_secao",
            "Redundância entre seções",
            "Verifica se o trecho proposto repete conteúdo de outras seções; pode corrigir automaticamente conforme Configurações.",
            [
                _prompt(
                    "system",
                    "Verificação de redundância",
                    SYSTEM_PROMPT_VERIFICACAO_REDUNDANCIA_SECAO_MARKDOWN_TRANSCRIBROTHERS,
                    chave="system_verificacao_redundancia_secao",
                    fonte_modulo="modulo_verificacao_redundancia_secao_markdown_entre_secoes_litellm_transcribrothers",
                ),
                _prompt(
                    "system",
                    "Correção automática de redundância",
                    SYSTEM_PROMPT_CORRECAO_REDUNDANCIA_SECAO_MARKDOWN_TRANSCRIBROTHERS,
                    chave="system_correcao_redundancia_secao",
                    fonte_modulo="modulo_verificacao_redundancia_secao_markdown_entre_secoes_litellm_transcribrothers",
                ),
            ],
        ),
    }


def _pipeline(
    id_pipeline: str,
    titulo: str,
    descricao: str,
    passos: list[PassoCatalogoPipelineTranscribrothers],
    *,
    entradas_aceitas: list[TipoEntradaMidiaCatalogoTranscribrothers] | None = None,
) -> PipelineCatalogoDocumentacaoTranscribrothers:
    return PipelineCatalogoDocumentacaoTranscribrothers(
        id=id_pipeline,
        titulo=titulo,
        descricao=descricao,
        origem="sistema",
        editavel=False,
        executavel=id_pipeline in PIPELINES_SISTEMA_EXECUTAVEIS_UPLOAD_TRANSCRIBROTHERS,
        entradas_aceitas=normalizar_entradas_aceitas_pipeline_catalogo_transcribrothers(
            entradas_aceitas, padrao=["video"]
        ),
        passos=passos,
    )


def _montar_pipelines_catalogo_transcribrothers() -> list[PipelineCatalogoDocumentacaoTranscribrothers]:
    agentes = _montar_agentes_catalogo_transcribrothers()

    def ref(id_passo: str, agente_id: str, descricao: str | None = None) -> PassoCatalogoPipelineTranscribrothers:
        agente = agentes[agente_id]
        return _passo(
            id_passo,
            agente_id,
            agente.rotulo,
            descricao or agente.descricao,
        )

    return [
        _pipeline(
            "pipeline_inicial_tutorial",
            "Fluxo 1 — Vídeo até tutorial",
            "Transcrição, capturas de tela sob demanda e primeira geração do Markdown de tutorial.",
            [
                ref(
                    "preparacao",
                    "preparacao_transcricao",
                    "Metadados do job, extração de áudio (ffmpeg) e transcrição do vídeo. É a base antes de qualquer captura ou geração do tutorial.",
                ),
                ref("rascunho", "rascunho_tutorial_sob_demanda"),
                ref("plano_capturas", "plano_capturas_tutorial"),
                ref("capturas", "capturas_ffmpeg_plano"),
                ref("gerador", "gerador_tutorial_markdown"),
                ref("verificacao_imagens", "verificacao_imagens_duplicadas"),
                ref("auditor", "auditor_sustentacao_tutorial"),
            ],
        ),
        _pipeline(
            "pipeline_inicial_notas_proposta",
            "Fluxo 1 — Vídeo até notas de proposta",
            "Transcrição de reunião, capturas de evidências visuais e notas de proposta de funcionalidade em Markdown.",
            [
                ref(
                    "preparacao",
                    "preparacao_transcricao",
                    "Mesma base do fluxo de tutorial: áudio, transcrição e metadados do job.",
                ),
                ref("rascunho", "rascunho_notas_proposta"),
                ref("plano_capturas", "plano_capturas_notas"),
                ref("capturas", "capturas_ffmpeg_plano", "Screenshots PNG nos instantes planejados."),
                ref("gerador", "gerador_notas_proposta"),
                ref("auditor", "auditor_sustentacao_notas"),
            ],
        ),
        _pipeline(
            "pipeline_inicial_reproducao_bug",
            "Fluxo 1 — Vídeo até reprodução de bug",
            "Transcrição opcional, capturas nos cliques RecBrothers e roteiro Markdown para reproduzir o bug.",
            [
                ref(
                    "preparacao",
                    "preparacao_transcricao",
                    "Carrega vídeo, JSON de cliques e transcreve áudio quando houver faixa de áudio.",
                ),
                ref("capturas", "capturas_ffmpeg_rec_brothers"),
                ref("gerador", "gerador_reproducao_bug"),
            ],
            entradas_aceitas=["video"],
        ),
        _pipeline(
            "pipeline_inicial_so_transcricao",
            "Fluxo 1 — Só transcrição",
            "Aceita vídeo ou áudio, transcreve e publica o texto no job — sem capturas nem geração de documento.",
            [
                ref(
                    "preparacao",
                    "preparacao_transcricao",
                    "Metadados do job e transcrição (extrai áudio do vídeo ou normaliza arquivo de áudio).",
                ),
                ref("resultado", "resultado_transcricao_markdown"),
            ],
            entradas_aceitas=["video", "audio"],
        ),
        _pipeline(
            "regeneracao_markdown",
            "Fluxo 2 — Regenerar documento inteiro",
            "Novo passe ao modelo sobre o tutorial atual (sem reprocessar o vídeo).",
            [
                ref("preparacao", "preparacao_reutilizacao_snapshot_regeneracao"),
                ref("gerador", "gerador_regeneracao_documento"),
                ref("verificacao_imagens", "verificacao_imagens_duplicadas", "Verificação de screenshots duplicadas no Markdown regenerado."),
                ref("auditor", "auditor_sustentacao_tutorial", "Verificação tutorial vs transcrição após a regeneração."),
                ref("preview_documento", "preview_documento_ui"),
            ],
        ),
        _pipeline(
            "revisao_profunda",
            "Fluxo 2 — Revisão profunda",
            "Plano estruturado, edição por tópicos e consolidação final.",
            [
                ref("preparacao", "preparacao_reutilizacao_snapshot_revisao"),
                ref("planejador", "planejador_revisao_profunda"),
                ref("editores", "editor_topico_revisao_profunda"),
                ref("consolidador", "consolidador_revisao_profunda"),
                ref("verificacao_imagens", "verificacao_imagens_duplicadas", "Verificação de screenshots duplicadas após a consolidação."),
                ref("auditor", "auditor_sustentacao_tutorial", "Verificação tutorial vs transcrição após a revisão profunda."),
                ref(
                    "preview_documento",
                    "preview_documento_ui",
                    "Pré-visualização pendente: comparativo antes/depois para aplicar ou descartar.",
                ),
            ],
        ),
        _pipeline(
            "edicao_parcial_secao",
            "Fluxo 2 — Edição parcial",
            "Interpreta o pedido, regenera só a região escolhida e gera pré-visualização para aplicar no editor.",
            [
                ref("escopo_edicao_secao", "escopo_edicao_secao"),
                ref("regeneracao_secao", "regeneracao_secao_parcial"),
                ref("redundancia_secao", "verificacao_redundancia_secao"),
                ref("preview_secao", "preview_secao_ui"),
            ],
        ),
    ]


def _preencher_pipelines_ids_nos_agentes_transcribrothers(
    agentes: dict[str, AgenteCatalogoDocumentacaoTranscribrothers],
    pipelines: list[PipelineCatalogoDocumentacaoTranscribrothers],
) -> list[AgenteCatalogoDocumentacaoTranscribrothers]:
    uso: dict[str, list[str]] = {aid: [] for aid in agentes}
    for pipeline in pipelines:
        for passo in pipeline.passos:
            if pipeline.id not in uso[passo.agente_id]:
                uso[passo.agente_id].append(pipeline.id)
    resultado: list[AgenteCatalogoDocumentacaoTranscribrothers] = []
    for agente in agentes.values():
        resultado.append(
            agente.model_copy(update={"pipelines_ids": uso.get(agente.id, [])}),
        )
    resultado.sort(key=lambda a: a.rotulo.casefold())
    return resultado


def obter_mapa_agentes_catalogo_sistema_transcribrothers() -> dict[str, AgenteCatalogoDocumentacaoTranscribrothers]:
    return _montar_agentes_catalogo_transcribrothers()


def obter_lista_pipelines_catalogo_sistema_transcribrothers() -> list[PipelineCatalogoDocumentacaoTranscribrothers]:
    return _montar_pipelines_catalogo_transcribrothers()


def obter_pipeline_catalogo_sistema_por_id_transcribrothers(
    pipeline_id: str,
) -> PipelineCatalogoDocumentacaoTranscribrothers | None:
    for p in _montar_pipelines_catalogo_transcribrothers():
        if p.id == pipeline_id:
            return p
    return None


def obter_agente_catalogo_sistema_por_id_transcribrothers(
    agente_id: str,
) -> AgenteCatalogoDocumentacaoTranscribrothers | None:
    return _montar_agentes_catalogo_transcribrothers().get(agente_id)


def pipeline_sistema_copiado_de_e_executavel_upload_transcribrothers(copiado_de: str) -> bool:
    """True se a pipeline (sistema ou custom com raiz em fluxo 1) pode ser usada no upload."""
    raiz = copiado_de
    while raiz and not raiz.startswith("pipeline_inicial_") and raiz != "regeneracao_markdown":
        # custom copiada de custom: seguir cadeia não implementada em profundidade;
        # usamos copiado_de direto da raiz gravada na duplicação
        break
    return raiz in PIPELINES_SISTEMA_EXECUTAVEIS_UPLOAD_TRANSCRIBROTHERS


def mapear_pipeline_sistema_para_destino_apos_transcricao_transcribrothers(
    pipeline_sistema_id: str,
) -> str | None:
    return {
        "pipeline_inicial_tutorial": "gerar_tutorial",
        "pipeline_inicial_notas_proposta": "notas_proposta_funcionalidade",
        "pipeline_inicial_reproducao_bug": "reproducao_bug",
        "pipeline_inicial_so_transcricao": "so_transcricao",
    }.get(pipeline_sistema_id)


def montar_resposta_catalogo_pipelines_disponiveis_documentacao_transcribrothers() -> (
    RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers
):
    agentes_map = _montar_agentes_catalogo_transcribrothers()
    pipelines = _montar_pipelines_catalogo_transcribrothers()
    return RespostaCatalogoPipelinesDisponiveisDocumentacaoTranscribrothers(
        pipeline_identificador=IDENTIFICADOR_VERSAO_PIPELINE_DIAGNOSTICO_TRANSCRIBROTHERS,
        agentes=_preencher_pipelines_ids_nos_agentes_transcribrothers(agentes_map, pipelines),
        pipelines=pipelines,
    )
