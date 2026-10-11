#!/usr/bin/env python3
"""Vytáhne překladové bloky (odstavce, nadpisy, položky, popisky) z českých stránek pro anglickou verzi.
Blok = vnitřní HTML prvku, který nemá uvnitř další blokový prvek. Klíč je přesně ten český HTML řetězec."""
import re, json, sys, html
from html.parser import HTMLParser

BLOKOVE = {"p", "h1", "h2", "h3", "h4", "li", "blockquote", "figcaption", "summary", "button", "a", "span", "b", "td", "th", "label", "title", "option", "strong", "em"}
KONTEJNERY = {"div", "section", "article", "ul", "ol", "main", "header", "footer", "nav", "figure", "details", "table", "tr", "aside", "form"}

def bloky(text):
    """vrátí seznam (tag, innerHTML) pro nejmenší bloky s českým textem"""
    out = []
    # vezmi p/h/li/blockquote/figcaption/summary/td/th/label/title s jejich obsahem (nehladově, bez vnoření stejného tagu)
    for tag in ("title", "h1", "h2", "h3", "h4", "p", "li", "blockquote", "figcaption", "summary", "td", "th", "label", "button"):
        for m in re.finditer(r"<%s(?:\s[^>]*)?>(.*?)</%s>" % (tag, tag), text, flags=re.S):
            inner = m.group(1).strip()
            if re.search(r"<(p|div|ul|ol|li|h[1-4]|section|figure|blockquote|table|details)\b", inner):
                continue
            if re.search(r"[A-Za-zÁ-žá-ž]", re.sub(r"<[^>]+>", "", inner)):
                out.append((tag, inner))
    # atributy s textem
    for m in re.finditer(r'\b(alt|aria-label|placeholder|title)="([^"]*[A-Za-zÁ-ž][^"]*)"', text):
        out.append(("@" + m.group(1), m.group(2)))
    for m in re.finditer(r'<meta (?:name|property)="(description|og:title|og:description)" content="([^"]+)"', text):
        out.append(("@meta", m.group(2)))
    return out

if __name__ == "__main__":
    vse = {}
    for f in sys.argv[1:]:
        t = open(f, encoding="utf-8").read()
        t = re.sub(r"<script.*?</script>", "", t, flags=re.S)
        t = re.sub(r"<style.*?</style>", "", t, flags=re.S)
        for tag, inner in bloky(t):
            vse.setdefault(inner, {"tag": tag, "stranky": []})
            if f not in vse[inner]["stranky"]:
                vse[inner]["stranky"].append(f)
    json.dump(vse, open("_preklad/_bloky-cz.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    znaku = sum(len(re.sub(r"<[^>]+>", "", k)) for k in vse)
    print("bloku:", len(vse), "znaku textu:", znaku)
    from collections import Counter
    print(Counter(p for v in vse.values() for p in v["stranky"]))
