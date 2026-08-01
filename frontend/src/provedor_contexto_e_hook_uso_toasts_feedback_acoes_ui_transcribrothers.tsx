import type { ReactNode } from "react";
import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import { createPortal } from "react-dom";
import "./estilos_css_portal_toasts_inferior_direita_feedback_ui_transcribrothers.css";

export type VarianteToastFeedbackUiTranscribrothers = "success" | "error" | "info";

type ItemToastInternoTranscribrothers = {
  id: string;
  message: string;
  variant: VarianteToastFeedbackUiTranscribrothers;
  /** Se definido, o toast não auto-fecha e mostra barra de progresso. */
  progresso?: {
    percentual: number | null;
    indeterminado: boolean;
  };
};

export type OpcoesToastProgressoTranscribrothers = {
  id?: string;
  message: string;
  percentual?: number | null;
  indeterminado?: boolean;
};

type ValorContextoToastTranscribrothers = {
  pushToast: (message: string, variant?: VarianteToastFeedbackUiTranscribrothers) => void;
  /** Toast persistente com barra (não auto-fecha). Devolve o id. */
  pushToastProgresso: (opcoes: OpcoesToastProgressoTranscribrothers) => string;
  atualizarToastProgresso: (
    id: string,
    opcoes: Partial<Pick<OpcoesToastProgressoTranscribrothers, "message" | "percentual" | "indeterminado">>,
  ) => void;
  removerToast: (id: string) => void;
};

const ContextoToastFeedbackAcoesUiTranscribrothers = createContext<ValorContextoToastTranscribrothers | null>(null);

const DURACAO_MS_TOAST_PADRAO_TRANSCRIBROTHERS = 4200;
const MAX_TOASTS_VISIVEIS_SIMULTANEOS_TRANSCRIBROTHERS = 5;

function novoIdToastTranscribrothers(): string {
  return typeof globalThis.crypto !== "undefined" && "randomUUID" in globalThis.crypto
    ? globalThis.crypto.randomUUID()
    : `toast-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

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

  const removerToast = useCallback((id: string) => {
    const prevT = timeoutsRef.current.get(id);
    if (prevT !== undefined) {
      window.clearTimeout(prevT);
      timeoutsRef.current.delete(id);
    }
    setItems((prev) => prev.filter((x) => x.id !== id));
  }, []);

  const pushToast = useCallback((message: string, variant: VarianteToastFeedbackUiTranscribrothers = "info") => {
    const id = novoIdToastTranscribrothers();
    setItems((prev) => [
      ...prev.slice(-(MAX_TOASTS_VISIVEIS_SIMULTANEOS_TRANSCRIBROTHERS - 1)),
      { id, message, variant },
    ]);
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

  const pushToastProgresso = useCallback((opcoes: OpcoesToastProgressoTranscribrothers) => {
    const id = opcoes.id?.trim() || novoIdToastTranscribrothers();
    const prevT = timeoutsRef.current.get(id);
    if (prevT !== undefined) {
      window.clearTimeout(prevT);
      timeoutsRef.current.delete(id);
    }
    const percentual =
      typeof opcoes.percentual === "number" && Number.isFinite(opcoes.percentual)
        ? Math.max(0, Math.min(100, opcoes.percentual))
        : null;
    const indeterminado = opcoes.indeterminado ?? percentual == null;
    setItems((prev) => {
      const semEste = prev.filter((x) => x.id !== id);
      return [
        ...semEste.slice(-(MAX_TOASTS_VISIVEIS_SIMULTANEOS_TRANSCRIBROTHERS - 1)),
        {
          id,
          message: opcoes.message,
          variant: "info",
          progresso: { percentual, indeterminado },
        },
      ];
    });
    return id;
  }, []);

  const atualizarToastProgresso = useCallback(
    (
      id: string,
      opcoes: Partial<Pick<OpcoesToastProgressoTranscribrothers, "message" | "percentual" | "indeterminado">>,
    ) => {
      setItems((prev) =>
        prev.map((it) => {
          if (it.id !== id || !it.progresso) return it;
          const percentual =
            opcoes.percentual === undefined
              ? it.progresso.percentual
              : typeof opcoes.percentual === "number" && Number.isFinite(opcoes.percentual)
                ? Math.max(0, Math.min(100, opcoes.percentual))
                : null;
          const indeterminado =
            opcoes.indeterminado !== undefined
              ? opcoes.indeterminado
              : percentual == null
                ? true
                : false;
          return {
            ...it,
            message: opcoes.message ?? it.message,
            progresso: { percentual, indeterminado },
          };
        }),
      );
    },
    [],
  );

  const valor = useMemo(
    () => ({ pushToast, pushToastProgresso, atualizarToastProgresso, removerToast }),
    [pushToast, pushToastProgresso, atualizarToastProgresso, removerToast],
  );

  return (
    <ContextoToastFeedbackAcoesUiTranscribrothers.Provider value={valor}>
      {props.children}
      {createPortal(
        <div className="tb-toast-stack" aria-live="polite">
          {items.map((it) => (
            <div key={it.id} className={`tb-toast tb-toast-${it.variant}`} role="status">
              <div className="tb-toast-mensagem">{it.message}</div>
              {it.progresso ? (
                <div
                  className={
                    it.progresso.indeterminado
                      ? "tb-toast-barra-progresso tb-toast-barra-progresso--indeterminada"
                      : "tb-toast-barra-progresso"
                  }
                  role="progressbar"
                  aria-valuemin={0}
                  aria-valuemax={100}
                  aria-valuenow={
                    it.progresso.indeterminado || it.progresso.percentual == null
                      ? undefined
                      : Math.round(it.progresso.percentual)
                  }
                >
                  <div
                    className="tb-toast-barra-progresso-preenchimento"
                    style={
                      it.progresso.indeterminado || it.progresso.percentual == null
                        ? undefined
                        : { width: `${it.progresso.percentual}%` }
                    }
                  />
                </div>
              ) : null}
            </div>
          ))}
        </div>,
        document.body,
      )}
    </ContextoToastFeedbackAcoesUiTranscribrothers.Provider>
  );
}
