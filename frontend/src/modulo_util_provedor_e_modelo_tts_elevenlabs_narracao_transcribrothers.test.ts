import { describe, expect, it } from "vitest";

import {
  escolherModeloTtsDaListaDisponivelTranscribrothers,
  listarModelosTtsDaListaDisponivelTranscribrothers,
  modeloLitellmPareceTtsPeloSlugTranscribrothers,
  rotuloCurtoModeloTtsParaUiTranscribrothers,
} from "./modulo_api_gerar_narracao_tts_markdown_job_transcribrothers.ts";
import {
  MODELO_TTS_ELEVENLABS_V4_TRANSCRIBROTHERS,
  PROVEDOR_TTS_ELEVENLABS_TRANSCRIBROTHERS,
  PROVEDOR_TTS_LITELLM_TRANSCRIBROTHERS,
  mesclarModelosTtsLitellmComElevenlabsSeConfiguradoTranscribrothers,
  modeloTtsPareceElevenlabsPeloSlugTranscribrothers,
  normalizarProvedorTtsNarracaoUiTranscribrothers,
} from "./modulo_util_provedor_e_modelo_tts_elevenlabs_narracao_transcribrothers.ts";

describe("slug TTS inclui eleven_v4 e rejeita turbo", () => {
  it("reconhece eleven_v4 como modelo TTS da narração", () => {
    expect(modeloLitellmPareceTtsPeloSlugTranscribrothers("eleven_v4")).toBe(true);
    expect(modeloTtsPareceElevenlabsPeloSlugTranscribrothers("eleven_v4")).toBe(true);
  });

  it("não trata eleven_v4_turbo como opção da UI", () => {
    expect(modeloLitellmPareceTtsPeloSlugTranscribrothers("eleven_v4_turbo")).toBe(false);
    expect(modeloTtsPareceElevenlabsPeloSlugTranscribrothers("eleven_v4_turbo")).toBe(false);
  });

  it("lista e escolhe eleven_v4 junto com slugs Gemini", () => {
    const lista = listarModelosTtsDaListaDisponivelTranscribrothers([
      "gemini/gemini-2.5-flash-preview-tts",
      "eleven_v4",
      "eleven_v4_turbo",
    ]);
    expect(lista).toEqual(["gemini/gemini-2.5-flash-preview-tts", "eleven_v4"]);
    expect(escolherModeloTtsDaListaDisponivelTranscribrothers(lista, "eleven_v4")).toBe(
      "eleven_v4",
    );
  });

  it("rótulo curto identifica ElevenLabs", () => {
    expect(rotuloCurtoModeloTtsParaUiTranscribrothers("eleven_v4")).toBe("eleven_v4 (ElevenLabs)");
  });
});

describe("provedor e mescla da lista TTS", () => {
  it("normaliza provedor vazio para litellm", () => {
    expect(normalizarProvedorTtsNarracaoUiTranscribrothers("")).toBe(
      PROVEDOR_TTS_LITELLM_TRANSCRIBROTHERS,
    );
    expect(normalizarProvedorTtsNarracaoUiTranscribrothers("ElevenLabs")).toBe(
      PROVEDOR_TTS_ELEVENLABS_TRANSCRIBROTHERS,
    );
  });

  it("só inclui eleven_v4 quando a chave está configurada", () => {
    const base = ["gemini/gemini-2.5-flash-preview-tts"];
    expect(
      mesclarModelosTtsLitellmComElevenlabsSeConfiguradoTranscribrothers(base, ["eleven_v4"], false),
    ).toEqual(base);
    expect(
      mesclarModelosTtsLitellmComElevenlabsSeConfiguradoTranscribrothers(base, ["eleven_v4"], true),
    ).toEqual(["gemini/gemini-2.5-flash-preview-tts", MODELO_TTS_ELEVENLABS_V4_TRANSCRIBROTHERS]);
  });
});
