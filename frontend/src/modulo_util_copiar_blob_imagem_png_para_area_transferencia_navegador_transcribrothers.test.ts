import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";
import { copiarBlobImagemPngParaAreaTransferenciaNavegadorTranscribrothers } from "./modulo_util_copiar_blob_imagem_png_para_area_transferencia_navegador_transcribrothers.ts";

describe("copiarBlobImagemPngParaAreaTransferenciaNavegadorTranscribrothers", () => {
  const clipboardWriteOriginal = navigator.clipboard?.write;
  const ClipboardItemOriginal = globalThis.ClipboardItem;

  beforeEach(() => {
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: {
        write: vi.fn().mockResolvedValue(undefined),
      },
    });
    // @ts-expect-error stub de teste
    globalThis.ClipboardItem = class ClipboardItemStub {
      constructor(public items: Record<string, Blob>) {}
    };
  });

  afterEach(() => {
    if (clipboardWriteOriginal) {
      Object.defineProperty(navigator, "clipboard", {
        configurable: true,
        value: { write: clipboardWriteOriginal },
      });
    }
    globalThis.ClipboardItem = ClipboardItemOriginal;
  });

  it("escreve ClipboardItem com image/png", async () => {
    const blob = new Blob([new Uint8Array([1, 2, 3])], { type: "image/png" });
    await copiarBlobImagemPngParaAreaTransferenciaNavegadorTranscribrothers(blob);
    expect(navigator.clipboard.write).toHaveBeenCalledTimes(1);
    const arg = vi.mocked(navigator.clipboard.write).mock.calls[0][0];
    expect(arg).toHaveLength(1);
    expect(arg[0]).toBeInstanceOf(ClipboardItem);
  });
});
