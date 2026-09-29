#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Postavi sourcing/data.json z oficialnich registru SVS + doporuceni z Akademie.
Kazde misto se posadi do sve obce (PSC + nazev obce), nic se neposila cizi sluzbe.
Fyzicke osoby se anonymizuji: bez jmena a ulice, jen obec a registracni cislo."""
import csv, json, math, os, re, unicodedata
from collections import defaultdict

Z = "sourcing/zdroje/"
SVS_MLEKO = "https://svs.gov.cz/registrovane-subjekty-svs/prodejci-syroveho-mleka/"
SVS_PP = "https://svs.gov.cz/registrovane-subjekty-svs/zpracovatele-zivocisnych-produktu-registrovani-pro-primy-prodej-v-cr/"

# soubor -> kategorie na mape, popis typu, odkaz na registr
REGISTRY = [
    ("svs-mleko.json", None,       None,                                   SVS_MLEKO),
    ("svs-P13.json",  "mleko",     "Mléčné výrobky z vlastní výroby",       SVS_PP),
    ("svs-P01.json",  "maso",      "Bourárna a porcovna pro přímý prodej",  SVS_PP),
    ("svs-P12.json",  "zverina",   "Zvěřina",                               SVS_PP),
    ("svs-P06.json",  "ryby",      "Zpracování ryb",                        SVS_PP),
    ("svs-P21.json",  "med",       "Med",                                   SVS_PP),
    ("svs-P05.json",  "vejce",     "Třídírna a prodej vajec",               SVS_PP),
]

PRAVNI = re.compile(r"(s\.\s?r\.\s?o|a\.\s?s\.|spol\.|z\.\s?s\.|o\.\s?p\.\s?s|k\.\s?s\.|v\.\s?o\.\s?s|"
                    r"v\.\s?v\.\s?i|družstvo|\bZD\b|\bZOD\b|\bZAS\b|státní podnik|\bs\.p\.|"
                    r"farma|statek|ranč|ranc|rybářství|rybarstvi|myslivec|mysliveck|\bMS\b|honeb|honitb|"
                    r"zemědělsk|zemedelsk|agro|mlékárn|mlekarn|řeznictví|reznictvi|uzenářství|uzenin|jatk|"
                    r"správa|sprava|lesy|obec |město|mesto|národní|narodni|ústav|ustav|škola|skola|"
                    r"automat|prodejn|sýrárn|syrarn|kozí|kravín|dvůr|dvur|mlýn|mlyn|chov|biofarm|ekofarm|"
                    r"včelař|vcelar|rodinná|rodinna|company|group|trade|market|shop|bistro|hotel|pension|penzion)", re.I)


RETEZCE = re.compile(r"(kaufland|\balbert\b|ahold|tesco|globus|\blidl\b|penny|billa|makro|terno|tamda|\bcoop\b|spotřební družstvo|\bnorma\b|hruška, spol|brněnka|\bratio\b|\bflop\b|žabka|interspar|\bspar\b)", re.I)


def bez_diakritiky(s):
    return "".join(c for c in unicodedata.normalize("NFD", s or "") if unicodedata.category(c) != "Mn").lower().strip()


def nacti_obce():
    podle_nazvu = defaultdict(list)
    podle_psc = defaultdict(list)
    with open(Z + "obce.csv", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            o = {"obec": r["Obec"], "lat": float(r["Latitude"]), "lon": float(r["Longitude"]),
                 "psc": r["PSČ"].replace(" ", ""), "okres": r["Okres"], "kraj": r["Kraj"]}
            podle_nazvu[bez_diakritiky(r["Obec"])].append(o)
            podle_psc[o["psc"]].append(o)
    return podle_nazvu, podle_psc


def najdi_obec(adresa, podle_nazvu, podle_psc):
    a = adresa or ""
    if re.search(r"\bpraha\b", bez_diakritiky(a)):
        return podle_nazvu["praha"][0]
    m = re.search(r"\b(\d{3})\s?(\d{2})\s+([^,]+?)\s*$", a) or re.search(r"\b(\d{3})\s?(\d{2})\s+([^,]+)", a)
    kandidati_jmen = []
    psc = None
    if m:
        psc = m.group(1) + m.group(2)
        kandidati_jmen.append(re.sub(r"\s+\d+$", "", m.group(3)).strip())
    casti = [c.strip() for c in a.split(",") if c.strip()]
    for c in casti:
        c2 = re.sub(r"\b\d{3}\s?\d{2}\b", "", c)
        c2 = re.sub(r"\b(č\.\s?p\.|č\.\s?ev\.|čp\.)\s*\d+", "", c2)
        c2 = re.sub(r"\s\d+[a-z]?(/\d+[a-z]?)?$", "", c2).strip()
        c2 = re.sub(r"\s*-\s*.*$", "", c2).strip()
        if c2: kandidati_jmen.append(c2)
    for jm in kandidati_jmen:
        k = podle_nazvu.get(bez_diakritiky(jm))
        if k:
            if len(k) == 1 or not psc: return k[0]
            k.sort(key=lambda o: abs(int(o["psc"] or 0) - int(psc)))
            return k[0]
    if psc and psc in podle_psc:
        return podle_psc[psc][0]
    if psc:
        # nejblizsi PSC ve stejne posted oblasti
        blizke = [o for p, lst in podle_psc.items() if p[:3] == psc[:3] for o in lst]
        if blizke:
            blizke.sort(key=lambda o: abs(int(o["psc"] or 0) - int(psc)))
            return blizke[0]
    return None


def je_fyzicka_osoba(nazev):
    n = (nazev or "").strip()
    n = re.sub(r"\s+[A-Z]{1,4}\s*-\s*\d+\s*$", "", n)          # kod provozovny na konci
    n = re.sub(r"\s*,?\s*(č\.|c\.)?\s*\d+\s*$", "", n).strip()
    if PRAVNI.search(n): return False
    slova = [s for s in re.split(r"[\s,]+", n) if s]
    if 2 <= len(slova) <= 4 and all(s[:1].isupper() for s in slova if s.isalpha()) and not re.search(r"\d", n):
        return True
    return False


def kategorie_mleko(zaznam):
    t = (zaznam.get("cinnost_text") or "").lower()
    if "automat na mléčné" in t: return "mleko", "Automat na mléčné výrobky"
    if "automat" in t: return "mleko", "Mlékomat se syrovým mlékem"
    return "mleko", "Syrové mléko ze dvora"


def tipy():
    """overene tipy od lidi (plni tydenni agent sourcing-tipy z Notionu)"""
    p = "sourcing/tipy.json"
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else []


def doporucene():
    p = "sourcing/doporucene.json"
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else []


if __name__ == "__main__":
    podle_nazvu, podle_psc = nacti_obce()
    obce = {}
    nenalezeno, fyzicke, celkem = [], 0, 0
    videne = set()
    for soubor, kat, typ, registr in REGISTRY:
        data = json.load(open(Z + soubor, encoding="utf-8"))["data"]
        for z in data:
            nazev = (z.get("nazev") or "").strip()
            adresa = (z.get("adresa") or "").strip()
            if kat is not None and RETEZCE.search(nazev):
                continue                      # supermarketove pulty na primal mapu nepatri
            klic = (nazev.lower(), adresa.lower(), kat or "mleko")
            if klic in videne: continue
            videne.add(klic)
            if kat is None:
                k, t = kategorie_mleko(z)
            else:
                k, t = kat, typ
            o = najdi_obec(adresa, podle_nazvu, podle_psc)
            if not o:
                nenalezeno.append(adresa); continue
            fo = je_fyzicka_osoba(nazev)
            if fo: fyzicke += 1
            misto = {
                "n": "Soukromý chovatel" if fo else nazev,
                "a": "" if fo else adresa,
                "t": t, "k": k,
                "r": (z.get("cz") or "").strip(),
                "u": registr,
                "z": "Registr SVS",
            }
            klic_obce = o["obec"] + "|" + o["okres"]
            ob = obces = obce.setdefault(klic_obce, {"obec": o["obec"], "okres": o["okres"], "kraj": o["kraj"],
                                                     "lat": o["lat"], "lon": o["lon"], "m": []})
            ob["m"].append(misto); celkem += 1
    for d in doporucene():
        o = najdi_obec(d["adresa"], podle_nazvu, podle_psc)
        if not o:
            nenalezeno.append("DOPORUCENE: " + d["adresa"]); continue
        klic_obce = o["obec"] + "|" + o["okres"]
        ob = obce.setdefault(klic_obce, {"obec": o["obec"], "okres": o["okres"], "kraj": o["kraj"],
                                         "lat": o["lat"], "lon": o["lon"], "m": []})
        ob["m"].insert(0, {"n": d["nazev"], "a": d["adresa"], "t": d["co"], "k": d["kategorie"],
                           "r": "", "u": d.get("odkaz", ""), "z": "Doporučeno v Akademii", "d": 1})
        celkem += 1
    for t in tipy():
        o = najdi_obec((t.get("adresa") or "") + ", " + t.get("obec", ""), podle_nazvu, podle_psc)
        if not o:
            nenalezeno.append("TIP: " + t.get("obec", "")); continue
        klic_obce = o["obec"] + "|" + o["okres"]
        ob = obce.setdefault(klic_obce, {"obec": o["obec"], "okres": o["okres"], "kraj": o["kraj"],
                                         "lat": o["lat"], "lon": o["lon"], "m": []})
        n = int(t.get("pocet", 1) or 1)
        popis = " · ".join(x for x in [t.get("co", ""), ("pastva: " + t["pastva"]) if t.get("pastva") else "",
                                        t.get("jak", ""), ("doporučuje %d lidí" % n) if n > 1 else ""] if x)
        ob["m"].insert(0, {"n": "Soukromý chovatel" if t.get("soukromy") else t["nazev"],
                           "a": "" if t.get("soukromy") else t.get("adresa", ""),
                           "t": "Tip od lidí", "k": t.get("kategorie", "ostatni"), "r": "",
                           "u": "" if t.get("soukromy") else t.get("odkaz", ""),
                           "z": "Tip od lidí", "l": 1, "p": popis, "q": t.get("poznamka", "")})
        celkem += 1
    ven = sorted(obce.values(), key=lambda o: -len(o["m"]))
    registry = [SVS_MLEKO, SVS_PP]
    typy = sorted({m["t"] for o in ven for m in o["m"]})
    for o in ven:
        for m in o["m"]:
            if m["u"] in registry: m["u"] = registry.index(m["u"])
            m["t"] = typy.index(m["t"])
            if not m["a"]: del m["a"]
            if not m["r"]: del m["r"]
            m.pop("z", None)
        o["lat"] = round(o["lat"], 4); o["lon"] = round(o["lon"], 4)
    json.dump({"aktualizace": "27. 9. 2026", "registry": registry, "typy": typy, "obce": ven},
              open("sourcing/data.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    from collections import Counter
    print("mist celkem:", celkem, "| obci:", len(ven), "| anonymizovanych fyzickych osob:", fyzicke)
    print("podle kategorie:", Counter(m["k"] for o in ven for m in o["m"]))
    print("nenalezeno adres:", len(nenalezeno))
    for a in nenalezeno[:12]: print("   ", a)
    print("velikost data.json:", os.path.getsize("sourcing/data.json"), "B")
