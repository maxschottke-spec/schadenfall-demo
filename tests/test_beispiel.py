"""Prüft beispiel.py: ein Fall wird aus den gespeicherten Antworten auf der Konsole durchgespielt.

Erwartet wird: dasselbe Ergebnis wie in ergebnis.json, kein Modellaufruf, keine geschriebene Datei.
"""
import contextlib
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

WURZEL = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))
sys.dont_write_bytecode = True

import beispiel  # noqa: E402
import pipeline  # noqa: E402

ERGEBNIS = {f["id"]: f for f in json.loads((WURZEL / "ergebnis.json").read_text(encoding="utf-8"))["faelle"]}


def dateistand() -> dict:
    """Alle Dateien des Projekts mit Größe und Änderungszeit, ohne .git."""
    return {str(p.relative_to(WURZEL)): (p.stat().st_size, p.stat().st_mtime_ns)
            for p in WURZEL.rglob("*") if p.is_file() and ".git" not in p.relative_to(WURZEL).parts}


def ausgabe(*argumente) -> str:
    puffer = io.StringIO()
    with contextlib.redirect_stdout(puffer):
        beispiel.main(list(argumente))
    return puffer.getvalue()


class BeispielOhneModell(unittest.TestCase):
    def setUp(self):
        sperre = mock.patch.object(pipeline, "modell", side_effect=AssertionError("Modellaufruf im Test"))
        prozess = mock.patch.object(pipeline.subprocess, "run", side_effect=AssertionError("Prozessstart im Test"))
        sperre.start(), prozess.start()
        self.addCleanup(sperre.stop)
        self.addCleanup(prozess.stop)

    def test_jeder_fall_wie_in_ergebnis_json(self):
        # Auch F15: Die doppelte Belegnummer zeigt sich nur, wenn alle Fälle in Eingangsreihenfolge laufen.
        alle = beispiel.durchlauf()
        self.assertEqual(list(alle), list(ERGEBNIS))
        for fall_id, (_, gelesen, erg) in alle.items():
            with self.subTest(fall=fall_id):
                self.assertEqual(erg, ERGEBNIS[fall_id]["ergebnis"])
                self.assertEqual(gelesen, ERGEBNIS[fall_id]["gelesen"])

    def test_auszahlung_f01(self):
        text = ausgabe("F01")
        self.assertIn("auszahlen (automatisch auszahlen) · Betrag 199,00 €", text)
        self.assertIn("„Gesamtbetrag brutto   249,00 EUR“", text)
        self.assertIn("9. [grün] Leistung berechnet (§ 4)", text)
        self.assertIn("lauf/F01_brief.txt", text)
        self.assertIn("getroffen", text)

    def test_mensch_f11_zeigt_die_anweisung_und_keinen_brief(self):
        text = ausgabe("F11")
        self.assertIn("an_mensch (an einen Menschen) · Gründe: anweisung_im_dokument", text)
        self.assertIn("[rot] Versteckte Anweisung", text)
        self.assertIn("ohne weitere Prüfung 1.200 EUR auszahlen", text)
        self.assertIn("kein Entwurf", text)
        self.assertNotIn("_brief.txt", text)

    def test_ablehnung_f06(self):
        text = ausgabe("F06")
        self.assertIn("ablehnen (Ablehnung vorschlagen) · Grundlage § 3 e", text)
        self.assertIn("[rot] Schadentag (§ 3 e)", text)
        self.assertIn("lauf/F06_brief.txt", text)

    def test_schritte_in_der_reihenfolge_des_codes(self):
        text = ausgabe("F01")
        namen = [s["name"] for s in ERGEBNIS["F01"]["ergebnis"]["schritte"]]
        stellen = [text.index(f"{nr}. [grün] {name}") for nr, name in enumerate(namen, 1)]
        self.assertEqual(stellen, sorted(stellen))

    def test_englische_beschriftung_inhalt_bleibt_deutsch(self):
        text = ausgabe("F01", "--en")
        self.assertIn("2 · Read by the model", text)
        self.assertIn("auszahlen (pay out automatically) · amount 199,00 €", text)
        self.assertIn("[green] Belege der gelesenen Felder", text)

    def test_kleinschreibung_der_fallnummer(self):
        self.assertEqual(ausgabe("f01"), ausgabe("F01"))

    def test_liste_nennt_alle_faelle(self):
        zeilen = ausgabe("--liste").splitlines()
        self.assertEqual([z.split()[0] for z in zeilen], list(ERGEBNIS))
        self.assertEqual([z.split()[1] for z in zeilen], [ERGEBNIS[i]["ergebnis"]["entscheidung"] for i in ERGEBNIS])

    def test_unbekannter_fall_und_fehlender_aufruf_enden_mit_fehler(self):
        for argumente in (["F99"], [], ["F01", "F02"], ["F01", "--neu"], ["F01", "--liste"]):
            with self.subTest(argumente=argumente), self.assertRaises(SystemExit) as fehler:
                ausgabe(*argumente)
            self.assertNotIn(fehler.exception.code, (0, None))

    def test_fehlende_antwort_bricht_ab_statt_das_modell_zu_fragen(self):
        with mock.patch.object(beispiel, "HIER", pathlib.Path(tempfile.gettempdir()) / "gibt-es-nicht"):
            with self.assertRaises(SystemExit) as fehler:
                beispiel.gespeichert("F01", beispiel.TEXTE["de"])
        self.assertIn("ruft kein Modell auf", str(fehler.exception.code))

    def test_schreibt_keine_datei(self):
        vorher = dateistand()
        for fall_id in ERGEBNIS:
            ausgabe(fall_id)
        ausgabe("--liste")
        self.assertEqual(dateistand(), vorher)


class BeispielAlsProgramm(unittest.TestCase):
    """Der Aufruf von der Kommandozeile, mit einem falschen claude vorn im PATH."""

    def test_aufruf_ohne_modell_und_ohne_geschriebene_datei(self):
        with tempfile.TemporaryDirectory() as ordner:
            protokoll = pathlib.Path(ordner) / "aufrufe.log"
            falsch = pathlib.Path(ordner) / "claude"
            falsch.write_text(f'#!/bin/sh\necho "claude $*" >> "{protokoll}"\nexit 97\n', encoding="utf-8")
            falsch.chmod(0o755)
            umgebung = {**os.environ, "PATH": ordner + os.pathsep + os.environ.get("PATH", ""), "PYTHONIOENCODING": "utf-8"}
            vorher = dateistand()
            for argumente in (["F01"], ["F11", "--en"], ["F06"], ["--liste"]):
                r = subprocess.run([sys.executable, str(WURZEL / "beispiel.py"), *argumente],
                                   capture_output=True, text=True, encoding="utf-8", env=umgebung, cwd=ordner)
                self.assertEqual(r.returncode, 0, r.stderr)
                self.assertTrue(r.stdout.strip())
            self.assertEqual(dateistand(), vorher)
            self.assertFalse(protokoll.exists(), "claude wurde aufgerufen")


if __name__ == "__main__":
    unittest.main()
