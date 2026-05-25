/**
 * Preset «Sem vídeo» no FAB de reprodução de bug: roteiro autônomo só com texto e imagens.
 */
export const TEXTO_INSTRUCAO_TEMPLATE_FAB_REGENERACAO_REPRODUCAO_BUG_SEM_VIDEO_TRANSCRIBROTHERS =
  [
    "Reescreva o roteiro de reprodução do bug para quem NÃO terá o vídeo nem o player.",
    "",
    "Remova ou substitua links [MM:SS](?t=SEGUNDOS) e menções a assistir, gravar ou reproduzir o vídeo.",
    "",
    "Cada passo relevante deve descrever a ação com clareza (clique, campo, URL) e incluir a imagem com ![](assets/…png) do instante do clique.",
    "",
    "Não invente cliques que não constem do JSON original. Use a transcrição só como complemento.",
    "",
    "Mantenha ou complete a seção «## Resultado observado» com o comportamento incorreto.",
  ].join("\n");
