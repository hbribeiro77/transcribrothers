/**
 * Substitui ``window.confirm`` pelo overlay customizado do app.
 * Uso: ``const ok = await pedirConfirmacao({...}); if (!ok) return;``
 * e renderizar ``elementoDialogoConfirmacao`` no JSX do componente.
 */

import { useCallback, useRef, useState, type ReactElement } from "react";
import { ComponenteDialogoConfirmacaoAcaoDestrutivaOverlayTranscribrothers } from "./componente_dialogo_confirmacao_acao_destrutiva_overlay_transcribrothers.tsx";

export type OpcoesPedirConfirmacaoDialogoUiTranscribrothers = {
  titulo: string;
  mensagem: string;
  rotuloConfirmar?: string;
  rotuloCancelar?: string;
  varianteConfirmar?: "destrutiva" | "neutra";
};

type PedidoConfirmacaoPendenteUiTranscribrothers = OpcoesPedirConfirmacaoDialogoUiTranscribrothers & {
  resolver: (ok: boolean) => void;
};

export type ResultadoHookDialogoConfirmacaoAcaoUiTranscribrothers = {
  pedirConfirmacao: (
    opcoes: OpcoesPedirConfirmacaoDialogoUiTranscribrothers,
  ) => Promise<boolean>;
  elementoDialogoConfirmacao: ReactElement;
};

export function usarDialogoConfirmacaoAcaoUiSubstituindoWindowConfirmTranscribrothers(): ResultadoHookDialogoConfirmacaoAcaoUiTranscribrothers {
  const [pedido, setPedido] = useState<PedidoConfirmacaoPendenteUiTranscribrothers | null>(null);
  const pedidoRef = useRef<PedidoConfirmacaoPendenteUiTranscribrothers | null>(null);

  const fecharComResultado = useCallback((ok: boolean) => {
    const atual = pedidoRef.current;
    pedidoRef.current = null;
    setPedido(null);
    atual?.resolver(ok);
  }, []);

  const pedirConfirmacao = useCallback(
    (opcoes: OpcoesPedirConfirmacaoDialogoUiTranscribrothers) => {
      return new Promise<boolean>((resolver) => {
        // Se já houver um diálogo aberto, cancela o anterior (evita Promise pendurada).
        if (pedidoRef.current) {
          pedidoRef.current.resolver(false);
        }
        const novo: PedidoConfirmacaoPendenteUiTranscribrothers = { ...opcoes, resolver };
        pedidoRef.current = novo;
        setPedido(novo);
      });
    },
    [],
  );

  const elementoDialogoConfirmacao = (
    <ComponenteDialogoConfirmacaoAcaoDestrutivaOverlayTranscribrothers
      aberto={pedido !== null}
      titulo={pedido?.titulo || ""}
      mensagem={pedido?.mensagem || ""}
      rotuloConfirmar={pedido?.rotuloConfirmar}
      rotuloCancelar={pedido?.rotuloCancelar}
      varianteConfirmar={pedido?.varianteConfirmar ?? "destrutiva"}
      aoConfirmar={() => fecharComResultado(true)}
      aoCancelar={() => fecharComResultado(false)}
    />
  );

  return { pedirConfirmacao, elementoDialogoConfirmacao };
}
