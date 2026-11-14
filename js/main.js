(function () {
  "use strict";

  var cfg = window.EMPATIA || {};
  var pagina = document.body.getAttribute("data-pagina");
  var params = new URLSearchParams(location.search);
  var numeroClinica = String(cfg.whatsapp || "559491182268").replace(/\D/g, "");

  var CHAVE_NOME = "empatiaNome";           // sessionStorage: primeiro nome para o obrigado
  var CHAVE_INTERESSE = "empatiaInteresse"; // sessionStorage: tratamento escolhido
  var CHAVE_LEAD = "empatiaLead";           // sessionStorage: dispara o Lead uma vez no obrigado

  function guardar(chave, valor) { try { sessionStorage.setItem(chave, valor); } catch (e) {} }
  function ler(chave) { try { return sessionStorage.getItem(chave); } catch (e) { return null; } }
  function apagar(chave) { try { sessionStorage.removeItem(chave); } catch (e) {} }

  function linkWhats(mensagem) {
    return "https://wa.me/" + numeroClinica + "?text=" + encodeURIComponent(mensagem);
  }

  // Nome de cada opção do formulário, como aparece na planilha e na mensagem do WhatsApp
  var INTERESSES = {
    varizes: "vasinhos e varizes",
    dor: "dor (ozonioterapia)",
    medidas: "gordura localizada (lipo ozonizada)",
    pele: "pele e rosto",
    intestino: "intestino e detox",
    cursos: "cursos para profissionais",
    outro: "orientação sobre os tratamentos",
  };

  /* Cliques no WhatsApp contam como contato no Pixel ---------------------- */
  document.addEventListener("click", function (e) {
    var link = e.target.closest && e.target.closest("[data-whatsapp]");
    if (!link) return;
    if (typeof window.fbq === "function") window.fbq("track", "Contact");
    if (typeof window.gtag === "function") window.gtag("event", "contact", { method: "whatsapp" });
  });

  /* Página de obrigado ---------------------------------------------------- */
  if (pagina === "obrigado") {
    var nome = ler(CHAVE_NOME);
    var interesse = ler(CHAVE_INTERESSE);
    var titulo = document.querySelector("[data-titulo]");
    if (nome && titulo) titulo.textContent = "Recebemos seu pedido, " + nome + ".";

    var mensagem = "Olá! " + (nome ? "Meu nome é " + nome + ". " : "") +
      "Acabei de preencher o formulário do site. " +
      (interesse === INTERESSES.cursos
        ? "Quero saber das próximas turmas dos cursos."
        : "Quero agendar uma avaliação" + (interesse ? " para " + interesse : "") + ".");
    document.querySelectorAll("[data-whatsapp]").forEach(function (a) { a.href = linkWhats(mensagem); });

    if (ler(CHAVE_LEAD) === "1") {
      apagar(CHAVE_LEAD);
      if (typeof window.fbq === "function") window.fbq("track", "Lead");
      if (typeof window.gtag === "function") window.gtag("event", "generate_lead");
    }
    return;
  }

  if (pagina !== "inicio") return;

  /* Menu do celular -------------------------------------------------------- */
  var botaoMenu = document.querySelector(".nav__botao");
  var listaMenu = document.getElementById("nav-lista");
  function fecharMenu() {
    botaoMenu.setAttribute("aria-expanded", "false");
    botaoMenu.textContent = "Menu";
  }
  if (botaoMenu && listaMenu) {
    botaoMenu.addEventListener("click", function () {
      var aberto = botaoMenu.getAttribute("aria-expanded") === "true";
      botaoMenu.setAttribute("aria-expanded", String(!aberto));
      botaoMenu.textContent = aberto ? "Menu" : "Fechar";
    });
    listaMenu.addEventListener("click", function (e) {
      if (e.target.closest("a")) fecharMenu();
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && botaoMenu.getAttribute("aria-expanded") === "true") {
        fecharMenu();
        botaoMenu.focus();
      }
    });
  }

  var form = document.getElementById("form-agendar");
  var seletor = document.getElementById("interesse");

  /* Versões da abertura para cada campanha --------------------------------- */
  // Use no anúncio: ?tratamento=varizes (ou dor, medidas, pele, intestino, cursos)
  var VERSOES = {
    varizes: {
      titulo: "Tratamento de vasinhos e varizes em Canaã dos Carajás",
      sub: "Avaliação das pernas com a biomédica Dra. Adelaine Montel e tratamento com PEIM integrativo e ozônio, com parcelamento em até 10x.",
    },
    dor: {
      titulo: "Ozonioterapia para dor em Canaã dos Carajás",
      sub: "Para dores crônicas na coluna, nos joelhos e nas articulações, com protocolo definido na avaliação com a biomédica e ozonioterapeuta Dra. Adelaine Montel.",
    },
    medidas: {
      titulo: "Lipo ozonizada para gordura localizada, sem cortes",
      sub: "Aplicações de ozônio na região que incomoda, com avaliação e acompanhamento da Dra. Adelaine Montel em Canaã dos Carajás.",
    },
    pele: {
      titulo: "Limpeza de pele e tratamentos faciais em Canaã dos Carajás",
      sub: "Limpeza de pele profunda, peelings e microagulhamento com a biomédica esteta Dra. Adelaine Montel.",
    },
    intestino: {
      titulo: "Cuidado integrativo do intestino em Canaã dos Carajás",
      sub: "Programa Disbiose Zero, enema de café e análise de exames com a Dra. Adelaine Montel.",
    },
    cursos: {
      titulo: "Cursos para profissionais da saúde e da estética",
      sub: "Interpretação de exames, ozonioterapia na dor e limpeza de pele, com a Dra. Adelaine Montel em Canaã dos Carajás.",
    },
  };

  var versao = String(params.get("tratamento") || "").toLowerCase();
  if (VERSOES[versao]) {
    var h1 = document.querySelector('[data-variavel="titulo"]');
    var sub = document.querySelector('[data-variavel="sub"]');
    if (h1) h1.textContent = VERSOES[versao].titulo;
    if (sub) sub.textContent = VERSOES[versao].sub;
    if (seletor) seletor.value = versao;
  }

  /* Botões que levam ao formulário ---------------------------------------- */
  document.addEventListener("click", function (e) {
    var gatilho = e.target.closest && e.target.closest("[data-ir-form]");
    if (!gatilho) return;
    var alvo = document.getElementById("agendar");
    if (!alvo) return;
    e.preventDefault();
    var escolha = gatilho.getAttribute("data-interesse");
    if (escolha && seletor) {
      seletor.value = escolha;
      mostrarErro(seletor, "");
    }
    var reduzir = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    alvo.scrollIntoView({ behavior: reduzir ? "auto" : "smooth", block: "start" });
    var nomeInput = form && form.elements.nome;
    if (nomeInput) setTimeout(function () { nomeInput.focus({ preventScroll: true }); }, reduzir ? 0 : 450);
  });

  /* Barra fixa do celular some quando o formulário está na tela ------------ */
  var barra = document.querySelector(".barra-fixa");
  var cartao = document.getElementById("agendar");
  if (barra && cartao && "IntersectionObserver" in window) {
    new IntersectionObserver(function (entradas) {
      barra.classList.toggle("barra-fixa--oculta", entradas[0].isIntersecting);
    }, { threshold: 0.15 }).observe(cartao);
  }

  /* Formulário ------------------------------------------------------------ */
  if (!form) return;

  var inputNome = form.elements.nome;
  var inputWhats = form.elements.whatsapp;
  var enviar = form.querySelector(".form__enviar");
  var textoEnviar = enviar.textContent;

  function mostrarErro(campo, mensagem) {
    var erro = document.getElementById(campo.id + "-erro");
    if (mensagem) {
      campo.setAttribute("aria-invalid", "true");
      if (erro) { erro.textContent = mensagem; erro.hidden = false; }
    } else {
      campo.removeAttribute("aria-invalid");
      if (erro) { erro.textContent = ""; erro.hidden = true; }
    }
  }

  // Telefone: só dígitos, sem o 55 do país e sem o 0 da operadora
  function digitosTelefone(valor) {
    var d = String(valor || "").replace(/\D/g, "");
    if ((d.length === 12 || d.length === 13) && d.indexOf("55") === 0) d = d.slice(2);
    if ((d.length === 11 || d.length === 12) && d[0] === "0") d = d.slice(1);
    return d;
  }
  function telefoneValido(d) {
    if (d.length !== 10 && d.length !== 11) return false;
    if (d[0] === "0" || d[1] === "0") return false;
    if (d.length === 11 && d[2] !== "9") return false;
    return true;
  }
  function formatarTelefone(d) {
    var meio = d.length === 11 ? 5 : 4;
    return "(" + d.slice(0, 2) + ") " + d.slice(2, 2 + meio) + "-" + d.slice(2 + meio);
  }

  inputWhats.addEventListener("blur", function () {
    var d = digitosTelefone(inputWhats.value);
    if (telefoneValido(d)) inputWhats.value = formatarTelefone(d);
  });
  [inputNome, inputWhats].forEach(function (campo) {
    campo.addEventListener("input", function () {
      if (campo.getAttribute("aria-invalid")) mostrarErro(campo, "");
    });
  });
  seletor.addEventListener("change", function () { mostrarErro(seletor, ""); });

  var enviando = false;

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (enviando) return;
    var nome = inputNome.value.replace(/\s+/g, " ").trim();
    var tel = digitosTelefone(inputWhats.value);
    var escolha = seletor.value;
    var primeiroErro = null;

    if (nome.length < 2) {
      mostrarErro(inputNome, "Escreva seu nome para a equipe saber com quem vai falar.");
      primeiroErro = inputNome;
    } else mostrarErro(inputNome, "");

    if (!telefoneValido(tel)) {
      mostrarErro(inputWhats, "Confira o número: coloque o DDD e o celular, por exemplo (94) 99999-9999.");
      primeiroErro = primeiroErro || inputWhats;
    } else mostrarErro(inputWhats, "");

    if (!INTERESSES[escolha]) {
      mostrarErro(seletor, "Escolha o que você quer tratar. Se ainda não sabe, marque a última opção.");
      primeiroErro = primeiroErro || seletor;
    } else mostrarErro(seletor, "");

    if (primeiroErro) { primeiroErro.focus(); return; }

    inputWhats.value = formatarTelefone(tel);
    enviando = true;
    enviar.disabled = true;
    enviar.textContent = "Enviando…";

    var dados = {
      nome: nome,
      whatsapp: "55" + tel,
      interesse: INTERESSES[escolha],
      utm_source: params.get("utm_source") || "",
      utm_medium: params.get("utm_medium") || "",
      utm_campaign: params.get("utm_campaign") || "",
      utm_content: params.get("utm_content") || "",
      utm_term: params.get("utm_term") || "",
      clique: params.get("fbclid") ? "fbclid" : params.get("gclid") ? "gclid" : "",
      pagina: location.href.split("#")[0],
      origem: document.referrer || "",
      site: form.elements.site.value,
    };

    var gravar = cfg.planilhaUrl
      ? fetch(cfg.planilhaUrl, {
          method: "POST",
          mode: "no-cors",
          keepalive: true,
          headers: { "Content-Type": "text/plain;charset=utf-8" },
          body: JSON.stringify(dados),
        }).catch(function () {})
      : Promise.resolve();
    if (!cfg.planilhaUrl && window.console) console.warn("Empatia Humana: planilhaUrl vazio em js/config.js, o pedido não foi gravado.");

    // Não segura a pessoa mais que 3 segundos esperando a planilha
    var limite = new Promise(function (ok) { setTimeout(ok, 3000); });

    Promise.race([gravar, limite]).then(function () {
      guardar(CHAVE_NOME, nome.split(" ")[0]);
      guardar(CHAVE_INTERESSE, INTERESSES[escolha]);
      guardar(CHAVE_LEAD, "1");
      // Mantém as UTMs no endereço do obrigado, para o Pixel e o Tintim
      var utm = [];
      params.forEach(function (v, k) {
        if (k.indexOf("utm_") === 0 || k === "tratamento") utm.push(encodeURIComponent(k) + "=" + encodeURIComponent(v));
      });
      location.href = "obrigado.html" + (utm.length ? "?" + utm.join("&") : "");
      enviando = false;
      enviar.disabled = false;
      enviar.textContent = textoEnviar;
    });
  });
})();
