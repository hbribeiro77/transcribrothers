import { useMemo, useState } from "react";

import { obterCatalogoModelosLitellmNoProxyApiTranscribrothers } from "./modulo_api_obter_catalogo_modelos_litellm_no_proxy_transcribrothers.ts";
import {
  filtrarItensCatalogoModelosLitellmProxyParaExibicaoGavetaTranscribrothers,
  rotuloCategoriaSlugModeloLitellmCatalogoProxyTranscribrothers,
  type ItemCatalogoModeloLitellmProxyTranscribrothers,
  type RespostaCatalogoModelosLitellmProxyApiTranscribrothers,
} from "./modulo_util_filtrar_catalogo_modelos_litellm_proxy_gaveta_configuracoes_transcribrothers.ts";
import "./estilos_css_painel_catalogo_modelos_litellm_proxy_gaveta_configuracoes_transcribrothers.css";

export type PropsComponentePainelCatalogoModelosLitellmProxyGavetaConfiguracoesTranscribrothers = {
  aoAdicionarModelo: (slug: string) => void | Promise<void>;
  desabilitado: boolean;
};

export function ComponentePainelCatalogoModelosLitellmProxyGavetaConfiguracoesTranscribrothers({
  aoAdicionarModelo,
  desabilitado,
}: PropsComponentePainelCatalogoModelosLitellmProxyGavetaConfiguracoesTranscribrothers) {
  const [catalogo, setCatalogo] = useState<RespostaCatalogoModelosLitellmProxyApiTranscribrothers | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [soUteisParaTutorial, setSoUteisParaTutorial] = useState(true);
  const [slugEmAdicao, setSlugEmAdicao] = useState<string | null>(null);

  const itensExibidos = useMemo(
    () =>
      catalogo
        ? filtrarItensCatalogoModelosLitellmProxyParaExibicaoGavetaTranscribrothers(
            catalogo.modelos,
            soUteisParaTutorial,
          )
        : [],
    [catalogo, soUteisParaTutorial],
  );

  async function carregarCatalogoDoProxy() {
    if (carregando) return;
    setCarregando(true);
    setErro(null);
    try {
      const r = await obterCatalogoModelosLitellmNoProxyApiTranscribrothers();
      setCatalogo(r);
    } catch (e) {
      setErro(e instanceof Error ? e.message : String(e));
    } finally {
      setCarregando(false);
    }
  }

  async function adicionarSlugDoCatalogo(item: ItemCatalogoModeloLitellmProxyTranscribrothers) {
    if (desabilitado || slugEmAdicao || item.na_allowlist) return;
    setSlugEmAdicao(item.id);
    try {
      await aoAdicionarModelo(item.id);
      setCatalogo((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          modelos: prev.modelos.map((m) => (m.id === item.id ? { ...m, na_allowlist: true } : m)),
          allowlist_ausente_no_proxy: prev.allowlist_ausente_no_proxy.filter((s) => s !== item.id),
        };
      });
    } finally {
      setSlugEmAdicao(null);
    }
  }

  const totalProxy = catalogo?.modelos.length ?? 0;
  const totalUteis = catalogo?.modelos.filter((m) => m.util_para_tutorial).length ?? 0;

  return (
    <section className="tb-catalogo-proxy-litellm" aria-labelledby="tb-catalogo-proxy-litellm-titulo">
      <div className="tb-drawer-secao-head tb-drawer-secao-head--apos-bloco">
        <h3 id="tb-catalogo-proxy-litellm-titulo" className="tb-drawer-subtitulo">
          Modelos no proxy
        </h3>
      </div>
      <p className="tb-muted tb-drawer-dica-inline">
        Lista ao vivo do LiteLLM. Adicionar inclui o slug na allowlist (mesmo fluxo do campo acima).
      </p>
      <div className="tb-row tb-catalogo-proxy-litellm-acoes">
        <button
          type="button"
          className="tb-linkbtn"
          disabled={desabilitado || carregando}
          onClick={() => void carregarCatalogoDoProxy()}
        >
          {carregando ? "Consultando proxy…" : catalogo ? "Atualizar lista" : "Ver modelos do proxy"}
        </button>
      </div>
      {erro ? (
        <p className="tb-catalogo-proxy-litellm-erro" role="alert">
          {erro}
        </p>
      ) : null}
      {catalogo ? (
        <>
          <label className="tb-catalogo-proxy-litellm-filtro">
            <input
              type="checkbox"
              checked={soUteisParaTutorial}
              onChange={(e) => setSoUteisParaTutorial(e.target.checked)}
            />
            Só os úteis para tutorial ({totalUteis} de {totalProxy} no proxy)
          </label>
          {catalogo.allowlist_ausente_no_proxy.length > 0 ? (
            <p className="tb-catalogo-proxy-litellm-ausentes">
              Na lista do app, mas o proxy não oferece agora:{" "}
              {catalogo.allowlist_ausente_no_proxy.map((s) => (
                <code key={s}>{s}</code>
              ))}
            </p>
          ) : null}
          {itensExibidos.length === 0 ? (
            <p className="tb-muted">Nenhum modelo neste filtro.</p>
          ) : (
            <ul className="tb-catalogo-proxy-litellm-lista">
              {itensExibidos.map((item) => (
                <li key={item.id} className="tb-catalogo-proxy-litellm-item">
                  <div className="tb-catalogo-proxy-litellm-item-texto">
                    <code className="tb-catalogo-proxy-litellm-slug">{item.id}</code>
                    <span className="tb-catalogo-proxy-litellm-meta">
                      {rotuloCategoriaSlugModeloLitellmCatalogoProxyTranscribrothers(item.categoria)}
                      {item.na_allowlist ? " · já na allowlist" : ""}
                    </span>
                  </div>
                  {item.na_allowlist ? (
                    <span className="tb-catalogo-proxy-litellm-badge">Na lista</span>
                  ) : (
                    <button
                      type="button"
                      className="tb-linkbtn tb-catalogo-proxy-litellm-add"
                      disabled={desabilitado || slugEmAdicao !== null}
                      onClick={() => void adicionarSlugDoCatalogo(item)}
                    >
                      {slugEmAdicao === item.id ? "Adicionando…" : "Adicionar"}
                    </button>
                  )}
                </li>
              ))}
            </ul>
          )}
        </>
      ) : null}
    </section>
  );
}
