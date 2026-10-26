export const LIMITE_DE_CARACTERES_DO_TITULO_DA_VINHETA = 48;

export const PALETA_PADRAO_DA_VINHETA = {
  fundo: "#0e1c2f",
  plano_principal: "#1b4f72",
  plano_destaque: "#c4a35a",
  texto: "#f7f4ef",
};

export type CoresDaVinheta = {
  fundo: string;
  plano_principal: string;
  plano_destaque: string;
  texto: string;
};

export type ResultadoDaValidacaoDaVinheta =
  | { valida: true; titulo: string; cores: CoresDaVinheta }
  | { valida: false; mensagem: string };

const NOMES_DAS_CORES: Record<keyof CoresDaVinheta, string> = {
  fundo: "fundo",
  plano_principal: "plano principal",
  plano_destaque: "plano de destaque",
  texto: "texto",
};

const ORDEM_DAS_CORES: (keyof CoresDaVinheta)[] = [
  "fundo",
  "plano_principal",
  "plano_destaque",
  "texto",
];

function cor_esta_no_formato_hex(cor: string): boolean {
  return /^#[0-9A-Fa-f]{6}$/.test(cor);
}

export function validar_titulo_e_cores_da_vinheta(
  titulo: string,
  cores: CoresDaVinheta,
): ResultadoDaValidacaoDaVinheta {
  const titulo_limpo = titulo.trim();
  if (!titulo_limpo) {
    return { valida: false, mensagem: "Informe um título." };
  }
  if (titulo_limpo.length > LIMITE_DE_CARACTERES_DO_TITULO_DA_VINHETA) {
    return {
      valida: false,
      mensagem: "O título aceita no máximo 48 caracteres.",
    };
  }
  for (const chave of ORDEM_DAS_CORES) {
    if (!cor_esta_no_formato_hex(cores[chave])) {
      return {
        valida: false,
        mensagem: `A cor do ${NOMES_DAS_CORES[chave]} precisa estar no formato #RRGGBB.`,
      };
    }
  }
  return { valida: true, titulo: titulo_limpo, cores };
}
