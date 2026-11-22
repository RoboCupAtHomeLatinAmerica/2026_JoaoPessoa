#!/usr/bin/env python3
"""Gera versões leves (WebP) das imagens para o site.

  Photos/objects/<Categoria>/<arquivo>.PNG -> Photos/thumbs/objects/<Categoria>/<arquivo>.webp  (240px)
  Photos/robots/<arquivo>                   -> Photos/thumbs/robots/<arquivo sem ext>.webp      (480px)
  Photos/robots.jpg, Photos/teams.jpg       -> Photos/thumbs/<nome>.webp                         (1200px)
  Photos/og-image.jpg                       -> 1200x630 (pré-visualização ao compartilhar), a partir de teams.jpg

Os originais não são alterados. Rode de novo sempre que adicionar fotos:
    python3 tools/make_thumbs.py
"""
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
PHOTOS = ROOT / "Photos"
THUMBS = PHOTOS / "thumbs"
EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def make(src: Path, dst: Path, max_side: int, quality: int = 80) -> None:
    if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src) as im:
        im = ImageOps.exif_transpose(im)
        im.thumbnail((max_side, max_side), Image.LANCZOS)
        if im.mode not in ("RGB", "RGBA"):
            im = im.convert("RGBA" if "transparency" in im.info else "RGB")
        im.save(dst, "WEBP", quality=quality, method=6)
    print(f"{src.relative_to(ROOT)} -> {dst.relative_to(ROOT)} ({dst.stat().st_size // 1024} KB)")


def main() -> None:
    for f in sorted((PHOTOS / "objects").rglob("*")):
        if f.is_file() and f.suffix.lower() in EXTS and "originals" not in f.parts:
            make(f, THUMBS / "objects" / f.parent.name / (f.stem + ".webp"), 240)
    for f in sorted((PHOTOS / "robots").glob("*")):
        if f.is_file() and f.suffix.lower() in EXTS:
            make(f, THUMBS / "robots" / (f.stem + ".webp"), 480)
    for name in ("robots.jpg", "teams.jpg"):
        f = PHOTOS / name
        if f.exists():
            make(f, THUMBS / (f.stem + ".webp"), 1200)

    # og-image 1200x630 (corte central de teams.jpg)
    src, dst = PHOTOS / "teams.jpg", PHOTOS / "og-image.jpg"
    if src.exists() and not dst.exists():
        with Image.open(src) as im:
            im = ImageOps.fit(ImageOps.exif_transpose(im).convert("RGB"), (1200, 630), Image.LANCZOS)
            im.save(dst, "JPEG", quality=82, optimize=True)
        print(f"{dst.relative_to(ROOT)} ({dst.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
