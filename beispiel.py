#!/usr/bin/env python3
"""Spielt einen Fall aus den gespeicherten Modellantworten lesbar auf der Konsole durch.

Eingang -> vom Modell gelesene Felder -> Prüfschritte des Codes -> Entscheidung.
Es wird kein Modell aufgerufen und keine Datei geschrieben.

Aufruf:  python3 beispiel.py F01         (deutsche Beschriftung)
         python3 beispiel.py F01 --en    (englische Beschriftung, die Inhalte bleiben deutsch)
         python3 beispiel.py --liste     (alle Fälle mit Entscheidung)
"""
import json, pathlib, sys

sys.dont_write_bytecode = True   # auch kein __pycache__: dieser Aufruf schreibt nichts

import pipeline  # noqa: E402

HIER = pathlib.Path(__file__).parent

TEXTE = {
    "de": {
        "fall": "Fall", "vertrag": "Vertrag", "seriennr": "Seriennummer", "kaufpreis": "Kaufpreis",
        "gekauft": "gekauft", "beginn": "Vertragsbeginn",
        "eingang": "1 · Eingang am", "meldung": "Schadenmeldung", "beleg": "Beleg", "kein_beleg": "(kein Beleg eingereicht)",
        "gelesen": "2 · Vom Modell gelesen", "gespeichert": "gespeicherte Antwort", "modell": "Modell",
        "feld": "Feld", "wert": "Wert", "zitat": "Wörtliches Zitat", "positionen": "Positionen",
        "geprueft": "3 · Vom Code geprüft (in dieser Reihenfolge, ohne Modell)",
        "status": {"gruen": "grün", "gelb": "gelb", "rot": "rot"},
        "entscheidung": "4 · Entscheidung",
        "wort": {"auszahlen": "automatisch auszahlen", "ablehnen": "Ablehnung vorschlagen", "an_mensch": "an einen Menschen"},
        "betrag": "Betrag", "paragraf": "Grundlage", "gruende": "Gründe", "berechnet": "berechnet wären",
        "soll": "Soll laut faelle.json", "getroffen": "getroffen", "verfehlt": "verfehlt",
        "brief": "5 · Entwurf des Schreibens", "kein_brief": "kein Entwurf: Über diesen Fall entscheidet ein Mensch",
        "brief_fehlt": "kein gespeicherter Entwurf vorhanden",
        "hinweis": "Das ist ein Vorschlag. Diese Vorführung zahlt nichts aus und versendet nichts.",
        "reihenfolge": "Geprüft wurden alle Fälle in der Reihenfolge des Eingangs, damit die Prüfung auf doppelte Belegnummern gilt.",
        "unbekannt": "Unbekannter Fall {id}. Vorhanden: {alle}",
        "fehlt": "{datei} fehlt in lauf/. Dieses Skript ruft kein Modell auf.",
        "aufruf": "Aufruf: python3 beispiel.py F01 [--en]   oder   python3 beispiel.py --liste",
    },
    "en": {
        "fall": "Case", "vertrag": "Contract", "seriennr": "serial number", "kaufpreis": "purchase price",
        "gekauft": "bought", "beginn": "cover starts",
        "eingang": "1 · Received on", "meldung": "Claim message (Schadenmeldung)", "beleg": "Receipt (Beleg)",
        "kein_beleg": "(no receipt submitted)",
        "gelesen": "2 · Read by the model", "gespeichert": "stored answer", "modell": "model",
        "feld": "Field", "wert": "Value", "zitat": "Verbatim quote", "positionen": "Line items (positionen)",
        "geprueft": "3 · Checked by code (in this order, no model involved)",
        "status": {"gruen": "green", "gelb": "yellow", "rot": "red"},
        "entscheidung": "4 · Decision",
        "wort": {"auszahlen": "pay out automatically", "ablehnen": "propose rejection", "an_mensch": "hand over to a human"},
        "betrag": "amount", "paragraf": "basis", "gruende": "reasons", "berechnet": "calculated amount would be",
        "soll": "Expected value in faelle.json", "getroffen": "matched", "verfehlt": "missed",
        "brief": "5 · Draft letter to the customer", "kein_brief": "no draft: a human decides this case",
        "brief_fehlt": "no stored draft available",
        "hinweis": "This is a proposal. This demo pays nothing out and sends nothing.",
        "reihenfolge": "All cases were checked in order of receipt so that the duplicate receipt number check applies.",
        "unbekannt": "Unknown case {id}. Available: {alle}",
        "fehlt": "{datei} is missing in lauf/. This script never calls a model.",
        "aufruf": "Usage: python3 beispiel.py F01 [--en]   or   python3 beispiel.py --liste",
    },
}

LESE_FELDER = [("schadentag", "schadentag_beleg"), ("schadenart", "schadenart_beleg"), ("beleg_vorhanden", None),
               ("beleg_typ", None), ("belegnummer", "belegnummer_beleg"), ("belegdatum", "belegdatum_beleg"),
               ("seriennummer_beleg_wert", "seriennummer_beleg"), ("gesamtbetrag", "gesamtbetrag_beleg"),
               ("anweisung_im_dokument", "anweisung_beleg")]


def lade_faelle() -> list:
    return json.loads((HIER / "faelle.json").read_text(encoding="utf-8"))


def gespeichert(fall_id: str, t: dict) -> dict:
    """Liest die gespeicherte Modellantwort. Fehlt sie, endet der Aufruf; ein Modell wird nie gefragt."""
    datei = HIER / "lauf" / f"{fall_id}_gelesen.json"
    if not datei.exists():
        sys.exit(t["fehlt"].format(datei=datei.name))
    return json.loads(datei.read_text(encoding="utf-8"))


def durchlauf(sprache: str = "de") -> dict:
    """Prüft alle Fälle wie pipeline.main() in der Reihenfolge des Eingangs. Gibt je Fall (Fall, Gelesenes, Ergebnis) zurück."""
    t = TEXTE[sprache]
    faelle = lade_faelle()
    gelesen = [gespeichert(f["id"], t) for f in faelle]
    gesehen, aus = {}, {}
    for f, x in sorted(zip(faelle, gelesen), key=lambda p: p[0]["eingang"]):
        aus[f["id"]] = (f, x, pipeline.pruefe(f, x, gesehen))
    return {f["id"]: aus[f["id"]] for f in faelle}


def _block(text: str) -> list:
    return [("    | " + zeile).rstrip() for zeile in text.splitlines()]


def _wert(w) -> str:
    return "null" if w is None else json.dumps(w, ensure_ascii=False) if isinstance(w, bool) else str(w)


def darstellung(fall: dict, x: dict, erg: dict, sprache: str = "de") -> str:
    """Der Text für die Konsole. Reine Funktion: liest nur den Briefentwurf, schreibt nichts."""
    t, v, z = TEXTE[sprache], fall["vertrag"], []
    z.append(f"{t['fall']} {fall['id']} · {fall['titel']}")
    z.append(f"{t['vertrag']} {v['vertragsnr']} · {v['geraet']} · {t['seriennr']} {v['seriennr']} · "
             f"{t['kaufpreis']} {pipeline.eur(v['kaufpreis'])} · {t['gekauft']} {v['kaufdatum']} · {t['beginn']} {v['vertragsbeginn']}")
    z += ["", f"{t['eingang']} {fall['eingang']}", f"  {t['meldung']}:"] + _block(fall["meldung"])
    z += [f"  {t['beleg']}:"] + (_block(fall["beleg"]) if fall["beleg"] else ["    " + t["kein_beleg"]])

    z += ["", f"{t['gelesen']} ({t['gespeichert']} lauf/{fall['id']}_gelesen.json, {t['modell']} {x.get('_modell')})"]
    for feld, zitat in LESE_FELDER:
        z.append(f"  {feld} = {_wert(x.get(feld))}")
        if zitat and x.get(zitat):
            z.append(f"      {t['zitat']} ({zitat}): „{x[zitat]}“")
    positionen = [p for p in x.get("positionen") or [] if p.get("text")]
    z.append(f"  {t['positionen']}: " + (" · ".join(f"{p['text']} {pipeline.eur(p['betrag'])}" for p in positionen) or "null"))

    z += ["", t["geprueft"]]
    for nr, s in enumerate(erg["schritte"], 1):
        par = f" ({s['paragraf']})" if s["paragraf"] else ""
        z.append(f"  {nr}. [{t['status'][s['status']]}] {s['name']}{par}: {s['detail']}")

    z += ["", t["entscheidung"]]
    zeile = f"  {erg['entscheidung']} ({t['wort'][erg['entscheidung']]})"
    if erg["entscheidung"] == "auszahlen":
        zeile += f" · {t['betrag']} {pipeline.eur(erg['betrag'])}"
    elif erg["entscheidung"] == "ablehnen":
        zeile += f" · {t['paragraf']} {erg['paragraf']}"
    else:
        zeile += f" · {t['gruende']}: {', '.join(erg['gruende'])}"
        if erg["betrag"] is not None:
            zeile += f" · {t['berechnet']} {pipeline.eur(erg['betrag'])}"
    z.append(zeile)
    g = fall["gold"]
    soll = g["entscheidung"] + (f" {pipeline.eur(g['betrag'])}" if g["betrag"] is not None else "") \
        + (f" {g['paragraf']}" if g["paragraf"] else "") + (f" ({', '.join(g['gruende'])})" if g["gruende"] else "")
    ok = pipeline.messe(fall, x, erg)["entscheidung_ok"]
    z.append(f"  {t['soll']}: {soll} · {t['getroffen'] if ok else t['verfehlt']}")

    z += ["", t["brief"]]
    datei = HIER / "lauf" / f"{fall['id']}_brief.txt"
    if erg["entscheidung"] == "an_mensch":
        z.append("  " + t["kein_brief"])
    elif datei.exists():
        z += [f"  lauf/{datei.name}:"] + _block(datei.read_text(encoding="utf-8"))
    else:
        z.append("  " + t["brief_fehlt"])
    z += ["", t["hinweis"], t["reihenfolge"]]
    return "\n".join(z)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else list(argv)
    sprache = "en" if "--en" in argv else "de"
    t = TEXTE[sprache]
    ids = [a for a in argv if not a.startswith("--")]
    unbekannt = [a for a in argv if a.startswith("--") and a not in ("--en", "--liste")]
    if unbekannt or ("--liste" in argv) == bool(ids) or len(ids) > 1:
        sys.exit(t["aufruf"])
    alle = durchlauf(sprache)
    if "--liste" in argv:
        for fall_id, (f, _, e) in alle.items():
            print(f"{fall_id}  {e['entscheidung']:<10} {f['titel']}")
        return 0
    fall_id = ids[0].upper()
    if fall_id not in alle:
        sys.exit(t["unbekannt"].format(id=ids[0], alle=", ".join(alle)))
    print(darstellung(*alle[fall_id], sprache))
    return 0


if __name__ == "__main__":
    sys.exit(main())
