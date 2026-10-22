#!/usr/bin/env python3
"""Genera le immagini di condivisione social (1200x630 JPG), una per lingua.

Uso:  python3 _src/og.py   (richiede Pillow: pip install pillow; font di sistema macOS)
Scrive img/og-<lingua>.jpg usando i testi di _src/i18n/<lingua>.json.
"""
import json, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
LANGS = ["it", "en", "de", "fr", "es"]
W, H = 1200, 630
FUTURA = "/System/Library/Fonts/Supplemental/Futura.ttc"
AVENIR = "/System/Library/Fonts/Avenir Next.ttc"
bold = lambda s: ImageFont.truetype(FUTURA, s, index=2)        # Futura Bold
light = lambda s: ImageFont.truetype(AVENIR, s, index=7)       # Avenir Next Regular
medium = lambda s: ImageFont.truetype(AVENIR, s, index=5)      # Avenir Next Medium
ACCENT = (224, 118, 43)


def background():
    im = Image.open(ROOT / "img/hero-1598.webp").convert("RGB")
    im = im.resize((W, round(im.height * W / im.width)), Image.LANCZOS)
    top = (im.height - H) // 2
    im = im.crop((0, top, W, top + H))
    # velatura scura a sinistra e in basso per leggere il testo
    shade = Image.new("L", (W, H))
    px = shade.load()
    for x in range(W):
        for y in range(H):
            a = max(0.0, 1 - x / (W * 0.85)) * 150 + (y / H) ** 2 * 90
            px[x, y] = min(200, int(a))
    im.paste(Image.new("RGB", (W, H), (14, 22, 26)), mask=shade)
    return im


def spaced(draw, xy, text, font, fill, tracking):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textlength(ch, font=font) + tracking
    return x


def fit(draw, lines, maxw, start):
    """Riduce il corpo finché tutte le righe del titolo stanno in larghezza."""
    s = start
    while s > 40:
        if all(draw.textlength(t, font=(bold(s) if i == 0 else light(s))) <= maxw for i, t in enumerate(lines)):
            return s
        s -= 2
    return s


def make(lang, bg, logo):
    T = json.loads((ROOT / "_src/i18n" / f"{lang}.json").read_text("utf-8"))
    im = bg.copy()
    d = ImageDraw.Draw(im)
    X = 72

    # logo + marchio
    im.paste(logo, (X, 56))
    spaced(d, (X + 62, 65), "ATTICO DELL'ARTISTA", medium(18), (255, 255, 255), 2.2)

    # kicker
    spaced(d, (X, 178), T["hero_kicker"].upper(), medium(17), (255, 255, 255), 2.6)

    # titolo: 3 righe, la prima in grassetto
    lines = [re.sub(r"<[^>]+>", "", p).upper() for p in T["hero_h1"].split("<br>")]
    s = fit(d, lines, W - X * 2 - 120, 76)
    y = 214
    for i, t in enumerate(lines):
        d.text((X, y), t, font=bold(s) if i == 0 else light(s), fill=(255, 255, 255))
        y += int(s * 1.08)

    # linea accento + sottotitolo + dati chiave
    y += 22
    d.rectangle((X, y, X + 56, y + 3), fill=ACCENT)
    spaced(d, (X, y + 22), T["hero_sub"].upper(), medium(21), (255, 255, 255), 1.4)
    facts = f"110 m²  ·  3 {T['fact_rooms']}  ·  2 {T['fact_baths']}  ·  {T['fact_extra']}"
    d.text((X, y + 60), facts, font=light(22), fill=(235, 235, 235))

    out = ROOT / f"img/og-{lang}.jpg"
    im.save(out, "JPEG", quality=84, optimize=True, progressive=True)
    print(out.relative_to(ROOT), out.stat().st_size // 1024, "KB")


if __name__ == "__main__":
    bg = background()
    logo = Image.open(ROOT / "img/logo-125.webp").convert("RGB").resize((46, 46), Image.LANCZOS)
    for l in LANGS:
        make(l, bg, logo)
