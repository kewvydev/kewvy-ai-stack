---
name: diagnosing-bugs
description: Diagnose a difficult reproducible failure or performance regression with a focused feedback loop and evidence.
license: MIT
---

# diagnosing-bugs

Use the project's existing runtime and checks to reproduce the reported symptom.
Read [the diagnosis workflow](references/upstream.md) when a structured investigation
is needed. Its optional human-feedback helper lives at `scripts/hitl-loop.template.sh`.
Keep hypotheses proportional to the failure. Capture evidence with secrets removed,
fix the demonstrated cause, verify the original symptom and relevant regressions,
and remove temporary instrumentation. Do not introduce a testing framework or
external service solely for this workflow. Record durable cross-module findings
in the project's finding register; leave incomplete work in its task record.
