import { useEffect, useId, useRef } from "react";

export type ItemMenuAcoesDropdownRodapeModalVideoNarradoTranscribrothers = {
  id: string;
  rotulo: string;
  desabilitado?: boolean;
  titulo?: string;
  onClick: () => void;
};

type PropsComponenteMenuAcoesDropdownRodapeModalVideoNarradoTranscribrothers = {
  rotulo: string;
  ariaLabel: string;
  desabilitado?: boolean;
  variante?: "secundario" | "primario";
  itens: ItemMenuAcoesDropdownRodapeModalVideoNarradoTranscribrothers[];
  /** Fecha outros menus do rodapé quando este abre. */
  menuAbertoId: string | null;
  idMenu: string;
  onMenuAbertoIdChange: (id: string | null) => void;
  badge?: boolean;
};

function IconeChevronBaixoMenuAcoesRodapeTranscribrothers() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true">
      <path
        fill="none"
        stroke="currentColor"
        strokeWidth="2.25"
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M6 9l6 6 6-6"
      />
    </svg>
  );
}

export function ComponenteMenuAcoesDropdownRodapeModalVideoNarradoTranscribrothers({
  rotulo,
  ariaLabel,
  desabilitado = false,
  variante = "secundario",
  itens,
  menuAbertoId,
  idMenu,
  onMenuAbertoIdChange,
  badge = false,
}: PropsComponenteMenuAcoesDropdownRodapeModalVideoNarradoTranscribrothers) {
  const listaId = useId();
  const ref = useRef<HTMLDivElement | null>(null);
  const aberto = menuAbertoId === idMenu;

  useEffect(() => {
    if (!aberto) return;
    const fecharSeCliqueFora = (evento: MouseEvent) => {
      const alvo = evento.target;
      if (!(alvo instanceof Node)) return;
      if (ref.current?.contains(alvo)) return;
      onMenuAbertoIdChange(null);
    };
    const fecharSeEscape = (evento: KeyboardEvent) => {
      if (evento.key === "Escape") onMenuAbertoIdChange(null);
    };
    document.addEventListener("mousedown", fecharSeCliqueFora);
    window.addEventListener("keydown", fecharSeEscape);
    return () => {
      document.removeEventListener("mousedown", fecharSeCliqueFora);
      window.removeEventListener("keydown", fecharSeEscape);
    };
  }, [aberto, onMenuAbertoIdChange]);

  return (
    <div
      className={
        "tb-modal-video-narrado-menu-acoes" +
        (aberto ? " tb-modal-video-narrado-menu-acoes--aberto" : "")
      }
      ref={ref}
    >
      <button
        type="button"
        className={
          (variante === "primario" ? "tb-primary" : "tb-linkbtn") +
          " tb-modal-video-narrado-menu-acoes-trigger"
        }
        aria-label={ariaLabel}
        aria-haspopup="menu"
        aria-expanded={aberto}
        aria-controls={listaId}
        disabled={desabilitado}
        onClick={() => onMenuAbertoIdChange(aberto ? null : idMenu)}
      >
        <span>{rotulo}</span>
        {badge ? <span className="tb-modal-video-narrado-menu-acoes-badge" aria-hidden="true" /> : null}
        <IconeChevronBaixoMenuAcoesRodapeTranscribrothers />
      </button>
      {aberto ? (
        <ul id={listaId} className="tb-modal-video-narrado-menu-acoes-lista" role="menu">
          {itens.map((item) => (
            <li key={item.id} role="none">
              <button
                type="button"
                role="menuitem"
                className="tb-modal-video-narrado-menu-acoes-item"
                disabled={item.desabilitado}
                title={item.titulo}
                onClick={() => {
                  onMenuAbertoIdChange(null);
                  item.onClick();
                }}
              >
                {item.rotulo}
              </button>
            </li>
          ))}
        </ul>
      ) : null}
    </div>
  );
}

export type AcaoPrimariaContextualRodapeModalVideoNarradoTranscribrothers = {
  rotulo: string;
  desabilitado: boolean;
  onClick: () => void;
  titulo?: string;
};

/** Botão primário só quando há algo para salvar (texto ou tempos). Aplicar fica no menu. */
export function resolverAcaoPrimariaContextualRodapeModalVideoNarradoTranscribrothers(opts: {
  podeSalvarLegendas: boolean;
  podeSalvarTempos: boolean;
  salvandoLegendas: boolean;
  salvandoJanelas: boolean;
  onSalvarLegendas: () => void;
  onSalvarTempos: () => void;
}): AcaoPrimariaContextualRodapeModalVideoNarradoTranscribrothers | null {
  if (opts.podeSalvarLegendas || opts.salvandoLegendas) {
    return {
      rotulo: opts.salvandoLegendas ? "Salvando…" : "Salvar legendas",
      desabilitado: !opts.podeSalvarLegendas,
      onClick: opts.onSalvarLegendas,
      titulo: "Grava o texto das legendas no VTT (não altera o áudio).",
    };
  }
  if (opts.podeSalvarTempos || opts.salvandoJanelas) {
    return {
      rotulo: opts.salvandoJanelas ? "Salvando…" : "Salvar tempos",
      desabilitado: !opts.podeSalvarTempos,
      onClick: opts.onSalvarTempos,
      titulo: "Grava os tempos de tela no manifesto (sem remux).",
    };
  }
  return null;
}
