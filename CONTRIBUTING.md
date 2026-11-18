# Contributing

This is a small template that is meant to stay readable in one sitting. The contributions that help most, in this order:

1. **A counter-example:** a case that is paid out automatically although it should not be. Use the issue form "Path to a wrong decision".
2. **A report from adapting it:** what was missing or wrong in [docs/adapt.md](docs/adapt.md) when you moved the pattern to your own process.
3. **A fix** for one of the two, with a test.

New features are added only if someone cannot use the template without them.

## Run the tests

Python 3.12 or newer, standard library only. Nothing is installed.

```
python3 -m unittest
```

Then the replay and one case on the console:

```
python3 pipeline.py
python3 report.py
python3 beispiel.py F01 --en
```

The replay rewrites `ergebnis.json` and `schaden-demo.html`; only the timestamp of the run changes. If you did not change a case, a check or the page, discard that change before you commit (`git checkout -- ergebnis.json schaden-demo.html`).

## No test may call a model

Tests, the replay and the automatic check run on the stored answers in `lauf/`. This is a rule, not a convenience:

- The tests that replay the cases block `pipeline.modell` and `subprocess.run` before every test: class `OhneModell` in `tests/test_entscheidung.py`, and the same `setUp` in `tests/test_beispiel.py`. A new test class that replays cases does the same.
- Do not run `python3 pipeline.py --neu` or `--modell-erlaubt` as part of a contribution, and do not add a test or a workflow step that does.
- `.github/workflows/test.yml` puts a fake `claude` first in the search path and fails if it was called.

A change to `LESE_PROMPT`, `BRIEF_PROMPT` or `modell()` cannot be verified by the tests. Say so in the pull request, and say whether and how you ran it against a model.

## Contribute a case

The steps are in [docs/adapt.md](docs/adapt.md#adding-one-case-of-the-same-kind): append the case to `faelle.json` with its expected values under `gold`, write `lauf/<id>_gelesen.json` by hand, add `lauf/<id>_brief.txt` if the decision is `auszahlen` or `ablehnen`, run the replay, then the tests.

- **Cases must be invented.** No real persons, companies, contract numbers, serial numbers, addresses or documents, and nothing copied from a real claim. Avoid names of real products and manufacturers.
- Write the expected values before you look at what the code decides.
- A case should be there for a reason that no existing case covers. Say in the pull request which check or which gap it exercises.
- A new case changes the figures. Commit the regenerated `ergebnis.json` and `schaden-demo.html`, and update the numbers that are written out in `README.md` and `README.de.md` (number of cases, the results table, the counter-check table, the number of tests).

If the code decides your case wrongly, do not adjust `gold` to make it pass. Open an issue, or send the case together with the fix and a test in `tests/test_haertung.py` that fails without the fix.

## Change a check

- One falsification per test, in the style of `tests/test_haertung.py`: change one document or one field of the model answer and assert that the case is not paid out automatically.
- Check that your test fails without your change.
- Keep the rule of the baseline safeguard: when in doubt, the case goes to a human and never to a payout.

## Style

- Identifiers in code and data are German; `README.md` has a glossary. Documentation for contributors is English.
- Standard library only.
- Stage files by path. Commit messages say what changed and why.

## Licence

By contributing you agree that your contribution is published under the MIT licence in `LICENSE`.
