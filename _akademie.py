#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Akademie na webu: data se berou PŘÍMO ze zdrojů Akademie (~/Work/skool/export-do-skoolu),
takže každá změna v Akademii se při dalším `python3 _postav.py` promítne i na web.

- moduly, obrazy a věty „proč“  ... SINE v _mapa-prestav.py (stejné jako mapa Akademie)
- submoduly a jejich popisy     ... mapa/_data.json
- názvy lekcí                   ... _mapa-m1.json až _mapa-m6.json (pořadí stránek ve Skoolu)
- počty lekcí a časy čtení      ... soubory v telo/ (stejný výpočet jako statistiky() mapy)

Vytváří: blok „Jak je to postavené“ na hlavní stránce a stránku akademie.html."""
import glob, importlib.util, json, os, re, html

ZDROJ = os.path.expanduser("~/Work/skool/export-do-skoolu")


def esc(t):
    return html.escape(t, quote=False)


def _sine():
    spec = importlib.util.spec_from_file_location("mapa_prestav", os.path.join(ZDROJ, "_mapa-prestav.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.SINE


def _statistiky():
    st = {}
    telo = os.path.join(ZDROJ, "telo")
    for fn in os.listdir(telo):
        if not fn.endswith(".md") or fn.startswith("M"):
            continue
        klic = fn.split("__")[0]
        m = re.match(r"^(\d+)\.", klic)
        if not m:
            continue
        mod = int(m.group(1))
        slova = len(open(os.path.join(telo, fn), encoding="utf-8").read().split())
        d = st.setdefault(mod, {"lekci": 0, "slov": 0, "klice": []})
        d["lekci"] += 1
        d["slov"] += slova
        d["klice"].append(klic)
    for d in st.values():
        minut = round(d["slov"] / 180)
        d["cas"] = ("%d h %d min" % (minut // 60, minut % 60)) if minut >= 60 else ("%d min" % minut)
    return st


def lekci_slovo(n):
    if n == 1:
        return "1 lekce"
    if 2 <= n <= 4:
        return "%d lekce" % n
    return "%d lekcí" % n


def submoduly_slovo(n):
    if n == 1:
        return "1 submodul"
    if 2 <= n <= 4:
        return "%d submoduly" % n
    return "%d submodulů" % n


def data():
    """Seznam modulů 0 až 6 se vším, co web potřebuje."""
    sine = _sine()
    st = _statistiky()
    mapa = json.load(open(os.path.join(ZDROJ, "mapa", "_data.json"), encoding="utf-8"))
    moduly = []
    for s in sine:
        i = s["i"]
        sub = []
        if i > 0:
            stranky = json.load(open(os.path.join(ZDROJ, "_mapa-m%d.json" % i), encoding="utf-8"))
            tituly = [t for _, t, _ in stranky if not re.match(r"^\d+(\.\d+)*b ·", t)]
            for sm in mapa.get("m%d" % i, []):
                klic = sm["klic"]
                je_cislo = bool(re.match(r"^\d+\.\d+$", klic))
                lekce = []
                if je_cislo:
                    lekce = [t for t in tituly if re.match(r"^%s\.\d+ ·" % re.escape(klic), t)]
                sub.append(dict(klic=klic, nazev=sm["nazev"], popis=sm["popis"], lekce=lekce, protokol=not je_cislo))
        info = st.get(i, {"lekci": 0, "cas": ""})
        cislovane = [x for x in sub if not x["protokol"]]
        moduly.append(dict(i=i, jmeno=s["jmeno"], proc=s["proc"], img="/" + s["img"], w=s["w"], h=s["h"],
                           alt=s["alt"], cap=s["cap"], sub=sub, pocet_sub=len(cislovane),
                           lekci=info["lekci"], cas=info["cas"]))
    return moduly


def cisla(moduly):
    ms = [m for m in moduly if m["i"] > 0]
    lekci = sum(m["lekci"] for m in moduly)   # i se vstupním Modulem 0, stejně jako statistiky() mapy (102)
    sub = sum(m["pocet_sub"] for m in ms)
    hodin = round(sum(_hodiny(m["cas"]) for m in moduly))   # i s Modulem 0, stejně jako statistiky() mapy (17. 10.: 22 h)
    return dict(moduly=len(ms), submoduly=sub, lekce=lekci, hodiny=hodin)


def cislo_slovy(n, rod="m"):
    """1 až 999 slovy, v 1. pádě (rod: m = submodul, f = lekce): 106 -> „sto šest“, 28 -> „dvacet osm“"""
    jed = {"m": ["", "jeden", "dva"], "f": ["", "jedna", "dvě"]}[rod] + ["tři", "čtyři", "pět", "šest", "sedm", "osm", "devět"]
    nact = ["deset", "jedenáct", "dvanáct", "třináct", "čtrnáct", "patnáct", "šestnáct", "sedmnáct", "osmnáct", "devatenáct"]
    des = ["", "", "dvacet", "třicet", "čtyřicet", "padesát", "šedesát", "sedmdesát", "osmdesát", "devadesát"]
    sta = ["", "sto", "dvě stě", "tři sta", "čtyři sta", "pět set", "šest set", "sedm set", "osm set", "devět set"]
    s, zb = divmod(n, 100)
    kusy = [sta[s]] if s else []
    if 10 <= zb < 20:
        kusy.append(nact[zb - 10])
    else:
        d, j = divmod(zb, 10)
        if d:
            kusy.append(des[d])
        if j:
            kusy.append(jed[j])
    return " ".join(kusy)


def _tvar(n, jedna, dve, pet):
    """tvar podstatného jména podle posledního členu čísla: sto jedna lekce, sto dvě lekce, sto šest lekcí"""
    z = n % 100
    return jedna if z == 1 else (dve if 2 <= z <= 4 else pet)


def pocty():
    """Jediný zdroj počtů pro celý web (17. 10. 2026, Matyáš: „aby kdykoliv jakýkoliv build byl relevantní“).
    Počítá se ze zdrojů Akademie stejně jako statistiky() mapy, nikde na webu se čísla nepíšou ručně."""
    c = cisla(data())
    slov = sum(len(open(f, encoding="utf-8").read().split()) for f in glob.glob(os.path.join(ZDROJ, "telo", "*.md")))
    zaokr = slov // 1000 * 1000
    c.update(
        slov=slov,
        slov_cz="{:,}".format(zaokr).replace(",", " "),
        slov_en="{:,}".format(zaokr),
        veta=("Šest modulů, %s %s, %s %s" % (cislo_slovy(c["submoduly"], "m"),
                                             _tvar(c["submoduly"], "submodul", "submoduly", "submodulů"),
                                             cislo_slovy(c["lekce"], "f"),
                                             _tvar(c["lekce"], "lekce", "lekce", "lekcí"))),
    )
    return c


def dosad_pocty(text, c=None):
    """Nahradí v textu značky §LEKCI§, §SUBMODULU§, §HODIN§, §SLOV§ a §POCTY_VETA§ skutečnými čísly."""
    c = c or pocty()
    for znacka, hodnota in (("§LEKCI§", str(c["lekce"])), ("§SUBMODULU§", str(c["submoduly"])),
                            ("§HODIN§", str(c["hodiny"])), ("§SLOV§", c["slov_cz"]), ("§POCTY_VETA§", c["veta"])):
        text = text.replace(znacka, hodnota)
    return text


def _hodiny(cas):
    h = re.search(r"(\d+) h", cas)
    mi = re.search(r"(\d+) min", cas)
    return (int(h.group(1)) if h else 0) + (int(mi.group(1)) if mi else 0) / 60


def _ukazka_lekce():
    """první odstavce lekce 1.1 · Co je nemoc (jeho text beze změny)"""
    p = os.path.join(ZDROJ, "telo", "1.1__1-1-co-je-nemoc.md")
    bloky = [b.strip() for b in open(p, encoding="utf-8").read().split("\n\n") if b.strip()]
    ven = []
    for b in bloky[:6]:
        if b.startswith("## "):
            ven.append("<h4>%s</h4>" % esc(b[3:]))
        else:
            t = esc(b)
            t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
            ven.append("<p>%s</p>" % t)
    return "".join(ven)


# ------------------------------------------------------------ blok na hlavní stránce
def pas_akademie(moduly, varianta="svetla"):
    karty = []
    for m in moduly:
        if m["i"] == 0:
            continue
        subs = "".join('<li><b>%s</b><span>%s</span></li>' % (esc(s["nazev"]), esc(s["popis"]))
                       for s in m["sub"] if not s["protokol"])
        karty.append(
            '<details class="modul-karta">'
            '<summary>'
            '<span class="modul-obr"><img src="%s" alt="%s" loading="lazy" width="%d" height="%d"></span>'
            '<span class="modul-telo">'
            '<span class="modul-cislo">Modul %d</span>'
            '<span class="modul-jmeno">%s</span>'
            '<span class="modul-proc">%s</span>'
            '<span class="modul-meta">%s · %s · %s</span>'
            '<span class="modul-vic" aria-hidden="true">Co je uvnitř</span>'
            '</span></summary>'
            '<ul class="modul-sub">%s</ul>'
            '</details>'
            % (m["img"], esc(m["alt"]), m["w"], m["h"], m["i"], esc(m["jmeno"]), esc(m["proc"]),
               submoduly_slovo(m["pocet_sub"]), lekci_slovo(m["lekci"]), esc(m["cas"]), subs))
    return """
  <section class="pas akademie-pas akademie-%s" id="akademie">
    <div class="obal">
      <p class="nadtitul">Akademie</p>
      <h2>Jak je to postavené</h2>
      <p class="text-stred">Šest modulů. Každý má dva až pět submodulů. Každý submodul je samostatný deep text.</p>
      <div class="moduly-mriz">%s</div>
      <p class="text-stred akademie-pozn">Když chceš číst na přeskočku, klidně. Jenom Modul 1 nepřeskakuj.</p>
      <div class="stred"><a class="cta" href="/akademie.html">Prohlédnout Akademii zevnitř</a></div>
    </div>
  </section>
""" % (varianta, "".join(karty))


# ------------------------------------------------------------ stránka akademie.html
CO_DOSTANES = [
    # (název, jeho věta, obrázek do zastřeného náhledu)
    ("Vstupní diagnostika", "Deset minut. Vyjde ti tempo, první modul a šest čísel.", "/mapa/nahledy/0.2--mapa-vysledek-zacinas-modulem-1.jpg"),
    ("První týden den po dni", "Nemusíš nic kupovat. Ani korunu. Nula korun, dvacet minut denně.", "/mapa/nahledy/0.1--smycka-navyku-cesky.jpg"),
    ("{lekce} lekcí", "Každý submodul je samostatný deep text.", "/mapa/nahledy/1.4--sestifazova-tabulka-reckeweg.jpg"),
    ("PLAYBOOK", "Stránka, kterou si otevřeš s horečkou v posteli.", "/mapa/nahledy/1.3.2--lymfaticka-drenaz-hlavy.jpg"),
    ("Čtyři protokoly", "Prostředí, výživa, trénink a mysl. Každý poskládaný do jednoho týdne.", "/mapa/nahledy/3.1--uvb-na-50-rovnobezce.jpg"),
    ("Komunita a mapa zdrojů", "Z těch okresů postupně vznikne mapa českých zdrojů, kterou nikdo jiný nemá.", "/mapa/nahledy/4.1--syrove-zivocisne-tradice-sveta.jpg"),
]

NENI = [
    ("Není to řešení akutní situace.", "Na akutní stav je tady PLAYBOOK."),
    ("Není to dieta na třicet dní.", "Nedostaneš jídelníček na míru a nedostaneš čísla, která máš plnit. Dostaneš principy a k nim konkrétní kroky."),
    ("Není to seznam zákazů.", "Seznam si musíš pamatovat. Mechanismus si pamatovat nemusíš."),
]


# „Co budeš umět po modulu" (návrh 9. 10. 2026, odvozené z popisů submodulů a protokolů, ke schválení)
VYSLEDKY = {
    0: "Víš, kterým modulem začít a jakým tempem. Vyjde ti to ze vstupní diagnostiky.",
    1: "Umíš si vysvětlit, odkud se nemoc bere, co dělá imunitní systém a co znamená příznak. A víš, co dělat, když onemocníš.",
    2: "Víš, čím jsou viry, bakterie a paraziti doopravdy, a zprávy o epidemiích čteš jinak.",
    3: "Máš nastavené světlo, spánek, vodu, pohyb a dech na celý den. Většina z toho je zadarmo.",
    4: "Víš, co jíst a proč, kde v Česku sehnat mléko, maso a vejce a co z nich uvařit.",
    5: "Máš trénink podle toho, kolik dní v týdnu doopravdy máš, a víš, jak podpořit hormony a regeneraci bez násilí.",
    6: "Rozumíš tomu, odkud se bere to, co prožíváš, a máš praktický týden kroků pro mysl.",
}


# karty bez obrázku z lekcí (Matyáš 11. 10.: „chci aby každá věc měla svou fotku“): volná díla z Wikimedia Commons
# (public domain / CC0, stažené 11. 10. 2026, zdroje v _nahledy/v12/karty-zdroje.json), jeho fotka a výřez jeho mapy
OBRAZKY_KARET = {
    "0.0": [("/pribeh/0.0__09-porovnani-dvojice.jpg", "Matyáš před a po")],
    "1.1": [("/mapa/karty/1-1.jpg", "Luke Fildes, Lékař, 1891")],
    "1.2": [("/mapa/karty/1-2.jpg", "Albert Edelfelt, Louis Pasteur, 1885")],
    "PLAYBOOK": [("/mapa/karty/playbook.jpg", "Jan Steen, Návštěva lékaře")],
    "2.1": [("/mapa/karty/2-1.jpg", "Robert Hooke, Micrographia, 1665")],
    "3.2": [("/mapa/karty/3-2.jpg", "Gustave Courbet, Pramen řeky Loue, 1864")],
    "Protokol PROSTŘEDÍ": [("/mapa/karty/prostredi.jpg", "Caspar David Friedrich, Žena před vycházejícím sluncem, 1818")],
    "Protokol VÝŽIVY": [("/mapa/karty/vyziva-sourcing.jpg", "Sourcing mapa")],
    "4.9": [("/mapa/karty/4-9.jpg", "Pieter Claesz, Zátiší")],
    "5.1": [("/mapa/karty/5-1.jpg", "Thomas Eakins, Max Schmitt na skifu, 1871")],
    "Protokol TRÉNINKU": [("/mapa/karty/trenink.jpg", "Leonardo da Vinci, Vitruviánský muž")],
    "6.4": [("/mapa/karty/6-4.jpg", "Caspar David Friedrich, Poutník nad mořem mlhy, 1818")],
    "6.5": [("/mapa/karty/6-5.jpg", "Albrecht Dürer, Melancholie I, 1514")],
}


def _obrazky_submodulu():
    """obrázky z lekcí (mapa/nahledy, jako ve staré mapě) podle submodulu: '1.3.2--x.jpg' patří k '1.3'"""
    import glob
    ven = {}
    for f in sorted(glob.glob("mapa/nahledy/*.jpg")):
        jmeno = os.path.basename(f)
        klic = jmeno.split("--")[0]
        sub = ".".join(klic.split(".")[:2])
        popis = jmeno.split("--", 1)[1].rsplit(".", 1)[0].replace("-", " ")
        ven.setdefault(sub, []).append(("/" + f, popis))
    return ven


def _zobraz_lekce(n):
    if n == 1:
        return "Zobrazit lekci"
    if n < 5:
        return "Zobrazit všechny %d lekce" % n
    return "Zobrazit všech %d lekcí" % n


def _sub_karta(s, obr, siroka=False):
    if obr:
        vrch = '<div class="sub-obr n%d">%s</div>' % (min(len(obr), 3), "".join(
            '<img src="%s" alt="%s" loading="lazy">' % (f, esc(pop)) for f, pop in obr[:3]))
    elif s["protokol"]:
        vrch = '<div class="sub-obr znak protokol"><span>Protokol</span></div>'
    else:
        vrch = '<div class="sub-obr znak"><span>%s</span></div>' % esc(s["klic"])
    nazev = re.sub(r"^%s\s*·\s*" % re.escape(s["klic"]), "", s["nazev"])
    nazev = nazev[:1].upper() + nazev[1:]
    nadpis = esc(nazev) if s["protokol"] else '<span>%s ·</span> %s' % (esc(s["klic"]), esc(nazev))
    lekce = ""
    if s["lekce"]:
        lekce = '<details class="sub-lekce"><summary>%s</summary><ol>%s</ol></details>' % (
            _zobraz_lekce(len(s["lekce"])), "".join("<li>%s</li>" % esc(t) for t in s["lekce"]))
    return '<article class="sub-karta%s%s">%s<div class="sub-telo"><h4>%s</h4><p>%s</p>%s</div></article>' % (
        " protokol" if s["protokol"] else "", " siroka" if siroka else "", vrch, nadpis, esc(s["popis"]), lekce)


def postav_stranku(HLAVA, PATA, SKOOL, recenze=""):
    moduly = data()
    c = cisla(moduly)
    dlazdice = "".join(
        '<article class="dlazdice"><div class="dlazdice-nahled"><img src="%s" alt="" loading="lazy"><span class="zamek">V Akademii</span></div>'
        '<h3>%s</h3><p>%s</p></article>' % (img, esc(n.format(**c)), esc(t)) for n, t, img in CO_DOSTANES)

    sine = []
    obrazky = _obrazky_submodulu()
    for m in moduly:
        if m["i"] == 0:
            subs = [dict(klic="0.0", nazev="Můj příběh", popis="Kdo tě tím provede a proč.", lekce=[], protokol=False),
                    dict(klic="0.1", nazev="Začni zde", popis="Jak je to postavené, pět pravidel a první týden den po dni.", lekce=[], protokol=False),
                    dict(klic="0.2", nazev="Vstupní diagnostika", popis="Ze které ti vyjde, kterým modulem začínáš a jakým tempem.", lekce=[], protokol=False)]
        else:
            subs = m["sub"]
        # souměrnost: protokol přes celou šířku, a když v úseku zbude jedna karta navíc, roztáhne se taky
        siroke, usek = set(), []
        for k, s in enumerate(subs + [None]):
            if s is None or s["protokol"]:
                if len(usek) % 2:
                    siroke.add(usek[-1])
                usek = []
                if s is not None:
                    siroke.add(k)
            else:
                usek.append(k)
        karty = "".join(_sub_karta(s, obrazky.get(s["klic"]) or OBRAZKY_KARET.get(s["klic"], []), k in siroke) for k, s in enumerate(subs))
        meta = "Než začneš" if m["i"] == 0 else "%s · %s · %s" % (submoduly_slovo(m["pocet_sub"]), lekci_slovo(m["lekci"]), m["cas"])
        sine.append(
            '<section class="sin sin4" id="modul-%d">'
            '<div class="sin-hlava">'
            '<figure class="sin-obr"><img src="%s" alt="%s" loading="lazy" width="%d" height="%d"><figcaption>%s</figcaption></figure>'
            '<div class="sin-text"><p class="modul-cislo">Modul %d</p><h3>%s</h3><p class="sin-proc">%s</p>%s<p class="modul-meta">%s</p></div>'
            '</div>'
            '<div class="sub-mriz">%s</div>'
            '</section>'
            % (m["i"], m["img"], esc(m["alt"]), m["w"], m["h"], esc(m["cap"]), m["i"], esc(m["jmeno"]),
               esc(m["proc"]), ('<p class="modul-vysledek"><b>Po modulu:</b> %s</p>' % esc(VYSLEDKY[m["i"]])) if m["i"] in VYSLEDKY else "",
               esc(meta), karty))

    neni = "".join('<li><b>%s</b> %s</li>' % (esc(a), esc(b)) for a, b in NENI)

    telo = """
<main>
  <section class="ak-uvod">
    <div class="obal ak-uvod-mriz">
      <div>
        <p class="nadtitul">Akademie</p>
        <h1 class="ak-nadpis">Život vysvětlen</h1>
        <p class="ak-veta">Celá Akademie stojí na tom, že člověk umí jít k prameni místo k něčímu shrnutí.</p>
        <p class="cisla ak-cisla"><span><b>{moduly}</b>modulů</span><span><b>{submoduly}</b>submodulů</span><span><b>{lekce}</b>lekcí</span><span><b>{hodiny}</b>hodin čtení</span></p>
        <div class="tlacitka"><a class="cta" href="{skool}">Vstoupit do Akademie</a><a class="cta-druhy" href="#moduly">Projít moduly</a></div>
      </div>
      <figure class="ak-uvod-obr"><img src="/mapa/hero.jpg" alt="Mapa Akademie" width="1600" height="1048"></figure>
    </div>
  </section>

  <section class="pas">
    <div class="obal">
      <p class="nadtitul">Co dostaneš</p>
      <h2>Všechno, co je uvnitř</h2>
      <div class="dlazdice-mriz">{dlazdice}</div>
    </div>
  </section>

  <section class="pas sine-pas" id="moduly">
    <div class="obal">
      <p class="nadtitul">Moduly</p>
      <h2>Sedm síní, jedna po druhé</h2>
      <p class="text-stred">Protože každý další modul stojí na tom předchozím.</p>
      {sine}
    </div>
  </section>

  <section class="pas">
    <div class="obal uzky">
      <p class="nadtitul">Lekce zdarma</p>
      <h2>1.1 · Co je nemoc</h2>
      <div class="ukazka"><div class="ukazka-text">{ukazka}</div><div class="ukazka-zamek"><p>Celou lekci si přečti zdarma</p><div class="tlacitka" style="justify-content:center"><a class="cta" href="/lekce-zdarma.html">Přečíst celou lekci</a><a class="cta-druhy" href="{skool}">Vstoupit do Akademie</a></div></div></div>
      <p class="text-stred" style="margin-top:22px">Zdarma jsou i <a href="/lekce-zdarma-vzhled.html">Vzhled jako viditelný výraz vnitřního terénu</a> (z lekce 5.4) a <a href="/lekce-zdarma-hormony.html">5.2 · Hormony</a>.</p>
    </div>
  </section>

{recenze}
  <section class="pas">
    <div class="obal uzky">
      <p class="nadtitul">Ať je jasno</p>
      <h2>Co tahle Akademie není</h2>
      <ul class="neni ak-neni">{neni}</ul>
    </div>
  </section>

  <section class="pas zaver-pas">
    <div class="obal uzky stred">
      <p class="vyzva">Seznam si musíš pamatovat. Mechanismus si pamatovat nemusíš.<strong>Ten pochopíš jednou a od té chvíle si každou další otázku zodpovíš sám.</strong></p>
      <a class="cta" href="{skool}">Vstoupit do Akademie</a>
      <p class="drobne"><a href="/jedna-na-jedna.html">Chceš to aplikované na sebe? Osobní vedení 1:1</a></p>
    </div>
  </section>
</main>
""".format(skool=SKOOL, dlazdice=dlazdice, sine="".join(sine), ukazka=_ukazka_lekce(), neni=neni, recenze=recenze, **c)

    stranka = HLAVA.format(titulek="Akademie · Život vysvětlen",
                           popis="Šest modulů, %d submodulů, %d lekcí. Co je v Akademii Život vysvětlen, modul po modulu." % (c["submoduly"], c["lekce"]),
                           kanon="akademie.html", ogobr="mapa/hero.jpg", skool=SKOOL) + telo + PATA.format(skool=SKOOL)
    open("akademie.html", "w", encoding="utf-8").write(stranka)
    return c


if __name__ == "__main__":
    for m in data():
        print(m["i"], m["jmeno"], m["pocet_sub"], m["lekci"], m["cas"], [ (s["klic"], len(s["lekce"])) for s in m["sub"]])
    print(cisla(data()))


# ------------------------------------------------------------ lekce zdarma (9. 10. 2026): celá 1.1 jeho slovy
# lekce zdarma na webu (9. 10. 1.1; 11. 10. Matyáš: „relevantní lekce zdarma … jak health a vzhled jsou interconnected“)
# od/do = výřez části submodulu podle nadpisu; text se nemění, jen se nadpis části stane nadpisem stránky
LEKCE_ZDARMA = [
    dict(soubor="lekce-zdarma.html", zdroj="1.1__1-1-co-je-nemoc.md", klic="1.1", nazev="Co je nemoc",
         popis="Celá první lekce Akademie Život vysvětlen. Co nemoc vlastně je a odkud se bere.", od=None, do=None, cast=None),
    dict(soubor="lekce-zdarma-vzhled.html", zdroj="5.4__5-4-dlouhovekost.md", klic="5.4",
         nazev="Vzhled jako viditelný výraz vnitřního terénu",
         popis="Proč tvář a postava nesou informaci o zdraví a co obličej staví. Část lekce z Akademie Život vysvětlen, zdarma.",
         od="# ČÁST 2 · Vzhled", do="# 📏 Co délku života", cast="Část submodulu 5.4 · Dlouhověkost"),
    dict(soubor="lekce-zdarma-hormony.html", zdroj="5.2__5-2-hormony.md", klic="5.2", nazev="Hormony",
         popis="Co doopravdy určuje testosteron, štítnou žlázu a cyklus a co hormony rozbíjí zvenčí. Celá lekce z Akademie, zdarma.",
         od=None, do=None, cast=None),
]


def _lekce_text(l):
    t = open(os.path.join(ZDROJ, "telo", l["zdroj"]), encoding="utf-8").read()
    if l["od"]:
        i = t.index(l["od"])
        j = t.index(l["do"], i) if l["do"] else len(t)
        t = t[i:j]
        t = t.split("\n", 1)[1] if t.startswith("# ") else t      # nadpis části → nadpis stránky
    t = re.sub(r"^<!--.*?-->\s*", "", t, flags=re.S)
    t = re.sub(r"\n---\s*$", "", t.strip())
    return t


def lekce_minut(l):
    return max(1, round(len(re.findall(r"\w+", _lekce_text(l))) / 230))


def _obrazek_lekce(jmeno):
    """obrázek z exportu Akademie → /lekce/obr/<jméno>.jpg (zmenšený, průhlednost na papír)"""
    from PIL import Image
    zdroj = os.path.join(ZDROJ, "obrazky", jmeno)
    cil_rel = "lekce/obr/%s.jpg" % os.path.splitext(jmeno)[0]
    if not os.path.exists(zdroj):
        return None
    if not os.path.exists(cil_rel) or os.path.getmtime(cil_rel) < os.path.getmtime(zdroj):
        os.makedirs("lekce/obr", exist_ok=True)
        im = Image.open(zdroj)
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA"); pod = Image.new("RGB", im.size, (253, 251, 246)); pod.paste(im, (0, 0), im); im = pod
        else:
            im = im.convert("RGB")
        im.thumbnail((1400, 1400), Image.LANCZOS)
        im.save(cil_rel, quality=84, optimize=True)
    return "/" + cil_rel


def postav_lekci_zdarma(HLAVA, PATA, SKOOL):
    import markdown
    moduly = data(); c = cisla(moduly)
    vystup = []
    for l in LEKCE_ZDARMA:
        t = _lekce_text(l)
        def obr(m):
            src = _obrazek_lekce(m.group(1).strip())
            return '\n\n<figure class="lekce-obr"><img src="%s" alt="" loading="lazy"></figure>\n\n' % src if src else ""
        t = re.sub(r"\[\[\s*SEM OBRÁZEK:\s*(.+?)\s*\]\]", obr, t)
        minut = lekce_minut(l)
        telo_html = markdown.markdown(t, extensions=["extra", "sane_lists"])
        dalsi = ""
        if l["klic"] == "1.1":
            for m in moduly:
                for sm in m["sub"]:
                    if sm["klic"] == "1.1" and sm["lekce"]:
                        dalsi = sm["lekce"][0]
        jine = "".join('<li><a href="/%s">%s · %s</a></li>' % (x["soubor"], esc(x["klic"]), esc(x["nazev"]))
                       for x in LEKCE_ZDARMA if x is not l)
        pod = ("%s, tak jak ji mají studenti. Čtení asi na %d minut." % (l["cast"], minut)) if l["cast"] else \
              ("Celá lekce z Akademie, tak jak ji mají studenti. Čtení asi na %d minut." % minut)
        stranka = HLAVA.format(titulek="Lekce zdarma: %s %s · Život vysvětlen" % (l["klic"], l["nazev"]), popis=l["popis"],
                               kanon=l["soubor"], ogobr="mapa/hero.jpg", skool=SKOOL) + """
<main>
  <section class="hero hero-uzsi">
    <div class="obal uzky">
      <p class="nadtitul">Lekce zdarma · Akademie</p>
      <h1 class="nadpis-str">{klic} · {nazev}</h1>
      <p class="tvrzeni-pod">{pod}</p>
    </div>
  </section>
  <section class="pas lekce-pas">
    <div class="obal uzky">
      <article class="text lekce-text">{telo}</article>
    </div>
  </section>
  <section class="pas zaver-pas">
    <div class="obal uzky stred">
      <div class="ozdoba" aria-hidden="true">◆</div>
      <h2>{konec}</h2>
      <p class="text-stred">{dalsi_veta}</p>
      <div class="tlacitka" style="justify-content:center"><a class="cta" href="{skool}">Vstoupit do Akademie</a><a class="cta-druhy" href="/akademie.html">Prohlédnout celou Akademii</a></div>
      <p class="nadtitul" style="margin-top:34px">Další lekce zdarma</p>
      <ul class="lekce-dalsi">{jine}</ul>
    </div>
  </section>
</main>
""".format(klic=esc(l["klic"]), nazev=esc(l["nazev"]), pod=esc(pod), telo=telo_html, skool=SKOOL, jine=jine,
           konec=("Tohle byla část jedné ze %d lekcí" % c["lekce"]) if l["cast"] else ("Tohle byla jedna ze %d lekcí" % c["lekce"]),
           dalsi_veta=("Další je %s." % esc(dalsi)) if dalsi else "Další lekce jsou v Akademii.") + PATA.format(skool=SKOOL)
        open(l["soubor"], "w", encoding="utf-8").write(stranka)
        vystup.append("%s %d min" % (l["soubor"], minut))
    return ", ".join(vystup)
