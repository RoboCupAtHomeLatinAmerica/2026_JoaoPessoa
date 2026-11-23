#!/usr/bin/env python3
"""Importa as fotos de objetos de uma pasta (ex.: baixadas do Drive) para o site.

Para cada foto: recorta um quadrado em volta do objeto, salva em
  Photos/objects/<Categoria>/<Nome>.jpg      (600x600, usado no site)
e reescreve Photos/objects/index.csv (uma coluna por categoria).
Depois rode:  python3 tools/make_thumbs.py

Uso:  python3 tools/import_objects.py <pasta_com_as_fotos> [--preview <arquivo.jpg>]
O mapeamento (foto -> categoria/nome/recorte) está em OBJECTS abaixo; edite-o para ajustar.
"""
import csv, sys, unicodedata
from pathlib import Path
from PIL import Image, ImageDraw, ImageOps

ROOT = Path(__file__).resolve().parent.parent
OBJ = ROOT / "Photos" / "objects"
CATEGORIES = ["Drinks", "Cleaning supplies", "Pantry items", "Fruits", "Snacks", "Personal care", "Tableware", "Others"]
SIZE = 600

# foto (hora do arquivo) -> (categoria, nome, centro x, centro y, lado do quadrado) em pixels da foto 1080x1440
OBJECTS = {
    "092456": ("Cleaning supplies", "Bom Bril", 527, 643, 1000),
    "092547": ("Cleaning supplies", "Scotch-Brite", 522, 740, 915),
    "092600": ("Cleaning supplies", "Furniture polish", 540, 638, 900),
    "092611": ("Cleaning supplies", "Limpol", 553, 694, 1180),
    "092652": ("Cleaning supplies", "Cloth", 558, 784, 1150),
    "092858": ("Personal care", "Even toothpaste", 604, 648, 830),
    "092921": ("Personal care", "Even soap", 553, 656, 735),
    "093012": ("Personal care", "Sanitary pad", 571, 553, 700),
    "093257": ("Drinks", "Parmalat milk", 553, 540, 700),
    "093316": ("Drinks", "Coconut water", 530, 700, 700),
    "093354": ("Drinks", "Indaiá Guaraná", 540, 648, 820),
    "093650": ("Drinks", "Indaiá Coke", 560, 591, 700),
    "093723": ("Drinks", "Yakult", 540, 681, 600),
    "093953": ("Pantry items", "Tomato extract", 522, 668, 550),
    "094007": ("Snacks", "Tortinhas", 540, 597, 750),
    "094216": ("Snacks", "Pocket chips", 545, 604, 650),
    "094230": ("Snacks", "Japanese peanuts", 545, 612, 700),
    "094302": ("Snacks", "White chocolate", 553, 663, 650),
    "094405": ("Snacks", "Kinder Joy", 540, 635, 700),
    "094422": ("Pantry items", "Vegetable broth", 553, 602, 600),
    "094438": ("Pantry items", "Instant coffee", 522, 674, 700),
    "094455": ("Pantry items", "Tambaú sauce", 525, 638, 750),
    "094539": ("Fruits", "Plum", 540, 674, 500),
    "094652": ("Fruits", "Kiwi", 560, 712, 550),
    "094734": ("Fruits", "Lime", 571, 674, 500),
    "094815": ("Fruits", "Green apple", 537, 674, 500),
    # fotos de 23/11 (fotos do dia 23 em paisagem: 1440x1080; lado máximo do recorte = 1080)
    "132602": ("Others", "Reusable bag", 540, 665, 1080),
    "132802": ("Tableware", "Plate", 532, 755, 950),
    "132811": ("Tableware", "Bowl", 765, 512, 1000),
    "132843": ("Tableware", "Cup", 547, 623, 800),
    "132855": ("Snacks", "Cereal", 520, 706, 700),
    "133008": ("Tableware", "Fork", 675, 477, 900),
    "133015": ("Tableware", "Knife", 755, 503, 900),
    "133020": ("Tableware", "Spoon", 765, 477, 900),
}


def square(im, cx, cy, side):
    w, h = im.size
    side = min(side, w, h)
    x0 = min(max(cx - side // 2, 0), w - side)
    y0 = min(max(cy - side // 2, 0), h - side)
    return im.crop((x0, y0, x0 + side, y0 + side))


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    preview = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    if preview:
        args = [a for a in args if a != preview]
    src = Path(args[0])
    files = {f.stem.split("_")[-1]: f for f in src.glob("IMG_*.jpg")}
    missing = [k for k in OBJECTS if k not in files]
    if missing:
        sys.exit(f"Fotos não encontradas em {src}: {missing}")

    tiles = []
    columns = {c: [] for c in CATEGORIES}
    for key, (cat, name, cx, cy, side) in sorted(OBJECTS.items()):
        name = unicodedata.normalize("NFC", name)
        with Image.open(files[key]) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            crop = square(im, cx, cy, side).resize((SIZE, SIZE), Image.LANCZOS)
        if preview:
            t = crop.resize((300, 300)); ImageDraw.Draw(t).text((6, 6), f"{cat}/{name}", fill="yellow"); tiles.append(t)
            continue
        (OBJ / cat).mkdir(parents=True, exist_ok=True)
        crop.save(OBJ / cat / f"{name}.jpg", "JPEG", quality=85, optimize=True)
        columns[cat].append(f"{name}.jpg")

    if preview:
        cols = 6
        sheet = Image.new("RGB", (300 * cols, 300 * ((len(tiles) + cols - 1) // cols)), "white")
        for i, t in enumerate(tiles):
            sheet.paste(t, ((i % cols) * 300, (i // cols) * 300))
        sheet.save(preview, quality=88)
        print("preview:", preview)
        return

    rows = max(len(v) for v in columns.values())
    with open(OBJ / "index.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(CATEGORIES)
        for r in range(rows):
            w.writerow([columns[c][r] if r < len(columns[c]) else "" for c in CATEGORIES])
    print(f"{sum(len(v) for v in columns.values())} objetos em {len(CATEGORIES)} categorias; index.csv atualizado")


if __name__ == "__main__":
    main()
