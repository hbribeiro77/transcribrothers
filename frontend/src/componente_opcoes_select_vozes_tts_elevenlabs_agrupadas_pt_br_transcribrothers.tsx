import type { VozTtsElevenlabsUiTranscribrothers } from "./modulo_api_listar_vozes_tts_elevenlabs_transcribrothers.ts";
import {
  agruparVozesTtsElevenlabsPtBrEOutrasTranscribrothers,
  rotuloVozTtsElevenlabsParaSelectTranscribrothers,
} from "./modulo_util_rotulo_e_grupo_vozes_tts_elevenlabs_pt_br_transcribrothers.ts";

function renderizarOpcaoVozTtsElevenlabsTranscribrothers(op: VozTtsElevenlabsUiTranscribrothers) {
  return (
    <option key={op.id} value={op.id} title={op.id}>
      {rotuloVozTtsElevenlabsParaSelectTranscribrothers(op)}
    </option>
  );
}

export function ComponenteOpcoesSelectVozesTtsElevenlabsAgrupadasPtBrTranscribrothers({
  vozes,
}: {
  vozes: VozTtsElevenlabsUiTranscribrothers[];
}) {
  const { ptBr, outras } = agruparVozesTtsElevenlabsPtBrEOutrasTranscribrothers(vozes);
  if (ptBr.length > 0 && outras.length > 0) {
    return (
      <>
        <optgroup label="Português do Brasil">
          {ptBr.map(renderizarOpcaoVozTtsElevenlabsTranscribrothers)}
        </optgroup>
        <optgroup label="Outras vozes">{outras.map(renderizarOpcaoVozTtsElevenlabsTranscribrothers)}</optgroup>
      </>
    );
  }
  return <>{[...ptBr, ...outras].map(renderizarOpcaoVozTtsElevenlabsTranscribrothers)}</>;
}
