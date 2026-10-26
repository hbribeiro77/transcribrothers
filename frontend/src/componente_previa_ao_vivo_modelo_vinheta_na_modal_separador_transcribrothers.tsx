import { useEffect, useState } from "react";

import { ComponenteQuadroDaCenaVinheta } from "./previa_ao_vivo_cena_vinheta_copiada_do_app_vinhetas/componente_quadro_da_cena_vinheta.tsx";
import {
  DURACAO_PADRAO_DA_VINHETA,
  EFEITO_PADRAO_DA_VINHETA,
  type EfeitoDaVinheta,
} from "./previa_ao_vivo_cena_vinheta_copiada_do_app_vinhetas/modulo_amostragem_dos_modelos_de_abertura_da_vinheta.ts";
import {
  ESTADO_INICIAL_DA_PREVIA_DA_VINHETA,
  avancar_previa_da_vinheta,
  reiniciar_previa_da_vinheta,
} from "./previa_ao_vivo_cena_vinheta_copiada_do_app_vinhetas/modulo_controle_de_reproducao_da_previa_da_vinheta.ts";
import {
  PALETA_PADRAO_DA_VINHETA,
  type CoresDaVinheta,
} from "./previa_ao_vivo_cena_vinheta_copiada_do_app_vinhetas/modulo_validacao_de_titulo_e_cores_da_vinheta.ts";

export function ComponentePreviaAoVivoModeloVinhetaNaModalSeparadorTranscribrothers({
  titulo,
  efeito = EFEITO_PADRAO_DA_VINHETA,
  duracao_segundos = DURACAO_PADRAO_DA_VINHETA,
  cores = PALETA_PADRAO_DA_VINHETA,
  url_da_imagem_de_fundo = null,
  presenca_da_imagem = 0,
  largura,
  altura,
}: {
  titulo: string;
  efeito?: EfeitoDaVinheta;
  duracao_segundos?: number;
  cores?: CoresDaVinheta;
  url_da_imagem_de_fundo?: string | null;
  presenca_da_imagem?: number;
  largura?: number;
  altura?: number;
}) {
  const [estado, setEstado] = useState(ESTADO_INICIAL_DA_PREVIA_DA_VINHETA);
  const duracao = duracao_segundos > 0 ? duracao_segundos : DURACAO_PADRAO_DA_VINHETA;

  useEffect(() => {
    setEstado(reiniciar_previa_da_vinheta());
  }, [efeito, duracao]);

  useEffect(() => {
    let identificador = 0;
    let ultimo = performance.now();
    const avancar = (agora: number) => {
      const delta = (agora - ultimo) / 1000;
      ultimo = agora;
      setEstado((atual) => avancar_previa_da_vinheta(atual, delta, duracao));
      identificador = requestAnimationFrame(avancar);
    };
    identificador = requestAnimationFrame(avancar);
    return () => cancelAnimationFrame(identificador);
  }, [efeito, duracao]);

  return (
    <ComponenteQuadroDaCenaVinheta
      projeto={{
        titulo,
        cores,
        efeito,
        duracao_segundos: duracao,
        largura,
        altura,
      }}
      tempo_segundos={estado.tempo_segundos}
      url_da_imagem_de_fundo={url_da_imagem_de_fundo}
      presenca_da_imagem={presenca_da_imagem}
    />
  );
}
