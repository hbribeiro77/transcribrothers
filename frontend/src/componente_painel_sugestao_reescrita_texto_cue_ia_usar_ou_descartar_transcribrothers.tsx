type Props = {
  sugestao: string;
  desabilitado?: boolean;
  onUsar: () => void;
  onDescartar: () => void;
};

/** Painel compartilhado: mostra sugestão IA com Usar / Descartar (não aplica sozinha). */
export function ComponentePainelSugestaoReescritaTextoCueIaUsarOuDescartarTranscribrothers({
  sugestao,
  desabilitado = false,
  onUsar,
  onDescartar,
}: Props) {
  const texto = (sugestao || "").trim();
  if (!texto) return null;
  return (
    <div className="tb-painel-sugestao-reescrita-cue-ia" role="note">
      <div className="tb-painel-sugestao-reescrita-cue-ia-cabecalho">
        <strong>Sugestão da IA</strong> — ainda não aplicada
      </div>
      <div className="tb-painel-sugestao-reescrita-cue-ia-texto">{texto}</div>
      <div className="tb-painel-sugestao-reescrita-cue-ia-acoes">
        <button
          type="button"
          className="tb-btn-secundario"
          disabled={desabilitado}
          onClick={onUsar}
        >
          Usar sugestão
        </button>
        <button
          type="button"
          className="tb-btn-secundario"
          disabled={desabilitado}
          onClick={onDescartar}
        >
          Descartar
        </button>
      </div>
    </div>
  );
}
