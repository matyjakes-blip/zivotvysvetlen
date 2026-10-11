# OSM vrstva pro sourcing mapu (jen Česko): přehled

Soubor `osm-cz.json` v téhle složce. Staženo 11. 10. 2026 z Overpass API (stav dat OSM 2026-10-11 05:36 UTC).
Do mapy zatím nic není zapojené, `data.json` ani web se neměnily. Spojení s mapou udělá jiná session.

## Co se stahovalo

Dva dotazy na `overpass-api.de` (oba jsou doslova uložené v `osm-cz.json` jako `dotaz` a `dotaz_obce`).
Každý jednou vrátil chybu 504 „server je přetížený“ a napodruhé prošel.

1. **Místa:** uzly a cesty (`nw`) uvnitř hranice ČR (`area["ISO3166-1"="CZ"][admin_level=2]`, takže Slovensko
   ne) s `shop=farm`, `shop=dairy`, `shop=honey`, `craft=beekeeper`, `vending~milk` a navíc automaty
   s „mléko“ v názvu. Výstup `out center tags` (u cest je bod ve středu).
2. **Obce:** pro každý nalezený prvek obec, ve které podle hranic v OSM leží (`is_in`, `admin_level=8`).
   Kód obce z OSM (`ref`) se páruje na `obce.csv`, takže `obec`/`okres`/`kraj` mají stejný zápis jako
   v `data.json` (včetně velkých písmen u statutárních měst: PLZEŇ, ZLÍN, HRADEC KRÁLOVÉ, ČESKÉ BUDĚJOVICE).
   Praha v OSM hranici obce na úrovni 8 nemá, takže 9 bodů bez obce (všechny v okolí Prahy) šlo do Prahy.
   Zadání chtělo `addr:city`, jinak nejbližší obec z `data.json`. Udělal jsem to přesněji: nejbližší střed
   obce dával špatnou obec u okrajových bodů (třeba Medotéka v Praze 8 vycházela jako Zdiby). Kde `addr:city`
   nesedí s obcí podle hranic, je původní hodnota v `obec_osm` (6 míst, např. „Praha 5“, „Dolní Hedeč“).

## Počty

**Celkem 277 míst** (257 uzlů, 20 cest).

| typ | počet | s názvem z OSM | s webem | s otevírací dobou |
|---|---:|---:|---:|---:|
| Med | 115 | 47 | 12 | 11 |
| Farmářský obchod | 86 | 75 | 45 | 52 |
| Mlékomat | 47 | 12 | 4 | 6 |
| Mléčná prodejna | 29 | 25 | 6 | 8 |
| **celkem** | **277** | **159** | **67** | **77** |

Dál: adresa z `addr:*` u 59 míst, produkty u 52, popis (`description`/`note`) u 18.

**Kategorie:** med 117, mleko 81, ostatni 57, zelenina 16, vejce 4, maso 2.
Farmářské obchody se rozpadají na: ostatni 57, zelenina 16, mleko 5, vejce 4, maso 2, med 2.

**Podle kraje:**

| kraj | celkem | Med | Farmářský obchod | Mlékomat | Mléčná prodejna |
|---|---:|---:|---:|---:|---:|
| Středočeský | 58 | 32 | 11 | 9 | 6 |
| Jihomoravský | 29 | 18 | 7 | 2 | 2 |
| Moravskoslezský | 28 | 1 | 18 | 9 | 0 |
| Pardubický | 26 | 15 | 2 | 6 | 3 |
| Jihočeský | 25 | 14 | 4 | 4 | 3 |
| Plzeňský | 20 | 3 | 15 | 1 | 1 |
| Ústecký | 18 | 9 | 4 | 3 | 2 |
| Královéhradecký | 16 | 1 | 7 | 4 | 4 |
| Vysočina | 11 | 5 | 1 | 4 | 1 |
| Olomoucký | 11 | 6 | 1 | 2 | 2 |
| Hlavní město Praha | 9 | 3 | 6 | 0 | 0 |
| Liberecký | 9 | 2 | 4 | 1 | 2 |
| Zlínský | 9 | 2 | 3 | 1 | 3 |
| Karlovarský | 8 | 4 | 3 | 1 | 0 |

202 míst leží v obci, která už v `data.json` je (`obec_v_mape: true`). Zbylých 75 míst je v 63 obcích,
které tam zatím nejsou. Při spojování se pro ně musí založit nová obec se souřadnicemi z `obce.csv`.

## Duplicity

- **Proti SVS, silná shoda (`duplicita_svs`): 12.** Ve stejné obci nebo do 5 km od středu obce SVS,
  stejná kategorie u mlékomatů/mléčných/medu a buď stejná adresa (2), nebo shodný výrazný název (10).
  Obecná slova (farma, mlékomat, prodej, s.r.o. …) a místní jména se nepočítají.
  Doslovné pravidlo „do 150 m od záznamu SVS“ by nenašlo nic (0), protože body SVS jsou jen středy obcí.
  Shody: U mlsné kozy, ZD Podlesí, Kozí farma Nový Dvůr, Farma Pod Filipkou, Mlékárna Čeladenka,
  Statek Doubravský Dvůr, Obživa, ROLS, Chov charolais (Slabce), AGRO Jesenice, Farma ZPZ, Vacheria.
  Všech 12 jsem prošel ručně, sedí.
- **Proti SVS, možná shoda (`mozna_duplicita_svs` + `mozna_duplicita_duvod`): 20, všechno mlékomaty.**
  18 je mlékomatů bez vlastního názvu v obci, kde SVS už eviduje mlékomat. 2 mají se SVS společné jen
  místní jméno (Bělčice, Chlum u Hořic). Bez názvu se to potvrdit nedá, takže jsou jen označené.
- **Uvnitř OSM (`duplicita_osm` = id prvního záznamu): 7.** Dvakrát zakreslené místo (BIO&CEEPORT,
  Včelí obchůdek, AGRO Jesenice s bezejmenným automatem na stejném bodě, dva automaty v Českém Těšíně 22 m
  od sebe, dva páry včelínů do 50 m a dva stánky „Med“ ve Vlkově do 500 m). Pobočky řetězců (U Lidušky 4× v Plzni, Náš grunt 3×,
  Farmářský obchod 2× v Plzni) leží 1,8 až 2,9 km od sebe, jsou to různé prodejny a označené nejsou.

## 10 ukázkových řádků

| název | typ | kat. | obec, kraj | adresa | otevírací doba | web | duplicita SVS |
|---|---|---|---|---|---|---|---|
| Farma Předlánce | Farmářský obchod | mleko | Višňová, Liberecký | Předlánce 93 | - | farmapredlance.cz | - |
| U mlsné kozy | Mlékomat | mleko | Želešice, Jihomoravský | - | - | farmamlsnakoza.cz/prodejni-automat | Faremní minimlékárna U Mlsné kozy |
| Prodej čerstvého mléka | Mlékomat | mleko | Nižní Lhoty, Moravskoslezský | - | Mo-Su 07:00-23:00; PH on | - | - |
| Statek Doubravský Dvůr | Mléčná prodejna | mleko | Červenka, Olomoucký | Nový Dvůr 243 | Mo-Su 09:00-17:00 | doubravskydvur.cz | OSIČKA Václav MVDr. Nový Dvůr č. 243, kravín |
| Minimlékárna - Farma ZPZ | Mléčná prodejna | mleko | Valašská Bystřice, Zlínský | - | - | farmazpz.cz | FARMA-ZPZ s.r.o. |
| Farmářská prodejna na Ráječku | Farmářský obchod | ostatni | Brno, Jihomoravský | Ráječek 2, 62000 Brno | Mo-Sa 08:00-18:00 | farmarajecek.cz | - |
| Rousova farma | Farmářský obchod | vejce | Libčice nad Vltavou, Středočeský | Lesní 559 | - | rousovafarma.cz | - |
| farma Strážný | Farmářský obchod | maso | Strážný, Jihočeský | Hliniště 45, 38443 Strážný | - | farmastrazny.cz | - |
| Medotéka | Med | med | Praha, Hlavní město Praha | Famfulíkova 1138/4 | Tu-Th 09:00-17:00; Fr 09:00-16:00 | medoteka-prokes.cz | - |
| Kolowratovy sady | Farmářský obchod | zelenina | Přimda, Plzeňský | - | Mo-Fr 8:00-11:30, 12:00-15:00 | kolowratovysady.cz | - |

## Problémy s kvalitou dat

1. **Včelaři nejsou prodejny.** 68 ze 115 „Med“ je jen `craft=beekeeper` bez názvu a bez náznaku prodeje.
   Často jde o polohu včelína nebo úlů. Mají `upozorneni` „prodej medu neověřen“. Na mapu bych je
   dal jen s rozmyslem, nebo vůbec.
2. **Mlékomaty jsou chudé.** 35 ze 47 nemá v OSM název (dostaly „Mlékomat“, nebo „Mlékomat (provozovatel)“,
   když je provozovatel firma), jen 4 mají web a 6 otevírací dobu. SVS má 118 mlékomatů, takže OSM přidá
   hlavně polohu na metr. Velká část se se SVS nejspíš kryje (viz 20 možných shod).
3. **`shop=farm` se v OSM používá volně.** Je tam pekárna (Náš chléb), delikatesy (Gusto Italia), e-shopy
   (Zelený eshop, Bedýnky Brno), samosběr jahod, sady a brambory. Kategorie u farmářských obchodů jsem
   určil jen podle klíčových slov v názvu, popisu a `produce`/`product`. Kde nic nebylo, je `ostatni`
   (57×). Kozí farmy (Žofín, Nový Dvůr) zůstaly `ostatni`, i když nejspíš prodávají sýry. U Nového Dvora
   to SVS potvrzuje (`duplicita_svs_kategorie: mleko`).
4. **Velké mlékárny.** 6 podnikových prodejen a bister (Madetka 2×, Tatra, Bohemilk, Laktos, Milko)
   nemá s farmou nic společného. Jsou označené v `upozorneni`.
5. **Včelařské potřeby.** 4 místa jsou spíš obchody s potřebami pro včelaře (Vydra, Škarecký, Trubec.cz,
   VšeProVčelařství.cz).
6. **Soukromé osoby (`soukroma_osoba: true`): 18.** Název je jméno člověka (Libor Vojtěch, Smetanovi …),
   nebo je název jen popisný a provozovatel je člověk, nebo jde o bezejmenného včelaře s adresou domu.
   Web ukazuje soukromé chovatele jen podle obce, bez jména a ulice. U těchhle míst by to mělo platit taky.
   Heuristika je stejná jako `je_fyzicka_osoba` v `_sourcing_data.py`, jen rozšířená.
7. **Drobnosti:** 4× `fixme` v OSM, 1 místo s `construction_date` 2026-10-31 (možná ještě neotevřené),
   1 „Mléčný automat“ s `vending=sweets` (mléčné výrobky, ne syrové mléko), 1 sezónní samosběr.
   Otevírací doby jsou v syntaxi OSM (`Mo-Fr 08:00-17:00`), pro web je bude potřeba přeložit.
   Datum ověření (`check_date`) má jen asi 23 míst, u ostatních není poznat, jak jsou údaje čerstvé.
8. **Licence.** Data OSM jsou pod ODbL 1.0. Když se vloží do `data.json`, je potřeba na mapě uvést
   „© přispěvatelé OpenStreetMap“ s odkazem na licenci. Taky upravit větu na právní stránce
   (`_postav.py` ř. 868, z něj se staví `pravni.html`), že místa pocházejí jen z registrů SVS. Spojená databáze se podle ODbL
   musí dát k dispozici pod stejnou licencí.

## Pole v `osm-cz.json`

Vždy: `osm` (node/… nebo way/…), `nazev`, `lat`, `lon` (4 desetinná místa), `kategorie`, `typ`, `obec`,
`okres`, `kraj`, `obec_urcena`, `obec_v_mape`.
Jen když je hodnota: `adresa`, `web` (website, contact:website, url, jinak Facebook), `oteviraci_doba`,
`produkty` (produce/product/vending/food převedené do češtiny), `popis`, `nazev_generovany`, `obec_osm`,
`soukroma_osoba`, `upozorneni`, `duplicita_svs` + `duplicita_svs_duvod` + `duplicita_svs_kategorie`,
`mozna_duplicita_svs` + `mozna_duplicita_duvod`, `duplicita_osm`.
