# -*- coding: utf-8 -*-
"""Gera o site estático da Empatia Humana.

Uso:  python scripts/gerar.py
Lê os textos de scripts/dados.py e os posts de conteudo/blog/*.md, e escreve os HTML,
sitemap.xml, robots.txt, llms.txt e blog/feed.xml na raiz do repositório.
Nunca edite os HTML gerados à mão: edite dados.py ou os .md e rode de novo.
"""
import html
import json
import os
import re
import sys
from datetime import date

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import dados  # noqa: E402

S = dados.SITE
DRA = dados.DRA
BASE = S["base"]
URL = S["url"].rstrip("/")
VERSAO = "4"  # aumente a cada publicação que mudar CSS ou JS
HOJE = S["data_atualizacao"]
TRAT = {t["slug"]: t for t in dados.TRATAMENTOS}


def esc(t):
    return html.escape(str(t), quote=True)


def link(caminho=""):
    """Caminho interno com a base do site (funciona no GitHub Pages em subpasta)."""
    return BASE + caminho.lstrip("/")


def absoluto(caminho=""):
    return URL + "/" + caminho.lstrip("/")


def wa(texto):
    from urllib.parse import quote
    return "https://wa.me/" + S["whatsapp"] + "?text=" + quote(texto)


# Markdown simples (o suficiente para os posts) --------------------------------------

def inline(t):
    t = esc(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)

    def _lk(m):
        txt, href = m.group(1), html.unescape(m.group(2))
        if href.startswith("/"):
            return '<a href="%s">%s</a>' % (esc(link(href)), txt)
        return '<a href="%s" target="_blank" rel="noopener">%s</a>' % (esc(href), txt)

    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", _lk, t)
    return t


def slugify(t):
    import unicodedata
    t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[:60]


def md_para_html(md):
    """Devolve (html, faq, toc). O FAQ é a seção '## Perguntas frequentes' com perguntas em ###."""
    linhas = md.replace("\r\n", "\n").split("\n")
    out, faq, toc = [], [], []
    para, lista, tipo_lista = [], [], None
    em_faq, faq_q, faq_r = False, None, []

    def fecha_para():
        nonlocal para
        if para:
            txt = " ".join(x.strip() for x in para)
            if em_faq and faq_q is not None:
                faq_r.append(txt)
            else:
                out.append("<p>%s</p>" % inline(txt))
            para = []

    def fecha_lista():
        nonlocal lista, tipo_lista
        if lista:
            itens = "".join("<li>%s</li>" % inline(i) for i in lista)
            if em_faq and faq_q is not None:
                faq_r.append(" ".join(lista))
            else:
                out.append("<%s>%s</%s>" % (tipo_lista, itens, tipo_lista))
            lista, tipo_lista = [], None

    def fecha_faq():
        nonlocal faq_q, faq_r
        if faq_q is not None:
            faq.append((faq_q, " ".join(faq_r)))
        faq_q, faq_r = None, []

    for ln in linhas:
        s = ln.rstrip()
        if not s.strip():
            fecha_para(); fecha_lista(); continue
        m = re.match(r"^(#{2,3})\s+(.*)$", s)
        if m:
            fecha_para(); fecha_lista()
            nivel, txt = len(m.group(1)), m.group(2).strip()
            if nivel == 2:
                fecha_faq()
                em_faq = txt.lower().startswith("perguntas frequentes")
                if not em_faq:
                    ident = slugify(txt)
                    toc.append((ident, txt))
                    out.append('<h2 id="%s">%s</h2>' % (ident, inline(txt)))
            else:
                if em_faq:
                    fecha_faq(); faq_q = txt
                else:
                    out.append("<h3>%s</h3>" % inline(txt))
            continue
        m = re.match(r"^\s*(-|\d+\.)\s+(.*)$", s)
        if m:
            fecha_para()
            t = "ol" if m.group(1)[0].isdigit() else "ul"
            if tipo_lista and tipo_lista != t:
                fecha_lista()
            tipo_lista = t
            lista.append(m.group(2).strip())
            continue
        if lista and ln.startswith("  "):
            lista[-1] += " " + s.strip(); continue
        fecha_lista()
        para.append(s)
    fecha_para(); fecha_lista(); fecha_faq()
    return "\n".join(out), faq, toc


def ler_posts():
    pasta = os.path.join(RAIZ, "conteudo", "blog")
    posts = []
    if not os.path.isdir(pasta):
        return posts
    for nome in sorted(os.listdir(pasta)):
        if not nome.endswith(".md"):
            continue
        bruto = open(os.path.join(pasta, nome), encoding="utf-8").read()
        m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", bruto, re.S)
        if not m:
            print("  aviso: sem cabeçalho em", nome); continue
        meta = {}
        for ln in m.group(1).split("\n"):
            if ":" in ln:
                k, v = ln.split(":", 1)
                meta[k.strip()] = v.strip()
        meta["slug"] = meta.get("slug") or nome[:-3]
        corpo, faq, toc = md_para_html(m.group(2))
        meta["html"], meta["faq"], meta["toc"] = corpo, faq, toc
        meta["palavras"] = len(re.sub(r"<[^>]+>", " ", corpo).split())
        if not meta.get("tempo_leitura"):
            meta["tempo_leitura"] = str(max(2, round(meta["palavras"] / 200)))
        if meta.get("rascunho", "").lower() in ("sim", "true", "1"):
            continue
        posts.append(meta)
    posts.sort(key=lambda p: (p.get("data", ""), p["slug"]), reverse=True)
    return posts


POSTS = ler_posts()
POST = {p["slug"]: p for p in POSTS}


def data_br(iso):
    meses = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"]
    try:
        a, m, d = iso.split("-")
        return "%d de %s de %s" % (int(d), meses[int(m) - 1], a)
    except Exception:
        return iso


# Ícones (traço fino, SVG inline) ----------------------------------------------------

ICONES = {
    "perna": '<path d="M9 3c0 5 1 8 1 11s-2 4-2 7h5c0-2 1-3 1-6s-1-6-1-12"/><path d="M10.5 9.5c.8.6 1.4 1.6 1.2 2.6M11 15c.6.4 1 1 .9 1.8"/>',
    "ozonio": '<circle cx="8" cy="9" r="4"/><circle cx="16" cy="9" r="3"/><circle cx="12" cy="16" r="3.5"/>',
    "cintura": '<path d="M7 3c1 3 1 5 0 9s-1 6 1 9M17 3c-1 3-1 5 0 9s1 6-1 9"/><path d="M8.5 12h7"/>',
    "lupa": '<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5 5M8 10.5h5M10.5 8v5"/>',
    "intestino": '<path d="M6 5h10a3 3 0 0 1 0 6H9a3 3 0 0 0 0 6h9"/><path d="M6 5v3M18 17v3"/>',
    "rosto": '<path d="M12 3c-4 0-7 3-7 8 0 4 3 9 7 9s7-5 7-9c0-5-3-8-7-8z"/><path d="M9 11h.01M15 11h.01M10 15.5c1 .8 3 .8 4 0"/>',
    "gota": '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/><path d="M9.5 14.5a2.5 2.5 0 0 0 2.5 2.5"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "estrela": '<path d="M12 3.5l2.6 5.5 6 .7-4.4 4.1 1.2 6-5.4-3-5.4 3 1.2-6L3.4 9.7l6-.7z"/>',
    "seta": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "local": '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "relogio": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "escudo": '<path d="M12 3l7 3v5c0 5-3.5 8.5-7 10-3.5-1.5-7-5-7-10V6z"/><path d="M9 12l2 2 4-4"/>',
    "folha": '<path d="M5 19c0-8 5-13 14-14-1 9-6 14-14 14z"/><path d="M5 19l7-7"/>',
}


def icone(nome, classe="icone"):
    return '<svg class="%s" viewBox="0 0 24 24" aria-hidden="true" focusable="false">%s</svg>' % (classe, ICONES.get(nome, ""))


SVG_WHATS = '<svg class="icone-whats" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2c-1.5 0-3-.4-4.3-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.4.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5c-.2 0-.4.1-.7.3-.2.3-.9.9-.9 2.1s.9 2.4 1 2.6c.1.2 1.8 2.8 4.4 3.9 1.6.7 2.3.8 3.1.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.2-.3-.2-.6-.4Z"/></svg>'
SVG_INSTA = '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.4" cy="6.6" r="1.1" fill="currentColor" stroke="none"/></svg>'
SVG_FACE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13.5 22v-8.2h2.8l.4-3.2h-3.2V8.6c0-.9.3-1.6 1.6-1.6h1.7V4.1c-.3 0-1.3-.1-2.5-.1-2.5 0-4.2 1.5-4.2 4.3v2.3H7.3v3.2h2.8V22h3.4Z"/></svg>'


def foto(nome, alt, largura, altura, classe="", lazy=True, sizes="100vw", prioridade=False):
    """<img> em webp (gerado por scripts/imagens.py)."""
    attrs = 'src="%s" width="%d" height="%d" alt="%s"' % (link("assets/img/%s.webp" % nome), largura, altura, esc(alt))
    if classe:
        attrs += ' class="%s"' % classe
    if prioridade:
        attrs += ' fetchpriority="high" decoding="async"'
    elif lazy:
        attrs += ' loading="lazy" decoding="async"'
    return "<img %s>" % attrs


FOTOS = {  # tamanho real dos .webp
    "adelaine-vertical": (900, 1333), "adelaine-avatar": (160, 160), "adelaine-vertical-540": (540, 800), "adelaine-retrato": (900, 900),
    "adelaine-consultorio": (337, 385), "avaliacao-pernas": (512, 380), "clinica-emblema": (512, 285),
    "recepcao": (660, 780), "fachada": (640, 490),
}


def foto_nome(nome, alt, classe="", **kw):
    w, h = FOTOS[nome]
    return foto(nome, alt, w, h, classe, **kw)


# Dados estruturados ----------------------------------------------------------------

def schema_clinica():
    d = {
        "@type": ["MedicalClinic", "HealthAndBeautyBusiness"],
        "@id": absoluto("#clinica"),
        "name": S["nome_completo"],
        "alternateName": ["Empatia Humana", "Clínica Empatia Humana"],
        "description": "Clínica de estética integrativa e ozonioterapia em Canaã dos Carajás (PA): vasinhos e varizes (PEIM), ozonioterapia para dor, lipo ozonizada, saúde intestinal, limpeza de pele e soroterapia.",
        "url": absoluto(),
        "logo": absoluto("assets/img/logo-empatia-humana.jpg"),
        "image": [absoluto("assets/img/fachada.jpg"), absoluto("assets/img/recepcao.jpg"), absoluto("assets/img/adelaine-retrato.jpg")],
        "telephone": "+55 94 99118-2268",
        "priceRange": "$$",
        "address": {"@type": "PostalAddress", "streetAddress": S["endereco"], "addressLocality": S["cidade"], "addressRegion": S["uf"], "addressCountry": "BR"},
        "geo": {"@type": "GeoCoordinates", "latitude": S["geo"][0], "longitude": S["geo"][1]},
        "hasMap": S["maps_cid"],
        "areaServed": [{"@type": "City", "name": c} for c in S["regiao"]],
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "08:00", "closes": "12:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"], "opens": "14:00", "closes": "18:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": "Saturday", "opens": "08:00", "closes": "12:00"},
        ],
        "founder": {"@id": absoluto("dra-adelaine-montel/#pessoa")},
        "employee": {"@id": absoluto("dra-adelaine-montel/#pessoa")},
        "sameAs": [S["instagram_clinica"], S["facebook"], S["maps_cid"]],
        "availableService": [{"@id": absoluto("tratamentos/%s/#servico" % t["slug"])} for t in dados.TRATAMENTOS],
    }
    return d


def schema_pessoa():
    return {
        "@type": "Person",
        "@id": absoluto("dra-adelaine-montel/#pessoa"),
        "name": DRA["nome_completo"],
        "alternateName": [DRA["nome"], "Dra. Adelaine Barros Montel", "Biomédica Adelaine"],
        "jobTitle": DRA["cargo"],
        "description": "Biomédica esteta e ozonioterapeuta, responsável técnica da Clínica Empatia Humana em Canaã dos Carajás (PA), com inscrição nº 1437 no CRBM 4ª Região desde 2011.",
        "url": absoluto("dra-adelaine-montel/"),
        "image": absoluto("assets/img/adelaine-retrato.jpg"),
        "worksFor": {"@id": absoluto("#clinica")},
        "knowsAbout": ["Ozonioterapia", "Estética integrativa", "PEIM", "Análises clínicas", "Nutrição ortomolecular", "Saúde intestinal", "Dor crônica"],
        "alumniOf": [{"@type": "CollegeOrUniversity", "name": "PUC Goiás"}],
        "identifier": [{"@type": "PropertyValue", "propertyID": "CRBM 4ª Região", "value": "1437"}, {"@type": "PropertyValue", "propertyID": "CRBM 3ª Região", "value": "18758"}],
        "hasCredential": [{"@type": "EducationalOccupationalCredential", "credentialCategory": "Registro profissional", "name": "Biomédica, CRBM 4ª Região nº 1437", "recognizedBy": {"@type": "Organization", "name": "Conselho Regional de Biomedicina 4ª Região"}},
                          {"@type": "EducationalOccupationalCredential", "credentialCategory": "Registro profissional", "name": "Biomédica, CRBM 3ª Região nº 18758", "recognizedBy": {"@type": "Organization", "name": "Conselho Regional de Biomedicina 3ª Região"}}]
        + [{"@type": "EducationalOccupationalCredential", "credentialCategory": "Habilitação", "name": h, "recognizedBy": {"@type": "Organization", "name": "Conselho Regional de Biomedicina 4ª Região"}} for h in DRA["habilitacoes"]],
        "sameAs": [S["instagram_dra"]],
    }


def schema_site():
    return {"@type": "WebSite", "@id": absoluto("#site"), "url": absoluto(), "name": S["nome"], "inLanguage": "pt-BR", "publisher": {"@id": absoluto("#clinica")}}


def schema_faq(faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}


def schema_migalhas(itens):
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": absoluto(c)} for i, (n, c) in enumerate(itens)]}


def jsonld(grafo):
    return '<script type="application/ld+json">%s</script>' % json.dumps({"@context": "https://schema.org", "@graph": grafo}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


# Partes comuns ---------------------------------------------------------------------

def head(titulo, descricao, caminho, grafo, imagem="assets/img/og-empatia.jpg", tipo="website", robots="index, follow", extra=""):
    canonical = absoluto(caminho)
    if S.get("google_verificacao"):
        extra += '\n  <meta name="google-site-verification" content="%s">' % esc(S["google_verificacao"])
    if S.get("bing_verificacao"):
        extra += '\n  <meta name="msvalidate.01" content="%s">' % esc(S["bing_verificacao"])
    return """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{t}</title>
  <meta name="description" content="{d}">
  <meta name="robots" content="{r}">
  {canon}
  <meta name="theme-color" content="#1f3a2e">
  <meta property="og:type" content="{tipo}">
  <meta property="og:locale" content="pt_BR">
  <meta property="og:site_name" content="Empatia Humana">
  <meta property="og:title" content="{t}">
  <meta property="og:description" content="{d}">
  <meta property="og:url" content="{c}">
  <meta property="og:image" content="{img}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Clínica Empatia Humana em Canaã dos Carajás, com a Dra. Adelaine Montel">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" type="image/png" href="{base}assets/img/favicon.png">
  <link rel="apple-touch-icon" href="{base}assets/img/apple-touch-icon.png">
  <link rel="alternate" type="application/rss+xml" title="Blog da Dra. Adelaine Montel" href="{base}blog/feed.xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Albert+Sans:wght@400..700&family=Newsreader:ital,wght@0,400..600;1,400..500&display=swap">
  <link rel="stylesheet" href="{base}css/site.css?v={v}">
  <script>document.documentElement.classList.add("js");window.EMPATIA_BASE="{base}";</script>
  <script src="{base}js/config.js?v={v}"></script>
  <script src="{base}js/medicao.js?v={v}"></script>
  {ld}{extra}
</head>""".format(canon=("" if robots.startswith("noindex") else '<link rel="canonical" href="%s">' % esc(canonical)), t=esc(titulo), d=esc(descricao), r=robots, c=esc(canonical), tipo=tipo, img=esc(absoluto(imagem)), base=BASE, v=VERSAO, ld=jsonld(grafo), extra=extra)


def cabecalho(atual=""):
    itens_trat = "".join('<li><a href="%s">%s %s</a></li>' % (link("tratamentos/%s/" % t["slug"]), icone(t["icone"], "icone icone--menu"), esc(t["menu"])) for t in dados.TRATAMENTOS)

    def ativo(nome):
        return ' aria-current="page"' if atual == nome else ""

    return """<a class="pular" href="#conteudo">Pular para o conteúdo</a>
<header class="topo">
  <div class="topo__barra">
    <a class="marca" href="{home}" aria-label="Empatia Humana, página inicial">
      <img src="{base}assets/img/logo-empatia-humana.webp" width="44" height="44" alt="">
      <span class="marca__texto"><span class="marca__nome">Empatia Humana</span><span class="marca__sub">Estética integrativa em Canaã</span></span>
    </a>
    <button class="menu-botao" type="button" aria-expanded="false" aria-controls="menu">Menu</button>
    <nav class="menu" id="menu" aria-label="Menu principal">
      <ul class="menu__lista">
        <li class="menu__grupo">
          <a href="{trats}"{a_t}>Tratamentos</a>
          <ul class="menu__sub">{itens}</ul>
        </li>
        <li><a href="{sobre}"{a_s}>Dra. Adelaine</a></li>
        <li><a href="{home}#depoimentos">Depoimentos</a></li>
        <li><a href="{blog}"{a_b}>Blog</a></li>
        <li><a href="{cursos}"{a_c}>Cursos</a></li>
        <li><a href="{home}#contato">Contato</a></li>
      </ul>
      <a class="botao botao--ouro menu__cta" href="#agendar" data-abrir-form data-origem="menu">Valores e horários</a>
    </nav>
  </div>
</header>""".format(home=link(), base=BASE, trats=link("tratamentos/"), sobre=link("dra-adelaine-montel/"), blog=link("blog/"), cursos=link("cursos/"), itens=itens_trat, a_t=ativo("tratamentos"), a_s=ativo("sobre"), a_b=ativo("blog"), a_c=ativo("cursos"))


def formulario(prefixo, interesse="", titulo="Valores e horários pelo WhatsApp", texto="", botao="Quero saber valores e horários", origem="pagina", titulo_tag="h2"):
    if not texto:
        texto = "Você vai direto para o WhatsApp da clínica, com a mensagem pronta%s." % ((" sobre " + esc(interesse)) if interesse else "")
    return """<form class="form-lead" data-form-lead data-origem="{o}" data-interesse="{i}" novalidate>
  <{tt} class="form-lead__titulo">{t}</{tt}>
  <p class="form-lead__texto">{tx}</p>
  <div class="campo">
    <label for="{p}-nome">Seu nome</label>
    <input id="{p}-nome" name="nome" type="text" autocomplete="name" autocapitalize="words" enterkeyhint="next" maxlength="80" required aria-describedby="{p}-nome-erro" data-clarity-mask="true">
    <p class="campo__erro" id="{p}-nome-erro" aria-live="polite" hidden></p>
  </div>
  <div class="campo">
    <label for="{p}-whatsapp">WhatsApp com DDD</label>
    <input id="{p}-whatsapp" name="whatsapp" type="tel" inputmode="tel" autocomplete="tel-national" enterkeyhint="next" placeholder="(94) 99999-9999" maxlength="16" required aria-describedby="{p}-whatsapp-erro" data-clarity-mask="true">
    <p class="campo__erro" id="{p}-whatsapp-erro" aria-live="polite" hidden></p>
  </div>
  <div class="campo">
    <label for="{p}-email">E-mail <span class="campo__opcional" data-email-opcional hidden>(opcional)</span></label>
    <input id="{p}-email" name="email" type="email" inputmode="email" autocomplete="email" enterkeyhint="send" placeholder="voce@email.com" maxlength="120" aria-describedby="{p}-email-erro" data-clarity-mask="true">
    <p class="campo__erro" id="{p}-email-erro" aria-live="polite" hidden></p>
  </div>
  <div class="campo-isca" aria-hidden="true"><label for="{p}-site">Não preencha</label><input id="{p}-site" name="site" type="text" tabindex="-1" autocomplete="off"></div>
  <button class="botao botao--ouro botao--cheio form-lead__enviar" type="submit">{svg}<span>{b}</span></button>
  <p class="form-lead__prova"><span class="estrelas" aria-hidden="true">★★★★★</span> <strong>5,0 no Google</strong> · 27 avaliações</p>
  <p class="form-lead__nota">Leva 20 segundos e não tem compromisso. Seus dados não são vendidos nem emprestados. <a href="{priv}">Privacidade</a>.</p>
  <div class="form-lead__ok" role="status" hidden><p class="form-lead__ok-titulo">Abrindo o WhatsApp…</p><p>Não abriu? <a href="#" data-wa-link target="_blank" rel="noopener">Abrir a conversa com a clínica</a></p></div>
</form>""".format(p=prefixo, i=esc(interesse), o=origem, t=titulo, tt=titulo_tag, tx=texto, b=botao, svg=SVG_WHATS, priv=link("politica-de-privacidade.html"))


def selo_google(classe=""):
    return '<a class="selo-google %s" href="%s" target="_blank" rel="noopener"><span class="estrelas" aria-hidden="true">★★★★★</span><span><strong>%s no Google</strong> · %d avaliações</span></a>' % (classe, esc(S["maps"]), S["nota_google"], S["avaliacoes_google"])


def rodape():
    trats = "".join('<li><a href="%s">%s</a></li>' % (link("tratamentos/%s/" % t["slug"]), esc(t["menu"])) for t in dados.TRATAMENTOS)
    posts = "".join('<li><a href="%s">%s</a></li>' % (link("blog/%s/" % p["slug"]), esc(p["titulo"])) for p in POSTS[:4])
    horas = "".join("<li><span>%s</span> %s</li>" % (esc(a), esc(b)) for a, b in S["horarios"])
    return """<footer class="rodape">
  <div class="largura rodape__grade">
    <div class="rodape__marca">
      <img src="{base}assets/img/logo-empatia-branca.png" width="372" height="235" alt="Empatia Humana, conceito em estética integrativa" loading="lazy">
      <p>Clínica de estética integrativa e ozonioterapia em Canaã dos Carajás (PA).</p>
      <ul class="redes">
        <li><a class="rede" href="{insta}" target="_blank" rel="noopener">{si}<span>@clinicaempatiahumana</span></a></li>
        <li><a class="rede" href="{insta_d}" target="_blank" rel="noopener">{si}<span>@biomedicaadelaine</span></a></li>
        <li><a class="rede" href="{face}" target="_blank" rel="noopener">{sf}<span>Facebook</span></a></li>
      </ul>
    </div>
    <div>
      <p class="rodape__titulo">Tratamentos</p>
      <ul class="rodape__links">{trats}</ul>
    </div>
    <div>
      <p class="rodape__titulo">Do blog</p>
      <ul class="rodape__links">{posts}<li><a href="{blog}">Todos os posts</a></li></ul>
    </div>
    <div>
      <p class="rodape__titulo">Onde estamos</p>
      <address>{end}<br>{bairro}, {cidade} ({uf})</address>
      <ul class="rodape__horas">{horas}</ul>
      <p><a href="{parau}">Pacientes de Parauapebas</a></p>
      <p><a href="#agendar" data-abrir-form data-origem="rodape">Agendar avaliação</a></p>
    </div>
  </div>
  <div class="largura rodape__legal">
    <p><strong>{dra}</strong>, {cargo_min}, inscrição nº 1437 no CRBM 4ª Região. Responsável técnica.</p>
    <p>{razao}, CNPJ {cnpj}. Os resultados variam de pessoa para pessoa e as informações deste site não substituem uma avaliação profissional.</p>
    <p><a href="{priv}">Política de privacidade</a> · <a href="#" data-cookies-abrir>Preferências de cookies</a></p>
  </div>
</footer>""".format(base=BASE, insta=S["instagram_clinica"], insta_d=S["instagram_dra"], face=S["facebook"], si=SVG_INSTA, sf=SVG_FACE, trats=trats, posts=posts, blog=link("blog/"), end=esc(S["endereco"]), bairro=S["bairro"], cidade=S["cidade"], uf=S["uf"], horas=horas, dra=DRA["nome_completo"], cargo_min="biomédica esteta e ozonioterapeuta", razao=S["razao"], cnpj=S["cnpj"], priv=link("politica-de-privacidade.html"), parau=link("pacientes-de-parauapebas/"))


def modal_e_barra(interesse="", texto_barra="Ver valores e horários"):
    return """<dialog class="modal" id="modal-agendar" aria-labelledby="modal-titulo">
  <div class="modal__caixa">
    <button class="modal__fechar" type="button" data-fechar-form aria-label="Fechar">×</button>
    <div class="modal__topo">
      <img src="{base}assets/img/adelaine-avatar.webp" width="64" height="64" alt="" loading="lazy">
      <p>Atendimento com a <strong>Dra. Adelaine Montel</strong><br><span class="estrelas" aria-hidden="true">★★★★★</span> 5,0 no Google</p>
    </div>
    {form}
  </div>
</dialog>
<div class="barra-fixa" data-barra-fixa>
  <a class="botao botao--ouro botao--cheio" href="#agendar" data-abrir-form data-origem="barra_fixa">{svg}<span>{tb}</span></a>
</div>
<script src="{base}js/site.js?v={v}" defer></script>""".format(base=BASE, form=formulario("modal", interesse, origem="modal", titulo_tag="h2").replace('class="form-lead__titulo"', 'class="form-lead__titulo" id="modal-titulo"'), svg=SVG_WHATS, tb=texto_barra, v=VERSAO)


def pagina(head_html, corpo, atual="", interesse="", data_pagina="", data_trat=""):
    return "%s\n<body data-pagina=\"%s\" data-tratamento=\"%s\">\n%s\n<main id=\"conteudo\">\n%s\n</main>\n%s\n%s\n</body>\n</html>\n" % (
        head_html, data_pagina, data_trat, cabecalho(atual), corpo, rodape(), modal_e_barra(interesse))


def migalhas_html(itens):
    partes = []
    for i, (nome, caminho) in enumerate(itens):
        if i == len(itens) - 1:
            partes.append('<li aria-current="page">%s</li>' % esc(nome))
        else:
            partes.append('<li><a href="%s">%s</a></li>' % (link(caminho), esc(nome)))
    return '<nav class="migalhas" aria-label="Você está em"><ol>%s</ol></nav>' % "".join(partes)


def bloco_avaliacoes(qtd=8, titulo_tag="h3", primeiro=None):
    cores = ["", " avatar--b", " avatar--c"]
    lista = list(dados.GOOGLE)
    if primeiro:
        lista.sort(key=lambda x: (x[0] not in primeiro, primeiro.index(x[0]) if x[0] in primeiro else 0))
    itens = "".join(
        '<li class="avaliacao"><div class="avaliacao__pessoa"><span class="avatar%s" aria-hidden="true">%s</span><span><strong>%s</strong><small>Avaliação no Google</small></span></div><p class="estrelas" aria-label="5 de 5 estrelas">★★★★★</p><p>%s</p></li>'
        % (cores[i % 3], esc(n[0]), esc(n), esc(t)) for i, (n, t) in enumerate(lista[:qtd]))
    return """<div class="google">
  <div class="google__cabeca"><{tt}>Nota {nota} no Google</{tt}><p><span class="estrelas" aria-hidden="true">★★★★★</span> {n} avaliações, todas com 5 estrelas</p></div>
  <ul class="avaliacoes carrossel">{itens}</ul>
  <p class="google__link"><a class="link-acao" href="{maps}" target="_blank" rel="noopener">Ver todas as avaliações no Google</a></p>
</div>""".format(tt=titulo_tag, nota=S["nota_google"], n=S["avaliacoes_google"], itens=itens, maps=esc(S["maps"]))


def bloco_whats(lista):
    itens = "".join(
        '<li class="conversa"><p class="conversa__titulo">"%s"</p><div class="conversa__tela"><p class="balao">%s%s</p></div><p class="conversa__nome">%s</p></li>'
        % (esc(w["titulo"]), esc(w["texto"]), ("<time>%s</time>" % w["hora"]) if w["hora"] else "", esc(w["quem"])) for w in lista)
    return '<ul class="conversas carrossel">%s</ul>' % itens


def bloco_video():
    v = dados.DEPOIMENTO_VIDEO
    return """<figure class="relato-video">
  <p class="relato-video__selo">Depoimento em vídeo</p>
  <blockquote><p>"{t}"</p></blockquote>
  <figcaption><span>{q}</span><a class="link-acao link-acao--claro" href="{l}" target="_blank" rel="noopener">Assistir no Instagram</a></figcaption>
</figure>""".format(t=esc(v["texto"]), q=esc(v["quem"]), l=esc(v["link"]))


def faq_html(faq, abrir_primeira=False):
    return '<div class="perguntas">%s</div>' % "".join(
        '<details%s><summary>%s</summary><p>%s</p></details>' % (" open" if (abrir_primeira and i == 0) else "", esc(q), inline(a)) for i, (q, a) in enumerate(faq))


def card_post(p, tag="h3"):
    return """<li class="card-post">
  <a href="{h}">
    <span class="card-post__cat">{c}</span>
    <{tg} class="card-post__titulo">{t}</{tg}>
    <span class="card-post__resumo">{r}</span>
    <span class="card-post__meta">{d} · {tl} min de leitura</span>
  </a>
</li>""".format(h=link("blog/%s/" % p["slug"]), c=esc(p.get("categoria", "Blog")), t=esc(p["titulo"]), r=esc(p.get("resumo", ""))[:170] + ("…" if len(p.get("resumo", "")) > 170 else ""), d=data_br(p.get("data", "")), tl=p["tempo_leitura"], tg=tag)


def card_cta():
    return """<li class="card-trat card-trat--cta">
  <a href="#agendar" data-abrir-form data-origem="card_tratamentos">
    {ic}
    <h3>Não sabe por onde começar?</h3>
    <p>Conte o que você sente. A Dra. Adelaine indica o tratamento certo na avaliação.</p>
    <span class="card-trat__mais">Falar com a clínica {seta}</span>
  </a>
</li>""".format(ic=icone("folha", "icone icone--card"), seta=icone("seta", "icone icone--seta"))


def cta_faixa(titulo, texto, interesse="", origem="faixa", botao="Quero saber valores e horários"):
    return """<section class="faixa-cta" aria-label="Agendar avaliação">
  <div class="largura faixa-cta__grade">
    <div><p class="faixa-cta__titulo">{t}</p><p>{x}</p></div>
    <a class="botao botao--ouro" href="#agendar" data-abrir-form data-origem="{o}" data-interesse="{i}">{svg}<span>{b}</span></a>
  </div>
</section>""".format(t=titulo, x=texto, o=origem, i=esc(interesse), svg=SVG_WHATS, b=botao)


# Páginas ---------------------------------------------------------------------------

def pagina_home():
    trats = "".join("""<li class="card-trat">
  <a href="{h}">
    {ic}
    <h3>{n}</h3>
    <p>{c}</p>
    <span class="card-trat__mais">Conhecer o tratamento {seta}</span>
  </a>
</li>""".format(h=link("tratamentos/%s/" % t["slug"]), ic=icone(t["icone"], "icone icone--card"), n=esc(t["nome"]), c=esc(t["card"]), seta=icone("seta", "icone icone--seta")) for t in dados.TRATAMENTOS)
    trats += card_cta()
    sintomas = "".join('<li><a href="%s">%s</a></li>' % (link("tratamentos/%s/" % s), esc(n)) for n, s in dados.SINTOMAS)
    posts = "".join(card_post(p) for p in POSTS[:3])
    horas = "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (esc(a), esc(b)) for a, b in S["horarios"])
    outros = "".join("<li>%s</li>" % esc(o) for o in dados.OUTROS_SERVICOS)
    cursos = "".join("<li><h3>%s</h3><p>%s</p></li>" % (esc(c["nome"]), esc(c["texto"])) for c in dados.CURSOS)

    corpo = """
<section class="hero" aria-labelledby="hero-titulo">
  <div class="hero__grade largura">
    <div class="hero__texto">
      {selo}
      <h1 id="hero-titulo">Clínica de estética e ozonioterapia em Canaã dos Carajás</h1>
      <p class="hero__sub"><strong>Dor, vasinhos, gordura localizada, pele e intestino</strong>, com a biomédica Dra. Adelaine Montel, que estuda o seu caso antes de indicar qualquer procedimento.</p>
      <ul class="lista-check lista-check--clara hero__pontos">
        <li>Biomédica com inscrição ativa no CRBM desde 2011</li>
        <li>Referência em ozonioterapia na região de Carajás</li>
        <li>Segunda a sábado, no Centro de Canaã</li>
      </ul>
      <figure class="hero__dra">
        {foto_dra}
        <figcaption><strong>Dra. Adelaine Montel</strong><span>Biomédica esteta e ozonioterapeuta · CRBM 1437</span></figcaption>
      </figure>
    </div>
    <div class="cartao-form" id="agendar">
      {form}
    </div>
  </div>
</section>

<section class="secao secao--clara" aria-labelledby="sintomas-titulo">
  <div class="largura quando">
    <div class="quando__texto">
      <h2 id="sintomas-titulo">Quando procurar a Empatia Humana?</h2>
      <p>Toque no que mais incomoda você para ver como é o tratamento.</p>
    </div>
    <ul class="chips chips--links">{sintomas}</ul>
  </div>
</section>

<section class="secao secao--areia" id="tratamentos" aria-labelledby="trat-titulo">
  <div class="largura">
    <div class="secao__cabeca">
      <h2 id="trat-titulo">Tratamentos da clínica</h2>
      <p>Cada tratamento começa por uma avaliação com a Dra. Adelaine. Escolha o que mais incomoda você e veja como funciona.</p>
    </div>
    <ul class="cards-trat">{trats}</ul>
    <div class="tambem"><p class="tambem__titulo">Também na clínica</p><ul class="etiquetas">{outros}</ul></div>
  </div>
</section>

<section class="numeros" aria-label="A clínica em números">
  <ul class="largura numeros__lista">
    <li><strong>+18 anos</strong><span>de formação da Dra. Adelaine</span></li>
    <li><strong>{icone_estrela}5,0</strong><span>no Google, em {n_av} avaliações</span></li>
    <li><strong>CRBM 1437</strong><span>inscrição ativa no CRBM 4ª Região</span></li>
    <li><strong>Seg a sáb</strong><span>no Centro de Canaã dos Carajás</span></li>
  </ul>
</section>

<section class="secao secao--clara" id="dra-adelaine" aria-labelledby="dra-titulo">
  <div class="largura sobre">
    <figure class="sobre__foto">
      {foto_vertical}
      <figcaption class="sobre__selo"><strong>CRBM 1437</strong> inscrição ativa no CRBM 4ª Região</figcaption>
    </figure>
    <div class="sobre__texto">
      <h2 id="dra-titulo">Quem vai cuidar de você</h2>
      <p class="sobre__nome">Dra. Adelaine Barros Montel</p>
      <p class="sobre__cargo">Biomédica esteta e ozonioterapeuta</p>
      <p>Em 2015, Adelaine recebeu o diagnóstico de lúpus. Foi como paciente que ela conheceu a ozonioterapia e sentiu a diferença: menos dor, menos crises, mais disposição. Essa experiência mudou a forma como ela cuida das pessoas.</p>
      <p>Depois de anos em laboratório de análises clínicas, ela uniu a biomedicina, a nutrição ortomolecular e a ozonioterapia num jeito de atender que olha para o corpo inteiro. Hoje está à frente da Empatia Humana e forma outros profissionais nos cursos que ministra.</p>
      <blockquote class="citacao"><p>{frase}</p></blockquote>
      <a class="link-acao" href="{sobre}">Conheça a trajetória e a formação da Dra. Adelaine</a>
    </div>
  </div>
</section>

<section class="secao secao--areia" aria-labelledby="integrativa-titulo">
  <div class="largura integrativa">
    <div class="integrativa__texto">
      <h2 id="integrativa-titulo">O que é estética integrativa?</h2>
      <p><strong>Estética integrativa é o cuidado da aparência que considera o funcionamento do corpo inteiro.</strong> Em vez de tratar só a mancha, a gordura ou a dor, a avaliação busca o que está por trás: intestino, inflamação, circulação, vitaminas, hábitos e exames.</p>
      <p>Na prática, isso significa que o mesmo incômodo pode ter planos diferentes para pessoas diferentes. E que o tratamento costuma durar mais, porque cuida da causa junto com o sintoma.</p>
      <a class="link-acao" href="{post_integrativa}">Leia mais sobre estética integrativa</a>
    </div>
    <ol class="passos">
      <li><h3>Você conta o que sente</h3><p>Pelo formulário ou pelo WhatsApp. A equipe responde e marca o melhor horário.</p></li>
      <li><h3>Avaliação sem pressa</h3><p>A Dra. Adelaine ouve sua história, examina e analisa seus exames.</p></li>
      <li><h3>O mapa do seu caso</h3><p>Na consulta integrativa, você recebe por escrito o estudo do seu caso.</p></li>
      <li><h3>Um plano só seu</h3><p>Tratamento, número de sessões e cuidados em casa pensados para o seu corpo.</p></li>
    </ol>
  </div>
</section>

<section class="secao secao--clara" id="depoimentos" aria-labelledby="dep-titulo">
  <div class="largura">
    <div class="secao__cabeca secao__cabeca--centro">
      <h2 id="dep-titulo">Quem passou pela clínica conta</h2>
      <p>Relatos que os pacientes mandaram para a clínica e avaliações públicas no Google.</p>
    </div>
    {video}
    <h3 class="subtitulo-centro">Direto do WhatsApp</h3>
    {whats}
    {google}
    <p class="centro"><a class="botao botao--mata" href="#agendar" data-abrir-form data-origem="depoimentos">{svg}<span>Quero saber valores e horários</span></a></p>
  </div>
</section>

<section class="secao secao--areia" id="duvidas" aria-labelledby="duvidas-titulo">
  <div class="largura estreita">
    <h2 id="duvidas-titulo" class="centro">Dúvidas frequentes</h2>
    {faq}
  </div>
</section>

<section class="secao secao--clara" id="contato" aria-labelledby="onde-titulo">
  <div class="largura onde">
    <div class="onde__texto">
      <h2 id="onde-titulo">Onde fica a clínica</h2>
      <address>{end}<br>{bairro}, {cidade} ({uf})</address>
      <dl class="horarios">{horas}</dl>
      <p class="onde__nota">Atendimento com horário marcado. Recebemos pacientes de Canaã, Parauapebas, Curionópolis e região.</p>
      <div class="onde__acoes">
        <a class="botao botao--mata" href="{maps}" target="_blank" rel="noopener">Abrir no Google Maps</a>
        <a class="link-acao" href="#agendar" data-abrir-form data-origem="contato">Agendar avaliação</a>
      </div>
    </div>
    <div class="onde__fotos">
      {foto_fachada}
      <iframe title="Mapa com a localização da Clínica Empatia Humana em Canaã dos Carajás" src="{embed}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
    </div>
  </div>
</section>

<section class="final" aria-labelledby="final-titulo">
  <div class="largura final__grade">
    <div class="final__texto">
      <h2 id="final-titulo">O primeiro passo é uma conversa.</h2>
      <p>Deixe seu nome, WhatsApp e e-mail. Você cai direto na conversa com a clínica para tirar dúvidas e marcar sua avaliação.</p>
      <p class="final__manuscrito" aria-hidden="true">te esperamos com empatia</p>
    </div>
    <div class="cartao-form">
      {form_final}
    </div>
  </div>
</section>

<section class="secao secao--areia" aria-labelledby="blog-titulo">
  <div class="largura">
    <div class="secao__cabeca secao__cabeca--linha">
      <div><h2 id="blog-titulo">Blog da Dra. Adelaine</h2><p>Explicações claras sobre os tratamentos e a saúde de dentro para fora.</p></div>
      <a class="link-acao" href="{blog}">Ver todos os posts</a>
    </div>
    <ul class="cards-post">{posts}</ul>
  </div>
</section>

<section class="secao secao--clara" aria-labelledby="cursos-titulo">
  <div class="largura">
    <div class="secao__cabeca">
      <h2 id="cursos-titulo">Cursos para profissionais</h2>
      <p>A Dra. Adelaine também forma outros profissionais, em turmas presenciais em Canaã dos Carajás, com certificado.</p>
    </div>
    <ul class="cursos">{cursos}</ul>
    <a class="link-acao cursos__acao" href="{link_cursos}">Ver os cursos e entrar na lista das próximas turmas</a>
  </div>
</section>

""".format(
        selo=selo_google("selo-google--claro"),
        foto_dra=foto_nome("adelaine-avatar", "Dra. Adelaine Montel, biomédica esteta, sorrindo", "hero__dra-img"),
        form=formulario("hero", "", origem="hero", titulo_tag="h2"),
        sintomas=sintomas, trats=trats, outros=outros,
        icone_estrela=icone("estrela", "icone icone--estrela"), n_av=S["avaliacoes_google"],
        foto_vertical=foto_nome("adelaine-vertical-540", "Retrato da Dra. Adelaine Montel"),
        frase=esc(DRA["frase"]), sobre=link("dra-adelaine-montel/"),
        post_integrativa=link("blog/estetica-integrativa-o-que-e/") if "estetica-integrativa-o-que-e" in POST else link("tratamentos/consulta-integrativa/"),
        video=bloco_video(), whats=bloco_whats(dados.WHATSAPP[:3]), google=bloco_avaliacoes(9), svg=SVG_WHATS,
        faq=faq_html(dados.FAQ_HOME).replace("Muitas pacientes vêm de Parauapebas", 'Muitas pacientes vêm de <a href="%s">Parauapebas</a>' % link("pacientes-de-parauapebas/"), 1), blog=link("blog/"), posts=posts,
        cursos=cursos, link_cursos=link("cursos/"),
        end=esc(S["endereco"]), bairro=S["bairro"], cidade=S["cidade"], uf=S["uf"], horas=horas, maps=esc(S["maps"]), embed=esc(S["maps_embed"]),
        foto_fachada=foto_nome("fachada", "Fachada da Clínica Empatia Humana com o letreiro, na Rua Círio de Nazaré"),
        form_final=formulario("final", "", origem="final", titulo_tag="h3"),
    )
    grafo = [schema_clinica(), schema_pessoa(), schema_site(), schema_faq(dados.FAQ_HOME),
             {"@type": "WebPage", "@id": absoluto("#pagina"), "url": absoluto(), "name": "Clínica de estética integrativa em Canaã dos Carajás", "isPartOf": {"@id": absoluto("#site")}, "about": {"@id": absoluto("#clinica")}, "inLanguage": "pt-BR", "dateModified": HOJE}]
    h = head("Clínica de estética em Canaã dos Carajás | Empatia Humana",
             "Ozonioterapia, tratamento de vasinhos (PEIM), lipo ozonizada, saúde intestinal e limpeza de pele em Canaã dos Carajás (PA), com a Dra. Adelaine Montel.",
             "", grafo)
    return pagina(h, corpo, data_pagina="inicio")


def pagina_tratamento(t):
    caminho = "tratamentos/%s/" % t["slug"]
    chips = "".join("<li>%s</li>" % esc(c) for c in t["chips"])
    ident = "".join("<p>%s</p>" % esc(p) for p in t["ident"])
    benef = "".join("<li><span class=\"num\">%d</span><span>%s</span></li>" % (i + 1, esc(b)) for i, b in enumerate(t["beneficios"]))
    como = "".join("<li><h3>%s</h3><p>%s</p></li>" % (esc(a), esc(b)) for a, b in t["como"])
    sinais = "".join("<li>%s</li>" % esc(s) for s in t["sinais"])
    inclui = "".join("<li>%s</li>" % esc(i) for i in t["inclui"])
    outros = "".join('<li><a href="%s">%s %s</a></li>' % (link("tratamentos/%s/" % o["slug"]), icone(o["icone"], "icone icone--menu"), esc(o["nome"])) for o in dados.TRATAMENTOS if o["slug"] != t["slug"])
    posts_rel = [POST[s] for s in t.get("posts", []) if s in POST]
    if not posts_rel:
        posts_rel = POSTS[:2]
    posts_html = "".join(card_post(p) for p in posts_rel[:3])

    prova = ""
    if t.get("depoimento_video"):
        prova += bloco_video()
    if t.get("depoimento_whats"):
        prova += bloco_whats([w for w in dados.WHATSAPP if w["tratamento"] == t["depoimento_whats"]])
    prova += bloco_avaliacoes(6, primeiro=["Aurora F.", "Juliane A.", "Marcos Z."])
    faq_t = list(t["faq"]) + list(dados.FAQ_TRATAMENTO_COMUM)

    aviso = '<p class="aviso">%s %s</p>' % (icone("escudo", "icone icone--aviso"), esc(t["aviso"])) if t.get("aviso") else ""

    corpo = """
<section class="hero hero--trat" aria-labelledby="hero-titulo">
  <div class="hero__grade largura">
    <div class="hero__texto">
      {migalhas}
      <h1 id="hero-titulo">{h1}</h1>
      <p class="hero__frase">{sub}</p>
      <p class="hero__destaque">{destaque}</p>
      {selo}
      <ul class="chips chips--claros">{chips}</ul>
      <figure class="hero__dra hero__dra--pequena">
        {foto_dra}
        <figcaption><strong><a href="{sobre}">Com a Dra. Adelaine Montel</a></strong><span>Biomédica esteta e ozonioterapeuta · CRBM 1437</span></figcaption>
      </figure>
    </div>
    <div class="cartao-form" id="agendar">
      {form}
    </div>
  </div>
</section>

<section class="resumo-trat" aria-label="Resumo do tratamento">
  <div class="largura">
    <dl class="resumo-trat__grade">
      <div class="resumo-trat__oque"><dt>Em resumo</dt><dd>{resumo}</dd></div>
      <div><dt>Quem faz</dt><dd><a href="{sobre}">Dra. Adelaine Montel</a>, biomédica, CRBM 1437</dd></div>
      <div><dt>Onde</dt><dd>Centro de Canaã dos Carajás (PA), segunda a sábado</dd></div>
      <div><dt>Sessões</dt><dd>Definidas na avaliação, conforme o seu caso</dd></div>
    </dl>
  </div>
</section>

<section class="secao secao--clara" aria-labelledby="ident-titulo">
  <div class="largura ident">
    <div class="ident__texto">
      <h2 id="ident-titulo">{ident_titulo}</h2>
      {ident}
      <p class="ident__virada">{reframe}</p>
    </div>
    <figure class="ident__foto{foto_classe}">{foto}</figure>
  </div>
</section>

<section class="secao secao--areia" aria-labelledby="prova-titulo">
  <div class="largura">
    <h2 id="prova-titulo" class="centro">Quem já passou pela Empatia Humana</h2>
    {prova}
  </div>
</section>

<section class="secao secao--clara" aria-labelledby="oque-titulo">
  <div class="largura oque">
    <div>
      <h2 id="oque-titulo">{oque_titulo}</h2>
      <p class="oque__intro">{oque_intro}</p>
      <ol class="beneficios">{benef}</ol>
    </div>
    <div class="cartao-inclui">
      <p class="cartao-inclui__titulo">Na Empatia Humana</p>
      <ul class="lista-check">{inclui}</ul>
      <a class="botao botao--mata botao--cheio" href="#agendar" data-abrir-form data-origem="inclui">{svg}<span>Quero saber valores e horários</span></a>
    </div>
  </div>
</section>

<section class="secao secao--areia" aria-labelledby="como-titulo">
  <div class="largura">
    <div class="secao__cabeca"><h2 id="como-titulo">Como é o tratamento, passo a passo</h2></div>
    <ol class="passos passos--quatro">{como}</ol>
    {aviso}
  </div>
</section>



<section class="secao secao--clara" aria-labelledby="faq-titulo">
  <div class="largura estreita">
    <h2 id="faq-titulo" class="centro">Perguntas sobre {nome_min}</h2>
    {faq}
  </div>
</section>

<section class="secao sinais-bloco" aria-labelledby="sinais-titulo">
  <div class="largura">
    <h2 id="sinais-titulo">Quando é hora de procurar?</h2>
    <ul class="sinais">{sinais}</ul>
    <div class="ganho">
      <p class="ganho__titulo">{ganho_titulo}</p>
      <p>{ganho}</p>
      <a class="botao botao--ouro" href="#agendar" data-abrir-form data-origem="ganho">{svg}<span>Quero saber valores e horários</span></a>
    </div>
  </div>
</section>

<section class="secao secao--clara" aria-labelledby="mais-titulo">
  <div class="largura">
    <h2 id="mais-titulo">Para ler antes da avaliação</h2>
    <ul class="cards-post">{posts}</ul>
    <h2 class="outros__titulo">Outros tratamentos</h2>
    <ul class="outros">{outros}</ul>
  </div>
</section>

{faixa}
""".format(
        migalhas=migalhas_html([("Início", ""), ("Tratamentos", "tratamentos/"), (t["nome"], caminho)]),
        resumo=esc(dados.RESUMOS.get(t["slug"], t["card"])), sobre=link("dra-adelaine-montel/"), h1=esc(t["h1"]), sub=esc(t["sub"]), destaque=esc(t.get("destaque") or t["card"]), selo=selo_google("selo-google--claro"), chips=chips,
        foto_dra=foto_nome("adelaine-avatar", "Dra. Adelaine Montel", "hero__dra-img"),
        form=formulario("hero", t["interesse"], origem="hero"),
        ident_titulo=esc(t["ident_titulo"]), ident=ident, reframe=esc(t["reframe"]),
        foto=foto_nome(t["foto"], t["foto_alt"]), foto_classe=(" ident__foto--retrato" if FOTOS[t["foto"]][1] > FOTOS[t["foto"]][0] else ""),
        oque_titulo=esc(t["oque_titulo"]), oque_intro=esc(t["oque_intro"]), benef=benef, inclui=inclui, svg=SVG_WHATS,
        como=como, aviso=aviso, sinais=sinais, ganho_titulo=esc(t["ganho_titulo"]), ganho=esc(t["ganho"]),
        prova=prova, faq=faq_html(faq_t, abrir_primeira=True), nome_min=esc(t["nome"].lower()), posts=posts_html, outros=outros,
        faixa=cta_faixa(esc(t["ganho_titulo"]), "Agende sua avaliação com a Dra. Adelaine Montel em Canaã dos Carajás.", t["interesse"], "faixa_final"),
    )
    grafo = [
        {"@type": "MedicalWebPage", "@id": absoluto(caminho + "#pagina"), "url": absoluto(caminho), "name": t["h1"], "description": t["meta"], "inLanguage": "pt-BR", "isPartOf": {"@id": absoluto("#site")}, "about": {"@id": absoluto(caminho + "#servico")}, "reviewedBy": {"@id": absoluto("dra-adelaine-montel/#pessoa")}, "lastReviewed": HOJE},
        {"@type": ["Service", "MedicalProcedure"], "@id": absoluto(caminho + "#servico"), "name": t["nome"], "serviceType": t["nome"], "description": dados.RESUMOS.get(t["slug"], t["oque_intro"]), "provider": {"@id": absoluto("#clinica")}, "areaServed": [{"@type": "City", "name": c} for c in S["regiao"]], "url": absoluto(caminho)},
        schema_clinica(), schema_pessoa(), schema_site(), schema_faq(faq_t),
        schema_migalhas([("Início", ""), ("Tratamentos", "tratamentos/"), (t["nome"], caminho)]),
    ]
    h = head(t["seo_title"], t["meta"], caminho, grafo)
    return pagina(h, corpo, atual="tratamentos", interesse=t["interesse"], data_pagina="tratamento", data_trat=t["slug"])


def pagina_tratamentos():
    caminho = "tratamentos/"
    cards = "".join("""<li class="card-trat card-trat--grande">
  <a href="{h}">{ic}<h2>{n}</h2><p class="card-trat__frase">{s}</p><p>{c}</p><span class="card-trat__mais">Conhecer o tratamento {seta}</span></a>
</li>""".format(h=link("tratamentos/%s/" % t["slug"]), ic=icone(t["icone"], "icone icone--card"), n=esc(t["nome"]), s=esc(t["sub"]), c=esc(t["card"]), seta=icone("seta", "icone icone--seta")) for t in dados.TRATAMENTOS)
    cards += card_cta().replace("card-trat card-trat--cta", "card-trat card-trat--grande card-trat--cta").replace("<h3>", "<h2>").replace("</h3>", "</h2>")
    outros = "".join("<li>%s</li>" % esc(o) for o in dados.OUTROS_SERVICOS)
    corpo = """
<section class="cabeca-pagina">
  <div class="largura">
    {mig}
    <h1>Tratamentos de estética integrativa em Canaã dos Carajás</h1>
    <p>Dor, vasinhos, gordura localizada, pele, intestino e disposição. Escolha o que mais incomoda você para ver como é o tratamento, o que esperar e as respostas para as dúvidas mais comuns.</p>
  </div>
</section>
<section class="secao secao--clara">
  <div class="largura">
    <ul class="cards-trat cards-trat--hub">{cards}</ul>
    <div class="tambem"><p class="tambem__titulo">Também na clínica</p><ul class="etiquetas">{outros}</ul></div>
  </div>
</section>
{faixa}
""".format(mig=migalhas_html([("Início", ""), ("Tratamentos", caminho)]), cards=cards, outros=outros,
           faixa=cta_faixa("Não sabe por onde começar?", "Conte o que você sente. A Dra. Adelaine indica o tratamento certo na avaliação.", "", "faixa_hub"))
    grafo = [{"@type": "CollectionPage", "@id": absoluto(caminho + "#pagina"), "url": absoluto(caminho), "name": "Tratamentos da Clínica Empatia Humana", "isPartOf": {"@id": absoluto("#site")}, "inLanguage": "pt-BR",
              "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": absoluto("tratamentos/%s/" % t["slug"]), "name": t["nome"]} for i, t in enumerate(dados.TRATAMENTOS)]}},
             schema_clinica(), schema_site(), schema_migalhas([("Início", ""), ("Tratamentos", caminho)])]
    h = head("Tratamentos estéticos em Canaã dos Carajás | Empatia Humana",
             "Ozonioterapia, PEIM para vasinhos, lipo ozonizada, saúde intestinal, limpeza de pele e soroterapia em Canaã dos Carajás (PA). Veja como é cada tratamento.",
             caminho, grafo)
    return pagina(h, corpo, atual="tratamentos", data_pagina="tratamentos")


def pagina_sobre():
    caminho = "dra-adelaine-montel/"
    formacao = "".join("<li>%s</li>" % esc(f) for f in DRA["formacao"])
    habil = "".join("<dd>%s</dd>" % esc(h) for h in DRA["habilitacoes"])
    corpo = """
<section class="cabeca-pagina cabeca-pagina--dra">
  <div class="largura dra-topo">
    <div>
      {mig}
      <h1>Dra. Adelaine Montel, biomédica esteta e ozonioterapeuta em Canaã dos Carajás</h1>
      <p>Responsável técnica da Clínica Empatia Humana. Mais de 18 anos de formada, inscrição nº 1437 no CRBM 4ª Região desde 2011 e uma história com a ozonioterapia que começou como paciente.</p>
      {selo}
      <p><a class="botao botao--ouro" href="#agendar" data-abrir-form data-origem="sobre_topo">{svg}<span>Valores e horários com a Dra. Adelaine</span></a></p>
    </div>
    <figure class="dra-topo__foto">{foto}</figure>
  </div>
</section>

<section class="secao secao--clara">
  <div class="largura estreita texto-longo">
    <h2>Por que a estética integrativa</h2>
    <p>Em 2015, Adelaine Barros Montel recebeu o diagnóstico de lúpus, uma doença autoimune que trouxe momentos muito difíceis. Durante essa jornada, ela conheceu a ozonioterapia e, com o tempo, percebeu mudanças importantes na qualidade de vida: menos dor, menos crises inflamatórias, mais energia e disposição.</p>
    <p>Quando precisou deixar o laboratório de análises clínicas, onde atuava como biomédica, encontrou na estética integrativa uma forma de continuar cuidando de pessoas. Uniu a experiência com exames laboratoriais, a nutrição ortomolecular e a ozonioterapia num atendimento que olha para o ser humano por inteiro.</p>
    <blockquote class="citacao"><p>{frase}</p></blockquote>
    <h2>O que ela acredita</h2>
    <p>Antes de indicar qualquer procedimento, ela estuda o caso: na consulta integrativa, cada paciente recebe por escrito o mapeamento do que foi encontrado e o plano proposto.</p>
    <h2>Formação</h2>
    <ul class="lista-check">{formacao}</ul>
    <h2>Além do consultório</h2>
    <p>A fé é um dos pilares da sua vida, ao lado da família: o marido, Lídio Rocha, e a filha, Maria Luiza. Ela também forma outros profissionais da saúde e da estética em cursos presenciais em Canaã dos Carajás.</p>
  </div>
</section>

<section class="secao secao--areia">
  <div class="largura">
    <div class="registro">
      <div class="registro__texto">
        <h2>Registro conferido no Conselho de Biomedicina</h2>
        <p>Adelaine Barros Montel tem inscrição ativa nº 1437 no CRBM 4ª Região (Pará), requerida em 2011, e também é inscrita no CRBM 3ª Região (nº 18758). É a responsável técnica da Clínica Empatia Humana.</p>
        <a class="link-acao" href="{cfbm}" target="_blank" rel="noopener">Conferir na consulta pública do CFBM</a>
      </div>
      <dl class="registro__habilitacoes"><dt>Habilitações registradas</dt>{habil}</dl>
    </div>
  </div>
</section>

<section class="secao secao--clara">
  <div class="largura">
    <h2 class="centro">O que os pacientes dizem</h2>
    {google}
  </div>
</section>
{faixa}
""".format(mig=migalhas_html([("Início", ""), ("Dra. Adelaine Montel", caminho)]), selo=selo_google("selo-google--claro"), svg=SVG_WHATS,
           foto=foto_nome("adelaine-vertical", "Dra. Adelaine Montel, biomédica esteta, sorrindo", lazy=False, prioridade=True),
           frase=esc(DRA["frase"]), formacao=formacao, cfbm=esc(DRA["consulta_cfbm"]), habil=habil, google=bloco_avaliacoes(9),
           faixa=cta_faixa("Quer ser atendida pela Dra. Adelaine?", "Deixe seu contato e continue a conversa no WhatsApp da clínica.", "", "faixa_sobre"))
    grafo = [{"@type": "ProfilePage", "@id": absoluto(caminho + "#pagina"), "url": absoluto(caminho), "name": "Dra. Adelaine Montel", "mainEntity": {"@id": absoluto(caminho + "#pessoa")}, "isPartOf": {"@id": absoluto("#site")}, "inLanguage": "pt-BR", "dateModified": HOJE},
             schema_pessoa(), schema_clinica(), schema_site(), schema_migalhas([("Início", ""), ("Dra. Adelaine Montel", caminho)])]
    h = head("Dra. Adelaine Montel, biomédica em Canaã dos Carajás",
             "Conheça a Dra. Adelaine Barros Montel: biomédica esteta e ozonioterapeuta, CRBM 4ª Região nº 1437, responsável pela Clínica Empatia Humana em Canaã dos Carajás.",
             caminho, grafo, tipo="profile")
    return pagina(h, corpo, atual="sobre", data_pagina="sobre")


def pagina_cursos():
    caminho = "cursos/"
    cursos = "".join("<li><h2>%s</h2><p>%s</p>%s</li>" % (esc(c["nome"]), esc(c["texto"]), ('<a class="link-acao" href="%s" target="_blank" rel="noopener">Inscrever-se na lista</a>' % esc(c["link"])) if c.get("link") else "") for c in dados.CURSOS)
    corpo = """
<section class="cabeca-pagina">
  <div class="largura">
    {mig}
    <h1>Cursos para profissionais da saúde e da estética em Canaã dos Carajás</h1>
    <p>Turmas presenciais com a Dra. Adelaine Montel, biomédica com formação em análises clínicas, nutrição ortomolecular e ozonioterapia. Aulas teóricas e práticas, estudo de casos e certificado.</p>
  </div>
</section>
<section class="secao secao--clara">
  <div class="largura cursos-grade">
    <ul class="cursos cursos--pagina">{cursos}</ul>
    <div class="cartao-form" id="agendar">{form}</div>
  </div>
</section>
""".format(mig=migalhas_html([("Início", ""), ("Cursos", caminho)]), cursos=cursos,
           form=formulario("cursos", "cursos para profissionais", titulo="Quero saber das próximas turmas", texto="Deixe seus dados e receba as datas e condições pelo WhatsApp.", botao="Quero saber das turmas", origem="cursos"))
    grafo = [{"@type": "WebPage", "@id": absoluto(caminho + "#pagina"), "url": absoluto(caminho), "name": "Cursos para profissionais", "isPartOf": {"@id": absoluto("#site")}, "inLanguage": "pt-BR"}]
    grafo += [{"@type": "Course", "name": c["nome"], "description": c["texto"], "inLanguage": "pt-BR", "provider": {"@id": absoluto("#clinica")}} for c in dados.CURSOS]
    grafo += [schema_clinica(), schema_site(), schema_migalhas([("Início", ""), ("Cursos", caminho)])]
    h = head("Cursos de ozonioterapia em Canaã dos Carajás",
             "Cursos presenciais com a Dra. Adelaine Montel em Canaã dos Carajás: interpretação de exames laboratoriais, ozonioterapia na dor crônica e limpeza de pele.",
             caminho, grafo)
    return pagina(h, corpo, atual="cursos", interesse="cursos para profissionais", data_pagina="cursos")


def pagina_blog():
    caminho = "blog/"
    cats = sorted(set(p.get("categoria", "Blog") for p in POSTS))
    filtros = '<li><button type="button" class="filtro" data-filtro="" aria-pressed="true">Todos</button></li>' + "".join('<li><button type="button" class="filtro" data-filtro="%s" aria-pressed="false">%s</button></li>' % (esc(c), esc(c)) for c in cats)
    cards = "".join(card_post(p, "h2").replace('<li class="card-post">', '<li class="card-post" data-categoria="%s">' % esc(p.get("categoria", "Blog")), 1) for p in POSTS)
    corpo = """
<section class="cabeca-pagina">
  <div class="largura">
    {mig}
    <h1>Blog da Dra. Adelaine Montel</h1>
    <p>Ozonioterapia, vasinhos, saúde intestinal, pele e estética integrativa explicados de forma simples, por quem atende em Canaã dos Carajás.</p>
  </div>
</section>
<section class="secao secao--clara">
  <div class="largura">
    <ul class="filtros" aria-label="Filtrar por tema">{filtros}</ul>
    <ul class="cards-post cards-post--blog">{cards}</ul>
  </div>
</section>
{faixa}
""".format(mig=migalhas_html([("Início", ""), ("Blog", caminho)]), filtros=filtros, cards=cards,
           faixa=cta_faixa("Ficou com alguma dúvida?", "Pergunte direto para a equipe da clínica pelo WhatsApp.", "", "faixa_blog", "Falar com a clínica"))
    grafo = [{"@type": "Blog", "@id": absoluto(caminho + "#blog"), "url": absoluto(caminho), "name": "Blog da Dra. Adelaine Montel", "inLanguage": "pt-BR", "publisher": {"@id": absoluto("#clinica")}, "author": {"@id": absoluto("dra-adelaine-montel/#pessoa")},
              "blogPost": [{"@type": "BlogPosting", "@id": absoluto("blog/%s/#post" % p["slug"]), "headline": p["titulo"], "url": absoluto("blog/%s/" % p["slug"]), "datePublished": p.get("data", HOJE) + "T08:00:00-03:00", "author": {"@id": absoluto("dra-adelaine-montel/#pessoa")}} for p in POSTS]},
             schema_clinica(), schema_pessoa(), schema_site(), schema_migalhas([("Início", ""), ("Blog", caminho)])]
    h = head("Blog da Dra. Adelaine Montel | Empatia Humana",
             "Artigos sobre ozonioterapia, vasinhos, lipo ozonizada, saúde intestinal e pele, escritos pela equipe da Clínica Empatia Humana em Canaã dos Carajás (PA).",
             caminho, grafo)
    return pagina(h, corpo, atual="blog", data_pagina="blog")


def pagina_post(p):
    caminho = "blog/%s/" % p["slug"]
    t = TRAT.get(p.get("tratamento", ""))
    interesse = t["interesse"] if t else ""
    toc = "".join('<li><a href="#%s">%s</a></li>' % (i, inline(n)) for i, n in p["toc"])
    relacionados = [x for x in POSTS if x["slug"] != p["slug"]]
    relacionados.sort(key=lambda x: (x.get("categoria") != p.get("categoria"), x.get("data", "")))
    rel = "".join(card_post(x) for x in relacionados[:3])
    cta_trat = ""
    if t:
        cta_trat = """<aside class="cta-post" aria-label="Tratamento relacionado">
  {ic}
  <div>
    <p class="cta-post__titulo">{h1}</p>
    <p>{sub} Agende sua avaliação com a Dra. Adelaine Montel.</p>
    <p class="cta-post__acoes"><a class="botao botao--ouro" href="#agendar" data-abrir-form data-origem="post_meio" data-interesse="{i}">{svg}<span>Quero saber valores e horários</span></a><a class="link-acao" href="{h}">Ver como é o tratamento</a></p>
  </div>
</aside>""".format(ic=icone(t["icone"], "icone icone--card"), h1=esc(t["h1"]), sub=esc(t["sub"]), i=esc(interesse), svg=SVG_WHATS, h=link("tratamentos/%s/" % t["slug"]))
    faq = ""
    if p["faq"]:
        faq = '<section class="post__faq" aria-labelledby="faq-post"><h2 id="faq-post">Perguntas frequentes</h2>%s</section>' % faq_html(p["faq"])
    lateral_trats = "".join('<li><a href="%s">%s %s</a></li>' % (link("tratamentos/%s/" % o["slug"]), icone(o["icone"], "icone icone--menu"), esc(o["nome"])) for o in dados.TRATAMENTOS)

    # coloca o CTA do tratamento depois do 2º subtítulo
    corpo_post = p["html"]
    partes = corpo_post.split("<h2 ")
    if len(partes) > 3 and cta_trat:
        corpo_post = "<h2 ".join(partes[:3]) + cta_trat.replace('data-origem="post_meio"', 'data-origem="post_meio"') + "<h2 " + "<h2 ".join(partes[3:])
        cta_fim = ""
    else:
        cta_fim = cta_trat

    corpo = """
<article class="post">
  <header class="post__cabeca">
    <div class="largura estreita">
      {mig}
      <p class="post__cat">{cat}</p>
      <h1>{titulo}</h1>
      <div class="post__autor">
        <img src="{base}assets/img/adelaine-avatar.webp" width="48" height="48" alt="" loading="lazy">
        <p>Por <a href="{sobre}">Dra. Adelaine Montel</a>, biomédica esteta e ozonioterapeuta (CRBM 1437)<br><span>{data} · {tl} min de leitura</span></p>
      </div>
    </div>
  </header>
  <div class="largura post__grade">
    <div class="post__corpo">
      <div class="resposta-rapida"><p class="resposta-rapida__titulo">Resposta rápida</p><p>{resumo}</p></div>
      {toc_html}
      <div class="texto-longo">{html}</div>
      {cta_fim}
      {faq}
      <aside class="autor-box" aria-label="Sobre a autora">
        <img src="{base}assets/img/adelaine-avatar.webp" width="88" height="88" alt="Dra. Adelaine Montel" loading="lazy">
        <div><p class="autor-box__nome">Dra. Adelaine Barros Montel</p><p>Biomédica esteta e ozonioterapeuta, inscrição nº 1437 no CRBM 4ª Região, responsável técnica da Clínica Empatia Humana em Canaã dos Carajás. Pós-graduada em Nutrição Ortomolecular, com mais de 18 anos de formada.</p><a class="link-acao" href="{sobre}">Conheça a Dra. Adelaine</a></div>
      </aside>
      <p class="post__aviso">Este conteúdo é informativo e não substitui uma avaliação individual.</p>
    </div>
    <aside class="post__lateral" aria-label="Agendamento e tratamentos">
      <div class="lateral-cartao">
        <p class="lateral-cartao__titulo">Valores e horários pelo WhatsApp</p>
        <p>Com a Dra. Adelaine Montel, no Centro de Canaã dos Carajás.</p>
        {selo}
        <a class="botao botao--ouro botao--cheio" href="#agendar" data-abrir-form data-origem="post_lateral" data-interesse="{i}">{svg}<span>Valores e horários</span></a>
      </div>
      <div class="lateral-lista"><p class="lateral-lista__titulo">Tratamentos</p><ul>{lateral_trats}</ul></div>
    </aside>
  </div>
</article>
<section class="secao secao--areia" aria-labelledby="rel-titulo">
  <div class="largura">
    <h2 id="rel-titulo">Continue lendo</h2>
    <ul class="cards-post">{rel}</ul>
  </div>
</section>
""".format(mig=migalhas_html([("Início", ""), ("Blog", "blog/"), (p["titulo"], caminho)]), cat=esc(p.get("categoria", "Blog")), titulo=esc(p["titulo"]),
           base=BASE, sobre=link("dra-adelaine-montel/"), data=data_br(p.get("data", "")), tl=p["tempo_leitura"], resumo=inline(p.get("resumo", "")),
           toc_html=('<nav class="indice-post" aria-label="Neste post"><p class="indice-post__titulo">Neste post</p><ol>%s</ol></nav>' % toc) if len(p["toc"]) > 2 else "",
           html=corpo_post, cta_fim=cta_fim, faq=faq, selo=selo_google(), i=esc(interesse), svg=SVG_WHATS, lateral_trats=lateral_trats, rel=rel)
    grafo = [
        {"@type": "BlogPosting", "@id": absoluto(caminho + "#post"), "headline": p["titulo"], "description": p.get("descricao", ""), "abstract": p.get("resumo", ""),
         "url": absoluto(caminho), "mainEntityOfPage": absoluto(caminho), "datePublished": p.get("data", HOJE) + "T08:00:00-03:00", "dateModified": p.get("atualizado", p.get("data", HOJE)) + "T08:00:00-03:00",
         "inLanguage": "pt-BR", "articleSection": p.get("categoria", "Blog"), "wordCount": p["palavras"],
         "image": absoluto("assets/img/og-empatia.jpg"), "author": {"@id": absoluto("dra-adelaine-montel/#pessoa")}, "publisher": {"@id": absoluto("#clinica")},
         "isPartOf": {"@id": absoluto("blog/#blog")}, "about": ({"@id": absoluto("tratamentos/%s/#servico" % t["slug"])} if t else None)},
        schema_pessoa(), schema_clinica(), schema_site(),
        schema_migalhas([("Início", ""), ("Blog", "blog/"), (p["titulo"], caminho)]),
    ]
    if not t:
        del grafo[0]["about"]
    if p["faq"]:
        grafo.append(schema_faq(p["faq"]))
    titulo_seo = p.get("seo_title") or (p["titulo"] + " | Empatia Humana" if len(p["titulo"]) <= 43 else p["titulo"])
    h = head(titulo_seo, p.get("descricao", p.get("resumo", "")), caminho, grafo, tipo="article",
             extra='\n  <meta property="article:published_time" content="%sT08:00:00-03:00">\n  <meta property="article:author" content="Dra. Adelaine Montel">' % p.get("data", HOJE))
    return pagina(h, corpo, atual="blog", interesse=interesse, data_pagina="post", data_trat=(t["slug"] if t else ""))


def pagina_parauapebas():
    caminho = "pacientes-de-parauapebas/"
    trats = "".join('<li><a href="%s">%s %s</a></li>' % (link("tratamentos/%s/" % t["slug"]), icone(t["icone"], "icone icone--menu"), esc(t["nome"])) for t in dados.TRATAMENTOS)
    horas = "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (esc(a), esc(b)) for a, b in S["horarios"])
    faq = dados.PARAUAPEBAS["faq"]
    corpo = """
<section class="cabeca-pagina">
  <div class="largura">
    {mig}
    <h1>Clínica de estética para quem é de Parauapebas</h1>
    <p>Pacientes de Parauapebas, Curionópolis e região fazem ozonioterapia, tratamento de vasinhos, lipo ozonizada e cuidados de pele e intestino na Empatia Humana, no Centro de Canaã dos Carajás, com a biomédica Dra. Adelaine Montel.</p>
    {selo}
    <p><a class="botao botao--ouro" href="#agendar" data-abrir-form data-origem="parauapebas_topo" data-interesse="avaliação (venho de Parauapebas)">{svg}<span>Quero saber valores e horários</span></a></p>
  </div>
</section>
<section class="secao secao--clara">
  <div class="largura onde">
    <div class="onde__texto">
      <h2>Vale a viagem até Canaã?</h2>
      <p class="onde__nota">Na Empatia Humana, cada caso é estudado antes de qualquer indicação. Quem vem de fora avisa no WhatsApp e a equipe organiza a agenda para aproveitar a viagem, inclusive aos sábados de manhã.</p>
      <ul class="lista-check" style="margin-top:1.25rem">
        <li>Avaliação com a própria Dra. Adelaine, biomédica com inscrição ativa no CRBM desde 2011</li>
        <li>Agenda pensada para quem viaja: avaliação e sessão no mesmo dia, quando o caso permite</li>
        <li>Atendimento aos sábados, das 8h às 12h</li>
      </ul>
      <h2 style="margin-top:2.5rem">Como chegar</h2>
      <address>{end}<br>{bairro}, {cidade} ({uf})</address>
      <dl class="horarios">{horas}</dl>
      <div class="onde__acoes"><a class="botao botao--mata" href="{maps}" target="_blank" rel="noopener">Abrir no Google Maps</a></div>
    </div>
    <div class="onde__fotos">{foto}<iframe title="Mapa da Clínica Empatia Humana em Canaã dos Carajás" src="{embed}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
  </div>
</section>
<section class="secao secao--areia">
  <div class="largura">
    <h2>Tratamentos que pacientes de Parauapebas procuram</h2>
    <ul class="outros" style="margin-top:1.5rem">{trats}</ul>
    {google}
  </div>
</section>
<section class="secao secao--clara">
  <div class="largura estreita">
    <h2 class="centro">Dúvidas de quem vem de Parauapebas</h2>
    {faq}
  </div>
</section>
{faixa}
""".format(mig=migalhas_html([("Início", ""), ("Pacientes de Parauapebas", caminho)]), selo=selo_google("selo-google--claro"), svg=SVG_WHATS,
           end=esc(S["endereco"]), bairro=S["bairro"], cidade=S["cidade"], uf=S["uf"], horas=horas, maps=esc(S["maps"]), embed=esc(S["maps_embed"]),
           foto=foto_nome("fachada", "Fachada da Clínica Empatia Humana em Canaã dos Carajás"), trats=trats, google=bloco_avaliacoes(6), faq=faq_html(faq),
           faixa=cta_faixa("Vem de Parauapebas?", "Avise no WhatsApp: a equipe organiza sua agenda para aproveitar a viagem.", "avaliação (venho de Parauapebas)", "faixa_parauapebas"))
    grafo = [{"@type": "WebPage", "@id": absoluto(caminho + "#pagina"), "url": absoluto(caminho), "name": "Clínica de estética para quem é de Parauapebas", "isPartOf": {"@id": absoluto("#site")}, "about": {"@id": absoluto("#clinica")}, "inLanguage": "pt-BR"},
             schema_clinica(), schema_site(), schema_faq(faq), schema_migalhas([("Início", ""), ("Pacientes de Parauapebas", caminho)])]
    h = head("Clínica de estética para pacientes de Parauapebas",
             "Pacientes de Parauapebas fazem ozonioterapia, tratamento de vasinhos e lipo ozonizada na Empatia Humana, em Canaã dos Carajás. Atendimento aos sábados.",
             caminho, grafo)
    return pagina(h, corpo, interesse="avaliação (venho de Parauapebas)", data_pagina="cidade")


def pagina_privacidade():
    corpo = """
<section class="cabeca-pagina"><div class="largura estreita"><h1>Política de privacidade</h1><p>Atualizada em novembro de 2026.</p></div></section>
<section class="secao secao--clara"><div class="largura estreita texto-longo">
<h2>Quem cuida dos seus dados</h2><p>{razao} (Empatia Humana), CNPJ {cnpj}, {end}, {bairro}, {cidade} ({uf}).</p>
<h2>Quais dados coletamos</h2><p>Pelos formulários do site: nome, WhatsApp e e-mail. Junto com eles, registramos a página em que você estava e de onde chegou ao site (por exemplo, o nome do anúncio ou da campanha), para saber quais divulgações funcionam.</p>
<h2>Para que usamos</h2><p>Para falar com você pelo WhatsApp, tirar suas dúvidas, marcar sua avaliação e mandar novidades da clínica. Você pode pedir para não receber mais mensagens a qualquer momento. Não vendemos nem emprestamos seus dados.</p>
<h2>Onde ficam guardados</h2><p>Em uma planilha privada da clínica no Google, acessada só pela equipe. O site é hospedado no GitHub Pages.</p>
<h2 id="cookies">Cookies e anúncios</h2><p>O site pode usar ferramentas de medição do Meta (Facebook e Instagram) e do Google para entender quantas pessoas chegam pelos anúncios e quantas pedem uma avaliação. Elas podem usar cookies. Você pode recusar no aviso de cookies ou em "Preferências de cookies", no rodapé.</p>
<h2>Seus direitos</h2><p>Você pode pedir para ver, corrigir ou apagar seus dados mandando uma mensagem para o WhatsApp da clínica, {tel}.</p>
<h2>Por quanto tempo</h2><p>Guardamos seus dados enquanto houver contato ou atendimento com a clínica, ou até você pedir para apagar.</p>
</div></section>""".format(razao=S["razao"], cnpj=S["cnpj"], end=esc(S["endereco"]), bairro=S["bairro"], cidade=S["cidade"], uf=S["uf"], tel=S["telefone"])
    h = head("Política de privacidade | Empatia Humana", "Como a Clínica Empatia Humana usa os dados enviados pelos formulários do site.", "politica-de-privacidade.html", [schema_site()])
    return pagina(h, corpo, data_pagina="privacidade")


def pagina_404():
    corpo = """
<section class="cabeca-pagina"><div class="largura estreita"><h1>Esta página não existe mais</h1><p>Talvez o endereço tenha mudado. Veja os tratamentos da clínica ou fale com a equipe.</p>
<p><a class="botao botao--ouro" href="{t}">Ver os tratamentos</a></p></div></section>""".format(t=link("tratamentos/"))
    h = head("Página não encontrada | Empatia Humana", "Página não encontrada.", "404.html", [schema_site()], robots="noindex, follow")
    return pagina(h, corpo, data_pagina="404")


# Arquivos de SEO e IA --------------------------------------------------------------

def urls_do_site():
    u = [("", "1.0"), ("tratamentos/", "0.9")]
    u += [("tratamentos/%s/" % t["slug"], "0.9") for t in dados.TRATAMENTOS]
    u += [("dra-adelaine-montel/", "0.8"), ("pacientes-de-parauapebas/", "0.7"), ("blog/", "0.8"), ("cursos/", "0.6")]
    u += [("blog/%s/" % p["slug"], "0.7") for p in POSTS]
    return u


def sitemap():
    linhas = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for c, pr in urls_do_site():
        lm = HOJE
        if c.startswith("blog/") and c != "blog/":
            lm = POST[c.split("/")[1]].get("atualizado", POST[c.split("/")[1]].get("data", HOJE))
        linhas.append("  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>" % (esc(absoluto(c)), lm, pr))
    linhas.append("</urlset>")
    return "\n".join(linhas) + "\n"


def robots():
    return "User-agent: *\nAllow: /\n\n# Buscadores com IA são bem-vindos a ler e citar o site\nUser-agent: GPTBot\nAllow: /\nUser-agent: OAI-SearchBot\nAllow: /\nUser-agent: ChatGPT-User\nAllow: /\nUser-agent: PerplexityBot\nAllow: /\nUser-agent: ClaudeBot\nAllow: /\nUser-agent: Google-Extended\nAllow: /\n\nSitemap: %s\n" % absoluto("sitemap.xml")


def llms():
    l = ["# Clínica Empatia Humana", "",
         "> Clínica de estética integrativa e ozonioterapia em Canaã dos Carajás (PA), Brasil. Responsável técnica: Dra. Adelaine Barros Montel, biomédica esteta e ozonioterapeuta, inscrição nº 1437 no CRBM 4ª Região desde 2011. Nota 5,0 no Google em %d avaliações (conferido em %s)." % (S["avaliacoes_google"], S["avaliacoes_conferidas_em"]), "",
         "Atualizado em %s." % data_br(HOJE), "",
         "## Dados da clínica",
         "- Nome: Clínica Empatia Humana (Empatia Humana - Conceito em Estética Integrativa)",
         "- Endereço: %s, %s, %s - %s" % (S["endereco"], S["bairro"], S["cidade"], S["uf"]),
         "- WhatsApp: %s" % S["telefone"],
         "- Horário: segunda a sexta, 8h às 12h e 14h às 18h; sábado, 8h às 12h; atendimento com horário marcado",
         "- Atende pacientes de: %s" % ", ".join(S["regiao"]),
         "- Instagram: %s e %s" % (S["instagram_clinica"], S["instagram_dra"]),
         "- Google Maps: %s" % S["maps_cid"],
         "- Registro da responsável: Adelaine Barros Montel, CRBM 4ª Região nº 1437, ativo; habilitações em %s" % "; ".join(DRA["habilitacoes"]),
         "", "## Tratamentos"]
    for t in dados.TRATAMENTOS:
        l.append("- [%s](%s): %s" % (t["nome"], absoluto("tratamentos/%s/" % t["slug"]), dados.RESUMOS.get(t["slug"], t["card"])))
    l += ["", "## Sobre a Dra. Adelaine Montel", "- [Trajetória, formação e registro](%s)" % absoluto("dra-adelaine-montel/"), "", "## Blog"]
    for p in POSTS:
        l.append("- [%s](%s): %s" % (p["titulo"], absoluto("blog/%s/" % p["slug"]), p.get("resumo", "")))
    l += ["", "## Cursos", "- [Cursos para profissionais](%s): %s" % (absoluto("cursos/"), "; ".join(c["nome"] for c in dados.CURSOS))]
    l += ["", "## Perguntas frequentes"]
    for q, a in dados.FAQ_HOME:
        l.append("- **%s** %s" % (q, a))
    l += ["", "## Pacientes de outras cidades", "- [Pacientes de Parauapebas](%s)" % absoluto("pacientes-de-parauapebas/"), ""]
    return "\n".join(l)


def feed():
    itens = []
    for p in POSTS[:20]:
        itens.append("""  <item>
    <title>{t}</title>
    <link>{u}</link>
    <guid>{u}</guid>
    <pubDate>{d}</pubDate>
    <description>{r}</description>
  </item>""".format(t=esc(p["titulo"]), u=esc(absoluto("blog/%s/" % p["slug"])), d=_rfc822(p.get("data", HOJE)), r=esc(p.get("resumo", ""))))
    return """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>Blog da Dra. Adelaine Montel | Empatia Humana</title>
  <link>{u}</link>
  <description>Estética integrativa, ozonioterapia e saúde de dentro para fora, em Canaã dos Carajás (PA).</description>
  <language>pt-BR</language>
{itens}
</channel>
</rss>
""".format(u=esc(absoluto("blog/")), itens="\n".join(itens))


def _rfc822(iso):
    try:
        a, m, d = [int(x) for x in iso.split("-")]
        dt = date(a, m, d)
        dias = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        meses = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return "%s, %02d %s %d 08:00:00 -0300" % (dias[dt.weekday()], d, meses[m - 1], a)
    except Exception:
        return ""


# Escrita ---------------------------------------------------------------------------

def grava(caminho, conteudo):
    destino = os.path.join(RAIZ, caminho)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8", newline="\n") as f:
        f.write(conteudo)


def main():
    grava("index.html", pagina_home())
    grava("tratamentos/index.html", pagina_tratamentos())
    for t in dados.TRATAMENTOS:
        grava("tratamentos/%s/index.html" % t["slug"], pagina_tratamento(t))
    grava("dra-adelaine-montel/index.html", pagina_sobre())
    grava("cursos/index.html", pagina_cursos())
    grava("pacientes-de-parauapebas/index.html", pagina_parauapebas())
    grava("blog/index.html", pagina_blog())
    for p in POSTS:
        grava("blog/%s/index.html" % p["slug"], pagina_post(p))
    grava("politica-de-privacidade.html", pagina_privacidade())
    grava("404.html", pagina_404())
    grava("sitemap.xml", sitemap())
    grava("robots.txt", robots())
    grava("llms.txt", llms())
    grava("blog/feed.xml", feed())
    dominio = URL.split("//", 1)[-1].split("/")[0]
    if BASE == "/" and not dominio.endswith("github.io"):
        grava("CNAME", dominio + "\n")
    print("Gerado: %d tratamentos, %d posts, %d URLs no sitemap." % (len(dados.TRATAMENTOS), len(POSTS), len(urls_do_site())))


if __name__ == "__main__":
    main()
