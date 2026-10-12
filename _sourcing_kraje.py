#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stránky sourcing mapy po krajích pro vyhledávače (gameplán, Fáze 2: „Stránky pro Google po krajích × potravinách“).
Jedna stránka na kraj, uvnitř sekce po potravinách a místa po okresech a obcích. Data jsou stejná jako na mapě
(sourcing/data.json + sourcing/osm.json): firmy s názvem a adresou z registru, soukromí lidé jen jako počet u obce.
Výstup: sourcing/kraj/<slug>.html, rozcestník sourcing/kraje.html a jejich řádky v sitemap.xml."""
import json, os, re, unicodedata
from collections import defaultdict, OrderedDict

WEB = "https://zivotvysvetlen.cz"
SOUKROMI = ("Soukromý chovatel", "Soukromý prodej")

# název na stránce (česky), „v kraji“ do vět, země
KRAJE = OrderedDict([
    ("Hlavní město Praha",   ("Praha", "v Praze", "cz")),
    ("Středočeský kraj",     ("Středočeský kraj", "ve Středočeském kraji", "cz")),
    ("Jihočeský kraj",       ("Jihočeský kraj", "v Jihočeském kraji", "cz")),
    ("Plzeňský kraj",        ("Plzeňský kraj", "v Plzeňském kraji", "cz")),
    ("Karlovarský kraj",     ("Karlovarský kraj", "v Karlovarském kraji", "cz")),
    ("Ústecký kraj",         ("Ústecký kraj", "v Ústeckém kraji", "cz")),
    ("Liberecký kraj",       ("Liberecký kraj", "v Libereckém kraji", "cz")),
    ("Královéhradecký kraj", ("Královéhradecký kraj", "v Královéhradeckém kraji", "cz")),
    ("Pardubický kraj",      ("Pardubický kraj", "v Pardubickém kraji", "cz")),
    ("Kraj Vysočina",        ("Kraj Vysočina", "v kraji Vysočina", "cz")),
    ("Jihomoravský kraj",    ("Jihomoravský kraj", "v Jihomoravském kraji", "cz")),
    ("Olomoucký kraj",       ("Olomoucký kraj", "v Olomouckém kraji", "cz")),
    ("Zlínský kraj",         ("Zlínský kraj", "ve Zlínském kraji", "cz")),
    ("Moravskoslezský kraj", ("Moravskoslezský kraj", "v Moravskoslezském kraji", "cz")),
    ("Bratislavský kraj",    ("Bratislavský kraj", "v Bratislavském kraji", "sk")),
    ("Trnavský kraj",        ("Trnavský kraj", "v Trnavském kraji", "sk")),
    ("Trenčiansky kraj",     ("Trenčínský kraj", "v Trenčínském kraji", "sk")),
    ("Nitriansky kraj",      ("Nitranský kraj", "v Nitranském kraji", "sk")),
    ("Žilinský kraj",        ("Žilinský kraj", "v Žilinském kraji", "sk")),
    ("Banskobystrický kraj", ("Banskobystrický kraj", "v Banskobystrickém kraji", "sk")),
    ("Prešovský kraj",       ("Prešovský kraj", "v Prešovském kraji", "sk")),
    ("Košický kraj",         ("Košický kraj", "v Košickém kraji", "sk")),
])

# pořadí sekcí a slova do titulku
KAT = [("mleko", "Mléko", "syrové mléko"), ("maso", "Maso", "maso"), ("zverina", "Zvěřina", "zvěřinu"),
       ("med", "Med", "med"), ("vejce", "Vejce", "vejce"), ("ryby", "Ryby", "ryby"),
       ("obchod", "Farmářské obchody", "farmářské obchody"), ("ostatni", "Ostatní", "")]


def slug(s):
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def cislo(n):
    return "{:,}".format(n).replace(",", " ")


def slovo_mist(n):
    return "místo" if n == 1 else ("místa" if 2 <= n <= 4 else "míst")


def nacti():
    d = json.load(open("sourcing/data.json", encoding="utf-8"))
    o = json.load(open("sourcing/osm.json", encoding="utf-8")) if os.path.exists("sourcing/osm.json") else {"obce": []}
    obce = {}
    for x in d["obce"]:
        obce[(x["obec"], x["okres"])] = {"obec": x["obec"], "okres": x["okres"], "kraj": x["kraj"], "m": list(x["m"])}
    for x in o["obce"]:
        k = (x["obec"], x["okres"])
        polozky = [dict(m, s="osm") for m in x["m"]]
        if k in obce:
            obce[k]["m"] += polozky
        else:
            obce[k] = {"obec": x["obec"], "okres": x["okres"], "kraj": x["kraj"], "m": polozky}
    return d, o, obce


def typ(m, d):
    return m["t"] if isinstance(m["t"], str) else d["typy"][m["t"]]


def odkaz(m, d, esc):
    if m.get("s") == "osm":
        u = m.get("w") or ("https://www.openstreetmap.org/" + m["o"])
        return '<a href="%s" rel="noopener nofollow">%s</a>' % (esc(u), "web" if m.get("w") else "OpenStreetMap")
    u = d["registry"][m["u"]] if isinstance(m.get("u"), int) else m.get("u")
    if not u:
        return ""
    if m.get("d"):
        text = "web farmy"
    elif m.get("l"):
        text = "odkaz"
    else:
        text = ("seznam ŠVPS" if m.get("c") == "sk" else "registr SVS") + ((" · " + m["r"]) if m.get("r") else "")
    return '<a href="%s" rel="noopener nofollow">%s</a>' % (esc(u), esc(text))


def zdroj(m):
    if m.get("s") == "osm":
        return "OpenStreetMap"
    if m.get("d"):
        return "doporučeno v Akademii"
    if m.get("l"):
        return "tip od lidí"
    return "ŠVPS SR" if m.get("c") == "sk" else "registr SVS"


def postav(HLAVA, PATA, SKOOL, esc):
    d, o, obce = nacti()
    os.makedirs("sourcing/kraj", exist_ok=True)
    po_krajich = defaultdict(list)
    for x in obce.values():
        if x["kraj"] in KRAJE:
            po_krajich[x["kraj"]].append(x)
    souhrn = []
    for kraj, (nazev, v_kraji, zeme) in KRAJE.items():
        seznam = po_krajich.get(kraj, [])
        if not seznam:
            continue
        s = slug(nazev)
        pocet_kat = defaultdict(int)
        sekce = []
        for k, jmeno, _ in KAT:
            okresy = defaultdict(list)
            for x in seznam:
                mm = [m for m in x["m"] if m["k"] == k]
                if mm:
                    okresy[x["okres"]].append((x, mm))
                    pocet_kat[k] += len(mm)
            if not okresy:
                continue
            bloky = []
            for okres in sorted(okresy, key=lambda t: slug(t)):
                obce_html = []
                for x, mm in sorted(okresy[okres], key=lambda t: slug(t[0]["obec"])):
                    pojm = [m for m in mm if m["n"] not in SOUKROMI]
                    soukr = len(mm) - len(pojm)
                    radky = []
                    for m in sorted(pojm, key=lambda m: (not m.get("d"), not m.get("l"), slug(m["n"]))):
                        cast = ['<b>%s%s</b>' % ("◆ " if m.get("d") else "", esc(m["n"]))]
                        if typ(m, d) != m["n"]:
                            cast.append(esc(typ(m, d)))
                        if m.get("a"):
                            cast.append(esc(m["a"]))
                        oz = odkaz(m, d, esc)
                        if oz:
                            cast.append(oz)
                        zd = zdroj(m) if (m.get("d") or m.get("l") or not oz) else ""
                        radky.append('<li>%s%s</li>' % (" · ".join(cast), (' <span class="kraj-zdroj">%s</span>' % esc(zd)) if zd else ""))
                    if soukr:
                        radky.append('<li class="kraj-soukr">%d× soukromý chovatel, bez jména a adresy</li>' % soukr)
                    obce_html.append('<div class="kraj-obec"><h4>%s <a class="kraj-namape" href="/sourcing.html?obec=%s">na mapě</a></h4><ul>%s</ul></div>'
                                     % (esc(x["obec"]), esc(x["obec"].replace(" ", "+")), "".join(radky)))
                hl = "" if len(okresy) == 1 and okres in (kraj, nazev, "Praha", "Hlavní město Praha") else '<h3>okres %s</h3>' % esc(okres)
                bloky.append(hl + "".join(obce_html))
            sekce.append('<section class="kraj-kat" id="%s"><h2>%s <span class="kraj-pocet">%s</span></h2>%s</section>'
                         % (k, esc(jmeno), cislo(pocet_kat[k]), "".join(bloky)))
        celkem = sum(pocet_kat.values())
        hlavni = [("mléko a sýry" if (k == "mleko" and zeme == "sk") else w) for k, _, w in KAT if pocet_kat.get(k) and w][:4]
        co = ", ".join(hlavni[:-1]) + (" a " + hlavni[-1] if len(hlavni) > 1 else (hlavni[0] if hlavni else ""))
        stitky = "".join('<a class="filtr" href="#%s">%s · %s</a>' % (k, esc(j), cislo(pocet_kat[k])) for k, j, _ in KAT if pocet_kat.get(k))
        zeme_txt = "Slovensko" if zeme == "sk" else "Česko"
        telo = """
<main>
  <section class="hero hero-uzsi">
    <div class="obal uzky">
      <p class="nadtitul"><a href="/sourcing.html">Sourcing mapa</a> · <a href="/sourcing/kraje.html">kraje</a> · {zeme}</p>
      <h1 class="nadpis-str">{nazev}</h1>
      <p class="tvrzeni-pod">{celkem} {slovo} {v_kraji}, kde se dá koupit {co} přímo od chovatele.</p>
    </div>
  </section>
  <section class="pas">
    <div class="obal uzky">
      <div class="filtry kraj-filtry">{stitky}</div>
      {sekce}
      <p class="drobne kraj-pata">Údaje z registru SVS ({svs}), ze seznamů ŠVPS SR ({svps}), z OpenStreetMap ({osm}, © přispěvatelé OpenStreetMap, licence ODbL) a od lidí. Soukromé chovatele ukazuju jen jako počet u obce. Údaje se mění, před cestou si u prodejce ověř, že pořád prodává. <a href="/jak-mapa-funguje.html">Jak mapa funguje, oprava a odstranění údajů</a></p>
      <div class="tlacitka" style="justify-content:center;margin-top:24px"><a class="cta" href="/sourcing.html">Otevřít celou mapu</a><a class="cta-druhy" href="{skool}">Vstoupit do Akademie</a></div>
    </div>
  </section>
</main>
""".format(nazev=esc(nazev), celkem=cislo(celkem), slovo=slovo_mist(celkem), v_kraji=esc(v_kraji), co=esc(co),
           stitky=stitky, sekce="".join(sekce), zeme=zeme_txt, skool=SKOOL,
           svs=esc(d.get("aktualizace", "")), svps=esc(d.get("aktualizace_sk", "")), osm=esc(o.get("stazeno", "")))
        NOM = {"mleko": "syrové mléko", "maso": "maso", "zverina": "zvěřina", "med": "med", "vejce": "vejce", "ryby": "ryby", "obchod": "farmářské obchody"}
        tri = [("mléko a sýry" if (k == "mleko" and zeme == "sk") else NOM[k]) for k, _, w in KAT if pocet_kat.get(k) and k in NOM][:3]
        co3 = ", ".join(tri[:-1]) + (" a " + tri[-1] if len(tri) > 1 else (tri[0] if tri else "jídlo od chovatele"))
        titulek = "%s %s · Sourcing mapa" % (co3[0].upper() + co3[1:], v_kraji)
        popis = "%s %s %s, kde koupit %s přímo od chovatele. Zdarma, z úředních registrů a od lidí." % (cislo(celkem), slovo_mist(celkem), v_kraji, co)
        cesta = "sourcing/kraj/%s.html" % s
        stranka = HLAVA.format(titulek=esc(titulek), popis=esc(popis), kanon=cesta, ogobr="mapa/hero.jpg", skool=SKOOL) + telo + PATA.format(skool=SKOOL)
        open(cesta, "w", encoding="utf-8").write(stranka)
        souhrn.append((nazev, zeme, cesta, celkem))

    # rozcestník
    def seznam_zeme(z):
        return "".join('<li><a href="/%s">%s</a> <span class="kraj-pocet">%s</span></li>' % (c, esc(n), cislo(p)) for n, ze, c, p in souhrn if ze == z)
    telo = """
<main>
  <section class="hero hero-uzsi">
    <div class="obal uzky">
      <p class="nadtitul"><a href="/sourcing.html">Sourcing mapa</a></p>
      <h1 class="nadpis-str">Jídlo od chovatele po krajích</h1>
      <p class="tvrzeni-pod">Syrové mléko, maso, zvěřina, med a vejce přímo od chovatele v každém kraji Česka a Slovenska.</p>
    </div>
  </section>
  <section class="pas">
    <div class="obal uzky kraj-rozcestnik">
      <div><h2>Česko</h2><ul>{cz}</ul></div>
      <div><h2>Slovensko</h2><ul>{sk}</ul></div>
    </div>
  </section>
</main>
""".format(cz=seznam_zeme("cz"), sk=seznam_zeme("sk"))
    stranka = HLAVA.format(titulek="Sourcing mapa po krajích · Život vysvětlen",
                           popis="Kde koupit syrové mléko, maso, zvěřinu, med a vejce přímo od chovatele, kraj po kraji v Česku a na Slovensku.",
                           kanon="sourcing/kraje.html", ogobr="mapa/hero.jpg", skool=SKOOL) + telo + PATA.format(skool=SKOOL)
    open("sourcing/kraje.html", "w", encoding="utf-8").write(stranka)

    # sitemap: blok mezi značkami se přepisuje při každém běhu
    sm = open("sitemap.xml", encoding="utf-8").read()
    sm = re.sub(r"\n?  <!-- kraje -->.*?<!-- /kraje -->", "", sm, flags=re.S)
    blok = "\n  <!-- kraje -->" + "".join("\n  <url><loc>%s/%s</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>" % (WEB, c)
                                         for c in ["sourcing/kraje.html"] + [c for _, _, c, _ in souhrn]) + "\n  <!-- /kraje -->"
    sm = sm.replace("</urlset>", blok + "\n</urlset>", 1)
    open("sitemap.xml", "w", encoding="utf-8").write(sm)
    return souhrn
