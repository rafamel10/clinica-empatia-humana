# -*- coding: utf-8 -*-
"""Gera as versões .webp das fotos e a imagem de prévia (og-empatia.jpg, 1200x630).

Uso:  python scripts/imagens.py   (precisa do Pillow: pip install pillow)
Rode de novo sempre que trocar uma foto em assets/img/.
"""
import os
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(RAIZ, "assets", "img")

FOTOS = ["adelaine-vertical", "adelaine-vertical-540", "adelaine-retrato", "adelaine-consultorio",
         "avaliacao-pernas", "clinica-emblema", "recepcao", "fachada", "logo-empatia-humana"]


def webp():
    for nome in FOTOS:
        origem = os.path.join(IMG, nome + ".jpg")
        if not os.path.exists(origem):
            print("  falta", origem)
            continue
        im = Image.open(origem).convert("RGB")
        destino = os.path.join(IMG, nome + ".webp")
        im.save(destino, "WEBP", quality=80, method=6)
        print(nome, im.size, os.path.getsize(origem) // 1024, "KB ->", os.path.getsize(destino) // 1024, "KB")
    # avatar pequeno (topo, janela de agendamento e autora dos posts)
    r = Image.open(os.path.join(IMG, "adelaine-retrato.jpg")).convert("RGB")
    w, h = r.size
    lado = int(w * 0.62)
    x0, y0 = (w - lado) // 2, int(h * 0.02)
    r.crop((x0, y0, x0 + lado, y0 + lado)).resize((160, 160), Image.LANCZOS).save(os.path.join(IMG, "adelaine-avatar.webp"), "WEBP", quality=82, method=6)
    print("adelaine-avatar.webp", os.path.getsize(os.path.join(IMG, "adelaine-avatar.webp")) // 1024, "KB")


def fonte(tamanho, negrito=False):
    for nome in (["georgiab.ttf", "seguisb.ttf"] if negrito else ["georgia.ttf", "segoeui.ttf"]):
        caminho = os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", nome)
        if os.path.exists(caminho):
            return ImageFont.truetype(caminho, tamanho)
    return ImageFont.load_default()


def og():
    W, H = 1200, 630
    base = Image.new("RGB", (W, H), (31, 58, 46))
    foto = Image.open(os.path.join(IMG, "adelaine-vertical.jpg")).convert("RGB")
    alvo_w = 470
    foto = foto.resize((alvo_w, int(foto.height * alvo_w / foto.width)), Image.LANCZOS)
    base.paste(foto.crop((0, 30, alvo_w, 30 + H)), (W - alvo_w, 0))
    # degradê para o texto não brigar com a foto
    sombra = Image.new("L", (160, H))
    d = ImageDraw.Draw(sombra)
    for x in range(160):
        d.line([(x, 0), (x, H)], fill=int(255 * (1 - x / 160)))
    base.paste(Image.new("RGB", (160, H), (31, 58, 46)), (W - alvo_w, 0), sombra)
    logo = Image.open(os.path.join(IMG, "logo-empatia-branca.png")).convert("RGBA")
    logo = logo.resize((250, int(logo.height * 250 / logo.width)), Image.LANCZOS)
    base.paste(logo, (70, 52), logo)
    d = ImageDraw.Draw(base)
    d.text((70, 250), "Estética integrativa", font=fonte(58, True), fill=(251, 250, 247))
    d.text((70, 318), "em Canaã dos Carajás", font=fonte(58, True), fill=(251, 250, 247))
    d.text((70, 410), "Dor · Vasinhos · Gordura localizada · Pele · Intestino", font=fonte(26), fill=(195, 204, 191))
    import math
    for i in range(5):  # estrelas desenhadas (a fonte do Windows não tem o caractere ★)
        cx, cy, r1, r2 = 84 + i * 30, 487, 13, 5.5
        pts = [(cx + (r1 if k % 2 == 0 else r2) * math.sin(k * math.pi / 5), cy - (r1 if k % 2 == 0 else r2) * math.cos(k * math.pi / 5)) for k in range(10)]
        d.polygon(pts, fill=(217, 171, 99))
    d.text((235, 470), "5,0 no Google", font=fonte(28, True), fill=(217, 171, 99))
    d.text((70, 530), "Dra. Adelaine Montel · Biomédica · CRBM 1437", font=fonte(24), fill=(195, 204, 191))
    base.save(os.path.join(IMG, "og-empatia.jpg"), "JPEG", quality=86, optimize=True, progressive=True)
    print("og-empatia.jpg", os.path.getsize(os.path.join(IMG, "og-empatia.jpg")) // 1024, "KB")


if __name__ == "__main__":
    webp()
    og()
