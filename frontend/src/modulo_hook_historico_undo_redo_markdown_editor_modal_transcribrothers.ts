import { useCallback, useRef, type KeyboardEvent } from "react";

const LIMITE_ENTRADAS_PILHA_UNDO_MARKDOWN_EDITOR_MODAL = 100;

/**
 * Histórico de undo/redo para o textarea controlado do modal.
 * Textareas com `value` via React não preservam a pilha nativa do navegador.
 */
export function useHistoricoUndoRedoMarkdownEditorModalTranscribrothers(
  valorAtual: string,
  aoAlterarValor: (valor: string) => void,
) {
  const pilhaUndoRef = useRef<string[]>([]);
  const pilhaRedoRef = useRef<string[]>([]);
  const aplicandoUndoOuRedoRef = useRef(false);

  const empilharSnapshotUndoMarkdownEditorTranscribrothers = useCallback(
    (snapshot: string) => {
      if (aplicandoUndoOuRedoRef.current) return;

      const pilha = pilhaUndoRef.current;
      const topo = pilha[pilha.length - 1];
      if (topo === snapshot) return;

      pilha.push(snapshot);
      if (pilha.length > LIMITE_ENTRADAS_PILHA_UNDO_MARKDOWN_EDITOR_MODAL) {
        pilha.shift();
      }
      pilhaRedoRef.current = [];
    },
    [],
  );

  const alterarValorMarkdownComHistoricoUndoTranscribrothers = useCallback(
    (novoValor: string, opcoes?: { registrarUndo?: boolean }) => {
      const registrarUndo = opcoes?.registrarUndo !== false;
      if (
        registrarUndo &&
        !aplicandoUndoOuRedoRef.current &&
        novoValor !== valorAtual
      ) {
        empilharSnapshotUndoMarkdownEditorTranscribrothers(valorAtual);
      }
      aoAlterarValor(novoValor);
    },
    [aoAlterarValor, empilharSnapshotUndoMarkdownEditorTranscribrothers, valorAtual],
  );

  const desfazerAlteracaoMarkdownEditorTranscribrothers = useCallback((): boolean => {
    const pilhaUndo = pilhaUndoRef.current;
    if (pilhaUndo.length === 0) return false;

    const valorAnterior = pilhaUndo.pop();
    if (valorAnterior == null) return false;

    aplicandoUndoOuRedoRef.current = true;
    pilhaRedoRef.current.push(valorAtual);
    aoAlterarValor(valorAnterior);
    aplicandoUndoOuRedoRef.current = false;
    return true;
  }, [aoAlterarValor, valorAtual]);

  const refazerAlteracaoMarkdownEditorTranscribrothers = useCallback((): boolean => {
    const pilhaRedo = pilhaRedoRef.current;
    if (pilhaRedo.length === 0) return false;

    const valorProximo = pilhaRedo.pop();
    if (valorProximo == null) return false;

    aplicandoUndoOuRedoRef.current = true;
    pilhaUndoRef.current.push(valorAtual);
    aoAlterarValor(valorProximo);
    aplicandoUndoOuRedoRef.current = false;
    return true;
  }, [aoAlterarValor, valorAtual]);

  const tratarAtalhoTecladoUndoRedoMarkdownNoTextareaTranscribrothers = useCallback(
    (evento: KeyboardEvent<HTMLTextAreaElement>): boolean => {
      const teclaComando = evento.ctrlKey || evento.metaKey;
      if (!teclaComando) return false;

      const tecla = evento.key.toLowerCase();

      if (tecla === "z" && !evento.shiftKey) {
        if (!desfazerAlteracaoMarkdownEditorTranscribrothers()) return false;
        evento.preventDefault();
        return true;
      }

      if (tecla === "y" || (tecla === "z" && evento.shiftKey)) {
        if (!refazerAlteracaoMarkdownEditorTranscribrothers()) return false;
        evento.preventDefault();
        return true;
      }

      return false;
    },
    [
      desfazerAlteracaoMarkdownEditorTranscribrothers,
      refazerAlteracaoMarkdownEditorTranscribrothers,
    ],
  );

  return {
    alterarValorMarkdownComHistoricoUndoTranscribrothers,
    tratarAtalhoTecladoUndoRedoMarkdownNoTextareaTranscribrothers,
  };
}
