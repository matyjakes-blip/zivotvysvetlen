#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Akademie na webu: data se berou PŘÍMO ze zdrojů Akademie (~/Work/skool/export-do-skoolu),
takže každá změna v Akademii se při dalším `python3 _postav.py` promítne i na web.

- moduly, obrazy a věty „proč“  ... SINE v _mapa-prestav.py (stejné jako mapa Akademie)
- submoduly a jejich popisy     ... mapa/_data.json
- názvy lekcí                   ... _mapa-m1.json až _mapa-m6.json (pořadí stránek ve Skoolu)
- počty lekcí a časy čtení      ... soubory v telo/ (stejný výpočet jako statistiky() mapy)

Vytváří: blok „Jak je to postavené“ na hlavní stránce a stránku akademie.html."""
import importlib.util, json, os, re, html

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
    hodin = round(sum(_hodiny(m["cas"]) for m in ms))
    return dict(moduly=len(ms), submoduly=sub, lekce=lekci, hodiny=hodin)


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


def postav_stranku(HLAVA, PATA, SKOOL, recenze=""):
    moduly = data()
    c = cisla(moduly)
    dlazdice = "".join(
        '<article class="dlazdice"><div class="dlazdice-nahled"><img src="%s" alt="" loading="lazy"><span class="zamek">V Akademii</span></div>'
        '<h3>%s</h3><p>%s</p></article>' % (img, esc(n.format(**c)), esc(t)) for n, t, img in CO_DOSTANES)

    sine = []
    for m in moduly:
        polozky = []
        for s in m["sub"]:
            if s["protokol"]:
                polozky.append('<li class="sub protokol"><div class="sub-hlava"><b>%s</b><span>%s</span></div></li>'
                               % (esc(s["nazev"]), esc(s["popis"])))
                continue
            ukaz = s["lekce"][:3]
            zbytek = len(s["lekce"]) - len(ukaz)
            lek = "".join("<li>%s</li>" % esc(t) for t in ukaz)
            if zbytek > 0:
                lek += '<li class="dalsi">+ %s</li>' % (
                    "ještě 1 lekce" if zbytek == 1 else ("další %d lekce" % zbytek if zbytek < 5 else "dalších %d lekcí" % zbytek))
            lek_html = '<ol class="lekce">%s</ol>' % lek if lek else ""
            polozky.append('<li class="sub"><div class="sub-hlava"><b>%s</b><span>%s</span></div>%s</li>'
                           % (esc(s["nazev"]), esc(s["popis"]), lek_html))
        meta = "Než začneš" if m["i"] == 0 else "%s · %s · %s" % (submoduly_slovo(m["pocet_sub"]), lekci_slovo(m["lekci"]), m["cas"])
        obsah = '<ul class="sine-sub">%s</ul>' % "".join(polozky) if polozky else \
            '<ul class="sine-sub"><li class="sub"><div class="sub-hlava"><b>0.0 · Můj příběh</b><span>Kdo tě tím provede a proč.</span></div></li>' \
            '<li class="sub"><div class="sub-hlava"><b>0.1 · Začni zde</b><span>Jak je to postavené, pět pravidel a první týden den po dni.</span></div></li>' \
            '<li class="sub"><div class="sub-hlava"><b>0.2 · Vstupní diagnostika</b><span>Ze které ti vyjde, kterým modulem začínáš a jakým tempem.</span></div></li></ul>'
        sine.append(
            '<section class="sin" id="modul-%d">'
            '<figure class="sin-obr"><img src="%s" alt="%s" loading="lazy" width="%d" height="%d"><figcaption>%s</figcaption></figure>'
            '<div class="sin-text"><p class="modul-cislo">Modul %d</p><h3>%s</h3><p class="sin-proc">%s</p><p class="modul-meta">%s</p>%s</div>'
            '</section>'
            % (m["i"], m["img"], esc(m["alt"]), m["w"], m["h"], esc(m["cap"]), m["i"], esc(m["jmeno"]),
               esc(m["proc"]), esc(meta), obsah))

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
      <p class="nadtitul">Ukázka</p>
      <h2>1.1 · Co je nemoc</h2>
      <div class="ukazka"><div class="ukazka-text">{ukazka}</div><div class="ukazka-zamek"><p>Pokračování je v Akademii</p><a class="cta" href="{skool}">Vstoupit do Akademie</a></div></div>
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
