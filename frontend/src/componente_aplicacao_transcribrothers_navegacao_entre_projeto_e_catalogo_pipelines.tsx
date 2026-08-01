import { useCallback, useEffect, useState } from "react";
import { ComponentePaginaCatalogoPipelinesDisponiveisComPromptsPorEtapaTranscribrothers } from "./componente_pagina_catalogo_pipelines_disponiveis_com_prompts_por_etapa_transcribrothers.tsx";
import { PaginaPrincipalTranscribrothersFormularioDrivePreviewTutorial } from "./componente_pagina_principal_formulario_drive_preview_tutorial.tsx";

export type TelaAtivaAplicacaoTranscribrothers = "projeto" | "pipelines";

function lerTelaAtivaDaQueryStringTranscribrothers(): TelaAtivaAplicacaoTranscribrothers {
  if (typeof window === "undefined") return "projeto";
  const view = new URLSearchParams(window.location.search).get("view");
  // `video-narrado` é página dentro do projeto (não o catálogo de pipelines).
  return view === "pipelines" ? "pipelines" : "projeto";
}

function atualizarQueryViewNaUrlTranscribrothers(tela: TelaAtivaAplicacaoTranscribrothers) {
  if (typeof window === "undefined") return;
  const url = new URL(window.location.href);
  if (tela === "pipelines") {
    url.searchParams.set("view", "pipelines");
  } else {
    url.searchParams.delete("view");
  }
  window.history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`);
}

/**
 * Mantém a página do projeto montada ao ir para Pipelines (só oculta),
 * para «Voltar ao projeto» restaurar o job/markdown em memória.
 */
export function ComponenteAplicacaoTranscribrothersNavegacaoEntreProjetoECatalogoPipelines() {
  const [telaAtiva, setTelaAtiva] = useState<TelaAtivaAplicacaoTranscribrothers>(() =>
    lerTelaAtivaDaQueryStringTranscribrothers(),
  );
  /** Evita desmontar o catálogo a cada ida/volta (estado de edição no catálogo). */
  const [catalogoJaMontado, setCatalogoJaMontado] = useState(
    () => lerTelaAtivaDaQueryStringTranscribrothers() === "pipelines",
  );

  const irParaPipelines = useCallback(() => {
    setCatalogoJaMontado(true);
    setTelaAtiva("pipelines");
    atualizarQueryViewNaUrlTranscribrothers("pipelines");
  }, []);

  const irParaProjeto = useCallback(() => {
    setTelaAtiva("projeto");
    atualizarQueryViewNaUrlTranscribrothers("projeto");
  }, []);

  useEffect(() => {
    const onPopState = () => {
      const tela = lerTelaAtivaDaQueryStringTranscribrothers();
      if (tela === "pipelines") setCatalogoJaMontado(true);
      setTelaAtiva(tela);
    };
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  const projetoVisivel = telaAtiva === "projeto";
  const pipelinesVisivel = telaAtiva === "pipelines";

  return (
    <>
      <div
        className="tb-app-tela-projeto"
        hidden={!projetoVisivel}
        aria-hidden={!projetoVisivel}
      >
        <PaginaPrincipalTranscribrothersFormularioDrivePreviewTutorial
          onAbrirCatalogoPipelines={irParaPipelines}
          projetoVisivel={projetoVisivel}
        />
      </div>
      {catalogoJaMontado ? (
        <div
          className="tb-app-tela-pipelines"
          hidden={!pipelinesVisivel}
          aria-hidden={!pipelinesVisivel}
        >
          <ComponentePaginaCatalogoPipelinesDisponiveisComPromptsPorEtapaTranscribrothers
            onVoltarParaProjeto={irParaProjeto}
          />
        </div>
      ) : null}
    </>
  );
}
