/** Liga/desliga uma chave num mapa de “aberto” (ex.: detalhe da cue). */
export function alternarChaveMapaAbertoUiTranscribrothers(
  atual: Record<string, true>,
  chave: string,
): Record<string, true> {
  const next = { ...atual };
  if (next[chave]) delete next[chave];
  else next[chave] = true;
  return next;
}
