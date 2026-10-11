#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Postavi sourcing.html: mapa CR a SR v nasem vizualu, cela z vlastniho webu.
Obrysy: sourcing/obrysy.json. Mista: sourcing/data.json (stavi _sourcing_data.py).
Body se kresli v prohlizeci, stranka sama zustava lehka."""
import json, math, os

FORM_TIPY = "https://indecisive-zenobia-f04.notion.site/ce110a2416d64dbbbbf337d14894c801"

W, H = 1000, 560
OKRAJ = 26

KATEGORIE = [
    ("mleko",   "Mléko"),
    ("maso",    "Maso"),
    ("zverina", "Zvěřina"),
    ("med",     "Med"),
    ("ryby",    "Ryby"),
    ("vejce",   "Vejce"),
    ("obchod",  "Farmářské obchody"),
]

# Vrstva z OpenStreetMap (připravená 11. 10. 2026 do sourcing/zdroje/osm-cz.json). Samostatný soubor
# sourcing/osm.json pod ODbL (© přispěvatelé OpenStreetMap); s daty z registru SVS se slučuje až v prohlížeči,
# takže registr zůstává oddělený. Na mapu jen místa, kde se dá něco koupit.
OSM_VYRADIT = ("jen craft=beekeeper", "firemní prodejna velké mlékárny", "včelařské potřeby",
               "vending=sweets", "construction_date", "ne mléčná prodejna")
# Slovensko z OpenStreetMap (11. 10. 2026, sourcing/zdroje/osm-sk.json): stejný formát, shoda s registrem ŠVPS = duplicita_svps
OSM_ZDROJE = ("sourcing/zdroje/osm-cz.json", "sourcing/zdroje/osm-sk.json")
OSM_KAT = {"Mlékomat": "mleko", "Mléčná prodejna": "mleko", "Med": "med", "Farmářský obchod": "obchod"}


def osm_vrstva(data):
    zdroje = [json.load(open(z, encoding="utf-8")) for z in OSM_ZDROJE if os.path.exists(z)]
    if not zdroje:
        return None
    src = {"stazeno": max(z.get("stazeno", "") for z in zdroje), "mista": [m for z in zdroje for m in z["mista"]]}
    souradnice = {(o["obec"], o["okres"]): (o["lat"], o["lon"]) for o in data["obce"]}
    skupiny = {}
    for m in src["mista"]:
        upo = m.get("upozorneni") or []
        upo = [upo] if isinstance(upo, str) else upo
        if any(v in u for u in upo for v in OSM_VYRADIT):
            continue
        if m.get("duplicita_svs") or m.get("duplicita_svps") or m.get("duplicita_osm"):
            continue
        typ, bezejmenne = m["typ"], bool(m.get("nazev_generovany"))
        if bezejmenne and typ in ("Med", "Farmářský obchod"):
            continue
        if bezejmenne and typ == "Mlékomat" and (m.get("mozna_duplicita_svs") or m.get("mozna_duplicita_svps")):
            continue
        soukr = bool(m.get("soukroma_osoba"))
        pol = {"n": "Soukromý prodej" if soukr else m["nazev"], "t": typ, "k": OSM_KAT.get(typ, "obchod"), "o": m["osm"]}
        if not soukr and m.get("adresa"):
            pol["a"] = m["adresa"]
        if not soukr and m.get("web"):
            pol["w"] = m["web"]
        if m.get("oteviraci_doba"):
            pol["h"] = m["oteviraci_doba"]
        klic = (m["obec"], m["okres"])
        if klic not in skupiny:
            lat, lon = souradnice.get(klic, (m.get("obec_lat") or m["lat"], m.get("obec_lon") or m["lon"]))
            skupiny[klic] = {"obec": m["obec"], "okres": m["okres"], "kraj": m["kraj"], "lat": lat, "lon": lon, "m": []}
        skupiny[klic]["m"].append(pol)
    ven = {"zdroj": "OpenStreetMap", "licence": "ODbL 1.0 (https://opendatacommons.org/licenses/odbl/)",
           "autori": "© přispěvatelé OpenStreetMap", "stazeno": src.get("stazeno", ""), "obce": list(skupiny.values())}
    json.dump(ven, open("sourcing/osm.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    return ven


def projekce(obrysy):
    vse = [b for p in obrysy.values() for c in p for r in c for b in r]
    lat0 = sum(b[1] for b in vse) / len(vse)
    k = math.cos(math.radians(lat0))
    xs = [b[0] * k for b in vse]; ys = [b[1] for b in vse]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    mer = min((W - 2 * OKRAJ) / (x1 - x0), (H - 2 * OKRAJ) / (y1 - y0))
    dx = (W - (x1 - x0) * mer) / 2
    dy = (H - (y1 - y0) * mer) / 2
    par = {"k": k, "x0": x0, "y1": y1, "mer": mer, "dx": dx, "dy": dy}

    def bod(lon, lat):
        return ((lon * k - x0) * mer + dx, (y1 - lat) * mer + dy)
    return bod, par


def cesty(obrysy, bod):
    ven = []
    for _, casti in obrysy.items():
        d = []
        for cast in casti:
            for prstenec in cast:
                d.append(" ".join("%s%.1f %.1f" % ("M" if i == 0 else "L", *bod(lon, lat))
                                  for i, (lon, lat) in enumerate(prstenec)) + " Z")
        ven.append(" ".join(d))
    return ven


def postav(HLAVA, PATA, SKOOL, esc):
    obrysy = json.load(open("sourcing/obrysy.json", encoding="utf-8"))
    data = json.load(open("sourcing/data.json", encoding="utf-8"))
    bod, par = projekce(obrysy)
    tvary = "".join('<path class="zeme" d="%s"></path>' % d for d in cesty(obrysy, bod))
    osm = osm_vrstva(data)
    pocet_osm = sum(len(o["m"]) for o in osm["obce"]) if osm else 0
    pocet = sum(len(o["m"]) for o in data["obce"]) + pocet_osm
    osm_datum = ""
    if osm and osm.get("stazeno"):
        r_, m_, d_ = osm["stazeno"].split("-")
        osm_datum = "%d. %d. %s" % (int(d_), int(m_), r_)
    filtry = "".join('<button class="filtr" data-kat="%s">%s</button>' % (k, esc(n)) for k, n in KATEGORIE)
    pocet_tipu = sum(1 for o in data["obce"] for m in o["m"] if m.get("l"))
    if pocet_tipu:
        filtry += '<button class="filtr filtr-dop" data-kat="lide">Od lidí</button>'

    telo = """
<main>
  <section class="hero hero-uzsi">
    <div class="obal uzky">
      <p class="nadtitul">Zdarma</p>
      <h1 class="nadpis-str">Sourcing mapa</h1>
      <p class="tvrzeni-pod">Kde v Česku a na Slovensku sehnat syrové mléko, maso, zvěřinu, med a ryby přímo od chovatele. {pocet_slovy} míst na jedné mapě.</p>
    </div>
  </section>

  <section class="pas mapa-pas">
    <div class="obal">
      <div class="filtry"><button class="filtr aktivni" data-kat="vse">Vše</button>{filtry}<button class="filtr filtr-dop" data-kat="dop">◆ Doporučeno</button></div>
      <div class="hledani"><input id="hledej-obec" type="search" placeholder="Najdi obec" autocomplete="off" aria-label="Najdi obec"></div>
      <div class="mapa-ram">
        <svg viewBox="0 0 {W} {H}" class="mapa-svg" role="img" aria-label="Mapa Česka a Slovenska s místy k nákupu">
          <g class="zeme-vrstva">{tvary}</g>
          <g class="body-vrstva"></g>
        </svg>
        <div class="karta" hidden>
          <button class="karta-zavrit" aria-label="Zavřít">×</button>
          <p class="karta-kat"></p>
          <h3 class="karta-nazev"></h3>
          <div class="karta-seznam"></div>
        </div>
      </div>
      <p class="popisek"><span class="pocet">Načítám…</span> · klikni na bod · část míst © <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">přispěvatelé OpenStreetMap</a></p>
      <div class="pridej">
        <p><strong>Chybí tu místo, kam chodíš?</strong> Registr říká jen, kdo smí prodávat. Jestli je to dobré, víš ty.</p>
        <a class="cta" href="{form_tipy}" target="_blank" rel="noopener">Přidej místo</a>
      </div>
    </div>
  </section>

  <section class="pas">
    <div class="obal uzky">
      <p class="nadtitul">Odkud to je</p>
      <h2>Oficiální registr a moje doporučení</h2>
      <p class="text-stred">Základ mapy tvoří registry Státní veterinární správy: <strong>každý, kdo smí prodávat syrové mléko ze dvora nebo z automatu</strong>, bourat maso, zpracovávat zvěřinu, ryby a med pro přímý prodej. Je to seznam lidí, kteří na to mají povolení, ne reklama. Zlatě orámované body jsou farmy, které doporučuju v Akademii.</p>
      <p class="text-stred">Na Slovensku jsou základem úřední seznamy Štátnej veterinárnej a potravinovej správy SR (ŠVPS): salaše, mlékárny a sýrárny z farem, malá jatka, zvěřina, med a vejce. U jatek a zvěřiny seznam neříká, jestli prodávají veřejnosti, tak si to ověř předem.</p>
      <p class="text-stred">Mlékomaty, mléčné prodejny a farmářské obchody, které v registru nejsou, doplňuju z <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>, otevřené mapy, kterou kreslí lidi. Tyhle body úřad neověřoval, u každého místa je vidět, odkud je.</p>
      <p class="text-stred">Soukromé chovatele ukazuju jen podle obce, bez jména a ulice. Kdo je chce najít, dohledá je v registru SVS nebo ŠVPS podle čísla.</p>
      <p class="text-stred drobne">Česko ze dne {aktualizace}, Slovensko ze dne {aktualizace_sk}. <a href="/jak-mapa-funguje.html">Jak mapa funguje, oprava a odstranění údajů</a></p>
      <div class="stred"><a class="cta-druhy" href="{skool}">Vstoupit do Akademie</a></div>
    </div>
  </section>

  <section class="pas zaver-pas">
    <div class="obal uzky stred">
      <div class="ozdoba" aria-hidden="true">◆</div>
      <h2>Dám vědět, až přibydou místa</h2>
      <p class="text-stred">Nech mi e-mail a napíšu ti, až se mapa rozroste. Nic jiného ti posílat nebudu.</p>
      <!-- FORMULAR -->
      <a class="cta" href="https://indecisive-zenobia-f04.notion.site/7a88bd5ce2bd47e8ba84dd5e08d059f3" target="_blank" rel="noopener">Nechat e-mail</a>
      <p class="drobne" style="margin-top:14px">Formulář běží v Notionu. Jak s e-mailem zacházím, je v <a href="/pravni.html#emaily">zásadách</a>.</p>
      <!-- /FORMULAR -->
    </div>
  </section>
</main>

<script>
(function () {{
  var P = {par};
  var KAT = {kat};
  var SVS_DATUM = {svs_datum}, SVPS_DATUM = {svps_datum}, OSM_DATUM = {osm_datum};
  var W = {W}, H = {H};
  var svg = document.querySelector('.mapa-svg');
  var vrstva = svg.querySelector('.body-vrstva');
  var karta = document.querySelector('.karta');
  var pocetEl = document.querySelector('.pocet');
  var NS = 'http://www.w3.org/2000/svg';
  var DATA = null, filtr = 'vse', vybrana = null;

  function xy(lon, lat) {{
    return [(lon * P.k - P.x0) * P.mer + P.dx, (P.y1 - lat) * P.mer + P.dy];
  }}
  function odpovida(m) {{
    if (filtr === 'vse') return true;
    if (filtr === 'dop') return !!m.d;
    if (filtr === 'lide') return !!m.l;
    return m.k === filtr;
  }}
  function slovo(n) {{ return n === 1 ? 'místo' : (n >= 2 && n <= 4 ? 'místa' : 'míst'); }}
  function cislo(n) {{ return String(n).replace(/\\B(?=(\\d{{3}})+(?!\\d))/g, '\\u00a0'); }}

  function kresli() {{
    while (vrstva.firstChild) vrstva.removeChild(vrstva.firstChild);
    var celkem = 0, dop = [];
    DATA.obce.forEach(function (o, i) {{
      var n = 0, maDop = false;
      o.m.forEach(function (m) {{ if (odpovida(m)) {{ n++; if (m.d) maDop = true; }} }});
      if (!n) return;
      celkem += n;
      var maLidi = o.m.some(function (m) {{ return m.l && odpovida(m); }});
      var p = xy(o.lon, o.lat);
      var c = document.createElementNS(NS, 'circle');
      c.setAttribute('cx', p[0].toFixed(1)); c.setAttribute('cy', p[1].toFixed(1));
      c.setAttribute('r', Math.min(8, 1.9 + 1.1 * Math.sqrt(n)).toFixed(2));
      c.setAttribute('class', 'misto' + (maDop ? ' dop' : '') + (maLidi ? ' lide' : ''));
      c.setAttribute('data-i', i);
      if (maDop || maLidi) dop.push(c); else vrstva.appendChild(c);
    }});
    dop.forEach(function (c) {{ vrstva.appendChild(c); }});
    pocetEl.textContent = cislo(celkem) + ' ' + slovo(celkem);
  }}

  function el(tag, cls, txt) {{
    var e = document.createElement(tag); if (cls) e.className = cls; if (txt) e.textContent = txt; return e;
  }}

  function ukaz(i) {{
    var o = DATA.obce[i]; if (!o) return;
    vybrana = i;
    karta.querySelector('.karta-kat').textContent = o.okres === o.obec ? o.kraj : ('okres ' + o.okres);
    karta.querySelector('.karta-nazev').textContent = o.obec;
    var s = karta.querySelector('.karta-seznam');
    while (s.firstChild) s.removeChild(s.firstChild);
    o.m.filter(odpovida).forEach(function (m) {{
      var b = el('div', 'polozka' + (m.d ? ' polozka-dop' : ''));
      b.appendChild(el('p', 'polozka-typ', (m.d ? '◆ Doporučeno v Akademii · ' : '') + (typeof m.t === 'string' ? m.t : (DATA.typy[m.t] || ''))));
      if (m.p) b.appendChild(el('p', 'polozka-adresa', m.p));
      if (m.q) b.appendChild(el('p', 'polozka-adresa', '„' + m.q + '“'));
      b.appendChild(el('p', 'polozka-nazev', m.n));
      if (m.a) b.appendChild(el('p', 'polozka-adresa', m.a));
      if (m.h) b.appendChild(el('p', 'polozka-adresa', 'Otevírací doba: ' + m.h));
      if (m.s === 'osm') {{
        var ao = el('a', 'polozka-odkaz', m.w ? 'Otevřít web' : 'Na OpenStreetMap');
        ao.href = m.w || ('https://www.openstreetmap.org/' + m.o); ao.target = '_blank'; ao.rel = 'noopener';
        b.appendChild(ao);
        b.appendChild(el('p', 'polozka-zdroj', 'Zdroj: OpenStreetMap, komunitní mapa · stav k ' + OSM_DATUM));
      }} else {{
        var u = typeof m.u === 'number' ? DATA.registry[m.u] : m.u;
        if (u) {{
          var a = el('a', 'polozka-odkaz', m.d ? 'Otevřít web farmy' : (m.l ? 'Otevřít' : ((m.c === 'sk' ? 'V seznamu ŠVPS' : 'V registru SVS') + (m.r ? ' · ' + m.r : ''))));
          a.href = u; a.target = '_blank'; a.rel = 'noopener';
          b.appendChild(a);
        }}
        b.appendChild(el('p', 'polozka-zdroj', m.d ? 'Zdroj: moje doporučení' : (m.l ? 'Zdroj: od lidí, prošel jsem ručně' :
          (m.c === 'sk' ? 'Zdroj: úřední seznam ŠVPS SR · stav k ' + SVPS_DATUM : 'Zdroj: registr Státní veterinární správy · stav k ' + SVS_DATUM))));
      }}
      s.appendChild(b);
    }});
    var ch = el('a', 'karta-chyba', 'Nahlásit chybu nebo odstranění');
    ch.href = 'mailto:mjmates@email.cz?subject=' + encodeURIComponent('Mapa: ' + o.obec);
    s.appendChild(ch);
    karta.hidden = false;
  }}

  svg.addEventListener('click', function (e) {{
    var b = e.target.closest('.misto');
    if (b) ukaz(+b.getAttribute('data-i'));
  }});
  karta.querySelector('.karta-zavrit').addEventListener('click', function () {{ karta.hidden = true; vybrana = null; }});

  document.querySelectorAll('.filtr').forEach(function (f) {{
    f.addEventListener('click', function () {{
      document.querySelectorAll('.filtr').forEach(function (x) {{ x.classList.remove('aktivni'); }});
      f.classList.add('aktivni');
      filtr = f.getAttribute('data-kat');
      kresli();
      if (vybrana !== null) ukaz(vybrana);
    }});
  }});

  function bezDiakritiky(s) {{ return s.normalize('NFD').replace(/[\\u0300-\\u036f]/g, '').toLowerCase(); }}
  document.getElementById('hledej-obec').addEventListener('input', function (e) {{
    var q = bezDiakritiky(e.target.value.trim());
    if (q.length < 2 || !DATA) return;
    for (var i = 0; i < DATA.obce.length; i++) {{
      var o = DATA.obce[i];
      if (bezDiakritiky(o.obec).indexOf(q) === 0 && o.m.some(odpovida)) {{ ukaz(i); return; }}
    }}
  }});

  // registr SVS a vrstva z OpenStreetMap jsou dva oddělené soubory, slučují se až tady
  Promise.all([
    fetch('/sourcing/data.json').then(function (r) {{ return r.json(); }}),
    fetch('/sourcing/osm.json').then(function (r) {{ return r.ok ? r.json() : null; }}).catch(function () {{ return null; }})
  ]).then(function (v) {{
    var d = v[0], osm = v[1];
    if (osm) {{
      var idx = {{}};
      d.obce.forEach(function (o, i) {{ idx[o.obec + '|' + o.okres] = i; }});
      osm.obce.forEach(function (o) {{
        o.m.forEach(function (m) {{ m.s = 'osm'; }});
        var i = idx[o.obec + '|' + o.okres];
        if (i === undefined) d.obce.push(o); else d.obce[i].m = d.obce[i].m.concat(o.m);
      }});
    }}
    DATA = d; kresli();
  }}).catch(function () {{ pocetEl.textContent = 'Mapu se nepodařilo načíst.'; }});
}})();
</script>
""".format(W=W, H=H, tvary=tvary, filtry=filtry, skool=SKOOL, form_tipy=FORM_TIPY,
           pocet_slovy=("Přes %d 000" % (pocet // 1000)) if pocet >= 1000 else str(pocet),
           aktualizace=data.get("aktualizace", ""), aktualizace_sk=data.get("aktualizace_sk", ""),
           svps_datum=json.dumps(data.get("aktualizace_sk", ""), ensure_ascii=False),
           svs_datum=json.dumps(data.get("aktualizace", ""), ensure_ascii=False), osm_datum=json.dumps(osm_datum, ensure_ascii=False),
           par=json.dumps({k: round(v, 6) for k, v in par.items()}),
           kat=json.dumps(dict(KATEGORIE), ensure_ascii=False))

    stranka = HLAVA.format(titulek="Sourcing mapa · Život vysvětlen",
                           popis="Syrové mléko, maso, zvěřina, med a ryby přímo od chovatele. Přes %d 000 míst v Česku a na Slovensku na jedné mapě, zdarma." % (pocet // 1000),
                           kanon="sourcing.html", ogobr="mapa/hero.jpg",
                           skool=SKOOL) + telo + PATA.format(skool=SKOOL)
    open("sourcing.html", "w", encoding="utf-8").write(stranka)
    return pocet
