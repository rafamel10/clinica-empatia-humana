# -*- coding: utf-8 -*-
"""Gera o site estático da Empatia Humana.

Uso:  python scripts/gerar.py
Lê os textos de scripts/dados.py e os posts de conteudo/blog/*.md, e escreve os HTML,
sitemap.xml, robots.txt, llms.txt e blog/feed.xml na raiz do repositório.
Nunca edite os HTML gerados à mão: edite dados.py ou os .md e rode de novo.

Visual: identidade da marca (assets/marca/cores.jpg): rosa #FDA1B3, rosa claro #FCCED8,
off-white #F3EEEA e texto #6D6467, com o símbolo da árvore e o lema "de dentro para fora".
"""
import html
import json
import os
import re
import sys
from datetime import date
from urllib.parse import quote

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)
import dados  # noqa: E402

S = dados.SITE
DRA = dados.DRA
BASE = S["base"]
URL = S["url"].rstrip("/")
VERSAO = "5"  # aumente a cada publicação que mudar CSS ou JS
HOJE = S["data_atualizacao"]
TRAT = {t["slug"]: t for t in dados.TRATAMENTOS}
SEM_CUSTO = bool(getattr(dados, "AVALIACAO_SEM_CUSTO", False))
FAQ_HOME = [x for x in dados.FAQ_HOME if SEM_CUSTO or not x[0].startswith("A avaliação é paga")]

try:
    with open(os.path.join(AQUI, "medidas.json"), encoding="utf-8") as _f:
        MEDIDAS = json.load(_f)
except Exception:
    MEDIDAS = {}


def esc(t):
    return html.escape(str(t), quote=True)


def link(caminho=""):
    """Caminho interno com a base do site (funciona no GitHub Pages em subpasta)."""
    return BASE + caminho.lstrip("/")


def absoluto(caminho=""):
    return URL + "/" + caminho.lstrip("/")


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

    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", _lk, t)


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
        with open(os.path.join(pasta, nome), encoding="utf-8") as f:
            bruto = f.read()
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
    posts.sort(key=lambda p: (p.get("data", ""), p.get("ordem", ""), p["slug"]), reverse=True)
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
    "seta": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "seta-diag": '<path d="M7 17L17 7M9 7h8v8"/>',
    "seta-esq": '<path d="M19 12H5M11 6l-6 6 6 6"/>',
    "escudo": '<path d="M12 3l7 3v5c0 5-3.5 8.5-7 10-3.5-1.5-7-5-7-10V6z"/><path d="M9 12l2 2 4-4"/>',
    "folha": '<path d="M5 19c0-8 5-13 14-14-1 9-6 14-14 14z"/><path d="M5 19l7-7"/>',
    "local": '<path d="M12 21s-7-6.2-7-11.5a7 7 0 0 1 14 0C19 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
    "relogio": '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    "coracao": '<path d="M12 20s-7-4.4-7-9.6A4.2 4.2 0 0 1 12 8a4.2 4.2 0 0 1 7 2.4C19 15.6 12 20 12 20z"/>',
    "ouvir": '<path d="M5 11a7 7 0 0 1 14 0v5a2 2 0 0 1-2 2h-1v-6h3M5 11v5a2 2 0 0 0 2 2h1v-6H5"/>',
}


def icone(nome, classe="icone"):
    return '<svg class="%s" viewBox="0 0 24 24" aria-hidden="true" focusable="false">%s</svg>' % (classe, ICONES.get(nome, ""))


SVG_WHATS = '<svg class="icone-whats" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2Zm0 18.2c-1.5 0-3-.4-4.3-1.2l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2Zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8-.2-.1-.4-.1-.6.1l-.8 1c-.1.2-.3.2-.5.1a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.2-.4.7-1.4.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5c-.2 0-.4.1-.7.3-.2.3-.9.9-.9 2.1s.9 2.4 1 2.6c.1.2 1.8 2.8 4.4 3.9 1.6.7 2.3.8 3.1.6.5-.1 1.5-.6 1.7-1.2.2-.6.2-1.1.2-1.2-.1-.2-.3-.2-.6-.4Z"/></svg>'
SVG_INSTA = '<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4.2"/><circle cx="17.4" cy="6.6" r="1.1" fill="currentColor" stroke="none"/></svg>'
SVG_FACE = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13.5 22v-8.2h2.8l.4-3.2h-3.2V8.6c0-.9.3-1.6 1.6-1.6h1.7V4.1c-.3 0-1.3-.1-2.5-.1-2.5 0-4.2 1.5-4.2 4.3v2.3H7.3v3.2h2.8V22h3.4Z"/></svg>'
SVG_GOOGLE = '<svg class="icone-google" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.84z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>'

FOTOS = {  # reserva, caso scripts/medidas.json não exista
    "adelaine-vertical": (900, 1333), "adelaine-vertical-540": (540, 800), "adelaine-retrato": (900, 900), "adelaine-avatar": (160, 160),
    "adelaine-consultorio": (337, 385), "avaliacao-pernas": (512, 380), "clinica-emblema": (512, 285),
    "recepcao": (660, 780), "fachada": (640, 490), "simbolo-rosa": (320, 304), "simbolo-branco": (320, 304),
    "logotipo-rosa": (720, 146), "logotipo-branco": (946, 192), "logo-rosa": (640, 401), "logo-branca": (640, 401),
}


def medida(nome):
    v = MEDIDAS.get(nome) or FOTOS.get(nome) or (1, 1)
    return int(v[0]), int(v[1])


def foto(nome, alt, classe="", lazy=True, prioridade=False):
    """<img> em webp (gerado por scripts/imagens.py)."""
    w, h = medida(nome)
    attrs = 'src="%s" width="%d" height="%d" alt="%s"' % (link("assets/img/%s.webp" % nome), w, h, esc(alt))
    if classe:
        attrs += ' class="%s"' % classe
    if prioridade:
        attrs += ' fetchpriority="high" decoding="async"'
    elif lazy:
        attrs += ' loading="lazy" decoding="async"'
    return "<img %s>" % attrs


# Dados estruturados ----------------------------------------------------------------

def schema_clinica():
    return {
        "@type": ["MedicalClinic", "HealthAndBeautyBusiness"],
        "@id": absoluto("#clinica"),
        "name": S["nome_completo"],
        "alternateName": ["Empatia Humana", "Clínica Empatia Humana"],
        "slogan": dados.SLOGAN,
        "description": "Clínica de estética integrativa e ozonioterapia em Canaã dos Carajás (PA): vasinhos e varizes (PEIM), ozonioterapia para dor, lipo ozonizada, saúde intestinal, limpeza de pele e soroterapia.",
        "url": absoluto(),
        "logo": absoluto("assets/img/logo-empatia-humana.png"),
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


def schema_pessoa():
    conselho4 = {"@type": "Organization", "name": "Conselho Regional de Biomedicina 4ª Região"}
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
        "hasCredential": [
            {"@type": "EducationalOccupationalCredential", "credentialCategory": "Registro profissional", "name": "Biomédica, CRBM 4ª Região nº 1437", "recognizedBy": conselho4},
            {"@type": "EducationalOccupationalCredential", "credentialCategory": "Registro profissional", "name": "Biomédica, CRBM 3ª Região nº 18758", "recognizedBy": {"@type": "Organization", "name": "Conselho Regional de Biomedicina 3ª Região"}},
        ] + [{"@type": "EducationalOccupationalCredential", "credentialCategory": "Habilitação", "name": h, "recognizedBy": conselho4} for h in DRA["habilitacoes"]],
        "sameAs": [S["instagram_dra"]],
    }


def schema_site():
    return {"@type": "WebSite", "@id": absoluto("#site"), "url": absoluto(), "name": S["nome"], "inLanguage": "pt-BR", "publisher": {"@id": absoluto("#clinica")}}


def schema_faq(faq):
    return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]}


def schema_migalhas(itens):
    return {"@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": absoluto(c)} for i, (n, c) in enumerate(itens)]}


def schema_pagina(caminho, nome, tipo="WebPage", extra=None):
    d = {"@type": tipo, "@id": absoluto(caminho + "#pagina"), "url": absoluto(caminho), "name": nome, "isPartOf": {"@id": absoluto("#site")}, "about": {"@id": absoluto("#clinica")}, "inLanguage": "pt-BR", "dateModified": HOJE}
    if extra:
        d.update(extra)
    return d


def jsonld(grafo):
    return '<script type="application/ld+json">%s</script>' % json.dumps({"@context": "https://schema.org", "@graph": grafo}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


# Partes comuns ---------------------------------------------------------------------

FONTES = "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500;1,600&family=Josefin+Sans:wght@400;600&family=Jost:wght@400;500;600&display=swap"


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
  <meta name="theme-color" content="#fda1b3">
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
  <link rel="stylesheet" href="{fontes}">
  <link rel="stylesheet" href="{base}css/site.css?v={v}">
  <script>document.documentElement.classList.add("js");window.EMPATIA_BASE="{base}";</script>
  <script src="{base}js/config.js?v={v}"></script>
  <script src="{base}js/medicao.js?v={v}"></script>
  {ld}{extra}
</head>""".format(canon=("" if robots.startswith("noindex") else '<link rel="canonical" href="%s">' % esc(canonical)),
                  t=esc(titulo), d=esc(descricao), r=robots, c=esc(canonical), tipo=tipo, img=esc(absoluto(imagem)),
                  base=BASE, v=VERSAO, ld=jsonld(grafo), extra=extra, fontes=FONTES)


def rotulo(texto, classe=""):
    return '<p class="rotulo%s">%s</p>' % ((" " + classe) if classe else "", texto)


def botao(texto, origem, interesse="", classe="botao--escuro", href="#agendar", abrir=True, externo=False):
    attrs = 'class="botao %s" href="%s"' % (classe, esc(href))
    if abrir:
        attrs += ' data-abrir-form data-origem="%s"' % origem
        if interesse:
            attrs += ' data-interesse="%s"' % esc(interesse)
    if externo:
        attrs += ' target="_blank" rel="noopener"'
    return '<a %s><span>%s</span><span class="botao__seta" aria-hidden="true">%s</span></a>' % (attrs, texto, icone("seta-diag", "icone icone--seta"))


CTA = "Quero saber valores e horários"


def prova_google(classe="", href=None):
    return '<a class="prova %s" href="%s"><span class="estrelas" aria-hidden="true">★★★★★</span><span><strong>%s no Google</strong> · %d avaliações</span></a>' % (classe, esc(href or link("depoimentos/")), S["nota_google"], S["avaliacoes_google"])


def marca_dagua(classe=""):
    w, h = medida("simbolo-branco")
    return '<img class="marca-dagua %s" src="%s" width="%d" height="%d" alt="" loading="lazy" decoding="async">' % (classe, link("assets/img/simbolo-branco.webp"), w, h)


def cabecalho(atual=""):
    itens_trat = "".join('<li><a href="%s">%s %s</a></li>' % (link("tratamentos/%s/" % t["slug"]), icone(t["icone"], "icone icone--menu"), esc(t["menu"])) for t in dados.TRATAMENTOS)

    def ativo(nome):
        return ' aria-current="page"' if atual == nome else ""

    lw, lh = medida("logotipo-branco")
    return """<a class="pular" href="#conteudo">Pular para o conteúdo</a>
<header class="topo">
  <div class="topo__barra">
    <a class="marca" href="{home}" aria-label="Empatia Humana, página inicial">
      <img class="marca__simbolo" src="{base}assets/img/simbolo-branco.webp" width="46" height="44" alt="">
      <img class="marca__nome" src="{base}assets/img/logotipo-branco.webp" width="{lw}" height="{lh}" alt="Empatia Humana, conceito em estética integrativa">
    </a>
    <button class="menu-botao" type="button" aria-expanded="false" aria-controls="menu">Menu</button>
    <nav class="menu" id="menu" aria-label="Menu principal">
      <ul class="menu__lista">
        <li class="menu__grupo">
          <a href="{trats}"{a_t}>Tratamentos</a>
          <ul class="menu__sub">{itens}</ul>
        </li>
        <li><a href="{clinica}"{a_cl}>A clínica</a></li>
        <li><a href="{sobre}"{a_s}>Dra. Adelaine</a></li>
        <li><a href="{deps}"{a_d}>Depoimentos</a></li>
        <li><a href="{blog}"{a_b}>Blog</a></li>
        <li><a href="{contato}"{a_c}>Contato</a></li>
      </ul>
      {cta}
    </nav>
  </div>
</header>""".format(home=link(), base=BASE, lw=lw, lh=lh, trats=link("tratamentos/"), clinica=link("a-clinica/"), sobre=link("dra-adelaine-montel/"),
                    deps=link("depoimentos/"), blog=link("blog/"), contato=link("contato/"), itens=itens_trat,
                    a_t=ativo("tratamentos"), a_cl=ativo("clinica"), a_s=ativo("sobre"), a_d=ativo("depoimentos"), a_b=ativo("blog"), a_c=ativo("contato"),
                    cta=botao("Valores e horários", "menu", classe="botao--escuro menu__cta"))


def formulario(prefixo, interesse="", titulo="Valores e horários pelo WhatsApp", texto="", texto_botao=CTA, origem="pagina", titulo_tag="h2"):
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
  <button class="botao botao--escuro botao--cheio form-lead__enviar" type="submit">{svg}<span>{b}</span></button>
  <p class="form-lead__prova"><span class="estrelas" aria-hidden="true">★★★★★</span> <strong>5,0 no Google</strong> · {n} avaliações</p>
  <p class="form-lead__nota">Leva 20 segundos e não tem compromisso. Seus dados ficam só com a clínica. <a href="{priv}">Privacidade</a>.</p>
  <div class="form-lead__ok" role="status" hidden><p class="form-lead__ok-titulo">Falta um toque: envie a mensagem que já está escrita.</p><p>Não abriu? <a href="#" data-wa-link target="_blank" rel="noopener">Abrir a conversa com a clínica</a></p></div>
</form>""".format(p=prefixo, i=esc(interesse), o=origem, t=titulo, tt=titulo_tag, tx=texto, b=texto_botao, svg=SVG_WHATS,
                  n=S["avaliacoes_google"], priv=link("politica-de-privacidade.html"))


def rodape():
    trats = "".join('<li><a href="%s">%s</a></li>' % (link("tratamentos/%s/" % t["slug"]), esc(t["menu"])) for t in dados.TRATAMENTOS)
    horas = "".join("<li><span>%s</span> %s</li>" % (esc(a), esc(b)) for a, b in S["horarios"])
    lw, lh = medida("logotipo-branco")
    return """<footer class="rodape">
  {dagua}
  <div class="largura">
    <div class="rodape__topo">
      <div>
        <p class="rodape__titulo">Endereço</p>
        <address>{end}<br>{bairro}, {cidade} ({uf})</address>
        <p><a href="{maps}" target="_blank" rel="noopener">Abrir no Google Maps</a></p>
        <p class="rodape__titulo rodape__titulo--espaco">Horários</p>
        <ul class="rodape__horas">{horas}</ul>
      </div>
      <div>
        <p class="rodape__titulo">Tratamentos</p>
        <ul class="rodape__links">{trats}</ul>
      </div>
      <div>
        <p class="rodape__titulo">A clínica</p>
        <ul class="rodape__links">
          <li><a href="{clinica}">Sobre a Empatia Humana</a></li>
          <li><a href="{sobre}">Dra. Adelaine Montel</a></li>
          <li><a href="{deps}">Depoimentos</a></li>
          <li><a href="{blog}">Blog</a></li>
          <li><a href="{cursos}">Cursos para profissionais</a></li>
          <li><a href="{parau}">Pacientes de Parauapebas</a></li>
          <li><a href="{contato}">Contato</a></li>
        </ul>
      </div>
      <div>
        <p class="rodape__titulo">Fale com a clínica</p>
        <ul class="redes">
          <li><a class="rede" href="#agendar" data-abrir-form data-origem="rodape">{sw}<span>{tel}</span></a></li>
          <li><a class="rede" href="{insta}" target="_blank" rel="noopener">{si}<span>@clinicaempatiahumana</span></a></li>
          <li><a class="rede" href="{insta_d}" target="_blank" rel="noopener">{si}<span>@biomedicaadelaine</span></a></li>
          <li><a class="rede" href="{face}" target="_blank" rel="noopener">{sf}<span>Facebook</span></a></li>
        </ul>
        <p class="rodape__cta">{cta}</p>
      </div>
    </div>
    <img class="rodape__marca" src="{base}assets/img/logotipo-branco.webp" width="{lw}" height="{lh}" alt="Empatia Humana, conceito em estética integrativa" loading="lazy" decoding="async">
    <div class="rodape__legal">
      <p><strong>{dra}</strong>, biomédica esteta e ozonioterapeuta, inscrição nº 1437 no CRBM 4ª Região. Responsável técnica.</p>
      <p>{razao}, CNPJ {cnpj}. Os resultados variam de pessoa para pessoa e as informações deste site não substituem uma avaliação profissional.</p>
      <p><a href="{priv}">Política de privacidade</a> · <a href="#" data-cookies-abrir>Preferências de cookies</a></p>
    </div>
  </div>
</footer>""".format(dagua=marca_dagua("marca-dagua--rodape"), base=BASE, lw=lw, lh=lh, end=esc(S["endereco"]), bairro=S["bairro"], cidade=S["cidade"], uf=S["uf"],
                    maps=esc(S["maps"]), horas=horas, trats=trats, clinica=link("a-clinica/"), sobre=link("dra-adelaine-montel/"), deps=link("depoimentos/"),
                    blog=link("blog/"), cursos=link("cursos/"), parau=link("pacientes-de-parauapebas/"), contato=link("contato/"),
                    sw=SVG_WHATS, tel=S["telefone"], insta=S["instagram_clinica"], insta_d=S["instagram_dra"], face=S["facebook"], si=SVG_INSTA, sf=SVG_FACE,
                    cta=botao(CTA, "rodape_botao", classe="botao--rosa"), dra=DRA["nome_completo"], razao=S["razao"], cnpj=S["cnpj"], priv=link("politica-de-privacidade.html"))


def modal_e_barra(interesse=""):
    return """<dialog class="modal" id="modal-agendar" aria-labelledby="modal-titulo">
  <div class="modal__caixa">
    <button class="modal__fechar" type="button" data-fechar-form aria-label="Fechar">×</button>
    <div class="modal__topo">
      <img src="{base}assets/img/adelaine-avatar.webp" width="64" height="64" alt="" loading="lazy">
      <p>Atendimento com a <strong>Dra. Adelaine Montel</strong><br>Biomédica · CRBM 1437</p>
    </div>
    {form}
  </div>
</dialog>
<div class="barra-fixa" data-barra-fixa>
  <a class="botao botao--escuro botao--cheio" href="#agendar" data-abrir-form data-origem="barra_fixa">{svg}<span>Ver valores e horários</span></a>
</div>
<script src="{base}js/site.js?v={v}" defer></script>""".format(
        base=BASE, v=VERSAO, svg=SVG_WHATS,
        form=formulario("modal", interesse, origem="modal").replace('class="form-lead__titulo"', 'class="form-lead__titulo" id="modal-titulo"'))


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


def cabeca_pagina(migalhas, rot, h1, texto, extra=""):
    return """<section class="cabeca-pagina">
  <div class="largura">
    {mig}
    {rot}
    <h1>{h1}</h1>
    <p class="cabeca-pagina__texto">{texto}</p>
    {extra}
  </div>
</section>""".format(mig=migalhas_html(migalhas), rot=rotulo(rot) if rot else "", h1=h1, texto=texto, extra=extra)


# Blocos de prova social ---------------------------------------------------------------

def lista_avaliacoes(qtd=9, primeiro=None):
    lista = list(dados.GOOGLE)
    if primeiro:
        lista.sort(key=lambda x: (x[0] not in primeiro, primeiro.index(x[0]) if x[0] in primeiro else 0))
    cores = ["", " avatar--b", " avatar--c"]
    return "".join("""<li class="avaliacao">
  <div class="avaliacao__topo"><span class="avatar{c}" aria-hidden="true">{i}</span><span class="avaliacao__quem"><strong>{n}</strong><small>Avaliação no Google</small></span>{g}</div>
  <p class="estrelas" aria-label="5 de 5 estrelas">★★★★★</p>
  <p class="avaliacao__texto">{t}</p>
</li>""".format(c=cores[k % 3], i=esc(n[0]), n=esc(n), t=esc(t), g=SVG_GOOGLE) for k, (n, t) in enumerate(lista[:qtd]))


def bloco_notas(ident, titulo_html, qtd=9, primeiro=None, tag="h2", mostrar_rotulo=True, link_todos=True):
    return """<div class="notas">
  <div class="notas__resumo">
    {rot}
    <{tag}>{titulo}</{tag}>
    <p class="nota-grande"><span class="nota-grande__numero">{nota}</span><span class="nota-grande__lado"><span class="estrelas" aria-hidden="true">★★★★★</span><span>{n} avaliações no Google</span></span></p>
    <div class="carrossel-botoes">
      <button type="button" data-carrossel="anterior" aria-controls="{id}" aria-label="Avaliações anteriores">{esq}</button>
      <button type="button" data-carrossel="proximo" aria-controls="{id}" aria-label="Próximas avaliações">{dir}</button>
    </div>
    {todos}
  </div>
  <ul class="carrossel avaliacoes" id="{id}" tabindex="0" aria-label="Avaliações de pacientes no Google">{itens}</ul>
</div>""".format(rot=rotulo("Depoimentos") if mostrar_rotulo else "", tag=tag, titulo=titulo_html, nota=S["nota_google"], n=S["avaliacoes_google"], id=ident,
                 esq=icone("seta-esq", "icone"), dir=icone("seta", "icone"), itens=lista_avaliacoes(qtd, primeiro),
                 todos=('<a class="link-acao" href="%s">Ver todos os depoimentos</a>' % link("depoimentos/")) if link_todos else "")


def bloco_whats(lista):
    return "".join(
        '<div class="conversa"><p class="conversa__titulo">"%s"</p><div class="conversa__tela"><p class="balao">%s%s</p></div><p class="conversa__nome">%s</p></div>'
        % (esc(w["titulo"]), esc(w["texto"]), ("<time>%s</time>" % w["hora"]) if w["hora"] else "", esc(w["quem"])) for w in lista)


def bloco_video(com_link=False):
    v = dados.DEPOIMENTO_VIDEO
    lk = '<a class="link-acao" href="%s" target="_blank" rel="noopener">Assistir no Instagram</a>' % esc(v["link"]) if com_link else ""
    return """<figure class="relato-video">
  <p class="relato-video__selo">Depoimento em vídeo</p>
  <blockquote><p>"{t}"</p></blockquote>
  <figcaption><span>{q}</span>{lk}</figcaption>
</figure>""".format(t=esc(v["texto"]), q=esc(v["quem"]), lk=lk)


def bloco_relatos(whats):
    return '<div class="relatos">%s%s</div>' % (bloco_video(), bloco_whats(whats))


def faq_html(faq, abrir_primeira=False):
    return '<div class="perguntas">%s</div>' % "".join(
        '<details%s><summary>%s</summary><p>%s</p></details>' % (" open" if (abrir_primeira and i == 0) else "", esc(q), inline(a)) for i, (q, a) in enumerate(faq))


def secao_duvidas(faq, titulo_html, ident="duvidas", classe="secao--creme", abrir_primeira=True, interesse=""):
    return """<section class="secao {classe}" id="{id}" aria-labelledby="{id}-titulo">
  <div class="largura duvidas">
    <div class="duvidas__lado">
      {rot}
      <h2 id="{id}-titulo">{titulo}</h2>
      <p>Não achou a sua? A equipe responde pelo WhatsApp.</p>
      <a class="link-acao" href="#agendar" data-abrir-form data-origem="duvidas"{inter}>Perguntar para a clínica</a>
    </div>
    {faq}
  </div>
</section>""".format(classe=classe, id=ident, rot=rotulo("Dúvidas"), titulo=titulo_html, faq=faq_html(faq, abrir_primeira),
                     inter=(' data-interesse="%s"' % esc(interesse)) if interesse else "")


def card_post(p, tag="h3", destaque=False):
    resumo = p.get("resumo", "")
    limite = 230 if destaque else 150
    return """<li class="card-post{d}" data-categoria="{cat}">
  <a href="{h}">
    <span class="card-post__cat">{c}</span>
    <{tg} class="card-post__titulo">{t}</{tg}>
    <span class="card-post__resumo">{r}</span>
    <span class="card-post__meta">{dt} · {tl} min de leitura</span>
  </a>
</li>""".format(d=" card-post--destaque" if destaque else "", cat=esc(p.get("categoria", "Blog")), h=link("blog/%s/" % p["slug"]), c=esc(p.get("categoria", "Blog")),
                t=esc(p["titulo"]), r=esc(resumo[:limite]) + ("…" if len(resumo) > limite else ""), dt=data_br(p.get("data", "")), tl=p["tempo_leitura"], tg=tag)


def cta_faixa(titulo_html, texto, interesse="", origem="faixa", texto_botao=CTA):
    return """<section class="faixa-cta" aria-label="Agendar avaliação">
  {dagua}
  <div class="largura faixa-cta__grade">
    <div><p class="faixa-cta__titulo">{t}</p><p class="faixa-cta__texto">{x}</p></div>
    {b}
  </div>
</section>""".format(dagua=marca_dagua("marca-dagua--faixa"), t=titulo_html, x=texto, b=botao(texto_botao, origem, interesse, "botao--escuro"))


def jornada(passos, titulo_html, texto, botao_html, rot="Como funciona", aviso=""):
    itens = "".join("<li><h3>%s</h3><p>%s</p></li>" % (esc(a), esc(b)) for a, b in passos)
    return """<div class="jornada">
  <div class="jornada__texto">
    {rot}
    <h2>{titulo}</h2>
    <p>{texto}</p>
    {botao}
  </div>
  <ol class="jornada__passos">{itens}</ol>
  {aviso}
</div>""".format(rot=rotulo(rot, "rotulo--claro"), titulo=titulo_html, texto=texto, botao=botao_html, itens=itens, aviso=aviso)


def bloco_comecar(prefixo, interesse="", origem="comecar", titulo_html="Receba valores e horários <em>no WhatsApp</em>", texto="Preencha e toque em enviar na mensagem que já vai pronta. A equipe responde no horário de atendimento, de segunda a sábado."):
    horas = "".join("<li><span>%s</span> %s</li>" % (esc(a), esc(b)) for a, b in S["horarios"][:2])
    return """<div class="comecar" id="agendar">
  <div class="comecar__form">
    {form}
  </div>
  <div class="comecar__mapa">
    <iframe title="Mapa com a localização da Clínica Empatia Humana em Canaã dos Carajás" src="{embed}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>
    <div class="comecar__cartao">
      <p class="comecar__nome">Empatia Humana</p>
      <address>{end}<br>{bairro}, {cidade} ({uf})</address>
      <ul>{horas}</ul>
      <a class="link-acao" href="{maps}" target="_blank" rel="noopener">Abrir no Google Maps</a>
    </div>
  </div>
</div>""".format(form=formulario(prefixo, interesse, titulo=titulo_html, texto=texto, origem=origem), embed=esc(S["maps_embed"]),
                 end=esc(S["endereco"]), bairro=S["bairro"], cidade=S["cidade"], uf=S["uf"], horas=horas, maps=esc(S["maps"]))


def faixas_html():
    def trilho(palavras):
        um = "".join('<span>%s</span><span class="faixa__estrela">✦</span>' % esc(p) for p in palavras)
        return um * 4
    return """<div class="faixas" aria-hidden="true">
  <div class="faixa faixa--escura"><div class="faixa__trilho">{b}</div></div>
  <div class="faixa faixa--rosa"><div class="faixa__trilho">{a}</div></div>
</div>""".format(a=trilho(dados.FAIXA_1), b=trilho(dados.FAIXA_2))


def bento_tratamentos(tag="h3"):
    t0 = dados.TRATAMENTOS[0]
    cards = ["""<li class="bento__item bento__item--destaque">
  <a href="{h}">
    <span class="bento__foto">{foto}</span>
    <span class="bento__corpo">
      <span class="bento__selo">O mais procurado</span>
      <{tag}>{n}</{tag}>
      <span class="bento__texto">{c}</span>
      <span class="bento__mais">Ver como funciona {seta}</span>
    </span>
  </a>
</li>""".format(h=link("tratamentos/%s/" % t0["slug"]), foto=foto(t0["foto"], t0["foto_alt"]), n=esc(t0["nome"]), c=esc(t0.get("destaque") or t0["card"]),
                tag=tag, seta=icone("seta-diag", "icone icone--seta"))]
    tons = ["bento__item--rosa", "", "", "bento__item--rosa", "bento__item--rosa", ""]
    for k, t in enumerate(dados.TRATAMENTOS[1:]):
        cards.append("""<li class="bento__item {tom}">
  <a href="{h}">
    {ic}
    <{tag}>{n}</{tag}>
    <span class="bento__texto">{c}</span>
    <span class="bento__mais">Ver como funciona {seta}</span>
  </a>
</li>""".format(tom=tons[k % len(tons)], h=link("tratamentos/%s/" % t["slug"]), ic=icone(t["icone"], "icone icone--card"), n=esc(t["nome"]), c=esc(t["card"]),
                tag=tag, seta=icone("seta-diag", "icone icone--seta")))
    cards.append("""<li class="bento__item bento__item--cta">
  <a href="#agendar" data-abrir-form data-origem="card_tratamentos">
    <{tag}>Não sabe por onde começar?</{tag}>
    <span class="bento__texto">Conte o que você sente. A Dra. Adelaine indica o tratamento certo na avaliação.</span>
    <span class="bento__mais">Falar com a clínica {seta}</span>
  </a>
</li>""".format(tag=tag, seta=icone("seta-diag", "icone icone--seta")))
    return '<ul class="bento">%s</ul>' % "".join(cards)


def etiquetas_outros():
    return '<div class="tambem"><p class="tambem__titulo">Também na clínica</p><ul class="etiquetas">%s</ul></div>' % "".join("<li>%s</li>" % esc(o) for o in dados.OUTROS_SERVICOS)


def credenciais_html():
    return '<ul class="credenciais">%s</ul>' % "".join(
        "<li>%s<span><strong>%s</strong>%s</span></li>" % (icone(i, "icone icone--card"), esc(a), esc(b)) for i, a, b in dados.CREDENCIAIS)


def espaco_fotos():
    return '<ul class="espaco__fotos">%s</ul>' % "".join(
        "<li%s>%s<span>%s</span></li>" % ((' class="%s"' % cl) if cl else "", foto(f, alt), esc(leg)) for f, alt, leg, cl in dados.ESPACO)


def horarios_dl():
    return '<dl class="horarios">%s</dl>' % "".join("<div><dt>%s</dt><dd>%s</dd></div>" % (esc(a), esc(b)) for a, b in S["horarios"])


# Páginas ---------------------------------------------------------------------------

def pagina_home():
    ident = "".join('<li><a href="%s"><span>%s</span>%s</a></li>' % (link("tratamentos/%s/" % sl), esc(tx), icone("seta-diag", "icone icone--seta")) for tx, sl in dados.IDENTIFICACAO)
    posts = "".join(card_post(p) for p in POSTS[:3])
    if SEM_CUSTO:
        sub = '<strong>Avaliação sem custo*</strong> com a biomédica Dra. Adelaine Montel, no Centro de <strong>Canaã dos Carajás</strong>. Ela estuda o seu caso antes de indicar qualquer procedimento.'
        nota = "*Para procedimentos como vasinhos, ozonioterapia, lipo ozonizada e pele. Leva 20 segundos e você vai direto para o WhatsApp."
    else:
        sub = 'Com a biomédica Dra. Adelaine Montel, no Centro de <strong>Canaã dos Carajás</strong>. Ela estuda o seu caso antes de indicar qualquer procedimento.'
        nota = "Leva 20 segundos e você vai direto para o WhatsApp."

    corpo = """
<section class="hero hero--home" aria-labelledby="hero-titulo">
  <div class="largura hero__grade">
    <div class="hero__texto">
      {rot_hero}
      <h1 id="hero-titulo">Vasinhos, dor e gordura localizada tratados <em>de dentro para fora</em></h1>
      <p class="hero__sub">{sub}</p>
      <div class="hero__acoes">
        {cta_hero}
        <a class="link-acao" href="#tratamentos">Conhecer os tratamentos</a>
      </div>
      <p class="hero__nota">{nota}</p>
      {prova}
    </div>
    <div class="hero__visual">
      <div class="hero__arco">{foto_hero}</div>
      <p class="etiqueta etiqueta--a">Avaliação individual</p>
      <p class="etiqueta etiqueta--b">Biomédica · CRBM 1437</p>
      <p class="etiqueta etiqueta--c">Centro · Canaã dos Carajás</p>
      <div class="selo-giratorio" aria-hidden="true">
        <svg viewBox="0 0 200 200" focusable="false"><defs><path id="selo-circ" d="M100,100 m-80,0 a80,80 0 1,1 160,0 a80,80 0 1,1 -160,0"/></defs><text><textPath href="#selo-circ" textLength="496" lengthAdjust="spacing">TRATANDO DE DENTRO PARA FORA ✦ EMPATIA HUMANA ✦</textPath></text></svg>
        <img src="{base}assets/img/simbolo-rosa.webp" width="76" height="72" alt="">
      </div>
    </div>
  </div>
</section>

{faixas}

<section class="secao secao--escura para-quem" aria-labelledby="quem-titulo">
  {dagua}
  <div class="largura para-quem__grade">
    <div>
      {rot_quem}
      <h2 id="quem-titulo">É para você <em>se…</em></h2>
      <p class="para-quem__dica">Toque no seu caso e veja como é o tratamento.</p>
      <ul class="lista-linhas">{ident}</ul>
      <p class="para-quem__fecho">Na Empatia Humana, o incômodo de fora é tratado junto com a causa de dentro.</p>
      {cta_quem}
    </div>
    <figure class="para-quem__foto">{foto_quem}</figure>
  </div>
</section>

<section class="secao secao--branca" id="depoimentos" aria-labelledby="dep-titulo">
  <div class="largura">
    {notas}
    {relatos}
    <p class="centro">{cta_dep}</p>
  </div>
</section>

<section class="secao secao--creme" id="tratamentos" aria-labelledby="trat-titulo">
  <div class="largura">
    <div class="cabeca cabeca--dupla">
      <div>{rot_trat}<h2 id="trat-titulo">O que você quer <em>tratar</em>?</h2></div>
      <p>Todo tratamento começa por uma avaliação com a Dra. Adelaine. Escolha o que mais incomoda você e veja como funciona.</p>
    </div>
    {bento}
    {outros}
  </div>
</section>

<section class="secao secao--branca" aria-labelledby="jornada-titulo">
  <div class="largura">
    {jornada}
  </div>
</section>

<section class="secao secao--creme" id="dra-adelaine" aria-labelledby="dra-titulo">
  <div class="largura">
    <div class="cuida">
      <figure class="cuida__foto">{foto_dra}</figure>
      <div class="cuida__texto">
        {rot_dra}
        <h2 id="dra-titulo">Antes do procedimento, alguém que <em>estuda o seu caso</em></h2>
        <p class="cuida__nome">Dra. Adelaine Montel <span>Biomédica esteta e ozonioterapeuta</span></p>
        <p>Em 2015, Adelaine recebeu o diagnóstico de lúpus. Foi como paciente que ela conheceu a ozonioterapia e sentiu a diferença: menos dor, menos crises, mais disposição.</p>
        <p>Depois de anos em laboratório de análises clínicas, ela uniu a biomedicina, a nutrição ortomolecular e a ozonioterapia num jeito de atender que olha para o corpo inteiro.</p>
        <blockquote class="citacao"><p>{frase}</p></blockquote>
        <a class="link-acao" href="{sobre}">Conhecer a trajetória da Dra. Adelaine</a>
      </div>
    </div>
    {credenciais}
  </div>
</section>

<section class="secao secao--branca espaco" aria-labelledby="espaco-titulo">
  <div class="largura">
    {espaco}
    <div class="cabeca cabeca--dupla cabeca--baixo">
      <h2 id="espaco-titulo">Um espaço pensado para você se sentir <em>acolhida</em></h2>
      <div>
        <p>A clínica fica no Centro de Canaã dos Carajás. Recepção aconchegante e atendimento com horário marcado, do jeito que as pacientes contam nas avaliações.</p>
        <a class="link-acao" href="{clinica}">Conhecer a clínica</a>
      </div>
    </div>
  </div>
</section>

{duvidas}

<section class="secao secao--rosa-claro" aria-label="Agendar avaliação">
  <div class="largura">
    {comecar}
  </div>
</section>

<section class="secao secao--branca" aria-labelledby="blog-titulo">
  <div class="largura">
    <div class="cabeca cabeca--dupla">
      <div>{rot_blog}<h2 id="blog-titulo">Para entender antes de <em>decidir</em></h2></div>
      <div><p>Explicações claras sobre os tratamentos, escritas para quem pesquisa antes de marcar.</p><a class="link-acao" href="{blog}">Ver todos os posts</a></div>
    </div>
    <ul class="cards-post">{posts}</ul>
  </div>
</section>

{faixa}
""".format(
        base=BASE,
        rot_hero=rotulo('<span class="so-desktop">Clínica de estética integrativa · Canaã dos Carajás</span><span class="so-celular">Estética integrativa em Canaã</span>'),
        sub=sub, nota=nota, cta_hero=botao(CTA, "hero"), prova=prova_google(href="#depoimentos"),
        foto_hero=foto("adelaine-vertical", "Dra. Adelaine Montel, biomédica esteta, sorrindo na Clínica Empatia Humana", lazy=False, prioridade=True),
        faixas=faixas_html(), dagua=marca_dagua("marca-dagua--secao"),
        rot_quem=rotulo("Para quem é", "rotulo--claro"), ident=ident, cta_quem=botao(CTA, "para_quem", classe="botao--rosa"),
        foto_quem=foto("avaliacao-pernas", "Dra. Adelaine Montel examinando as pernas de uma paciente"),
        notas=bloco_notas("avaliacoes-home", 'Quem passou pela clínica <em>conta</em>', primeiro=["Aurora F.", "Marcos Z.", "Juliane A.", "Fernandes S."]).replace("<h2>", '<h2 id="dep-titulo">', 1),
        relatos=bloco_relatos(dados.WHATSAPP[:2]), cta_dep=botao(CTA, "depoimentos"),
        rot_trat=rotulo("Tratamentos"), bento=bento_tratamentos(), outros=etiquetas_outros(),
        jornada=jornada(dados.PASSOS, 'Do primeiro contato ao <em>seu plano</em>', "Um caminho simples, sem pressão para fechar nada no primeiro dia. Se o tratamento não for para você, a Dra. Adelaine diz.", botao(CTA, "jornada", classe="botao--rosa")).replace("<h2>", '<h2 id="jornada-titulo">', 1),
        foto_dra=foto("adelaine-retrato", "Retrato da Dra. Adelaine Montel"), rot_dra=rotulo("Quem cuida de você"),
        frase=esc(DRA["frase"]), sobre=link("dra-adelaine-montel/"), credenciais=credenciais_html(),
        espaco=espaco_fotos(), clinica=link("a-clinica/"),
        duvidas=secao_duvidas(FAQ_HOME, 'Perguntas que <em>sempre aparecem</em>').replace("Muitas pacientes vêm de Parauapebas", 'Muitas pacientes vêm de <a href="%s">Parauapebas</a>' % link("pacientes-de-parauapebas/"), 1),
        comecar=bloco_comecar("home"),
        rot_blog=rotulo("Blog"), blog=link("blog/"), posts=posts,
        faixa=cta_faixa('As avaliações são feitas pela própria <em>Dra. Adelaine</em>', "Com horário marcado, de segunda a sábado. Peça os horários desta semana.", "", "faixa_home"),
    )
    grafo = [schema_clinica(), schema_pessoa(), schema_site(), schema_faq(FAQ_HOME),
             schema_pagina("", "Clínica de estética integrativa em Canaã dos Carajás")]
    h = head("Clínica de estética em Canaã dos Carajás | Empatia Humana",
             "Ozonioterapia, tratamento de vasinhos (PEIM), lipo ozonizada, saúde intestinal e limpeza de pele em Canaã dos Carajás (PA), com a Dra. Adelaine Montel.",
             "", grafo)
    return pagina(h, corpo, data_pagina="inicio")


def pagina_tratamento(t):
    caminho = "tratamentos/%s/" % t["slug"]
    chips = "".join("<li>%s</li>" % esc(c) for c in t["chips"])
    ident = "".join("<p>%s</p>" % esc(p) for p in t["ident"])
    benef = "".join("<li>%s</li>" % esc(b) for b in t["beneficios"])
    sinais = "".join("<li>%s</li>" % esc(s) for s in t["sinais"])
    inclui = "".join("<li>%s</li>" % esc(i) for i in t["inclui"])
    outros = "".join('<li><a href="%s">%s %s</a></li>' % (link("tratamentos/%s/" % o["slug"]), icone(o["icone"], "icone icone--menu"), esc(o["nome"])) for o in dados.TRATAMENTOS if o["slug"] != t["slug"])
    posts_rel = [POST[s] for s in t.get("posts", []) if s in POST]
    posts_rel += [p for p in POSTS if p.get("tratamento") == t["slug"] and p not in posts_rel]
    if not posts_rel:
        posts_rel = POSTS[:2]
    posts_html = "".join(card_post(p) for p in posts_rel[:3])
    faq_t = list(t["faq"]) + list(dados.FAQ_TRATAMENTO_COMUM)

    relatos = ""
    whats = [w for w in dados.WHATSAPP if t.get("depoimento_whats") and w["tratamento"] == t["depoimento_whats"]]
    if t.get("depoimento_video"):
        relatos = bloco_relatos(whats or dados.WHATSAPP[1:3])
    elif whats:
        relatos = '<div class="relatos relatos--so-whats">%s</div>' % bloco_whats(whats + [w for w in dados.WHATSAPP if w not in whats][:1])

    aviso = '<p class="aviso">%s<span>%s</span></p>' % (icone("escudo", "icone icone--aviso"), esc(t["aviso"])) if t.get("aviso") else ""
    retrato = medida(t["foto"])[1] > medida(t["foto"])[0]

    corpo = """
<section class="hero hero--trat" aria-labelledby="hero-titulo">
  <div class="largura hero__grade">
    <div class="hero__texto">
      {migalhas}
      <h1 id="hero-titulo">{h1}</h1>
      <p class="hero__frase">{sub}</p>
      <p class="hero__destaque">{destaque}</p>
      <ul class="chips">{chips}</ul>
      {prova}
      <figure class="hero__dra">
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

<section class="secao secao--creme" aria-labelledby="ident-titulo">
  <div class="largura ident">
    <div class="ident__texto">
      {rot_ident}
      <h2 id="ident-titulo">{ident_titulo}</h2>
      {ident}
      <p class="ident__virada">{reframe}</p>
    </div>
    <figure class="ident__foto{foto_classe}">{foto}</figure>
  </div>
</section>

<section class="secao secao--branca" aria-labelledby="prova-titulo">
  <div class="largura">
    {notas}
    {relatos}
  </div>
</section>

<section class="secao secao--creme" aria-labelledby="oque-titulo">
  <div class="largura oque">
    <div>
      {rot_oque}
      <h2 id="oque-titulo">{oque_titulo}</h2>
      <p class="oque__intro">{oque_intro}</p>
      <ul class="lista-check beneficios">{benef}</ul>
    </div>
    <div class="cartao-inclui">
      <p class="cartao-inclui__titulo">Na Empatia Humana</p>
      <ul class="lista-check lista-check--clara">{inclui}</ul>
      {cta_inclui}
    </div>
  </div>
</section>

<section class="secao secao--branca" aria-labelledby="como-titulo">
  <div class="largura">
    {jornada}
  </div>
</section>

{duvidas}

<section class="secao secao--rosa-claro sinais-bloco" aria-labelledby="sinais-titulo">
  <div class="largura">
    <h2 id="sinais-titulo" class="centro">Quando é hora de <em>procurar</em>?</h2>
    <ul class="sinais">{sinais}</ul>
    <div class="ganho">
      <p class="ganho__titulo">{ganho_titulo}</p>
      <p>{ganho}</p>
      {cta_ganho}
    </div>
  </div>
</section>

<section class="secao secao--creme" aria-labelledby="mais-titulo">
  <div class="largura">
    <div class="cabeca"><h2 id="mais-titulo">Para ler antes da <em>avaliação</em></h2></div>
    <ul class="cards-post">{posts}</ul>
    <h2 class="outros__titulo">Outros tratamentos</h2>
    <ul class="outros">{outros}</ul>
  </div>
</section>

{faixa}
""".format(
        migalhas=migalhas_html([("Início", ""), ("Tratamentos", "tratamentos/"), (t["nome"], caminho)]),
        h1=esc(t["h1"]), sub=esc(t["sub"]), destaque=esc(t.get("destaque") or t["card"]), chips=chips, prova=prova_google(href="#prova-titulo"),
        foto_dra=foto("adelaine-avatar", "Dra. Adelaine Montel", "hero__dra-img"), sobre=link("dra-adelaine-montel/"),
        form=formulario("hero", t["interesse"], origem="hero"),
        resumo=esc(dados.RESUMOS.get(t["slug"], t["card"])),
        rot_ident=rotulo("Você se reconhece?"), ident_titulo=esc(t["ident_titulo"]), ident=ident, reframe=esc(t["reframe"]),
        foto=foto(t["foto"], t["foto_alt"]), foto_classe=" ident__foto--retrato" if retrato else "",
        notas=bloco_notas("avaliacoes-trat", 'Quem já passou <em>por aqui</em>', 6, primeiro=["Aurora F.", "Juliane A.", "Marcos Z."]).replace("<h2>", '<h2 id="prova-titulo">', 1),
        relatos=relatos,
        rot_oque=rotulo("O tratamento"), oque_titulo=esc(t["oque_titulo"]), oque_intro=esc(t["oque_intro"]), benef=benef, inclui=inclui,
        cta_inclui=botao(CTA, "inclui", t["interesse"], "botao--rosa"),
        jornada=jornada(t["como"], 'Como é o tratamento, <em>passo a passo</em>', "Você sabe o que vai acontecer em cada etapa, antes de começar.", botao(CTA, "passos", t["interesse"], "botao--rosa"), rot="Passo a passo", aviso=aviso).replace("<h2>", '<h2 id="como-titulo">', 1),
        duvidas=secao_duvidas(faq_t, "Perguntas sobre <em>%s</em>" % esc(t["nome"].lower()), ident="faq", classe="secao--creme", interesse=t["interesse"]),
        sinais=sinais, ganho_titulo=esc(t["ganho_titulo"]), ganho=esc(t["ganho"]), cta_ganho=botao(CTA, "ganho", t["interesse"]),
        posts=posts_html, outros=outros,
        faixa=cta_faixa(esc(t["ganho_titulo"]), "Comece pela avaliação com a Dra. Adelaine Montel, em Canaã dos Carajás.", t["interesse"], "faixa_final"),
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
    corpo = """
{cabeca}
<section class="secao secao--creme">
  <div class="largura">
    {bento}
    {outros}
  </div>
</section>
<section class="secao secao--branca">
  <div class="largura">
    {jornada}
  </div>
</section>
{faixa}
""".format(cabeca=cabeca_pagina([("Início", ""), ("Tratamentos", caminho)], "Tratamentos", 'Tratamentos de estética integrativa em <em>Canaã dos Carajás</em>',
                                "Dor, vasinhos, gordura localizada, pele, intestino e disposição. Escolha o que mais incomoda você para ver como é o tratamento, o que esperar e as respostas para as dúvidas mais comuns."),
           bento=bento_tratamentos("h2"), outros=etiquetas_outros(),
           jornada=jornada(dados.PASSOS, 'Do primeiro contato ao <em>seu plano</em>', "Um caminho simples, sem pressão para fechar nada no primeiro dia.", botao(CTA, "jornada", classe="botao--rosa")),
           faixa=cta_faixa("Não sabe por onde começar?", "Conte o que você sente. A Dra. Adelaine indica o tratamento certo na avaliação.", "", "faixa_hub"))
    grafo = [schema_pagina(caminho, "Tratamentos da Clínica Empatia Humana", "CollectionPage", {
        "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": absoluto("tratamentos/%s/" % t["slug"]), "name": t["nome"]} for i, t in enumerate(dados.TRATAMENTOS)]}}),
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
      {rot}
      <h1>Dra. Adelaine Montel, <em>biomédica esteta</em> em Canaã dos Carajás</h1>
      <p class="cabeca-pagina__texto">Responsável técnica da Clínica Empatia Humana. Mais de 18 anos de formada, inscrição nº 1437 no CRBM 4ª Região desde 2011 e uma história com a ozonioterapia que começou como paciente.</p>
      <div class="hero__acoes">{cta}</div>
      {prova}
    </div>
    <figure class="dra-topo__foto"><div class="hero__arco">{foto}</div></figure>
  </div>
</section>

<section class="secao secao--branca">
  <div class="largura estreita texto-longo">
    <h2>Por que a <em>estética integrativa</em></h2>
    <p>Em 2015, Adelaine Barros Montel recebeu o diagnóstico de lúpus, uma doença autoimune que trouxe momentos muito difíceis. Durante essa jornada, ela conheceu a ozonioterapia e, com o tempo, percebeu mudanças importantes na qualidade de vida: menos dor, menos crises inflamatórias, mais energia e disposição.</p>
    <p>Quando precisou deixar o laboratório de análises clínicas, onde atuava como biomédica, encontrou na estética integrativa uma forma de continuar cuidando de pessoas. Uniu a experiência com exames laboratoriais, a nutrição ortomolecular e a ozonioterapia num atendimento que olha para o ser humano por inteiro.</p>
    <blockquote class="citacao"><p>{frase}</p></blockquote>
    <h2>Como ela atende</h2>
    <p>Antes de indicar qualquer procedimento, ela estuda o caso: na consulta integrativa, cada paciente recebe por escrito o mapeamento do que foi encontrado e o plano proposto.</p>
    <h2>Formação</h2>
    <ul class="lista-check">{formacao}</ul>
    <h2>Além do consultório</h2>
    <p>A fé é um dos pilares da sua vida, ao lado da família: o marido, Lídio Rocha, e a filha, Maria Luiza. Ela também forma outros profissionais da saúde e da estética em <a href="{cursos}">cursos presenciais em Canaã dos Carajás</a>.</p>
  </div>
</section>

<section class="secao secao--creme">
  <div class="largura">
    {credenciais}
    <div class="registro">
      <div class="registro__texto">
        <h2>Registro conferido no <em>Conselho de Biomedicina</em></h2>
        <p>Adelaine Barros Montel tem inscrição ativa nº 1437 no CRBM 4ª Região (Pará), requerida em 2011, e também é inscrita no CRBM 3ª Região (nº 18758). É a responsável técnica da Clínica Empatia Humana.</p>
        <a class="link-acao" href="{cfbm}" target="_blank" rel="noopener">Conferir na consulta pública do CFBM</a>
      </div>
      <dl class="registro__habilitacoes"><dt>Habilitações registradas</dt>{habil}</dl>
    </div>
  </div>
</section>

<section class="secao secao--branca">
  <div class="largura">
    {notas}
  </div>
</section>
{faixa}
""".format(mig=migalhas_html([("Início", ""), ("Dra. Adelaine Montel", caminho)]), rot=rotulo("Quem cuida de você"), cta=botao(CTA, "sobre_topo"), prova=prova_google(),
           foto=foto("adelaine-vertical", "Dra. Adelaine Montel, biomédica esteta, sorrindo", lazy=False, prioridade=True),
           frase=esc(DRA["frase"]), formacao=formacao, cursos=link("cursos/"), credenciais=credenciais_html(), cfbm=esc(DRA["consulta_cfbm"]), habil=habil,
           notas=bloco_notas("avaliacoes-dra", 'O que os pacientes <em>dizem</em>', 9),
           faixa=cta_faixa("Quer ser atendida pela Dra. Adelaine?", "Deixe seu contato e continue a conversa no WhatsApp da clínica.", "", "faixa_sobre"))
    grafo = [schema_pagina(caminho, "Dra. Adelaine Montel", "ProfilePage", {"mainEntity": {"@id": absoluto(caminho + "#pessoa")}}),
             schema_pessoa(), schema_clinica(), schema_site(), schema_migalhas([("Início", ""), ("Dra. Adelaine Montel", caminho)])]
    h = head("Dra. Adelaine Montel, biomédica em Canaã dos Carajás",
             "Conheça a Dra. Adelaine Barros Montel: biomédica esteta e ozonioterapeuta, CRBM 4ª Região nº 1437, responsável pela Clínica Empatia Humana em Canaã dos Carajás.",
             caminho, grafo, tipo="profile")
    return pagina(h, corpo, atual="sobre", data_pagina="sobre")


def pagina_clinica():
    caminho = "a-clinica/"
    c = dados.CLINICA
    conceito = "".join("<p>%s</p>" % esc(p) for p in c["conceito"])
    valores = "".join("<li><h3>%s</h3><p>%s</p></li>" % (esc(a), esc(b)) for a, b in c["valores"])
    trats = "".join('<li><a href="%s">%s %s</a></li>' % (link("tratamentos/%s/" % t["slug"]), icone(t["icone"], "icone icone--menu"), esc(t["nome"])) for t in dados.TRATAMENTOS)
    corpo = """
{cabeca}
<section class="secao secao--branca" aria-labelledby="conceito-titulo">
  <div class="largura ident">
    <div class="ident__texto texto-corrido">
      {rot_conceito}
      <h2 id="conceito-titulo">Tratar de <em>dentro para fora</em></h2>
      {conceito}
    </div>
    <figure class="ident__foto ident__foto--logo"><img src="{base}assets/img/logo-rosa.webp" width="{lw}" height="{lh}" alt="Logo da Empatia Humana: árvore formada por dois rostos, conceito em estética integrativa" loading="lazy" decoding="async"></figure>
  </div>
</section>

<section class="secao secao--creme" aria-labelledby="valores-titulo">
  <div class="largura">
    <div class="cabeca"><h2 id="valores-titulo">O que você encontra <em>aqui</em></h2></div>
    <ul class="valores">{valores}</ul>
    <h3 class="outros__titulo">Tratamentos da clínica</h3>
    <ul class="outros">{trats}</ul>
  </div>
</section>

<section class="secao secao--branca espaco" aria-labelledby="espaco-titulo">
  <div class="largura">
    {espaco}
    <div class="cabeca cabeca--dupla cabeca--baixo">
      <h2 id="espaco-titulo">O espaço, no <em>Centro de Canaã</em></h2>
      <div>
        <p>{end}, {bairro}. Recepção aconchegante e atendimento com horário marcado, para você não esperar.</p>
        <a class="link-acao" href="{contato}">Ver endereço, mapa e horários</a>
      </div>
    </div>
  </div>
</section>

<section class="secao secao--creme" aria-labelledby="quem-titulo">
  <div class="largura">
    <div class="cuida">
      <figure class="cuida__foto">{foto_dra}</figure>
      <div class="cuida__texto">
        {rot_dra}
        <h2 id="quem-titulo">Dra. Adelaine Montel, <em>à frente da clínica</em></h2>
        <p>Biomédica esteta e ozonioterapeuta, com inscrição ativa no CRBM desde 2011. Ela atende pessoalmente as avaliações e também forma outros profissionais nos <a href="{cursos}">cursos da clínica</a>.</p>
        <a class="link-acao" href="{sobre}">Conhecer a Dra. Adelaine</a>
      </div>
    </div>
    {credenciais}
  </div>
</section>

<section class="secao secao--branca">
  <div class="largura">
    {notas}
  </div>
</section>

{duvidas}
{faixa}
""".format(cabeca=cabeca_pagina([("Início", ""), ("A clínica", caminho)], "A clínica", 'Empatia Humana: estética integrativa em <em>Canaã dos Carajás</em>',
                                "Uma clínica que cuida da aparência olhando para o corpo inteiro, no Centro da cidade.", '<div class="hero__acoes">%s</div>%s' % (botao(CTA, "clinica_topo"), prova_google())),
           base=BASE, lw=medida("logo-rosa")[0], lh=medida("logo-rosa")[1], rot_conceito=rotulo("Nosso conceito"), conceito=conceito, valores=valores, trats=trats,
           espaco=espaco_fotos(), end=esc(S["endereco"]), bairro=S["bairro"], contato=link("contato/"),
           foto_dra=foto("adelaine-retrato", "Retrato da Dra. Adelaine Montel"), rot_dra=rotulo("Quem cuida de você"), cursos=link("cursos/"), sobre=link("dra-adelaine-montel/"),
           credenciais=credenciais_html(), notas=bloco_notas("avaliacoes-clinica", 'O que dizem da <em>clínica</em>', 9, primeiro=["Gisele R.", "Mayra L.", "Daiane S."]),
           duvidas=secao_duvidas(c["faq"], 'Sobre a <em>Empatia Humana</em>', classe="secao--creme"),
           faixa=cta_faixa("Venha conhecer a clínica", "Deixe seu contato e marque sua avaliação pelo WhatsApp.", "", "faixa_clinica"))
    grafo = [schema_pagina(caminho, "A Clínica Empatia Humana", "AboutPage"), schema_clinica(), schema_pessoa(), schema_site(), schema_faq(c["faq"]),
             schema_migalhas([("Início", ""), ("A clínica", caminho)])]
    h = head("Clínica Empatia Humana em Canaã dos Carajás: quem somos",
             "Conheça a Empatia Humana, clínica de estética integrativa e ozonioterapia no Centro de Canaã dos Carajás (PA): conceito, espaço, equipe e tratamentos.",
             caminho, grafo)
    return pagina(h, corpo, atual="clinica", data_pagina="clinica")


def pagina_depoimentos():
    caminho = "depoimentos/"
    corpo = """
{cabeca}
<section class="secao secao--branca" aria-labelledby="google-titulo">
  <div class="largura">
    <div class="destaque-video">{video}</div>
    <div class="cabeca cabeca--dupla">
      <h2 id="google-titulo">Avaliações no <em>Google</em></h2>
      <p class="nota-grande"><span class="nota-grande__numero">{nota}</span><span class="nota-grande__lado"><span class="estrelas" aria-hidden="true">★★★★★</span><span>{n} avaliações no Google</span></span></p>
    </div>
    <ul class="avaliacoes avaliacoes--grade">{itens}</ul>
    <p class="centro"><a class="link-acao" href="{maps}" target="_blank" rel="noopener">Ver todas as avaliações no Google</a></p>
  </div>
</section>

<section class="secao secao--creme" aria-labelledby="relatos-titulo">
  <div class="largura">
    <div class="cabeca"><h2 id="relatos-titulo">Relatos que chegam pelo <em>WhatsApp</em></h2><p>Mensagens que os pacientes mandaram para a clínica e que foram publicadas nos destaques do Instagram.</p></div>
    <div class="relatos relatos--grade">{whats}</div>
    <p class="aviso-relatos">Relatos pessoais. Os resultados variam de pessoa para pessoa.</p>
  </div>
</section>
{faixa}
""".format(cabeca=cabeca_pagina([("Início", ""), ("Depoimentos", caminho)], "Depoimentos", 'O que dizem os pacientes da <em>Empatia Humana</em>',
                                "Avaliações públicas no Google e relatos que os pacientes mandaram para a clínica em Canaã dos Carajás."),
           nota=S["nota_google"], n=S["avaliacoes_google"], itens=lista_avaliacoes(len(dados.GOOGLE)), maps=esc(S["maps"]),
           video=bloco_video(com_link=True), whats=bloco_whats(dados.WHATSAPP),
           faixa=cta_faixa("Quer saber se o seu caso tem tratamento?", "Comece pela avaliação com a Dra. Adelaine Montel.", "", "faixa_depoimentos"))
    grafo = [schema_pagina(caminho, "Depoimentos de pacientes da Empatia Humana"), schema_clinica(), schema_site(), schema_migalhas([("Início", ""), ("Depoimentos", caminho)])]
    h = head("Depoimentos de pacientes | Empatia Humana, Canaã dos Carajás",
             "Veja avaliações no Google e relatos de pacientes da Clínica Empatia Humana, em Canaã dos Carajás (PA): ozonioterapia, vasinhos, pele e estética integrativa.",
             caminho, grafo)
    return pagina(h, corpo, atual="depoimentos", data_pagina="depoimentos")


def pagina_contato():
    caminho = "contato/"
    corpo = """
{cabeca}
<section class="secao secao--rosa-claro">
  <div class="largura">
    {comecar}
  </div>
</section>
<section class="secao secao--branca" aria-labelledby="onde-titulo">
  <div class="largura onde">
    <div>
      <h2 id="onde-titulo">Onde fica a <em>clínica</em></h2>
      <address class="onde__endereco">{end}<br>{bairro}, {cidade} ({uf})</address>
      {horarios}
      <p class="onde__nota">Atendimento com horário marcado. Recebemos pacientes de Canaã, <a href="{parau}">Parauapebas</a>, Curionópolis e região.</p>
      <p class="onde__nota">{maps_botao}</p>
    </div>
    <ul class="canais">
      <li>{sw}<span><strong>WhatsApp · {tel}</strong><a href="#agendar" data-abrir-form data-origem="contato_whats">Chamar no WhatsApp</a></span></li>
      <li>{si}<span><strong>Instagram da clínica</strong><a href="{insta}" target="_blank" rel="noopener">@clinicaempatiahumana</a></span></li>
      <li>{si}<span><strong>Instagram da Dra. Adelaine</strong><a href="{insta_d}" target="_blank" rel="noopener">@biomedicaadelaine</a></span></li>
      <li>{sf}<span><strong>Facebook</strong><a href="{face}" target="_blank" rel="noopener">facebook.com/empatiahumana</a></span></li>
    </ul>
  </div>
</section>
<section class="secao secao--creme espaco">
  <div class="largura">
    {espaco}
  </div>
</section>
""".format(cabeca=cabeca_pagina([("Início", ""), ("Contato", caminho)], "Contato", 'Fale com a Empatia Humana em <em>Canaã dos Carajás</em>',
                                "Tire suas dúvidas, peça valores e marque sua avaliação pelo WhatsApp. A clínica fica no Centro, na Rua Círio de Nazaré, 558."),
           comecar=bloco_comecar("contato", origem="contato"), end=esc(S["endereco"]), bairro=S["bairro"], cidade=S["cidade"], uf=S["uf"], horarios=horarios_dl(),
           parau=link("pacientes-de-parauapebas/"), maps_botao='<a class="link-acao" href="%s" target="_blank" rel="noopener">Abrir no Google Maps</a>' % esc(S["maps"]),
           sw=SVG_WHATS, si=SVG_INSTA, sf=SVG_FACE, tel=S["telefone"], insta=S["instagram_clinica"], insta_d=S["instagram_dra"], face=S["facebook"], espaco=espaco_fotos())
    grafo = [schema_pagina(caminho, "Contato da Clínica Empatia Humana", "ContactPage"), schema_clinica(), schema_site(), schema_migalhas([("Início", ""), ("Contato", caminho)])]
    h = head("Contato e endereço | Empatia Humana, Canaã dos Carajás",
             "Endereço, WhatsApp, horários e mapa da Clínica Empatia Humana: Rua Círio de Nazaré, 558, Centro, Canaã dos Carajás (PA). Atendimento de segunda a sábado.",
             caminho, grafo)
    return pagina(h, corpo, atual="contato", data_pagina="contato")


def pagina_cursos():
    caminho = "cursos/"
    cursos = "".join("<li><h2>%s</h2><p>%s</p>%s</li>" % (esc(c["nome"]), esc(c["texto"]), ('<a class="link-acao" href="%s" target="_blank" rel="noopener">Inscrever-se na lista</a>' % esc(c["link"])) if c.get("link") else "") for c in dados.CURSOS)
    corpo = """
{cabeca}
<section class="secao secao--branca">
  <div class="largura cursos-grade">
    <ul class="cursos">{cursos}</ul>
    <div class="cartao-form" id="agendar">{form}</div>
  </div>
</section>
""".format(cabeca=cabeca_pagina([("Início", ""), ("Cursos", caminho)], "Para profissionais", 'Cursos para profissionais da saúde e da estética em <em>Canaã dos Carajás</em>',
                                "Turmas presenciais com a Dra. Adelaine Montel, biomédica com formação em análises clínicas, nutrição ortomolecular e ozonioterapia. Aulas teóricas e práticas, estudo de casos e certificado."),
           cursos=cursos,
           form=formulario("cursos", "cursos para profissionais", titulo="Quero saber das próximas turmas", texto="Deixe seus dados e receba as datas e condições pelo WhatsApp.", texto_botao="Quero saber das turmas", origem="cursos"))
    grafo = [schema_pagina(caminho, "Cursos para profissionais")]
    grafo += [{"@type": "Course", "name": c["nome"], "description": c["texto"], "inLanguage": "pt-BR", "provider": {"@id": absoluto("#clinica")}} for c in dados.CURSOS]
    grafo += [schema_clinica(), schema_site(), schema_migalhas([("Início", ""), ("Cursos", caminho)])]
    h = head("Cursos de ozonioterapia em Canaã dos Carajás",
             "Cursos presenciais com a Dra. Adelaine Montel em Canaã dos Carajás: interpretação de exames laboratoriais, ozonioterapia na dor crônica e limpeza de pele.",
             caminho, grafo)
    return pagina(h, corpo, interesse="cursos para profissionais", data_pagina="cursos")


def pagina_parauapebas():
    caminho = "pacientes-de-parauapebas/"
    trats = "".join('<li><a href="%s">%s %s</a></li>' % (link("tratamentos/%s/" % t["slug"]), icone(t["icone"], "icone icone--menu"), esc(t["nome"])) for t in dados.TRATAMENTOS)
    faq = dados.PARAUAPEBAS["faq"]
    inter = "avaliação (venho de Parauapebas)"
    corpo = """
{cabeca}
<section class="secao secao--branca">
  <div class="largura onde">
    <div>
      <h2>Vale a viagem até <em>Canaã</em>?</h2>
      <p class="onde__nota">Na Empatia Humana, cada caso é estudado antes de qualquer indicação. Quem vem de fora avisa no WhatsApp e a equipe organiza a agenda para aproveitar a viagem, inclusive aos sábados de manhã.</p>
      <ul class="lista-check">
        <li>Avaliação com a própria Dra. Adelaine, biomédica com inscrição ativa no CRBM desde 2011</li>
        <li>Agenda pensada para quem viaja: avaliação e sessão no mesmo dia, quando o caso permite</li>
        <li>Atendimento aos sábados, das 8h às 12h</li>
      </ul>
      <h2 class="onde__subtitulo">Como chegar</h2>
      <address class="onde__endereco">{end}<br>{bairro}, {cidade} ({uf})</address>
      {horarios}
      <div class="hero__acoes">{maps_botao}</div>
    </div>
    <div class="onde__mapa">{foto}<iframe title="Mapa da Clínica Empatia Humana em Canaã dos Carajás" src="{embed}" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe></div>
  </div>
</section>
<section class="secao secao--creme">
  <div class="largura">
    <div class="cabeca"><h2>Tratamentos que pacientes de Parauapebas <em>procuram</em></h2></div>
    <ul class="outros">{trats}</ul>
  </div>
</section>
<section class="secao secao--branca">
  <div class="largura">
    {notas}
  </div>
</section>
{duvidas}
{faixa}
""".format(cabeca=cabeca_pagina([("Início", ""), ("Pacientes de Parauapebas", caminho)], "Para quem vem de fora", 'Clínica de estética para quem é de <em>Parauapebas</em>',
                                "Pacientes de Parauapebas, Curionópolis e região fazem ozonioterapia, tratamento de vasinhos, lipo ozonizada e cuidados de pele e intestino na Empatia Humana, no Centro de Canaã dos Carajás.",
                                '<div class="hero__acoes">%s</div>' % botao(CTA, "parauapebas_topo", inter)),
           end=esc(S["endereco"]), bairro=S["bairro"], cidade=S["cidade"], uf=S["uf"], horarios=horarios_dl(),
           maps_botao=botao("Abrir no Google Maps", "", href=S["maps"], abrir=False, externo=True),
           foto=foto("fachada", "Fachada da Clínica Empatia Humana em Canaã dos Carajás"), embed=esc(S["maps_embed"]), trats=trats,
           notas=bloco_notas("avaliacoes-parauapebas", 'Quem já veio <em>conta</em>', 6),
           duvidas=secao_duvidas(faq, 'Dúvidas de quem vem de <em>Parauapebas</em>', interesse=inter),
           faixa=cta_faixa("Vem de Parauapebas?", "Avise no WhatsApp: a equipe organiza sua agenda para aproveitar a viagem.", inter, "faixa_parauapebas"))
    grafo = [schema_pagina(caminho, "Clínica de estética para quem é de Parauapebas"), schema_clinica(), schema_site(), schema_faq(faq),
             schema_migalhas([("Início", ""), ("Pacientes de Parauapebas", caminho)])]
    h = head("Clínica de estética para pacientes de Parauapebas",
             "Pacientes de Parauapebas fazem ozonioterapia, tratamento de vasinhos e lipo ozonizada na Empatia Humana, em Canaã dos Carajás. Atendimento aos sábados.",
             caminho, grafo)
    return pagina(h, corpo, interesse=inter, data_pagina="cidade")


def pagina_blog():
    caminho = "blog/"
    cats = sorted(set(p.get("categoria", "Blog") for p in POSTS))
    filtros = '<li><button type="button" class="filtro" data-filtro="" aria-pressed="true">Todos</button></li>' + "".join('<li><button type="button" class="filtro" data-filtro="%s" aria-pressed="false">%s</button></li>' % (esc(c), esc(c)) for c in cats)
    cards = "".join(card_post(p, "h2", destaque=(i == 0)) for i, p in enumerate(POSTS))
    corpo = """
{cabeca}
<section class="secao secao--branca">
  <div class="largura">
    <ul class="filtros" aria-label="Filtrar por tema">{filtros}</ul>
    <ul class="cards-post cards-post--blog">{cards}</ul>
  </div>
</section>
{faixa}
""".format(cabeca=cabeca_pagina([("Início", ""), ("Blog", caminho)], "Blog", 'Blog da <em>Dra. Adelaine Montel</em>',
                                "Ozonioterapia, vasinhos, saúde intestinal, pele e estética integrativa explicados de forma simples, por quem atende em Canaã dos Carajás."),
           filtros=filtros, cards=cards,
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
    relacionados.sort(key=lambda x: (x.get("categoria") != p.get("categoria"), x.get("tratamento") != p.get("tratamento")))
    rel = "".join(card_post(x) for x in relacionados[:3])
    cta_trat = ""
    if t:
        cta_trat = """<aside class="cta-post" aria-label="Tratamento relacionado">
  {ic}
  <div>
    <p class="cta-post__titulo">{h1}</p>
    <p>{sub}</p>
    <p class="cta-post__acoes">{b}<a class="link-acao" href="{h}">Ver como é o tratamento</a></p>
  </div>
</aside>""".format(ic=icone(t["icone"], "icone icone--card"), h1=esc(t["h1"]), sub=esc(t["sub"]), b=botao(CTA, "post_meio", interesse, "botao--rosa"), h=link("tratamentos/%s/" % t["slug"]))
    faq = ""
    if p["faq"]:
        faq = '<section class="post__faq" aria-labelledby="faq-post"><h2 id="faq-post">Perguntas frequentes</h2>%s</section>' % faq_html(p["faq"])
    lateral_trats = "".join('<li><a href="%s">%s %s</a></li>' % (link("tratamentos/%s/" % o["slug"]), icone(o["icone"], "icone icone--menu"), esc(o["nome"])) for o in dados.TRATAMENTOS)

    # o botão do tratamento entra depois do 2º subtítulo
    corpo_post = p["html"]
    partes = corpo_post.split("<h2 ")
    if len(partes) > 3 and cta_trat:
        corpo_post = "<h2 ".join(partes[:3]) + cta_trat + "<h2 " + "<h2 ".join(partes[3:])
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
        <div><p class="autor-box__nome">Dra. Adelaine Barros Montel</p><p>Biomédica esteta e ozonioterapeuta, inscrição nº 1437 no CRBM 4ª Região, responsável técnica da Clínica Empatia Humana em Canaã dos Carajás. Pós-graduada em Nutrição Ortomolecular, com mais de 18 anos de formada.</p><a class="link-acao" href="{sobre}">Conhecer a Dra. Adelaine</a></div>
      </aside>
      <p class="post__aviso">Este conteúdo é informativo e não substitui uma avaliação individual.</p>
    </div>
    <aside class="post__lateral" aria-label="Agendamento e tratamentos">
      <div class="lateral-cartao">
        <p class="lateral-cartao__titulo">Valores e horários pelo WhatsApp</p>
        <p>Com a Dra. Adelaine Montel, no Centro de Canaã dos Carajás.</p>
        {b_lateral}
      </div>
      <div class="lateral-lista"><p class="lateral-lista__titulo">Tratamentos</p><ul>{lateral_trats}</ul></div>
    </aside>
  </div>
</article>
<section class="secao secao--creme" aria-labelledby="rel-titulo">
  <div class="largura">
    <div class="cabeca"><h2 id="rel-titulo">Continue <em>lendo</em></h2></div>
    <ul class="cards-post">{rel}</ul>
  </div>
</section>
{faixa}
""".format(mig=migalhas_html([("Início", ""), ("Blog", "blog/"), (p["titulo"], caminho)]), cat=esc(p.get("categoria", "Blog")), titulo=esc(p["titulo"]),
           base=BASE, sobre=link("dra-adelaine-montel/"), data=data_br(p.get("data", "")), tl=p["tempo_leitura"], resumo=inline(p.get("resumo", "")),
           toc_html=('<nav class="indice-post" aria-label="Neste post"><p class="indice-post__titulo">Neste post</p><ol>%s</ol></nav>' % toc) if len(p["toc"]) > 2 else "",
           html=corpo_post, cta_fim=cta_fim, faq=faq, b_lateral=botao("Quero saber", "post_lateral", interesse, "botao--rosa"), lateral_trats=lateral_trats, rel=rel,
           faixa=cta_faixa("Quer conversar sobre o seu caso?", "A equipe passa valores e horários pelo WhatsApp.", interesse, "faixa_post"))
    grafo = [
        {"@type": "BlogPosting", "@id": absoluto(caminho + "#post"), "headline": p["titulo"], "description": p.get("descricao", ""), "abstract": p.get("resumo", ""),
         "url": absoluto(caminho), "mainEntityOfPage": absoluto(caminho),
         "datePublished": p.get("data", HOJE) + "T08:00:00-03:00", "dateModified": p.get("atualizado", p.get("data", HOJE)) + "T08:00:00-03:00",
         "inLanguage": "pt-BR", "articleSection": p.get("categoria", "Blog"), "wordCount": p["palavras"],
         "image": absoluto("assets/img/og-empatia.jpg"), "author": {"@id": absoluto("dra-adelaine-montel/#pessoa")}, "publisher": {"@id": absoluto("#clinica")},
         "isPartOf": {"@id": absoluto("blog/#blog")}},
        schema_pessoa(), schema_clinica(), schema_site(),
        schema_migalhas([("Início", ""), ("Blog", "blog/"), (p["titulo"], caminho)]),
    ]
    if t:
        grafo[0]["about"] = {"@id": absoluto("tratamentos/%s/#servico" % t["slug"])}
    if p["faq"]:
        grafo.append(schema_faq(p["faq"]))
    titulo_seo = p.get("seo_title") or (p["titulo"] + " | Empatia Humana" if len(p["titulo"]) <= 43 else p["titulo"])
    h = head(titulo_seo, p.get("descricao", p.get("resumo", "")), caminho, grafo, tipo="article",
             extra='\n  <meta property="article:published_time" content="%sT08:00:00-03:00">\n  <meta property="article:author" content="Dra. Adelaine Montel">' % p.get("data", HOJE))
    return pagina(h, corpo, atual="blog", interesse=interesse, data_pagina="post", data_trat=(t["slug"] if t else ""))


def pagina_privacidade():
    corpo = """
<section class="cabeca-pagina"><div class="largura estreita"><h1>Política de privacidade</h1><p class="cabeca-pagina__texto">Atualizada em novembro de 2026.</p></div></section>
<section class="secao secao--branca"><div class="largura estreita texto-longo">
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
<section class="cabeca-pagina"><div class="largura estreita"><h1>Esta página <em>não existe mais</em></h1><p class="cabeca-pagina__texto">Talvez o endereço tenha mudado. Veja os tratamentos da clínica ou fale com a equipe.</p>
<div class="hero__acoes">{b}</div></div></section>""".format(b=botao("Ver os tratamentos", "", href=link("tratamentos/"), abrir=False))
    h = head("Página não encontrada | Empatia Humana", "Página não encontrada.", "404.html", [schema_site()], robots="noindex, follow")
    return pagina(h, corpo, data_pagina="404")


# Arquivos de SEO e IA --------------------------------------------------------------

def urls_do_site():
    u = [("", "1.0"), ("tratamentos/", "0.9")]
    u += [("tratamentos/%s/" % t["slug"], "0.9") for t in dados.TRATAMENTOS]
    u += [("a-clinica/", "0.8"), ("dra-adelaine-montel/", "0.8"), ("depoimentos/", "0.7"), ("contato/", "0.7"),
          ("pacientes-de-parauapebas/", "0.7"), ("blog/", "0.8"), ("cursos/", "0.6")]
    u += [("blog/%s/" % p["slug"], "0.7") for p in POSTS]
    return u


def sitemap():
    linhas = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for c, pr in urls_do_site():
        lm = HOJE
        if c.startswith("blog/") and c != "blog/":
            pp = POST[c.split("/")[1]]
            lm = pp.get("atualizado", pp.get("data", HOJE))
        linhas.append("  <url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>" % (esc(absoluto(c)), lm, pr))
    linhas.append("</urlset>")
    return "\n".join(linhas) + "\n"


def robots():
    return ("User-agent: *\nAllow: /\n\n# Buscadores com IA são bem-vindos a ler e citar o site\n"
            "User-agent: GPTBot\nAllow: /\nUser-agent: OAI-SearchBot\nAllow: /\nUser-agent: ChatGPT-User\nAllow: /\n"
            "User-agent: PerplexityBot\nAllow: /\nUser-agent: ClaudeBot\nAllow: /\nUser-agent: Google-Extended\nAllow: /\n\nSitemap: %s\n" % absoluto("sitemap.xml"))


def llms():
    l = ["# Clínica Empatia Humana", "",
         "> Clínica de estética integrativa e ozonioterapia em Canaã dos Carajás (PA), Brasil. Lema: \"%s\". Responsável técnica: Dra. Adelaine Barros Montel, biomédica esteta e ozonioterapeuta, inscrição nº 1437 no CRBM 4ª Região desde 2011. Nota 5,0 no Google em %d avaliações (conferido em %s)." % (dados.SLOGAN, S["avaliacoes_google"], S["avaliacoes_conferidas_em"]), "",
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
         "- [Sobre a clínica](%s) · [Contato](%s) · [Depoimentos](%s)" % (absoluto("a-clinica/"), absoluto("contato/"), absoluto("depoimentos/")),
         "", "## Tratamentos"]
    for t in dados.TRATAMENTOS:
        l.append("- [%s](%s): %s" % (t["nome"], absoluto("tratamentos/%s/" % t["slug"]), dados.RESUMOS.get(t["slug"], t["card"])))
    l += ["", "## Sobre a Dra. Adelaine Montel", "- [Trajetória, formação e registro](%s)" % absoluto("dra-adelaine-montel/"), "", "## Blog"]
    for p in POSTS:
        l.append("- [%s](%s): %s" % (p["titulo"], absoluto("blog/%s/" % p["slug"]), p.get("resumo", "")))
    l += ["", "## Cursos", "- [Cursos para profissionais](%s): %s" % (absoluto("cursos/"), "; ".join(c["nome"] for c in dados.CURSOS))]
    l += ["", "## Perguntas frequentes"]
    for q, a in FAQ_HOME:
        l.append("- **%s** %s" % (q, a))
    l += ["", "## Pacientes de outras cidades", "- [Pacientes de Parauapebas](%s)" % absoluto("pacientes-de-parauapebas/"), ""]
    return "\n".join(l)


def _rfc822(iso):
    try:
        a, m, d = [int(x) for x in iso.split("-")]
        dt = date(a, m, d)
        dias = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        meses = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        return "%s, %02d %s %d 08:00:00 -0300" % (dias[dt.weekday()], d, meses[m - 1], a)
    except Exception:
        return ""


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
    grava("a-clinica/index.html", pagina_clinica())
    grava("dra-adelaine-montel/index.html", pagina_sobre())
    grava("depoimentos/index.html", pagina_depoimentos())
    grava("contato/index.html", pagina_contato())
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
