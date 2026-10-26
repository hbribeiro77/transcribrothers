/**
 * Quadros usados quando a vinheta entra entre dois trechos do vídeo.
 * O seguinte vira a imagem de fundo. O anterior dissolve na entrada.
 */

export type JanelaParaQuadroDaTransicaoTranscribrothers = {
  inicioVideoSegundos: number;
  fimVideoSegundos: number;
  idFonteVideo?: string | null;
};

export function fonte_de_tela_e_o_video_de_entrada_transcribrothers(idFonte: string | null | undefined): boolean {
  const id = (idFonte || "").trim();
  return !id || id === "entrada";
}

export function instantes_dos_quadros_da_transicao_do_separador_transcribrothers(opts: {
  janelas: JanelaParaQuadroDaTransicaoTranscribrothers[];
  indiceDaCueAnterior: number | null;
  instanteAtualDoVideo: number | null;
}): { seguinte: number; anterior: number | null } {
  const indice = opts.indiceDaCueAnterior;
  const anterior =
    indice != null && indice >= 0 && indice < opts.janelas.length ? opts.janelas[indice] : null;
  const candidataSeguinte =
    indice != null && indice >= 0 ? opts.janelas[indice + 1] : opts.janelas[0];
  const seguinte = candidataSeguinte && fonte_de_tela_e_o_video_de_entrada_transcribrothers(candidataSeguinte.idFonteVideo)
    ? candidataSeguinte.inicioVideoSegundos
    : Math.max(0, opts.instanteAtualDoVideo ?? 0);
  const instanteAnterior =
    anterior && fonte_de_tela_e_o_video_de_entrada_transcribrothers(anterior.idFonteVideo)
      ? Math.max(0, anterior.fimVideoSegundos - 0.05)
      : null;
  return { seguinte, anterior: instanteAnterior };
}
