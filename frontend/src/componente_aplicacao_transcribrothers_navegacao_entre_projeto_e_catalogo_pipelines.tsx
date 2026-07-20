import { useCallback, useEffect, useState } from "react";
import { ComponentePaginaCatalogoPipelinesDisponiveisComPromptsPorEtapaTranscribrothers } from "./componente_pagina_catalogo_pipelines_disponiveis_com_prompts_por_etapa_transcribrothers.tsx";
import { PaginaPrincipalTranscribrothersFormularioDrivePreviewTutorial } from "./componente_pagina_principal_formulario_drive_preview_tutorial.tsx";

export type TelaAtivaAplicacaoTranscribrothers = "projeto" | "pipelines";

function lerTelaAtivaDaQueryStringTranscribrothers(): TelaAtivaAplicacaoTranscribrothers {
  if (typeof window === "undefined") return "projeto";
  const view = new URLSearchParams(window.location.search).get("view");
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

export function ComponenteAplicacaoTranscribrothersNavegacaoEntreProjetoECatalogoPipelines() {
  const [telaAtiva, setTelaAtiva] = useState<TelaAtivaAplicacaoTranscribrothers>(() =>
    lerTelaAtivaDaQueryStringTranscribrothers(),
  );

  const irParaPipelines = useCallback(() => {
    setTelaAtiva("pipelines");
    atualizarQueryViewNaUrlTranscribrothers("pipelines");
  }, []);

  const irParaProjeto = useCallback(() => {
    setTelaAtiva("projeto");
    atualizarQueryViewNaUrlTranscribrothers("projeto");
  }, []);

  useEffect(() => {
    const onPopState = () => setTelaAtiva(lerTelaAtivaDaQueryStringTranscribrothers());
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  if (telaAtiva === "pipelines") {
    return (
      <ComponentePaginaCatalogoPipelinesDisponiveisComPromptsPorEtapaTranscribrothers
        onVoltarParaProjeto={irParaProjeto}
      />
    );
  }

  return (
    <PaginaPrincipalTranscribrothersFormularioDrivePreviewTutorial onAbrirCatalogoPipelines={irParaPipelines} />
  );
}
