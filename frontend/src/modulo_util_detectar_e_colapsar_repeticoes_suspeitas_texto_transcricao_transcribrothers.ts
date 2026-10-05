/**
 * Detecta loops de palavra/n-grama na transcrição (alucinação típica de STT) e aplica colapso com aceite do usuário.
 */

export type OcorrenciaRepeticaoSuspeitaTextoTranscricaoTranscribrothers = {
  id: string;
  inicio: number;
  fim: number;
  textoOriginal: string;
  textoColapsado: string;
  repeticoes: number;
  nPalavrasUnidade: number;
  marcadaPorPadrao: boolean;
};

export const MIN_REPETICOES_DETECCAO_SUSPEITA_TRANSCRICAO_TRANSCRIBROTHERS = 4;
export const LIMIAR_REPETICOES_MARCADA_POR_PADRAO_TRANSCRICAO_TRANSCRIBROTHERS = 8;

const CLASSE_PALAVRA_TRANSCRICAO_TRANSCRIBROTHERS = String.raw`[\p{L}\p{N}]+`;

function montarRegexUnidadeRepetidaTranscricaoTranscribrothers(
  nPalavras: number,
  minRepeticoes: number,
): RegExp {
  const p = CLASSE_PALAVRA_TRANSCRICAO_TRANSCRIBROTHERS;
  const unidade =
    nPalavras <= 1 ? `(${p})` : `(${p}(?:\\s+${p}){${nPalavras - 1}})`;
  const sep = String.raw`(?:\s*,\s*|\s+)`;
  const extra = Math.max(1, minRepeticoes - 1);
  return new RegExp(`${unidade}(?:${sep}\\1){${extra},}`, "giu");
}

function contarRepeticoesUnidadeNoTrechoTranscribrothers(trecho: string, unidade: string): number {
  const sep = /^(?:\s*,\s*|\s+)/;
  let rest = trecho;
  let n = 0;
  const alvo = unidade.toLowerCase();
  while (rest.length > 0) {
    if (!rest.toLowerCase().startsWith(alvo)) break;
    n += 1;
    rest = rest.slice(unidade.length);
    if (!rest) break;
    const mSep = rest.match(sep);
    if (!mSep) break;
    rest = rest.slice(mSep[0].length);
  }
  return n;
}

function intervalosSeSobrepoemTranscribrothers(
  aIni: number,
  aFim: number,
  bIni: number,
  bFim: number,
): boolean {
  return aIni < bFim && aFim > bIni;
}

export function detectarOcorrenciasRepeticaoSuspeitaEmTextoTranscricaoTranscribrothers(
  texto: string,
  opcoes?: {
    minRepeticoes?: number;
    limiarMarcadaPorPadrao?: number;
  },
): OcorrenciaRepeticaoSuspeitaTextoTranscricaoTranscribrothers[] {
  const fonte = texto || "";
  if (!fonte.trim()) return [];
  const minRep =
    opcoes?.minRepeticoes ?? MIN_REPETICOES_DETECCAO_SUSPEITA_TRANSCRICAO_TRANSCRIBROTHERS;
  const limiarMarcada =
    opcoes?.limiarMarcadaPorPadrao ?? LIMIAR_REPETICOES_MARCADA_POR_PADRAO_TRANSCRICAO_TRANSCRIBROTHERS;
  const ocupados: { ini: number; fim: number }[] = [];
  const saida: OcorrenciaRepeticaoSuspeitaTextoTranscricaoTranscribrothers[] = [];
  let seq = 0;

  for (const nPalavras of [3, 2, 1]) {
    const re = montarRegexUnidadeRepetidaTranscricaoTranscribrothers(nPalavras, minRep);
    re.lastIndex = 0;
    let m: RegExpExecArray | null;
    while ((m = re.exec(fonte)) !== null) {
      if (!m[0] || !m[1]) {
        re.lastIndex += 1;
        continue;
      }
      const ini = m.index;
      const fim = ini + m[0].length;
      if (ocupados.some((o) => intervalosSeSobrepoemTranscribrothers(ini, fim, o.ini, o.fim))) {
        continue;
      }
      const unidade = m[1];
      if (nPalavras > 1) {
        const tokensUnidade = unidade.toLowerCase().split(/\s+/).filter(Boolean);
        if (new Set(tokensUnidade).size <= 1) continue;
      }
      const repeticoes = contarRepeticoesUnidadeNoTrechoTranscribrothers(m[0], unidade);
      if (repeticoes < minRep) continue;
      ocupados.push({ ini, fim });
      seq += 1;
      saida.push({
        id: `rep-${seq}-${ini}-${fim}`,
        inicio: ini,
        fim,
        textoOriginal: m[0],
        textoColapsado: unidade,
        repeticoes,
        nPalavrasUnidade: nPalavras,
        marcadaPorPadrao: repeticoes >= limiarMarcada,
      });
    }
  }

  saida.sort((a, b) => a.inicio - b.inicio);
  return saida;
}

export function aplicarColapsoOcorrenciasRepeticaoSelecionadasEmTextoTranscricaoTranscribrothers(
  texto: string,
  ocorrencias: readonly OcorrenciaRepeticaoSuspeitaTextoTranscricaoTranscribrothers[],
  idsSelecionados: readonly string[],
): string {
  const ids = new Set(idsSelecionados);
  const escolhidas = ocorrencias
    .filter((o) => ids.has(o.id))
    .slice()
    .sort((a, b) => b.inicio - a.inicio);
  let out = texto;
  for (const o of escolhidas) {
    out = `${out.slice(0, o.inicio)}${o.textoColapsado}${out.slice(o.fim)}`;
  }
  return out;
}
