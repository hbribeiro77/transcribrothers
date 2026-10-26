import { describe, expect, it } from "vitest";
import { instantes_dos_quadros_da_transicao_do_separador_transcribrothers } from "./modulo_util_instantes_dos_quadros_da_transicao_do_separador_transcribrothers.ts";

describe("quadros da transição do separador", () => {
  const janelas = [
    { inicioVideoSegundos: 12, fimVideoSegundos: 20, idFonteVideo: "entrada" },
    { inicioVideoSegundos: 40, fimVideoSegundos: 55, idFonteVideo: "entrada" },
  ];

  it("usa o começo do trecho seguinte e o fim do anterior", () => {
    expect(
      instantes_dos_quadros_da_transicao_do_separador_transcribrothers({
        janelas,
        indiceDaCueAnterior: 0,
        instanteAtualDoVideo: 3,
      }),
    ).toEqual({ seguinte: 40, anterior: 19.95 });
  });

  it("cai no instante do player quando o seguinte não é o vídeo de entrada", () => {
    expect(
      instantes_dos_quadros_da_transicao_do_separador_transcribrothers({
        janelas: [{ inicioVideoSegundos: 4, fimVideoSegundos: 9, idFonteVideo: "biblioteca-1" }],
        indiceDaCueAnterior: null,
        instanteAtualDoVideo: 7.2,
      }),
    ).toEqual({ seguinte: 7.2, anterior: null });
  });
});
