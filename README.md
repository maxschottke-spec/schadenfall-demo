# Schadenfall-Demo

Eine kleine Vorführstrecke: Ein Geräteschaden läuft vom Posteingang bis zum Entscheidungsvorschlag.

Alle Fälle, Namen und Bedingungen sind erfunden.

## Was die Strecke zeigt

Das Sprachmodell liest Schadenmeldung und Beleg und füllt ein Formular; zu jedem Feld liefert es ein wörtliches Zitat aus den Unterlagen.
Fester Code prüft, ob jedes Zitat wirklich in den Unterlagen steht, rechnet nach, prüft Bedingungen und Auffälligkeiten und entscheidet.
Ein Mensch gibt alles frei, was nicht eindeutig ist: jede Auffälligkeit, jeden Betrag über 500 € und jede Ablehnung.

## Ansehen ohne Schlüssel und ohne Modellaufruf

Die Modellantworten eines Laufs vom 16.11.2026 liegen in `lauf/` (16 gelesene Formulare, 8 Briefentwürfe). Damit läuft alles lokal und ohne Netz.

1. **Ergebnisseite öffnen:** `schaden-demo.html` im Browser öffnen. Die Seite ist eine einzelne Datei ohne externe Abhängigkeiten.
2. **Wiedergabe starten:**

   ```
   python3 pipeline.py
   python3 report.py
   ```

   `pipeline.py` liest die gespeicherten Antworten aus `lauf/`, lässt die Prüfungen laufen und schreibt `ergebnis.json`. `report.py` baut daraus `schaden-demo.html` neu. Dabei ändert sich nur die Zeitangabe des Laufs.
3. **Tests laufen lassen:**

   ```
   python3 -m unittest -v
   ```

Voraussetzung: Python 3.12 oder neuer, nur Standardbibliothek. Geprüft mit Python 3.14.5.

Ein neuer Modell-Lauf ist für das Ansehen nicht nötig. `python3 pipeline.py --neu` fragt das Modell für alle Fälle neu und überschreibt die Dateien in `lauf/`. Der Aufruf geht über das Kommandozeilenprogramm `claude` und dessen eigene Anmeldung; im Code steht kein Schlüssel. Fehlt eine Datei in `lauf/`, ruft auch der Aufruf ohne `--neu` für diesen Fall das Modell auf.

## Fälle und Sollwerte

`faelle.json` enthält 16 Fälle. Jeder Fall besteht aus Vertragsdaten, dem Text der Schadenmeldung, dem Text des Belegs (oder keinem Beleg) und einem von Hand festgelegten Soll unter `gold`:

- sechs gelesene Felder: Schadentag, Schadenart, Belegnummer, Belegdatum, Seriennummer im Beleg, Gesamtbetrag
- die Entscheidung: `auszahlen`, `ablehnen` oder `an_mensch`
- der Betrag, die Gründe für die Übergabe an einen Menschen und bei Ablehnung der Paragraf

Die Bedingungen, gegen die geprüft wird, stehen in `bedingungen.md`.

## Ergebnisse

Wiedergabe der gespeicherten Antworten (Modell laut gespeicherten Antworten: `claude-sonnet-5-5`), ausgeführt am 18.11.2026:

| Messgröße | Wert |
| --- | --- |
| Entscheidungen wie im Soll | 16 von 16 |
| Gelesene Felder wie im Soll | 96 von 96 |
| Falsch automatisch ausgezahlt | 0 |
| Automatisch auszahlen | 4 |
| Ablehnung vorgeschlagen | 4 |
| An einen Menschen | 8 |

Gegenprobe: Dieselbe Messung mit je einer abgeschalteten Sicherung.

| Abgeschaltet | Falsch entschieden | Davon fälschlich ausgezahlt |
| --- | --- | --- |
| Betragsgrenze | 1 Fall (F10) | 1 |
| Auffälligkeiten | 7 Fälle (F07, F08, F11, F12, F13, F14, F15) | 7 |

Tests: 9 Tests, alle bestanden. Sie prüfen Entscheidung, Gründe, Paragraf und Betrag sowie die sechs gelesenen Felder aller 16 Fälle gegen `gold`, auf Basis der gespeicherten Antworten und mit gesperrtem Modellaufruf.

## Grenzen

- Fälle, Namen, Werkstatt und Bedingungen sind erfunden. Die Bedingungen gehören zu keinem Versicherer; die Strecke trifft keine Aussage über echte Versicherungsbedingungen.
- Kein Produktivsystem. Es gibt keine Anbindung an Posteingang, Bestandssystem oder Zahlung.
- Die Unterlagen sind Text. Fotos, Scans und Handschrift werden nicht gelesen; Fall F16 ist die Abschrift einer handgeschriebenen Quittung.
- Fälle und Soll stammen vom selben Autor wie der Code. 16 von 16 sagt deshalb wenig über die Leistung bei fremden, echten Fällen.
- Die Zahlen oben gelten für einen gespeicherten Modell-Lauf. Ein neuer Lauf kann andere Antworten liefern.
- Über mehrere Fälle hinweg wird nur die doppelte Belegnummer geprüft.

## Dateien

| Datei | Inhalt |
| --- | --- |
| `pipeline.py` | Leseauftrag an das Modell, Prüfungen, Entscheidung, Messung, Gegenprobe |
| `report.py` | baut aus `ergebnis.json` die Ergebnisseite |
| `faelle.json` | 16 Fälle mit Soll |
| `bedingungen.md` | die erfundenen Bedingungen |
| `lauf/` | gespeicherte Modellantworten |
| `ergebnis.json`, `schaden-demo.html` | Ergebnis des Laufs vom 16.11.2026 |
| `tests/` | Tests der Entscheidungslogik gegen das Soll |

## Lizenz

MIT, siehe `LICENSE`.
