# Security

This repository is a demonstration with invented data. It runs no service, holds no secrets and pays nothing out. A security problem here is therefore a flaw in the pattern it demonstrates, which matters to anyone who adapts the code to real documents.

## What counts as a security problem

1. **A path to a wrong automatic payout.** Documents, or a model answer, for which `pipeline.pruefe()` returns `auszahlen` although the terms in `bedingungen.md` do not allow it. The code is meant to trust neither the documents nor the model answer.
2. **A path from document text to a model or tool call.** Text in a claim message or receipt that makes the code call a model without `--neu` or `--modell-erlaubt`, that reaches a model call with tools enabled or outside the empty working directory, or that makes the code start any other program.
3. **Document text that is executed.** Text from a case, a model answer or a letter that runs as markup or script when `schaden-demo.html` is opened.

## What is already known and documented

The section "Limits" in `README.md` lists gaps that are known and left open, among them: the type of damage is the model's judgement and only its quote is checked; the search for embedded instructions is a phrase list; the draft letter is not checked against the facts. A new variant of these is welcome as a normal issue, not as a security report.

## How to report

- **A wrong payout on invented data** harms nobody. Report it in full with the issue form "Path to a wrong decision".
- **Points 2 and 3**, and any finding you made on an adaptation that handles real data: use "Report a vulnerability" under the Security tab of this repository if that button is shown. If it is not shown, open an issue that says a security problem exists and which of the three points it concerns, without the details needed to exploit it, so that a way to pass on the details can be agreed there.

There is no private e-mail address for reports.

## What to expect

This is a personal project without a support commitment, and no response time is promised. The aim is that a confirmed problem ends in a fix with a test, or in an entry under "Limits" if it is left open. Only the current state of the branch `main` is maintained.
