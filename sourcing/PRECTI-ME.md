# Sourcing mapa — jak ji plnit

Mapa na `zivotvysvetlen.cz/sourcing` se kreslí ze dvou souborů v téhle složce.
Nic se nenačítá z cizích serverů, takže mapa nikomu neposílá IP adresy návštěvníků
a na právní stránce kvůli ní nic přibývat nemusí.

## Přidat místo

Otevři `mista.json` a přidej záznam do pole `mista`:

```json
{
 "nazev": "Farma U Nováků",
 "obec": "Kostelec nad Labem",
 "lat": 50.2274,
 "lon": 14.5861,
 "kategorie": "mleko",
 "co": "Syrové kravské mléko, máslo, tvaroh. Prodej z farmy ve středu a v sobotu.",
 "odkaz": "https://priklad.cz",
 "pozn": "Volá se den dopředu."
}
```

- **lat a lon** vezmi z Mapy.cz nebo Google Maps: pravým tlačítkem na místo, souřadnice se zkopírují. Stačí čtyři desetinná místa.
- **kategorie** musí být jedna z: `mleko`, `maso`, `vejce`, `tuky`, `ryby`, `med`, `minerals`, `zelenina`, `ostatni`.
- **odkaz** a **pozn** jsou nepovinné.

Pak v kořeni webu spusť `python3 _postav.py` a pushni. Mapa se překreslí sama.

## Formulář na e-maily

Na stránce je dole rámeček `<!-- SEM PATRI FORMULAR -->`, kde zatím stojí jen věta.
Statický web sám e-maily sbírat neumí, potřebuje k tomu službu. **Nejjednodušší je
Notion, který už máš:** v Notionu založ formulář (New → Form), dej tam jedno pole
na e-mail, publikuj ho a pošli mi odkaz. Vložím ho na stránku a e-maily se budou
sbírat rovnou do Notionu.

Jakmile začneš e-maily sbírat, přibude na právní stránku souhlas a odhlašovací odkaz.
To udělám zároveň s tím formulářem.

## Obrysy

`obrysy.json` jsou hranice Česka a Slovenska z Natural Earth (volné dílo), převedené
na body. Měnit se nemusí.
