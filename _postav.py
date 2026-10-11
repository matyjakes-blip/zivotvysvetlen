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

# ---- uvodni fotka (Matyas dodá portrét dle vkusu, 5. 10. 2026) ----
# None = na webu je prázdné políčko. Až ji dodá: uložit do media/ a sem napsat cestu, např. "/media/matyas-uvod.jpg"
FOTO_UVOD = "/media/matyas-uvod.jpg"   # 6. 10. 2026: „prozatím tyto fotky, od budoucna přidám / změním"
FOTO_UVOD_POPIS = "Matyáš Jakeš"

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
<meta name="google-site-verification" content="K5nMPWFlkAFN3Gpmh8F9qS0GFZt2nsEMVbkdj5riIac">
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
<link rel="preload" href="/pisma/instrument-sans.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/pisma/cormorant.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/styl.css">
</head>
<body>
<header class="hlavicka">
  <a class="znacka" href="/">Život vysvětlen</a>
  <nav class="nav" aria-label="Hlavní">
    <a href="/akademie.html">Akademie</a>
    <a href="/sourcing.html">Sourcing mapa</a>
    <a href="/jedna-na-jedna.html">Osobní vedení</a>
    <a href="/pribeh.html">O mně</a>
  </nav>
  <div class="hlavicka-vpravo">
    <a class="cta-maly" href="{skool}">Vstoupit</a>
    <details class="menu">
      <summary aria-label="Menu"><span></span></summary>
      <div class="menu-obsah">
        <a href="/">Úvod</a>
        <a href="/akademie.html">Akademie</a>
        <a href="/sourcing.html">Sourcing mapa</a>
        <a href="/jedna-na-jedna.html">Osobní vedení 1:1</a>
        <a href="/pribeh.html">O mně</a>
        <a href="/kontakt.html">Kontakt</a>
      </div>
    </details>
  </div>
</header>
"""

PATA = """
<footer class="pata">
  <div class="ozdoba" aria-hidden="true">◆</div>
  <p class="znacka-pata">Život vysvětlen</p>
  <p class="drobne">Matyáš Jakeš · <a href="{skool}">Akademie na Skoolu</a> · <a href="/akademie.html">Akademie</a> · <a href="/jedna-na-jedna.html">Osobní vedení 1:1</a> · <a href="/pribeh.html">O mně</a> · <a href="/sourcing.html">Sourcing mapa</a> · <a href="/kontakt.html">Kontakt</a></p>
  <p class="drobne">Obsah webu a Akademie je vzdělávací, nejde o zdravotní služby.</p>
  <p class="drobne">IČO 23494204 · <a href="/pravni.html">Právní informace a zásady</a> · <a href="/jak-mapa-funguje.html">Jak mapa funguje</a></p>
</footer>
<script src="/web.js" defer></script>
</body>
</html>
"""


# verze stylu a skriptu v odkazu: po každé změně se v prohlížečích načte nový soubor, ne starý z mezipaměti
import hashlib
# NAHLED=1 python3 _postav.py → i zástupná místa (jen pro náhledy); bez toho vznikne verze bezpečná pro živý web
NAHLED = os.environ.get("NAHLED") == "1"
def _verze(soubor):
    try:
        return hashlib.md5(open(soubor, "rb").read()).hexdigest()[:8]
    except OSError:
        return "0"
HLAVA = HLAVA.replace('href="/styl.css"', 'href="/styl.css?v=%s"' % _verze("styl.css"))
PATA = PATA.replace('src="/web.js"', 'src="/web.js?v=%s"' % _verze("web.js"))


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


def _fotorada(skupina):
    from PIL import Image
    figs = []
    for f in skupina:
        try:
            w, h = Image.open(os.path.join("pribeh", f)).size
        except Exception:
            w, h = 3, 4
        figs.append('<figure style="--p:%.3f"><img src="/pribeh/%s" alt="" loading="lazy" width="%d" height="%d"></figure>' % (w / h, f, w, h))
    return '<div class="fotorada%s">%s</div>' % (" jedna" if len(skupina) == 1 else "", "".join(figs))


def pribeh_html():
    """celý text lekce 0.0 jeho slovy, fotky na původních místech v řadách se stejnou výškou"""
    kusy = nacti_pribeh()
    ven, i = [], 0
    while i < len(kusy):
        typ, v = kusy[i]
        if typ == "obr":
            skupina = []
            while i < len(kusy) and kusy[i][0] == "obr":
                skupina.append(kusy[i][1]); i += 1
            ven.append(_fotorada(skupina))
            continue
        ven.append("<p>%s</p>" % v); i += 1
    return "\n".join(ven)


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
                           popis="Od 55 kilo a neplodnosti přes 106 kilo a akné až sem. Celá cesta, bez vynechání.",
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


# lev patří jen k programu 1:1 (Matyáš 10. 10.), ne vedle „Život vysvětlen“
ODZNAK_PROGRAMU = '<img class="cesta-odznak" src="/media/lev/odznak.svg" alt="" width="52" height="52">'


def pas_cesty():
    karty = []
    for c in CESTY:
        if not c["aktivni"]:
            continue
        body = "".join("<li>%s</li>" % esc(b) for b in c["body"])
        odkaz = c["odkaz"] or (CALENDLY if c["hlavni"] else SKOOL)
        pod = '<span class="pod">%s</span>' % esc(c["pod"]) if c["pod"] else ""
        karty.append(
            '<article class="cesta%s">%s'
            '<p class="cesta-znak">%s</p>'
            '<h3>%s</h3>'
            '<p class="vysvetleni">%s</p>'
            '<ul>%s</ul>'
            '<p class="pro-koho">%s</p>'
            '<div class="dole"><a href="%s">%s</a>%s</div>'
            '</article>'
            % (" hlavni" if c["hlavni"] else "", ODZNAK_PROGRAMU if c["hlavni"] else "", esc(c["znak"]), esc(c["nazev"]),
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


# ---- proměna: posuvník před / po (krok 2 přestavby, 6. 10. 2026) ----
# štítky jen z faktů v lekci 0.0; "Teď · 20 let" = selfie od Matyáše 6. 10. (věk řekl 6. 10.)
PROMENA = [
    # AI vizualizace z jeho skutečných fotek (Gemini, 8. 10. 2026); obličej 15/18 → 20, postava jen 18 → 20
    # (v 15 byl nezletilý: žádné AI tělo z té doby). Originály v _fotky/ai-vystupy/ (mimo git), výtky k dalšímu kolu v POZNAMKY.md.
    # 15 let z důkazu pryč (Matyáš 11. 10.: „dal bych pryč 15yo variantu z důkazu úplně“)
    dict(klic="o18", rezim="o", vek="18", nazev="Obličej, 18 let",
         pred="/media/dukaz/ai-18.jpg", po="/media/dukaz/ai-20.jpg",
         stitek_pred="18 let · 106 kg", stitek_po="20 let · 94 kg"),
    dict(klic="p18", rezim="p", vek="18", nazev="Postava, 18 let",
         pred="/media/dukaz/ai-p18.jpg", po="/media/dukaz/ai-p20.jpg",
         stitek_pred="18 let · 106 kg", stitek_po="20 let · 94 kg"),
]
REZIMY = [("o", "Obličej"), ("p", "Postava")]
VEKY = [("18", "18 let")]

# skutečné fotky pod posuvníkem: (soubor, věk, údaj, poznámka)
SKUTECNE = [
    ("/pribeh/0.0__01-patnact-selfie.jpg", "15 let", "55 kg", ""),
    ("/pribeh/0.0__03-patnact-postava.jpg", "15 let", "167 cm · 55 kg", ""),
    ("/pribeh/0.0__06-sedmnact-bulk.jpg", "16 let", "182 cm · 95 kg", "+40 kg za rok"),
    ("/pribeh/0.0__07-akne-zblizka.jpg", "17 let", "akné", ""),
    ("/pribeh/0.0__11-pred-ctyri-mesice.jpg", "18 let", "106 kg", "před změnou stravy"),
    ("/pribeh/0.0__12-po-ctyrech-mesicich.jpg", "18 let", "−15 kg", "o 4 měsíce později"),
    ("/media/matyas-uvod.jpg", "20 let", "191 cm · 94 kg", "dnes"),
]

# okno „Co se změnilo a proč": jen jeho věty (lekce 0.0 a 1.4.5), nic dopsaného; názvy záložek jsou moje
PROC = [
    ("zkousel", "Co jsem zkoušel", [
        "A jako by toho nebylo málo, o pár měsíců později se mi brutálně rozjelo akné. Totální breakout. Psychicky mě to úplně ničilo. Zkoušel jsem všechno – drahý skincare, červený lampy, celerový džusy, kosmetičky, různé detox kůry... a nic. **Jen se to horšilo.** Až mi došlo, že všechny ty chemický přípravky vlastně tělo jen ještě víc zanáší.",
     ], "Lekce 0.0 · Můj příběh", "/pribeh.html"),
    ("testy", "Co ukázaly testy", [
        "Šel jsem k doktorce na krevní testy, protože už jsem fakt nevěděl, co se se mnou děje – a byla úplně v šoku. Řekla mi, že mám hyperurikémii – zvýšenou hladinu kyseliny močový, a to na úrovni 60letýho chlapa. Zároveň jsem si nechal zkontrolovat i testosteron, a ten byl taky úplně na dně.",
     ], "Lekce 0.0 · Můj příběh", "/pribeh.html"),
    ("zmena", "Co se změnilo", [
        "Okamžitě po správné dietě se mi zastavil zánět, kyselina močová a močovina se vrátili do normálu. Můj testosteron vystřelil, můj metabolismus se dal zpátky do normálu, vysekal jsem 15 kilo a vypadal 10 krát lépe. Od té doby jsem nikdy nebyl šťastnější.",
        "Hormony mají neskutečný vliv na člověka a hrají zásadní roli ve vývinu jeho vzhledu, zdraví orgánů, metabolismu, a psychiky.",
     ], "Lekce 0.0 · Můj příběh", "/pribeh.html"),
    ("akne", "Proč akné", [
        "**Znamená:** chronické vylučování kůží a ukládání navázané na hormony, na střevní stagnaci a na psychický terén.",
        "**Pohání:** zpracované potraviny, semenné oleje, rafinované sacharidy · hormonální stres, tedy antikoncepce, endokrinní disruptory, narušený spánek · chronická zácpa nebo líná játra · sebekritika, stud, srovnávání, starosti.",
        "**Podpora:** úplný reset stravy · denní průchodné střevo, podpora lymfy pohybem · přírodní péče o pleť, tedy syrové tuky a prosté mytí bez odmastení · medové nebo jílové masky · méně obrazovek a srovnávání, léčení sebeobrazu · dost slunce a spánku.",
     ], "Lekce 1.4.5 · Aplikované dekódování příznaků", SKOOL),
]


def pas_promena():
    prep_rezim = "".join(
        '<button type="button" class="prepinac-tl" data-rezim="%s" aria-pressed="%s">%s</button>'
        % (k, "true" if i == 0 else "false", esc(n)) for i, (k, n) in enumerate(REZIMY))
    prep_vek = "".join(
        '<button type="button" class="prepinac-tl" data-vek="%s" aria-pressed="%s">%s</button>'
        % (k, "true" if k == "18" else "false", esc(n)) for k, n in VEKY)
    posuvniky = "".join(
        '<div class="posuvnik" data-par="%s" data-rezim="%s" data-vek="%s">'
        '<img class="po" src="%s" alt="%s: %s" width="720" height="960" loading="lazy">'
        '<div class="pred-obal"><img src="%s" alt="%s: %s" width="720" height="960" loading="lazy"></div>'
        '<span class="stitek stitek-pred">%s</span><span class="stitek stitek-po">%s</span>'
        '<span class="stitek-ai">Vizualizace AI</span>'
        '<span class="predel" aria-hidden="true"><span class="madlo"></span></span>'
        '<input class="posuvnik-ovladac" type="range" min="0" max="100" value="50" aria-label="%s: posunout předěl mezi před a po">'
        '</div>'
        % (p["klic"], p["rezim"], p["vek"], p["po"], esc(p["nazev"]), esc(p["stitek_po"]), p["pred"], esc(p["nazev"]), esc(p["stitek_pred"]),
           esc(p["stitek_pred"]), esc(p["stitek_po"]), esc(p["nazev"])) for p in PROMENA)
    skutecne = "".join(
        '<figure><img src="%s" alt="Matyáš, %s" loading="lazy" width="300" height="400"><figcaption><b>%s</b><span>%s</span>%s%s</figcaption></figure>'
        % (f, esc(v), esc(v), esc(u), ('<span>%s</span>' % esc(p)) if p else "", "<em>kdy: doplníš</em>" if NAHLED else "")
        for f, v, u, p in SKUTECNE)
    zalozky = "".join(
        '<button type="button" class="zalozka" data-zalozka="%s" aria-selected="%s">%s</button>'
        % (k, "true" if i == 0 else "false", esc(n)) for i, (k, n, _, _, _) in enumerate(PROC))
    panely = "".join(
        '<section class="panel" data-panel="%s"><h3>%s</h3>%s<p class="zdroj"><a href="%s">%s</a></p></section>'
        % (k, esc(n), "".join("<p>%s</p>" % md_inline(t) for t in texty), odkaz, esc(zdroj))
        for k, n, texty, zdroj, odkaz in PROC)
    return """
  <section class="pas promena" id="promena">
    <div class="obal">
      <div class="promena-mriz">
        <div class="promena-hlava">
          <p class="nadtitul">Důkaz</p>
          <h2>Nejdřív jsem to zkusil na sobě</h2>
        </div>
        <div class="promena-obr">
          <div class="prepinac-radek"><div class="prepinac" role="group" aria-label="Co porovnat">%s</div></div>
          %s
          <p class="popisek">Táhni předělem do stran · Vizualizace vytvořená AI z mých skutečných fotek · výsledky jsou individuální</p>
        </div>
        <div class="promena-text">
          <ol class="osa">
            <li><b>18 let</b><span>182 cm · 106 kg</span></li>
            <li><b>20 let</b><span>191 cm · 94 kg</span></li>
          </ol>
          <p>Moje důvěryhodnost není v tom, že jsem to vždycky věděl. Je v tom, že jsem si tu špatnou cestu prošel celou.</p>
          <div class="tlacitka">
            <a class="cta" href="#proc">Co se změnilo a proč</a>
            <a class="cta-druhy" href="/pribeh.html">Celý příběh</a>
          </div>
        </div>
      </div>
    </div>
  </section>
  <div class="clanek okno-proc" id="proc" role="dialog" aria-modal="true" aria-labelledby="proc-nadpis">
    <a class="clanek-pozadi" href="#promena" aria-label="Zavřít"></a>
    <div class="clanek-okno">
      <a class="clanek-zavrit" href="#promena" aria-label="Zavřít">×</a>
      <p class="nadtitul" id="proc-nadpis">Co se změnilo a proč</p>
      <div class="zalozky" role="tablist">%s</div>
      <div class="panely">%s</div>
    </div>
  </div>
""" % (prep_rezim, posuvniky, zalozky, panely)


# ---- starý × nový způsob (krok 3 přestavby, návrh 7. 10. 2026) ----
# jen jeho věty z lekcí 0.1 a 1.4.3, ubraná slova na začátku vět (viz chat 7. 10.); moje jsou jen slova Běžně / Tady
ZPUSOB_NADPIS = "Rozdíl je zásadní"
ZPUSOB_POD = "Tohle je ten hlavní rozdíl proti všemu ostatnímu, co se v téhle oblasti prodává."
ZPUSOB = [
    ("Moderní medicína se ptá: jak ten příznak zastavíme?",
     "Terénní myšlení se ptá: jak pomůžeme tělu dokončit, co začalo?"),
    ("Kurzů o tom, jak být zdravý, jsou tisíce a většina z nich ti prodá další protokol.",
     "Tady nikdy nedostaneš odpověď typu „ber tohle“. Vždycky dostaneš proč."),
    ("Seznam si musíš pamatovat.",
     "Mechanismus si pamatovat nemusíš. Ten pochopíš jednou a od té chvíle si každou další otázku zodpovíš sám."),
    ("Jídelníček přestane platit v okamžiku, kdy ti dojde jedna surovina.",
     "Princip platí i v cizí zemi na dovolené."),
    ("Přidat si do života dvacet nových povinností.",
     "Odebrat věci, které tělu překážejí, a vrátit mu podmínky, se kterými počítá."),
]


def pas_zpusob():
    radky = "".join(
        '<div class="zpusob-radek">'
        '<p class="bezne"><span class="zpusob-stitek">Běžně</span><span class="znak" aria-hidden="true">×</span>%s</p>'
        '<p class="tady"><span class="zpusob-stitek">Tady</span><span class="znak" aria-hidden="true"></span>%s</p>'
        '</div>' % (esc(a), esc(b)) for a, b in ZPUSOB)
    return """
  <section class="pas zpusob" id="rozdil">
    <div class="obal">
      <h2>%s</h2>
      <p class="text-stred">%s</p>
      <div class="zpusob-tabulka">
        <div class="zpusob-hlava" aria-hidden="true"><span>Běžně</span><span>Tady</span></div>
        %s
      </div>
    </div>
  </section>
""" % (esc(ZPUSOB_NADPIS), esc(ZPUSOB_POD), radky)


# ---- galerie nejlepších fotek (návrh 7. 10.; fotky dodá Matyáš, teď jen zástupné z _nahledy) ----
GALERIE = ["/_nahledy/galerie/g%d.jpg" % i for i in range(1, 7)] if NAHLED else []


def pas_galerie():
    if not GALERIE:
        return ""
    fotky = "".join('<figure><img src="%s" alt="Matyáš Jakeš" loading="lazy" width="640" height="800"></figure>' % f for f in GALERIE)
    return """
  <section class="pas galerie-pas">
    <div class="obal">
      <p class="nadtitul">Galerie</p>
      <h2>Zdraví je vidět</h2>
    </div>
    <div class="galerie-pruh">%s</div>
  </section>
""" % fotky


# kartičky v úvodu: hlavní fotka + jeho fotky z 9. 10. 2026 (šatna: kamarád ořízlý, letadlo: spolucestující rozmazaná) (balíček, táhne se do strany, po poslední zase první)
FOTKY_UVOD = ["/media/uvod/%s.jpg" % n for n in ("hory", "podcast", "zapad", "ostrovy", "slunce", "satna", "garda", "kokos", "letadlo", "more", "zrcadlo")]


def uvod_foto():
    if FOTO_UVOD and not FOTKY_UVOD:
        return '<img src="%s" alt="%s" width="800" height="1000" fetchpriority="high">' % (FOTO_UVOD, esc(FOTO_UVOD_POPIS))
    if FOTO_UVOD:
        vse = [FOTO_UVOD] + FOTKY_UVOD
        n = len(vse)
        karty = "".join(
            '<figure class="fotokarta" data-poz="%d" style="z-index:%d"><img src="%s" alt="%s" width="800" height="1000" draggable="false"%s></figure>'
            % (min(i, 3), n - i, f, esc(FOTO_UVOD_POPIS), ' fetchpriority="high"' if i == 0 else ' loading="lazy"')
            for i, f in enumerate(vse))
        return ('<div class="karty" data-karty><div class="karty-balik" tabindex="0" aria-label="Moje fotky, táhni do strany">%s</div>'
                '<div class="karty-ovladani"><button type="button" class="karty-tl" data-smer="-1" aria-label="Předchozí fotka"></button>'
                '<span class="karty-pocet" aria-live="polite">1 / %d</span>'
                '<button type="button" class="karty-tl" data-smer="1" aria-label="Další fotka"></button></div></div>' % (karty, n))
    # prázdné políčko, dokud Matyáš nedodá fotku (na živý web takhle nepouštět)
    return '<div class="foto-misto"><b>Sem přijde tvoje fotka</b><small>portrét na výšku, poměr 4 : 5</small></div>'


def pas_video():
    # video se z YouTube načte až po kliknutí (web.js); do té doby jen místní náhled, nic se neposílá Googlu
    if not VIDEO:
        return ""
    vid = VIDEO.rstrip("/").split("/")[-1].split("?")[0]
    return """
  <section class="pas video-pas">
    <div class="obal">
      <div class="video-ram">
        <a class="video-spust" href="https://www.youtube.com/watch?v=%s" data-video="%s?autoplay=1&amp;rel=0">
          <img src="/media/video-nahled.jpg" alt="" width="960" height="540" loading="lazy">
          <span class="video-play" aria-hidden="true"></span>
          <span class="sr">Přehrát video: %s</span>
        </a>
      </div>
      <p class="popisek">%s</p>
      <p class="drobne">Video se načte z YouTube až po kliknutí.</p>
    </div>
  </section>
""" % (vid, VIDEO, esc(VIDEO_POPIS), esc(VIDEO_POPIS))


def postav_index():
    video = pas_video()

    poradi = "".join(
        '<li><b>%d</b><span><strong>%s</strong>, %s</span></li>' % (i + 1, esc(a), esc(b))
        for i, (a, b) in enumerate(PORADI))

    pravidla = "".join(
        '<section class="pravidlo"><h3>%s</h3><p>%s</p></section>' % (esc(a), esc(b))
        for a, b in PRAVIDLA)

    moduly = "".join(
        '<li><b>%s</b><span><strong>%s</strong><em>%s</em></span></li>' % (c, esc(n), esc(p))
        for c, n, p in MODULY)

    telo = """
<main>
  <section class="uvod">
    <div class="obal uvod-mriz">
      <div class="uvod-text">
        <p class="nadtitul">Život vysvětlen</p>
        <h1>Matyáš Jakeš</h1>
        <p class="tvrzeni">Postava, energie, klid i vzhled jsou vedlejší produkty.<strong>Ne cíl.</strong></p>
        <p class="tvrzeni-pod">Oprav terén a biologie, psychika i to, kdo jsi, začnou vyjadřovat to, co měly celou dobu.</p>
        <div class="tlacitka">
          <a class="cta" href="/akademie.html">Vstoupit do Akademie</a>
          <a class="cta-druhy" href="/jedna-na-jedna.html">Osobní vedení 1:1</a>
        </div>
        <p class="psali"><a class="psali-titul" href="#hoste">Psali o mně a byl jsem hostem</a><a href="#respekt">Respekt</a><a href="#hoste">Debatní deník</a><a href="#hoste">POD 10</a><a href="#hoste">Světy proti sobě</a></p>
      </div>
      <figure class="uvod-foto">{foto}</figure>
    </div>
  </section>
{video}
{promena}{zpusob}
{akademie}{galerie}
  <section class="pas sourcing-pas">
    <div class="obal uzky stred">
      <p class="nadtitul">Zdarma</p>
      <h2>Kde to všechno koupit</h2>
      <p class="text-stred">Přes tři tisíce míst v Česku, kde se dá koupit syrové mléko, maso, zvěřina, med a ryby přímo od chovatele. Všechno na jedné mapě.</p>
      <a class="cta-druhy" href="/sourcing.html">Otevřít sourcing mapu</a>
    </div>
  </section>
{cesty}{recenze}{podcasty}
  <section class="pas zaver-pas">
    <div class="obal uzky stred">
      <div class="ozdoba" aria-hidden="true">◆</div>
      <p class="vyzva">Každý modul staví na předchozím a nic v něm nezazní bez vysvětlení.<strong>Kdo přeskočí rovnou na viry, bude mít pocit, že tomu rozumí, a bude se mýlit.</strong></p>
      <div class="tlacitka" style="justify-content:center"><a class="cta" href="/akademie.html">Vstoupit do Akademie</a><a class="cta-druhy" href="/jedna-na-jedna.html">Osobní vedení 1:1</a></div>
    </div>
  </section>
</main>
""".format(skool=SKOOL, video=video, podcasty=pas_podcasty(), cesty=pas_cesty(), foto=uvod_foto(), promena=pas_promena(), zpusob=pas_zpusob(), akademie=_akademie.pas_akademie(_akademie.data()), galerie="", recenze=_recenze.pas_recenze(),
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


# ---------------------------------------------------------------- jak mapa funguje (krok 7, 9. 10. 2026)
def postav_jak_mapa():
    import json as _json
    d = _json.load(open("sourcing/data.json", encoding="utf-8"))
    pocet = sum(len(o["m"]) for o in d["obce"])
    telo = """
<main>
  <section class="hero hero-uzsi">
    <div class="obal uzky">
      <p class="nadtitul">Sourcing mapa</p>
      <h1 class="nadpis-str">Jak mapa funguje</h1>
      <p class="tvrzeni-pod">Odkud jsou místa, co se na mapu dostane a jak opravit nebo odstranit údaj.</p>
    </div>
  </section>

  <section class="pas">
    <div class="obal uzky pravidla-mapy">
      <h2>Odkud jsou místa</h2>
      <ul>
        <li><b>Registr Státní veterinární správy.</b> Základ mapy. Každý, kdo smí prodávat syrové mléko ze dvora nebo z automatu, bourat maso a zpracovávat zvěřinu, ryby a med pro přímý prodej. Je to seznam lidí, kteří na to mají povolení. O kvalitě to neříká nic. Údaje ze dne {aktualizace}, teď {pocet} míst.</li>
        <li><b>Od lidí.</b> Tipy, které pošleš přes formulář. Každý projdu ručně, než se na mapě objeví, a na mapě jsou označené zvlášť. Nejsou ověřené tak jako registr.</li>
        <li><b>◆ Doporučeno.</b> Farmy, které doporučuju v Akademii.</li>
      </ul>

      <h2>Co se na mapu dostane</h2>
      <ul>
        <li>Místo, kde se dají koupit potraviny přímo od chovatele nebo zpracovatele: syrové mléko, maso, zvěřina, med, ryby, vejce.</li>
        <li>Žádná reklama a žádné osobní údaje soukromých lidí bez jejich souhlasu.</li>
        <li>Jméno toho, kdo tip poslal, nikde nezveřejňuju.</li>
      </ul>

      <h2>Soukromí chovatelé</h2>
      <p>Soukromé chovatele z registru ukazuju jen podle obce, bez jména a ulice. Kdo je chce najít, dohledá je v registru SVS podle čísla.</p>

      <h2>Oprava nebo odstranění</h2>
      <p>Jsi na mapě a nechceš tam být? Je údaj špatně nebo místo už neprodává? Napiš na <a href="mailto:{mail}">{mail}</a> s názvem obce a místa. Opravím to nebo místo z mapy odstraním.</p>

      <h2>Než vyrazíš</h2>
      <p>Údaje se mění. Před cestou si u prodejce ověř, že pořád prodává a kdy. Za to, co prodává, odpovídá prodejce.</p>

      <div class="tlacitka" style="justify-content:center;margin-top:30px"><a class="cta" href="/sourcing.html">Otevřít mapu</a><a class="cta-druhy" href="{form_tipy}" target="_blank" rel="noopener">Přidat místo</a></div>
    </div>
  </section>
</main>
""".format(aktualizace=d.get("aktualizace", ""), pocet="{:,}".format(pocet).replace(",", "\u00a0"), mail=MAIL,
           form_tipy=_sourcing.FORM_TIPY)
    stranka = HLAVA.format(titulek="Jak mapa funguje · Život vysvětlen",
                           popis="Odkud jsou místa na sourcing mapě, co se na ni dostane a jak opravit nebo odstranit údaj.",
                           kanon="jak-mapa-funguje.html", ogobr="mapa/hero.jpg",
                           skool=SKOOL) + telo + PATA.format(skool=SKOOL)
    open("jak-mapa-funguje.html", "w", encoding="utf-8").write(stranka)


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
import _akademie
import _recenze


if __name__ == "__main__":
    n = postav_pribeh()
    postav_index()
    postav_11()
    # návrhy v2 (větev navrhy-v2): nové 1:1 a O mně přepíšou staré
    import _stranky_v2
    rek = _recenze.pas_recenze("Co píšou klienti", jen="klient")
    _stranky_v2.postav_11_v2(HLAVA, PATA, SKOOL, CALENDLY, recenze=rek)
    for v in ("v1", "v3"):   # varianty úvodu jen do náhledů
        _stranky_v2.postav_11_v2(HLAVA, PATA, SKOOL, CALENDLY, varianta=v, soubor="_nahledy/jedna-%s.html" % v, recenze=rek)
    _stranky_v2.postav_pribeh_v2(HLAVA, PATA, SKOOL, pribeh_html())
    postav_kontakt()
    postav_jak_mapa()
    postav_pravni()
    print(oprav_mapu())
    print(pata_mapy())
    print("sourcing.html: %d mist" % _sourcing.postav(HLAVA, PATA, SKOOL, esc))
    print("lekce-zdarma.html: %d min" % _akademie.postav_lekci_zdarma(HLAVA, PATA, SKOOL))
    print("akademie.html:", _akademie.postav_stranku(HLAVA, PATA, SKOOL, recenze=_recenze.pas_recenze("Co píšou studenti", jen="student")))
    print("pribeh.html: %d bloku" % n)
    for f in ("index.html", "jedna-na-jedna.html", "kontakt.html", "pravni.html"):
        print("%-22s %d znaku" % (f, os.path.getsize(f)))
    if not FOTO_UVOD:
        print("POZOR: úvodní fotka chybí (FOTO_UVOD = None), na hlavní stránce je prázdné políčko. Takhle nepushovat na main.")
    if not NAHLED:
        # pojistka před pushem: na živých stránkách nesmí zůstat nic zástupného
        spatne = []
        for f in glob.glob("*.html") + glob.glob("sourcing/**/*.html", recursive=True) + glob.glob("mapa/**/*.html", recursive=True):
            t = open(f, encoding="utf-8").read()
            for znak in ("/_nahledy/", "doplníš", "recenze zastupna", "foto-misto", "Návrh:", "disabled>"):
                if znak in t:
                    spatne.append("%s: %s" % (f, znak))
        print("POZOR, zástupné věci na živých stránkách: " + "; ".join(spatne) if spatne else "kontrola živých stránek: čisto")
