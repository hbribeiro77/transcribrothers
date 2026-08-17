import { useId } from "react";

import {
  TEMPERATURA_TTS_NARRACAO_MAX_TRANSCRIBROTHERS,
  TEMPERATURA_TTS_NARRACAO_MIN_TRANSCRIBROTHERS,
  TEMPERATURA_TTS_NARRACAO_STEP_TRANSCRIBROTHERS,
  formatarTemperaturaTtsNarracaoParaUiTranscribrothers,
  normalizarTemperaturaTtsNarracaoTranscribrothers,
} from "./modulo_perfil_motor_sintese_tts_narracao_transcribrothers.ts";
import "./estilos_css_controle_slider_temperatura_tts_narracao_com_ajuda_transcribrothers.css";

type Props = {
  valor: number;
  desabilitado?: boolean;
  /** `campo` = grid da modal de escopo; `compacto` = cabeçalho da modal de editar. */
  variante?: "campo" | "compacto";
  idInput?: string;
  onChange: (temperatura: number) => void;
};

export function ComponenteControleSliderTemperaturaTtsNarracaoComAjudaTranscribrothers({
  valor,
  desabilitado = false,
  variante = "campo",
  idInput,
  onChange,
}: Props) {
  const idGerado = useId();
  const id = idInput || `${idGerado}-slider-temperatura-tts`;
  const valorNorm = normalizarTemperaturaTtsNarracaoTranscribrothers(valor);
  const valorTexto = formatarTemperaturaTtsNarracaoParaUiTranscribrothers(valorNorm);

  return (
    <div
      className={
        variante === "compacto"
          ? "tb-controle-temperatura-tts tb-controle-temperatura-tts--compacto"
          : "tb-controle-temperatura-tts"
      }
    >
      <div className="tb-controle-temperatura-tts-label-linha">
        <label className="tb-controle-temperatura-tts-rotulo" htmlFor={id}>
          Temperatura
        </label>
        <span className="tb-controle-temperatura-tts-valor" aria-live="polite">
          {valorTexto}
        </span>
        <details className="tb-controle-temperatura-tts-ajuda">
          <summary
            className="tb-controle-temperatura-tts-ajuda-resumo"
            aria-label="Ajuda sobre temperatura TTS"
            title="Ajuda sobre temperatura TTS"
          >
            <svg
              className="tb-controle-temperatura-tts-ajuda-icone"
              width="16"
              height="16"
              viewBox="0 0 16 16"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
              aria-hidden="true"
            >
              <circle cx="8" cy="8" r="6.25" stroke="currentColor" strokeWidth="1.5" />
              <path
                d="M8 7.25v4"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
              />
              <circle cx="8" cy="5.1" r="0.9" fill="currentColor" />
            </svg>
          </summary>
          <div className="tb-controle-temperatura-tts-ajuda-popover" role="note">
            <p>
              Menor valor = fala mais estável/repetível; maior = mais variação. O padrão do
              Transcribrothers é <strong>0,4</strong>. Em testes internos, <strong>0,2</strong>{" "}
              chegou a “travar” títulos (entonação engessada).
            </p>
          </div>
        </details>
      </div>
      <input
        id={id}
        className="tb-controle-temperatura-tts-slider"
        type="range"
        min={TEMPERATURA_TTS_NARRACAO_MIN_TRANSCRIBROTHERS}
        max={TEMPERATURA_TTS_NARRACAO_MAX_TRANSCRIBROTHERS}
        step={TEMPERATURA_TTS_NARRACAO_STEP_TRANSCRIBROTHERS}
        value={valorNorm}
        disabled={desabilitado}
        aria-valuemin={TEMPERATURA_TTS_NARRACAO_MIN_TRANSCRIBROTHERS}
        aria-valuemax={TEMPERATURA_TTS_NARRACAO_MAX_TRANSCRIBROTHERS}
        aria-valuenow={valorNorm}
        aria-valuetext={valorTexto}
        onChange={(e) =>
          onChange(normalizarTemperaturaTtsNarracaoTranscribrothers(e.target.value))
        }
      />
    </div>
  );
}
