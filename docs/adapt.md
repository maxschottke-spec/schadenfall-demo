# Adapt this to your own process

[back to the README](../README.md) · this document exists in English only

This repository is a worked example of one pattern: a language model reads documents and fills in a form with verbatim quotes, fixed code checks the form and decides, and a human approves everything that is not clear-cut. The example process is a device damage claim. This guide says which parts you can keep when you move the pattern to a different process, which parts you have to rewrite, and in which order to do it.

Everything below is taken from the code in this repository. It was written by reading the code and by adding one extra case of the same kind to a fresh clone. Nobody has reported back a port to a different process yet, so treat the order below as a proposal, and expect the first port to find gaps in it.

## What you get, and what you do not

You get about 640 lines of standard-library Python in `pipeline.py` that you can read in one sitting, 16 cases with expected values, stored model answers so that everything runs without a model, a measurement against the expected values, and a counter-check that proves the measurement notices errors.

You do not get a library, a package, a configuration file or an API. Adapting means editing `pipeline.py`. The checks are written for German-language documents and German number and date formats. Nothing here is connected to an inbox, a payment system or a screen for the human approval; see "How this maps to a real rollout" in [walkthrough.md](walkthrough.md).

## Which parts are specific to the claim example

These are tied to the device damage claim and have to be rewritten for your process.

| Part | Where | Why it is specific |
| --- | --- | --- |
| The rules the decision refers to | `bedingungen.md` | Invented insurance terms. `report.py` shows this file on the results page and skips its first two blocks (title and introduction). |
| The reading task and the form | `LESE_PROMPT` in `pipeline.py` | Names the fields of this form, the nine types of damage and the German instructions to the model. |
| The shape check of the form | `TEXT_FELDER` and `form_fehler()` | Lists the field names and types of this form. |
| Which value needs which quote | `WERT_BRAUCHT_ZITAT` | Maps each value field of this form to its quote field. |
| Which quotes must come from which document | `BELEG_FELDER` | Here: receipt number, receipt date, serial number and total must be quoted from the receipt, not from the customer's message. |
| Business constants | `GRENZE_AUTOMATIK` (500 €), `SELBSTBETEILIGUNG` (50 €), `MELDEFRIST_TAGE` (14), `FRUEHSCHADEN_TAGE` (14), `VERSICHERT`, `AUSSCHLUSS` | Limits, deductible, deadlines and the covered and excluded types of damage from the invented terms. |
| The business checks | steps 2b to 5 in `_pruefe()`, plus `zeitwert()` and `monate()` | Contract data, type of damage against § 2 and § 3, dates and deadlines, receipt, serial number, line items, duplicate receipt number, calculation of the benefit. |
| Patterns for German documents | `SUMMEN_RE`, `SERIEN_RE`, `MONATE`, `ANWEISUNG_MUSTER` | Words for "total", labels for serial numbers, month names, and phrases addressed to a system, all in German. |
| The letter | `BRIEF_PROMPT` and `brief()` | The facts handed to the model and the German instructions for the letter. |
| The model call itself | `modell()` and `MODELL` | Calls the command line program `claude` and reads `result` and `modelUsage` from its JSON output. If you use another provider, this function is the one place to change. |
| Cases and expected values | `faelle.json`, key `gold` | 16 invented claims. |
| Stored model answers | `lauf/` | Answers to exactly these 16 cases. |
| What is measured | `FELDER` and `messe()` | The six fields compared with `gold`, and the four parts of a decision: `entscheidung`, `gruende`, `paragraf`, `betrag`. |
| The results page | `report.py` | German page with fixed field labels, a fixed "6" for the number of measured fields, the date of the stored model run, the author's name and a section on where the author's rules come from. |
| The console view | `LESE_FELDER` and `TEXTE` in `beispiel.py` | Field list and labels of this form. |
| Most tests | `tests/test_haertung.py`, `tests/test_beispiel.py` | The hardening tests are built on case F01; the example tests assert texts of F01, F06 and F11. |

## Which parts are general

These do not depend on insurance. You can keep them, with the limits named in the last column.

| Part | Where | What it does | Limits |
| --- | --- | --- | --- |
| Quote check | `zitat_vollstaendig()`, `norm()`, step 1 of `_pruefe()` | Every field ending in `_beleg` must appear in the documents. Case and whitespace are normalised. A quote must not start or end in the middle of a number. | A quote that is present does not prove that it supports the value. See "What the general checks do not give you". |
| Value without a quote | the loop over `WERT_BRAUCHT_ZITAT` in step 1 | A value that is set without a quote counts as unproven. | The mapping itself is specific. |
| Value against its own quote | `als_ganzes_wort()`, `kennung()`, `betraege_cent()`, `in_cent()`, `datum_im_zitat()` | A number or identifier must stand in its quote as a whole word; an amount is parsed from the quote and compared in cents; day, month and a stated year must match the date. | Number formats `1.249,00`, `249,5`, `249.00`, `249` and `119,-`. Date formats `3.11.26`, `03.11.2026`, `3. November`. Other formats are not read. |
| The code's own reading | `gesamt_im_beleg()`, the `SERIEN_RE` search in step 5 | The code looks for the total line and for labelled serial numbers itself and sends the case to a human if that differs from the model's answer. | The patterns are German and specific; the idea of a second, independent reading by code is general. |
| Ambiguous numbers | `MEHRDEUTIG_RE` | A number with a space such as `1 249,00` goes to a human. | |
| Embedded instructions | step 2 of `_pruefe()` | A case goes to a human if the model reports an instruction in the documents or if the code's own pattern search finds one. | `ANWEISUNG_MUSTER` is a short German phrase list and not complete protection. |
| Baseline safeguard | `pruefe()`, `form_fehler()`, `an_mensch_wegen()` | An answer in the wrong shape leads to a human. Any unexpected exception in the checks leads to a human. | The shape check itself is specific. |
| Decision ladder | step 6 of `_pruefe()` | In this order: any hard finding leads to a human; an exclusion leads to a proposed rejection; any warning sign leads to a human; an amount above the limit leads to a human; no positive calculated amount leads to a human; only then the automatic outcome. | The names of the outcomes are specific. |
| No silent model call | `modell_erlaubt()`, `lies()`, `brief()` | A model is only called with `--neu` or `--modell-erlaubt`. A missing stored answer stops the run with a message. Every answer is stored as a file per case. | |
| Restricted model call | `modell()` | The call runs without tools and from an empty directory, because the prompt contains text written by customers. | The flags are those of the `claude` program. |
| Measurement | `messe()`, the summary in `main()` | Compares every case with its expected values and counts wrong decisions and wrong automatic outcomes separately. | The compared fields are specific. |
| Counter-check | `gegenprobe()` | Repeats the measurement with the limit switched off and with all findings ignored. If the measurement then still reports no error, it measures nothing. | The two switches are `GRENZE_AUTOMATIK` and `SIGNALE_AUS`. |
| Replay check | `tests/test_entscheidung.py`, class `OhneModell` | Blocks `pipeline.modell` and `subprocess.run` for every test, then checks all cases against `gold`. | `SOLL_FELDER` is specific. |
| Check on every change | `.github/workflows/test.yml` | Puts a fake `claude` first in the search path, fails if it was called, and fails if the committed results differ from a fresh replay. | Named after the `claude` program. |

## What the general checks do not give you

- **The classification is the model's judgement.** The code checks that the quote for `schadenart` is in the documents. It cannot check that the quote supports the chosen type. In this repository, changing `schadenart` in `lauf/F04_gelesen.json` from `optisch` to `sturz_bruch` and leaving the quote unchanged turns the proposed rejection into an automatic payout of 210,00 €. Any field your process decides on that is a judgement and not a copied value has this property.
- **A quote can be correct and still belong to something else.** A date that appears in the message is accepted as the date of damage if day, month and year match the quote, whatever the sentence around it says.
- **The letter is not checked.** The draft is taken as the model wrote it. For a rejection because of the type of damage, the quoted customer text is part of the facts handed to the letter-writing model.
- **The cases and the expected values in this repository come from the author of the code.** That says little about documents the author did not think of.
- **No test calls a model.** Tests and the automatic check run on stored answers. The only test of `modell()` replaces the process start and checks the arguments of the call (no tools, empty directory).

## Checklist, in the order you would work

1. **Run the example unchanged.** `python3 pipeline.py`, `python3 report.py`, `python3 -m unittest`, `python3 beispiel.py F01 --en`. You need Python 3.12 or newer. Read [walkthrough.md](walkthrough.md) for three cases step by step.
2. **Name your outcomes and the one error that must not happen.** Here the outcomes are `auszahlen`, `ablehnen` and `an_mensch`, and the error that is counted separately is `falsch_ausgezahlt`: an automatic payout that the expected values do not allow. Decide what the equivalent is in your process before you write any code.
3. **Write your rules down in one short file**, as `bedingungen.md` does. Every check you write later should point to a line in it.
4. **Define the form.** For every value the decision needs, one value field and one quote field. Decide which quotes must come from which document. This becomes `LESE_PROMPT`, `TEXT_FELDER`, `form_fehler()`, `WERT_BRAUCHT_ZITAT` and `BELEG_FELDER`.
5. **Write the cases and their expected values by hand, before the checks.** Follow the structure of an entry in `faelle.json` (see the next section). Include at least one case per outcome, one per warning sign, one above your limit, one with an instruction hidden in a document and one with a missing document. The 16 cases here are built that way; their titles in `faelle.json` say what each one is for.
6. **Write the model's answers by hand** as `lauf/<id>_gelesen.json`, one per case. You do not need a model for any step up to step 11.
7. **Rewrite the business checks** (steps 2b to 5 of `_pruefe()`), and keep step 1 (quotes), step 2 (embedded instructions), step 6 (decision ladder) and the wrapper `pruefe()`. Sort every finding into `hart` (the answer or the data cannot be trusted: always a human, even if the case would be excluded) or `weich` (warning sign: a human, unless the case is excluded anyway and a rejection is proposed).
8. **Adapt the measurement**: `FELDER`, the keys under `gold`, `messe()`.
9. **Run `python3 pipeline.py` until every line says `OK`, then read the counter-check.** `pipeline.py` exits with status 0 even if a line says `FALSCH`; the tests are what fail. If switching a safeguard off produces no wrong decision in the `Gegenprobe` line, no case of yours tests that safeguard: go back to step 5.
10. **Rewrite the hardening tests.** `tests/test_haertung.py` shows the method: take one case that is decided automatically, falsify one document or one field of the answer the way a reading error or an attacker would, and expect that the case is no longer decided automatically. Keep the class `OhneModell` from `tests/test_entscheidung.py` so that no test can start a model. Then change one line of a safeguard on purpose and see whether a test fails.
11. **Only now connect a model.** Replace `modell()` if you do not use the `claude` program. Keep the three properties of the call: no tools, an empty working directory, and the answer stored per case. Run it deliberately with `--neu`, look at the differences to your hand-written answers, and commit the stored answers. The figures you report afterwards hold for that one stored run.
12. **Adapt what people look at**: `report.py` (labels, texts, the author line, the date of the stored run) and `beispiel.py` (`LESE_FELDER`, `TEXTE`). Both are optional for the pattern itself.
13. **Adapt the automatic check.** In `.github/workflows/test.yml`, name the fake program after the command your `modell()` starts. Commit `ergebnis.json` and the results page after a replay, because the workflow compares a fresh replay with the committed files.
14. **Before real use**, read "How this maps to a real rollout" in [walkthrough.md](walkthrough.md): intake, contract data, a queue for the human decision, memory across runs, and expected values from cases that people in your process have decided.

## The structure of a case

One entry in `faelle.json`, as the code reads it:

| Key | Content | Read by |
| --- | --- | --- |
| `id` | case number such as `F17`; also the file name prefix in `lauf/` | `lies()`, `brief()` |
| `titel` | short title | results page, `beispiel.py` |
| `vertrag` | `vertragsnr`, `geraet`, `seriennr`, `kaufpreis` (number), `kaufdatum` and `vertragsbeginn` (`YYYY-MM-DD`) | `_pruefe()` |
| `eingang` | date the claim was received, `YYYY-MM-DD`. Cases are checked in this order, so that a receipt number counts as a duplicate in the later case. | `_pruefe()`, `main()` |
| `meldung` | text of the customer's message | `LESE_PROMPT`, quote check |
| `beleg` | text of the receipt, or `null` | `LESE_PROMPT`, quote check |
| `gold` | expected values, all ten keys required: `schadentag`, `schadenart`, `belegnummer`, `belegdatum`, `seriennummer_beleg`, `gesamtbetrag` (the six read fields, `null` where the documents do not contain them), `entscheidung`, `betrag`, `gruende` (list, empty unless the decision is `an_mensch`), `paragraf` (`null` unless the decision is `ablehnen`) | `messe()`, tests |

Two details of `gold` that are easy to get wrong:

- `betrag` is the amount to be paid out, after the current value cap and the deductible, not the total on the receipt. It is `null` for `ablehnen` and for `an_mensch`, with one exception: for the reason `betrag_ueber_grenze` it is the calculated amount (case F10: 730.0).
- The form field for the serial number is called `seriennummer_beleg_wert`, the expected value is called `seriennummer_beleg`. In the form, `seriennummer_beleg` is the quote.

## Adding one case of the same kind

This is the small version of the checklist, for the claim process as it is. It was carried out on a fresh clone while this guide was written.

1. Append the case to `faelle.json`.
2. Create `lauf/<id>_gelesen.json` by hand; copy `lauf/F01_gelesen.json` and adapt it. The field `_modell` is optional.
3. Run `python3 pipeline.py`. If it stops with `<id>_brief.txt fehlt in lauf/`, the decision is `auszahlen` or `ablehnen` and the pipeline expects a draft letter: create `lauf/<id>_brief.txt` with any text. `python3 beispiel.py <id> --en` shows the decision without needing the letter.
4. Run `python3 pipeline.py` and `python3 report.py` again, then `python3 -m unittest`. Run the tests after the replay: `tests/test_beispiel.py` compares with `ergebnis.json` and fails as long as that file does not contain the new case.
5. If the line for your case says `FALSCH`, either the expected values or the hand-written answer are not what the code computes. `python3 beispiel.py <id> --en` lists every check with its result.
6. If you commit the case, commit `ergebnis.json` and `schaden-demo.html` with it.
