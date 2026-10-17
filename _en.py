#!/usr/bin/env python3
"""Anglická verze webu (Matyáš 11. 10.: „anglická verze udělej taky ty, chci to v angličtině než to dám do světa“).

Rozhodnutí 11. 10.: „Join the Academy“ = Life Explained (anglický Skool), 1:1 v angličtině s anglickým Calendly,
přeložit celý web včetně příběhu a tří lekcí zdarma, mapu do anglické verze nedávat.

Jak to funguje: české stránky se postaví jako vždycky (_postav.py) a tenhle skript z nich udělá /en/.
Každý odstavec, nadpis a popisek se přeloží podle slovníku _preklad/preklad-*.json (klíč = přesně české HTML).
Když se česká stránka změní a anglický překlad k novému textu chybí, skript to vypíše (a stránka by měla
na tom místě češtinu), takže překlad stačí doplnit do slovníku. Akademie je v angličtině Life Explained,
proto má vlastní blok na úvodu a vlastní stránku.
"""
import glob, html, json, os, re

WEB = "https://zivotvysvetlen.cz"
SKOOL_CZ = "https://www.skool.com/zivot-vysvetlen-1338"
SKOOL_EN = "https://www.skool.com/life-explained-1568"
CAL_CZ = "https://calendly.com/yacashh/1-1-osobni-kvalifikacni-hovor"
CAL_EN = "https://calendly.com/yacashh/1-1-qualification-call-with-matyas"

STRANKY = [  # česká → anglická
    ("index.html", "en/index.html"),
    ("jedna-na-jedna.html", "en/coaching.html"),
    ("pribeh.html", "en/about.html"),
    ("kontakt.html", "en/contact.html"),
    ("pravni.html", "en/legal.html"),
    ("lekce-zdarma.html", "en/free-lesson-disease.html"),
    ("lekce-zdarma-vzhled.html", "en/free-lesson-looks.html"),
    ("lekce-zdarma-hormony.html", "en/free-lesson-hormones.html"),
]
PROTEJSEK = {"akademie.html": "en/academy.html", **dict(STRANKY)}   # česká → anglická (i pro přepínač jazyka)
ODKAZY = {"/": "/en/", "/index.html": "/en/"}
for cz, en in PROTEJSEK.items():
    if cz != "index.html":
        ODKAZY["/" + cz] = "/" + en

# místa, kde se anglická verze vědomě liší od doslovného překladu (Akademie = Life Explained, lekce z české Akademie)
UPRAVY = {
    "Mapa, první týden den po dni a vstupní diagnostika": "Start Here first, then level by level, in a clear order",
    "Celý systém napsaný, čteš vlastním tempem": "The whole system in one place, at your own pace",
    "Další je 1.1.1 · Dvanáct axiomů terénu.": "The rest of the curriculum is inside the Academy.",
    # „v češtině“ v anglické verzi neplatí, věta vypuštěna
    "Tohle není kurz o tom, jak být zdravý. Je to kurz o tom, jak zdraví vlastně funguje. První terénní akademie v češtině.":
        "This isn’t a course on how to be healthy. It’s a course on how health actually works.",
    # překlep „Modul 3 a 3“ opraven i v originále 12. 10. (Modul 3 Prostředí + Modul 4 Výživa)
    "Všimni si, co v tom seznamu <strong>není.</strong> Není tam žádný doplněk, žádný booster a žádný prášek. <strong>Je tam spánek, jídlo, zátěž, světlo a klid.</strong> To je celý Modul 3 a 4.":
        "Notice what <strong>isn’t</strong> on that list. No supplement, no booster, no pill. <strong>It’s sleep, food, load, light and calm.</strong> That’s all of Modules 3 and 4.",
}

# Life Explained: jeho vlastní anglický popis ze Skoolu (opravené jen překlepy: information, your body, an 8-hour)
LE_POPIS = [
    "The modern world is making you sick, ugly, distracted, and spiritually empty by design.",
    "Not because you are weak. Because the signals and information you live in and give your body are not symbiotic with your biology. You will learn how the body was systematically disconnected from the inputs it was built by God for. How the food, light, movement, mindset and environment of modern life are producing disease and suffering. And how to reverse it at the baseline level.",
    "You will also learn what no health course teaches: that the physical terrain and the inner terrain are the same project. That consciousness, frequency, and identity determine what the biology produces. And that a person operating at their genuine frequency physically and spiritually is ungovernable.",
    "6 levels. 13 modules. The complete blueprint. Life Explained is an 8-hour curriculum that dismantles what you were told about health, reality, and human potential and replaces it with what actually works.",
]
LE_UROVNE = [  # názvy a podtituly kurzů v Life Explained (Classroom, 11. 10. 2026)
    ("", "Start Here", "Before you begin, read this first."),
    ("Mind", "Foundation Explained", "The Holy Trinity"),
    ("Mind", "Level 1 · Terrain Explained", "Modern life is biologically hostile by default."),
    ("Body", "Level 2 · Environment Explained", "The body was built for specific inputs."),
    ("Body", "Level 3 · Biology Explained", "The body is a signal-driven biological system."),
    ("Body", "Level 4 · Performance Explained", "Most people go against their biology."),
    ("Spirit", "Level 5 · Life Explained", "The Closing Line"),
]
LEKCE_EN = [("/en/free-lesson-looks.html", "Looks as the visible expression of the inner terrain", "from lesson 5.4"),
            ("/en/free-lesson-hormones.html", "Hormones", "lesson 5.2"),
            ("/en/free-lesson-disease.html", "What disease is", "lesson 1.1")]

BLOKY = ("title", "h1", "h2", "h3", "h4", "p", "li", "blockquote", "figcaption", "summary", "td", "th", "label", "button")
VNORENE = re.compile(r"<(p|div|ul|ol|li|h[1-4]|section|figure|blockquote|table|details)\b")


def upravy_pocty():
    """překlady vět s počty Akademie; klíče se skládají z aktuálních čísel (_akademie.pocty), takže po každé nové
    lekci sedí samy (17. 10. 2026)"""
    import _akademie
    c = _akademie.pocty()
    return {
        c["veta"]: "Six levels, thirteen modules, about eight hours",
        "Tohle byla jedna ze %d lekcí" % c["lekce"]: "This was one lesson from the curriculum",
        "Tohle byla část jedné ze %d lekcí" % c["lekce"]: "This was part of one lesson from the curriculum",
        "Všech %d lekcí, protokoly a komunita. Je v ceně." % c["lekce"]: "The full curriculum, protocols and community. Included.",
        "<b>%d</b><span>lekcí v šesti modulech</span>" % c["lekce"]: "<b>%d</b><span>lessons across six modules</span>" % c["lekce"],
        "<b>%s</b><span>slov výkladu</span>" % c["slov_cz"]: "<b>%s</b><span>words of explanation</span>" % c["slov_en"],
    }


def slovnik():
    d = {}
    for f in sorted(glob.glob("_preklad/preklad-*.json")):
        if f.endswith("preklad-uzly.json"):
            continue
        d.update(json.load(open(f, encoding="utf-8")))
    d.update(UPRAVY)
    d.update(upravy_pocty())
    uzly = json.load(open("_preklad/preklad-uzly.json", encoding="utf-8")) if os.path.exists("_preklad/preklad-uzly.json") else {}
    uzly.update(UPRAVY)
    uzly.update(upravy_pocty())
    return d, uzly


def les(cesta):
    return "en/" + os.path.basename(cesta) if not cesta.startswith("en/") else cesta


def vyrizni(t, zacatek):
    i = t.find(zacatek)
    if i < 0:
        return t, -1
    j = t.find("</section>", i) + len("</section>")
    return t[:i] + t[j:], i


def blok_le(uvod=True):
    urovne = "".join('<div class="le-uroven"><p class="le-vrstva">%s</p><h3>%s</h3><p>%s</p></div>' % (html.escape(v or "Start"), html.escape(n), html.escape(p))
                     for v, n, p in LE_UROVNE)
    popis = "".join("<p class=\"text-stred\">%s</p>" % html.escape(p) for p in (LE_POPIS[:1] + LE_POPIS[3:] if uvod else LE_POPIS[1:]))
    nadtitul, nadpis = ("The Academy", "Life Explained") if uvod else ("What's inside", "The curriculum")
    tlacitka = ('<a class="cta" href="/en/academy.html">See the Academy</a><a class="cta-druhy" href="/en/free-lesson-looks.html">Read a free lesson</a>'
                if uvod else '<a class="cta" href="%s">Join Life Explained</a><a class="cta-druhy" href="/en/free-lesson-looks.html">Read a free lesson</a>' % SKOOL_EN)
    return """
  <section class="pas akademie-pas akademie-svetla" id="akademie">
    <div class="obal">
      <p class="nadtitul">%s</p>
      <h2>%s</h2>
      %s
      <div class="le-urovne">%s</div>
      <div class="tlacitka" style="justify-content:center;margin-top:26px">%s</div>
    </div>
  </section>
""" % (nadtitul, nadpis, popis, urovne, tlacitka)


def preloz(t, d, uzly, chybi, stranka):
    hotove = set(d.values()) | set(uzly.values())
    # bloky
    for tag in BLOKY:
        def r(m):
            inner = m.group(2)
            k = inner.strip()
            if VNORENE.search(k) or not re.search(r"[A-Za-zÁ-ž]", re.sub(r"<[^>]+>", "", k)):
                return m.group(0)
            if k in d:
                return m.group(1) + inner.replace(k, d[k]) + m.group(3)
            if k in uzly:
                return m.group(1) + inner.replace(k, uzly[k]) + m.group(3)
            if re.search(r"[ěščřžýáíéůúňťďĚŠČŘŽÝÁÍÉŮÚŇŤĎ]", k) and k not in hotove:
                chybi.setdefault(k, set()).add(stranka)
            return m.group(0)
        t = re.sub(r"(<%s(?:\s[^>]*)?>)(.*?)(</%s>)" % (tag, tag), r, t, flags=re.S)
    # atributy a meta
    def ra(m):
        k = m.group(2)
        return m.group(1) + '="' + (d.get(k) or uzly.get(k) or k) + '"'
    t = re.sub(r'\b(alt|aria-label|placeholder|title)="([^"]*)"', ra, t)
    t = re.sub(r'(<meta (?:name|property)="(?:description|og:title|og:description)" content)="([^"]*)"',
               lambda m: m.group(1) + '="' + (d.get(m.group(2)) or uzly.get(m.group(2)) or m.group(2)) + '"', t)
    # zbylé krátké texty (menu, tlačítka, štítky)
    def ru(m):
        s = m.group(1)
        k = s.strip()
        if k in uzly:
            return ">" + s.replace(k, uzly[k]) + "<"
        if k in d:
            return ">" + s.replace(k, d[k]) + "<"
        return m.group(0)
    hlavni = re.split(r"(<script.*?</script>|<style.*?</style>)", t, flags=re.S)
    t = "".join(x if x.startswith(("<script", "<style")) else re.sub(r">([^<>]*[A-Za-zÁ-ž][^<>]*)<", ru, x) for x in hlavni)
    return t


def odkazy(t):
    t = t.replace(SKOOL_CZ, SKOOL_EN).replace(CAL_CZ, CAL_EN)
    def r(m):
        u = m.group(2)
        cesta, _, kotva = u.partition("#")
        if cesta in ODKAZY:
            return m.group(1) + '="' + ODKAZY[cesta] + (("#" + kotva) if kotva else "") + '"'
        return m.group(0)
    return re.sub(r'(href)="(/[^"]*)"', r, t)


def jazykovy_prepinac(t, kam, jazyk):
    """odkaz CZ/EN v hlavičce + hreflang v hlavě"""
    t = re.sub(r'\s*<a class="jazyk"[^>]*>[^<]*</a>', "", t)
    odkaz = '<a class="jazyk" href="%s" hreflang="%s" lang="%s">%s</a>' % (kam, jazyk, jazyk, jazyk.upper().replace("CS", "CZ"))
    return t.replace('<div class="hlavicka-vpravo">', '<div class="hlavicka-vpravo">\n    ' + odkaz, 1)


def hreflang(t, cz_url, en_url):
    t = re.sub(r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*">', "", t)
    tagy = ('<link rel="alternate" hreflang="cs" href="%s">\n<link rel="alternate" hreflang="en" href="%s">\n'
            '<link rel="alternate" hreflang="x-default" href="%s">' % (cz_url, en_url, cz_url))
    return t.replace("</head>", tagy + "\n</head>", 1)


def url(cesta):
    return WEB + "/" + ("" if cesta == "index.html" else cesta.replace("en/index.html", "en/"))


def anglicky_obal(t, en_cesta):
    t = t.replace('<html lang="cs">', '<html lang="en">', 1)
    t = t.replace('content="cs_CZ"', 'content="en_US"')
    t = re.sub(r'(<link rel="canonical" href=")[^"]*(")', r'\g<1>%s\2' % url(en_cesta), t)
    t = re.sub(r'(<meta property="og:url" content=")[^"]*(")', r'\g<1>%s\2' % url(en_cesta), t)
    t, _ = vyrizni(t, '<section class="pas sourcing-pas">')
    return t


def bez_mapy(t):
    """mapa v anglické verzi není: pryč z menu a patičky (až po překladu, ať sedí slovník)"""
    t = re.sub(r'\n\s*<a href="/sourcing\.html">[^<]*</a>', "", t)
    t = re.sub(r'\s*·\s*<a href="/sourcing\.html">[^<]*</a>', "", t)
    t = re.sub(r'\s*·\s*<a href="/jak-mapa-funguje\.html">[^<]*</a>', "", t)
    return t


def postav():
    d, uzly = slovnik()
    chybi = {}
    os.makedirs("en", exist_ok=True)
    for cz, en in STRANKY:
        t = open(cz, encoding="utf-8").read()
        t = anglicky_obal(t, en)
        if cz == "index.html":
            t, i = vyrizni(t, '<section class="pas akademie-pas')
            if i >= 0:
                t = t[:i] + blok_le(uvod=True) + t[i:]
        if cz.startswith("lekce-zdarma"):
            t = t.replace('<p class="tvrzeni-pod">', '<p class="drobne">Translated from the Czech original.</p>\n      <p class="tvrzeni-pod">', 1)
        if '<section class="pas recenze-pas"' in t:
            t = re.sub(r'(<section class="pas recenze-pas"[^>]*>\s*<div class="obal">.*?</h2>)', r'\1<p class="text-stred drobne">Translated from Czech.</p>', t, count=1, flags=re.S)
        t = preloz(t, d, uzly, chybi, en)
        t = bez_mapy(t)
        t = odkazy(t)
        t = jazykovy_prepinac(t, "/" + cz if cz != "index.html" else "/", "cs")
        t = hreflang(t, url(cz), url(en))
        open(en, "w", encoding="utf-8").write(t)
    # stránka Akademie = Life Explained (kostra z anglického úvodu)
    t = open("en/index.html", encoding="utf-8").read()
    i, j = t.index("<main>"), t.index("</main>") + len("</main>")
    hlavni = """<main>
  <section class="ak-uvod">
    <div class="obal ak-uvod-mriz">
      <div>
        <p class="nadtitul">The Academy</p>
        <h1 class="ak-nadpis">Life Explained</h1>
        <p class="ak-veta">%s</p>
        <p class="cisla ak-cisla"><span><b>6</b>levels</span><span><b>13</b>modules</span><span><b>8</b>hours</span></p>
        <div class="tlacitka"><a class="cta" href="%s">Join Life Explained</a><a class="cta-druhy" href="#lekce">Free lessons</a></div>
      </div>
      <figure class="ak-uvod-obr"><img src="/mapa/hero.jpg" alt="The Academy" width="1600" height="1048"></figure>
    </div>
  </section>
%s
  <section class="pas" id="lekce">
    <div class="obal uzky">
      <p class="nadtitul">Free lessons</p>
      <h2>Read before you join</h2>
      <p class="text-stred">Translated from the Czech original, complete, as students have them.</p>
      <ul class="lekce-dalsi">%s</ul>
    </div>
  </section>
</main>""" % (html.escape(LE_POPIS[0]), SKOOL_EN, blok_le(uvod=False),
              "".join('<li><a href="%s">%s</a> · %s</li>' % (u, html.escape(n), html.escape(o)) for u, n, o in LEKCE_EN))
    t = t[:i] + hlavni + t[j:]
    t = re.sub(r"<title>[^<]*</title>", "<title>Life Explained · the Academy</title>", t, count=1)
    t = re.sub(r'(<meta name="description" content=")[^"]*(")', r"\1Life Explained: 6 levels, 13 modules, an 8-hour curriculum on health, terrain and the inner terrain. By Matyáš Jakeš.\2", t, count=1)
    t = re.sub(r'(<link rel="canonical" href=")[^"]*(")', r"\g<1>%s\2" % url("en/academy.html"), t)
    t = re.sub(r'(<meta property="og:url" content=")[^"]*(")', r"\g<1>%s\2" % url("en/academy.html"), t)
    t = jazykovy_prepinac(t, "/akademie.html", "cs")
    t = hreflang(t, url("akademie.html"), url("en/academy.html"))
    open("en/academy.html", "w", encoding="utf-8").write(t)
    # české stránky: přepínač na angličtinu a hreflang
    for cz in glob.glob("*.html"):
        if cz.startswith("google") or cz == "mapa.html":
            continue
        t = open(cz, encoding="utf-8").read()
        en = PROTEJSEK.get(cz)
        t = jazykovy_prepinac(t, "/" + en.replace("en/index.html", "en/") if en else "/en/", "en")
        if en:
            t = hreflang(t, url(cz), url(en))
        open(cz, "w", encoding="utf-8").write(t)
    # sitemap
    s = open("sitemap.xml", encoding="utf-8").read()
    s = re.sub(r"\s*<url><loc>%s/en/[^<]*</loc>[^/]*</url>" % re.escape(WEB), "", s)
    s = re.sub(r"\s*<url>\s*<loc>%s/en/[^<]*</loc>.*?</url>" % re.escape(WEB), "", s, flags=re.S)
    pridat = "".join("\n  <url><loc>%s</loc></url>" % url(en) for en in ["en/index.html", "en/academy.html"] + [e for _, e in STRANKY[1:]])
    s = s.replace("</urlset>", pridat + "\n</urlset>")
    open("sitemap.xml", "w", encoding="utf-8").write(s)
    return chybi


if __name__ == "__main__":
    chybi = postav()
    print("anglická verze: %d stránek, chybí přeložit: %d" % (len(STRANKY) + 1, len(chybi)))
    for k, v in list(chybi.items())[:40]:
        print("  [%s] %s" % (", ".join(sorted(v)), k[:120]))
