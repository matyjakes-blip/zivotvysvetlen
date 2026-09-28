#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Postavi sourcing.html: mapa CR a SR v nasem vizualu, cela z vlastniho webu.
Data: sourcing/mista.json, obrysy: sourcing/obrysy.json (TopoJSON prevedeny na body)."""
import json, math, os, html

W, H = 1000, 560
OKRAJ = 26

KATEGORIE = [
    ("mleko",    "Mléko a mléčné"),
    ("maso",     "Maso a orgány"),
    ("vejce",    "Vejce"),
    ("tuky",     "Tuky a sádlo"),
    ("ryby",     "Ryby"),
    ("med",      "Med"),
    ("minerals", "Sůl a minerály"),
    ("zelenina", "Zelenina a ovoce"),
    ("ostatni",  "Ostatní"),
]


def projekce(obrysy):
    """rovnovalecna projekce s korekci podle zemepisne sirky, natazena na platno"""
    vse = [b for p in obrysy.values() for c in p for r in c for b in r]
    lat0 = sum(b[1] for b in vse) / len(vse)
    k = math.cos(math.radians(lat0))
    xs = [b[0] * k for b in vse]; ys = [b[1] for b in vse]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    mer = min((W - 2 * OKRAJ) / (x1 - x0), (H - 2 * OKRAJ) / (y1 - y0))
    dx = (W - (x1 - x0) * mer) / 2
    dy = (H - (y1 - y0) * mer) / 2

    def bod(lon, lat):
        return ((lon * k - x0) * mer + dx, (y1 - lat) * mer + dy)
    return bod


def cesty(obrysy, bod):
    ven = []
    for jmeno, casti in obrysy.items():
        d = []
        for cast in casti:
            for prstenec in cast:
                kusy = []
                for i, (lon, lat) in enumerate(prstenec):
                    x, y = bod(lon, lat)
                    kusy.append("%s%.1f %.1f" % ("M" if i == 0 else "L", x, y))
                d.append(" ".join(kusy) + " Z")
        ven.append((jmeno, " ".join(d)))
    return ven


def postav(HLAVA, PATA, SKOOL, esc):
    obrysy = json.load(open("sourcing/obrysy.json", encoding="utf-8"))
    data = json.load(open("sourcing/mista.json", encoding="utf-8"))
    mista = data.get("mista", [])
    bod = projekce(obrysy)

    tvary = "".join('<path class="zeme" d="%s"></path>' % d for _, d in cesty(obrysy, bod))

    body, seznam = [], []
    for i, m in enumerate(mista):
        try:
            x, y = bod(float(m["lon"]), float(m["lat"]))
        except Exception:
            continue
        kat = m.get("kategorie", "ostatni")
        body.append('<circle class="misto" data-i="%d" data-kat="%s" cx="%.1f" cy="%.1f" r="5"></circle>' % (i, kat, x, y))
        seznam.append({"n": m.get("nazev", ""), "o": m.get("obec", ""), "k": kat,
                       "c": m.get("co", ""), "u": m.get("odkaz", ""), "p": m.get("pozn", "")})

    filtry = "".join(
        '<button class="filtr" data-kat="%s">%s</button>' % (k, esc(n)) for k, n in KATEGORIE)

    prazdno = "" if mista else """
      <p class="text-stred prazdno">Mapa se teprve plní. <strong>První místa do ní zadávám sám</strong> a pak ji otevřu členům Akademie.</p>"""

    telo = """
<main>
  <section class="hero hero-uzsi">
    <div class="obal uzky">
      <p class="nadtitul">Zdarma</p>
      <h1 class="nadpis-str">Primal sourcing mapa</h1>
      <p class="tvrzeni-pod">Kde v Česku a na Slovensku sehnat mléko, maso, vejce a tuky, které za to stojí. Sbírá se to od lidí, kteří tam doopravdy nakupují.</p>
    </div>
  </section>

  <section class="pas mapa-pas">
    <div class="obal">
      <div class="filtry">{filtry}<button class="filtr aktivni" data-kat="vse">Vše</button></div>
      <div class="mapa-ram">
        <svg viewBox="0 0 {W} {H}" class="mapa-svg" role="img" aria-label="Mapa Česka a Slovenska s místy k nákupu">
          <g class="zeme-vrstva">{tvary}</g>
          <g class="body-vrstva">{body}</g>
        </svg>
        <div class="karta" hidden>
          <button class="karta-zavrit" aria-label="Zavřít">×</button>
          <p class="karta-kat"></p>
          <h3 class="karta-nazev"></h3>
          <p class="karta-obec"></p>
          <p class="karta-co"></p>
          <p class="karta-pozn"></p>
          <a class="karta-odkaz" href="#" hidden>Otevřít</a>
        </div>
      </div>
      <p class="popisek">Klikni na bod. <span class="pocet">{pocet}</span></p>{prazdno}
    </div>
  </section>

  <section class="pas">
    <div class="obal uzky">
      <p class="nadtitul">Jak to roste</p>
      <h2>Dívat se může kdokoli, zadávat jen členové</h2>
      <p class="text-stred">Mapa je zdarma a zůstane zdarma. Zadávat do ní místa můžou lidé, kteří jsou uvnitř Akademie, protože ti vědí, co hledají a proč. Tím se drží kvalita a mapa roste sama.</p>
      <div class="stred"><a class="cta-druhy" href="{skool}">Vstoupit do Akademie</a></div>
    </div>
  </section>

  <section class="pas zaver-pas">
    <div class="obal uzky stred">
      <div class="ozdoba" aria-hidden="true">◆</div>
      <h2>Dám vědět, až přibydou místa</h2>
      <p class="text-stred">Nech mi e-mail a napíšu ti, až se mapa rozroste. Nic jiného ti posílat nebudu.</p>
      <!-- SEM PATRI FORMULAR: viz sourcing/PRECTI-ME.md -->
      <div class="formular-misto">
        <p class="drobne">Formulář sem přijde, jakmile bude založený.</p>
      </div>
    </div>
  </section>
</main>

<script>
(function () {{
  var DATA = {json_data};
  var NAZVY = {json_kat};
  var svg = document.querySelector('.mapa-svg');
  if (!svg) return;
  var karta = document.querySelector('.karta');
  var body = svg.querySelectorAll('.misto');

  function ukaz(i) {{
    var m = DATA[i];
    if (!m) return;
    karta.querySelector('.karta-kat').textContent = NAZVY[m.k] || m.k || '';
    karta.querySelector('.karta-nazev').textContent = m.n || '';
    karta.querySelector('.karta-obec').textContent = m.o || '';
    karta.querySelector('.karta-co').textContent = m.c || '';
    karta.querySelector('.karta-pozn').textContent = m.p || '';
    var a = karta.querySelector('.karta-odkaz');
    if (m.u) {{ a.href = m.u; a.hidden = false; }} else {{ a.hidden = true; }}
    karta.hidden = false;
  }}

  svg.addEventListener('click', function (e) {{
    var b = e.target.closest('.misto');
    if (b) ukaz(+b.getAttribute('data-i'));
  }});
  karta.querySelector('.karta-zavrit').addEventListener('click', function () {{ karta.hidden = true; }});

  document.querySelectorAll('.filtr').forEach(function (f) {{
    f.addEventListener('click', function () {{
      document.querySelectorAll('.filtr').forEach(function (x) {{ x.classList.remove('aktivni'); }});
      f.classList.add('aktivni');
      var kat = f.getAttribute('data-kat');
      var n = 0;
      body.forEach(function (b) {{
        var ok = (kat === 'vse' || b.getAttribute('data-kat') === kat);
        b.style.display = ok ? '' : 'none';
        if (ok) n++;
      }});
      var p = document.querySelector('.pocet');
      if (p) p.textContent = n + (n === 1 ? ' místo' : (n >= 2 && n <= 4 ? ' místa' : ' míst'));
      karta.hidden = true;
    }});
  }});
}})();
</script>
""".format(W=W, H=H, tvary=tvary, body="".join(body), filtry=filtry, skool=SKOOL,
           prazdno=prazdno,
           pocet=("%d míst" % len(mista)) if len(mista) != 1 else "1 místo",
           json_data=json.dumps(seznam, ensure_ascii=False),
           json_kat=json.dumps(dict(KATEGORIE), ensure_ascii=False))

    stranka = HLAVA.format(titulek="Primal sourcing mapa · Život vysvětlen",
                           popis="Kde v Česku a na Slovensku sehnat mléko, maso, vejce a tuky, které za to stojí. Mapa zdarma.",
                           kanon="sourcing.html", ogobr="mapa/hero.jpg",
                           skool=SKOOL) + telo + PATA.format(skool=SKOOL)
    open("sourcing.html", "w", encoding="utf-8").write(stranka)
    return len(mista)
