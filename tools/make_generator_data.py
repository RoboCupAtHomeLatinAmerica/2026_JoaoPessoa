#!/usr/bin/env python3
"""Gera a pasta command_generator/ (dados do CommandGenerator oficial para o GPSR) a partir dos dados do site.

  command_generator/names/names.md            <- csv/people.csv
  command_generator/objects/objects.md        <- Photos/objects/index.csv
  command_generator/maps/location_names.md    <- LOCATIONS abaixo (mesma numeração da planta "Arena locations")
  command_generator/maps/room_names.md        <- ROOMS abaixo

Uso:  python3 tools/make_generator_data.py
Depois: athome-generator -d command_generator   (ou athome-generator-gpsr-ui -d command_generator)
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "command_generator"

ROOMS = ["bedroom", "home office", "balcony", "laundry", "living room", "kitchen"]

# (número na planta, nome, pode receber objetos, categoria guardada ali)
# Ficam de fora do gerador os móveis repetidos (2 e 3, criados-mudos; 7 e 8, poltronas da varanda).
LOCATIONS = [
    (1, "bed", True, ""),
    (4, "desk", True, ""), (5, "office chair", False, ""), (6, "trash bin", False, ""),
    (9, "coffee table", True, "snacks"),
    (10, "side cabinet", True, "drinks"), (11, "washing machine", True, ""), (12, "ironing board", True, ""),
    (13, "laundry basket", False, ""), (14, "dining table", True, ""), (15, "sofa", True, ""),
    (16, "armchair", True, ""), (17, "shelf", True, "pantry items"), (18, "tv stand", True, ""),
    (19, "dishwasher", True, ""), (20, "sink", True, "cleaning supplies"), (21, "kitchen table", True, "fruits"),
    (22, "refrigerator", False, ""), (23, "kitchen trash bin", False, ""),
]

# coluna do index.csv -> (plural, singular) usados nos comandos.
# Ficam de fora "Others" ("other item" não faz sentido) e "Personal care".
CATEGORIES = {
    "Drinks": ("drinks", "drink"),
    "Cleaning supplies": ("cleaning supplies", "cleaning supply"),
    "Pantry items": ("pantry items", "pantry item"),
    "Fruits": ("fruits", "fruit"),
    "Snacks": ("snacks", "snack"),
    "Tableware": ("tableware items", "tableware item"),
}


# objetos do site que não entram nos comandos (o nome não é lido pelo gerador sem ajuste)
EXCLUDE_OBJECTS = {"Scotch-Brite"}


def token(name):
    """O leitor do gerador só aceita letras, números e '_' em nomes de objeto (o '_' vira espaço)."""
    return re.sub(r"_+", "_", re.sub(r"[^\w]", "_", name.strip())).strip("_")


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main():
    # nomes: uma coluna única; o leitor só aceita uma palavra com letras A-Z por nome
    with open(ROOT / "csv" / "people.csv", encoding="utf-8") as f:
        rows = list(csv.reader(f))[1:]
    names = [c.strip() for r in rows for c in r[1:] if c.strip()]
    bad = [n for n in names if not re.fullmatch(r"[A-Za-z]+", n)]
    if bad:
        raise SystemExit(f"Nomes que o gerador não lê (só letras A-Z, uma palavra): {bad}")
    write(OUT / "names" / "names.md", "## Names\n| Names |\n| ----- |\n" + "".join(f"| {n} |\n" for n in names))

    write(OUT / "maps" / "room_names.md", "## Rooms\n| Name |\n| ---- |\n" + "".join(f"| {r} |\n" for r in ROOMS))

    lines = "".join(f"| {n} | {name}{' (p)' if p else ''} | {cat} |\n" for n, name, p, cat in LOCATIONS)
    write(OUT / "maps" / "location_names.md",
          "## Locations\n| Number | Name | Object Category |\n| ------ | ---- | --------------- |\n" + lines +
          "\n(p) indicates whether objects can be placed at the location\n")

    with open(ROOT / "Photos" / "objects" / "index.csv", encoding="utf-8") as f:
        table = list(csv.reader(f))
    head = table[0]
    out = ["# Objects\n"]
    for col, (plural, singular) in CATEGORIES.items():
        i = head.index(col)
        objs = [Path(r[i]).stem for r in table[1:] if i < len(r) and r[i].strip() and Path(r[i]).stem not in EXCLUDE_OBJECTS]
        out.append(f"# Class {token(plural)} ({token(singular)})\n\n| Objectname | Image |\n| ---------- | ----- |\n" +
                   "".join(f"| {token(o)} |  |\n" for o in objs) + "\n")
    write(OUT / "objects" / "objects.md", "".join(out))
    print(f"{len(names)} nomes, {len(ROOMS)} ambientes, {len(LOCATIONS)} locais, {len(CATEGORIES)} categorias -> {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
