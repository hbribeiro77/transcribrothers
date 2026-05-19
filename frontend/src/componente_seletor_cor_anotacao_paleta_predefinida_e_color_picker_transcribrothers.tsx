import type * as React from "react";
import { PALETA_CORES_PREDEFINIDAS_FERRAMENTAS_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS } from "./constante_paleta_cores_predefinidas_ferramentas_anotacao_imagem_tutorial_transcribrothers.ts";

type PropsSeletorCorAnotacaoPaletaEColorPickerTranscribrothers = {
  corAtual: string;
  aoSelecionarCor: (hex: string) => void;
  tituloSeletor?: string;
};

export function ComponenteSeletorCorAnotacaoPaletaPredefinidaEColorPickerTranscribrothers({
  corAtual,
  aoSelecionarCor,
  tituloSeletor = "Cor do traço e do texto",
}: PropsSeletorCorAnotacaoPaletaEColorPickerTranscribrothers) {
  const corNormalizada = corAtual.toLowerCase();

  return (
    <div className="tb-anotacao-seletor-cor-grupo" role="group" aria-label={tituloSeletor}>
      <span className="tb-anotacao-seletor-cor-rotulo">Cores</span>
      <div className="tb-anotacao-paleta-cores" role="list">
        {PALETA_CORES_PREDEFINIDAS_FERRAMENTAS_ANOTACAO_IMAGEM_TUTORIAL_TRANSCRIBROTHERS.map((item) => (
          <button
            key={item.hex}
            type="button"
            role="listitem"
            className={[
              "tb-anotacao-paleta-cor",
              item.hex.toLowerCase() === "#ffffff" ? "tb-anotacao-paleta-cor-branca" : "",
              corNormalizada === item.hex.toLowerCase() ? "tb-anotacao-paleta-cor-ativa" : "",
            ]
              .filter(Boolean)
              .join(" ")}
            title={item.rotulo}
            aria-label={item.rotulo}
            aria-pressed={corNormalizada === item.hex.toLowerCase()}
            style={{ backgroundColor: item.hex }}
            onClick={() => aoSelecionarCor(item.hex)}
          />
        ))}
      </div>
      <label className="tb-anotacao-seletor-cor tb-anotacao-seletor-cor-custom" title="Cor personalizada">
        <span className="sr-only">Cor personalizada</span>
        <input
          type="color"
          value={corAtual}
          onChange={(e) => aoSelecionarCor(e.target.value)}
          aria-label="Seletor de cor personalizada"
        />
      </label>
    </div>
  );
}
