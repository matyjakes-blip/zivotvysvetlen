#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Postavi web zivotvysvetlen.cz: index.html (funnel) a pribeh.html.
Texty se berou ze zdroju Akademie, nic se nedopisuje.
Pouziti: python3 _postav.py     (spoustet ze slozky ~/Work/web-zivotvysvetlen)"""
import os, re, html, glob

TELO = os.path.expanduser("~/Work/skool/export-do-skoolu/telo")

# ---- video: az bude VSL, sem prijde odkaz (YouTube/Vimeo embed) ----
VIDEO = "https://www.youtube-nocookie.com/embed/JlXmno16D5s"
VIDEO_POPIS = "Celá pravda k nejvyšší vitalitě · detailní rozbor"

SKOOL = "https://www.skool.com/zivot-vysvetlen-1338"
CALENDLY = "https://calendly.com/yacashh/1-1-osobni-kvalifikacni-hovor"
INSTAGRAM = "https://www.instagram.com/yacashh/"
MAIL = "mjmates@email.cz"
FORMULAR_EMAIL = "https://indecisive-zenobia-f04.notion.site/7a88bd5ce2bd47e8ba84dd5e08d059f3"

# hosteni v podcastech (overeno na YouTube 25. 9. 2026)
PODCASTY = [
    # clanek v tydeniku Respekt 32/2025 (4.-10. 8. 2025), pridano 28. 9. 2026 na Matyasovo prani
    ("Respekt 32/2025", "Článek v týdeníku · Najednou jsem měl chuť do života", "https://www.respekt.cz/tydenik/2025/32/najednou-jsem-mel-chut-do-zivota"),
    ("Debatní deník", "Debata s odpůrcem moderní vědy a medicíny", "https://www.youtube.com/watch?v=CHxI8kVo_2Q"),
    # POD 10, overeno na YouTube 29. 9. 2026 (2. dil, 1. dil se na YouTube nenasel)
    ("POD 10", "Nejezte zeleninu · kontroverzní výživový poradce", "https://www.youtube.com/watch?v=xNz05rFzncQ"),
    ("Světy proti sobě", "Grznár vs. Jakeš · sypač vs. naturál", "https://www.youtube.com/watch?v=bs12r6PMWC0"),
]

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
<link rel="preload" href="/pisma/cinzel.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/pisma/cormorant.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/styl.css">
</head>
<body>
<header class="hlavicka">
  <a class="znacka" href="/">Život vysvětlen</a>
  <nav class="nav">
    <a href="/mapa.html">Mapa</a>
    <a href="/jedna-na-jedna.html">1:1</a>
    <a href="/pribeh.html">Příběh</a>
    <a class="cta-maly" href="{skool}">Vstoupit</a>
  </nav>
</header>
"""

PATA = """
<footer class="pata">
  <div class="ozdoba" aria-hidden="true">◆</div>
  <p class="znacka-pata">Život vysvětlen</p>
  <p class="drobne">Matyáš Jakeš · <a href="{skool}">Akademie na Skoolu</a> · <a href="/mapa.html">Mapa</a> · <a href="/jedna-na-jedna.html">1:1</a> · <a href="/pribeh.html">Příběh</a> · <a href="/sourcing.html">Sourcing mapa</a> · <a href="/kontakt.html">Kontakt</a></p>
  <p class="drobne">IČO 23494204 · <a href="/pravni.html">Právní informace a zásady</a></p>
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


def pas_podcasty():
    # Respekt se neotevira hned na respekt.cz: klik ukaze dvojstranu v okne (#respekt), odkaz na clanek je uvnitr
    polozky = "".join(
        '<a class="host" href="%s"><b>%s</b><span>%s</span></a>' % ("#respekt" if n.startswith("Respekt") else u, esc(n), esc(p))
        for n, p, u in PODCASTY)
    return """
  <section class="pas hoste" id="hoste">
    <div class="obal">
      <p class="nadtitul">Psali o mně · byl jsem hostem</p>
      <div class="hoste-radek">%s</div>
    </div>
  </section>
  <div class="clanek" id="respekt" role="dialog" aria-modal="true" aria-label="Respekt 32/2025">
    <a class="clanek-pozadi" href="#hoste" aria-label="Zavřít"></a>
    <div class="clanek-okno">
      <a class="clanek-zavrit" href="#hoste" aria-label="Zavřít">×</a>
      <p class="nadtitul">Respekt 32/2025 · 4. až 10. srpna 2025</p>
      <div class="dvojice">
        <a class="ram" href="/media/respekt-32-2025-str14.jpg"><img src="/media/respekt-32-2025-str14.jpg" alt="Respekt 32/2025, strana 14: článek o Matyášovi" loading="lazy"></a>
        <a class="ram" href="/media/respekt-32-2025-str15.jpg"><img src="/media/respekt-32-2025-str15.jpg" alt="Respekt 32/2025, strana 15" loading="lazy"></a>
      </div>
      <p class="popisek"><a href="https://www.respekt.cz/tydenik/2025/32/najednou-jsem-mel-chut-do-zivota">Celý článek na respekt.cz</a></p>
    </div>
  </div>
""" % polozky


# ---- tri cesty (produktove povedomi) ----
# aktivni=False se nevykresli: mid ticket ceka na Matyasovo rozhodnuti
CESTY = [
    dict(aktivni=True, hlavni=False, znak="Nejdostupnější",
         nazev="Akademie", vysvetleni="Celý systém napsaný, čteš vlastním tempem",
         body=["Šest modulů, čtyřiadvacet submodulů, sto dvě lekce",
               "Mapa, první týden den po dni a vstupní diagnostika",
               "Komunita, kde se doptáváš, když něco nesedí",
               "Zůstává ti to napořád, vracíš se k tomu kdykoli"],
         pro="Pro toho, kdo si to chce odvodit sám a nechce, aby mu někdo stál za ramenem.",
         odkaz=None, odkaz_text="Vstoupit do Akademie", pod=None),

    dict(aktivni=False, hlavni=False, znak="Mezi tím",
         nazev="Akademie a hovory", vysvetleni="Čteš sám, ale nejsi v tom sám",
         body=["Celá Akademie",
               "Tři hovory se mnou v průběhu prvních měsíců",
               "Na každém si ověříš, že to aplikuješ na svoji situaci správně"],
         pro="Pro toho, kdo si věří, že si to přečte sám, ale chce si to nechat zkontrolovat.",
         odkaz=None, odkaz_text="Napsat mi", pod=None),

    dict(aktivni=True, hlavni=True, znak="Nejhlubší",
         nazev="Osobní vedení 1:1", vysvetleni="Ten samý systém aplikovaný na jednoho člověka",
         body=["Vstupní dotazník: historie, prostředí, spánek, jídlo, trénink, míry",
               "Tvůj vlastní dokument s tvým pořadím kroků a odůvodněním",
               "Týdenní balíčky, každý týden jedna věc",
               "Kontrolní hovory a přehazování tempa podle toho, co ti vychází"],
         pro="Pro toho, komu běžná cesta nezabrala a chce vědět, proč to jeho tělo dělá.",
         odkaz=None, odkaz_text="Domluvit hovor", pod="Hovor je zdarma a nezavazuje"),
]


def pas_cesty():
    karty = []
    for c in CESTY:
        if not c["aktivni"]:
            continue
        body = "".join("<li>%s</li>" % esc(b) for b in c["body"])
        odkaz = c["odkaz"] or (CALENDLY if c["hlavni"] else SKOOL)
        pod = '<span class="pod">%s</span>' % esc(c["pod"]) if c["pod"] else ""
        karty.append(
            '<article class="cesta%s">'
            '<p class="cesta-znak">%s</p>'
            '<h3>%s</h3>'
            '<p class="vysvetleni">%s</p>'
            '<ul>%s</ul>'
            '<p class="pro-koho">%s</p>'
            '<div class="dole"><a href="%s">%s</a>%s</div>'
            '</article>'
            % (" hlavni" if c["hlavni"] else "", esc(c["znak"]), esc(c["nazev"]),
               esc(c["vysvetleni"]), body, esc(c["pro"]), odkaz, esc(c["odkaz_text"]), pod))
    return """
  <section class="pas cesty-pas" id="cesty">
    <div class="obal">
      <p class="nadtitul">Jak se do toho dá jít</p>
      <h2>Dvě cesty, jeden systém</h2>
      <p class="text-stred">Je to pořád stejné vysvětlení. Rozdíl je jen v tom, jestli si ho přečteš sám, nebo ti ho na tebe někdo přeloží.</p>
      <div class="cesty">%s</div>
      <p class="text-stred" style="margin-top:26px">Nevíš, co z toho? Začni Akademií. Kdo pak chce jít hlouběji, přejde na osobní vedení.</p>
    </div>
  </section>
""" % "".join(karty)


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
        <a class="cta-druhy" href="#cesty">Co nabízím</a>
      </div>
      <p class="cisla"><span><b>6</b>modulů</span><span><b>24</b>submodulů</span><span><b>102</b>lekcí</span><span><b>21</b>hodin čtení</span></p>
    </div>
  </section>
{video}{podcasty}
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
      <h2>Šest modulů, čtyřiadvacet submodulů</h2>
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


  <section class="pas sourcing-pas">
    <div class="obal uzky stred">
      <p class="nadtitul">Zdarma</p>
      <h2>Kde to všechno koupit</h2>
      <p class="text-stred">Přes tři tisíce míst v Česku, kde se dá koupit syrové mléko, maso, zvěřina, med a ryby přímo od chovatele. Všechno na jedné mapě.</p>
      <a class="cta-druhy" href="/sourcing.html">Otevřít sourcing mapu</a>
    </div>
  </section>
{cesty}
  <section class="pas zaver-pas">
    <div class="obal uzky stred">
      <div class="ozdoba" aria-hidden="true">◆</div>
      <p class="vyzva">Každý modul staví na předchozím a nic v něm nezazní bez vysvětlení.<strong>Kdo přeskočí rovnou na viry, bude mít pocit, že tomu rozumí, a bude se mýlit.</strong></p>
      <a class="cta" href="{skool}">Vstoupit do Akademie</a>
    </div>
  </section>
</main>
""".format(skool=SKOOL, video=video, podcasty=pas_podcasty(), cesty=pas_cesty(),
           poradi=poradi, moduly=moduly, pravidla=pravidla)

    stranka = HLAVA.format(titulek="Život vysvětlen · Akademie",
                           popis="Tohle není kurz o tom, jak být zdravý. Je to kurz o tom, jak zdraví vlastně funguje. První terénní akademie v češtině.",
                           kanon="", ogobr="mapa/hero.jpg", skool=SKOOL) + telo + PATA.format(skool=SKOOL)
    open("index.html", "w", encoding="utf-8").write(stranka)




# ---------------------------------------------------------------- 1:1
KROKY = [
    ("Kvalifikační hovor", "Zdarma, nezávazně. Projdeme, co řešíš a co už jsi zkoušel. Na konci oba víme, jestli to dává smysl."),
    ("Vstupní dotazník", "Zdravotní historie, prostředí, spánek, jídlo, trénink, míry a fotky. Bez toho se nedá stavět nic osobního."),
    ("Tvůj vlastní dokument", "Dostaneš svůj proces implementace. Tvoje situace, tvoje pořadí kroků, tvoje odůvodnění."),
    ("Týdenní balíčky", "Každý týden jedna věc. Ne deset. Tempo se řídí podle toho, co ti reálně vychází."),
    ("Kontrolní hovory", "Pravidelný check-in a hovor, když je potřeba něco přehodit."),
]

NENI = [
    "Není to jídelníček, který vydrží týden a pak se vrátíš tam, kde jsi byl.",
    "Nepočítáš makra ani kalorie. Kalorie jsou měřák, ne cíl.",
    "Nedostaneš seznam doplňků, které si máš koupit.",
]


def postav_11():
    kroky = "".join(
        '<li><b>%d</b><span><strong>%s</strong><em>%s</em></span></li>' % (i + 1, esc(a), esc(b))
        for i, (a, b) in enumerate(KROKY))
    neni = "".join('<li>%s</li>' % esc(x) for x in NENI)

    telo = """
<main>
  <section class="hero hero-uzsi">
    <div class="obal uzky">
      <p class="nadtitul">Osobní vedení</p>
      <h1 class="nadpis-str">1:1</h1>
      <p class="tvrzeni-pod">Akademie je ten systém napsaný. Tohle je ten samý systém aplikovaný na jednoho člověka.</p>
      <div class="tlacitka"><a class="cta" href="{calendly}">Domluvit hovor</a></div>
    </div>
  </section>

  <section class="pas">
    <div class="obal uzky">
      <p class="nadtitul">Pro koho to je</p>
      <h2>Pro toho, komu běžná cesta nezabrala</h2>
      <p class="text-stred">Byl jsi u doktora a vyšlo ti, že je všechno v pořádku, jenom se pořád necítíš dobře. Zkoušel jsi dietu, doplňky a protokoly z internetu. Něco na chvíli zabralo, nic nevydrželo. Tohle není o další dietě, ale o tom, proč to tělo dělá.</p>
      <p class="text-stred">Sám jsem si tím prošel. Ve <a href="/pribeh.html">svém příběhu</a> je to celé, včetně toho, co jsem dělal špatně.</p>
    </div>
  </section>

  <section class="pas">
    <div class="obal uzky">
      <p class="nadtitul">Jak to běží</p>
      <h2>Pět kroků od hovoru k prvnímu týdnu</h2>
      <ol class="poradi kroky">{kroky}</ol>
    </div>
  </section>

  <section class="pas">
    <div class="obal uzky">
      <p class="nadtitul">Ať je jasno</p>
      <h2>Co to není</h2>
      <ul class="neni">{neni}</ul>
    </div>
  </section>

  <section class="pas">
    <div class="obal uzky stred">
      <p class="nadtitul">Hovor</p>
      <h2>Co se na něm stane</h2>
      <p class="text-stred">Zavoláme si a projdeme, co řešíš, co už jsi zkoušel a co ti z toho vyšlo. Ptám se na spánek, světlo, jídlo, trénink a na to, jak ti je. Na konci oba víme, jestli je osobní vedení to, co potřebuješ, nebo ti stačí Akademie.</p>
      <p class="text-stred">Nic se na hovoru neplatí a nikam se nepřihlašuješ.</p>
    </div>
  </section>

  <section class="pas zaver-pas">
    <div class="obal uzky stred">
      <div class="ozdoba" aria-hidden="true">◆</div>
      <p class="vyzva">Hovor je zdarma a k ničemu tě nezavazuje.<strong>Nejhorší, co se může stát, je že si ujasníš, co s tebou vlastně je.</strong></p>
      <a class="cta" href="{calendly}">Domluvit hovor</a>
      <p class="drobne"><a href="{skool}">Nebo začni Akademií</a></p>
    </div>
  </section>
</main>
""".format(calendly=CALENDLY, skool=SKOOL, kroky=kroky, neni=neni)

    stranka = HLAVA.format(titulek="Osobní vedení 1:1 · Život vysvětlen",
                           popis="Akademie je ten systém napsaný. 1:1 je ten samý systém aplikovaný na jednoho člověka. Hovor je zdarma.",
                           kanon="jedna-na-jedna.html", ogobr="pribeh/0.0__09-porovnani-dvojice.jpg",
                           skool=SKOOL) + telo + PATA.format(skool=SKOOL)
    open("jedna-na-jedna.html", "w", encoding="utf-8").write(stranka)


# ---------------------------------------------------------------- kontakt
def postav_kontakt():
    telo = """
<main>
  <section class="hero hero-uzsi">
    <div class="obal uzky">
      <p class="nadtitul">Kontakt</p>
      <h1 class="nadpis-str">Kde mě najdeš</h1>
      <p class="tvrzeni-pod">Nejrychleji na Instagramu. Píšu si tam sám.</p>
    </div>
  </section>

  <section class="pas">
    <div class="obal uzky">
      <ul class="kontakty">
        <li><a href="{instagram}"><b>Instagram</b><span>@yacashh · napiš do zpráv</span></a></li>
        <li><a href="{calendly}"><b>Hovor 1:1</b><span>Zdarma a nezávazně, vybereš si termín</span></a></li>
        <li><a href="{skool}"><b>Akademie</b><span>Skupina Život vysvětlen na Skoolu</span></a></li>
        <li><a href="mailto:{mail}"><b>E-mail</b><span>{mail} · obchodní a formální věci</span></a></li>
      </ul>
      <p class="text-stred">Na zprávy odpovídám sám, ne asistent. Někdy to trvá den nebo dva.</p>
    </div>
  </section>

  <section class="pas zaver-pas">
    <div class="obal uzky stred">
      <div class="ozdoba" aria-hidden="true">◆</div>
      <a class="cta" href="{skool}">Vstoupit do Akademie</a>
    </div>
  </section>
</main>
""".format(instagram=INSTAGRAM, calendly=CALENDLY, skool=SKOOL, mail=MAIL)

    stranka = HLAVA.format(titulek="Kontakt · Život vysvětlen",
                           popis="Instagram, hovor 1:1, Akademie na Skoolu a e-mail.",
                           kanon="kontakt.html", ogobr="mapa/hero.jpg",
                           skool=SKOOL) + telo + PATA.format(skool=SKOOL)
    open("kontakt.html", "w", encoding="utf-8").write(stranka)


# ---------------------------------------------------------------- pravni informace
UDAJE = [
    ("Jméno", "Matyáš Jakeš"),
    ("IČO", "23494204"),
    ("Právní forma", "Fyzická osoba podnikatel (OSVČ), nezapsaná v obchodním rejstříku"),
    ("Zapsán", "V živnostenském rejstříku, Magistrát města Teplice"),
    ("Sídlo", "Heydukova 1648/8, 415 01 Teplice"),
    ("E-mail", "mjmates@email.cz"),
]

PRAVA = [
    "Chtít po mně, ať ti řeknu, co o tobě mám.",
    "Nechat si to opravit, když je to špatně.",
    "Nechat si to smazat nebo omezit, pokud to nemusím ze zákona držet dál.",
    "Dostat to ve strojově čitelné podobě a odnést si to jinam.",
    "Odvolat souhlas, který jsi mi dal, a to kdykoli.",
    "Stěžovat si na Úřad pro ochranu osobních údajů, Pplk. Sochora 27, 170 00 Praha 7.",
]


def postav_pravni():
    udaje = "".join('<div><dt>%s</dt><dd>%s</dd></div>' % (esc(a), esc(b)) for a, b in UDAJE)
    prava = "".join('<li>%s</li>' % esc(x) for x in PRAVA)

    telo = """
<main>
  <section class="hero hero-uzsi">
    <div class="obal uzky">
      <p class="nadtitul">Právní informace</p>
      <h1 class="nadpis-str">Kdo web provozuje a co se tu děje s údaji</h1>
      <p class="tvrzeni-pod">Krátce a bez právničiny. Kdyby ti něco nebylo jasné, napiš mi.</p>
    </div>
  </section>

  <div class="pravni">
    <section>
      <h2>Kdo tenhle web provozuje</h2>
      <dl class="udaje">{udaje}</dl>
    </section>

    <section>
      <h2>Co tenhle web o tobě sbírá</h2>
      <p>Sám o sobě nic. Není tu žádná analytika ani žádný reklamní kód a neukládám ti do prohlížeče vlastní cookies. Nemusíš tu nic odklikávat, protože tu není co povolovat. Jediná výjimka je odběr novinek níž, a ten běží mimo tenhle web a jen když se k němu sám přihlásíš.</p>
      <p>Písma, obrázky i styly se načítají z tohoto webu, ne od Googlu ani odjinud. Tvoje IP adresa se tím pádem nikomu třetímu neposílá.</p>
    </section>

    <section>
      <h2>Co je sem vložené odjinud</h2>
      <ul>
        <li><b>Video</b> je z YouTube v režimu bez cookies. Dokud na něj neklikneš, neposílá se nikam nic. Jak ho spustíš, dozví se Google tvoji IP adresu a že jsi ho pustil. Platí pak <a href="https://policies.google.com/privacy?hl=cs" rel="noopener">zásady Googlu</a>.</li>
        <li><b>Server.</b> Web běží na GitHub Pages. Poskytovatel serveru vidí IP adresy návštěvníků v technických záznamech, stejně jako každý webový server na světě. Já se k nim nedostanu.</li>
      </ul>
    </section>

    <section>
      <h2>Kam vedou odkazy z webu</h2>
      <p>Na Skool, na Calendly, na Instagram a na můj e-mail. Jak klikneš, jsi u nich a platí jejich pravidla, ne moje.</p>
      <p>Když tam o sobě něco zadáš, třeba si na Calendly vybereš termín hovoru nebo mi napíšeš na Instagram, dostane se to ke mně. Pracuju s tím jen proto, abych se ti ozval a ten hovor s tebou odbyl. Držím si to po dobu, kdy to má smysl, nikomu to neprodávám a nikam to dál neposílám.</p>
    </section>

    <section id="emaily">
      <h2>E-maily o sourcing mapě</h2>
      <p>Když se přihlásíš k odběru, uložím si tvůj e-mail a kraj, pokud ho vyplníš. Použiju je jen k tomu, abych ti napsal, až na sourcing mapu přibydou místa, případně místa u tebe. Nic jiného ti posílat nebudu a nikomu je nedám.</p>
      <ul>
        <li><b>Právní základ</b> je tvůj souhlas, který dáváš zaškrtnutím ve formuláři.</li>
        <li><b>Kde to leží:</b> formulář i seznam běží v Notionu (Notion Labs, Inc.), který pro mě data zpracovává.</li>
        <li><b>Jak dlouho:</b> dokud se neodhlásíš.</li>
        <li><b>Odhlášení:</b> stačí odpovědět na kterýkoli můj e-mail, nebo napsat na <a href="mailto:{mail}">{mail}</a>. Pak ti už nic nepřijde. E-mail si nechám jen s poznámkou, že nechceš nic dostávat, aby ti omylem nic nepřišlo znovu.</li>
      </ul>
    </section>

    <section>
      <h2>Sourcing mapa</h2>
      <p>Místa na <a href="/sourcing.html">sourcing mapě</a> pocházejí z veřejných registrů Státní veterinární správy (prodejci syrového mléka a zpracovatelé živočišných produktů registrovaní pro přímý prodej). Firmy a farmy ukazuju s názvem a adresou tak, jak je zveřejňuje SVS. Soukromé chovatele ukazuju jen podle obce, bez jména a ulice.</p>
      <p>Jste na mapě a nechcete tam být, nebo je něco špatně? Napište mi na <a href="mailto:{mail}">{mail}</a> a do pár dní to opravím nebo odstraním.</p>
    </section>

    <section>
      <h2>Co s tím můžeš udělat</h2>
      <p>Cokoli z tohohle a stačí mi napsat na <a href="mailto:{mail}">{mail}</a>:</p>
      <ul>{prava}</ul>
    </section>

    <section>
      <h2>Podmínky Akademie a osobního vedení</h2>
      <p>Akademie i osobní vedení mají svoje obchodní podmínky a svoje zásady zpracování osobních údajů. Dostaneš je k přečtení dřív, než za cokoli zaplatíš. Jsou odkazované v nabídce a ve faktuře a bez nich se nic neuzavírá.</p>
      <p>Tenhle web nic neprodává. Jenom vysvětluje, co dělám, a odkazuje tě dál.</p>
    </section>

    <section>
      <h2>Povaha obsahu</h2>
      <p>Obsah tohoto webu a Akademie má informativní a vzdělávací charakter. Nejde o poskytování zdravotních služeb ve smyslu zákona č. 372/2011 Sb. a provozovatel není poskytovatelem zdravotních služeb. Využití uvedených informací je na vlastní odpovědnost čtenáře.</p>
    </section>

    <section>
      <h2>Obsah webu</h2>
      <p>Texty, obrázky, mapa i celý obsah Akademie jsou moje autorské dílo. Číst si to můžeš kolikrát chceš. Kopírovat to jinam nebo to vydávat za svoje ne.</p>
    </section>

    <p class="datum">Naposledy upraveno 27. 9. 2026</p>
  </div>

  <section class="pas zaver-pas">
    <div class="obal uzky stred">
      <div class="ozdoba" aria-hidden="true">◆</div>
      <a class="cta-druhy" href="/kontakt.html">Kontakt</a>
    </div>
  </section>
</main>
""".format(udaje=udaje, prava=prava, mail=MAIL)

    stranka = HLAVA.format(titulek="Právní informace · Život vysvětlen",
                           popis="Kdo web provozuje, co se tu děje s údaji a jaké máš práva.",
                           kanon="pravni.html", ogobr="mapa/hero.jpg",
                           skool=SKOOL) + telo + PATA.format(skool=SKOOL)
    open("pravni.html", "w", encoding="utf-8").write(stranka)


# ---------------------------------------------------------------- mapa.html
# Mapa se sem kopiruje z ~/Work/skool/export-do-skoolu/mapa-akademie.html.
# Ta ma vlastni inline CSS a tahne pisma od Googlu. Na verejnem webu to nechceme
# (odesilalo by to IP navstevniku Googlu), takze to tady prepneme na nase pisma.
PISMA_MISTNE = """<link rel="preload" href="/pisma/cinzel.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/pisma/cormorant.woff2" as="font" type="font/woff2" crossorigin>
<style>
@font-face{font-family:'Cinzel';src:url('/pisma/cinzel.woff2') format('woff2');font-weight:400 900;font-style:normal;font-display:swap}
@font-face{font-family:'Cormorant Garamond';src:url('/pisma/cormorant.woff2') format('woff2');font-weight:300 700;font-style:normal;font-display:swap}
@font-face{font-family:'Cormorant Garamond';src:url('/pisma/cormorant-italic.woff2') format('woff2');font-weight:300 700;font-style:italic;font-display:swap}
</style>"""


def oprav_mapu():
    """Vymeni Google Fonts v mape za pisma z tohoto webu. Da se poustet opakovane."""
    if not os.path.exists("mapa.html"):
        return "mapa.html chybi"
    h = open("mapa.html", encoding="utf-8").read()
    if "fonts.googleapis" not in h:
        return "mapa.html: pisma uz jsou mistni"
    h = re.sub(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^"]*">',
               PISMA_MISTNE, h, count=1)
    open("mapa.html", "w", encoding="utf-8").write(h)
    return "mapa.html: pisma prepnuta na mistni"


PATA_MAPY = """<footer style="max-width:1060px;margin:0 auto;padding:44px clamp(18px,4vw,28px) 56px;\
text-align:center;border-top:1px solid rgba(198,161,91,.14)">
  <p style="font-family:'Cinzel',serif;font-size:.68rem;letter-spacing:.2em;text-transform:uppercase;color:#6f6353">
    Matyáš Jakeš · IČO 23494204 ·
    <a href="/pravni.html" style="color:#7d6031">Právní informace a zásady</a> ·
    <a href="/kontakt.html" style="color:#7d6031">Kontakt</a>
  </p>
</footer>
</body>"""


def pata_mapy():
    """Doplni do mapy patu s odkazem na pravni informace. Da se poustet opakovane."""
    if not os.path.exists("mapa.html"):
        return "mapa.html chybi"
    h = open("mapa.html", encoding="utf-8").read()
    if "/pravni.html" in h:
        return "mapa.html: pata uz tam je"
    h = h.replace("</body>", PATA_MAPY, 1)
    open("mapa.html", "w", encoding="utf-8").write(h)
    return "mapa.html: pata s pravnimi informacemi doplnena"


import _sourcing


if __name__ == "__main__":
    n = postav_pribeh()
    postav_index()
    postav_11()
    postav_kontakt()
    postav_pravni()
    print(oprav_mapu())
    print(pata_mapy())
    print("sourcing.html: %d mist" % _sourcing.postav(HLAVA, PATA, SKOOL, esc))
    print("pribeh.html: %d bloku" % n)
    for f in ("index.html", "jedna-na-jedna.html", "kontakt.html", "pravni.html"):
        print("%-22s %d znaku" % (f, os.path.getsize(f)))
