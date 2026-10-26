import { describe, expect, it } from "vitest";
import {
  ESTADO_INICIAL_DA_PREVIA_DA_VINHETA,
  avancar_previa_da_vinheta,
  continuar_previa_da_vinheta,
  formatar_tempo_da_previa_da_vinheta,
  pausar_previa_da_vinheta,
  reiniciar_previa_da_vinheta,
  trocar_duracao_da_previa_da_vinheta,
} from "./modulo_controle_de_reproducao_da_previa_da_vinheta";

describe("controle de reprodução da prévia", () => {
  it("pausa no instante atual e continua dali", () => {
    const andando = avancar_previa_da_vinheta(ESTADO_INICIAL_DA_PREVIA_DA_VINHETA, 2.1, 5);
    const pausada = pausar_previa_da_vinheta(andando);
    expect(pausada).toEqual({ tempo_segundos: 2.1, tocando: false });
    expect(avancar_previa_da_vinheta(pausada, 1, 5)).toEqual(pausada);
    expect(continuar_previa_da_vinheta(pausada).tocando).toBe(true);
    expect(continuar_previa_da_vinheta(pausada).tempo_segundos).toBe(2.1);
  });

  it("reinicia tocando do começo", () => {
    const pausada = pausar_previa_da_vinheta(
      avancar_previa_da_vinheta(ESTADO_INICIAL_DA_PREVIA_DA_VINHETA, 3, 5),
    );
    expect(reiniciar_previa_da_vinheta()).toEqual({ tempo_segundos: 0, tocando: true });
    expect(pausada.tocando).toBe(false);
  });

  it("repete a duração e zera ao trocar a velocidade", () => {
    const voltou = avancar_previa_da_vinheta(ESTADO_INICIAL_DA_PREVIA_DA_VINHETA, 5.4, 5);
    expect(voltou.tempo_segundos).toBeCloseTo(0.4);
    expect(voltou.tocando).toBe(true);
    expect(trocar_duracao_da_previa_da_vinheta()).toEqual({ tempo_segundos: 0, tocando: true });
  });

  it("mostra o tempo com um decimal e vírgula", () => {
    expect(formatar_tempo_da_previa_da_vinheta(2.14)).toBe("2,1 s");
    expect(formatar_tempo_da_previa_da_vinheta(0)).toBe("0,0 s");
  });
});
