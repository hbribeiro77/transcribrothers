import type { MouseEvent } from "react";
import {
  DURACAO_PADRAO_DA_VINHETA,
  amostrar_quadro_da_vinheta,
  tempo_da_coreografia,
  type EfeitoDaVinheta,
} from "./modulo_amostragem_dos_modelos_de_abertura_da_vinheta";
import { plano_do_bloco, type BlocoDaVinheta, type SaidaDaVinheta } from "./modulo_movimento_do_bloco_adicionado_na_vinheta";
import type { CoresDaVinheta } from "./modulo_validacao_de_titulo_e_cores_da_vinheta";

type ProjetoVisivel = {
  titulo: string;
  cores: CoresDaVinheta;
  efeito?: EfeitoDaVinheta;
  duracao_segundos?: number;
  blocos?: BlocoDaVinheta[];
  saida?: SaidaDaVinheta;
  largura?: number;
  altura?: number;
};

export function ComponenteQuadroDaCenaVinheta({
  projeto,
  tempo_segundos,
  bloco_selecionado_id = null,
  url_da_imagem_de_fundo = null,
  presenca_da_imagem = 0,
  ao_clicar_no_viewbox,
}: {
  projeto: ProjetoVisivel;
  tempo_segundos: number;
  bloco_selecionado_id?: string | null;
  url_da_imagem_de_fundo?: string | null;
  presenca_da_imagem?: number;
  ao_clicar_no_viewbox?: (ponto: { x: number; y: number }) => void;
}) {
  const quadro = amostrar_quadro_da_vinheta({ ...projeto, presenca_da_imagem }, tempo_segundos);
  const descricao = projeto.titulo.trim() || "Prévia da vinheta";
  const selecionado = (projeto.blocos ?? []).find((bloco) => bloco.id === bloco_selecionado_id) ?? null;
  const contorno = selecionado
    ? plano_do_bloco(
        selecionado,
        tempo_da_coreografia(tempo_segundos, projeto.duracao_segundos ?? DURACAO_PADRAO_DA_VINHETA),
        projeto.saida ?? "esmaecer",
      )
    : null;

  function clicar(evento: MouseEvent<SVGSVGElement>) {
    if (!ao_clicar_no_viewbox) {
      return;
    }
    const svg = evento.currentTarget;
    const matriz = svg.getScreenCTM();
    if (!matriz) {
      return;
    }
    const ponto = svg.createSVGPoint();
    ponto.x = evento.clientX;
    ponto.y = evento.clientY;
    const local = ponto.matrixTransform(matriz.inverse());
    ao_clicar_no_viewbox({ x: local.x, y: local.y });
  }

  return (
    <svg
      className={ao_clicar_no_viewbox ? "quadro-da-cena-vinheta quadro-clicavel-vinheta" : "quadro-da-cena-vinheta"}
      viewBox={`0 0 ${quadro.largura} ${quadro.altura}`}
      role="img"
      aria-label={descricao}
      onClick={ao_clicar_no_viewbox ? clicar : undefined}
    >
      <rect width={quadro.largura} height={quadro.altura} fill={quadro.fundo} />
      {url_da_imagem_de_fundo && (quadro.opacidade_da_imagem ?? 0) > 0 ? (
        <image
          href={url_da_imagem_de_fundo}
          width={quadro.largura}
          height={quadro.altura}
          preserveAspectRatio="xMidYMid meet"
          opacity={quadro.opacidade_da_imagem}
          pointerEvents="none"
        />
      ) : null}
      {quadro.planos.map((plano, indice) => (
        <rect
          key={indice}
          x={plano.x}
          y={plano.y}
          width={plano.largura}
          height={plano.altura}
          fill={plano.cor}
          opacity={plano.opacidade ?? 1}
        />
      ))}
      <text
        x={quadro.titulo.x}
        y={quadro.titulo.y}
        fill={quadro.titulo.cor}
        opacity={quadro.titulo.opacidade}
        textAnchor="middle"
        dominantBaseline="central"
        fontFamily="Segoe UI, sans-serif"
        fontSize={quadro.titulo.tamanho_fonte}
      >
        {quadro.titulo.texto}
      </text>
      {contorno ? (
        <rect
          data-contorno-do-bloco="sim"
          x={contorno.x}
          y={contorno.y}
          width={contorno.largura}
          height={contorno.altura}
          fill="none"
          stroke="#f7f4ef"
          strokeWidth={6}
          pointerEvents="none"
        />
      ) : null}
    </svg>
  );
}
