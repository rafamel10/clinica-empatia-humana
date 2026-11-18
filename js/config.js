// Configuração do site. Este é o único arquivo que você precisa editar.
window.EMPATIA = {
  // Endereço do Apps Script que grava os pedidos na planilha (termina em /exec).
  // Passo a passo no README, seção "Planilha de leads".
  // Vazio: o formulário continua funcionando e leva a pessoa ao WhatsApp, mas nada é gravado.
  planilhaUrl: "",

  // WhatsApp da clínica, só números, com 55 e DDD.
  whatsapp: "559491182268",

  // Vídeos que aparecem na seção "A clínica". Cole os links entre aspas, separados por vírgula.
  // Aceita Reels do Instagram, vídeos/Shorts do YouTube ou arquivos .mp4 colocados em assets/video/.
  // Exemplo:
  //   videos: [
  //     "https://www.instagram.com/reel/XXXXXXXXXXX/",
  //     { url: "https://youtu.be/XXXXXXXXXXX", titulo: "Como funciona a ozonioterapia" },
  //     { url: "assets/video/clinica.mp4", capa: "assets/img/clinica-sala.webp" },
  //   ],
  // Vazio: a parte de vídeos fica escondida.
  videos: [],
};
