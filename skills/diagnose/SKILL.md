---
name: diagnose
description: Compatibility name for diagnosing-bugs; reproduce a hard failure and investigate falsifiable causes before fixing it.
license: MIT
---

# Diagnose

The upstream `diagnose` skill was renamed to `diagnosing-bugs`. In initialized
stack projects use `$diagnosing-bugs` for the full workflow; do not run two separate
diagnosis processes. If that project skill is unavailable, use the bundled
[diagnosis method](references/upstream.md) and optional helper at
`scripts/hitl-loop.template.sh` from this skill directory.

Keep work within the authorized scope. Build a reproducible feedback loop, confirm
the failure, rank falsifiable hypotheses, collect targeted evidence, fix the cause
and verify a regression check. If reproduction is unavailable, report the missing
artifact and retain the criterion as pending. Do not execute the helper or install
browser dependencies merely because the skill is installed. Record reusable,
confirmed findings locally; suggestions do not authorize another module's changes.
