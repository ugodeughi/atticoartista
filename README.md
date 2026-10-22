# Attico dell'Artista – minisito multilingua

Sito statico (HTML + CSS + ~3 KB JS), nessun framework.
Lingue: italiano (`/`), inglese (`/en/`), tedesco (`/de/`), francese (`/fr/`), spagnolo (`/es/`).

## Modificare i testi
1. Modifica `_src/i18n/<lingua>.json` (stesse chiavi in tutti i file).
2. Rigenera le pagine:  `python3 _src/build.py`
3. Se cambi titolo/sottotitolo, rigenera anche le immagini social: `python3 _src/og.py` (richiede Pillow, font macOS)

## Dominio
Il dominio è impostato in `_src/build.py` (`BASE = "https://villaada-b401.com"`):
se cambia, aggiorna `BASE` e `robots.txt`, poi rilancia `python3 _src/build.py`.

## Anteprima locale
`python3 -m http.server 8000` → http://localhost:8000

## Pubblicazione (Vercel)
Progetto statico, nessuna build: Framework Preset "Other", Build Command vuoto,
Output Directory `.` (radice). Ogni push su `main` viene pubblicato in automatico.
`vercel.json` imposta cache e header; `.vercelignore` esclude `_src`.
