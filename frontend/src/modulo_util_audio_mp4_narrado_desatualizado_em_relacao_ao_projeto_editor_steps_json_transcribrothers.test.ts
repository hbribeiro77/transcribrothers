import { describe, expect, it } from "vitest";
import {
  audioMp4NarradoDesatualizadoEmRelacaoAoProjetoEditorDosStepsJsonTranscribrothers,
  CHAVE_STEPS_EDITOR_VIDEO_NARRADO_AUDIO_MP4_DESATUALIZADO_TRANSCRIBROTHERS,
} from "./modulo_util_audio_mp4_narrado_desatualizado_em_relacao_ao_projeto_editor_steps_json_transcribrothers.ts";

describe("audioMp4NarradoDesatualizadoEmRelacaoAoProjetoEditorDosStepsJsonTranscribrothers", () => {
  it("respeita a flag sticky verdadeira", () => {
    expect(
      audioMp4NarradoDesatualizadoEmRelacaoAoProjetoEditorDosStepsJsonTranscribrothers({
        [CHAVE_STEPS_EDITOR_VIDEO_NARRADO_AUDIO_MP4_DESATUALIZADO_TRANSCRIBROTHERS]: true,
      }),
    ).toBe(true);
  });

  it("respeita a flag sticky falsa mesmo com promoção antiga", () => {
    expect(
      audioMp4NarradoDesatualizadoEmRelacaoAoProjetoEditorDosStepsJsonTranscribrothers({
        [CHAVE_STEPS_EDITOR_VIDEO_NARRADO_AUDIO_MP4_DESATUALIZADO_TRANSCRIBROTHERS]: false,
        editor_video_narrado_projeto_previews_promovidas: 2,
        editor_video_narrado_projeto_salvo_em: "2026-08-18T20:00:00+00:00",
        video_com_narracao_tts: { gerado_em: "2026-08-18T10:00:00+00:00" },
      }),
    ).toBe(false);
  });

  it("legado: promoção após o MP4 marca desatualizado", () => {
    expect(
      audioMp4NarradoDesatualizadoEmRelacaoAoProjetoEditorDosStepsJsonTranscribrothers({
        editor_video_narrado_projeto_previews_promovidas: 1,
        editor_video_narrado_projeto_salvo_em: "2026-08-18T20:00:00.000Z",
        video_com_narracao_tts: { gerado_em: "2026-08-18T10:00:00.000Z" },
      }),
    ).toBe(true);
  });

  it("legado: MP4 mais novo que o save com promoção não marca", () => {
    expect(
      audioMp4NarradoDesatualizadoEmRelacaoAoProjetoEditorDosStepsJsonTranscribrothers({
        editor_video_narrado_projeto_previews_promovidas: 1,
        editor_video_narrado_projeto_salvo_em: "2026-08-18T10:00:00.000Z",
        video_com_narracao_tts: { gerado_em: "2026-08-18T20:00:00.000Z" },
      }),
    ).toBe(false);
  });

  it("save sem promoção não marca desatualizado", () => {
    expect(
      audioMp4NarradoDesatualizadoEmRelacaoAoProjetoEditorDosStepsJsonTranscribrothers({
        editor_video_narrado_projeto_previews_promovidas: 0,
        editor_video_narrado_projeto_salvo_em: "2026-08-18T20:00:00.000Z",
        video_com_narracao_tts: { gerado_em: "2026-08-18T10:00:00.000Z" },
      }),
    ).toBe(false);
  });
});
