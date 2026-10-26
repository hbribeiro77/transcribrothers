import { useEffect, useId, useState } from "react";
import { createPortal } from "react-dom";

import { ComponentePreviaAoVivoModeloVinhetaNaModalSeparadorTranscribrothers } from "./componente_previa_ao_vivo_modelo_vinheta_na_modal_separador_transcribrothers.tsx";
import { listarVinhetasDisponiveisParaSeparadorApiTranscribrothers } from "./modulo_api_biblioteca_midias_tela_job_transcribrothers.ts";
import { ComponenteQuadroDaCenaVinheta } from "./previa_ao_vivo_cena_vinheta_copiada_do_app_vinhetas/componente_quadro_da_cena_vinheta.tsx";
import {
  DURACAO_PADRAO_DA_VINHETA,
  tempo_de_reproducao_do_quadro_assentado,
} from "./previa_ao_vivo_cena_vinheta_copiada_do_app_vinhetas/modulo_amostragem_dos_modelos_de_abertura_da_vinheta.ts";
import {
  PALETA_PADRAO_DA_VINHETA,
  type CoresDaVinheta,
} from "./previa_ao_vivo_cena_vinheta_copiada_do_app_vinhetas/modulo_validacao_de_titulo_e_cores_da_vinheta.ts";
import {
  montarCartoesVinhetaSeparadorDeSecaoTranscribrothers,
  type CartaoVinhetaSeparadorDeSecaoTranscribrothers,
  type EscolhaDeVinhetaParaSeparadorTranscribrothers,
} from "./modulo_util_montar_cartoes_e_resolver_escolha_vinheta_separador_de_secao_transcribrothers.ts";
import {
  CAMPOS_DE_COR_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS,
  DURACAO_MAXIMA_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS,
  DURACAO_MINIMA_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS,
  PASSO_DE_DURACAO_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS,
  PRESENCA_PADRAO_DA_IMAGEM_DE_FUNDO_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS,
  montarReceitaVinhetaDoSeparadorTranscribrothers,
  normalizarDimensoesParesDoCanvasDaVinhetaTranscribrothers,
  normalizarDuracaoSegundosDaVinhetaDoSeparadorTranscribrothers,
  normalizarPresencaDaImagemDaVinhetaDoSeparadorTranscribrothers,
  type ReceitaVinhetaDoSeparadorTranscribrothers,
} from "./modulo_util_receita_e_velocidade_da_vinheta_do_separador_de_secao_transcribrothers.ts";
import "./estilos_css_modal_escolher_vinheta_para_separador_de_secao_transcribrothers.css";

export type { EscolhaDeVinhetaParaSeparadorTranscribrothers, ReceitaVinhetaDoSeparadorTranscribrothers };

function chaveDaReceitaVinhetaSeparadorTranscribrothers(
  receita: ReceitaVinhetaDoSeparadorTranscribrothers | null | undefined,
): string {
  if (!receita) return "";
  if (receita.vinhetaId) return `salva:${receita.vinhetaId}`;
  if (receita.efeito) return `modelo:${receita.efeito}`;
  return "";
}

export function ComponenteModalEscolherVinhetaParaSeparadorDeSecaoTranscribrothers({
  aberto,
  tituloInicial,
  ocupado,
  urlQuadroDoTutorial = null,
  receitaInicial = null,
  rotuloConfirmar = "Inserir",
  aoCancelar,
  aoConfirmar,
}: {
  aberto: boolean;
  tituloInicial: string;
  ocupado: boolean;
  urlQuadroDoTutorial?: string | null;
  receitaInicial?: ReceitaVinhetaDoSeparadorTranscribrothers | null;
  rotuloConfirmar?: string;
  aoCancelar: () => void;
  aoConfirmar: (escolha: ReceitaVinhetaDoSeparadorTranscribrothers) => void;
}) {
  const tituloId = useId();
  const [titulo, setTitulo] = useState(tituloInicial);
  const [cartoes, setCartoes] = useState<CartaoVinhetaSeparadorDeSecaoTranscribrothers[]>([]);
  const [chave, setChave] = useState("");
  const [erro, setErro] = useState<string | null>(null);
  const [duracaoSegundos, setDuracaoSegundos] = useState(DURACAO_PADRAO_DA_VINHETA);
  const [presencaDaImagem, setPresencaDaImagem] = useState(
    PRESENCA_PADRAO_DA_IMAGEM_DE_FUNDO_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS,
  );
  const [cores, setCores] = useState<CoresDaVinheta>(PALETA_PADRAO_DA_VINHETA);
  const [canvasDoTutorial, setCanvasDoTutorial] = useState<{ largura: number; altura: number } | null>(
    null,
  );

  useEffect(() => {
    if (!aberto) return;
    setTitulo(receitaInicial?.titulo || tituloInicial);
    setDuracaoSegundos(
      normalizarDuracaoSegundosDaVinhetaDoSeparadorTranscribrothers(
        receitaInicial?.duracaoSegundos ?? DURACAO_PADRAO_DA_VINHETA,
      ),
    );
    setPresencaDaImagem(
      normalizarPresencaDaImagemDaVinhetaDoSeparadorTranscribrothers(
        receitaInicial?.presencaDaImagem ??
          PRESENCA_PADRAO_DA_IMAGEM_DE_FUNDO_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS,
      ),
    );
    setCores(receitaInicial?.cores ? { ...PALETA_PADRAO_DA_VINHETA, ...receitaInicial.cores } : PALETA_PADRAO_DA_VINHETA);
    setErro(null);
    let ativo = true;
    listarVinhetasDisponiveisParaSeparadorApiTranscribrothers()
      .then((lista) => {
        if (!ativo) return;
        const montados = montarCartoesVinhetaSeparadorDeSecaoTranscribrothers(lista);
        setCartoes(montados);
        const chaveReceita = chaveDaReceitaVinhetaSeparadorTranscribrothers(receitaInicial);
        if (chaveReceita && montados.some((cartao) => cartao.chave === chaveReceita)) {
          setChave(chaveReceita);
        } else if (montados[0]) {
          setChave(montados[0].chave);
        }
      })
      .catch((falha: unknown) => {
        if (ativo) {
          setErro(falha instanceof Error ? falha.message : "Não foi possível listar as vinhetas.");
        }
      });
    return () => {
      ativo = false;
    };
  }, [aberto, tituloInicial, receitaInicial]);

  useEffect(() => {
    if (!urlQuadroDoTutorial) {
      setCanvasDoTutorial(null);
      return;
    }
    const imagem = new Image();
    imagem.onload = () => {
      setCanvasDoTutorial(
        normalizarDimensoesParesDoCanvasDaVinhetaTranscribrothers(imagem.naturalWidth, imagem.naturalHeight),
      );
    };
    imagem.src = urlQuadroDoTutorial;
    return () => {
      imagem.onload = null;
    };
  }, [urlQuadroDoTutorial]);

  useEffect(() => {
    if (!aberto) return;
    const aoTeclar = (evento: KeyboardEvent) => {
      if (evento.key === "Escape") aoCancelar();
    };
    window.addEventListener("keydown", aoTeclar);
    return () => window.removeEventListener("keydown", aoTeclar);
  }, [aberto, aoCancelar]);

  if (!aberto) return null;

  const textoTitulo = titulo.trim() || tituloInicial;
  const escolhaAtual = chave
    ? montarReceitaVinhetaDoSeparadorTranscribrothers({
        chave,
        titulo: textoTitulo,
        duracaoSegundos,
        presencaDaImagem,
        cores,
      })
    : null;
  const cartaoSelecionado = cartoes.find((cartao) => cartao.chave === chave) ?? null;
  const presencaNaPrevia = urlQuadroDoTutorial ? presencaDaImagem : 0;

  return createPortal(
    <div className="tb-modal-escolher-vinheta-separador-overlay" role="presentation">
      <button
        type="button"
        className="tb-modal-escolher-vinheta-separador-backdrop"
        aria-label="Fechar escolha de vinheta"
        onClick={aoCancelar}
      />
      <form
        className="tb-modal-escolher-vinheta-separador"
        role="dialog"
        aria-modal="true"
        aria-labelledby={tituloId}
        onSubmit={(evento) => {
          evento.preventDefault();
          if (!escolhaAtual) return;
          aoConfirmar(escolhaAtual);
        }}
      >
        <header className="tb-modal-escolher-vinheta-separador-cabecalho">
          <h2 id={tituloId} className="tb-modal-escolher-vinheta-separador-titulo">
            {receitaInicial ? "Ajustar vinheta do separador" : "Escolher vinheta do separador"}
          </h2>
          <button
            type="button"
            className="tb-modal-escolher-vinheta-separador-fechar"
            onClick={aoCancelar}
            aria-label="Fechar"
          >
            ×
          </button>
        </header>
        <p className="tb-modal-escolher-vinheta-separador-ajuda">
          Escolha o estilo e veja a prévia na hora, com o quadro do tutorial no fundo. Velocidade,
          presença da imagem e cores atualizam na hora. Inserir gera o cartão no vídeo.
        </p>
        <div className="tb-modal-escolher-vinheta-separador-corpo">
          <ul className="tb-modal-escolher-vinheta-separador-grade" role="list">
            {cartoes.map((cartao) => (
              <li key={cartao.chave}>
                <button
                  type="button"
                  className={
                    "tb-modal-escolher-vinheta-separador-card" +
                    (cartao.chave === chave
                      ? " tb-modal-escolher-vinheta-separador-card--selecionado"
                      : "")
                  }
                  aria-pressed={cartao.chave === chave}
                  onClick={() => {
                    setChave(cartao.chave);
                    setErro(null);
                  }}
                >
                  <div className="tb-modal-escolher-vinheta-separador-card-quadro">
                    <ComponenteQuadroDaCenaVinheta
                      projeto={{
                        titulo: cartao.rotulo,
                        cores: PALETA_PADRAO_DA_VINHETA,
                        efeito: cartao.efeitoPrevia,
                        duracao_segundos: DURACAO_PADRAO_DA_VINHETA,
                      }}
                      tempo_segundos={tempo_de_reproducao_do_quadro_assentado(
                        DURACAO_PADRAO_DA_VINHETA,
                      )}
                    />
                    <span className="tb-modal-escolher-vinheta-separador-card-selo">
                      {cartao.grupo === "salva" ? "Salva" : "Modelo"}
                    </span>
                  </div>
                  <span className="tb-modal-escolher-vinheta-separador-card-nome">{cartao.rotulo}</span>
                  <p className="tb-modal-escolher-vinheta-separador-card-grupo">
                    {cartao.grupo === "salva" ? "Vinheta salva" : "Estilo do catálogo"}
                  </p>
                </button>
              </li>
            ))}
          </ul>
          <div className="tb-modal-escolher-vinheta-separador-lado">
            <div className="tb-modal-escolher-vinheta-separador-previa" aria-live="polite">
              {cartaoSelecionado ? (
                <ComponentePreviaAoVivoModeloVinhetaNaModalSeparadorTranscribrothers
                  titulo={textoTitulo}
                  efeito={cartaoSelecionado.efeitoPrevia}
                  duracao_segundos={duracaoSegundos}
                  cores={cores}
                  url_da_imagem_de_fundo={urlQuadroDoTutorial}
                  presenca_da_imagem={presencaNaPrevia}
                  largura={canvasDoTutorial?.largura}
                  altura={canvasDoTutorial?.altura}
                />
              ) : (
                <p className="tb-modal-escolher-vinheta-separador-previa-vazia">
                  Escolha uma vinheta para ver a prévia.
                </p>
              )}
            </div>
            <label className="tb-modal-escolher-vinheta-separador-campo">
              Título
              <input
                value={titulo}
                onChange={(evento) => setTitulo(evento.target.value)}
                maxLength={48}
                disabled={ocupado}
              />
            </label>
            <label className="tb-modal-escolher-vinheta-separador-campo tb-modal-escolher-vinheta-separador-slider">
              Velocidade
              <input
                type="range"
                min={DURACAO_MINIMA_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS}
                max={DURACAO_MAXIMA_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS}
                step={PASSO_DE_DURACAO_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS}
                value={duracaoSegundos}
                disabled={ocupado}
                aria-label="Velocidade da vinheta em segundos"
                onChange={(evento) =>
                  setDuracaoSegundos(
                    normalizarDuracaoSegundosDaVinhetaDoSeparadorTranscribrothers(
                      Number(evento.target.value),
                    ),
                  )
                }
              />
              <span>{duracaoSegundos.toLocaleString("pt-BR")} s</span>
            </label>
            <label className="tb-modal-escolher-vinheta-separador-campo tb-modal-escolher-vinheta-separador-slider">
              Presença
              <input
                type="range"
                min={0}
                max={100}
                step={1}
                value={presencaDaImagem}
                disabled={ocupado || !urlQuadroDoTutorial}
                aria-label="Presença da imagem de fundo"
                onChange={(evento) =>
                  setPresencaDaImagem(
                    normalizarPresencaDaImagemDaVinhetaDoSeparadorTranscribrothers(
                      Number(evento.target.value),
                    ),
                  )
                }
              />
              <span>{urlQuadroDoTutorial ? presencaDaImagem : 0}</span>
            </label>
            <div className="tb-modal-escolher-vinheta-separador-paleta">
              {CAMPOS_DE_COR_DA_VINHETA_DO_SEPARADOR_TRANSCRIBROTHERS.map((campo) => (
                <label key={campo.chave} className="tb-modal-escolher-vinheta-separador-cor">
                  {campo.rotulo}
                  <input
                    type="color"
                    value={cores[campo.chave].toLowerCase()}
                    aria-label={campo.rotulo}
                    title={cores[campo.chave]}
                    disabled={ocupado}
                    onChange={(evento) =>
                      setCores((atual) => ({ ...atual, [campo.chave]: evento.target.value }))
                    }
                  />
                </label>
              ))}
            </div>
          </div>
        </div>
        {erro ? <p className="tb-modal-escolher-vinheta-separador-erro">{erro}</p> : null}
        <footer className="tb-modal-escolher-vinheta-separador-rodape">
          <button type="button" className="tb-linkbtn" onClick={aoCancelar} disabled={ocupado}>
            Cancelar
          </button>
          <button type="submit" className="tb-primary" disabled={ocupado || cartoes.length === 0}>
            {ocupado ? "Gerando…" : rotuloConfirmar}
          </button>
        </footer>
      </form>
    </div>,
    document.body,
  );
}
