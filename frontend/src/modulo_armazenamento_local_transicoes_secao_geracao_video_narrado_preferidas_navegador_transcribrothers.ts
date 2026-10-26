import {
  DURACAO_PADRAO_TRANSICAO_SECAO_GERACAO_VIDEO_NARRADO_SEGUNDOS,
  EFEITO_PADRAO_TRANSICAO_SECAO_GERACAO_VIDEO_NARRADO,
  normalizarDuracaoTransicaoSecaoGeracaoVideoNarradoTranscribrothers,
  normalizarEfeitoTransicaoSecaoGeracaoVideoNarradoTranscribrothers,
} from "./modulo_util_transicoes_secao_na_geracao_video_narrado_transcribrothers.ts";
import type { EfeitoDaVinheta } from "./previa_ao_vivo_cena_vinheta_copiada_do_app_vinhetas/modulo_amostragem_dos_modelos_de_abertura_da_vinheta.ts";

const CHAVE = "transcribrothers_transicoes_secao_geracao_video_narrado_preferidas_navegador_v1";

export type PreferenciaTransicoesSecaoGeracaoVideoNarradoTranscribrothers = {
  incluir: boolean;
  efeito: EfeitoDaVinheta;
  duracaoSegundos: 2 | 5;
  vinhetaId: string | null;
};

const PADRAO: PreferenciaTransicoesSecaoGeracaoVideoNarradoTranscribrothers = {
  incluir: true,
  efeito: EFEITO_PADRAO_TRANSICAO_SECAO_GERACAO_VIDEO_NARRADO,
  duracaoSegundos: DURACAO_PADRAO_TRANSICAO_SECAO_GERACAO_VIDEO_NARRADO_SEGUNDOS,
  vinhetaId: null,
};

export function carregarPreferenciaTransicoesSecaoGeracaoVideoNarradoDoNavegadorTranscribrothers(): PreferenciaTransicoesSecaoGeracaoVideoNarradoTranscribrothers {
  try {
    const raw = window.localStorage.getItem(CHAVE);
    if (!raw) return { ...PADRAO };
    const parsed = JSON.parse(raw) as Partial<PreferenciaTransicoesSecaoGeracaoVideoNarradoTranscribrothers>;
    return {
      incluir: parsed.incluir !== false,
      efeito: normalizarEfeitoTransicaoSecaoGeracaoVideoNarradoTranscribrothers(parsed.efeito),
      duracaoSegundos: normalizarDuracaoTransicaoSecaoGeracaoVideoNarradoTranscribrothers(
        parsed.duracaoSegundos,
      ),
      vinhetaId:
        typeof parsed.vinhetaId === "string" && parsed.vinhetaId.trim()
          ? parsed.vinhetaId.trim()
          : null,
    };
  } catch {
    return { ...PADRAO };
  }
}

export function salvarPreferenciaTransicoesSecaoGeracaoVideoNarradoNoNavegadorTranscribrothers(
  pref: PreferenciaTransicoesSecaoGeracaoVideoNarradoTranscribrothers,
): void {
  try {
    window.localStorage.setItem(
      CHAVE,
      JSON.stringify({
        incluir: pref.incluir !== false,
        efeito: normalizarEfeitoTransicaoSecaoGeracaoVideoNarradoTranscribrothers(pref.efeito),
        duracaoSegundos: normalizarDuracaoTransicaoSecaoGeracaoVideoNarradoTranscribrothers(
          pref.duracaoSegundos,
        ),
        vinhetaId: (pref.vinhetaId || "").trim() || null,
      }),
    );
  } catch {
    /* quota / modo privado */
  }
}
