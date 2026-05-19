import type { ReactNode } from "react";
import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import "./estilos_css_portal_toasts_inferior_direita_feedback_ui_transcribrothers.css";

export type VarianteToastFeedbackUiTranscribrothers = "success" | "error" | "info";

type ItemToastInternoTranscribrothers = {
  id: string;
  message: string;
  variant: VarianteToastFeedbackUiTranscribrothers;
};

type ValorContextoToastTranscribrothers = {
  pushToast: (message: string, variant?: VarianteToastFeedbackUiTranscribrothers) => void;
};

const ContextoToastFeedbackAcoesUiTranscribrothers = createContext<ValorContextoToastTranscribrothers | null>(null);

const DURACAO_MS_TOAST_PADRAO_TRANSCRIBROTHERS = 4200;
const MAX_TOASTS_VISIVEIS_SIMULTANEOS_TRANSCRIBROTHERS = 5;

export function usarToastFeedbackAcoesUiTranscribrothers(): ValorContextoToastTranscribrothers {
  const v = useContext(ContextoToastFeedbackAcoesUiTranscribrothers);
  if (!v) {
    throw new Error("usarToastFeedbackAcoesUiTranscribrothers: envolva a árvore com ProvedorToastsFeedbackAcoesUiTranscribrothers.");
  }
  return v;
}

export function ProvedorToastsFeedbackAcoesUiTranscribrothers(props: { children: ReactNode }) {
  const [items, setItems] = useState<ItemToastInternoTranscribrothers[]>([]);
  const timeoutsRef = useRef<Map<string, number>>(new Map());

  useEffect(() => {
    const m = timeoutsRef.current;
    return () => {
      for (const t of m.values()) {
        window.clearTimeout(t);
      }
      m.clear();
    };
  }, []);

  const pushToast = useCallback((message: string, variant: VarianteToastFeedbackUiTranscribrothers = "info") => {
    const id =
      typeof globalThis.crypto !== "undefined" && "randomUUID" in globalThis.crypto
        ? globalThis.crypto.randomUUID()
        : `toast-${Date.now()}-${Math.random().toString(16).slice(2)}`;
    setItems((prev) => [...prev.slice(-(MAX_TOASTS_VISIVEIS_SIMULTANEOS_TRANSCRIBROTHERS - 1)), { id, message, variant }]);
    const prevT = timeoutsRef.current.get(id);
    if (prevT !== undefined) {
      window.clearTimeout(prevT);
    }
    const t = window.setTimeout(() => {
      setItems((prev) => prev.filter((x) => x.id !== id));
      timeoutsRef.current.delete(id);
    }, DURACAO_MS_TOAST_PADRAO_TRANSCRIBROTHERS);
    timeoutsRef.current.set(id, t);
  }, []);

  const valor = useMemo(() => ({ pushToast }), [pushToast]);

  return (
    <ContextoToastFeedbackAcoesUiTranscribrothers.Provider value={valor}>
      {props.children}
      {createPortal(
        <div className="tb-toast-stack" aria-live="polite">
          {items.map((it) => (
            <div key={it.id} className={`tb-toast tb-toast-${it.variant}`} role="status">
              {it.message}
            </div>
          ))}
        </div>,
        document.body,
      )}
    </ContextoToastFeedbackAcoesUiTranscribrothers.Provider>
  );
}
