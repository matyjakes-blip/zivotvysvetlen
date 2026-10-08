#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Návrhy v2 (7. 10. 2026): stránka Osobní vedení 1:1 a stránka O mně.
Texty: jeho věty ze schválených karuselů (kit/content/pinned-carousels.md, 21. 7.) a z lekce 0.0,
zkrácené jen ubráním. Popisy u ukázky boardu a nadpisy kapitol jsou MOJE, k jeho schválení."""
import html, re

def esc(t):
    return html.escape(t, quote=False)


# ------------------------------------------------------------ 1:1
BOLEST = [
    "Většina lidí, co ke mně přijde, už zkusila všechno. Diety, doplňky, doktory, plány od trenérů.",
    "A pořád to samé. Únava, trávení, pleť, žádná energie. Nikdo jim neřekl proč.",
    "Nedávám další jídelníček s kaloriemi. Bereme terén a čistíme ho od kořene.",
    "Pryč průmyslové oleje. Zpátky skutečné jídlo. Srovnat světlo, spánek a trávení.",
]

# úvod 1:1: varianty (MOJE věty, 8. 10. k výběru); výchozí V2
UVOD_11 = {
    "v1": ("Život vysvětlen.", "Na tobě.", "Akademie je ten systém napsaný. Tohle je ten samý systém aplikovaný na jednoho člověka."),
    "v2": ("Na každé proč", "dostaneš odpověď.", "Spánek, jídlo, trénink, hormony, pleť i hlava. Tvoje tělo, tvoje pořadí kroků a vysvětlení, proč zrovna takhle."),
    "v3": ("Celý systém.", "Postavený kolem tebe.", "Akademie je ten systém napsaný. Tohle je ten samý systém aplikovaný na jednoho člověka."),
}
UVOD_11_VYCHOZI = "v2"

# co klient dostane navíc k Akademii (podle skutečné struktury klientského boardu; popisy MOJE)
NAVIC = [
    ("🏛️", "Tvůj proces implementace", "Dokument jen pro tebe: tvoje situace, tvoje pořadí kroků a proč zrovna takhle."),
    ("🚀", "Úkoly týden po týdnu", "Každý týden se otevře další krok, až zvládneš ten předchozí."),
    ("📋", "Check-in každou neděli", "Krátký formulář: spánek, energie, trávení, fotky. Podle něj stavím další týden."),
    ("🗺️", "Tvoje mapa", "Tvoje čísla a cíle na jednom místě, ať je vidět posun."),
    ("📞", "Hovory se mnou", "Onboarding a kontrolní hovory, když je potřeba něco přehodit."),
    ("🌟", "Podklady jen pro klienty", "Krevní testy, syrová kuchyně v receptech, nákup v řetězcích a hotový košík na Rohlíku."),
]

# ukázka boardu: (ikona, název bloku, co v něm je = MOJE věty o mechanice)
BOARD = [
    ("🏛️", "Tvůj specifický proces implementace", "Dokument jen pro tebe. Tvoje situace, tvoje pořadí kroků a proč zrovna takhle."),
    ("🚀", "Týden 1", "První týden rozepsaný na konkrétní úkoly, které si odškrtáváš."),
    ("📦", "Týdenní balíček", "Každý týden jedna věc navíc. Tempo podle toho, co ti reálně vychází."),
    ("📋", "Check-in", "Krátký formulář každý týden: spánek, energie, trávení, fotky."),
    ("📸", "Fotky vedle sebe", "Tvoje fotky ve třech sloupcích, týden po týdnu. Posun vidíš sám."),
    ("🍳", "Recepty a nákup", "Co vařit a co vzít do košíku, i v obyčejném řetězci."),
]

PRUBEH = [
    ("Hovor", "Zdarma, nezávazně. Projdeme, co řešíš a co už jsi zkoušel."),
    ("Dotazník", "Historie, prostředí, spánek, jídlo, trénink, míry a fotky."),
    ("Tvůj dokument", "Tvoje pořadí kroků a odůvodnění."),
    ("Každý týden", "Check-in a balíček s jednou věcí."),
    ("Hovory", "Když je potřeba něco přehodit."),
]

NENI = [
    "Není to jídelníček, který vydrží týden a pak se vrátíš tam, kde jsi byl.",
    "Nepočítáš makra ani kalorie. Kalorie jsou měřák, ne cíl.",
    "Nedostaneš seznam doplňků, které si máš koupit.",
    "Osobní vedení beru od 20 let. Pro mladší je tu Akademie.",
]


def _board():
    radky = "".join(
        '<div class="nb-blok"><div class="nb-hlava"><span class="nb-ikona">%s</span><b>%s</b></div>'
        '<div class="nb-obsah"><span></span><span></span><span class="kratka"></span></div></div>' % (i, esc(n))
        for i, n, _ in BOARD)
    return ('<div class="nb" aria-label="Ukázka osobního boardu">'
            '<div class="nb-lista"><i></i><i></i><i></i><span>Tvůj board · Osobní vedení</span></div>'
            '<div class="nb-stranka"><div class="nb-titul"><span class="nb-velka-ikona">🧭</span><b>Tvoje jméno</b><small>Týden 3 z 24 · další check-in v neděli</small></div>'
            '<div class="nb-mriz">%s</div></div>'
            '<p class="nb-pozn">Ukázka. Jména a data jsou vymyšlená.</p></div>' % radky)


def postav_11_v2(HLAVA, PATA, SKOOL, CALENDLY, varianta=None, soubor="jedna-na-jedna.html", recenze=""):
    bolest = "".join('<p>%s</p>' % esc(t) for t in BOLEST)
    popisy = "".join('<li><span class="nb-ikona">%s</span><div><b>%s</b><span>%s</span></div></li>' % (i, esc(n), esc(p))
                     for i, n, p in BOARD)
    prubeh = "".join('<li><b>%d</b><strong>%s</strong><span>%s</span></li>' % (k + 1, esc(a), esc(b))
                     for k, (a, b) in enumerate(PRUBEH))
    neni = "".join('<li>%s</li>' % esc(x) for x in NENI)
    h1a, h1b, pod = UVOD_11[varianta or UVOD_11_VYCHOZI]
    navic = "".join('<li><span class="nb-ikona">%s</span><div><b>%s</b><span>%s</span></div></li>' % (i, esc(n), esc(t)) for i, n, t in NAVIC)
    import os
    board_img = '<figure class="board-snimek"><img src="/media/ukazka-board.jpg" alt="Ukázka osobního boardu v Notionu" loading="lazy"><figcaption>Ukázka. Jméno a data jsou vymyšlená.</figcaption></figure>' if os.path.exists("media/ukazka-board.jpg") else _board()
    telo = """
<main>
  <section class="uvod v11-uvod">
    <div class="obal uvod-mriz">
      <div class="uvod-text">
        <p class="nadtitul">Osobní vedení 1:1</p>
        <h1 class="v11-h1">{h1a}<span>{h1b}</span></h1>
        <p class="tvrzeni-pod">{pod}</p>
        <div class="tlacitka"><a class="cta" href="#zadost">Požádat o místo</a><a class="cta-druhy" href="#board">Co dostaneš</a></div>
        <p class="drobne">Hovor je zdarma a nezavazuje.</p>
      </div>
      <div class="v11-board">{board_img}</div>
    </div>
  </section>

  <section class="pas v11-bolest">
    <div class="obal uzky">{bolest}</div>
  </section>

  <section class="pas" id="board">
    <div class="obal">
      <p class="nadtitul">Co dostaneš</p>
      <h2>Tohle všechno dostaneš</h2>
      <p class="text-stred">Akademie ti dá všechno, co potřebuješ vědět. Osobní vedení to postaví na tobě.</p>
      <div class="v11-dostanes"><div>{board_img}</div>
        <div><div class="v11-akademie"><span class="nb-ikona">🎓</span><div><b>Celá Akademie</b><span>Všech 102 lekcí, protokoly a komunita. Je v ceně.</span></div></div>
        <p class="v11-navic-titul">Navíc jen pro klienty</p><ul class="v11-popisy">{navic}</ul></div>
      </div>
    </div>
  </section>

  <section class="pas v11-prubeh-pas">
    <div class="obal">
      <p class="nadtitul">Jak to běží</p>
      <h2>Od hovoru k prvnímu týdnu</h2>
      <ol class="v11-osa">{prubeh}</ol>
    </div>
  </section>

{recenze}
  <section class="pas">
    <div class="obal uzky">
      <p class="nadtitul">Ať je jasno</p>
      <h2>Co to není</h2>
      <ul class="neni">{neni}</ul>
    </div>
  </section>

  <section class="pas v11-zadost-pas" id="zadost">
    <div class="obal uzky">
      <p class="nadtitul">Žádost o místo</p>
      <h2>Tři otázky, pak si vybereš termín</h2>
      <div class="v11-form">
        <p class="v11-krok">Krok 1 ze 3</p>
        <label>Jméno<input type="text" placeholder="Jak ti říkat" disabled></label>
        <label>Věk<input type="text" placeholder="Osobní vedení beru od 20 let" disabled></label>
        <div class="v11-form-dalsi"><span>2 · Co řešíš a co už jsi zkoušel</span><span>3 · Kontakt (Instagram nebo WhatsApp)</span></div>
        <a class="cta" href="{calendly}">Pokračovat</a>
        <p class="drobne">Návrh: formulář se dodělá v kroku 5. Teď tlačítko vede rovnou do kalendáře.</p>
      </div>
    </div>
  </section>
</main>
""".format(board_img=board_img, bolest=bolest, navic=navic, prubeh=prubeh, neni=neni, calendly=CALENDLY,
           h1a=esc(h1a), h1b=esc(h1b), pod=esc(pod), recenze=recenze)
    stranka = HLAVA.format(titulek="Osobní vedení 1:1 · Život vysvětlen",
                           popis="Akademie je ten systém napsaný. 1:1 je ten samý systém aplikovaný na jednoho člověka. Hovor je zdarma.",
                           kanon="jedna-na-jedna.html", ogobr="media/matyas-uvod.jpg", skool=SKOOL) + telo + PATA.format(skool=SKOOL)
    open(soubor, "w", encoding="utf-8").write(stranka)


# ------------------------------------------------------------ O mně
# kapitoly: (věk, nadpis = MOJE, jeho věty z lekce 0.0 zkrácené ubráním, fotky, popisek fotek)
KAPITOLY = [
    ("Do 15", "Bílé pečivo a kakao pudinky",
     ["Jakmile jsem jako dítě začal jíst normální jídlo a přestal být jen na mateřském mléce, sám od sebe jsem začal odmítat maso – aniž by mě k tomu rodiče nutili.",
      "Nebyl jsem ani na typické vegetariánské stravě, jedl jsem prakticky jen bílé pečivo a zpracovaný kakao pudinky. Tahle strava mi vydržela až do patnácti let."],
     ["0.0__04-jako-dite.jpg", "0.0__01-patnact-selfie.jpg"], ""),
    ("15", "167 cm, 55 kilo",
     ["Kolem patnácti se u mě začaly hodně projevovat ženský rysy – široký boky, tuk hlavně na břiše, žádný svaly, jemnej, pískavej hlas.",
      "Když jsem v patnácti končil základku, měl jsem 167 cm a vážil sotva 55 kilo."],
     ["0.0__03-patnact-postava.jpg", "0.0__02-patnact-parta.jpg", "0.0__05-noc-cigareta.jpg"], ""),
    ("16", "Posilovna a +40 kilo za rok",
     ["Když mi bylo 16, začal jsem chodit do posilky – hlavně proto, že jsem byl fakt hubenej a lidi se mi smáli.",
      "Za jeden rok jsem přibral 40 kg a vyrostl o 12 cm.",
      "Ale upřímně… skoro všechno šlo do tuku a zdraví šlo úplně stranou."],
     ["0.0__06-sedmnact-bulk.jpg"], "182 cm, 95 kg, poslední měsíc, kdy mi bylo 16"),
    ("17", "Klouby, kotník a akné",
     ["Šel jsem k doktorovi s kolenama – řekl mi, že je všechno v pohodě. Šel jsem k dalšímu – řekl to samý.",
      "O pár měsíců později se mi brutálně rozjelo akné. Zkoušel jsem všechno – drahý skincare, červený lampy, celerový džusy, kosmetičky, různé detox kůry... a nic."],
     ["0.0__07-akne-zblizka.jpg", "0.0__08-akne-venku.jpg", "0.0__10-cervena-lampa.jpg"], ""),
    ("18", "110 kilo a krevní testy",
     ["Šel jsem k doktorce na krevní testy, protože už jsem fakt nevěděl, co se se mnou děje – a byla úplně v šoku.",
      "Řekla mi, že mám hyperurikémii – zvýšenou hladinu kyseliny močový, a to na úrovni 60letýho chlapa. Zároveň jsem si nechal zkontrolovat i testosteron, a ten byl taky úplně na dně.",
      "Když mi bylo osmnáct, vážil jsem 110 kilo při 182 cm."],
     ["0.0__09-porovnani-dvojice.jpg"], ""),
    ("Zlom", "Správná dieta",
     ["Okamžitě po správné dietě se mi zastavil zánět, kyselina močová a močovina se vrátili do normálu. Můj testosteron vystřelil, můj metabolismus se dal zpátky do normálu, vysekal jsem 15 kilo a vypadal 10 krát lépe."],
     ["0.0__11-pred-ctyri-mesice.jpg", "0.0__12-po-ctyrech-mesicich.jpg"], "Rozdíl 4 měsíce"),
    ("20", "Dnes",
     ["Od té doby jsem nikdy nebyl šťastnější."],
     ["0.0__13-pred-dva-a-pul-roku.jpg", "0.0__14-po-dvou-a-pul-roce.jpg"], "Rozdíl 2,5 roku mojí cesty"),
]


def postav_pribeh_v2(HLAVA, PATA, SKOOL, cely_text_html):
    kap = []
    for vek, nadpis, vety, fotky, popisek in KAPITOLY:
        obr = "".join('<figure><img src="/pribeh/%s" alt="" loading="lazy"></figure>' % f for f in fotky)
        pop = '<p class="popisek">%s</p>' % esc(popisek) if popisek else ""
        kap.append('<section class="kap"><div class="kap-vek">%s</div><div class="kap-telo"><h2>%s</h2>%s'
                   '<div class="kap-fotky n%d">%s</div>%s</div></section>'
                   % (esc(vek), esc(nadpis), "".join("<p>%s</p>" % esc(v) for v in vety), len(fotky), obr, pop))
    telo = """
<main>
  <section class="uvod">
    <div class="obal uvod-mriz">
      <div class="uvod-text">
        <p class="nadtitul">O mně</p>
        <h1>Mohl jsem já, proč ne ty?</h1>
        <p class="tvrzeni">Moje důvěryhodnost není v tom, že jsem to vždycky věděl.<strong>Je v tom, že jsem si tu špatnou cestu prošel celou.</strong></p>
        <ol class="osa"><li><b>15 let</b><span>167 cm · 55 kg</span></li><li><b>18 let</b><span>182 cm · 110 kg</span></li><li><b>20 let</b><span>191 cm · 94 kg</span></li></ol>
      </div>
      <figure class="uvod-foto"><img src="/_nahledy/galerie/g2.jpg" alt="Matyáš Jakeš" width="640" height="800"></figure>
    </div>
  </section>
  <section class="pas omne-mel" id="prosel">
    <div class="obal uzky">
      <p class="nadtitul">Čím jsem si prošel</p>
      <ul class="mel-seznam"><li>Zažívací problémy</li><li>Nadváha, +55 kg (z 55 na 110)</li><li>Akné</li><li>Inzulínová rezistence</li><li>Neustálé přejídání</li><li>Záněty kloubů</li></ul>
    </div>
  </section>
  <div class="obal kapitoly">{kapitoly}</div>
  <section class="pas autorita-pas" id="odkud">
    <div class="obal uzky">
      <p class="nadtitul">Odkud to vím</p>
      <h2>Co jsem studoval a z čeho čerpám</h2>
      <div class="autorita-mriz">
        <div><b>Studium</b><span>doplníš: co a kde jsi studoval, kurzy, certifikáty</span></div>
        <div><b>Zdroje</b><span>doplníš: autoři a knihy, ze kterých stavíš (Weston Price, Pottenger…)</span></div>
        <div><b>Praxe</b><span>doplníš: od kdy pracuješ s klienty, kolik lidí jsi vedl</span></div>
        <div><b>Akademie</b><span>6 modulů, 102 lekcí, u každé napsané, odkud informace je</span></div>
      </div>
    </div>
  </section>
  <section class="pas citat-pas"><div class="obal uzky stred"><p class="citat">Hormony mají neskutečný vliv na člověka a hrají zásadní roli ve vývinu jeho vzhledu, zdraví orgánů, metabolismu, a psychiky.</p></div></section>
  <section class="pas"><div class="obal uzky"><details class="cely-text"><summary>Celý příběh, jak jsem ho napsal</summary><div class="text">{cely}</div></details></div></section>
  <section class="pas zaver-pas"><div class="obal uzky stred"><div class="tlacitka" style="justify-content:center"><a class="cta" href="/akademie.html">Prohlédnout Akademii</a><a class="cta-druhy" href="/jedna-na-jedna.html">Osobní vedení 1:1</a></div></div></section>
</main>
""".format(kapitoly="".join(kap), cely=cely_text_html)
    stranka = HLAVA.format(titulek="O mně · Život vysvětlen",
                           popis="Od 55 kilo přes 110 kilo a akné až sem. Celá cesta.",
                           kanon="pribeh.html", ogobr="pribeh/0.0__09-porovnani-dvojice.jpg", skool=SKOOL) + telo + PATA.format(skool=SKOOL)
    open("pribeh.html", "w", encoding="utf-8").write(stranka)
