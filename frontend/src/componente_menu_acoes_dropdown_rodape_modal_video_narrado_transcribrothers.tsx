import { useEffect, useId, useLayoutEffect, useRef } from "react";

export type ItemMenuAcoesDropdownRodapeModalVideoNarradoTranscribrothers = {
  id: string;
  rotulo: string;
  desabilitado?: boolean;
  titulo?: string;
  variante?: "perigo";
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
  posicaoLista?: "acima" | "abaixo";
  classeTrigger?: string;
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
  posicaoLista = "acima",
  classeTrigger,
}: PropsComponenteMenuAcoesDropdownRodapeModalVideoNarradoTranscribrothers) {
  const listaId = useId();
  const ref = useRef<HTMLDivElement | null>(null);
  const listaRef = useRef<HTMLUListElement | null>(null);
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
    const fecharSeScroll = () => onMenuAbertoIdChange(null);
    document.addEventListener("mousedown", fecharSeCliqueFora);
    window.addEventListener("keydown", fecharSeEscape);
    window.addEventListener("scroll", fecharSeScroll, true);
    return () => {
      document.removeEventListener("mousedown", fecharSeCliqueFora);
      window.removeEventListener("keydown", fecharSeEscape);
      window.removeEventListener("scroll", fecharSeScroll, true);
    };
  }, [aberto, onMenuAbertoIdChange]);

  useLayoutEffect(() => {
    if (!aberto || posicaoLista !== "abaixo") return;
    const trigger = ref.current?.querySelector("button");
    const lista = listaRef.current;
    if (!trigger || !lista) return;
    const r = trigger.getBoundingClientRect();
    lista.style.position = "fixed";
    lista.style.top = `${Math.round(r.bottom + 4)}px`;
    lista.style.right = `${Math.round(window.innerWidth - r.right)}px`;
    lista.style.left = "auto";
    lista.style.bottom = "auto";
  }, [aberto, posicaoLista, itens.length]);

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
          (classeTrigger
            ? classeTrigger
            : (variante === "primario" ? "tb-primary" : "tb-linkbtn") +
              " tb-modal-video-narrado-menu-acoes-trigger")
        }
        aria-label={ariaLabel}
        aria-haspopup="menu"
        aria-expanded={aberto}
        aria-controls={listaId}
        disabled={desabilitado}
        onClick={(e) => {
          e.stopPropagation();
          onMenuAbertoIdChange(aberto ? null : idMenu);
        }}
      >
        <span>{rotulo}</span>
        {badge ? <span className="tb-modal-video-narrado-menu-acoes-badge" aria-hidden="true" /> : null}
        <IconeChevronBaixoMenuAcoesRodapeTranscribrothers />
      </button>
      {aberto ? (
        <ul
          id={listaId}
          ref={listaRef}
          className={
            "tb-modal-video-narrado-menu-acoes-lista" +
            (posicaoLista === "abaixo"
              ? " tb-modal-video-narrado-menu-acoes-lista--abaixo"
              : "")
          }
          role="menu"
        >
          {itens.map((item) => (
            <li key={item.id} role="none">
              <button
                type="button"
                role="menuitem"
                className={
                  "tb-modal-video-narrado-menu-acoes-item" +
                  (item.variante === "perigo"
                    ? " tb-modal-video-narrado-menu-acoes-item--perigo"
                    : "")
                }
                disabled={item.desabilitado}
                title={item.titulo}
                onClick={(e) => {
                  e.stopPropagation();
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
