#!/usr/bin/env python3
"""Gera o cardápio da prova Restaurant (Photos/menu/restaurant-menu.png) com as bebidas e os itens
comestíveis da tabela de objetos (Photos/objects/index.csv).

Uso:  python3 tools/make_menu.py     (rode de novo se a lista de objetos mudar)
"""
import csv
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OBJ = ROOT / "Photos" / "objects"
OUT = ROOT / "Photos" / "menu" / "restaurant-menu.png"
# categorias do cardápio (sem os itens de despensa), na ordem em que aparecem
SECTIONS = {"Drinks": ["Drinks"], "Foods": ["Snacks", "Fruits"]}   # título no cardápio -> categorias da tabela

FONTS = Path("/usr/share/fonts/truetype/dejavu")
font = lambda name, size: ImageFont.truetype(str(FONTS / name), size)
W, MARGIN, COLS, PHOTO, GAP = 1240, 50, 6, 164, 30
BG, INK, SOFT, ACCENT, LINE = (253, 250, 243), (41, 33, 28), (110, 96, 86), (150, 48, 38), (214, 198, 176)
Z = 2  # desenha em dobro e reduz (texto e cantos mais suaves)


def main():
    with open(OBJ / "index.csv", encoding="utf-8") as f:
        table = list(csv.reader(f))
    head = table[0]
    sections = []
    for name, categories in SECTIONS.items():
        items = []   # cada item guarda a pasta da categoria de origem
        for cat in categories:
            i = head.index(cat)
            items += [(cat, r[i]) for r in table[1:] if i < len(r) and r[i].strip()]
        if items:
            sections.append((name, items))

    cell_w = (W - 2 * MARGIN) / COLS
    row_h = PHOTO + 52
    height = 190 + sum(76 + row_h * ((len(it) + COLS - 1) // COLS) + GAP for _, it in sections) + 40
    img = Image.new("RGB", (W * Z, height * Z), BG)
    d = ImageDraw.Draw(img)
    S = lambda *v: tuple(int(x * Z) for x in v)

    # moldura e título
    d.rectangle(S(16, 16, W - 16, height - 16), outline=ACCENT, width=3 * Z)
    d.rectangle(S(24, 24, W - 24, height - 24), outline=LINE, width=Z)
    d.text(S(W / 2, 82), "Restaurant Menu", font=font("DejaVuSerif-Bold.ttf", 54 * Z), fill=ACCENT, anchor="mm")
    d.text(S(W / 2, 140), "RoboCup@Home Brazil Open 2026", font=font("DejaVuSerif.ttf", 22 * Z), fill=SOFT, anchor="mm")

    y = 190
    for title, items in sections:
        tf = font("DejaVuSerif-Bold.ttf", 30 * Z)
        d.text(S(W / 2, y + 26), title, font=tf, fill=INK, anchor="mm")
        half = d.textlength(title, font=tf) / Z / 2 + 24
        d.line(S(MARGIN + 20, y + 28, W / 2 - half, y + 28), fill=LINE, width=2 * Z)
        d.line(S(W / 2 + half, y + 28, W - MARGIN - 20, y + 28), fill=LINE, width=2 * Z)
        y += 76
        rows = [items[i:i + COLS] for i in range(0, len(items), COLS)]
        for row in rows:
            x0 = MARGIN + (COLS - len(row)) * cell_w / 2          # centraliza a linha
            for k, (folder, file) in enumerate(row):
                cx = x0 + k * cell_w + cell_w / 2
                photo = Image.open(OBJ / folder / file).convert("RGB").resize(S(PHOTO, PHOTO), Image.LANCZOS)
                mask = Image.new("L", photo.size, 0)
                ImageDraw.Draw(mask).rounded_rectangle((0, 0, *photo.size), radius=14 * Z, fill=255)
                img.paste(photo, S(cx - PHOTO / 2, y), mask)
                d.rounded_rectangle(S(cx - PHOTO / 2, y, cx + PHOTO / 2, y + PHOTO), radius=14 * Z, outline=LINE, width=2 * Z)
                label, size = Path(file).stem, 20
                while d.textlength(label, font=font("DejaVuSerif.ttf", size * Z)) > (cell_w - 8) * Z and size > 12:
                    size -= 1
                d.text(S(cx, y + PHOTO + 22), label, font=font("DejaVuSerif.ttf", size * Z), fill=INK, anchor="mm")
            y += row_h
        y += GAP

    OUT.parent.mkdir(parents=True, exist_ok=True)
    img.resize((W, height), Image.LANCZOS).save(OUT, optimize=True)
    print(f"{sum(len(i) for _, i in sections)} itens em {len(sections)} seções -> {OUT.relative_to(ROOT)} ({W}x{height}, {OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
