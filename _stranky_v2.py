#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Návrhy v2 (7. 10. 2026): stránka Osobní vedení 1:1 a stránka O mně.
Texty: jeho věty ze schválených karuselů (kit/content/pinned-carousels.md, 21. 7.) a z lekce 0.0,
zkrácené jen ubráním. Popisy u ukázky boardu a nadpisy kapitol jsou MOJE, k jeho schválení."""
import html, os, re
NAHLED = os.environ.get("NAHLED") == "1"

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


# odkaz na formulář přihlášky (Notion formulář do 🎯 Leady), dokud není schválený a veřejný, krok se na živém webu vynechá
PRIHLASKA_URL = None


def _krok_formular():
    if not (PRIHLASKA_URL or NAHLED):
        return ""
    return ('          <p class="prihlaska-krok"><b>2</b>Napiš mi pár řádků o sobě</p>\n'
            '          <p>Jméno, co řešíš, co už jsi zkoušel a jak tě nejlíp zastihnu. Zabere to dvě minuty.</p>\n'
            '          <a class="cta-druhy" href="%s" target="_blank" rel="noopener">Vyplnit přihlášku</a>\n' % (PRIHLASKA_URL or "#zadost"))


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
      <h2>Začíná to hovorem</h2>
      <div class="prihlaska" data-prihlaska>
        <p class="prihlaska-krok"><b>1</b>Kolik ti je let?</p>
        <div class="prepinac prihlaska-volby" role="group" aria-label="Věk"><button type="button" class="prepinac-tl" data-pr-vek="pod" aria-pressed="false">Méně než 20</button><button type="button" class="prepinac-tl" data-pr-vek="nad" aria-pressed="false">20 a víc</button></div>
        <div class="prihlaska-panel" data-pr-panel="pod">
          <p>Osobní vedení beru od 20 let. Pro tebe je teď Akademie: stejné principy, svým tempem.</p>
          <a class="cta" href="/akademie.html">Prohlédnout Akademii</a>
        </div>
        <div class="prihlaska-panel" data-pr-panel="nad">
{formular}          <p class="prihlaska-krok"><b>{krok_hovor}</b>Vyber si termín hovoru</p>
          <p>Hovor je zdarma a nezávazný. Projdeme, co řešíš a co už jsi zkoušel.</p>
          <a class="cta" href="{calendly}">Vybrat termín hovoru</a>
        </div>
      </div>
    </div>
  </section>
</main>
""".format(board_img=board_img, bolest=bolest, navic=navic, prubeh=prubeh, neni=neni, calendly=CALENDLY,
           h1a=esc(h1a), h1b=esc(h1b), pod=esc(pod), recenze=recenze,
           formular=_krok_formular(), krok_hovor="3" if (PRIHLASKA_URL or NAHLED) else "2")
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
    ("18", "106 kilo a krevní testy",
     ["Šel jsem k doktorce na krevní testy, protože už jsem fakt nevěděl, co se se mnou děje – a byla úplně v šoku.",
      "Řekla mi, že mám hyperurikémii – zvýšenou hladinu kyseliny močový, a to na úrovni 60letýho chlapa. Zároveň jsem si nechal zkontrolovat i testosteron, a ten byl taky úplně na dně.",
      "Když mi bylo osmnáct, vážil jsem 106 kilo při 182 cm."],
     ["0.0__09-porovnani-dvojice.jpg"], ""),
    ("Zlom", "Správná dieta",
     ["Okamžitě po správné dietě se mi zastavil zánět, kyselina močová a močovina se vrátili do normálu. Můj testosteron vystřelil, můj metabolismus se dal zpátky do normálu, vysekal jsem 15 kilo a vypadal 10 krát lépe."],
     ["0.0__11-pred-ctyri-mesice.jpg", "0.0__12-po-ctyrech-mesicich.jpg"], "Rozdíl 4 měsíce"),
    ("20", "Dnes",
     ["Od té doby jsem nikdy nebyl šťastnější."],
     ["0.0__13-pred-dva-a-pul-roku.jpg", "0.0__14-po-dvou-a-pul-roce.jpg"], "Rozdíl 2,5 roku mojí cesty"),
]


# „Odkud to vím" (návrh 9. 10. 2026, stavba jako u Beyond Terrain / lievdalton.com: bez titulů, samostudium jako volba,
# jmenované zdroje z lekcí Akademie, vlastní cesta, klienti; tvrzení „líp než většina vystudovaných" chtěl Matyáš)
ODKUD = """  <section class="pas autorita-pas" id="odkud">
    <div class="obal uzky">
      <p class="nadtitul">Odkud to vím</p>
      <h2>Nestudoval jsem to na škole. Šel jsem ke zdrojům.</h2>
      <div class="autorita-text">
        <p>Mikrobiologii, virologii ani medicínu jsem na vysoké škole nestudoval. Všechno, co učím, jsem si nastudoval sám.</p>
        <p>Škola učí, co obor tvrdí dnes. Mě zajímalo, odkud se to vzalo. Proto jsem četl původní práce, ze kterých dnešní učebnice vycházejí, od Mieschera v roce 1869 přes Kossela a Chargaffa po Watsona a Cricka. A k tomu lidi, kteří šli proti proudu nebo zkoumali, jak žili zdraví lidé bez moderní stravy: Béchampa, Enderleina, Reckewega, Reného Quintona a Westona Price.</p>
        <p>V tom, na čem pro tvoje zdraví doopravdy záleží, tedy proč tělo dělá, co dělá, a co mu vrátit, se vyznám líp než většina lidí, kteří tyhle obory vystudovali. Ne proto, že bych byl chytřejší. Jen jsem nezůstal u učebnice.</p>
      </div>
      <div class="autorita-mriz tri">
        <div><b>Na sobě</b><span>Pět let, od 55 kilo přes 106 až sem. Co učím, jsem nejdřív vyzkoušel na vlastním těle.</span></div>
        <div><b>U zdroje</b><span>V Akademii ukazuju i původní práce, ze kterých to vychází, ať si to můžeš ověřit sám.</span></div>
        <div><b>S klienty</b><span>Vedu klienty 1:1. Vidím, co funguje i na jiných tělech než na mém.</span></div>
      </div>
    </div>
  </section>
"""


def postav_pribeh_v2(HLAVA, PATA, SKOOL, cely_text_html):
    # 9. 10. 2026 (Matyáš): příběh zpátky celý jeho slovy, žádné kapitoly; políčka s věkem jen v Důkazu na hlavní stránce
    telo = """
<main>
  <section class="uvod">
    <div class="obal uvod-mriz">
      <div class="uvod-text">
        <p class="nadtitul">O mně</p>
        <h1>Mohl jsem já, proč ne ty?</h1>
        <p class="tvrzeni">Moje důvěryhodnost není v tom, že jsem to vždycky věděl.<strong>Je v tom, že jsem si tu špatnou cestu prošel celou.</strong></p>
        <div class="tlacitka"><a class="cta" href="#pribeh">Číst můj příběh</a><a class="cta-druhy" href="#odkud">Odkud to vím</a></div>
      </div>
      <figure class="uvod-foto"><img src="/media/matyas-uvod.jpg" alt="Matyáš Jakeš" width="640" height="800"></figure>
    </div>
  </section>
  <section class="pas omne-mel" id="prosel">
    <div class="obal uzky">
      <p class="nadtitul">Čím jsem si prošel</p>
      <ul class="mel-seznam"><li>Zažívací problémy</li><li>Nadváha, +51 kg (z 55 na 106)</li><li>Akné</li><li>Inzulínová rezistence</li><li>Neustálé přejídání</li><li>Záněty kloubů</li></ul>
    </div>
  </section>
  <section class="pas pribeh-pas" id="pribeh">
    <div class="obal uzky">
      <p class="nadtitul">Můj příběh</p>
      <div class="text pribeh-text">{cely}</div>
    </div>
  </section>
{odkud}  <section class="pas zaver-pas"><div class="obal uzky stred"><div class="tlacitka" style="justify-content:center"><a class="cta" href="/akademie.html">Prohlédnout Akademii</a><a class="cta-druhy" href="/jedna-na-jedna.html">Osobní vedení 1:1</a></div></div></section>
</main>
""".format(cely=cely_text_html, odkud=ODKUD)
    stranka = HLAVA.format(titulek="O mně · Život vysvětlen",
                           popis="Od 55 kilo přes 106 kilo a akné až sem. Celá cesta, jak jsem ji napsal.",
                           kanon="pribeh.html", ogobr="pribeh/0.0__09-porovnani-dvojice.jpg", skool=SKOOL) + telo + PATA.format(skool=SKOOL)
    open("pribeh.html", "w", encoding="utf-8").write(stranka)
