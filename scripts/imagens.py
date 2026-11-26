# -*- coding: utf-8 -*-
"""Gera as imagens do site: fotos .webp, logos a partir da identidade visual, favicon e a prévia (og-empatia.jpg).

Uso:  python scripts/imagens.py   (precisa do Pillow: pip install pillow)
Os originais da marca ficam em assets/marca/ (arquivos da pasta "ID Visual").
Rode de novo sempre que trocar uma foto em assets/img/ ou um logo em assets/marca/.
"""
import json
import math
import os
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(RAIZ, "assets", "img")
MARCA = os.path.join(RAIZ, "assets", "marca")

# Cores da identidade (cores.jpg)
ROSA = (253, 161, 179)        # predominante  #FDA1B3
ROSA_CLARO = (252, 206, 216)  # secundária    #FCCED8
CREME = (243, 238, 234)       # terciária     #F3EEEA
TEXTO = (109, 100, 103)       # letras        #6D6467
GRAFITE = (74, 66, 69)        # tom mais escuro do cinza da marca, para títulos e fundos
ROSA_PROFUNDO = (200, 82, 110)

FOTOS = ["adelaine-vertical", "adelaine-vertical-540", "adelaine-retrato", "adelaine-consultorio",
         "avaliacao-pernas", "clinica-emblema", "recepcao", "fachada"]

MEDIDAS = {}


def webp():
    for nome in FOTOS:
        origem = os.path.join(IMG, nome + ".jpg")
        if not os.path.exists(origem):
            print("  falta", origem)
            continue
        im = Image.open(origem).convert("RGB")
        im.save(os.path.join(IMG, nome + ".webp"), "WEBP", quality=80, method=6)
        MEDIDAS[nome] = im.size
    # avatar pequeno (janela de agendamento e autora dos posts)
    r = Image.open(os.path.join(IMG, "adelaine-retrato.jpg")).convert("RGB")
    w, h = r.size
    lado = int(w * 0.62)
    x0, y0 = (w - lado) // 2, int(h * 0.02)
    r.crop((x0, y0, x0 + lado, y0 + lado)).resize((160, 160), Image.LANCZOS).save(os.path.join(IMG, "adelaine-avatar.webp"), "WEBP", quality=82, method=6)
    MEDIDAS["adelaine-avatar"] = (160, 160)


def recorte(im, limiar=128, folga=4):
    """Corta a área útil do logo (ignora resíduos quase transparentes)."""
    bb = im.split()[3].point(lambda v: 255 if v > limiar else 0).getbbox()
    return im.crop((max(0, bb[0] - folga), max(0, bb[1] - folga), min(im.width, bb[2] + folga), min(im.height, bb[3] + folga)))


def pintar(im, cor):
    novo = Image.new("RGBA", im.size, cor + (0,))
    novo.putalpha(im.split()[3])
    return novo


def salvar(im, nome, largura=None):
    if largura and largura < im.width:
        im = im.resize((largura, round(im.height * largura / im.width)), Image.LANCZOS)
    im.save(os.path.join(IMG, nome + ".webp"), "WEBP", quality=92, method=6)
    MEDIDAS[nome] = im.size
    print(nome, im.size, os.path.getsize(os.path.join(IMG, nome + ".webp")) // 1024, "KB")
    return im


def marca():
    simbolo = recorte(Image.open(os.path.join(MARCA, "simbolo-rosa.png")).convert("RGBA"))
    logotipo = recorte(Image.open(os.path.join(MARCA, "logotipo-rosa.png")).convert("RGBA"))
    logo_rosa = recorte(Image.open(os.path.join(MARCA, "logo-rosa.png")).convert("RGBA"))
    logo_branca = recorte(Image.open(os.path.join(MARCA, "logo-branca.png")).convert("RGBA"))

    salvar(simbolo, "simbolo-rosa", 320)
    simb_branco = pintar(simbolo, (255, 255, 255))
    salvar(simb_branco, "simbolo-branco", 320)
    salvar(logotipo, "logotipo-rosa", 720)
    salvar(pintar(logotipo, (255, 255, 255)), "logotipo-branco")
    salvar(logo_rosa, "logo-rosa", 640)
    salvar(logo_branca, "logo-branca", 640)

    # ícones: símbolo branco sobre o rosa da marca
    def icone(lado, redondo):
        base = Image.new("RGBA", (lado * 4, lado * 4), (0, 0, 0, 0))
        d = ImageDraw.Draw(base)
        if redondo:
            d.ellipse([0, 0, lado * 4 - 1, lado * 4 - 1], fill=ROSA + (255,))
        else:
            d.rectangle([0, 0, lado * 4, lado * 4], fill=ROSA + (255,))
        s = simb_branco.copy()
        alvo = int(lado * 4 * 0.74)
        s = s.resize((alvo, round(s.height * alvo / s.width)), Image.LANCZOS)
        base.alpha_composite(s, ((lado * 4 - s.width) // 2, (lado * 4 - s.height) // 2))
        return base.resize((lado, lado), Image.LANCZOS)

    icone(64, True).save(os.path.join(IMG, "favicon.png"))
    icone(180, False).convert("RGB").save(os.path.join(IMG, "apple-touch-icon.png"))
    # logo quadrado para os dados estruturados (como a foto de perfil da clínica)
    q = Image.new("RGB", (512, 512), ROSA)
    lb = logo_branca.resize((400, round(logo_branca.height * 400 / logo_branca.width)), Image.LANCZOS)
    q.paste(lb, ((512 - lb.width) // 2, (512 - lb.height) // 2), lb)
    q.save(os.path.join(IMG, "logo-empatia-humana.png"), optimize=True)


def fonte(tamanho, estilo=""):
    nomes = {"": ["georgia.ttf"], "b": ["georgiab.ttf"], "i": ["georgiai.ttf"], "s": ["segoeui.ttf"], "sb": ["seguisb.ttf"]}[estilo]
    for nome in nomes:
        caminho = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", nome)
        if os.path.exists(caminho):
            return ImageFont.truetype(caminho, tamanho)
    return ImageFont.load_default()


def og():
    W, H = 1200, 630
    base = Image.new("RGB", (W, H), CREME)
    d = ImageDraw.Draw(base)
    # arco rosa com o retrato
    ax, ay, aw, ah = 760, 60, 370, 570
    mascara = Image.new("L", (aw, ah), 0)
    dm = ImageDraw.Draw(mascara)
    dm.ellipse([0, 0, aw, aw], fill=255)
    dm.rectangle([0, aw // 2, aw, ah], fill=255)
    foto = Image.open(os.path.join(IMG, "adelaine-vertical.jpg")).convert("RGB")
    escala = max(aw / foto.width, (ah + 12) / foto.height)  # cobre o arco inteiro
    foto = foto.resize((round(foto.width * escala), round(foto.height * escala)), Image.LANCZOS)
    x0 = (foto.width - aw) // 2
    foto = foto.crop((x0, 10, x0 + aw, 10 + ah))
    d.ellipse([ax + 26, ay - 22, ax + 26 + aw, ay - 22 + aw], outline=ROSA, width=3)
    d.line([ax + 26, ay - 22 + aw // 2, ax + 26, H], fill=ROSA, width=3)
    d.line([ax + 26 + aw, ay - 22 + aw // 2, ax + 26 + aw, H], fill=ROSA, width=3)
    base.paste(foto, (ax, ay), mascara)
    # logo
    logo = recorte(Image.open(os.path.join(MARCA, "logo-rosa.png")).convert("RGBA"))
    logo = logo.resize((250, round(logo.height * 250 / logo.width)), Image.LANCZOS)
    base.paste(logo, (70, 48), logo)
    d.text((70, 250), "Estética que trata você", font=fonte(54), fill=GRAFITE)
    d.text((70, 314), "de dentro para fora", font=fonte(54, "i"), fill=ROSA_PROFUNDO)
    d.text((70, 404), "Clínica de estética integrativa em Canaã dos Carajás", font=fonte(25, "s"), fill=TEXTO)
    for i in range(5):  # estrelas desenhadas (a fonte do Windows não tem o caractere)
        cx, cy, r1, r2 = 84 + i * 30, 478, 13, 5.5
        pts = [(cx + (r1 if k % 2 == 0 else r2) * math.sin(k * math.pi / 5), cy - (r1 if k % 2 == 0 else r2) * math.cos(k * math.pi / 5)) for k in range(10)]
        d.polygon(pts, fill=ROSA)
    d.text((232, 461), "5,0 no Google", font=fonte(26, "sb"), fill=GRAFITE)
    d.text((70, 528), "Dra. Adelaine Montel · Biomédica · CRBM 1437", font=fonte(23, "s"), fill=TEXTO)
    base.save(os.path.join(IMG, "og-empatia.jpg"), "JPEG", quality=88, optimize=True, progressive=True)
    print("og-empatia.jpg", os.path.getsize(os.path.join(IMG, "og-empatia.jpg")) // 1024, "KB")


if __name__ == "__main__":
    webp()
    marca()
    og()
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "medidas.json"), "w", encoding="utf-8") as f:
        json.dump(MEDIDAS, f, indent=1, sort_keys=True)
