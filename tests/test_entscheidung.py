"""Prüft die Entscheidungslogik gegen die von Hand festgelegten Sollwerte.

Grundlage sind die gespeicherten Modellantworten in lauf/. Es wird kein Modell
aufgerufen: Der Aufruf ist für die Dauer der Tests gesperrt.
Die Sollwerte stehen in faelle.json unter "gold" und werden hier nur gelesen.

Start aus dem Projektordner:  python3 -m unittest discover -s tests -v
"""
import json
import pathlib
import sys
import unittest
from unittest import mock

WURZEL = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))
sys.dont_write_bytecode = True

import pipeline  # noqa: E402

FAELLE = json.loads((WURZEL / "faelle.json").read_text(encoding="utf-8"))
SOLL_FELDER = [("schadentag", "schadentag"), ("schadenart", "schadenart"), ("belegnummer", "belegnummer"),
               ("belegdatum", "belegdatum"), ("seriennummer_beleg", "seriennummer_beleg_wert"),
               ("gesamtbetrag", "gesamtbetrag")]


def gespeichert(fall_id: str) -> dict:
    return json.loads((WURZEL / "lauf" / f"{fall_id}_gelesen.json").read_text(encoding="utf-8"))


def entscheide_alle() -> dict:
    """Lässt den Code über alle Fälle laufen, in der Reihenfolge des Posteingangs wie in pipeline.main()."""
    gesehen, ergebnisse = {}, {}
    for fall in sorted(FAELLE, key=lambda f: f["eingang"]):
        ergebnisse[fall["id"]] = pipeline.pruefe(fall, gespeichert(fall["id"]), gesehen)
    return ergebnisse


def abweichungen(ergebnisse: dict) -> list:
    """Fall-IDs, bei denen Entscheidung, Gründe, Paragraf oder Betrag vom Soll abweichen."""
    falsch = []
    for fall in FAELLE:
        g, e = fall["gold"], ergebnisse[fall["id"]]
        betrag_gleich = (g["betrag"] is None and e["betrag"] is None) or (
            g["betrag"] is not None and e["betrag"] is not None and abs(g["betrag"] - e["betrag"]) < 0.005)
        if not (e["entscheidung"] == g["entscheidung"] and e["gruende"] == sorted(g["gruende"])
                and e["paragraf"] == g["paragraf"] and betrag_gleich):
            falsch.append(fall["id"])
    return falsch


class OhneModell(unittest.TestCase):
    def setUp(self):
        sperre = mock.patch.object(pipeline, "modell", side_effect=AssertionError("Modellaufruf im Test"))
        prozess = mock.patch.object(pipeline.subprocess, "run", side_effect=AssertionError("Prozessstart im Test"))
        sperre.start(), prozess.start()
        self.addCleanup(sperre.stop)
        self.addCleanup(prozess.stop)


class Datenstand(OhneModell):
    def test_sechzehn_faelle_mit_soll(self):
        self.assertEqual(len(FAELLE), 16)
        for fall in FAELLE:
            self.assertIn("gold", fall, fall["id"])

    def test_jede_gelesene_antwort_ist_gespeichert(self):
        for fall in FAELLE:
            self.assertTrue((WURZEL / "lauf" / f"{fall['id']}_gelesen.json").exists(), fall["id"])


class EntscheidungGegenSoll(OhneModell):
    def test_entscheidung_gruende_paragraf_betrag(self):
        ergebnisse = entscheide_alle()
        for fall in FAELLE:
            g, e = fall["gold"], ergebnisse[fall["id"]]
            with self.subTest(fall=fall["id"], titel=fall["titel"]):
                self.assertEqual(e["entscheidung"], g["entscheidung"])
                self.assertEqual(e["gruende"], sorted(g["gruende"]))
                self.assertEqual(e["paragraf"], g["paragraf"])
                if g["betrag"] is None:
                    self.assertIsNone(e["betrag"])
                else:
                    self.assertIsNotNone(e["betrag"])
                    self.assertAlmostEqual(e["betrag"], g["betrag"], places=2)

    def test_keine_auszahlung_ohne_soll_auszahlung(self):
        ergebnisse = entscheide_alle()
        for fall in FAELLE:
            if ergebnisse[fall["id"]]["entscheidung"] == "auszahlen":
                self.assertEqual(fall["gold"]["entscheidung"], "auszahlen", fall["id"])

    def test_brief_liegt_fuer_jeden_fall_ohne_menschen_vor(self):
        for fall_id, e in entscheide_alle().items():
            if e["entscheidung"] != "an_mensch":
                self.assertTrue((WURZEL / "lauf" / f"{fall_id}_brief.txt").exists(), fall_id)


class GeleseneFelderGegenSoll(OhneModell):
    def test_sechs_felder_je_fall(self):
        for fall in FAELLE:
            x = gespeichert(fall["id"])
            for soll_name, ist_name in SOLL_FELDER:
                soll, ist = fall["gold"][soll_name], x.get(ist_name)
                with self.subTest(fall=fall["id"], feld=soll_name):
                    if soll is None:
                        self.assertIn(ist, (None, ""))
                    elif isinstance(soll, float):
                        self.assertIsNotNone(ist)
                        self.assertAlmostEqual(float(ist), soll, places=2)
                    else:
                        self.assertEqual(str(ist).strip().lower(), str(soll).strip().lower())


class Gegenprobe(OhneModell):
    """Mit abgeschalteter Sicherung muss der Vergleich mit dem Soll Abweichungen zeigen."""

    def test_ohne_betragsgrenze_gibt_es_abweichungen(self):
        with mock.patch.object(pipeline, "GRENZE_AUTOMATIK", 10**9):
            self.assertTrue(abweichungen(entscheide_alle()))

    def test_ohne_auffaelligkeiten_gibt_es_abweichungen(self):
        with mock.patch.object(pipeline, "SIGNALE_AUS", True):
            self.assertTrue(abweichungen(entscheide_alle()))

    def test_unveraendert_keine_abweichung(self):
        self.assertEqual(abweichungen(entscheide_alle()), [])


if __name__ == "__main__":
    unittest.main()
