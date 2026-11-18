(function () {
  "use strict";

  var cfg = window.EMPATIA || {};
  var pagina = document.body.getAttribute("data-pagina");
  var params = new URLSearchParams(location.search);
  var numeroClinica = String(cfg.whatsapp || "559491182268").replace(/\D/g, "");
  var reduzirMovimento = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var CHAVE_NOME = "empatiaNome";           // sessionStorage: primeiro nome para o obrigado
  var CHAVE_INTERESSE = "empatiaInteresse"; // sessionStorage: tratamento escolhido
  var CHAVE_PERIODO = "empatiaPeriodo";     // sessionStorage: melhor horário
  var CHAVE_LEAD = "empatiaLead";           // sessionStorage: dispara o Lead uma vez no obrigado

  function guardar(chave, valor) { try { sessionStorage.setItem(chave, valor); } catch (e) {} }
  function ler(chave) { try { return sessionStorage.getItem(chave); } catch (e) { return null; } }
  function apagar(chave) { try { sessionStorage.removeItem(chave); } catch (e) {} }

  function linkWhats(mensagem) {
    return "https://wa.me/" + numeroClinica + "?text=" + encodeURIComponent(mensagem);
  }

  function evento(nome, dados) {
    if (typeof window.fbq === "function") window.fbq("trackCustom", nome, dados || {});
    if (typeof window.gtag === "function") window.gtag("event", nome, dados || {});
  }

  // Nome de cada opção, como aparece na planilha e na mensagem do WhatsApp
  var INTERESSES = {
    varizes: "vasinhos e varizes",
    dor: "dor (ozonioterapia)",
    medidas: "gordura localizada (lipo ozonizada)",
    pele: "pele e rosto",
    intestino: "intestino e detox",
    cursos: "cursos para profissionais",
    outro: "orientação sobre os tratamentos",
  };

  var PERIODOS = {
    "Manhã": "de manhã",
    "Tarde": "à tarde",
    "Sábado de manhã": "sábado de manhã",
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
    var periodo = ler(CHAVE_PERIODO);
    var titulo = document.querySelector("[data-titulo]");
    if (nome && titulo) titulo.textContent = "Recebemos seu pedido, " + nome + ".";

    var mensagem = "Olá! " + (nome ? "Meu nome é " + nome + ". " : "") +
      "Acabei de preencher o formulário do site. " +
      (interesse === INTERESSES.cursos
        ? "Quero saber das próximas turmas dos cursos."
        : "Quero agendar uma avaliação" + (interesse ? " para " + interesse : "") + "." +
          (PERIODOS[periodo] ? " O melhor horário para mim é " + PERIODOS[periodo] + "." : ""));
    document.querySelectorAll("[data-whatsapp]").forEach(function (a) { a.href = linkWhats(mensagem); });

    if (ler(CHAVE_LEAD) === "1") {
      apagar(CHAVE_LEAD);
      if (typeof window.fbq === "function") window.fbq("track", "Lead");
      if (typeof window.gtag === "function") window.gtag("event", "generate_lead");
    }
    return;
  }

  if (pagina !== "inicio") return;

  /* Utilidades de formulário --------------------------------------------- */

  function mostrarErro(alvo, mensagem) {
    // alvo pode ser um campo (input/select) ou o <p> de erro de um grupo de opções
    var erro = alvo.classList && alvo.classList.contains("campo__erro") ? alvo : document.getElementById(alvo.id + "-erro");
    if (alvo.tagName === "INPUT" || alvo.tagName === "SELECT") {
      if (mensagem) alvo.setAttribute("aria-invalid", "true");
      else alvo.removeAttribute("aria-invalid");
    }
    if (erro) {
      erro.textContent = mensagem || "";
      erro.hidden = !mensagem;
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

  function prepararCamposTexto(form) {
    var inputWhats = form.elements.whatsapp;
    inputWhats.addEventListener("blur", function () {
      var d = digitosTelefone(inputWhats.value);
      if (telefoneValido(d)) inputWhats.value = formatarTelefone(d);
    });
    [form.elements.nome, inputWhats].forEach(function (campo) {
      campo.addEventListener("input", function () {
        if (campo.getAttribute("aria-invalid")) mostrarErro(campo, "");
      });
    });
  }

  // Valida nome e WhatsApp. Devolve {nome, tel} ou null (e põe o foco no primeiro erro)
  function validarContato(form) {
    var inputNome = form.elements.nome;
    var inputWhats = form.elements.whatsapp;
    var nome = inputNome.value.replace(/\s+/g, " ").trim();
    var tel = digitosTelefone(inputWhats.value);
    var primeiro = null;

    if (nome.length < 2) {
      mostrarErro(inputNome, "Escreva seu nome para a equipe saber com quem vai falar.");
      primeiro = inputNome;
    } else mostrarErro(inputNome, "");

    if (!telefoneValido(tel)) {
      mostrarErro(inputWhats, "Confira o número: coloque o DDD e o celular, por exemplo (94) 99999-9999.");
      primeiro = primeiro || inputWhats;
    } else mostrarErro(inputWhats, "");

    if (primeiro) { primeiro.focus(); return null; }
    inputWhats.value = formatarTelefone(tel);
    return { nome: nome, tel: tel };
  }

  var enviando = false;

  function enviarLead(dados, botao) {
    if (enviando) return;
    enviando = true;
    var textoBotao = botao.textContent;
    botao.disabled = true;
    botao.textContent = "Enviando…";

    var pacote = {
      nome: dados.nome,
      whatsapp: "55" + dados.tel,
      interesse: INTERESSES[dados.interesse] || "",
      detalhe: dados.detalhe || "",
      periodo: dados.periodo || "",
      formulario: dados.formulario,
      utm_source: params.get("utm_source") || "",
      utm_medium: params.get("utm_medium") || "",
      utm_campaign: params.get("utm_campaign") || "",
      utm_content: params.get("utm_content") || "",
      utm_term: params.get("utm_term") || "",
      clique: params.get("fbclid") ? "fbclid" : params.get("gclid") ? "gclid" : "",
      pagina: location.href.split("#")[0],
      origem: document.referrer || "",
      site: dados.isca || "",
    };

    var gravar = cfg.planilhaUrl
      ? fetch(cfg.planilhaUrl, {
          method: "POST",
          mode: "no-cors",
          keepalive: true,
          headers: { "Content-Type": "text/plain;charset=utf-8" },
          body: JSON.stringify(pacote),
        }).catch(function () {})
      : Promise.resolve();
    if (!cfg.planilhaUrl && window.console) console.warn("Empatia Humana: planilhaUrl vazio em js/config.js, o pedido não foi gravado.");

    // Não segura a pessoa mais que 3 segundos esperando a planilha
    var limite = new Promise(function (ok) { setTimeout(ok, 3000); });

    Promise.race([gravar, limite]).then(function () {
      guardar(CHAVE_NOME, dados.nome.split(" ")[0]);
      guardar(CHAVE_INTERESSE, pacote.interesse);
      guardar(CHAVE_PERIODO, pacote.periodo);
      guardar(CHAVE_LEAD, "1");
      // Mantém as UTMs no endereço do obrigado, para o Pixel e o Tintim
      var manter = [];
      params.forEach(function (v, k) {
        if (k.indexOf("utm_") === 0 || k === "tratamento") manter.push(encodeURIComponent(k) + "=" + encodeURIComponent(v));
      });
      location.href = "obrigado.html" + (manter.length ? "?" + manter.join("&") : "");
      enviando = false;
      botao.disabled = false;
      botao.textContent = textoBotao;
    });
  }

  /* Quiz de agendamento -------------------------------------------------- */

  var quiz = document.getElementById("quiz");
  var passoAtual = 1;
  var TOTAL_PASSOS = 4;

  function valorRadio(nome) {
    var el = quiz && quiz.querySelector('input[name="' + nome + '"]:checked');
    return el ? el.value : "";
  }
  function marcarRadio(nome, valor) {
    var el = quiz && quiz.querySelector('input[name="' + nome + '"][value="' + valor + '"]');
    if (el) el.checked = true;
    return !!el;
  }
  function ramo() {
    return valorRadio("interesse") === "cursos" ? "cursos" : "paciente";
  }
  function etapaDo(n) {
    var etapas = quiz.querySelectorAll(".quiz__etapa");
    for (var i = 0; i < etapas.length; i++) {
      var e = etapas[i];
      if (Number(e.getAttribute("data-etapa")) === n && (!e.getAttribute("data-ramo") || e.getAttribute("data-ramo") === ramo())) return e;
    }
    return null;
  }
  function campoDoPasso(n) {
    if (n === 1) return "interesse";
    if (n === 2) return ramo() === "cursos" ? "area" : "tempo";
    if (n === 3) return "periodo";
    return null;
  }
  function erroDoPasso(n) {
    var nome = campoDoPasso(n);
    return nome ? quiz.querySelector('[data-erro="' + nome + '"]') : null;
  }
  function validarPasso(n) {
    var nome = campoDoPasso(n);
    if (!nome) return true;
    var erro = erroDoPasso(n);
    if (!valorRadio(nome)) {
      if (erro) mostrarErro(erro, "Escolha uma opção para continuar.");
      var primeiro = etapaDo(n).querySelector("input");
      if (primeiro) primeiro.focus();
      return false;
    }
    if (erro) mostrarErro(erro, "");
    return true;
  }

  function mostrarPasso(n, focar) {
    passoAtual = n;
    quiz.querySelectorAll(".quiz__etapa").forEach(function (e) { e.classList.remove("quiz__etapa--atual"); });
    var etapa = etapaDo(n);
    etapa.classList.add("quiz__etapa--atual");
    var contagem = quiz.querySelector("[data-passo-atual]");
    if (contagem) contagem.textContent = n;
    var barra = quiz.querySelector("[data-barra]");
    if (barra) barra.style.width = (n / TOTAL_PASSOS) * 100 + "%";
    quiz.querySelector("[data-voltar]").hidden = n === 1;
    quiz.querySelector("[data-continuar]").hidden = n === TOTAL_PASSOS;
    if (focar) {
      var alvo = n === TOTAL_PASSOS ? quiz.elements.nome : etapa;
      alvo.focus({ preventScroll: true });
      var cartao = document.getElementById("agendar");
      var topo = cartao.getBoundingClientRect().top;
      if (topo < 0 || topo > window.innerHeight * 0.6) {
        cartao.scrollIntoView({ behavior: reduzirMovimento ? "auto" : "smooth", block: "start" });
      }
      evento("QuizPasso", { passo: n });
    }
  }

  function avancar() {
    if (!validarPasso(passoAtual)) return;
    if (passoAtual < TOTAL_PASSOS) mostrarPasso(passoAtual + 1, true);
  }

  if (quiz) {
    mostrarPasso(1, false);

    quiz.querySelector("[data-continuar]").addEventListener("click", avancar);
    quiz.querySelector("[data-voltar]").addEventListener("click", function () {
      if (passoAtual > 1) mostrarPasso(passoAtual - 1, true);
    });

    // Quem toca numa opção vai direto para a próxima pergunta. No teclado, a pessoa usa o Continuar.
    var ultimoToque = 0;
    quiz.addEventListener("pointerdown", function () { ultimoToque = Date.now(); });
    quiz.addEventListener("change", function (e) {
      if (e.target.type !== "radio") return;
      var erro = erroDoPasso(passoAtual);
      if (erro) mostrarErro(erro, "");
      if (Date.now() - ultimoToque < 1200 && passoAtual < TOTAL_PASSOS) {
        setTimeout(avancar, 260);
      }
    });

    prepararCamposTexto(quiz);

    quiz.addEventListener("submit", function (e) {
      e.preventDefault();
      if (passoAtual < TOTAL_PASSOS) { avancar(); return; }
      // Confere se as perguntas anteriores foram respondidas
      for (var n = 1; n < TOTAL_PASSOS; n++) {
        if (!valorRadio(campoDoPasso(n))) {
          mostrarPasso(n, true);
          validarPasso(n);
          return;
        }
      }
      var contato = validarContato(quiz);
      if (!contato) return;
      enviarLead({
        nome: contato.nome,
        tel: contato.tel,
        interesse: valorRadio("interesse"),
        detalhe: valorRadio(campoDoPasso(2)),
        periodo: valorRadio("periodo"),
        formulario: "quiz",
        isca: quiz.elements.site.value,
      }, quiz.querySelector(".form__enviar"));
    });
  }

  /* Formulário final (curto) --------------------------------------------- */

  var formFinal = document.querySelector('[data-form="final"]');
  if (formFinal) {
    prepararCamposTexto(formFinal);
    var seletorFinal = formFinal.elements.interesse;
    seletorFinal.addEventListener("change", function () { mostrarErro(seletorFinal, ""); });

    formFinal.addEventListener("submit", function (e) {
      e.preventDefault();
      var contato = validarContato(formFinal);
      var escolha = seletorFinal.value;
      if (!INTERESSES[escolha]) {
        mostrarErro(seletorFinal, "Escolha o que você quer tratar. Se ainda não sabe, marque a última opção.");
        if (contato) seletorFinal.focus();
        return;
      }
      mostrarErro(seletorFinal, "");
      if (!contato) return;
      enviarLead({
        nome: contato.nome,
        tel: contato.tel,
        interesse: escolha,
        formulario: "final",
        isca: formFinal.elements.site.value,
      }, formFinal.querySelector(".form__enviar"));
    });
  }

  /* Abas dos tratamentos -------------------------------------------------- */

  var abas = document.querySelector("[data-abas]");
  var selecionarAba = function () {};
  if (abas) {
    abas.classList.add("abas--ativas");
    var botoesAba = Array.prototype.slice.call(abas.querySelectorAll('[role="tab"]'));

    selecionarAba = function (botao, focar) {
      botoesAba.forEach(function (b) {
        var ativo = b === botao;
        b.setAttribute("aria-selected", String(ativo));
        b.tabIndex = ativo ? 0 : -1;
        document.getElementById(b.getAttribute("aria-controls")).hidden = !ativo;
      });
      if (focar) botao.focus();
    };

    selecionarAba(botoesAba[0], false);

    botoesAba.forEach(function (b, i) {
      b.addEventListener("click", function () {
        selecionarAba(b, false);
        evento("AbaTratamento", { aba: b.id.replace("aba-", "") });
      });
      b.addEventListener("keydown", function (e) {
        var alvo = null;
        if (e.key === "ArrowRight") alvo = botoesAba[(i + 1) % botoesAba.length];
        if (e.key === "ArrowLeft") alvo = botoesAba[(i - 1 + botoesAba.length) % botoesAba.length];
        if (e.key === "Home") alvo = botoesAba[0];
        if (e.key === "End") alvo = botoesAba[botoesAba.length - 1];
        if (alvo) { e.preventDefault(); selecionarAba(alvo, true); }
      });
    });
  }

  /* Versões da abertura para cada campanha --------------------------------- */
  // Use no anúncio: ?tratamento=varizes (ou dor, medidas, pele, intestino, cursos)
  var VERSOES = {
    varizes: {
      titulo: "Tratamento de vasinhos e varizes em Canaã dos Carajás",
      sub: "Avaliação das pernas com a biomédica Dra. Adelaine Montel e tratamento com PEIM integrativo e ozônio para microvasos.",
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
      titulo: "Exames normais, mas você não se sente bem?",
      sub: "Na consulta integrativa, a Dra. Adelaine analisa seus exames com mais detalhe e cuida do intestino, da disposição e da pele em Canaã dos Carajás.",
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
    if (quiz && marcarRadio("interesse", versao)) mostrarPasso(2, false);
    if (formFinal) formFinal.elements.interesse.value = versao;
    var abaDaVersao = document.getElementById("aba-" + versao);
    if (abaDaVersao) selecionarAba(abaDaVersao, false);
  }

  /* Botões que levam ao quiz ---------------------------------------------- */
  document.addEventListener("click", function (e) {
    var gatilho = e.target.closest && e.target.closest("[data-ir-form]");
    if (!gatilho) return;
    var alvo = document.getElementById("agendar");
    if (!alvo) return;
    e.preventDefault();
    var escolha = gatilho.getAttribute("data-interesse");
    if (quiz && escolha && marcarRadio("interesse", escolha)) {
      var erro = erroDoPasso(1);
      if (erro) mostrarErro(erro, "");
      mostrarPasso(2, false);
    }
    alvo.scrollIntoView({ behavior: reduzirMovimento ? "auto" : "smooth", block: "start" });
    setTimeout(function () {
      var foco = passoAtual === TOTAL_PASSOS ? quiz.elements.nome : etapaDo(passoAtual);
      if (foco) foco.focus({ preventScroll: true });
    }, reduzirMovimento ? 0 : 450);
  });

  /* Barra fixa do celular some quando um formulário está na tela ----------- */
  var barra = document.querySelector(".barra-fixa");
  if (barra && "IntersectionObserver" in window) {
    var visiveis = new Set();
    var observador = new IntersectionObserver(function (entradas) {
      entradas.forEach(function (en) {
        if (en.isIntersecting) visiveis.add(en.target); else visiveis.delete(en.target);
      });
      barra.classList.toggle("barra-fixa--oculta", visiveis.size > 0);
    }, { threshold: 0.15 });
    ["agendar"].forEach(function (id) { var el = document.getElementById(id); if (el) observador.observe(el); });
    var cartaoFinal = document.querySelector(".cartao-final");
    if (cartaoFinal) observador.observe(cartaoFinal);
  }

  /* Antes e depois: aparece quando houver fotos em js/config.js ------------- */
  var resultados = Array.isArray(cfg.resultados) ? cfg.resultados.filter(function (r) { return r && r.antes && r.depois; }) : [];
  var secaoResultados = document.getElementById("resultados");
  var listaResultados = document.querySelector("[data-resultados]");
  if (resultados.length && secaoResultados && listaResultados) {
    resultados.forEach(function (r) {
      var li = document.createElement("li");
      li.className = "resultado";
      var fotos = document.createElement("div");
      fotos.className = "resultado__fotos";
      [["Antes", r.antes], ["Depois", r.depois]].forEach(function (par) {
        var fig = document.createElement("figure");
        var img = document.createElement("img");
        img.src = par[1];
        img.alt = par[0] + (r.tratamento ? " do tratamento de " + r.tratamento : "");
        img.loading = "lazy";
        img.decoding = "async";
        var cap = document.createElement("figcaption");
        cap.textContent = par[0];
        fig.appendChild(img);
        fig.appendChild(cap);
        fotos.appendChild(fig);
      });
      li.appendChild(fotos);
      if (r.tratamento || r.legenda) {
        var p = document.createElement("p");
        p.className = "resultado__legenda";
        p.textContent = [r.tratamento, r.legenda].filter(Boolean).join(": ");
        li.appendChild(p);
      }
      listaResultados.appendChild(li);
    });
    secaoResultados.hidden = false;
  }
})();
