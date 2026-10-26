export type EstadoDaReproducaoDaPrevia = {
  tempo_segundos: number;
  tocando: boolean;
};

export const ESTADO_INICIAL_DA_PREVIA_DA_VINHETA: EstadoDaReproducaoDaPrevia = {
  tempo_segundos: 0,
  tocando: true,
};

export function pausar_previa_da_vinheta(estado: EstadoDaReproducaoDaPrevia): EstadoDaReproducaoDaPrevia {
  return { ...estado, tocando: false };
}

export function continuar_previa_da_vinheta(estado: EstadoDaReproducaoDaPrevia): EstadoDaReproducaoDaPrevia {
  return { ...estado, tocando: true };
}

export function reiniciar_previa_da_vinheta(): EstadoDaReproducaoDaPrevia {
  return { tempo_segundos: 0, tocando: true };
}

export function trocar_duracao_da_previa_da_vinheta(): EstadoDaReproducaoDaPrevia {
  return { tempo_segundos: 0, tocando: true };
}

export function avancar_previa_da_vinheta(
  estado: EstadoDaReproducaoDaPrevia,
  delta_segundos: number,
  duracao_segundos: number,
): EstadoDaReproducaoDaPrevia {
  if (!estado.tocando || duracao_segundos <= 0) {
    return estado;
  }
  const resto = (estado.tempo_segundos + delta_segundos) % duracao_segundos;
  const tempo_segundos = resto < 0 ? resto + duracao_segundos : resto;
  return { ...estado, tempo_segundos };
}

export function formatar_tempo_da_previa_da_vinheta(tempo_segundos: number): string {
  return `${tempo_segundos.toFixed(1).replace(".", ",")} s`;
}
