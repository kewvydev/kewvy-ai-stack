---
name: tdd
description: Build or fix behavior test-first when TDD is requested, using red-green cycles at agreed public interfaces.
license: MIT
---

# Test-Driven Development

Use TDD for the requested scope, not as a mandate for every project change.
Read existing test commands, domain vocabulary and relevant decisions. Agree the
observable interfaces and behaviors to test with the user; reuse agreement already
present in the request or project criteria. Do not write tests at unconfirmed seams.

Work one behavior at a time: write a test, run it and observe the intended failure,
make the smallest implementation pass, then repeat. Diagnose setup failures before
calling a test red. Tests must observe public behavior and survive internal refactors;
avoid private-method tests, tautological assertions and batches of speculative tests.
Keep refactoring separately scoped. Report checks actually run and remaining gaps.

Read [test examples](references/tests.md) and [mocking guidance](references/mocking.md)
before choosing test doubles. If interface placement is unclear, consult the
[design vocabulary](references/design/vocabulary.md); this is a reference, not an
extra installed skill or approval for architectural changes.
