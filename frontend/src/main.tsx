import React from "react";
import ReactDOM from "react-dom/client";
import { ComponenteAplicacaoTranscribrothersNavegacaoEntreProjetoECatalogoPipelines } from "./componente_aplicacao_transcribrothers_navegacao_entre_projeto_e_catalogo_pipelines.tsx";
import { ProvedorToastsFeedbackAcoesUiTranscribrothers } from "./provedor_contexto_e_hook_uso_toasts_feedback_acoes_ui_transcribrothers.tsx";
import "./estilos_globais_transcribrothers.css";
import "./estilos_css_modal_editor_anotacao_imagem_tutorial_fabric_js_transcribrothers.css";
import "./estilos_css_modo_inserir_imagem_asset_markdown_tutorial_preview_transcribrothers.css";
import "./estilos_css_player_video_job_controles_customizados_e_modal_ampliar_tela_maior_transcribrothers.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
      <ProvedorToastsFeedbackAcoesUiTranscribrothers>
        <ComponenteAplicacaoTranscribrothersNavegacaoEntreProjetoECatalogoPipelines />
      </ProvedorToastsFeedbackAcoesUiTranscribrothers>
  </React.StrictMode>,
);
