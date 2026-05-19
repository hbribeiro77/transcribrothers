/**
 * Instrução enviada ao modelo na regeneração do tutorial (FAB «Regenerar tutorial»)
 * quando o utilizador escolhe o modelo rápido «Sem vídeo».
 */
export const TEXTO_INSTRUCAO_TEMPLATE_FAB_REGENERACAO_TUTORIAL_SEM_REFERENCIAS_VIDEO_DOCUMENTO_AUTONOMO_TRANSCRIBROTHERS =
  [
    "Reescreva o tutorial em Markdown para uma versão autónoma: o leitor não tem acesso ao vídeo original.",
    "",
    "Remova ou substitua referências ao vídeo ou à necessidade de o ver (timestamps clicáveis, «assista», «no minuto», «no trecho», «conforme o vídeo», saltos para o player, etc.).",
    "",
    "Onde o texto dependia de «ver o vídeo» para fazer sentido, desenvolva a explicação em prosa clara, usando apenas a transcrição (com tempos) e as figuras já fornecidas como base. O conteúdo que o trecho de vídeo ilustraria deve aparecer escrito, de forma coerente com o que se diz na transcrição e com o que as imagens mostram.",
    "",
    "Mantenha títulos, listas e código úteis. Preserve as referências a imagens existentes no Markdown (![](assets/…png)) na mesma ordem lógica, salvo se remover uma menção ao vídeo exigir um ajuste mínimo de redação em volta.",
    "",
    "Não invente factos que não constem da transcrição ou das imagens; se algo for ambíguo, seja explícito sobre a limitação.",
  ].join("\n");
