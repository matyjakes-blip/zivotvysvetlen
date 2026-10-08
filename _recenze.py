#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Recenze ve stylu Beyond Terrain: pás karet, který sám jede do strany (zastaví se pod prstem nebo myší).
Pravidlo od Matyáše (7. 10. 2026): každá recenze nese, čím člověk prošel. KLIENT = 1:1, STUDENT = jen Akademie.
Dokud nejsou skutečné recenze se souhlasem, RECENZE je prázdný a ukazují se zástupné karty (na živý web nepouštět)."""
import html

def esc(t):
    return html.escape(t, quote=False)

# (text, iniciály, typ "klient" nebo "student")
RECENZE = []

TYPY = {"klient": "Klient · 1:1", "student": "Student · Akademie"}

ZASTUPNE = [("klient", "Sem přijde recenze klienta z 1:1, jeho slovy, se souhlasem."),
            ("student", "Sem přijde dlouhá recenze studenta Akademie."),
            ("klient", "Nebo screenshot výhry z tvých highlightů na Instagramu."),
            ("student", "Sem přijde recenze studenta Akademie."),
            ("klient", "Sem přijde recenze klienta z 1:1.")]


def pas_recenze(nadpis="Co říkají klienti a studenti", jen=None):
    if RECENZE:
        polozky = [(t, i, typ) for t, i, typ in RECENZE if not jen or typ == jen]
        karty = "".join('<figure class="recenze"><blockquote>%s</blockquote><figcaption><b>%s</b> · %s</figcaption></figure>'
                        % (esc(t), esc(i), TYPY[typ]) for t, i, typ in polozky)
    else:
        polozky = [(typ, t) for typ, t in ZASTUPNE if not jen or typ == jen]
        karty = "".join('<figure class="recenze zastupna"><blockquote>%s</blockquote><figcaption><b>XY</b> · %s</figcaption></figure>'
                        % (esc(t), TYPY[typ]) for typ, t in polozky)
    return """
  <section class="pas recenze-pas" id="recenze">
    <div class="obal">
      <p class="nadtitul">Jejich slovy</p>
      <h2>%s</h2>
    </div>
    <div class="recenze-okno"><div class="recenze-pruh">%s%s</div></div>
  </section>
""" % (esc(nadpis), karty, karty.replace('<figure class="recenze', '<figure aria-hidden="true" class="recenze'))
