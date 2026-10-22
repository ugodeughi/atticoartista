# Attico dell'Artista – minisito multilingua

Sito statico (HTML + CSS + ~3 KB JS), nessun framework.
Lingue: italiano (`/`), inglese (`/en/`), tedesco (`/de/`), francese (`/fr/`), spagnolo (`/es/`).

## Modificare i testi
1. Modifica `_src/i18n/<lingua>.json` (stesse chiavi in tutti i file).
2. Rigenera le pagine:  `python3 _src/build.py`

## Prima della pubblicazione
In `_src/build.py` imposta `BASE = "https://tuodominio.it"` e rilancia lo script:
rende assoluti hreflang/canonical/og:image e genera `sitemap.xml`.

## Anteprima locale
`python3 -m http.server 8000` → http://localhost:8000

## Pubblicazione
Carica la cartella su un hosting statico (Netlify, Cloudflare Pages, GitHub Pages, FTP).
La cartella `_src` non serve online: puoi escluderla.
