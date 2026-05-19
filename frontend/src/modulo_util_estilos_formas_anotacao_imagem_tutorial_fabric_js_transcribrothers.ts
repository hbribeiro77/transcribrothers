/** Cores e estilos padrão das formas no editor de anotação (Fabric.js). */

export const COR_PADRAO_FERRAMENTAS_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS = "#2563eb";

export const ESPESSURA_TRACO_PADRAO_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS = 3;

export const PREENCHIMENTO_VAZADO_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS = "transparent";

export function obterEstiloContornoFormaVazadaAnotacaoImagemTutorialTranscribrothers(cor: string): {
  fill: string;
  stroke: string;
  strokeWidth: number;
} {
  return {
    fill: PREENCHIMENTO_VAZADO_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS,
    stroke: cor,
    strokeWidth: ESPESSURA_TRACO_PADRAO_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS,
  };
}

/** Amarelo semitransparente clássico do «Destaque» (sem borda). */
export const COR_DESTAQUE_AMARELO_PADRAO_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS = "#facc15";

const OPACIDADE_PREENCHIMENTO_DESTAQUE_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS = 0.35;

export function converterCorHexParaRgbaComOpacidadeTranscribrothers(
  corHex: string,
  opacidade: number,
): string {
  const limpo = corHex.trim().replace("#", "");
  if (limpo.length !== 6) {
    return `rgba(250, 204, 21, ${opacidade})`;
  }
  const r = Number.parseInt(limpo.slice(0, 2), 16);
  const g = Number.parseInt(limpo.slice(2, 4), 16);
  const b = Number.parseInt(limpo.slice(4, 6), 16);
  if ([r, g, b].some((n) => Number.isNaN(n))) {
    return `rgba(250, 204, 21, ${opacidade})`;
  }
  return `rgba(${r}, ${g}, ${b}, ${opacidade})`;
}

/** Retângulo preenchido semitransparente, sem contorno visível. */
export function obterEstiloRetanguloDestaqueSemitransparenteSemBordaAnotacaoImagemTutorialTranscribrothers(
  corHex: string = COR_DESTAQUE_AMARELO_PADRAO_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS,
): {
  fill: string;
  stroke: string;
  strokeWidth: number;
} {
  return {
    fill: converterCorHexParaRgbaComOpacidadeTranscribrothers(
      corHex,
      OPACIDADE_PREENCHIMENTO_DESTAQUE_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS,
    ),
    stroke: "transparent",
    strokeWidth: 0,
  };
}

export const PROPRIEDADE_FABRIC_TIPO_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS = "tbTipoAnotacaoImagemTutorial";

export const VALOR_TIPO_ANOTACAO_DESTAQUE_SEMITRANSPARENTE_TRANSCRIBROTHERS = "destaque_semitransparente";
