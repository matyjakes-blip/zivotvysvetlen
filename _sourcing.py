#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Postavi sourcing.html: mapa CR a SR v nasem vizualu, cela z vlastniho webu.
Obrysy: sourcing/obrysy.json. Mista: sourcing/data.json (stavi _sourcing_data.py).
Body se kresli v prohlizeci, stranka sama zustava lehka."""
import json, math

W, H = 1000, 560
OKRAJ = 26

KATEGORIE = [
    ("mleko",   "Mléko"),
    ("maso",    "Maso"),
    ("zverina", "Zvěřina"),
    ("med",     "Med"),
    ("ryby",    "Ryby"),
    ("vejce",   "Vejce"),
]


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
    pocet = sum(len(o["m"]) for o in data["obce"])
    filtry = "".join('<button class="filtr" data-kat="%s">%s</button>' % (k, esc(n)) for k, n in KATEGORIE)

    telo = """
<main>
  <section class="hero hero-uzsi">
    <div class="obal uzky">
      <p class="nadtitul">Zdarma</p>
      <h1 class="nadpis-str">Primal sourcing mapa</h1>
      <p class="tvrzeni-pod">Kde v Česku sehnat syrové mléko, maso, zvěřinu, med a ryby přímo od chovatele. {pocet_slovy} míst na jedné mapě.</p>
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
      <p class="popisek"><span class="pocet">Načítám…</span> · klikni na bod</p>
    </div>
  </section>

  <section class="pas">
    <div class="obal uzky">
      <p class="nadtitul">Odkud to je</p>
      <h2>Oficiální registr a moje doporučení</h2>
      <p class="text-stred">Základ mapy tvoří registry Státní veterinární správy: <strong>každý, kdo smí prodávat syrové mléko ze dvora nebo z automatu</strong>, bourat maso, zpracovávat zvěřinu, ryby a med pro přímý prodej. Je to seznam lidí, kteří na to mají povolení, ne reklama. Zlatě orámované body jsou farmy, které doporučuju v Akademii.</p>
      <p class="text-stred">Soukromé chovatele ukazuju jen podle obce, bez jména a ulice. Kdo je chce najít, dohledá je v registru SVS podle čísla.</p>
      <p class="text-stred drobne">Údaje ze dne {aktualizace}. Slovensko se doplní.</p>
      <div class="stred"><a class="cta-druhy" href="{skool}">Vstoupit do Akademie</a></div>
    </div>
  </section>

  <section class="pas zaver-pas">
    <div class="obal uzky stred">
      <div class="ozdoba" aria-hidden="true">◆</div>
      <h2>Dám vědět, až přibydou místa</h2>
      <p class="text-stred">Nech mi e-mail a napíšu ti, až se mapa rozroste. Nic jiného ti posílat nebudu.</p>
      <!-- FORMULAR -->
      <div class="formular-misto">
        <p class="drobne">Formulář sem přijde, jakmile bude založený.</p>
      </div>
      <!-- /FORMULAR -->
    </div>
  </section>
</main>

<script>
(function () {{
  var P = {par};
  var KAT = {kat};
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
      var p = xy(o.lon, o.lat);
      var c = document.createElementNS(NS, 'circle');
      c.setAttribute('cx', p[0].toFixed(1)); c.setAttribute('cy', p[1].toFixed(1));
      c.setAttribute('r', Math.min(8, 1.9 + 1.1 * Math.sqrt(n)).toFixed(2));
      c.setAttribute('class', 'misto' + (maDop ? ' dop' : ''));
      c.setAttribute('data-i', i);
      if (maDop) dop.push(c); else vrstva.appendChild(c);
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
      b.appendChild(el('p', 'polozka-typ', (m.d ? '◆ Doporučeno v Akademii · ' : '') + (DATA.typy[m.t] || '')));
      b.appendChild(el('p', 'polozka-nazev', m.n));
      if (m.a) b.appendChild(el('p', 'polozka-adresa', m.a));
      var u = typeof m.u === 'number' ? DATA.registry[m.u] : m.u;
      if (u) {{
        var a = el('a', 'polozka-odkaz', m.d ? 'Otevřít web farmy' : ('V registru SVS' + (m.r ? ' · ' + m.r : '')));
        a.href = u; a.target = '_blank'; a.rel = 'noopener';
        b.appendChild(a);
      }}
      s.appendChild(b);
    }});
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

  fetch('/sourcing/data.json').then(function (r) {{ return r.json(); }}).then(function (d) {{
    DATA = d; kresli();
  }}).catch(function () {{ pocetEl.textContent = 'Mapu se nepodařilo načíst.'; }});
}})();
</script>
""".format(W=W, H=H, tvary=tvary, filtry=filtry, skool=SKOOL,
           pocet_slovy=("Přes %d 000" % (pocet // 1000)) if pocet >= 1000 else str(pocet),
           aktualizace=data.get("aktualizace", ""),
           par=json.dumps({k: round(v, 6) for k, v in par.items()}),
           kat=json.dumps(dict(KATEGORIE), ensure_ascii=False))

    stranka = HLAVA.format(titulek="Primal sourcing mapa · Život vysvětlen",
                           popis="Syrové mléko, maso, zvěřina, med a ryby přímo od chovatele. Přes 3 000 míst v Česku na jedné mapě, zdarma.",
                           kanon="sourcing.html", ogobr="mapa/hero.jpg",
                           skool=SKOOL) + telo + PATA.format(skool=SKOOL)
    open("sourcing.html", "w", encoding="utf-8").write(stranka)
    return pocet
