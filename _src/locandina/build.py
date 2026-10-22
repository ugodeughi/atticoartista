#!/usr/bin/env python3
"""Genera la locandina A4 in PDF con QR code verso il sito.

Uso:  python3 _src/locandina/build.py   (richiede: pip install segno playwright)
Scrive _src/locandina/qr.svg e locandina-attico-artista.pdf nella cartella sopra al progetto.
"""
from pathlib import Path
import segno
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
URL = "https://villaada-b401.com"
OUT = HERE.parents[2] / "locandina-attico-artista.pdf"

segno.make(URL, error="m").save(HERE / "qr.svg", scale=10, border=0, dark="#24474f")

with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page()
    pg.goto((HERE / "locandina.html").as_uri(), wait_until="networkidle")
    pg.evaluate("document.fonts.ready")
    pg.pdf(path=str(OUT), format="A4", print_background=True, prefer_css_page_size=True)
    b.close()
print(OUT)
