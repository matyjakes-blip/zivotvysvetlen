#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Postavi web zivotvysvetlen.cz: index.html (funnel) a pribeh.html.
Texty se berou ze zdroju Akademie, nic se nedopisuje.
Pouziti: python3 _postav.py     (spoustet ze slozky ~/Work/web-zivotvysvetlen)"""
import os, re, html, glob

TELO = os.path.expanduser("~/Work/skool/export-do-skoolu/telo")

# ---- video: az bude VSL, sem prijde odkaz (YouTube/Vimeo embed) ----
VIDEO = ""          # napr. "https://www.youtube.com/embed/XXXX"
VIDEO_POPIS = "Než začneš, tohle je celé vysvětlené za pár minut."

SKOOL = "https://www.skool.com/zivot-vysvetlen-1338"

HLAVA = """<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{titulek}</title>
<meta name="description" content="{popis}">
<link rel="canonical" href="https://zivotvysvetlen.cz/{kanon}">
<meta property="og:title" content="{titulek}">
<meta property="og:description" content="{popis}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://zivotvysvetlen.cz/{kanon}">
<meta property="og:image" content="https://zivotvysvetlen.cz/{ogobr}">
<meta property="og:locale" content="cs_CZ">
<meta property="og:site_name" content="Život vysvětlen">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="https://zivotvysvetlen.cz/{ogobr}">
<link rel="icon" href="/favicon.ico" sizes="any">
<link rel="icon" href="/ikona-512.png" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;1,400;1,500&display=swap">
<link rel="stylesheet" href="/styl.css">
</head>
<body>
<header class="hlavicka">
  <a class="znacka" href="/">Život vysvětlen</a>
  <nav class="nav">
    <a href="/mapa.html">Mapa</a>
    <a href="/pribeh.html">Příběh</a>
    <a class="cta-maly" href="{skool}">Vstoupit</a>
  </nav>
</header>
"""

PATA = """
<footer class="pata">
  <div class="ozdoba" aria-hidden="true">◆</div>
  <p class="znacka-pata">Život vysvětlen</p>
  <p class="drobne">Matyáš Jakeš · <a href="{skool}">Akademie na Skoolu</a> · <a href="/mapa.html">Mapa</a> · <a href="/pribeh.html">Příběh</a></p>
</footer>
</body>
</html>
"""


def esc(t):
    return html.escape(t, quote=False)


def md_inline(t):
    t = esc(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    return t


def nacti_pribeh():
    """vrati seznam ('text', html) / ('obr', soubor) ze zdroje lekce 0.0"""
    cesta = os.path.join(TELO, "0.0__0-0-muj-pribeh.md")
    raw = open(cesta, encoding="utf-8").read()
    kusy = []
    for blok in raw.split("\n\n"):
        b = blok.strip()
        if not b:
            continue
        m = re.match(r"^\[\[\s*SEM OBRÁZEK:\s*(.+?)\s*\]\]$", b)
        if m:
            kusy.append(("obr", m.group(1)))
        else:
            kusy.append(("text", md_inline(b)))
    return kusy


def galerie(soubory, popisek=None):
    figs = "".join('<figure class="ram"><img src="/pribeh/%s" alt="" loading="lazy"></figure>' % s for s in soubory)
    pop = '<figcaption class="popisek">%s</figcaption>' % esc(popisek) if popisek else ""
    return '<div class="dvojice">%s</div>%s' % (figs, pop)


# ---------------------------------------------------------------- příběh
def postav_pribeh():
    kusy = nacti_pribeh()
    ven = []
    i = 0
    while i < len(kusy):
        typ, v = kusy[i]
        if typ == "obr":
            skupina = []
            while i < len(kusy) and kusy[i][0] == "obr":
                skupina.append(kusy[i][1])
                i += 1
            ven.append('<div class="obrazy">%s</div>' % "".join(
                '<figure class="ram"><img src="/pribeh/%s" alt="" loading="lazy"></figure>' % s for s in skupina))
            continue
        ven.append("<p>%s</p>" % v)
        i += 1

    telo = """
<main class="obal uzky">
  <p class="nadtitul">Příběh</p>
  <h1 class="nadpis-str">Můj příběh</h1>
  <div class="text">
%s
  </div>
  <section class="zaver">
    <div class="ozdoba" aria-hidden="true">◆</div>
    <p class="vyzva">Tohle není kurz o tom, jak být zdravý.<strong>Je to kurz o tom, jak zdraví vlastně funguje.</strong></p>
    <a class="cta" href="%s">Vstoupit do Akademie</a>
    <p class="drobne"><a href="/mapa.html">Nebo si nejdřív projdi mapu</a></p>
  </section>
</main>
""" % ("\n".join("    " + x for x in ven), SKOOL)

    stranka = HLAVA.format(titulek="Můj příběh · Život vysvětlen",
                           popis="Od 55 kilo a neplodnosti přes 110 kilo a akné až sem. Celá cesta, bez vynechání.",
                           kanon="pribeh.html", ogobr="pribeh/0.0__09-porovnani-dvojice.jpg",
                           skool=SKOOL) + telo + PATA.format(skool=SKOOL)
    open("pribeh.html", "w", encoding="utf-8").write(stranka)
    return len(ven)


# ---------------------------------------------------------------- funnel
PORADI = [
    ("Nejdřív musíš vědět, co nemoc je", "jinak budeš to, co ti tělo dělá, pořád vypínat."),
    ("Pak přijde prostředí", "protože je zadarmo a dělá nejvíc."),
    ("Pak jídlo", "protože je nejdražší a nemá smysl za něj utrácet, dokud spíš pět hodin."),
    ("Pak výkon", "protože trénink je jenom signál a staví se ze spánku a jídla."),
    ("A nakonec mysl", "protože člověk, který žije ve strachu, si nepomůže žádným jídlem."),
]

PRAVIDLA = [
    ("Jedna věc týdně", "Ne pět. Každý submodul končí jednou výzvou a ta je záměrně malá. Kdo začne dělat deset věcí najednou, skončí do tří týdnů."),
    ("Nejdřív odebírej, potom přidávej", "Odebrat světlo večer, chemii z koupelny nebo router z ložnice stojí nulu. Přidávat doplňky stojí peníze a často to zhorší."),
    ("Nic si neber jenom proto, že to říkám já", "V každém submodulu je napsané, odkud to je. Když tě něco zarazí, dohledej si to. Kdo si to ověří sám, už to nikdy nezapomene."),
    ("Když něco vynecháš, nic se neděje", "Vynechaný týden není selhání. Selhání je, když si z toho uděláš další povinnost, kterou nesmíš porušit."),
    ("Sdílej číslo, ne názor", "Každá výzva končí tím, že do komunity napíšeš jedno konkrétní číslo nebo jednu větu. Ne co si myslíš, ale co ti vyšlo."),
]

MODULY = [
    ("1", "Terén vs. zárodek", "Odkud se nemoc bere. Imunita, příznaky, nosologie."),
    ("2", "Mikroby", "Viry, bakterie a paraziti. Druhá polovina teorie."),
    ("3", "Prostředí", "Světlo, voda, pohyb a dech, spánek."),
    ("4", "Výživa", "Živočišný základ, minerály a sůl, tuky, vitamínová lež."),
    ("5", "Výkon a tělo", "Trénink, hormony, regenerace a detox, dlouhověkost."),
    ("6", "Mysl a duch", "Myšlenka a zkušenost, trauma, nervový systém, víra."),
]


def postav_index():
    video = ""
    if VIDEO:
        video = """
  <section class="video">
    <div class="ram-video"><iframe src="%s" title="Život vysvětlen" loading="lazy" allowfullscreen></iframe></div>
    <p class="popisek">%s</p>
  </section>
""" % (VIDEO, esc(VIDEO_POPIS))

    poradi = "".join(
        '<li><b>%d</b><span><strong>%s.</strong> %s</span></li>' % (i + 1, esc(a), esc(b))
        for i, (a, b) in enumerate(PORADI))

    pravidla = "".join(
        '<section class="pravidlo"><h3>%s</h3><p>%s</p></section>' % (esc(a), esc(b))
        for a, b in PRAVIDLA)

    moduly = "".join(
        '<li><b>%s</b><span><strong>%s</strong><em>%s</em></span></li>' % (c, esc(n), esc(p))
        for c, n, p in MODULY)

    telo = """
<main>
  <section class="hero">
    <div class="obal">
      <h1 class="znacka-velka">Život vysvětlen</h1>
      <p class="podtitul">První terénní akademie v češtině</p>
      <div class="ozdoba" aria-hidden="true">◆</div>
      <p class="tvrzeni">Tohle není kurz o tom, jak být zdravý.<strong>Tohle je kurz o tom, jak zdraví vlastně funguje.</strong></p>
      <p class="tvrzeni-pod">Člověk, který zná sto protokolů a nerozumí principu, je závislý na tom, kdo mu ten sto první řekne.</p>
      <div class="tlacitka">
        <a class="cta" href="{skool}">Vstoupit do Akademie</a>
        <a class="cta-druhy" href="/mapa.html">Projít mapu</a>
      </div>
      <p class="cisla"><span><b>6</b>modulů</span><span><b>23</b>submodulů</span><span><b>101</b>lekcí</span><span><b>21</b>hodin čtení</span></p>
    </div>
  </section>
{video}
  <section class="pas dukaz">
    <div class="obal uzky">
      <p class="nadtitul">Důkaz</p>
      <h2>Nejdřív jsem to zkusil na sobě</h2>
      <div class="dvojice">
        <figure class="ram"><img src="/pribeh/0.0__11-pred-ctyri-mesice.jpg" alt="před" loading="lazy"></figure>
        <figure class="ram"><img src="/pribeh/0.0__12-po-ctyrech-mesicich.jpg" alt="po" loading="lazy"></figure>
      </div>
      <p class="popisek">Rozdíl čtyři měsíce</p>
      <div class="dvojice">
        <figure class="ram"><img src="/pribeh/0.0__13-pred-dva-a-pul-roku.jpg" alt="před" loading="lazy"></figure>
        <figure class="ram"><img src="/pribeh/0.0__14-po-dvou-a-pul-roce.jpg" alt="po" loading="lazy"></figure>
      </div>
      <p class="popisek">Rozdíl dva a půl roku</p>
      <p class="text-stred">V patnácti jsem měl 167 centimetrů a 55 kilo, ženské rysy, nulovou energii a byl jsem v podstatě neplodný. V osmnácti jsem vážil 110 kilo, měl kyselinu močovou na úrovni šedesátiletého chlapa a testosteron na dně.</p>
      <a class="odkaz-dal" href="/pribeh.html">Celý příběh, bez vynechání</a>
    </div>
  </section>

  <section class="pas">
    <div class="obal uzky">
      <p class="nadtitul">Proč zrovna v tomhle pořadí</p>
      <h2>Každý modul stojí na tom předchozím</h2>
      <ol class="poradi">{poradi}</ol>
      <p class="text-stred">Když chceš číst na přeskočku, klidně. Jenom Modul 1 nepřeskakuj.</p>
    </div>
  </section>

  <section class="pas moduly-pas">
    <div class="obal">
      <p class="nadtitul">Co je uvnitř</p>
      <h2>Šest modulů, dvacet tři submodulů</h2>
      <ol class="moduly">{moduly}</ol>
      <div class="stred"><a class="cta-druhy" href="/mapa.html">Otevřít mapu Akademie</a></div>
    </div>
  </section>

  <section class="pas">
    <div class="obal uzky">
      <p class="nadtitul">Jak to běží</p>
      <h2>Pět pravidel Akademie</h2>
      <div class="pravidla">{pravidla}</div>
    </div>
  </section>

  <section class="pas zaver-pas">
    <div class="obal uzky stred">
      <div class="ozdoba" aria-hidden="true">◆</div>
      <p class="vyzva">Každý modul staví na předchozím a nic v něm nezazní bez vysvětlení.<strong>Kdo přeskočí rovnou na viry, bude mít pocit, že tomu rozumí, a bude se mýlit.</strong></p>
      <a class="cta" href="{skool}">Vstoupit do Akademie</a>
    </div>
  </section>
</main>
""".format(skool=SKOOL, video=video, poradi=poradi, moduly=moduly, pravidla=pravidla)

    stranka = HLAVA.format(titulek="Život vysvětlen · Akademie",
                           popis="Tohle není kurz o tom, jak být zdravý. Je to kurz o tom, jak zdraví vlastně funguje. První terénní akademie v češtině.",
                           kanon="", ogobr="mapa/hero.jpg", skool=SKOOL) + telo + PATA.format(skool=SKOOL)
    open("index.html", "w", encoding="utf-8").write(stranka)


if __name__ == "__main__":
    n = postav_pribeh()
    postav_index()
    print("pribeh.html: %d bloku" % n)
    print("index.html: %d znaku" % os.path.getsize("index.html"))
