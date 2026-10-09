#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Recenze ve stylu Beyond Terrain: pás karet, který sám jede do strany (zastaví se pod prstem nebo myší).
Pravidlo od Matyáše (7. 10. 2026): každá recenze nese, čím člověk prošel. KLIENT = 1:1, STUDENT = jen Akademie.
Dokud nejsou skutečné recenze se souhlasem, RECENZE je prázdný a ukazují se zástupné karty (na živý web nepouštět)."""
import html, os

def esc(t):
    return html.escape(t, quote=False)

# (text, iniciály, typ "klient" nebo "student", kdy). Klienti z jeho IG highlightu „Klienti" (souhlas má ke všem,
# Matyáš 9. 10. 2026), zkrácené jejich slovy; jen text, žádné fotky klientů, jména jen iniciálou, intimní věci vynechané.
RECENZE = [
    ("Díky tobě se cítím opravdu skvěle. Moje zdraví i fyzická kondice jsou na úplně jiné úrovni než dřív. Vážím si nejen tvých znalostí a zkušeností, ale i toho, jak lidsky ke mně přistupuješ.", "R.", "klient", ""),
    ("Přišel jsem hlavně proto, že mě často bolelo břicho, měl jsem průjmy, ranní zvracení a reflux. Přestala mě bolet záda i břicho, zmizel reflux a ranní zvracení, mnohem lépe spím a podstatně méně se potím. Všechno jsi mi srozumitelně vysvětlil a nastavil tak, aby se to dalo normálně dodržovat.", "", "klient", ""),
    ("Cítím se jako superman. Zvládnu daleko víc věcí, jsem líp koncentrovaný, síla šla nahoru okamžitě, jsem víc v klidu a víc přítomný. Manželka říkala, že mám najednou nějakou jiskru.", "", "klient", "po 4 dnech"),
    ("Dneska mi trenér řekl, že vypadám esteticky dobře a že silově sem na tom líp. Po měsíci, co sem něco změnil. To je kompliment jako blázen, on to normálně neříká.", "R.", "klient", "po měsíci"),
    ("Zmizelo nadýmání, s tím špatný trávení a ty fakt nepříjemný a neřešitelný crashe odpoledne. Cítím velkou změnu na spánku, energii a náladě přes den.", "M.", "klient", "1. týden"),
    ("Energie a celkově nálada se mi kompletně vrací do normálu. Hlavně ta nálada, to je úplně něco jinýho než předtím.", "F.", "klient", ""),
    ("Brácho, mám problém. Padají mi všechny kalhoty. Jak bylo vedro, nosil jsem jen kraťasy, a dneska prší, jdu na schůzku a kalhoty velký všechny.", "", "klient", ""),
    ("Cítím progress hlavně i po tý mentální straně, ta strava mi dává úplně jiný signály v tom těle. Nehty a vlasy rostou rychleji, i pleť je lepší, přijdu si hezčí v zrcadle. Přítelkyně mi řekla taky, že vypadám líp.", "", "klient", ""),
    ("Co se businessu týče, mám daleko víc energie. Díky změně stravy nepotřebuju jíst tolik jídel denně jako předtím, stačí mi dvě velký jídla a jedna svačina. Produktivita se zvýšila.", "", "klient", ""),
    ("Prostě ta nálada, chuť si na max užívat života. Všechno feeluju 1000× líp.", "", "klient", "po měsíci"),
    ("Ráno je teď 100% moje. Vstanu, umyju ze sebe pot, jdu ven, dám si grounding a mořskou plazmu a k tomu pět základních cviků. Jedu to fakt napohodu, bez stresu a v klidu.", "", "klient", ""),
    ("Větší přítomnost, klid v hlavě, jiná energie a přirozenější chuť dělat věci podle sebe a pro sebe.", "", "klient", ""),
    ("Přijde mi, že každý den je výhra. Všechno pod kontrolou a zase začínám mít víc energie a chuti na trénink.", "", "klient", ""),
    ("Kámo, to je šílený. Mám obrovskou radost, co se to se mnou děje.", "", "klient", ""),
]

TYPY = {"klient": "Klient · 1:1", "student": "Student · Akademie"}

ZASTUPNE = [("klient", "Sem přijde recenze klienta z 1:1, jeho slovy, se souhlasem."),
            ("student", "Sem přijde dlouhá recenze studenta Akademie."),
            ("klient", "Nebo screenshot výhry z tvých highlightů na Instagramu."),
            ("student", "Sem přijde recenze studenta Akademie."),
            ("klient", "Sem přijde recenze klienta z 1:1.")]


def pas_recenze(nadpis="Co říkají klienti a studenti", jen=None):
    if RECENZE:
        polozky = [r for r in RECENZE if not jen or r[2] == jen]
        if not polozky:
            return ""
        if nadpis == "Co říkají klienti a studenti" and all(r[2] == "klient" for r in polozky):
            nadpis = "Co píšou klienti"   # dokud nejsou recenze studentů
        karty = "".join('<figure class="recenze"><blockquote>%s</blockquote><figcaption>%s%s%s</figcaption></figure>'
                        % (esc(t), ("<b>%s</b> · " % esc(i)) if i else "", TYPY[typ], (" · %s" % esc(kdy)) if kdy else "")
                        for t, i, typ, kdy in polozky)
    elif os.environ.get("NAHLED") != "1":
        return ""  # bez skutečných recenzí se souhlasem se sekce na živém webu neukazuje
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
