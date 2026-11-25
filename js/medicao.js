/* Medição e cookies: carrega no <head>, logo depois do config.js.
   - Modo de consentimento do Google (Consent Mode v2) antes de tudo
   - GTM e Pixel do Meta, se os IDs estiverem no config.js
   - Aviso de cookies com "Aceitar" e "Recusar"; a escolha fica guardada no navegador */
(function () {
  "use strict";
  var w = window, d = document;
  var cfg = w.EMPATIA || {};
  var CHAVE = "empatiaCookies";
  var temGtm = /^GTM-[A-Z0-9]+$/.test(cfg.gtmId || "");
  var temPixel = /^\d{6,20}$/.test(cfg.pixelId || "");
  var modoAviso = cfg.cookies !== "consentimento";

  w.dataLayer = w.dataLayer || [];
  function gtag() { w.dataLayer.push(arguments); }
  w.gtag = w.gtag || gtag;

  var escolha = null;
  try { escolha = localStorage.getItem(CHAVE); } catch (e) {}
  var estado = escolha === "sim" ? "granted" : escolha === "nao" ? "denied" : (modoAviso ? "granted" : "denied");
  function sinais(v) { return { ad_storage: v, ad_user_data: v, ad_personalization: v, analytics_storage: v }; }

  var inicio = sinais(estado);
  inicio.functionality_storage = "granted";
  inicio.security_storage = "granted";
  inicio.wait_for_update = 500;
  gtag("consent", "default", inicio);
  gtag("set", "ads_data_redaction", true);
  gtag("set", "url_passthrough", true);

  var carregou = false;
  function carregar() {
    if (carregou) return;
    carregou = true;
    if (temGtm) {
      w.dataLayer.push({ "gtm.start": Date.now(), event: "gtm.js" });
      var s = d.createElement("script");
      s.async = true;
      s.src = "https://www.googletagmanager.com/gtm.js?id=" + cfg.gtmId;
      d.head.appendChild(s);
    }
    if (temPixel) {
      /* eslint-disable */
      !function (f, b, e, v, n, t, s) { if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); }; if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = "2.0"; n.queue = []; t = b.createElement(e); t.async = !0; t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s); }(w, d, "script", "https://connect.facebook.net/en_US/fbevents.js");
      /* eslint-enable */
      w.fbq("set", "autoConfig", false, cfg.pixelId);
      if (estado !== "granted") w.fbq("consent", "revoke");
      w.fbq("init", cfg.pixelId);
      w.fbq("track", "PageView");
    }
  }
  if (modoAviso ? escolha !== "nao" : escolha === "sim") carregar();

  var ouvintes = [];
  w.LP_MEDICAO = {
    consentiu: function () { return estado === "granted"; },
    pixelDoSite: temPixel,
    aoEscolher: function (fn) { if (typeof fn === "function") ouvintes.push(fn); },
  };

  function aplicar(sim) {
    estado = sim ? "granted" : "denied";
    try { localStorage.setItem(CHAVE, sim ? "sim" : "nao"); } catch (e) {}
    gtag("consent", "update", sinais(estado));
    if (sim) carregar();
    if (temPixel && typeof w.fbq === "function") w.fbq("consent", sim ? "grant" : "revoke");
    w.dataLayer.push({ event: sim ? "cookies_aceitos" : "cookies_recusados" });
    ouvintes.forEach(function (fn) { try { fn(sim); } catch (e) {} });
  }

  function aviso() {
    if (d.querySelector(".cookies")) return;
    var base = (w.EMPATIA_BASE || "/");
    var el = d.createElement("div");
    el.className = "cookies";
    el.setAttribute("role", "region");
    el.setAttribute("aria-label", "Aviso de cookies");
    el.innerHTML = '<p>Usamos <a href="' + base + 'politica-de-privacidade.html#cookies">cookies</a> para medir os anúncios.</p>' +
      '<div class="cookies__acoes"><button type="button" class="cookies__recusar">Recusar</button><button type="button" class="cookies__aceitar">Aceitar</button></div>';
    d.body.appendChild(el);
    d.body.classList.add("cookies-abertos");
    el.addEventListener("click", function (e) {
      var b = e.target.closest && e.target.closest("button");
      if (!b) return;
      aplicar(b.className.indexOf("cookies__aceitar") > -1);
      if (el.parentNode) el.parentNode.removeChild(el);
      d.body.classList.remove("cookies-abertos");
    });
  }

  function pronto(fn) { if (d.readyState === "loading") d.addEventListener("DOMContentLoaded", fn); else fn(); }
  pronto(function () {
    var forcar = /[?&]cookies=1/.test(location.search);
    if ((temGtm || temPixel || forcar) && (escolha === null || forcar)) aviso();
    d.addEventListener("click", function (e) {
      if (e.target.closest && e.target.closest("[data-cookies-abrir]")) { e.preventDefault(); aviso(); }
    });
  });
})();
