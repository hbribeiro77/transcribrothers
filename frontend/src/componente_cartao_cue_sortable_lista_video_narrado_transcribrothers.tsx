/** Cartão sortable da lista de cues (handle de arraste + gap estilo Trello). */

import type { CSSProperties, ReactNode } from "react";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

export type PropsHandleArrasteCueVideoNarradoTranscribrothers = {
  setActivatorNodeRef: (el: HTMLElement | null) => void;
  attributes: Record<string, unknown>;
  listeners: Record<string, unknown> | undefined;
};

type PropsCartaoCueSortableListaVideoNarradoTranscribrothers = {
  id: string;
  desabilitado: boolean;
  className: string;
  mostrarGapAntes: boolean;
  ariaCurrent?: "true";
  onClickLista: () => void;
  liRef?: (el: HTMLLIElement | null) => void;
  children: (handle: PropsHandleArrasteCueVideoNarradoTranscribrothers) => ReactNode;
};

export function CartaoCueSortableListaVideoNarradoTranscribrothers({
  id,
  desabilitado,
  className,
  mostrarGapAntes,
  ariaCurrent,
  onClickLista,
  liRef,
  children,
}: PropsCartaoCueSortableListaVideoNarradoTranscribrothers) {
  const {
    attributes,
    listeners,
    setNodeRef,
    setActivatorNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id, disabled: desabilitado });

  const estilo: CSSProperties = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.35 : undefined,
  };

  return (
    <li
      ref={(el) => {
        setNodeRef(el);
        liRef?.(el);
      }}
      style={estilo}
      className={
        className +
        (isDragging ? " tb-modal-assistir-video-narrado-cue-item--arrastando" : "")
      }
      aria-current={ariaCurrent}
      onClick={onClickLista}
    >
      {mostrarGapAntes ? (
        <div
          className="tb-modal-assistir-video-narrado-cue-drop-gap"
          aria-hidden="true"
        />
      ) : null}
      {children({
        setActivatorNodeRef,
        attributes: attributes as unknown as Record<string, unknown>,
        listeners: listeners as unknown as Record<string, unknown> | undefined,
      })}
    </li>
  );
}
