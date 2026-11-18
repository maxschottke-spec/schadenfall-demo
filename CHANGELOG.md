# Changelog

What changed, for people who use or adapt this repository. The first release is v0.1.0.

## 0.1.0 — 2026-11-18

First release. Everything below came to `main` on 18 November 2026.

### Added

- English `README.md` with a glossary of the German identifiers; the German text moved to `README.de.md`.
- `docs/walkthrough.md` and `docs/walkthrough.de.md`: three cases step by step (automatic payout, handed to a human, proposed rejection), and a list of what is implemented, what comes from stored answers and what does not exist.
- `docs/adapt.md`: which parts are specific to the claim example, which are general, the structure of a case, and a checklist for moving the pattern to another process.
- `beispiel.py`: plays one case on the console from the stored answers, without a model call and without writing a file; `--en` for English labels, `--liste` for all cases.
- `.github/workflows/test.yml`: tests, replay and `beispiel.py` on push to `main` and on pull requests, with Python 3.12 and 3.13. A fake `claude` in the search path makes the run fail if a model is called; the run also fails if `ergebnis.json` or the results page differ from the committed files in more than the timestamp.
- `CONTRIBUTING.md`, `SECURITY.md`, this changelog, and two issue forms ("Path to a wrong decision", "Question or idea").
- Tests: `tests/test_beispiel.py`, `tests/test_seite.py`, a test for the limit at exactly 500 €, two tests for the measurement, one for the counter-check and one for an embedded instruction in an excluded claim. 72 tests in total (52 on `main`).

### Changed

- The messages of `pipeline.py` for a missing stored answer and for missing expected values name the sections of both README files.
- README: the requirement (Python 3.12 or newer) is stated before the first command, with the error messages older versions produce. The steps for adding a case say when to run the tests and what `FALSCH` means.
- README, "Limits": two entries added. The type of damage is the model's judgement and only its quote is checked. The draft letter is not checked against the facts.

### Fixed

- Measurement (`pipeline.messe()`): an expected amount written as a whole number (`249` instead of `249.0`) was reported as a wrongly read field, and expected reasons that were not in alphabetical order were reported as a wrong decision. The decision logic did not change.
- Results page: the note under a draft letter claimed that every rejection contains a quote from the customer's message. That holds for rejections under § 3 a to d, not for § 3 e.
- Results page: the case number, contract data and expected values from `faelle.json`, and the model name, were inserted without escaping. Text from the documents and from the model answer was already escaped.
- Results page: the first case in `faelle.json` is shown on opening, instead of a fixed `F01`.

## State of `main` on 18 November 2026

The state published before the changes above. It was never tagged.

- Pipeline in `pipeline.py`: reading task for the model with a verbatim quote for every field, checks and decision in fixed code, draft letter, measurement against expected values set by hand, counter-check with one safeguard switched off at a time.
- 16 invented cases in `faelle.json`, invented terms in `bedingungen.md`, stored model answers in `lauf/`, results page `schaden-demo.html` built by `report.py`.
- Hardening of the checks without a model: every value needs a quote; quotes for receipt data must come from the receipt; values are compared with their own quote; numbers and identifiers must stand as whole words; the code reads the total line and labelled serial numbers itself; malformed answers and unexpected errors lead to a human.
- No model call unless `--neu` or `--modell-erlaubt` is given; a missing stored answer stops the run with a message.
- German README with instructions for adding a case by hand and a table of the reasons for handing a case to a human.
- 52 tests.
