// Configuração do site. Este é o único arquivo que você precisa editar.
window.EMPATIA = {
  // Endereço do Apps Script que grava os pedidos na planilha (termina em /exec).
  // Passo a passo no README, seção "Planilha de leads".
  // Vazio: o formulário continua funcionando e leva a pessoa ao WhatsApp, mas nada é gravado.
  planilhaUrl: "",

  // WhatsApp da clínica, só números, com 55 e DDD.
  whatsapp: "559491182268",

  // Antes e depois. A seção só aparece quando houver pelo menos um item aqui.
  // Só coloque fotos de pacientes que assinaram o termo de consentimento (TCLE)
  // autorizando a publicação, como exige o Código de Ética da Biomedicina.
  // Ponha as fotos em assets/img/resultados/ e preencha assim:
  // { antes: "assets/img/resultados/peim-1-antes.jpg", depois: "assets/img/resultados/peim-1-depois.jpg",
  //   tratamento: "PEIM integrativo", legenda: "4 sessões" },
  resultados: [],
};
