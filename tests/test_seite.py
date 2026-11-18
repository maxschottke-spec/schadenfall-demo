"""Prüft die Vorlage der Ergebnisseite in report.py, ohne report.py auszuführen.

Felder aus der Fallakte (Fallnummer, Vertragsdaten, Soll) dürfen nur über esc() in die Seite gelangen.
Sonst könnte ein beigesteuerter Fall beim Öffnen der Seite Markup oder Skript ausführen.
Gelesen wird nur der Quelltext: report.py schreibt beim Import die Seite, und ein Test soll nichts schreiben.
"""
import pathlib
import re
import unittest

WURZEL = pathlib.Path(__file__).resolve().parent.parent
QUELLE = (WURZEL / "report.py").read_text(encoding="utf-8")


class SeiteEscaped(unittest.TestCase):
    def test_felder_der_fallakte_nur_ueber_esc(self):
        roh = re.findall(r"\$\{(?:f\.id|f\.titel|f\.eingang|v\.\w+|f\.gold\.(?:paragraf|betrag))\}", QUELLE)
        self.assertEqual(roh, [])
        self.assertNotIn("GR[g]||g)", QUELLE.split("Soll laut Testsatz")[1].split("\n")[0])
        self.assertNotIn("zeige('${", QUELLE)

    def test_esc_ersetzt_auch_anfuehrungszeichen(self):
        zeile = next(z for z in QUELLE.splitlines() if z.startswith("const esc="))
        for zeichen in ("&amp;", "&lt;", "&gt;", "&quot;", "&#39;"):
            self.assertIn(zeichen, zeile)

    def test_modellname_und_laufzeit_werden_escaped(self):
        self.assertIn('"__MODELL__": html.escape(', QUELLE)
        self.assertIn('"__LAUF__": html.escape(', QUELLE)


if __name__ == "__main__":
    unittest.main()
