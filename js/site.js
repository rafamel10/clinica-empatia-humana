/* Site da Empatia Humana: formulário de lead (nome, WhatsApp, e-mail) que grava na planilha
   e leva direto para o WhatsApp, janela de agendamento, menu, barra fixa, filtros do blog e eventos.
   Eventos no dataLayer (nomes neutros, sem dado de saúde):
   inicio_formulario, lead (lead_id), clique_whatsapp (origem), abriu_formulario (origem),
   rolagem_50, abriu_duvida, cookies_aceitos / cookies_recusados (no medicao.js). */
(function () {
  "use strict";
  var w = window, d = document;
  var cfg = w.EMPATIA || {};
  var NUMERO = String(cfg.whatsapp || "559491182268").replace(/\D/g, "");
  var reduzir = w.matchMedia && w.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var tratamentoPagina = d.body.getAttribute("data-tratamento") || "";

  /* Links antigos dos anúncios (?tratamento=varizes etc.) vão para a página do tratamento, mantendo as UTMs */
  (function () {
    var mapa = { varizes: "tratamentos/vasinhos-e-varizes/", dor: "tratamentos/ozonioterapia/", medidas: "tratamentos/lipo-ozonizada/", pele: "tratamentos/limpeza-de-pele/", intestino: "tratamentos/saude-intestinal/", cursos: "cursos/", integrativa: "tratamentos/consulta-integrativa/", soroterapia: "tratamentos/soroterapia/" };
    var params = new URLSearchParams(location.search);
    var alvo = mapa[String(params.get("tratamento") || "").toLowerCase()];
    if (!alvo || d.body.getAttribute("data-pagina") !== "inicio") return;
    params.delete("tratamento");
    var resto = params.toString();
    location.replace((w.EMPATIA_BASE || "/") + alvo + (resto ? "?" + resto : "") + location.hash);
  })();

  w.dataLayer = w.dataLayer || [];
  function sinal(evento, dados) {
    var base = { event: evento, pagina_tipo: d.body.getAttribute("data-pagina") || "", pagina_tratamento: tratamentoPagina || "geral" };
    if (dados) for (var k in dados) if (Object.prototype.hasOwnProperty.call(dados, k)) base[k] = dados[k];
    w.dataLayer.push(base);
  }

  /* Origem (UTM e clid): último toque na sessão, primeiro toque no aparelho com consentimento */
  var CHAVES = ["utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "fbclid", "gclid", "gbraid", "wbraid"];
  function lerJ(store, chave) { try { return JSON.parse(store.getItem(chave) || "null"); } catch (e) { return null; } }
  function gravarJ(store, chave, valor) { try { store.setItem(chave, JSON.stringify(valor)); } catch (e) {} }
  (function () {
    var params = new URLSearchParams(location.search), atual = {};
    CHAVES.forEach(function (k) { var v = params.get(k); if (v) atual[k] = v.slice(0, 150); });
    if (!Object.keys(atual).length) return;
    atual.pagina = location.pathname;
    atual.em = new Date().toISOString();
    gravarJ(sessionStorage, "lp_ultimo_toque", atual);
    if (!lerJ(sessionStorage, "lp_primeiro_toque")) gravarJ(sessionStorage, "lp_primeiro_toque", atual);
    var med = w.LP_MEDICAO;
    if (med && med.consentiu() && !lerJ(localStorage, "lp_primeiro_toque")) gravarJ(localStorage, "lp_primeiro_toque", atual);
  })();
  function origem() {
    return {
      ultimo: lerJ(sessionStorage, "lp_ultimo_toque") || {},
      primeiro: lerJ(localStorage, "lp_primeiro_toque") || lerJ(sessionStorage, "lp_primeiro_toque") || {},
    };
  }

  function linkWhats(texto) {
    var o = origem().ultimo;
    var ref = [o.utm_source, o.utm_campaign, o.utm_content].filter(Boolean).join("-");
    if (ref) texto += "\n\n(ref: " + ref.slice(0, 60) + ")";
    return "https://wa.me/" + NUMERO + "?text=" + encodeURIComponent(texto);
  }

  /* Menu do celular */
  var menuBotao = d.querySelector(".menu-botao");
  var menu = d.getElementById("menu");
  if (menuBotao && menu) {
    menuBotao.addEventListener("click", function () {
      var aberto = menuBotao.getAttribute("aria-expanded") === "true";
      menuBotao.setAttribute("aria-expanded", String(!aberto));
      menuBotao.textContent = aberto ? "Menu" : "Fechar";
      d.body.classList.toggle("menu-aberto", !aberto);
    });
    menu.addEventListener("click", function (e) {
      if (e.target.closest("a") && menuBotao.getAttribute("aria-expanded") === "true") menuBotao.click();
    });
  }

  /* Janela de agendamento */
  var modal = d.getElementById("modal-agendar");
  var formModal = modal && modal.querySelector("[data-form-lead]");
  var cartaoPagina = d.getElementById("agendar");

  function abrirForm(origemClique, interesse) {
    sinal("abriu_formulario", { origem: origemClique || "botao" });
    // Se a página tem o formulário no topo e ele está perto, rola até ele; senão, abre a janela.
    if (formModal) {
      if (interesse) formModal.setAttribute("data-interesse", interesse);
      if (modal.showModal) {
        modal.showModal();
      } else {
        modal.setAttribute("open", "");
      }
      d.body.classList.add("modal-aberto");
      var nome = formModal.querySelector('input[name="nome"]');
      if (nome && !("ontouchstart" in w)) setTimeout(function () { nome.focus(); }, 50);
      return;
    }
    if (cartaoPagina) cartaoPagina.scrollIntoView({ behavior: reduzir ? "auto" : "smooth", block: "start" });
  }
  function fecharForm() {
    if (!modal) return;
    if (modal.close) modal.close(); else modal.removeAttribute("open");
    d.body.classList.remove("modal-aberto");
  }
  if (modal) {
    modal.addEventListener("click", function (e) {
      if (e.target === modal || (e.target.closest && e.target.closest("[data-fechar-form]"))) fecharForm();
    });
    modal.addEventListener("close", function () { d.body.classList.remove("modal-aberto"); });
  }
  d.addEventListener("click", function (e) {
    var g = e.target.closest && e.target.closest("[data-abrir-form]");
    if (!g) return;
    e.preventDefault();
    abrirForm(g.getAttribute("data-origem"), g.getAttribute("data-interesse"));
  });

  /* Barra fixa do celular: aparece depois da primeira tela e some quando um formulário está visível */
  var barra = d.querySelector("[data-barra-fixa]");
  if (barra && "IntersectionObserver" in w) {
    var visiveis = new Set();
    var heroVisivel = true;
    var atualizar = function () { barra.classList.toggle("barra-fixa--visivel", !heroVisivel && visiveis.size === 0); };
    var obsForm = new IntersectionObserver(function (en) {
      en.forEach(function (x) { if (x.isIntersecting) visiveis.add(x.target); else visiveis.delete(x.target); });
      atualizar();
    }, { threshold: 0.1 });
    d.querySelectorAll("main [data-form-lead]").forEach(function (f) { obsForm.observe(f); });
    var hero = d.querySelector(".hero, .cabeca-pagina, .post__cabeca");
    if (hero) {
      new IntersectionObserver(function (en) { heroVisivel = en[0].isIntersecting; atualizar(); }, { threshold: 0 }).observe(hero);
    } else { heroVisivel = false; atualizar(); }
  }

  /* Formulários */
  var DDDS = "11 12 13 14 15 16 17 18 19 21 22 24 27 28 31 32 33 34 35 37 38 41 42 43 44 45 46 47 48 49 51 53 54 55 61 62 63 64 65 66 67 68 69 71 73 74 75 77 79 81 82 83 84 85 86 87 88 89 91 92 93 94 95 96 97 98 99".split(" ");
  function digitos(v) {
    var x = String(v || "").replace(/\D/g, "");
    if ((x.length === 12 || x.length === 13) && x.indexOf("55") === 0) x = x.slice(2);
    if ((x.length === 11 || x.length === 12) && x[0] === "0") x = x.slice(1);
    return x;
  }
  function telValido(x) {
    if (x.length !== 10 && x.length !== 11) return false;
    if (DDDS.indexOf(x.slice(0, 2)) < 0) return false;
    if (x.length === 11 && x[2] !== "9") return false;
    if (/^(\d)\1+$/.test(x.slice(2))) return false;
    return true;
  }
  function mascara(x) {
    if (x.length <= 2) return x.length ? "(" + x : "";
    var meio = x.length > 10 ? 5 : 4;
    if (x.length <= 2 + meio) return "(" + x.slice(0, 2) + ") " + x.slice(2);
    return "(" + x.slice(0, 2) + ") " + x.slice(2, 2 + meio) + "-" + x.slice(2 + meio, 11);
  }
  var DOMINIOS = { "gmial.com": "gmail.com", "gmal.com": "gmail.com", "gmai.com": "gmail.com", "gmail.co": "gmail.com", "gmail.con": "gmail.com", "gamil.com": "gmail.com", "hotmal.com": "hotmail.com", "hotmail.co": "hotmail.com", "hotmail.con": "hotmail.com", "hotmial.com": "hotmail.com", "outlok.com": "outlook.com", "yahoo.com.b": "yahoo.com.br", "icloud.co": "icloud.com" };
  function emailValido(v) { return /^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i.test(v); }

  function erro(campo, msg) {
    var p = d.getElementById(campo.id + "-erro");
    if (msg) campo.setAttribute("aria-invalid", "true"); else campo.removeAttribute("aria-invalid");
    if (p) { p.textContent = msg || ""; p.hidden = !msg; }
  }

  var enviando = false;
  var comecou = false;

  d.querySelectorAll("[data-form-lead]").forEach(function (form) {
    var nome = form.elements.nome, tel = form.elements.whatsapp, email = form.elements.email;
    var botao = form.querySelector(".form-lead__enviar");
    var opcional = form.querySelector("[data-email-opcional]");
    if (!cfg.emailObrigatorio && opcional) opcional.hidden = false;
    if (cfg.emailObrigatorio) email.required = true;

    form.addEventListener("focusin", function () {
      if (comecou) return;
      comecou = true;
      sinal("inicio_formulario", { origem: form.getAttribute("data-origem") || "" });
    });
    tel.addEventListener("input", function () {
      var x = digitos(tel.value).slice(0, 11);
      var fim = tel.selectionStart === tel.value.length;
      tel.value = mascara(x);
      if (fim) try { tel.setSelectionRange(tel.value.length, tel.value.length); } catch (e) {}
      if (tel.getAttribute("aria-invalid")) erro(tel, "");
    });
    nome.addEventListener("input", function () { if (nome.getAttribute("aria-invalid")) erro(nome, ""); });
    email.addEventListener("input", function () { if (email.getAttribute("aria-invalid")) erro(email, ""); });
    email.addEventListener("blur", function () {
      var v = email.value.trim().toLowerCase();
      var dom = v.split("@")[1];
      if (dom && DOMINIOS[dom]) {
        var sugestao = v.split("@")[0] + "@" + DOMINIOS[dom];
        var p = d.getElementById(email.id + "-erro");
        if (p) {
          p.hidden = false;
          p.innerHTML = "";
          var b = d.createElement("button");
          b.type = "button";
          b.className = "sugestao";
          b.textContent = "Você quis dizer " + sugestao + "?";
          b.addEventListener("click", function () { email.value = sugestao; p.hidden = true; email.focus(); });
          p.appendChild(b);
        }
      }
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (enviando) return;
      var vNome = nome.value.replace(/\s+/g, " ").trim();
      var vTel = digitos(tel.value);
      var vEmail = email.value.trim();
      var primeiro = null;
      if (vNome.length < 2) { erro(nome, "Escreva seu nome para a equipe saber com quem vai falar."); primeiro = nome; } else erro(nome, "");
      if (!telValido(vTel)) { erro(tel, vTel.length < 10 ? "Confira o número: coloque o DDD e o celular, por exemplo (94) 99999-9999." : "Esse número não parece um celular válido. Confira o DDD e os dígitos."); primeiro = primeiro || tel; } else erro(tel, "");
      if (vEmail && !emailValido(vEmail)) { erro(email, "Confira o e-mail, por exemplo maria@gmail.com."); primeiro = primeiro || email; }
      else if (!vEmail && cfg.emailObrigatorio) { erro(email, "Coloque seu e-mail para receber as orientações da clínica."); primeiro = primeiro || email; }
      else erro(email, "");
      if (primeiro) { primeiro.focus(); return; }

      enviando = true;
      var textoBotao = botao.innerHTML;
      botao.disabled = true;
      botao.querySelector("span").textContent = "Abrindo o WhatsApp…";

      var leadId = Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
      var interesse = form.getAttribute("data-interesse") || "";
      var o = origem();
      var dados = {
        lead_id: leadId,
        nome: vNome,
        whatsapp: "55" + vTel,
        email: vEmail,
        interesse: interesse,
        tratamento_pagina: tratamentoPagina,
        formulario: form.getAttribute("data-origem") || "",
        pagina: location.href.split("#")[0].split("?")[0],
        utm_source: o.ultimo.utm_source || "",
        utm_medium: o.ultimo.utm_medium || "",
        utm_campaign: o.ultimo.utm_campaign || "",
        utm_content: o.ultimo.utm_content || "",
        utm_term: o.ultimo.utm_term || "",
        clique: o.ultimo.fbclid ? "fbclid" : o.ultimo.gclid ? "gclid" : o.ultimo.gbraid ? "gbraid" : o.ultimo.wbraid ? "wbraid" : "",
        primeira_origem: [o.primeiro.utm_source, o.primeiro.utm_campaign].filter(Boolean).join(" / "),
        origem: d.referrer || "",
        site: form.elements.site ? form.elements.site.value : "",
      };

      // Planilha: sem bloquear a pessoa (keepalive deixa o envio terminar mesmo saindo da página)
      if (cfg.planilhaUrl) {
        try {
          var corpo = new URLSearchParams(dados);
          if (navigator.sendBeacon) navigator.sendBeacon(cfg.planilhaUrl, corpo);
          else fetch(cfg.planilhaUrl, { method: "POST", mode: "no-cors", keepalive: true, body: corpo }).catch(function () {});
        } catch (err) {}
      } else if (w.console) {
        console.warn("Empatia Humana: planilhaUrl vazio em js/config.js, o lead não foi gravado.");
      }

      // Eventos (sem nome, telefone ou e-mail nas ferramentas de anúncio)
      sinal("lead", { lead_id: leadId, origem: dados.formulario });
      if (typeof w.fbq === "function") w.fbq("track", "Lead", {}, { eventID: leadId });

      var primeiroNome = vNome.split(" ")[0];
      var msg = "Olá! Meu nome é " + primeiroNome + ". Vim pelo site da Empatia Humana e quero saber valores e horários" + (interesse ? " para " + interesse : " dos tratamentos") + ".";
      if (interesse === "cursos para profissionais") msg = "Olá! Meu nome é " + primeiroNome + ". Vim pelo site da Empatia Humana e quero saber das próximas turmas dos cursos.";
      var destino = linkWhats(msg);
      sinal("clique_whatsapp", { origem: "formulario" });

      // Tela de "abrindo o WhatsApp" com o link, caso o aplicativo não abra sozinho (computador, navegador interno)
      var ok = form.querySelector(".form-lead__ok");
      if (ok) {
        var a = ok.querySelector("[data-wa-link]");
        if (a) a.href = destino;
        ok.hidden = false;
        form.classList.add("form-lead--enviado");
      }

      // Dá um instante para o Pixel e o GTM mandarem o evento antes de sair
      setTimeout(function () {
        enviando = false;
        botao.disabled = false;
        botao.innerHTML = textoBotao;
        location.href = destino;
      }, 450);
    });
  });

  /* Links diretos de WhatsApp (se houver) */
  d.addEventListener("click", function (e) {
    var a = e.target.closest && e.target.closest('a[href^="https://wa.me/"]');
    if (!a) return;
    sinal("clique_whatsapp", { origem: a.getAttribute("data-origem") || "link" });
    if (typeof w.fbq === "function") w.fbq("track", "Contact");
  });

  /* FAQ: primeira pergunta aberta na visita */
  var abriuDuvida = false;
  d.querySelectorAll("details").forEach(function (det) {
    det.addEventListener("toggle", function () {
      if (det.open && !abriuDuvida) { abriuDuvida = true; sinal("abriu_duvida"); }
    });
  });

  /* Rolagem de 50% */
  var rolou = false;
  var alvo50 = d.createElement("div");
  alvo50.setAttribute("aria-hidden", "true");
  alvo50.style.cssText = "position:absolute;left:0;width:1px;height:1px;pointer-events:none";
  if ("IntersectionObserver" in w) {
    d.body.appendChild(alvo50);
    var posicionar = function () { alvo50.style.top = Math.round(d.documentElement.scrollHeight / 2) + "px"; };
    posicionar();
    w.addEventListener("load", posicionar);
    new IntersectionObserver(function (en) {
      if (en[0].isIntersecting && !rolou) { rolou = true; sinal("rolagem_50"); }
    }).observe(alvo50);
  }

  /* Filtros do blog */
  var filtros = d.querySelectorAll(".filtro");
  if (filtros.length) {
    filtros.forEach(function (b) {
      b.addEventListener("click", function () {
        var cat = b.getAttribute("data-filtro");
        filtros.forEach(function (x) { x.setAttribute("aria-pressed", String(x === b)); });
        d.querySelectorAll(".cards-post--blog .card-post").forEach(function (c) {
          c.hidden = !!cat && c.getAttribute("data-categoria") !== cat;
        });
      });
    });
  }
})();
