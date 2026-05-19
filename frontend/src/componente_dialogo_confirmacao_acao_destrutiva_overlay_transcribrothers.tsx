import { useEffect } from "react";
import "./estilos_css_componente_dialogo_confirmacao_acao_destrutiva_overlay_transcribrothers.css";

export type PropsComponenteDialogoConfirmacaoAcaoDestrutivaOverlayTranscribrothers = {
  aberto: boolean;
  titulo: string;
  mensagem: string;
  rotuloConfirmar?: string;
  rotuloCancelar?: string;
  varianteConfirmar?: "destrutiva" | "neutra";
  processando?: boolean;
  aoConfirmar: () => void;
  aoCancelar: () => void;
};

export function ComponenteDialogoConfirmacaoAcaoDestrutivaOverlayTranscribrothers({
  aberto,
  titulo,
  mensagem,
  rotuloConfirmar = "Confirmar",
  rotuloCancelar = "Cancelar",
  varianteConfirmar = "destrutiva",
  processando = false,
  aoConfirmar,
  aoCancelar,
}: PropsComponenteDialogoConfirmacaoAcaoDestrutivaOverlayTranscribrothers) {
  useEffect(() => {
    if (!aberto) return;

    const aoTeclar = (evento: KeyboardEvent) => {
      if (evento.key === "Escape" && !processando) {
        aoCancelar();
      }
    };

    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
  }, [aberto, aoCancelar, processando]);

  if (!aberto) return null;

  const classeConfirmar =
    varianteConfirmar === "neutra"
      ? "tb-dialogo-confirmacao-btn tb-dialogo-confirmacao-btn--neutro"
      : "tb-dialogo-confirmacao-btn tb-dialogo-confirmacao-btn--confirmar";

  return (
    <div
      className="tb-dialogo-confirmacao-overlay"
      role="presentation"
      onClick={processando ? undefined : aoCancelar}
    >
      <div
        className="tb-dialogo-confirmacao-painel"
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="tb-dialogo-confirmacao-titulo"
        aria-describedby="tb-dialogo-confirmacao-mensagem"
        onClick={(evento) => evento.stopPropagation()}
      >
        <header className="tb-dialogo-confirmacao-cabecalho">
          <h2 id="tb-dialogo-confirmacao-titulo" className="tb-dialogo-confirmacao-titulo">
            {titulo}
          </h2>
        </header>

        <div className="tb-dialogo-confirmacao-corpo">
          <p id="tb-dialogo-confirmacao-mensagem" className="tb-dialogo-confirmacao-mensagem">
            {mensagem}
          </p>
        </div>

        <footer className="tb-dialogo-confirmacao-rodape">
          <button
            type="button"
            className="tb-dialogo-confirmacao-btn tb-dialogo-confirmacao-btn--cancelar"
            disabled={processando}
            onClick={aoCancelar}
          >
            {rotuloCancelar}
          </button>
          <button
            type="button"
            className={classeConfirmar}
            disabled={processando}
            onClick={aoConfirmar}
          >
            {processando ? "Aguarde…" : rotuloConfirmar}
          </button>
        </footer>
      </div>
    </div>
  );
}
