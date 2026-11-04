"""Branded cover image for a blog post (1536x1024 WebP) - used when there is no real job photo.

Usage (from repo root):
  python .claude/blog/make_cover.py <slug> "<Title>" <category> [--photo path/to/photo.jpg]

With --photo the photo becomes the background (darkened) under the title, which is the best
option: real work photos beat generic graphics. Without it a clean navy/orange card is drawn.
Requires Pillow (pip install pillow). Fonts: Roboto (Apache 2.0) in .claude/blog/fonts/.
"""
import argparse
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[2]
FONTS = Path(__file__).resolve().parent / "fonts"
W, H = 1536, 1024
NAVY, ORANGE, WHITE = (30, 58, 95), (255, 107, 53), (255, 255, 255)
LABELS = {
    "plumbing": "PLUMBING & BATHROOM", "electrical": "LIGHTS & ELECTRICAL", "mounting": "MOUNTING & ASSEMBLY",
    "interior": "WALLS, DOORS & FLOORS", "outdoor": "OUTDOOR & CLEANUP", "home-bar": "HOME BAR & KEGERATOR",
    "guides": "HOMEOWNER GUIDES",
}


def font(name, size):
    return ImageFont.truetype(str(FONTS / f"Roboto-{name}.ttf"), size)


def background(photo):
    if photo:
        im = ImageOps.fit(ImageOps.exif_transpose(Image.open(photo)).convert("RGB"), (W, H))
        im = im.filter(ImageFilter.GaussianBlur(2))
        shade = Image.new("RGB", (W, H), NAVY)
        return Image.blend(im, shade, 0.62)
    im = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(im)
    for i in range(0, W + H, 64):  # subtle diagonal texture
        d.line([(i, 0), (i - H, H)], fill=(36, 66, 105), width=18)
    d.ellipse([W - 520, -260, W + 260, 520], outline=ORANGE, width=14)
    d.rectangle([W - 340, H - 300, W - 140, H - 100], outline=(255, 255, 255), width=10)
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("title")
    ap.add_argument("category", choices=list(LABELS))
    ap.add_argument("--photo")
    a = ap.parse_args()

    im = background(a.photo)
    d = ImageDraw.Draw(im)
    x = 110
    d.rectangle([x, 150, x + 120, 162], fill=ORANGE)
    d.text((x, 190), LABELS[a.category], font=font("Bold", 40), fill=ORANGE)

    size = 104
    for size in (104, 96, 88, 80, 72):
        lines = textwrap.wrap(a.title, width=int(1180 / (size * 0.52)))
        if len(lines) <= 4:
            break
    f = font("Black", size)
    y = 270
    for line in lines[:4]:
        d.text((x, y), line, font=f, fill=WHITE)
        y += int(size * 1.15)

    d.text((x, H - 150), "Nestor's Home Help", font=font("Black", 46), fill=WHITE)
    d.text((x, H - 92), "Licensed & insured handyman  |  Calgary, Airdrie, Chestermere, Okotoks, Cochrane",
           font=font("Bold", 30), fill=(200, 210, 225))

    out = ROOT / "assets" / "blog" / f"{a.slug}.webp"
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, "WEBP", quality=82, method=6)
    print(f"Saved {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
