// Configuração do site. Este é o único arquivo de JavaScript que você precisa editar.
window.EMPATIA = {
  // Endereço do Apps Script que grava os leads na planilha (termina em /exec).
  // Passo a passo no README, seção "Planilha de leads". Vazio: o formulário leva ao WhatsApp, mas nada é gravado.
  planilhaUrl: "",

  // WhatsApp da clínica, só números, com 55 e DDD.
  whatsapp: "559491182268",

  // E-mail obrigatório no formulário? false = aparece como "(opcional)" (costuma converter mais).
  emailObrigatorio: true,

  // Medição. Cole os IDs quando tiver: "GTM-XXXXXXX" e o número do Pixel do Meta.
  gtmId: "",
  pixelId: "",
  // "aviso": GTM e Pixel carregam logo e a pessoa pode recusar (mede mais).
  // "consentimento": só carregam depois do "Aceitar".
  cookies: "aviso",
};
