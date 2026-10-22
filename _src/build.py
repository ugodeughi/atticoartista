#!/usr/bin/env python3
"""Genera le pagine del sito in tutte le lingue.

Uso:  python3 _src/build.py
Legge i testi da _src/i18n/<lingua>.json e scrive index.html (italiano)
e <lingua>/index.html per le altre lingue.
"""
import html, json, os, re, struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LANGS = ["it", "en", "de", "fr", "es"]  # il primo è la lingua principale (radice del sito)
# Dominio definitivo, senza barra finale (es. "https://www.atticodellartista.it").
# Serve per hreflang/canonical/og:image assoluti. Vuoto = percorsi relativi alla radice.
BASE = ""

PHONE = "+393355858642"
EMAIL = "ateliermazzola@gmail.com"
SITE = "https://www.annamazzola.it"
MAPS = "https://www.google.com/maps/search/?api=1&query=Via+Arcipreturale+36+Ghiffa+VB"


# ---------- immagini: leggo larghezze/altezze dai file WebP ----------
def webp_size(p):
    b = p.read_bytes()[:40]
    if b[12:16] == b"VP8 ":
        w, h = struct.unpack("<HH", b[26:30]); return w & 0x3FFF, h & 0x3FFF
    if b[12:16] == b"VP8L":
        v = int.from_bytes(b[21:25], "little"); return (v & 0x3FFF) + 1, ((v >> 14) & 0x3FFF) + 1
    if b[12:16] == b"VP8X":
        return int.from_bytes(b[24:27], "little") + 1, int.from_bytes(b[27:30], "little") + 1
    raise ValueError(p)

SZ = {}
for f in (ROOT / "img").glob("*.webp"):
    m = re.match(r"(.+)-(\d+)\.webp$", f.name)
    name, w = m.group(1), int(m.group(2))
    SZ.setdefault(name, {})[w] = f
SZ = {n: (sorted(ws), webp_size(ws[max(ws)])) for n, ws in SZ.items()}

esc = lambda s: html.escape(s, quote=True)


def build(lang):
    T = json.loads((ROOT / "_src/i18n" / f"{lang}.json").read_text("utf-8"))
    P = "" if lang == LANGS[0] else "../"          # prefisso verso la radice
    url = lambda l: f"{BASE}/" if l == LANGS[0] else f"{BASE}/{l}/"
    rel = lambda l: (P or "./") if l == LANGS[0] else f"{P}{l}/"

    def srcset(n):
        ws, _ = SZ[n]; return ", ".join(f"{P}img/{n}-{w}.webp {w}w" for w in ws)

    def pic(n, alt, sizes="(max-width: 800px) 100vw, 50vw", cls="", lb=True):
        ws, (w, h) = SZ[n]
        a = (f'<img src="{P}img/{n}-{ws[0]}.webp" srcset="{srcset(n)}" sizes="{sizes}" '
             f'width="{w}" height="{h}" alt="{esc(alt)}" loading="lazy" decoding="async"'
             + (f' class="{cls}"' if cls else "") + ">")
        if lb:
            a = f'<a href="{P}img/{n}-{ws[-1]}.webp" class="lb" data-cap="{esc(alt)}">{a}</a>'
        return a

    def bg(n, alt=""):
        ws, (w, h) = SZ[n]
        return (f'<img class="oh-bg" src="{P}img/{n}-{ws[0]}.webp" srcset="{srcset(n)}" sizes="100vw" '
                f'width="{w}" height="{h}" alt="{esc(alt)}" loading="lazy" decoding="async">')

    # --- blocchi ripetuti ---
    vista = "".join(
        f'<figure class="g-item{" wide" if i in (1, 6, 11, 16) else ""}">'
        f'{pic(f"vista-{i:02d}", a, "(max-width: 700px) 100vw, 33vw")}</figure>'
        for i, a in enumerate(T["vista_alts"], 1))

    amen = "".join(
        f'<article class="card">{pic(img, T[k+"_t"], "(max-width: 700px) 100vw, 33vw")}'
        f'<div class="card-b"><h3>{T[k+"_t"]}</h3><p>{T[k+"_p"]}</p></div></article>'
        for img, k in [("piscina", "am_piscina"), ("spiaggia", "am_spiaggia"), ("porto", "am_porto"),
                       ("tennis", "am_tennis"), ("parco-1", "am_parco"), ("garage-accesso", "am_garage")])

    mini = "".join(f'<figure>{pic(n, a, "(max-width: 700px) 50vw, 20vw")}</figure>'
                   for n, a in zip(["parco-2", "parco-4", "parco-3", "parco-5", "pontile"], T["mini_alts"]))

    def room(i, t, p):
        r = f"r{i}"
        def layer(kind, alt, cls=""):
            n = f"{r}-{kind}"; ws, (w, h) = SZ[n]
            return (f'<img{cls} src="{P}img/{n}-{ws[0]}.webp" srcset="{srcset(n)}" '
                    f'sizes="(max-width: 900px) 100vw, 60vw" width="{w}" height="{h}" '
                    f'alt="{esc(t)}, {esc(alt)}" loading="lazy" decoding="async">')
        return (f'<article class="room"><div class="ba" style="--p:50%">'
                f'{layer("arredata", T["ba_alt_full"])}{layer("vuota", T["ba_alt_empty"], " class=\"ba-top\"")}'
                f'<span class="ba-l">{T["ba_left"]}</span><span class="ba-r">{T["ba_right"]}</span>'
                f'<input type="range" min="0" max="100" value="50" aria-label="{esc(T["ba_aria"].format(t=t))}"></div>'
                f'<div class="room-t"><span class="num">{i}</span><h3>{t}</h3><p>{p}</p></div></article>')
    rooms = "".join(room(i, t, p) for i, (t, p) in enumerate(T["rooms"], 1))

    tags = "".join(f"<li>{x}</li>" for x in T["man_tags"])
    legend = "".join(f"<li>{x}</li>" for x in T["plan_legend"])
    details = "".join(f"<article><h3>{h}</h3><p>{p}</p></article>" for h, p in T["details"])
    steps = "".join(f"<li><span>{i:02d}</span><h3>{h}</h3><p>{p}</p></li>"
                    for i, (h, p) in enumerate(T["steps"], 1))

    # selettore lingua (i link portano i testi per il suggerimento automatico)
    others = {l: json.loads((ROOT / "_src/i18n" / f"{l}.json").read_text("utf-8")) for l in LANGS}
    switch = "".join(
        f'<a href="{rel(l)}" hreflang="{l}" lang="{l}" title="{esc(others[l]["lang_name"])}"'
        + (' aria-current="true"' if l == lang else
           f' data-s="{esc(others[l]["suggest"])}" data-go="{esc(others[l]["suggest_go"])}"')
        + f">{l.upper()}</a>" for l in LANGS)
    alternates = "\n".join(f'<link rel="alternate" hreflang="{l}" href="{url(l)}">' for l in LANGS)
    alternates += f'\n<link rel="alternate" hreflang="x-default" href="{url(LANGS[0])}">'

    hero_ws, (hw, hh) = SZ["hero"]
    hero_ss = srcset("hero")
    og_img = f"{BASE}/img/hero-{hero_ws[-1]}.webp"

    ld = {"@context": "https://schema.org", "@type": "RealEstateListing", "inLanguage": lang,
          "name": T["ld_name"], "description": T["ld_desc"], "url": url(lang), "image": og_img,
          "offers": {"@type": "Offer", "price": 730000, "priceCurrency": "EUR",
                     "availability": "https://schema.org/InStock"},
          "itemOffered": {"@type": "Apartment", "numberOfRooms": 4, "numberOfBedrooms": 3,
                          "numberOfBathroomsTotal": 2,
                          "floorSize": {"@type": "QuantitativeValue", "value": 110, "unitCode": "MTK"},
                          "address": {"@type": "PostalAddress", "streetAddress": "Via Arcipreturale 36",
                                      "addressLocality": "Ghiffa", "addressRegion": "VB",
                                      "postalCode": "28823", "addressCountry": "IT"}},
          "seller": {"@type": "Person", "name": "Anna Mazzola", "telephone": PHONE,
                     "email": EMAIL, "url": SITE}}

    from urllib.parse import quote
    wa = f"https://wa.me/{PHONE[1:]}?text={quote(T['ct_wa_text'])}"
    mail = f"mailto:{EMAIL}?subject={quote(T['ct_mail_subject'])}"

    return f'''<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(T["title"])}</title>
<meta name="description" content="{esc(T["meta_desc"])}">
<meta name="theme-color" content="#24474f">
<link rel="canonical" href="{url(lang)}">
{alternates}
<link rel="icon" href="{P}img/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="{P}img/apple-touch-icon.png">
<meta property="og:type" content="website">
<meta property="og:title" content="{esc(T["og_title"])}">
<meta property="og:description" content="{esc(T["og_desc"])}">
<meta property="og:image" content="{og_img}">
<meta property="og:url" content="{url(lang)}">
<meta property="og:locale" content="{T["locale"]}">
{"".join(f'<meta property="og:locale:alternate" content="{others[l]["locale"]}">' for l in LANGS if l != lang)}
<link rel="preload" as="image" href="{P}img/hero-{hero_ws[0]}.webp" imagesrcset="{hero_ss}" imagesizes="100vw" fetchpriority="high">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Jost:wght@300;400;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{P}style.css">
<script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
</head>
<body>
<a class="skip" href="#main">{T["skip"]}</a>
<header class="nav" id="top">
  <a class="brand" href="#top" aria-label="{esc(T["home_aria"])}"><img src="{P}img/logo-125.webp" width="36" height="36" alt=""><span>{T["brand"]}</span></a>
  <div class="langs" role="navigation" aria-label="{esc(T["lang_label"])}">{switch}</div>
  <button class="burger" aria-label="{esc(T["menu_open"])}" aria-expanded="false" aria-controls="menu"><span></span><span></span></button>
  <nav id="menu">
    <a href="#vista">{T["nav_vista"]}</a><a href="#residence">{T["nav_residence"]}</a><a href="#mansarda">{T["nav_mansarda"]}</a><a href="#architetto">{T["nav_architetto"]}</a><a href="#proposta">{T["nav_proposta"]}</a><a href="#contatti" class="btn btn-s">{T["nav_cta"]}</a>
  </nav>
</header>

<main id="main">
<section class="hero">
  <img class="hero-bg" src="{P}img/hero-{hero_ws[0]}.webp" srcset="{hero_ss}" sizes="100vw" width="{hw}" height="{hh}" alt="{esc(T["hero_alt"])}" fetchpriority="high">
  <div class="hero-c wrap">
    <p class="kicker">{T["hero_kicker"]}</p>
    <h1>{T["hero_h1"]}</h1>
    <p class="hero-sub">{T["hero_sub"]}<br><em>{T["hero_by"]}</em></p>
    <div class="hero-cta"><a href="#contatti" class="btn">{T["hero_cta1"]}</a><a href="#vista" class="btn btn-ghost">{T["hero_cta2"]}</a></div>
  </div>
</section>

<section class="intro wrap">
  <div class="intro-t">
    <h2 class="h-lite">{T["intro_h2"]}</h2>
    <p>{T["intro_p1"]}</p>
    <p>{T["intro_p2"]}</p>
  </div>
  <figure class="intro-art">{pic("intro-art", T["intro_art_alt"], "(max-width: 800px) 60vw, 300px", lb=False)}</figure>
</section>

<section class="facts" aria-label="{esc(T["facts_aria"])}">
  <ul class="wrap">
    <li><b>110 m²</b><span>{T["fact_m2"]}</span></li>
    <li><b>3</b><span>{T["fact_rooms"]}</span></li>
    <li><b>1</b><span>{T["fact_office"]}</span></li>
    <li><b>2</b><span>{T["fact_baths"]}</span></li>
    <li><b>3</b><span>{T["fact_loggias"]}</span></li>
    <li><b>+</b><span>{T["fact_extra"]}</span></li>
  </ul>
</section>

<section id="vista" class="sec dark">
  <div class="wrap">
    <p class="eyebrow">{T["vista_eyebrow"]}</p>
    <h2 class="h-lite">{T["vista_h2"]}</h2>
    <p class="lead">{T["vista_p1"]}</p>
    <p class="lead">{T["vista_p2"]}</p>
    <div class="gallery">{vista}</div>
  </div>
</section>

<section id="residence" class="sec">
  <div class="wrap split">
    <div>
      <p class="eyebrow">{T["res_eyebrow"]}</p>
      <h2 class="h-lite">{T["res_h2"]}</h2>
      <p>{T["res_p1"]}</p>
      <p>{T["res_p2"]}</p>
    </div>
    <figure>{pic("silenzio", T["res_silenzio_alt"], "(max-width: 800px) 100vw, 45vw")}</figure>
  </div>
  <div class="wrap trio">
    <figure>{pic("edificio-1", T["res_ed1_alt"], "(max-width: 700px) 100vw, 33vw")}</figure>
    <figure>{pic("edificio-2", T["res_ed2_alt"], "(max-width: 700px) 100vw, 33vw")}</figure>
    <figure>{pic("edificio-3", T["res_ed3_alt"], "(max-width: 700px) 100vw, 33vw")}</figure>
  </div>
  <div class="wrap cards">{amen}</div>
  <div class="wrap mini">{mini}</div>
  <div class="wrap split map">
    <figure>{pic("mappa", T["map_alt"], "(max-width: 800px) 100vw, 60vw")}</figure>
    <div>
      <p class="eyebrow">{T["map_eyebrow"]}</p>
      <h3>{T["map_h3"]}</h3>
      <p>{T["map_p"]}</p>
      <a class="link" href="{MAPS}" target="_blank" rel="noopener">{T["map_link"]}</a>
    </div>
  </div>
</section>

<section id="mansarda" class="sec cream">
  <div class="wrap split">
    <div>
      <p class="eyebrow">{T["man_eyebrow"]}</p>
      <h2 class="h-lite">{T["man_h2"]}</h2>
      <p>{T["man_p"]}</p>
      <ul class="tags">{tags}</ul>
    </div>
    <figure>{pic("mansarda", T["man_alt"], "(max-width: 800px) 100vw, 45vw")}</figure>
  </div>

  <div class="wrap">
    <h3 class="sub">{T["rooms_h3"]}</h3>
    <p class="muted">{T["rooms_hint"]}</p>
    <div class="rooms">{rooms}</div>
  </div>

  <div class="wrap split plan">
    <figure>{pic("pianta", T["plan_alt"], "(max-width: 800px) 100vw, 60vw")}</figure>
    <div>
      <h3 class="sub">{T["plan_h3"]}</h3>
      <ol class="legend">{legend}</ol>
    </div>
  </div>

  <div class="wrap details">{details}</div>

  <div class="wrap duo">
    <figure>{pic("catasto-attico", T["cat_alt_prefix"] + ": " + T["cat_attico"], "(max-width: 700px) 50vw, 25vw")}<figcaption>{T["cat_attico"]}</figcaption></figure>
    <figure>{pic("catasto-cantina", T["cat_alt_prefix"] + ": " + T["cat_cantina"], "(max-width: 700px) 50vw, 25vw")}<figcaption>{T["cat_cantina"]}</figcaption></figure>
  </div>
</section>

<section id="architetto" class="sec dark">
  <div class="wrap">
    <p class="eyebrow">{T["arch_eyebrow"]}</p>
    <h2 class="h-lite">{T["arch_h2"]}</h2>
    <p class="lead">{T["arch_lead"]}</p>
    <div class="trio roles">
      <figure>{pic("anna-imprenditrice", "Anna Mazzola · " + T["role_1"], "(max-width: 700px) 100vw, 33vw", lb=False)}<figcaption>{T["role_1"]}</figcaption></figure>
      <figure>{pic("anna-direttrice", "Anna Mazzola · " + T["role_2"], "(max-width: 700px) 100vw, 33vw", lb=False)}<figcaption>{T["role_2"]}</figcaption></figure>
      <figure>{pic("anna-artista", "Anna Mazzola · " + T["role_3"], "(max-width: 700px) 100vw, 33vw", lb=False)}<figcaption>{T["role_3"]}</figcaption></figure>
    </div>
    <blockquote>{T["arch_quote"]}<cite>{T["arch_cite"]}</cite></blockquote>
  </div>
</section>

<section id="su-misura" class="sec">
  <div class="wrap">
    <p class="eyebrow">{T["mis_eyebrow"]}</p>
    <h2 class="h-lite">{T["mis_h2"]}</h2>
    <p class="lead">{T["mis_p1"]}</p>
    <p class="lead">{T["mis_p2"]}</p>
    <div class="trio styles">
      {"".join(f'<figure>{pic(n, T["style_alt_prefix"] + ": " + T[k], "(max-width: 700px) 100vw, 33vw")}<figcaption>{T[k]}</figcaption></figure>' for n, k in [("stile-classico", "style_1"), ("stile-impero", "style_2"), ("stile-country", "style_3")])}
    </div>
    <p class="note">{T["mis_note"]}</p>
  </div>
</section>

<section id="garage" class="sec cream">
  <div class="wrap split">
    <div>
      <p class="eyebrow">{T["gar_eyebrow"]}</p>
      <h2 class="h-lite">{T["gar_h2"]}</h2>
      <h3>{T["gar_h3a"]}</h3>
      <p>{T["gar_pa"]}</p>
      <h3>{T["gar_h3b"]}</h3>
      <p>{T["gar_pb"]}</p>
      <p class="muted">{T["gar_value"].format(p=T["price_80"])}</p>
    </div>
    <figure class="narrow">{pic("garage-pianta", T["gar_alt"], "(max-width: 800px) 80vw, 340px")}</figure>
  </div>
</section>

<section id="test" class="sec dark">
  <div class="wrap">
    <p class="eyebrow">{T["test_eyebrow"]}</p>
    <h2 class="h-lite">{T["test_h2"]}</h2>
    <p class="lead">{T["test_lead"]}</p>
    <p class="kicker">{T["test_kicker"]}</p>
    <ol class="steps">{steps}</ol>
    <p class="note">{T["test_note"]}</p>
  </div>
</section>

<section id="open-house" class="sec oh">
  {bg("openhouse")}
  <div class="wrap oh-c">
    <p class="eyebrow">{T["oh_eyebrow"]}</p>
    <h2 class="h-lite">{T["oh_h2"]}</h2>
    <p>{T["oh_p"]}</p>
    <a href="#contatti" class="btn">{T["oh_cta"]}</a>
  </div>
</section>

<section id="proposta" class="sec">
  <div class="wrap">
    <p class="eyebrow">{T["pr_eyebrow"]}</p>
    <h2 class="h-lite">{T["pr_h2"]}</h2>
    <div class="price">
      <div class="price-main"><span>{T["pr_main"]}</span><b>{T["price_730"]}</b></div>
      <div class="price-row"><span>{T["pr_row1"]}</span><b>{T["price_650"]}</b></div>
      <div class="price-row"><span>{T["pr_row2"]}</span><b>{T["price_80"]}</b></div>
      <div class="price-row"><span><em>{T["pr_row3"]}</em></span><b>{T["pr_on_request"]}</b></div>
    </div>
    <p class="note">{T["pr_note"]}</p>
  </div>
</section>

<section id="contatti" class="contact">
  {bg("contact")}
  <div class="contact-c">
    {pic("anna-ritratto", "Anna Mazzola", "160px", cls="avatar", lb=False)}
    <h2 class="h-lite">{T["ct_h2"]}</h2>
    <p><strong>Anna Mazzola</strong> · {T["ct_role"]}</p>
    <div class="contact-cta">
      <a class="btn" href="tel:{PHONE}">{T["ct_call"]}</a>
      <a class="btn btn-ghost" href="{wa}" target="_blank" rel="noopener">WhatsApp</a>
      <a class="btn btn-ghost" href="{mail}">{EMAIL}</a>
    </div>
    <p><a class="link" href="{SITE}" target="_blank" rel="noopener">www.annamazzola.it</a></p>
  </div>
</section>
</main>

<footer class="foot wrap">
  <p>{T["foot_1"]}</p>
  <p>{T["foot_2"]}</p>
  <p class="foot-langs">{switch}</p>
</footer>

<dialog id="lb" aria-label="{esc(T["lb_aria"])}">
  <button class="lb-x" aria-label="{esc(T["lb_close"])}">×</button>
  <button class="lb-p" aria-label="{esc(T["lb_prev"])}">‹</button>
  <figure><img alt=""><figcaption></figcaption></figure>
  <button class="lb-n" aria-label="{esc(T["lb_next"])}">›</button>
</dialog>
<script src="{P}app.js" defer></script>
</body>
</html>
'''


def main():
    ref = json.loads((ROOT / "_src/i18n/it.json").read_text("utf-8"))
    for lang in LANGS:
        T = json.loads((ROOT / "_src/i18n" / f"{lang}.json").read_text("utf-8"))
        missing = set(ref) - set(T)
        assert not missing, f"{lang}: chiavi mancanti {missing}"
        out = ROOT / ("index.html" if lang == LANGS[0] else f"{lang}/index.html")
        out.parent.mkdir(exist_ok=True)
        out.write_text(build(lang), "utf-8")
        print(f"{lang}: {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")
    # sitemap con alternative linguistiche
    if BASE:
        u = lambda l: f"{BASE}/" if l == LANGS[0] else f"{BASE}/{l}/"
        alts = "".join(f'<xhtml:link rel="alternate" hreflang="{l}" href="{u(l)}"/>' for l in LANGS)
        body = "".join(f"<url><loc>{u(l)}</loc>{alts}</url>" for l in LANGS)
        (ROOT / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
            f'xmlns:xhtml="http://www.w3.org/1999/xhtml">{body}</urlset>\n', "utf-8")
        print("sitemap.xml")


if __name__ == "__main__":
    main()
