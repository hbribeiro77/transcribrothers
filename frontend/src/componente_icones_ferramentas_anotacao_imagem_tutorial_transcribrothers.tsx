import type { ReactNode } from "react";
import type { FerramentaAnotacaoImagemTutorialTranscribrothers } from "./tipos_ferramenta_anotacao_imagem_tutorial_transcribrothers.ts";

function SvgIconeFerramentaAnotacaoTranscribrothers({ children }: { children: ReactNode }) {
  return (
    <svg className="tb-icone-ferramenta-anotacao-imagem" viewBox="0 0 24 24" width="18" height="18" aria-hidden>
      {children}
    </svg>
  );
}

export function IconeFerramentaAnotacaoImagemTutorialTranscribrothers({
  ferramenta,
}: {
  ferramenta: FerramentaAnotacaoImagemTutorialTranscribrothers;
}) {
  switch (ferramenta) {
    case "selecionar":
      return (
        <SvgIconeFerramentaAnotacaoTranscribrothers>
          <path
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            d="M4 4l7 16 2.5-6.5L20 11 4 4z"
          />
        </SvgIconeFerramentaAnotacaoTranscribrothers>
      );
    case "destaque":
      return (
        <SvgIconeFerramentaAnotacaoTranscribrothers>
          <path fill="currentColor" opacity="0.35" d="M4 14h16v4H4z" />
          <path
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            d="M6 18h12M8 14l4-8 4 8"
          />
        </SvgIconeFerramentaAnotacaoTranscribrothers>
      );
    case "retangulo":
      return (
        <SvgIconeFerramentaAnotacaoTranscribrothers>
          <rect
            x="5"
            y="7"
            width="14"
            height="10"
            rx="1"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          />
        </SvgIconeFerramentaAnotacaoTranscribrothers>
      );
    case "elipse":
      return (
        <SvgIconeFerramentaAnotacaoTranscribrothers>
          <ellipse cx="12" cy="12" rx="7" ry="5" fill="none" stroke="currentColor" strokeWidth="2" />
        </SvgIconeFerramentaAnotacaoTranscribrothers>
      );
    case "linha":
      return (
        <SvgIconeFerramentaAnotacaoTranscribrothers>
          <path
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            d="M5 19L19 5"
          />
        </SvgIconeFerramentaAnotacaoTranscribrothers>
      );
    case "seta":
      return (
        <SvgIconeFerramentaAnotacaoTranscribrothers>
          <path
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M5 19L19 5M19 5h-8M19 5v8"
          />
        </SvgIconeFerramentaAnotacaoTranscribrothers>
      );
    case "texto":
      return (
        <SvgIconeFerramentaAnotacaoTranscribrothers>
          <text
            x="12"
            y="16.5"
            textAnchor="middle"
            fontSize="13"
            fontWeight="700"
            fontFamily="system-ui, Segoe UI, sans-serif"
            fill="currentColor"
          >
            T
          </text>
        </SvgIconeFerramentaAnotacaoTranscribrothers>
      );
    default:
      return null;
  }
}

export function IconeExcluirSelecaoAnotacaoImagemTutorialTranscribrothers() {
  return (
    <svg className="tb-icone-ferramenta-anotacao-imagem" viewBox="0 0 24 24" width="18" height="18" aria-hidden>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M4 7h16M9 7V5a1 1 0 011-1h4a1 1 0 011 1v2m2 0v12a2 2 0 01-2 2H8a2 2 0 01-2-2V7h12zM10 11v6M14 11v6"
      />
    </svg>
  );
}

export function IconeAjustarAreaVisualizacaoCanvasAnotacaoImagemTutorialTranscribrothers() {
  return (
    <svg className="tb-icone-ferramenta-anotacao-imagem" viewBox="0 0 24 24" width="18" height="18" aria-hidden>
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M4 9V4h5M15 4h5v5M20 15v5h-5M9 20H4v-5"
      />
    </svg>
  );
}

export function obterRotuloAcessivelFerramentaAnotacaoImagemTutorialTranscribrothers(
  ferramenta: FerramentaAnotacaoImagemTutorialTranscribrothers,
): string {
  const rotulos: Record<FerramentaAnotacaoImagemTutorialTranscribrothers, string> = {
    selecionar: "Selecionar",
    destaque: "Destaque",
    retangulo: "Retângulo",
    elipse: "Elipse",
    linha: "Linha reta",
    seta: "Seta",
    texto: "Texto",
  };
  return rotulos[ferramenta];
}
