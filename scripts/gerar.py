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
VERSAO = "10"  # aumente a cada publicação que mudar CSS ou JS
HOJE = S["data_atualizacao"]
TRAT = {t["slug"]: t for t in dados.TRATAMENTOS}
SEM_CUSTO = bool(getattr(dados, "AVALIACAO_SEM_CUSTO", False))
FAQ_HOME = [x for x in dados.FAQ_HOME if SEM_CUSTO or not x[0].startswith("A avaliação é paga")]

try:
    with open(os.path.join(AQUI, "medidas.json"), encoding="utf-8") as _f:
        MEDIDAS = json.load(_f)
except Exception:
    MEDIDAS = {}

# Configuração central (dados/config.json): WhatsApp, telefone, link de agendamento e medição
with open(os.path.join(AQUI, "..", "dados", "config.json"), encoding="utf-8") as _f:
    CONFIG = json.load(_f)
S["whatsapp"] = "".join(c for c in CONFIG["whatsapp"] if c.isdigit())
S["telefone"] = CONFIG["telefone"]
S["endereco"] = CONFIG.get("endereco") or "[ENDEREÇO]"
S["bairro"] = CONFIG.get("bairro", S["bairro"])
S["horarios"] = [tuple(x) for x in CONFIG["horarios"]]
HORARIO_TXT = CONFIG["horario_texto"]
PAGAMENTO = CONFIG["pagamento"]


def _carregar(sub):
    pasta = os.path.join(RAIZ, "dados", sub)
    out = {}
    for f in sorted(os.listdir(pasta)):
        if f.endswith(".json"):
            with open(os.path.join(pasta, f), encoding="utf-8") as _f:
                out[f[:-5]] = json.load(_f)
    return out


SERV = _carregar("servicos")          # páginas de serviço (template único)
PAGS = _carregar("paginas")           # frentes, programas, spa, cursos, equipe, contato, loja, home, guia
FRENTES = PAGS["frentes"]["frentes"]
FRENTE = {f["slug"]: f for f in FRENTES}
PROG = PAGS["programas-spa-cursos"]["programas"]
SPA = PAGS["programas-spa-cursos"]["spa"]
EQUIPE = PAGS["equipe-contato"]["equipe"]
HOME = PAGS["home"]
GUIA = PAGS["guia"]
GUIA_CAMINHO = "guia-cuidados-pos-procedimento/"
LOJA = PAGS["loja"]
PAI = {f["slug"]: (f["nome"], f["slug"] + "/") for f in FRENTES}
PAI.update({"programas-e-desafios": ("Programas e desafios", "programas-e-desafios/"), "spa-e-bem-estar": ("Spa e bem-estar", "spa/")})
ICONE_FRENTE = {"emagrecimento-e-medidas": "cintura", "pele-e-rejuvenescimento": "rosto", "pernas-e-circulacao": "perna", "saude-integrativa": "folha"}


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
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
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
        "description": "Clínica de estética integrativa e ozonioterapia em Canaã dos Carajás (PA), com biomédicas: emagrecimento e medidas, pele e rejuvenescimento, pernas e circulação e saúde integrativa.",
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
            {"@type": "OpeningHoursSpecification", "dayOfWeek": CONFIG["horario_schema"]["dias"], "opens": CONFIG["horario_schema"]["abre"], "closes": CONFIG["horario_schema"]["fecha"]},
        ],
        "paymentAccepted": "PIX, cartão de crédito",
        "founder": {"@id": absoluto("dra-adelaine-montel/#pessoa")},
        "employee": [{"@id": absoluto("dra-adelaine-montel/#pessoa")}, {"@type": "Person", "name": "Dra. Adriana Montel", "jobTitle": "Biomédica esteta e ozonioterapeuta"}],
        "sameAs": [S["instagram_clinica"], S["facebook"], S["maps_cid"]],
        "availableService": [{"@id": absoluto("tratamentos/%s/#servico" % sl)} for sl in SERV],
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


CTA = "Agendar minha avaliação"


def link_agendar(mensagem):
    """Destino dos botões de agendar: a agenda online, se configurada; senão, o WhatsApp com a mensagem da página."""
    if CONFIG.get("agendamento_url"):
        return CONFIG["agendamento_url"]
    from urllib.parse import quote
    return "https://wa.me/%s?text=%s" % (S["whatsapp"], quote(mensagem, safe=""))


def botao_agendar(texto, origem, mensagem, classe="botao--escuro"):
    return '<a class="botao %s" href="%s" data-agendar data-origem="%s" target="_blank" rel="noopener"><span>%s</span><span class="botao__seta" aria-hidden="true">%s</span></a>' % (
        classe, esc(link_agendar(mensagem)), origem, texto, icone("seta-diag", "icone icone--seta"))


def config_js():
    return """// Arquivo GERADO a partir de dados/config.json. Não edite aqui: mude lá e rode python scripts/gerar.py
window.EMPATIA = %s;
""" % json.dumps({
        "planilhaUrl": CONFIG.get("planilha_url", ""),
        "whatsapp": S["whatsapp"],
        "agendamentoUrl": CONFIG.get("agendamento_url", ""),
        "emailObrigatorio": bool(CONFIG.get("email_obrigatorio", True)),
        "gtmId": CONFIG.get("gtm_id", ""),
        "pixelId": CONFIG.get("pixel_id", ""),
        "cookies": CONFIG.get("cookies", "aviso"),
    }, ensure_ascii=False, indent=2)


def prova_google(classe="", href=None):
    return '<a class="prova %s" href="%s"><span class="estrelas" aria-hidden="true">★★★★★</span><span><strong>%s no Google</strong> · %d avaliações</span></a>' % (classe, esc(href or link("depoimentos/")), S["nota_google"], S["avaliacoes_google"])


def marca_dagua(classe=""):
    w, h = medida("simbolo-branco")
    return '<img class="marca-dagua %s" src="%s" width="%d" height="%d" alt="" loading="lazy" decoding="async">' % (classe, link("assets/img/simbolo-branco.webp"), w, h)


def faixa_campanha():
    fc = CONFIG.get("faixa_campanha") or {}
    if not fc.get("ativa"):
        return ""
    return '<a class="faixa-campanha" href="%s" data-origem="faixa_campanha"><strong>%s</strong><span>%s</span>%s</a>' % (
        link(fc["link"]), esc(fc["texto"]), esc(fc["chamada"]), icone("seta", "icone"))


def cabecalho(atual=""):
    itens_trat = "".join('<li><a href="%s">%s %s</a></li>' % (link(f["slug"] + "/"), icone(ICONE_FRENTE.get(f["slug"], "folha"), "icone icone--menu"), esc(f["nome"])) for f in FRENTES)
    itens_trat += '<li><a href="%s">%s Todos os tratamentos</a></li>' % (link("tratamentos/"), icone("seta", "icone icone--menu"))

    def ativo(nome):
        return ' aria-current="page"' if atual == nome else ""

    lw, lh = medida("nome-branco")
    return """<a class="pular" href="#conteudo">Pular para o conteúdo</a>
{faixa}
<header class="topo">
  <div class="topo__barra">
    <a class="marca" href="{home}" aria-label="Empatia Humana, página inicial">
      <img class="marca__simbolo" src="{base}assets/img/simbolo-branco.webp" width="46" height="44" alt="">
      <img class="marca__nome" src="{base}assets/img/nome-branco.webp" width="{lw}" height="{lh}" alt="Empatia Humana, conceito em estética integrativa">
    </a>
    <button class="menu-botao" type="button" aria-expanded="false" aria-controls="menu">Menu</button>
    <nav class="menu" id="menu" aria-label="Menu principal">
      <ul class="menu__lista">
        <li class="menu__grupo">
          <a href="{trats}"{a_t}>Tratamentos</a>
          <ul class="menu__sub">{itens}</ul>
        </li>
        <li><a href="{prog}"{a_p}>Programas</a></li>
        <li><a href="{spa}"{a_s}>Spa</a></li>
        <li><a href="{equipe}"{a_e}>Equipe</a></li>
        <li><a href="{loja}"{a_l}>Loja</a></li>
        <li><a href="{contato}"{a_c}>Contato</a></li>
      </ul>
      {cta}
    </nav>
  </div>
</header>""".format(faixa=faixa_campanha(), home=link(), base=BASE, lw=lw, lh=lh, trats=link("tratamentos/"), prog=link("programas-e-desafios/"), spa=link("spa/"),
                    equipe=link("equipe/"), loja=link("loja/"), contato=link("contato/"), itens=itens_trat,
                    a_t=ativo("tratamentos"), a_p=ativo("programas"), a_s=ativo("spa"), a_e=ativo("equipe"), a_l=ativo("loja"), a_c=ativo("contato"),
                    cta=botao("Agendar avaliação", "menu", classe="botao--escuro menu__cta"))


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
    trats = "".join('<li><a href="%s">%s</a></li>' % (link(f["slug"] + "/"), esc(f["nome"])) for f in FRENTES)
    trats += "".join('<li><a href="%s">%s</a></li>' % (link(c), n) for c, n in (("programas-e-desafios/", "Programas e desafios"), ("spa/", "Spa e vale-presente"), ("loja/", "Loja e home care"), ("tratamentos/", "Todos os tratamentos")))
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
          <li><a href="{equipe}">Equipe</a></li>
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
    <p class="rodape__lema">{lema}</p>
    <div class="rodape__legal">
      <p><strong>{dra}</strong>, biomédica esteta e ozonioterapeuta, inscrição nº 1437 no CRBM 4ª Região. Responsável técnica.</p>
      <p>{razao}, CNPJ {cnpj}. Os resultados variam de pessoa para pessoa e as informações deste site não substituem uma avaliação profissional.</p>
      <p><a href="{priv}">Política de privacidade</a> · <a href="#" data-cookies-abrir>Preferências de cookies</a></p>
    </div>
  </div>
</footer>""".format(dagua=marca_dagua("marca-dagua--rodape"), lema=esc(dados.SLOGAN), base=BASE, lw=lw, lh=lh, end=esc(S["endereco"]), bairro=S["bairro"], cidade=S["cidade"], uf=S["uf"],
                    maps=esc(S["maps"]), horas=horas, trats=trats, equipe=link("equipe/"), clinica=link("a-clinica/"), sobre=link("dra-adelaine-montel/"), deps=link("depoimentos/"),
                    blog=link("blog/"), cursos=link("cursos/"), parau=link("pacientes-de-parauapebas/"), contato=link("contato/"),
                    sw=SVG_WHATS, tel=S["telefone"], insta=S["instagram_clinica"], insta_d=S["instagram_dra"], face=S["facebook"], si=SVG_INSTA, sf=SVG_FACE,
                    cta=botao(CTA, "rodape_botao", classe="botao--rosa"), dra=DRA["nome_completo"], razao=S["razao"], cnpj=S["cnpj"], priv=link("politica-de-privacidade.html"))


def mensagem_whats(interesse=""):
    if interesse:
        return "Olá! Vim pelo site e quero saber sobre %s." % interesse
    return dados.HERO["whatsapp_msg"]


def modal_e_barra(interesse=""):
    return """<div class="barra-fixa barra-fixa--visivel" data-barra-fixa>
  <a class="botao botao--escuro botao--cheio" href="{href}" data-agendar data-origem="barra_fixa" target="_blank" rel="noopener">{svg}<span>Agendar pelo WhatsApp</span></a>
</div>
<script src="{base}js/site.js?v={v}" defer></script>""".format(base=BASE, v=VERSAO, svg=SVG_WHATS, href=esc(link_agendar(mensagem_whats(interesse))))


def links_diretos(html, interesse=""):
    """Todo botão que abria a janela do formulário vira link direto de agendamento (WhatsApp com a mensagem da página)."""
    import re

    def sub(m):
        inter = m.group(3) or interesse
        return 'href="%s" data-agendar data-origem="%s" target="_blank" rel="noopener"' % (esc(link_agendar(mensagem_whats(inter))), m.group(1))
    return re.sub(r'href="#agendar" data-abrir-form data-origem="([^"]*)"( data-interesse="([^"]*)")?', sub, html)


def pagina(head_html, corpo, atual="", interesse="", data_pagina="", data_trat=""):
    return links_diretos(("%s\n<body data-pagina=\"%s\" data-tratamento=\"%s\">\n%s\n<main id=\"conteudo\">\n%s\n</main>\n%s\n%s\n</body>\n</html>\n" % (
        head_html, data_pagina, data_trat, cabecalho(atual), corpo, rodape(), modal_e_barra(interesse))).replace(link("tratamentos/saude-intestinal/"), link("tratamentos/disbiose-zero/")), interesse)


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

def faq_home():
    end = "%s, %s, %s (%s)" % (S["endereco"], S["bairro"], S["cidade"], S["uf"])
    return [(x["p"], x["r"].replace("{horario}", HORARIO_TXT).replace("{endereco}", end)) for x in HOME["faq"]]


def formulario_guia(prefixo, origem):
    G = GUIA["bloco"]
    return """<form class="form-lead form-guia" data-form-lead data-guia="{destino}" data-origem="{o}" data-interesse="Guia de cuidados pós-procedimento" novalidate>
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
    <label for="{p}-email">E-mail</label>
    <input id="{p}-email" name="email" type="email" inputmode="email" autocomplete="email" enterkeyhint="send" placeholder="voce@email.com" maxlength="120" required aria-describedby="{p}-email-erro" data-clarity-mask="true">
    <p class="campo__erro" id="{p}-email-erro" aria-live="polite" hidden></p>
  </div>
  <div class="campo-isca" aria-hidden="true"><label for="{p}-site">Não preencha</label><input id="{p}-site" name="site" type="text" tabindex="-1" autocomplete="off"></div>
  <button class="botao botao--escuro botao--cheio form-lead__enviar" type="submit"><span>{b}</span></button>
  <p class="form-lead__nota">{priv} <a href="{lp}">Política de privacidade</a>.</p>
  <div class="form-lead__ok" role="status" hidden><p class="form-lead__ok-titulo">{ok}</p><p><a href="{destino}" data-wa-link>Abrir o guia</a></p></div>
</form>""".format(p=prefixo, o=origem, destino=link(GUIA_CAMINHO), b=esc(G["botao"]), ok=esc(G["sucesso"]),
                  priv=esc(G["privacidade"].replace(" Veja a política de privacidade.", "")), lp=link("politica-de-privacidade.html"))


def bloco_guia(prefixo="guia", origem="guia", classe="secao--rosa-claro"):
    G = GUIA["bloco"]
    return """<section class="secao {classe}" id="guia" aria-labelledby="{p}-titulo">
  <div class="largura guia">
    <div class="guia__texto">
      {rot}
      <h2 id="{p}-titulo">{t}</h2>
      <p>{x}</p>
      {itens}
    </div>
    <div class="guia__form">{form}</div>
  </div>
</section>""".format(classe=classe, p=prefixo, rot=rotulo("Material gratuito"), t=esc(G["titulo"]), x=esc(G["texto"]),
                     itens=lista_check(G["itens"]), form=formulario_guia(prefixo, origem))


def bloco_consulta():
    C = HOME["consulta"]
    cards = "".join("""<li class="compara__item{d}">
  <p class="compara__nome">{n}</p>
  <p class="compara__dados"><span>{dur}</span><strong>{pr}</strong></p>
  <p>{para}</p>
</li>""".format(d=" compara__item--destaque" if i else "", n=esc(x["nome"]), dur=esc(x["duracao"]), pr=esc(x["preco"][:1].upper() + x["preco"][1:]), para=esc(x["para"]))
        for i, x in enumerate(C["comparacao"]) if SEM_CUSTO or "gratuita" not in x["preco"])
    return """<section class="secao secao--branca" aria-labelledby="consulta-titulo">
  <div class="largura">
    <div class="cabeca cabeca--dupla">
      <div>{rot}<h2 id="consulta-titulo">{t}</h2></div>
      <p>{x}</p>
    </div>
    <ul class="compara">{cards}</ul>
    <div class="hero__acoes centro-bloco">{b}<a class="link-acao" href="{l}">{lt}</a></div>
  </div>
</section>""".format(rot=rotulo("Por onde começar"), t=esc(C["titulo"]), x=esc(C["texto"]), cards=cards,
                     b=botao_agendar(C["cta"], "home_consulta", C["whatsapp_msg"]), l=link(C["link"].strip("/") + "/"), lt=esc(C["link_texto"]))


def bloco_final(origem="final"):
    F = HOME["cta_final"]
    horas = "".join("<li><span>%s</span> %s</li>" % (esc(a), esc(b)) for a, b in S["horarios"][:2])
    return """<div class="comecar" id="agendar">
  <div class="comecar__form final">
    {rot}
    <h2 id="final-titulo">{t}</h2>
    <p>{x}</p>
    {b}
    {pag}
    <p class="final__tel">Prefere ligar? <a href="tel:+{wa}">{tel}</a></p>
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
</div>""".format(rot=rotulo("Agendar"), t=esc(F["titulo"]), x=esc(F["texto"]), b=botao_agendar(F["cta"], origem, dados.HERO["whatsapp_msg"]), pag=pagamento_html(),
                 wa=S["whatsapp"], tel=S["telefone"], embed=esc(S["maps_embed"]), end=esc(S["endereco"]), bairro=S["bairro"], cidade=S["cidade"], uf=S["uf"], horas=horas, maps=esc(S["maps"]))


def pagina_home():
    posts = "".join(card_post(p) for p in POSTS[:3])
    H = dados.HERO
    prova_itens = [x for x in H["microprova"] if SEM_CUSTO or "gratuita" not in x.lower()]
    microprova = '<ul class="microprova">%s</ul>' % "".join("<li>%s<span>%s</span></li>" % (icone("check"), esc(x)) for x in prova_itens)
    nota = '<p class="hero__nota">%s</p>' % esc(H["nota"]) if SEM_CUSTO else ""
    O, CC, EQ, PR, PG, LJ = HOME["objetivos"], HOME["carros_chefe"], HOME["equipe"], HOME["prova"], HOME["programas"], HOME["loja"]
    faq = faq_home()

    corpo = """
<section class="hero hero--home" aria-labelledby="hero-titulo">
  <div class="largura hero__grade">
    <div class="hero__texto">
      {rot_hero}
      <h1 id="hero-titulo">{h1}</h1>
      <p class="hero__sub">{sub}</p>
      <div class="hero__acoes">
        {cta_hero}
        {cta2_hero}
      </div>
      {microprova}
      {nota}
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

<section class="secao secao--creme" id="tratamentos" aria-labelledby="trat-titulo">
  <div class="largura">
    <div class="cabeca cabeca--dupla">
      <div>{rot_trat}<h2 id="trat-titulo">O que você quer <em>cuidar</em>?</h2></div>
      <p>{o_sub}</p>
    </div>
    {bento}
    <h3 class="subtitulo-secao">{cc_t}</h3>
    <p class="texto-intro">{cc_sub}</p>
    {outros}
    <p class="centro"><a class="link-acao" href="{todos}">Ver todos os tratamentos</a></p>
  </div>
</section>

{consulta}

<section class="secao secao--creme" id="dra-adelaine" aria-labelledby="dra-titulo">
  <div class="largura">
    <div class="cuida">
      <figure class="cuida__foto">{foto_dra}</figure>
      <div class="cuida__texto">
        {rot_dra}
        <h2 id="dra-titulo">{eq_t}</h2>
        <p>{eq_x}</p>
        <blockquote class="citacao"><p>{frase}</p></blockquote>
        <a class="link-acao" href="{equipe}">{eq_l}</a>
      </div>
    </div>
    {credenciais}
  </div>
</section>

<section class="secao secao--branca" id="depoimentos" aria-labelledby="dep-titulo">
  <div class="largura">
    {notas}
    <p class="nota-pequena centro">{pr_x}</p>
    {relatos}
    <p class="centro">{cta_dep}</p>
  </div>
</section>

<section class="secao secao--branca" aria-labelledby="jornada-titulo">
  <div class="largura">
    {jornada}
  </div>
</section>

<section class="secao secao--creme" aria-label="Programas e loja">
  <div class="largura duas-colunas">
    <div class="cartao-info">
      {rot_pg}
      <h2>{pg_t}</h2>
      <p>{pg_x}</p>
      <a class="link-acao" href="{pg_l}">{pg_lt}</a>
    </div>
    <div class="cartao-info">
      {rot_lj}
      <h2>{lj_t}</h2>
      <p>{lj_x}</p>
      <a class="link-acao" href="{lj_l}">{lj_lt}</a>
    </div>
  </div>
</section>

{guia}

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

<section class="secao secao--rosa-claro" aria-labelledby="final-titulo">
  <div class="largura">
    {final}
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
""".format(
        base=BASE,
        rot_hero=rotulo('<span class="so-desktop">Clínica de estética integrativa · Canaã dos Carajás</span><span class="so-celular">Estética integrativa em Canaã</span>'),
        h1=H["headline"], sub=esc(H["sub"]), nota=nota, microprova=microprova, cta_hero=botao_agendar(H["cta"], "hero", H["whatsapp_msg"]), cta2_hero=botao(H["cta2"], "", classe="botao--contorno", href="#tratamentos", abrir=False), prova=prova_google(href="#depoimentos"),
        foto_hero=foto("adelaine-vertical", "Dra. Adelaine Montel, biomédica esteta, sorrindo na Clínica Empatia Humana", lazy=False, prioridade=True),
        rot_trat=rotulo("Tratamentos"), o_sub=esc(O["sub"]), bento=cards_frentes(), cc_t=esc(CC["titulo"]), cc_sub=esc(CC["sub"]), outros=lista_servicos(CC["servicos"]), todos=link("tratamentos/"),
        consulta=bloco_consulta(),
        foto_dra=foto("adelaine-retrato", "Retrato da Dra. Adelaine Montel"), rot_dra=rotulo("Equipe"),
        eq_t=esc(EQ["titulo"]), eq_x=esc(EQ["texto"]), frase=esc(DRA["frase"]), equipe=link(EQ["link"].strip("/") + "/"), eq_l=esc(EQ["link_texto"]), credenciais=credenciais_html(),
        notas=bloco_notas("avaliacoes-home", 'O que as pacientes <em>contam</em>', primeiro=["Aurora F.", "Marcos Z.", "Juliane A.", "Fernandes S."]).replace("<h2>", '<h2 id="dep-titulo">', 1),
        pr_x=esc(PR["texto"]), relatos=bloco_relatos(dados.WHATSAPP[:2]), cta_dep=botao(CTA, "depoimentos"),
        jornada=jornada(dados.PASSOS, 'Do primeiro contato ao <em>seu plano</em>', "Um caminho simples, sem pressão para fechar nada no primeiro dia. Se o tratamento não for para você, as biomédicas dizem.", botao(CTA, "jornada", classe="botao--rosa")).replace("<h2>", '<h2 id="jornada-titulo">', 1),
        rot_pg=rotulo("Programas"), pg_t=esc(PG["titulo"]), pg_x=esc(PG["texto"]), pg_l=link(PG["link"].strip("/") + "/"), pg_lt=esc(PG["link_texto"]),
        rot_lj=rotulo("Loja"), lj_t=esc(LJ["titulo"]), lj_x=esc(LJ["texto"]), lj_l=link(LJ["link"].strip("/") + "/"), lj_lt=esc(LJ["link_texto"]),
        guia=bloco_guia("guia-home", "guia_home"),
        espaco=espaco_fotos(), clinica=link("a-clinica/"),
        duvidas=secao_duvidas(faq, 'Perguntas que <em>sempre aparecem</em>').replace("de Parauapebas, Curionópolis", 'de <a href="%s">Parauapebas</a>, Curionópolis' % link("pacientes-de-parauapebas/"), 1),
        final=bloco_final("final_home"),
        rot_blog=rotulo("Blog"), blog=link("blog/"), posts=posts,
    )
    grafo = [schema_clinica(), schema_pessoa(), schema_site(), schema_faq(faq),
             schema_pagina("", "Clínica de estética integrativa em Canaã dos Carajás")]
    h = head(HOME["seo"]["title"], HOME["seo"]["description"], "", grafo)
    return pagina(h, corpo, data_pagina="inicio")


def pagina_guia():
    P = GUIA["pagina"]
    caminho = GUIA_CAMINHO
    secoes = "".join('<section class="guia-secao"><h2>%s</h2>%s</section>' % (esc(x["titulo"]), lista_check(x["itens"])) for x in P["secoes"])
    corpo = """
{cabeca}
<section class="secao secao--branca"><div class="largura largura--texto">
  {secoes}
  <p class="cartao-atencao">{aviso}</p>
  <p class="centro">{b}</p>
  <p class="centro"><button class="botao botao--contorno" type="button" onclick="window.print()"><span>Imprimir ou salvar em PDF</span></button></p>
</div></section>
""".format(cabeca=cabeca_pagina([("Início", ""), ("Guia de cuidados", caminho)], "Guia gratuito", esc(P["h1"]), esc(P["intro"])),
           secoes=secoes, aviso=esc(P["aviso"]), b=botao_agendar(P["cta"], "guia_pagina", P["whatsapp_msg"]))
    grafo = [schema_pagina(caminho, P["h1"]), schema_site()]
    return pagina(head(P["seo"]["title"], P["seo"]["description"], caminho, grafo, robots="noindex, follow"), corpo, data_pagina="guia")


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
    <p>Em 2015, Adelaine Barros Montel recebeu o diagnóstico de lúpus, uma doença autoimune, e passou a viver o cuidado do lado de quem é paciente. Foi nessa fase que ela conheceu a ozonioterapia, como terapia complementar ao acompanhamento médico, e se aproximou da ideia de olhar para a pessoa por inteiro.</p>
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
    C = PAGS["equipe-contato"]["contato"]
    end = "%s, %s, %s (%s)" % (S["endereco"], S["bairro"], S["cidade"], S["uf"])

    def tx(t):
        return t.replace("{telefone}", S["telefone"]).replace("{endereco}", end).replace("{horario}", HORARIO_TXT)
    acoes = {
        "whatsapp": lambda c: botao_agendar(c["botao"], "contato_whats", C["whatsapp_msg"]),
        "telefone": lambda c: '<a class="botao botao--contorno" href="tel:+%s" data-origem="contato_tel"><span>%s</span></a>' % (S["whatsapp"], esc(c["botao"])),
        "endereco": lambda c: '<a class="botao botao--contorno" href="%s" target="_blank" rel="noopener"><span>%s</span></a>' % (esc(S["maps"]), esc(c["botao"])),
    }
    canais = "".join("""<li class="canal">
  <h2 class="canal__titulo">{t}</h2>
  <p class="canal__valor">{v}</p>
  <p>{x}</p>
  {b}
</li>""".format(t=esc(c["titulo"]), v=esc(tx(c["valor"])), x=esc(tx(c["texto"])), b=acoes[c["tipo"]](c) if c.get("botao") and c["tipo"] in acoes else "") for c in C["canais"])
    R = C["regiao"]
    faq = [(x["p"], tx(x["r"])) for x in C["faq"]]
    corpo = """
{cabeca}
<section class="secao secao--branca">
  <div class="largura">
    <ul class="canais-grade">{canais}</ul>
  </div>
</section>
<section class="secao secao--rosa-claro" aria-label="Mapa e redes">
  <div class="largura">
    {final}
  </div>
</section>
<section class="secao secao--branca" aria-labelledby="regiao-titulo">
  <div class="largura duas-colunas">
    <div>
      <h2 id="regiao-titulo">{r_t}</h2>
      <p>{r_x}</p>
      <p><a class="link-acao" href="{parau}">Para quem vem de Parauapebas</a></p>
    </div>
    <div class="cartao-info">
      <h3>Redes da clínica</h3>
      <ul class="canais">
        <li>{si}<span><strong>Instagram da clínica</strong><a href="{insta}" target="_blank" rel="noopener">@clinicaempatiahumana</a></span></li>
        <li>{si}<span><strong>Instagram da Dra. Adelaine</strong><a href="{insta_d}" target="_blank" rel="noopener">@biomedicaadelaine</a></span></li>
        <li>{sf}<span><strong>Facebook</strong><a href="{face}" target="_blank" rel="noopener">facebook.com/empatiahumana</a></span></li>
      </ul>
    </div>
  </div>
</section>
{duvidas}
<section class="secao secao--creme espaco">
  <div class="largura">
    {espaco}
  </div>
</section>
""".format(cabeca=cabeca_pagina([("Início", ""), ("Contato", caminho)], "Contato", esc(C["h1"]), esc(C["sub"])),
           canais=canais, final=bloco_final("contato_final"), r_t=esc(R["titulo"]), r_x=esc(R["texto"]), parau=link("pacientes-de-parauapebas/"),
           si=SVG_INSTA, sf=SVG_FACE, insta=S["instagram_clinica"], insta_d=S["instagram_dra"], face=S["facebook"],
           duvidas=secao_duvidas(faq, "Dúvidas sobre <em>o atendimento</em>", ident="faq"), espaco=espaco_fotos())
    grafo = [schema_pagina(caminho, "Contato da Clínica Empatia Humana", "ContactPage"), schema_clinica(), schema_site(), schema_faq(faq), schema_migalhas([("Início", ""), ("Contato", caminho)])]
    h = head(C["seo"]["title"], C["seo"]["description"], caminho, grafo)
    return pagina(h, corpo, atual="contato", data_pagina="contato")


def pagina_cursos():
    caminho = "cursos/"
    C = PAGS["programas-spa-cursos"]["cursos"]
    faq = [(x["p"], x["r"]) for x in C["faq"]]
    cursos = "".join("""<article class="cartao-info curso">
  <h2>{n}</h2>
  <p class="curso__preco">{p}</p>
  <p>{t}</p>
  <h3>Para quem é</h3>
  {pq}
  <div class="hero__acoes">{b}</div>
</article>""".format(n=esc(c["nome"]), p=esc(c["preco"]), t=esc(c["texto"]), pq=lista_check(c["para_quem"]),
                     b=botao_agendar("Quero saber das próximas turmas", "cursos", C["whatsapp_msg"])) for c in C["cursos"])
    corpo = """
{cabeca}
<section class="secao secao--branca">
  <div class="largura largura--texto">
    {cursos}
    <p class="nota-pequena">Os cursos são para profissionais. Para fazer um tratamento na clínica, veja os <a href="{trats}">tratamentos</a>.</p>
  </div>
</section>
{duvidas}
""".format(cabeca=cabeca_pagina([("Início", ""), ("Cursos", caminho)], "Para profissionais", esc(C["h1"]), esc(C["sub"])),
           cursos=cursos, trats=link("tratamentos/"), duvidas=secao_duvidas(faq, "Dúvidas sobre <em>o curso</em>", ident="faq", interesse="cursos para profissionais"))
    grafo = [schema_pagina(caminho, C["h1"])]
    grafo += [{"@type": "Course", "name": c["nome"], "description": c["texto"], "inLanguage": "pt-BR", "provider": {"@id": absoluto("#clinica")}} for c in C["cursos"]]
    grafo += [schema_clinica(), schema_site(), schema_faq(faq), schema_migalhas([("Início", ""), ("Cursos", caminho)])]
    h = head(C["seo"]["title"], C["seo"]["description"], caminho, grafo)
    return pagina(h, corpo, interesse="cursos para profissionais", data_pagina="cursos")


def pagina_parauapebas():
    caminho = "pacientes-de-parauapebas/"
    trats = lista_servicos(HOME["carros_chefe"]["servicos"])
    faq = dados.PARAUAPEBAS["faq"]
    inter = "avaliação (venho de Parauapebas)"
    corpo = """
{cabeca}
<section class="secao secao--branca">
  <div class="largura onde">
    <div>
      <h2>Vale a viagem até <em>Canaã</em>?</h2>
      <p class="onde__nota">Na Empatia Humana, cada caso é estudado antes de qualquer indicação. Quem vem de fora avisa no WhatsApp e a equipe organiza a agenda para aproveitar a viagem, inclusive aos sábados.</p>
      <ul class="lista-check">
        <li>Avaliação gratuita com as biomédicas da clínica, a Dra. Adelaine Montel (CRBM 4ª Região nº 1437) e a Dra. Adriana Montel</li>
        <li>Agenda pensada para quem viaja: avaliação e sessão no mesmo dia, quando o caso permite</li>
        <li>Atendimento {ht}, com horário marcado</li>
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
    {trats}
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
           foto=foto("fachada", "Fachada da Clínica Empatia Humana em Canaã dos Carajás"), embed=esc(S["maps_embed"]), trats=trats, ht=HORARIO_TXT,
           notas=bloco_notas("avaliacoes-parauapebas", 'Quem já veio <em>conta</em>', 6),
           duvidas=secao_duvidas(faq, 'Dúvidas de quem vem de <em>Parauapebas</em>', interesse=inter),
           faixa=cta_faixa("Vem de Parauapebas?", "Avise no WhatsApp: a equipe organiza sua agenda para aproveitar a viagem.", inter, "faixa_parauapebas"))
    grafo = [schema_pagina(caminho, "Clínica de estética para quem é de Parauapebas"), schema_clinica(), schema_site(), schema_faq(faq),
             schema_migalhas([("Início", ""), ("Pacientes de Parauapebas", caminho)])]
    h = head("Clínica de estética para pacientes de Parauapebas",
             "Pacientes de Parauapebas fazem ozonioterapia, tratamento de vasinhos e lipo ozonizada na Empatia Humana, em Canaã dos Carajás. Atendimento de segunda a sábado.",
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

# ======================================================================================
# Estrutura por objetivo (briefing, seção 4): template único de serviço, frentes e páginas novas
# Os textos vêm de dados/servicos/*.json e dados/paginas/*.json
# ======================================================================================

def reais(v):
    v = float(v)
    txt = ("%.2f" % v).replace(".", ",")
    inteiro, cent = txt.split(",")
    inteiro = "{:,}".format(int(inteiro)).replace(",", ".")
    return "R$ %s" % inteiro if cent == "00" else "R$ %s,%s" % (inteiro, cent)


def preco_txt(sv):
    inv = sv["investimento"]
    if inv["tipo"] == "gratuito":
        return "Gratuita"
    if inv["tipo"] == "sob_avaliacao" or not inv.get("valor"):
        return "Sob avaliação"
    return "A partir de %s" % reais(inv["valor"])


def duracao_curta(sv):
    vs = sv["investimento"].get("variacoes") or []
    ds = sorted({x.get("duracao", "") for x in vs if x.get("duracao")})
    if len(ds) == 1:
        return ds[0]
    return sv["duracao_sessoes"]["duracao"]


def marc(t):
    return (t.replace("{telefone}", S["telefone"]).replace("{endereco}", "%s, %s, %s (%s)" % (S["endereco"], S["bairro"], S["cidade"], S["uf"]))
            .replace("{horario}", HORARIO_TXT))


def link_whats(msg):
    from urllib.parse import quote
    return "https://wa.me/%s?text=%s" % (S["whatsapp"], quote(msg, safe=""))


def botao_whats(texto, origem, msg, classe="botao--escuro"):
    return '<a class="botao %s" href="%s" data-origem="%s" target="_blank" rel="noopener"><span>%s</span><span class="botao__seta" aria-hidden="true">%s</span></a>' % (
        classe, esc(link_whats(msg)), origem, esc(texto), icone("seta-diag", "icone icone--seta"))


def lista_check(itens, classe="lista-ok"):
    return '<ul class="%s">%s</ul>' % (classe, "".join("<li>%s<span>%s</span></li>" % (icone("check"), esc(marc(x))) for x in itens))


def resposta_direta(texto, rot="Em resumo"):
    return '<div class="resposta-direta"><p class="resposta-direta__rotulo">%s</p><p>%s</p></div>' % (rot, esc(marc(texto)))


def card_servico(sv, tag="h3", destaque=False):
    pai = PAI.get(sv["frente"], ("", ""))[0]
    return """<li class="card-serv{d}"><a href="{h}">
  <span class="card-serv__frente">{pai}</span>
  <{tag} class="card-serv__nome">{n}</{tag}>
  <span class="card-serv__texto">{t}</span>
  <span class="card-serv__rodape"><span class="card-serv__preco">{p}</span><span class="card-serv__mais">Ver detalhes {seta}</span></span>
</a></li>""".format(d=" card-serv--destaque" if destaque else "", h=link("tratamentos/%s/" % sv["slug"]), pai=esc(pai), tag=tag, n=esc(sv["nome"]),
                    t=esc(sv["resumo_card"]), p=esc(preco_txt(sv)), seta=icone("seta-diag", "icone icone--seta"))


def lista_servicos(slugs, tag="h3", destaque=None):
    return '<ul class="cards-serv">%s</ul>' % "".join(card_servico(SERV[sl], tag, sl == destaque) for sl in slugs if sl in SERV)


def cards_frentes(tag="h3"):
    itens = []
    for f in FRENTES:
        c = f["card_home"]
        itens.append("""<li class="objetivo"><a href="{h}">
  {ic}
  <{tag} class="objetivo__titulo">{t}</{tag}>
  <span class="objetivo__texto">{x}</span>
  <span class="objetivo__queixas">{q}</span>
  <span class="objetivo__mais">Ver tratamentos {seta}</span>
</a></li>""".format(h=link(f["slug"] + "/"), ic=icone(ICONE_FRENTE.get(f["slug"], "folha"), "icone icone--card"), tag=tag, t=esc(c["titulo"]), x=esc(c["texto"]),
                    q="".join("<span>%s</span>" % esc(x) for x in c["queixas"]), seta=icone("seta-diag", "icone icone--seta")))
    return '<ul class="objetivos">%s</ul>' % "".join(itens)


def antes_depois_html(itens):
    """Componente de antes e depois: pronto, mas só aparece com fotos autorizadas pela paciente e conforme as regras do CRBM."""
    if not itens:
        return ""
    figs = "".join('<figure class="antes-depois__item"><div class="antes-depois__fotos">%s%s</div><figcaption>%s</figcaption></figure>' % (
        foto(x["antes"], "Antes: " + x["legenda"]), foto(x["depois"], "Depois: " + x["legenda"]), esc(x["legenda"])) for x in itens)
    return """<section class="secao secao--branca" aria-labelledby="ad-titulo"><div class="largura">
  <h2 id="ad-titulo">Antes e depois</h2>
  <div class="antes-depois">{figs}</div>
  <p class="nota-pequena">Fotos publicadas com autorização da paciente. A resposta varia de pessoa para pessoa e não há resultado garantido.</p>
</div></section>""".format(figs=figs)


def pagamento_html():
    return '<p class="pagamento">%s<span><strong>%s</strong> · Avaliação gratuita para indicar o procedimento</span></p>' % (icone("check"), esc(PAGAMENTO))


def secao_cabeca(rot, titulo_html, texto="", ident=""):
    return '<div class="cabeca">%s<h2%s>%s</h2>%s</div>' % (rotulo(rot) if rot else "", (' id="%s"' % ident) if ident else "", titulo_html, ("<p>%s</p>" % esc(texto)) if texto else "")


def pagina_servico(sv):
    sl = sv["slug"]
    caminho = "tratamentos/%s/" % sl
    pai_nome, pai_cam = PAI.get(sv["frente"], ("Tratamentos", "tratamentos/"))
    inv = sv["investimento"]
    msg = sv.get("whatsapp_msg") or mensagem_whats(sv["nome"])
    faq = [(x["p"], x["r"]) for x in sv["faq"]]
    passos = [(x["titulo"], x["texto"]) for x in sv["como_funciona"]["passos"]]
    dur = sv["duracao_sessoes"]
    res = sv["resultados"]
    cuid = sv["cuidados"]
    pq = sv["para_quem"]
    variacoes = "".join("""<li class="preco"><span class="preco__nome">{n}</span><span class="preco__dur">{d}</span><span class="preco__valor">{p}</span></li>""".format(
        n=esc(x["nome"]), d=esc(x.get("duracao", "")), p=esc(x["preco"][:1].upper() + x["preco"][1:])) for x in inv.get("variacoes", []))
    rel = [x for x in sv.get("relacionados", []) if x in SERV and x != sl][:3]
    corpo = """
<section class="cabeca-pagina cabeca-servico">
  <div class="largura">
    {mig}
    {rot}
    <h1>{h1}</h1>
    <p class="cabeca-pagina__texto">{sub}</p>
    <ul class="fatos">
      <li><span>Duração</span><strong>{dur}</strong></li>
      <li><span>Investimento</span><strong>{preco}</strong></li>
      <li><span>Avaliação</span><strong>Gratuita</strong></li>
    </ul>
    <div class="hero__acoes">{cta}{cta2}</div>
  </div>
</section>

<section class="secao secao--branca secao--curta">
  <div class="largura largura--texto">{resposta}</div>
</section>

<section class="secao secao--creme" aria-labelledby="quem-titulo">
  <div class="largura duas-colunas">
    <div>
      {cab_quem}
      {itens_quem}
    </div>
    <aside class="cartao-atencao" aria-labelledby="atencao-titulo">
      <h3 id="atencao-titulo">Converse na avaliação antes se</h3>
      {atencao}
    </aside>
  </div>
</section>

<section class="secao secao--branca" aria-labelledby="como-titulo">
  <div class="largura">
    {jornada}
  </div>
</section>

<section class="secao secao--creme" aria-labelledby="dur-titulo">
  <div class="largura duas-colunas">
    <div class="cartao-info">
      <h2 id="dur-titulo">Duração e sessões</h2>
      <dl class="dados-lista">
        <div><dt>Cada sessão</dt><dd>{dur_txt}</dd></div>
        <div><dt>Número de sessões</dt><dd>{sessoes}</dd></div>
      </dl>
      {obs}
    </div>
    <div class="cartao-info">
      <h2 id="res-titulo">Resultados esperados</h2>
      <p>{res_txt}</p>
      {res_itens}
      <p class="nota-pequena">{ressalva}</p>
    </div>
  </div>
</section>

<section class="secao secao--branca" aria-labelledby="cuid-titulo">
  <div class="largura">
    {cab_cuid}
    <div class="duas-colunas">
      <div class="cartao-info"><h3>Antes</h3>{antes}</div>
      <div class="cartao-info"><h3>Depois</h3>{depois}</div>
    </div>
    <p class="nota-pequena">{nota_cuid}</p>
  </div>
</section>

<section class="secao secao--creme" id="investimento" aria-labelledby="inv-titulo">
  <div class="largura">
    {cab_inv}
    <ul class="precos">{variacoes}</ul>
    {pagamento}
    <p class="centro">{cta3}</p>
  </div>
</section>
{antes_depois}
{duvidas}
{relacionados}
{faixa}
""".format(
        mig=migalhas_html([("Início", ""), (pai_nome, pai_cam), (sv["nome"], caminho)]), rot=rotulo(pai_nome), h1=esc(sv["h1"]), sub=esc(sv["sub"]),
        dur=esc(duracao_curta(sv)), preco=esc(preco_txt(sv)),
        cta=botao_agendar(CTA, "servico_topo", msg), cta2=botao("Ver investimento", "", classe="botao--contorno", href="#investimento", abrir=False),
        resposta=resposta_direta(sv["resposta_direta"], "O que é, em resumo"),
        cab_quem=secao_cabeca("Para quem é", "Para quem é", pq.get("intro", ""), "quem-titulo"), itens_quem=lista_check(pq["itens"]),
        atencao=lista_check(pq.get("atencao", []), "lista-ok lista-ok--alerta"),
        jornada=jornada(passos, "Como funciona", " ".join(esc(x) for x in sv["como_funciona"]["texto"]), botao_agendar(CTA, "passos", msg, "botao--rosa"), rot="Passo a passo").replace("<h2>", '<h2 id="como-titulo">', 1),
        dur_txt=esc(dur["duracao"]), sessoes=esc(dur["sessoes"]), obs=('<p class="nota-pequena">%s</p>' % esc(dur["observacao"])) if dur.get("observacao") else "",
        res_txt=esc(res["texto"]), res_itens=lista_check(res["itens"]), ressalva=esc(res["ressalva"]),
        cab_cuid=secao_cabeca("Cuidados", "Cuidados antes e depois", "", "cuid-titulo"), antes=lista_check(cuid["antes"]), depois=lista_check(cuid["depois"]), nota_cuid=esc(cuid.get("nota", "")),
        cab_inv=secao_cabeca("Investimento", "Quanto custa", inv.get("texto", ""), "inv-titulo"), variacoes=variacoes, pagamento=pagamento_html(),
        cta3=botao_agendar(CTA, "investimento", msg),
        antes_depois=antes_depois_html(sv.get("antes_depois") or []),
        duvidas=secao_duvidas(faq, "Perguntas sobre <em>%s</em>" % esc(sv["nome"]), ident="faq", interesse=sv["nome"]),
        relacionados=('<section class="secao secao--branca" aria-labelledby="rel-titulo"><div class="largura">%s%s</div></section>' % (
            secao_cabeca("Veja também", "Outros tratamentos", "", "rel-titulo"), lista_servicos(rel))) if rel else "",
        faixa=cta_faixa("Comece pela <em>avaliação gratuita</em>", "As biomédicas ouvem você e indicam o que faz sentido para o seu caso, em Canaã dos Carajás.", sv["nome"], "faixa_final"),
    )
    servico = {"@type": ["Service", "MedicalProcedure"], "@id": absoluto(caminho + "#servico"), "name": sv["nome"], "serviceType": sv["nome"],
               "description": sv["resposta_direta"], "provider": {"@id": absoluto("#clinica")}, "areaServed": [{"@type": "City", "name": c} for c in S["regiao"]], "url": absoluto(caminho)}
    if inv["tipo"] == "a_partir_de" and inv.get("valor"):
        servico["offers"] = {"@type": "Offer", "priceCurrency": "BRL", "price": "%.2f" % float(inv["valor"]), "url": absoluto(caminho),
                             "priceSpecification": {"@type": "PriceSpecification", "minPrice": float(inv["valor"]), "priceCurrency": "BRL"}}
    elif inv["tipo"] == "gratuito":
        servico["offers"] = {"@type": "Offer", "priceCurrency": "BRL", "price": "0", "url": absoluto(caminho)}
    grafo = [
        {"@type": "MedicalWebPage", "@id": absoluto(caminho + "#pagina"), "url": absoluto(caminho), "name": sv["h1"], "description": sv["seo"]["description"], "inLanguage": "pt-BR",
         "isPartOf": {"@id": absoluto("#site")}, "about": {"@id": absoluto(caminho + "#servico")}, "lastReviewed": HOJE},
        servico, schema_clinica(), schema_site(), schema_faq(faq),
        schema_migalhas([("Início", ""), (pai_nome, pai_cam), (sv["nome"], caminho)]),
    ]
    h = head(sv["seo"]["title"], sv["seo"]["description"], caminho, grafo)
    return pagina(h, corpo, atual="tratamentos", interesse=sv["nome"], data_pagina="servico", data_trat=sl)


def pagina_frente(f):
    caminho = f["slug"] + "/"
    faq = [(x["p"], x["r"]) for x in f["faq"]]
    outros = ""
    if f.get("outros_servicos"):
        outros = '<div class="tambem"><p class="tambem__titulo">Também na clínica</p><ul class="etiquetas">%s</ul></div>' % "".join("<li>%s</li>" % esc(o) for o in f["outros_servicos"])
    acoes = '<div class="hero__acoes">%s%s</div>' % (botao_agendar(CTA, "frente_topo", f["whatsapp_msg"]), botao("Ver os tratamentos", "", classe="botao--contorno", href="#lista", abrir=False))
    corpo = """
{cabeca}
<section class="secao secao--branca secao--curta">
  <div class="largura largura--texto">{resposta}</div>
</section>
<section class="secao secao--creme" aria-labelledby="ident-titulo">
  <div class="largura largura--texto">
    {cab_ident}
    {ident}
  </div>
</section>
<section class="secao secao--branca" id="lista" aria-labelledby="lista-titulo">
  <div class="largura">
    {cab_lista}
    {lista}
    {outros}
    {pagamento}
  </div>
</section>
{duvidas}
{faixa}
""".format(cabeca=cabeca_pagina([("Início", ""), (f["nome"], caminho)], "Tratamentos por objetivo", esc(f["h1"]), esc(f["sub"]), acoes),
           resposta=resposta_direta(f["resposta_direta"]),
           cab_ident=secao_cabeca("Para quem é", "Você se reconhece?", "", "ident-titulo"), ident=lista_check(f["identificacao"]),
           cab_lista=secao_cabeca("Tratamentos", "Tratamentos para <em>%s</em>" % esc(f["nome"].lower()), "Toque em um tratamento para ver como funciona, quanto tempo leva e o investimento.", "lista-titulo"),
           lista=lista_servicos(f["servicos"], destaque=f.get("destaque")), outros=outros, pagamento=pagamento_html(),
           duvidas=secao_duvidas(faq, "Dúvidas sobre <em>%s</em>" % esc(f["nome"].lower()), ident="faq", interesse=f["nome"].lower()),
           faixa=cta_faixa("Não sabe qual escolher?", "Na avaliação gratuita, as biomédicas ouvem você e indicam o caminho para o seu caso.", f["nome"].lower(), "faixa_final"))
    grafo = [schema_pagina(caminho, f["h1"], "CollectionPage", {"description": f["seo"]["description"], "mainEntity": {"@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": absoluto("tratamentos/%s/" % sl), "name": SERV[sl]["nome"]} for i, sl in enumerate([x for x in f["servicos"] if x in SERV])]}}),
        schema_clinica(), schema_site(), schema_faq(faq), schema_migalhas([("Início", ""), (f["nome"], caminho)])]
    h = head(f["seo"]["title"], f["seo"]["description"], caminho, grafo)
    return pagina(h, corpo, atual="tratamentos", interesse=f["nome"].lower(), data_pagina="frente")


def pagina_tratamentos():
    caminho = "tratamentos/"
    grupos = []
    for f in FRENTES:
        grupos.append('<section class="grupo-trat" aria-labelledby="g-%s"><div class="grupo-trat__cabeca"><h2 id="g-%s">%s</h2><a class="link-acao" href="%s">Ver a página %s</a></div>%s</section>' % (
            f["slug"], f["slug"], esc(f["nome"]), link(f["slug"] + "/"), icone("seta-diag", "icone icone--seta"), lista_servicos(f["servicos"])))
    grupos.append('<section class="grupo-trat" aria-labelledby="g-prog"><div class="grupo-trat__cabeca"><h2 id="g-prog">Programas e desafios</h2><a class="link-acao" href="%s">Ver a página %s</a></div>%s</section>' % (
        link("programas-e-desafios/"), icone("seta-diag", "icone icone--seta"), lista_servicos(PROG["programas"] + ["desinflamando-para-o-natal"])))
    grupos.append('<section class="grupo-trat" aria-labelledby="g-spa"><div class="grupo-trat__cabeca"><h2 id="g-spa">Spa e bem-estar</h2><a class="link-acao" href="%s">Ver a página %s</a></div>%s</section>' % (
        link("spa/"), icone("seta-diag", "icone icone--seta"), lista_servicos(SPA.get("paginas", ["toque-de-spa", "massagens"]))))
    corpo = """
{cabeca}
<section class="secao secao--creme">
  <div class="largura">
    {objetivos}
  </div>
</section>
<section class="secao secao--branca">
  <div class="largura">
    {grupos}
    {pagamento}
  </div>
</section>
{faixa}
""".format(cabeca=cabeca_pagina([("Início", ""), ("Tratamentos", caminho)], "Tratamentos", 'Tratamentos de estética integrativa em <em>Canaã dos Carajás</em>',
                                "Organizados pelo que você quer cuidar: emagrecimento e medidas, pele e rejuvenescimento, pernas e circulação e saúde integrativa. Todos começam pela avaliação gratuita."),
           objetivos=cards_frentes("h2"), grupos="".join(grupos), pagamento=pagamento_html(),
           faixa=cta_faixa("Não sabe por onde começar?", "Conte o que você sente. As biomédicas indicam o caminho na avaliação gratuita.", "", "faixa_hub"))
    grafo = [schema_pagina(caminho, "Tratamentos da Clínica Empatia Humana", "CollectionPage", {
        "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": absoluto("tratamentos/%s/" % sl), "name": sv["nome"]} for i, (sl, sv) in enumerate(SERV.items())]}}),
        schema_clinica(), schema_site(), schema_migalhas([("Início", ""), ("Tratamentos", caminho)])]
    h = head("Tratamentos estéticos em Canaã dos Carajás | Empatia Humana",
             "Emagrecimento e medidas, pele, vasinhos e saúde integrativa com ozonioterapia em Canaã dos Carajás (PA). Veja cada tratamento, a duração e o investimento.",
             caminho, grafo)
    return pagina(h, corpo, atual="tratamentos", data_pagina="tratamentos")


def pagina_programas():
    caminho = "programas-e-desafios/"
    P = PROG
    faq = [(x["p"], x["r"]) for x in P["faq"]]
    camp = P.get("campanha") or {}
    campanha = ""
    if camp:
        campanha = '<a class="cartao-campanha" href="%s"><span class="cartao-campanha__selo">Campanha da estação</span><strong>%s</strong><span>%s</span><span class="card-serv__mais">Ver o programa %s</span></a>' % (
            link("tratamentos/%s/" % camp["slug"]), esc(camp["titulo"]), esc(camp["texto"]), icone("seta-diag", "icone icone--seta"))
    passos = [(x["titulo"], x["texto"]) for x in P["como_funciona"]]
    acoes = '<div class="hero__acoes">%s</div>' % botao_agendar(CTA, "programas_topo", P["whatsapp_msg"])
    corpo = """
{cabeca}
<section class="secao secao--branca secao--curta"><div class="largura largura--texto">{resposta}<p class="texto-intro">{intro}</p></div></section>
<section class="secao secao--creme" aria-labelledby="lista-titulo"><div class="largura">
  {cab}
  {campanha}
  {lista}
  <p class="nota-pequena">Os programas são indicados na avaliação. O valor é sob avaliação, porque depende do que entra no seu plano.</p>
  {pagamento}
</div></section>
<section class="secao secao--branca" aria-labelledby="como-titulo"><div class="largura">{jornada}</div></section>
{duvidas}
{faixa}
""".format(cabeca=cabeca_pagina([("Início", ""), ("Programas e desafios", caminho)], "Programas e desafios", esc(P["h1"]), esc(P["sub"]), acoes),
           resposta=resposta_direta(P["resposta_direta"]), intro=esc(P.get("intro", "")),
           cab=secao_cabeca("Programas", "Escolha o seu ponto de partida", "", "lista-titulo"), campanha=campanha, lista=lista_servicos(P["programas"]), pagamento=pagamento_html(),
           jornada=jornada(passos, "Como funciona", "Do primeiro contato ao seu plano, com tudo combinado antes de começar.", botao_agendar(CTA, "passos", P["whatsapp_msg"], "botao--rosa"), rot="Passo a passo").replace("<h2>", '<h2 id="como-titulo">', 1),
           duvidas=secao_duvidas(faq, "Dúvidas sobre <em>os programas</em>", ident="faq", interesse="os programas e desafios"),
           faixa=cta_faixa("Qual programa é para você?", "A resposta vem na avaliação gratuita, depois de ouvir o seu objetivo e a sua rotina.", "os programas e desafios", "faixa_final"))
    grafo = [schema_pagina(caminho, P["h1"], "CollectionPage", {"mainEntity": {"@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "url": absoluto("tratamentos/%s/" % sl), "name": SERV[sl]["nome"]} for i, sl in enumerate(P["programas"]) if sl in SERV]}}),
        schema_clinica(), schema_site(), schema_faq(faq), schema_migalhas([("Início", ""), ("Programas e desafios", caminho)])]
    return pagina(head(P["seo"]["title"], P["seo"]["description"], caminho, grafo), corpo, atual="programas", interesse="os programas e desafios", data_pagina="programas")


def pagina_spa():
    caminho = "spa/"
    P = SPA
    faq = [(x["p"], x["r"]) for x in P["faq"]]
    vp = P["vale_presente"]
    itens = "".join('<li class="preco"><span class="preco__nome">%s</span><span class="preco__dur">%s</span><span class="preco__valor">%s</span>%s</li>' % (
        esc(x["nome"]), esc(x.get("duracao", "")), esc(x["preco"][:1].upper() + x["preco"][1:]), ('<span class="preco__texto">%s</span>' % esc(x["texto"])) if x.get("texto") else "") for x in P["itens"])
    acoes = '<div class="hero__acoes">%s%s</div>' % (botao_agendar("Agendar um horário", "spa_topo", P["whatsapp_msg"]), botao_whats("Quero dar um vale-presente", "vale_presente", vp["whatsapp_msg"], "botao--contorno"))
    corpo = """
{cabeca}
<section class="secao secao--branca secao--curta"><div class="largura largura--texto">{resposta}</div></section>
<section class="secao secao--rosa-claro" aria-labelledby="vp-titulo"><div class="largura largura--texto centro-bloco">
  <h2 id="vp-titulo">{vp_t}</h2><p>{vp_x}</p><p>{vp_b}</p>
</div></section>
<section class="secao secao--creme" aria-labelledby="menu-spa"><div class="largura">
  {cab}
  <ul class="precos precos--spa">{itens}</ul>
  {nota}
  {pagamento}
</div></section>
<section class="secao secao--branca"><div class="largura">{cab2}{paginas}</div></section>
{duvidas}
{faixa}
""".format(cabeca=cabeca_pagina([("Início", ""), ("Spa e bem-estar", caminho)], "Spa e bem-estar", esc(P["h1"]), esc(P["sub"]), acoes),
           resposta=resposta_direta(P["resposta_direta"]), vp_t=esc(vp["titulo"]), vp_x=esc(vp["texto"]), vp_b=botao_whats("Pedir um vale-presente", "vale_presente", vp["whatsapp_msg"]),
           cab=secao_cabeca("Cardápio", "Cuidados do spa", "", "menu-spa"), itens=itens, nota=('<p class="nota-pequena">%s</p>' % esc(P["nota"])) if P.get("nota") else "", pagamento=pagamento_html(),
           cab2=secao_cabeca("Saiba mais", "Como é cada cuidado"), paginas=lista_servicos(P.get("paginas", [])),
           duvidas=secao_duvidas(faq, "Dúvidas sobre <em>o spa</em>", ident="faq", interesse="o spa"),
           faixa=cta_faixa("Uma pausa para você <em>ou para quem você ama</em>", "Agende pelo WhatsApp ou peça um vale-presente.", "o spa", "faixa_final"))
    grafo = [schema_pagina(caminho, P["h1"], extra={"description": P["seo"]["description"]}), schema_clinica(), schema_site(), schema_faq(faq), schema_migalhas([("Início", ""), ("Spa e bem-estar", caminho)])]
    return pagina(head(P["seo"]["title"], P["seo"]["description"], caminho, grafo), corpo, atual="spa", interesse="o spa", data_pagina="spa")


def pagina_equipe():
    caminho = "equipe/"
    P = EQUIPE
    faq = [(x["p"], x["r"]) for x in P["faq"]]
    pessoas = []
    for x in P["pessoas"]:
        nome_foto = (x.get("foto") or "").replace(".webp", "")
        if nome_foto and os.path.exists(os.path.join(RAIZ, "assets", "img", nome_foto + ".webp")):
            img = foto(nome_foto, x["nome"], "pessoa__foto")
        else:
            iniciais = "".join(p[0] for p in x["nome"].replace("Dra. ", "").split()[:2])
            img = '<span class="pessoa__foto pessoa__foto--iniciais" aria-hidden="true">%s</span>' % esc(iniciais)
        bio = "".join("<p>%s</p>" % esc(b) for b in x.get("bio", []))
        frase = ('<blockquote class="pessoa__frase">%s</blockquote>' % esc(x["frase"])) if x.get("frase") else ""
        extra = ('<p><a class="link-acao" href="%s">Trajetória completa %s</a></p>' % (link("dra-adelaine-montel/"), icone("seta-diag", "icone icone--seta"))) if "Adelaine" in x["nome"] else ""
        pessoas.append("""<article class="pessoa">
  <div class="pessoa__midia">{img}</div>
  <div class="pessoa__texto">
    <h2>{n}</h2>
    <p class="pessoa__cargo">{c}{r}</p>
    {bio}{frase}{extra}
  </div>
</article>""".format(img=img, n=esc(x["nome"]), c=esc(x["cargo"]), r=(" · " + esc(x["registro"])) if x.get("registro") else "", bio=bio, frase=frase, extra=extra))
    como = "".join("<li><h3>%s</h3><p>%s</p></li>" % (esc(x["titulo"]), esc(x["texto"])) if isinstance(x, dict) else "<li><p>%s</p></li>" % esc(x) for x in P.get("como_atendemos", []))
    corpo = """
{cabeca}
<section class="secao secao--branca"><div class="largura equipe">{intro}{pessoas}</div></section>
<section class="secao secao--creme" aria-labelledby="como-titulo"><div class="largura">{cab}<ol class="passos-simples">{como}</ol></div></section>
{duvidas}
{faixa}
""".format(cabeca=cabeca_pagina([("Início", ""), ("Equipe", caminho)], "Equipe", esc(P["h1"]), esc(P["sub"]), '<div class="hero__acoes">%s</div>' % botao_agendar(CTA, "equipe_topo", P["whatsapp_msg"])),
           intro=('<p class="texto-intro">%s</p>' % esc(P["intro"])) if P.get("intro") else "", pessoas="".join(pessoas),
           cab=secao_cabeca("Como atendemos", "Como é o atendimento", "", "como-titulo"), como=como,
           duvidas=secao_duvidas(faq, "Dúvidas sobre <em>a equipe</em>", ident="faq"),
           faixa=cta_faixa("Agende com <em>as biomédicas</em>", "A avaliação é gratuita e serve para indicar o que faz sentido para você.", "", "faixa_final"))
    grafo = [schema_pagina(caminho, P["h1"], "AboutPage"), schema_clinica(), schema_pessoa(), schema_site(), schema_faq(faq), schema_migalhas([("Início", ""), ("Equipe", caminho)])]
    return pagina(head(P["seo"]["title"], P["seo"]["description"], caminho, grafo), corpo, atual="equipe", data_pagina="equipe")


def pagina_loja():
    caminho = "loja/"
    P = LOJA
    faq = [(x["p"], x["r"]) for x in P["faq"]]
    dest = "".join("""<li class="produto produto--destaque"><strong>{n}</strong><span>{t}</span>{b}</li>""".format(
        n=esc(x["nome"]), t=esc(x["texto"]), b=botao_whats("Pedir pelo WhatsApp", "loja_destaque", x["whatsapp_msg"], "botao--rosa")) for x in P["destaques"])
    grupos = "".join("""<section class="grupo-loja" aria-labelledby="gl-{sl}"><h3 id="gl-{sl}">{n}</h3><p>{t}</p><ul class="produtos">{itens}</ul></section>""".format(
        sl=g["slug"], n=esc(g["nome"]), t=esc(g.get("texto", "")),
        itens="".join('<li class="produto"><span>%s</span><a class="link-acao" href="%s" data-origem="loja_item" target="_blank" rel="noopener">Pedir %s</a></li>' % (
            esc(x["nome"]), esc(link_whats(x["whatsapp_msg"])), icone("seta-diag", "icone icone--seta")) for x in g["produtos"])) for g in P["grupos"])
    passos = "".join("<li><h3>%s</h3><p>%s</p></li>" % (esc(x["titulo"]), esc(x["texto"])) for x in P["como_pedir"])
    corpo = """
{cabeca}
<section class="secao secao--branca secao--curta"><div class="largura largura--texto">{resposta}<ol class="passos-simples passos-simples--linha">{passos}</ol></div></section>
<section class="secao secao--creme" aria-labelledby="dest-titulo"><div class="largura">{cab}<ul class="produtos produtos--destaque">{dest}</ul></div></section>
<section class="secao secao--branca" aria-labelledby="todos-titulo"><div class="largura">{cab2}{grupos}<p class="nota-pequena">{aviso}</p></div></section>
{duvidas}
{faixa}
""".format(cabeca=cabeca_pagina([("Início", ""), ("Loja e home care", caminho)], "Home care", esc(P["h1"]), esc(P["sub"]), '<div class="hero__acoes">%s</div>' % botao_whats("Fazer um pedido", "loja_topo", P["whatsapp_msg"])),
           resposta=resposta_direta(P["resposta_direta"]), passos=passos,
           cab=secao_cabeca("Mais pedidos", "Os queridinhos da clínica", "", "dest-titulo"), dest=dest,
           cab2=secao_cabeca("Vitrine", "Todos os produtos", "Os valores são informados pelo WhatsApp, junto com a disponibilidade.", "todos-titulo"), grupos=grupos, aviso=esc(P.get("aviso", "")),
           duvidas=secao_duvidas(faq, "Dúvidas sobre <em>a loja</em>", ident="faq", interesse="os produtos da loja"),
           faixa=cta_faixa("Não sabe qual produto escolher?", "Chame no WhatsApp e conte o que você procura.", "os produtos da loja", "faixa_final"))
    grafo = [schema_pagina(caminho, P["h1"], "CollectionPage", {"description": P["seo"]["description"]}), schema_clinica(), schema_site(), schema_faq(faq), schema_migalhas([("Início", ""), ("Loja e home care", caminho)])]
    return pagina(head(P["seo"]["title"], P["seo"]["description"], caminho, grafo), corpo, atual="loja", interesse="os produtos da loja", data_pagina="loja")


def urls_do_site():
    u = [("", "1.0"), ("tratamentos/", "0.9")]
    u += [(f["slug"] + "/", "0.9") for f in FRENTES]
    u += [("programas-e-desafios/", "0.8"), ("spa/", "0.7"), ("equipe/", "0.8"), ("loja/", "0.7")]
    u += [("tratamentos/%s/" % sl, "0.8") for sl in SERV]
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
         "- Horário: %s, com horário marcado" % HORARIO_TXT,
         "- Equipe: Dra. Adelaine Montel e Dra. Adriana Montel, biomédicas estetas e ozonioterapeutas",
         "- Pagamento: %s. Avaliação gratuita para indicar o procedimento." % PAGAMENTO,
         "- Atende pacientes de: %s" % ", ".join(S["regiao"]),
         "- Instagram: %s e %s" % (S["instagram_clinica"], S["instagram_dra"]),
         "- Google Maps: %s" % S["maps_cid"],
         "- Registro da responsável: Adelaine Barros Montel, CRBM 4ª Região nº 1437, ativo; habilitações em %s" % "; ".join(DRA["habilitacoes"]),
         "- [Sobre a clínica](%s) · [Contato](%s) · [Depoimentos](%s)" % (absoluto("a-clinica/"), absoluto("contato/"), absoluto("depoimentos/")),
         ""]
    for f in FRENTES:
        l += ["## %s" % f["nome"], "[Página da frente](%s): %s" % (absoluto(f["slug"] + "/"), f["resposta_direta"])]
        for sl in f["servicos"]:
            if sl in SERV:
                l.append("- [%s](%s) (%s): %s" % (SERV[sl]["nome"], absoluto("tratamentos/%s/" % sl), preco_txt(SERV[sl]).lower(), SERV[sl]["resumo_card"]))
        l.append("")
    l += ["## Programas e desafios", "[Página](%s): %s" % (absoluto("programas-e-desafios/"), PROG["resposta_direta"])]
    for sl in PROG["programas"]:
        l.append("- [%s](%s): %s" % (SERV[sl]["nome"], absoluto("tratamentos/%s/" % sl), SERV[sl]["resumo_card"]))
    l += ["", "## Spa e bem-estar", "[Página](%s): %s" % (absoluto("spa/"), SPA["resposta_direta"]),
          "", "## Equipe", "[Equipe](%s)" % absoluto("equipe/"), "", "## Loja e home care", "[Loja](%s): %s" % (absoluto("loja/"), LOJA["resposta_direta"])]
    l += ["", "## Sobre a Dra. Adelaine Montel", "- [Trajetória, formação e registro](%s)" % absoluto("dra-adelaine-montel/"), "", "## Blog"]
    for p in POSTS:
        l.append("- [%s](%s): %s" % (p["titulo"], absoluto("blog/%s/" % p["slug"]), p.get("resumo", "")))
    l += ["", "## Cursos", "- [Cursos para profissionais](%s): %s" % (absoluto("cursos/"), "; ".join(c["nome"] for c in PAGS["programas-spa-cursos"]["cursos"]["cursos"]))]
    l += ["", "## Perguntas frequentes"]
    for q, a in faq_home():
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
    grava("js/config.js", config_js())
    grava("index.html", pagina_home())
    grava("tratamentos/index.html", pagina_tratamentos())
    for sl, sv in SERV.items():
        grava("tratamentos/%s/index.html" % sl, pagina_servico(sv))
    for f in FRENTES:
        grava("%s/index.html" % f["slug"], pagina_frente(f))
    grava("programas-e-desafios/index.html", pagina_programas())
    grava("spa/index.html", pagina_spa())
    grava("equipe/index.html", pagina_equipe())
    grava("loja/index.html", pagina_loja())
    grava(GUIA_CAMINHO + "index.html", pagina_guia())
    antigo = os.path.join(RAIZ, "tratamentos", "saude-intestinal")
    if os.path.isdir(antigo):
        import shutil
        shutil.rmtree(antigo)
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
    print("Gerado: %d páginas de serviço, %d frentes, %d posts, %d URLs no sitemap." % (len(SERV), len(FRENTES), len(POSTS), len(urls_do_site())))


if __name__ == "__main__":
    main()
