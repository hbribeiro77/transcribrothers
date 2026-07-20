import { useCallback, useEffect, useState } from "react";

import { atualizarAgenteCustomApiTranscribrothers } from "./modulo_api_crud_pipelines_e_agentes_custom_transcribrothers.ts";
import type {
  AgenteCatalogoApiTranscribrothers,
  PromptCatalogoPassoPipelineApiTranscribrothers,
  RespostaCatalogoPipelinesApiTranscribrothers,
} from "./tipos_catalogo_pipelines_api_transcribrothers.ts";
import { usarToastFeedbackAcoesUiTranscribrothers } from "./provedor_contexto_e_hook_uso_toasts_feedback_acoes_ui_transcribrothers.tsx";

export type ComponentePainelEdicaoInlineAgenteCustomCatalogoPipelinesTranscribrothersProps = {
  agente: AgenteCatalogoApiTranscribrothers;
  descricaoPasso?: string;
  modelosLitellm: string[];
  modeloPadrao: string;
  modoEdicao: boolean;
  onSalvo: (catalogo: RespostaCatalogoPipelinesApiTranscribrothers) => void;
  onCancelarEdicao?: () => void;
  desabilitado?: boolean;
};

function PainelPromptsAgenteSomenteLeituraTranscribrothers({
  descricao,
  prompts,
}: {
  descricao: string;
  prompts: PromptCatalogoPassoPipelineApiTranscribrothers[];
}) {
  const { pushToast } = usarToastFeedbackAcoesUiTranscribrothers();

  const copiarPrompt = useCallback(
    (prompt: PromptCatalogoPassoPipelineApiTranscribrothers) => {
      const texto = (prompt.texto || "").trim() || (prompt.observacao || "").trim();
      if (!texto) {
        pushToast("Não há texto para copiar neste item.", "info");
        return;
      }
      void navigator.clipboard.writeText(texto).then(
        () => pushToast(`Copiado: ${prompt.rotulo}`, "success"),
        () => pushToast("Não foi possível copiar para a área de transferência.", "error"),
      );
    },
    [pushToast],
  );

  return (
    <>
      {descricao ? <p className="tb-catalogo-pipelines-descricao-passo">{descricao}</p> : null}
      {prompts.length > 0 ? (
        <div className="tb-catalogo-pipelines-prompts-secao">
          <h4 className="tb-catalogo-pipelines-prompts-titulo">Prompts e textos fixos</h4>
          {prompts.map((prompt, indice) => (
            <div key={`${prompt.chave}-${indice}`} className="tb-catalogo-pipelines-prompt-bloco">
              <div className="tb-catalogo-pipelines-prompt-cabecalho">
                <span className="tb-catalogo-pipelines-prompt-rotulo">{prompt.rotulo}</span>
                <span className="tb-catalogo-pipelines-prompt-tipo">{prompt.tipo}</span>
                {(prompt.texto || "").trim() ? (
                  <button type="button" className="tb-linkbtn" onClick={() => copiarPrompt(prompt)}>
                    Copiar
                  </button>
                ) : null}
              </div>
              {prompt.observacao ? (
                <p className="tb-catalogo-pipelines-prompt-observacao">{prompt.observacao}</p>
              ) : null}
              {(prompt.texto || "").trim() ? (
                <pre className="tb-catalogo-pipelines-prompt-pre" tabIndex={0}>
                  {prompt.texto}
                </pre>
              ) : null}
              {prompt.fonte_modulo ? (
                <p className="tb-catalogo-pipelines-prompt-fonte">
                  Fonte: <code>{prompt.fonte_modulo}</code>
                </p>
              ) : null}
            </div>
          ))}
        </div>
      ) : (
        <p className="tb-muted">Nenhum prompt fixo catalogado para este agente.</p>
      )}
    </>
  );
}

export function ComponentePainelEdicaoInlineAgenteCustomCatalogoPipelinesTranscribrothers({
  agente,
  descricaoPasso,
  modelosLitellm,
  modeloPadrao,
  onSalvo,
  onCancelarEdicao,
  desabilitado = false,
  modoEdicao,
}: ComponentePainelEdicaoInlineAgenteCustomCatalogoPipelinesTranscribrothersProps) {
  const { pushToast } = usarToastFeedbackAcoesUiTranscribrothers();
  const [rotulo, setRotulo] = useState(agente.rotulo);
  const [descricao, setDescricao] = useState(agente.descricao);
  const [modelo, setModelo] = useState(agente.modelo_litellm ?? "");
  const [promptsTexto, setPromptsTexto] = useState<Record<string, string>>({});
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    setRotulo(agente.rotulo);
    setDescricao(agente.descricao);
    setModelo(agente.modelo_litellm ?? "");
    const mapa: Record<string, string> = {};
    for (const p of agente.prompts) {
      mapa[p.chave] = p.texto ?? "";
    }
    setPromptsTexto(mapa);
  }, [agente]);

  const salvar = useCallback(async () => {
    setSalvando(true);
    try {
      const prompts = agente.prompts.map((p) => ({
        chave: p.chave,
        tipo: p.tipo,
        rotulo: p.rotulo,
        texto: promptsTexto[p.chave] ?? p.texto ?? "",
        observacao: p.observacao ?? null,
      }));
      const catalogo = await atualizarAgenteCustomApiTranscribrothers(agente.id, {
        rotulo: rotulo.trim(),
        descricao,
        modelo_litellm: modelo.trim() || null,
        prompts,
      });
      pushToast("Agente atualizado.", "success");
      onSalvo(catalogo);
      onCancelarEdicao?.();
    } catch (e: unknown) {
      pushToast(e instanceof Error ? e.message : "Falha ao salvar agente.", "error");
    } finally {
      setSalvando(false);
    }
  }, [agente, descricao, modelo, onCancelarEdicao, onSalvo, promptsTexto, pushToast, rotulo]);

  const bloqueado = desabilitado || salvando;

  if (!agente.editavel || !modoEdicao) {
    return (
      <>
        <p className="tb-catalogo-pipelines-agente-ref">
          Agente: <strong>{agente.rotulo}</strong> <code className="tb-code-inline">{agente.id}</code>
        </p>
        <PainelPromptsAgenteSomenteLeituraTranscribrothers
          descricao={descricaoPasso ?? agente.descricao}
          prompts={agente.prompts}
        />
      </>
    );
  }

  const promptsEditaveis = agente.prompts.filter(
    (p) => (p.texto || "").trim() || (promptsTexto[p.chave] || "").trim() || p.tipo !== "observacao",
  );

  return (
    <div className="tb-catalogo-painel-agente-inline">
      <p className="tb-catalogo-pipelines-agente-ref">
        Agente: <strong>{agente.rotulo}</strong>{" "}
        <code className="tb-code-inline">{agente.handler_chave ?? agente.id}</code>
        <span className="tb-catalogo-badge tb-catalogo-badge--custom tb-catalogo-painel-agente-inline-badge">
          Editável
        </span>
      </p>
      <p className="tb-muted tb-catalogo-painel-agente-aviso-compartilhado">
        Alterações valem para todas as pipelines que usam este agente. Jobs já iniciados não mudam. Para isolar, use
        Duplicar agente no catálogo.
      </p>
      {descricaoPasso ? <p className="tb-catalogo-pipelines-descricao-passo">{descricaoPasso}</p> : null}
      <label className="tb-field">
        <span className="tb-field-label">Nome do agente</span>
        <input className="tb-input" value={rotulo} onChange={(e) => setRotulo(e.target.value)} disabled={bloqueado} />
      </label>
      <label className="tb-field">
        <span className="tb-field-label">Descrição</span>
        <textarea
          className="tb-input"
          rows={2}
          value={descricao}
          onChange={(e) => setDescricao(e.target.value)}
          disabled={bloqueado}
        />
      </label>
      <label className="tb-field">
        <span className="tb-field-label">Modelo LiteLLM (opcional)</span>
        <select className="tb-select" value={modelo} onChange={(e) => setModelo(e.target.value)} disabled={bloqueado}>
          <option value="">Padrão do job ({modeloPadrao || "servidor"})</option>
          {modelosLitellm.map((m) => (
            <option key={m} value={m}>
              {m}
            </option>
          ))}
        </select>
      </label>
      {promptsEditaveis.length > 0 ? (
        <div className="tb-catalogo-pipelines-prompts-secao">
          <h4 className="tb-catalogo-pipelines-prompts-titulo">Prompts</h4>
          {promptsEditaveis.map((p) => (
            <label key={p.chave} className="tb-field tb-catalogo-painel-agente-inline-prompt">
              <span className="tb-field-label">
                {p.rotulo} <code className="tb-code-inline">{p.chave}</code>
              </span>
              {p.observacao ? <p className="tb-catalogo-pipelines-prompt-observacao">{p.observacao}</p> : null}
              <textarea
                className="tb-input tb-catalogo-modal-prompt-textarea"
                rows={6}
                value={promptsTexto[p.chave] ?? ""}
                onChange={(e) => setPromptsTexto((prev) => ({ ...prev, [p.chave]: e.target.value }))}
                disabled={bloqueado}
              />
            </label>
          ))}
        </div>
      ) : null}
      <div className="tb-catalogo-painel-agente-inline-acoes">
        {onCancelarEdicao ? (
          <button type="button" className="tb-linkbtn" onClick={onCancelarEdicao} disabled={bloqueado}>
            Descartar
          </button>
        ) : null}
        <button type="button" className="tb-primary" onClick={() => void salvar()} disabled={bloqueado}>
          {salvando ? "Salvando…" : "Salvar agente"}
        </button>
      </div>
    </div>
  );
}
