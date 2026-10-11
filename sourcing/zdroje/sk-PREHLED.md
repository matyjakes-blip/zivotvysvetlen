# Slovensko pro sourcing mapu: přehled dat

Staženo 11. 10. 2026. Vznikly jen datové soubory v téhle složce, do mapy zatím nic není zapojené
(`data.json`, HTML ani generátory webu se neměnily). Spojení s mapou udělá jiná session.

| soubor | co obsahuje |
|---|---|
| `osm-sk.json` | 245 míst z OpenStreetMap (farmářské obchody, mlékomaty, mléčné prodejny, med), stejný formát jako `osm-cz.json` |
| `svps-sk.json` | 590 míst ze 6 úředních seznamů ŠVPS SR + 34 vyřazených (pole `vyrazene`) |
| `obce-sk.csv` | 2 887 slovenských obcí: `obec,okres,kraj,psc,lat,lon` + navíc `kod,souradnice,obyvatel` |

## Zdroje

**OpenStreetMap** přes `https://overpass-api.de/api/interpreter` (stav dat OSM 2026-10-11 11:57 UTC):

1. *Místa:* stejné tagy jako u Česka uvnitř hranice SR: `shop=farm`, `shop=dairy`, `shop=honey`,
   `craft=beekeeper`, `vending~milk` a automaty s „mléko/mlieko/mliečn…“ v názvu. Dotaz je doslova v `osm-sk.json` → `dotaz`.
2. *Obec každého bodu:* `is_in` na souřadnicích bodu (u cest střed), hranice obce `admin_level=8`, Bratislava a Košice
   jako celé město (`admin_level=5`), okres `6`, kraj `4`. Popis dotazu je v `dotaz_obce`.
   Česká varianta (`foreach` + `is_in` přes všechny uzly cest) na přetíženém serveru opakovaně padala na 504 a timeout,
   proto je dotaz rozepsaný na jeden řádek na bod. Všech 245 míst má obec podle hranic v OSM.
3. *Obce:* kraje (`admin_level=4`, `ref` SK0…) → okresy (`6`, role `subarea`) → obce (`8`) + Bratislava a Košice.
   Souřadnice a PSČ z uzlu obce (role `label`, tag `postal_code`). 4 obce okres jako subarea nemá (Krivá, Gerlachov,
   Bzenov, Teriakovce), ty jsem doplnil přes `is_in`.

**ŠVPS SR**, živé seznamy na `https://zoznamy.svps.sk/default.asp?typ=zoznam-food` (každý seznam jedna stránka, stažené
jednou s pauzami):

| seznam | URL (parametry za `default.asp?`) | v seznamu | převzato | kategorie, typ |
|---|---|---:|---:|---|
| Predaj malých množstiev vajec konečnému spotrebiteľovi | `typ=zoznam-food-schvalene&Zoznamy=853&Sekcia=817` | 96 | 96 | vejce, Malý prodej vajec |
| Prevádzkarne pre zber a balenie medu | `typ=zoznamy-schvalene-n&Zoznamy=nizkokap&Sekcia=18` | 37 | 37 | med, Sběr a balení medu |
| Surové mlieko a mliečne výrobky, spracovateľské prevádzkarne | `…&Sekcia=809&Cinnost=PP` | 292 | 277 | mleko, Salaš / Mlékárna nebo sýrárna |
| Mäso domácich kopytníkov, bitúnky | `…&Sekcia=801&Cinnost=SH` | 110 | 64 | maso, Malá jatka (nízká kapacita) |
| Zverina z voľne žijúcej zveri, manipulácia so zverou | `…&Sekcia=804&Cinnost=GHE` | 31 | 28 | zverina, Zpracovna zvěřiny |
| Zberné strediská pre ulovenú voľne žijúcu zver | `typ=zoznam-food-schvalene&Zoznamy=ostatne&Sekcia=21` | 103 | 88 | zverina, Sběrné středisko ulovené zvěře |

Celé URL jsou v `svps-sk.json` → `seznamy[].url` i u každého místa (`zdroj_url`).
Datová sada ŠVPS `https://svps.sk/dokumenty/GOV/Prevadzky_Potraviny.xml` (z `https://svps.sk/datasety/`, naposledy
13. 11. 2024) posloužila jen k doplnění ulice a PSČ tam, kde živý seznam uvádí jen obec (165 míst).

**Co jsem ze ŠVPS záměrně nebral:** velká jatka (45 bez přípony L), rozrábkárny (230), masné výrobky a polotovary
(216 + 88 + 46), třídírny vajec (46, průmysl), drůbeží jatka (7, HYZA a spol.), zpracovny ryb (11 + 30), jatka farmové
zvěře (2), mléčná sběrná střediska (6). Z veterinárních seznamů registr akvakultury (197 rybníků a líhní) a registr
farmových chovů zvěře (836): jsou to chovy, ne místa prodeje. Kdyby se hodily ryby, registr akvakultury je nejbližší kandidát.

## Počty: OpenStreetMap (`osm-sk.json`)

**Celkem 245 míst** (196 uzlů, 49 cest) ve 149 obcích.

| typ | počet | s názvem z OSM | s webem | s otevírací dobou |
|---|---:|---:|---:|---:|
| Farmářský obchod | 88 | 73 | 35 | 37 |
| Med | 78 | 32 | 15 | 10 |
| Mlékomat | 47 | 18 | 0 | 9 |
| Mléčná prodejna | 32 | 27 | 8 | 16 |
| **celkem** | **245** | **150** | **58** | **72** |

Adresa z `addr:*` u 22 míst, produkty u 57, popis u 9. 13 mlékomatů má výslovně `drink:raw_milk=yes`.

**Kategorie:** mleko 84, med 79, ostatni 61, zelenina 15, vejce 4, ryby 1 (Pstruhová farma), maso 1.
Farmářské obchody: ostatni 61, zelenina 15, mleko 5, vejce 4, ryby 1, med 1, maso 1.

| kraj | celkem | Med | Farmářský obchod | Mlékomat | Mléčná prodejna |
|---|---:|---:|---:|---:|---:|
| Prešovský | 47 | 19 | 13 | 10 | 5 |
| Žilinský | 38 | 8 | 10 | 10 | 10 |
| Trenčiansky | 36 | 9 | 15 | 7 | 5 |
| Bratislavský | 31 | 9 | 17 | 4 | 1 |
| Košický | 31 | 19 | 8 | 0 | 4 |
| Banskobystrický | 22 | 6 | 7 | 7 | 2 |
| Nitriansky | 22 | 3 | 12 | 5 | 2 |
| Trnavský | 18 | 5 | 6 | 4 | 3 |

`obec_v_mape` je u všech `false`, protože `data.json` zatím obsahuje jen české obce. Proto je navíc `obec_v_svps_sk`:
157 OSM míst leží v obci, kde je i záznam ze ŠVPS.

## Počty: ŠVPS (`svps-sk.json`)

**Celkem 590 míst ve 429 obcích.**

| typ | počet | z toho fyzické osoby |
|---|---:|---:|
| Salaš (ovčí sýry, bryndza) | 143 | 52 |
| Mlékárna nebo sýrárna | 134 | 25 |
| Malý prodej vajec | 96 | 55 |
| Sběrné středisko ulovené zvěře | 88 | 15 |
| Malá jatka (nízká kapacita) | 64 | 5 |
| Sběr a balení medu | 37 | 11 |
| Zpracovna zvěřiny | 28 | 2 |
| **celkem** | **590** | **165** |

**Kategorie:** mleko 277, zverina 116, vejce 96, maso 64, med 37.

| kraj | celkem | mleko | zverina | vejce | maso | med |
|---|---:|---:|---:|---:|---:|---:|
| Žilinský | 128 | 90 | 5 | 22 | 8 | 3 |
| Prešovský | 111 | 60 | 16 | 15 | 14 | 6 |
| Banskobystrický | 110 | 49 | 38 | 14 | 7 | 2 |
| Trenčiansky | 85 | 27 | 22 | 24 | 11 | 1 |
| Košický | 63 | 30 | 13 | 7 | 8 | 5 |
| Trnavský | 44 | 15 | 8 | 10 | 5 | 6 |
| Nitriansky | 34 | 4 | 9 | 3 | 10 | 8 |
| Bratislavský | 15 | 2 | 5 | 1 | 1 | 6 |

**Vyřazeno 34** (pole `vyrazene`, jen firmy): 12 průmyslových mlékáren (Tami, Milsy, Euromilk, Levické mliekárne,
Meggle, Syráreň Bel, Savencia, Tatranská mliekareň, 2× Syráreň Havran, Zvolenská mliekareň, Milk-Agro),
1 výrobna nanuků (podle názvu), 1 logistická firma, 3 velkozpracovatelé zvěřiny (Italzver, Karpatia Wilde, Tauris),
14 výkupních míst těchže velkozpracovatelů (Italzver 11×, Tauris 2×, Berbera) a 3 provozovny s pozastavenou činností.

## Fyzické osoby

- **ŠVPS: 165 z 590** má `fyzicka_osoba: true`. Pravidlo: v názvu je křestní jméno + příjmení (nebo zkratka SHR,
  samostatne hospodáriaci roľník) a žádná právní forma (s.r.o., a.s., družstvo, š.p., spoločnosť, združenie …).
  Na rozdíl od české heuristiky se osoba označí i tehdy, když má v názvu farmu („Erika Kováčová, SHR, Farma plná lásky“),
  protože jde pořád o člověka a jinak by web ukázal jeho jméno. U 68 z nich je `nazev_bez_osoby` (např. „Farma plná lásky“,
  „Ranč ORTAŠE“, „Salaš Brezina“), když obchodní název neobsahuje příjmení. Web může ukázat ten, nebo jen „Soukromý chovatel“.
  Ručně: 2 výjimky (příjmení bez křestního jména „Mádr“ a záznam, kde registr místo jména uvádí jen adresu).
- **Adresy fyzických osob se do souboru nepíšou** (`adresa: ""`, `adresa_skryta: true`, 94 záznamů). Zůstává obec a PSČ.
  Jméno zůstává v `nazev`, protože ho ŠVPS sám zveřejňuje a zadání ho chtělo; adresa bydliště majitele (u sběrných
  středisek zvěře je v registru) se nepřebírá vůbec.
- **OSM: 10 míst** má `soukroma_osoba: true` (jméno člověka v názvu, popisný název + člověk jako provozovatel,
  nebo bezejmenný včelař s adresou).

## Obce (`obce-sk.csv`) a párování

- 2 887 obcí z OSM (2 881 obcí a měst + Bratislava a Košice jako celek). Úřední počet je 2 890, tři obce v OSM
  chybějí nebo jsou jinak označené; které, jsem neověřoval. 72 okresů (Bratislava I až V a Košice I až IV jsou sloučené
  do „Bratislava“ a „Košice“). Souřadnice všech obcí jsou z uzlu obce v OSM, ne ze středu hranice.
- **PSČ má 2 859 obcí.** Bez PSČ je 28 velkých měst, která jich mají víc (Banská Bystrica, Nitra, Prešov, Žilina …).
  Bratislava a Košice mají v `psc` jen PSČ svých městských částí oddělená středníkem, ne všechna PSČ města.
- **ŠVPS → obec: nenapárováno 0 z 590.** Způsob je u každého místa v `obec_urcena`:
  název obce + okres 527, název obce 19 (Bratislava, Košice, obec jediná v SR), část názvu obce 26
  („Považská Bystrica - Práznov“, „Salaš Zliechov“), obec z adresy nebo názvu 6, část obce podle uzlu `place` v OSM 6
  (Milochov → Považská Bystrica, Starý Smokovec → Vysoké Tatry, Oravice → Tvrdošín), podobný název 4
  (překlepy: „Kysudké Nové Mesto“, „Plavecký Štvrtrok“, „Svätuša“, „Koválovce“), PSČ sdílené víc obcemi 1
  (Šarpanec → Spišská Belá, odhad podle největší obce) a sídlo provozovatele 1 („Kamenný vrch“ Vojenských lesov,
  nejspíš ve vojenském obvodu Lešť, posazeno do Pliešovců). Původní text je v `mesto_registr` a `okres_registr`.
- **OSM → obec:** všech 245 podle hranic obce v OSM. K bodu jsou navíc `obec_lat`/`obec_lon` z `obce-sk.csv`
  (střed obce pro seskupení), `lat`/`lon` zůstávají přesné souřadnice místa.

## Duplicity

- **Uvnitř OSM (`duplicita_osm`): 9.** Hlavně dvojice a trojice včelínů do 50 m (Svit, Poprad, Spišská Teplica, Suché,
  Stará Halič, Liptovské Sliače), dva bezejmenné farmářské obchody v Bratislavě a mlékomat v Ružomberku zakreslený dvakrát.
- **OSM proti ŠVPS: 8 silných (`duplicita_svps`), 4 možné (`mozna_duplicita_svps`).** Jen ve stejné obci a stejné
  kategorii (u farmářských obchodů s kategorií ostatni libovolné). Silné: Salaš Beniky, Agrofarma Baranec, Salaš SPDP Lúžňan,
  Predajňa Madonan, Podniková predajňa Červený Kameň (Agrofarma), Predajňa PD Vlára Nemšová, Včelco, Zlatý nektár.
  Mlékomaty se neporovnávají, ŠVPS je nevede.
- **Uvnitř ŠVPS (`stejny_provozovatel_v_obci`): 15.** Stejný provozovatel ve stejné obci ve dvou seznamech nebo na dvou
  místech (Farma Lomnička jako jatka i zpracovna zvěřiny, Lesy SR se dvěma sběrnými místy v Prašicích). Nejsou to chyby.

## Ukázka (jen firmy)

| název | typ | kat. | obec, kraj | zdroj |
|---|---|---|---|---|
| Salaš Strednica | Salaš (ovčí sýry, bryndza) | mleko | Ždiar, Prešovský | ŠVPS 807 S |
| Farma Toporec – mini mliekareň | Mlékárna nebo sýrárna | mleko | Toporec, Prešovský | ŠVPS 4-7-128 |
| Výroba mlieka a mliečnych výrobkov, predaj mlieka z dvora | Mlékárna nebo sýrárna | mleko | Kežmarok, Prešovský | ŠVPS 4-7-813 |
| Bitúnok, rozrábkareň a predaj z dvora na farme Vislanka | Malá jatka (nízká kapacita) | maso | Vislanka, Prešovský | ŠVPS 7106L |
| Mangalica farma, s.r.o. | Malá jatka (nízká kapacita) | maso | Hurbanovo, Nitriansky | ŠVPS 4016L |
| Vajíčka z Pandiakovho dvora | Malý prodej vajec | vejce | Predajná, Banskobystrický | ŠVPS BR1108PR |
| Včelia farma MEDAR | Sběr a balení medu | med | Bardejov, Prešovský | ŠVPS 257 |
| Kozia farma Becka | Mléčná prodejna | mleko | Šaštín-Stráže, Trnavský | OSM, koziafarmabecka.sk |
| Salaš Záturčie | Mléčná prodejna | mleko | Martin, Žilinský | OSM, Tu-Sa 09:00-15:00 |
| Gazdovský dvor Branovo | Farmářský obchod | ostatni | Branovo, Nitriansky | OSM, gazdovskydvorbranovo.sk |

## Problémy s kvalitou dat

1. **ŠVPS jsou hlavně schválené provozovny, ne prodejní místa.** Prodej přímo spotřebiteli zaručuje jen seznam malého
   prodeje vajec (podle NV SR 360/2011 chovatel od 50 nosnic, prodává i na trhu). U jatek, zpracoven zvěřiny a sběrných
   středisek je `upozorneni`, že prodej veřejnosti není ověřený. Sběrná střediska zvěře (88) jsou místa, kam myslivci
   a lesy vozí úlovky; jako zdroj zvěřiny dávají smysl, jako „obchod“ ne.
2. **Salaš a malá jatka jsou odvozené z čísla schválení.** ŠVPS příponu nevysvětluje. Čísla s „S“ v mlékárnách jsou
   ze 141 ze 142 jen ovce a 92 má „salaš“ v názvu, proto typ Salaš (143 = 142 s příponou + 1 podle názvu).
   Přípona „L“ u jatek odpovídá názvům typu „bitúnok s malým objemom výroby“, proto „nízká kapacita“ (`nizka_kapacita`).
3. **Okres v registru je někdy okres veterinární správy, ne skutečný** (Prečín je v seznamu pod Púchovem, Ladce pod
   Púchovem, Slatvina pod Gelnicí). Párování to toleruje, u obcí se stejným názvem ve dvou okresech to rozhoduje kraj.
4. **Adresy a PSČ.** Živé seznamy mají jen obec. Ulice z datové sady 2024 je u 165 míst (u fyzických osob se nepíše) a může být zastaralá.
   Datová sada má i chyby (Agromliekáreň Debraď s PSČ 37901). Většina mlékáren nemá ulici vůbec.
5. **Větší mlékárny.** Kromě 12 vyřazených zůstalo 9 větších (staré číslo EU nebo 4-6-…, např. Koliba a.s., Orava-Milk,
   Farma Majcichov, Agrofarma Červený Kameň) s upozorněním, protože některé mají podnikovou prodejnu.
6. **Med v ŠVPS je jen 37 provozoven na sběr a balení**, 20 z nich jsou s.r.o. Drobní včelaři, kteří med jen
   stáčejí doma, v tomhle seznamu nejsou.
7. **OSM: včelaři nejsou prodejny.** 51 ze 78 „Med“ má upozornění „jen craft=beekeeper, prodej medu neověřen“
   (bez otevírací doby a bez slova prodej/med v názvu). 2 jsou spíš včelařské potřeby nebo vzdělávací centrum.
8. **OSM: mlékomaty jsou chudé.** 29 ze 47 nemá název, žádný nemá web, 9 má otevírací dobu, `check_date` má v celé
   vrstvě jen 12 míst. Je to hlavně poloha na metr.
9. **OSM: `shop=farm` se používá volně.** 3 tržnice, 5 samosběrů (jahody, jablka, meruňky), pojízdná prodejna
   (Farmfoods) a několik obchodů, u kterých z OSM není poznat, jestli jde o farmu. 4 firemní prodejny velkých mlékáren (Rajo/Meggle, Levmilk,
   Milk Agro, Bánovecká mliekareň) a 1 „mléčná prodejna“, která je podle názvu lahůdkářství s rybami. Vše v `upozorneni`.
   Kategorie farmářských obchodů je podle klíčových slov; kde nic nebylo, zůstalo `ostatni` (61).
10. **Licence a zveřejnění.** OSM je pod ODbL 1.0, na mapě je potřeba uvést „© přispěvatelé OpenStreetMap“ a spojenou
    databázi sdílet pod stejnou licencí (stejně jako u Česka). ŠVPS je veřejný úřední rejstřík bez výslovné licence.
    Složka `sourcing/zdroje/` je součástí webového repozitáře, takže `svps-sk.json` se jmény fyzických osob bude veřejně
    stažitelný, stejně jako dnešní české `svs-*.json`. Adresy fyzických osob v něm nejsou.

## Co veřejně k dispozici není

- **Syrové mléko ze dvora.** Přímý prodej syrového mléka na Slovensku podléhá registraci u regionální veterinární správy
  (NV SR 360/2011), ale veřejný seznam takových prodejců jsem na zoznamy.svps.sk ani v datových sadách nenašel.
  Jediná zmínka je jedna mlékárna s názvem „…predaj mlieka z dvora“ (Kežmarok).
- **Úřední seznam mlékomatů** neexistuje. OSM má 47, soubor Slovenského zväzu výrobcov mlieka (114 automatů) je z roku
  2019 a nestahoval jsem ho.
- **Drobní producenti masa, drůbeže a medu prodávající malá množství** (NV SR 360/2011) veřejný seznam nemají,
  kromě vajec. Totéž ryby ze sádek: registr akvakultury jsou chovy, ne prodejní místa.
- **Ulice a kontakty**: živé seznamy ŠVPS je neuvádějí, telefon ani web nemá žádný záznam.
- Nejširší neúřední pokrytí Slovenska mají soukromé adresáře (predajzdvora.sk svazu EKOTREND, FarMapa), ty se dají jen
  oslovit, ne převzít.

## Pole

**`osm-sk.json`** stejně jako `osm-cz.json`: `osm`, `nazev`, `lat`, `lon`, `kategorie`, `typ`, `adresa`, `obec`, `okres`,
`kraj`, `obec_urcena`, `obec_v_mape`, `web`, `oteviraci_doba`, `produkty`, `popis`, `nazev_generovany`, `soukroma_osoba`,
`upozorneni`, `duplicita_osm`, `duplicita_svps` + `duplicita_svps_duvod` + `duplicita_svps_kategorie`,
`mozna_duplicita_svps` + `mozna_duplicita_duvod`. Navíc `obec_lat`, `obec_lon`, `obec_v_svps_sk`.

**`svps-sk.json`**: `nazev`, `adresa`, `obec`, `okres`, `kraj`, `psc`, `lat`, `lon` (střed obce), `kategorie`, `typ`,
`registr_cislo` (u sběrných středisek zvěře registr číslo neuvádí), `zdroj_url`, `seznam`, `fyzicka_osoba`.
Podle potřeby: `nazev_bez_osoby`, `adresa_skryta`, `adresa_zdroj`, `mesto_registr`, `okres_registr`, `obec_urcena`,
`druhy` (skot, ovce, kozy …), `nizka_kapacita`, `poznamka_registr`, `stejny_provozovatel_v_obci`, `upozorneni`.
Kategorie `zverina` v mapě zatím není mezi povolenými v `PRECTI-ME.md`, v `_sourcing_data.py` se ale pro české SVS už používá.

Skripty, které soubory postavily, zůstaly mimo repozitář v dočasné složce session (`scratchpad/sk/skripty`).
