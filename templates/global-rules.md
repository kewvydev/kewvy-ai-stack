# AI Engineering Stack working agreements

Use a lightweight ODD flow: understand, explore, implement, and verify.
Keep changes proportional, preserve existing work, and reuse project conventions.
Resolve material open decisions with the user; continue independent authorized work.
Propose SDD only when it adds useful definition or traceability, explain why,
and wait for explicit approval for that change. Retain approvals already given
for the same scope. Do not require SDD artifacts or multiple agents routinely.

Use the project's reproducible checks. Report what was changed, configured,
executed, and verified separately, including failures and pending checks.
Instructions guide behavior; they do not enforce approval, security, or correctness.
Respect the client's actual permissions and the user's authorization for external actions.
Keep project decisions local and do not store secrets in instructions or records.
On resume, read the project's existing task and finding registers when relevant.
Keep incomplete acceptance criteria open with evidence, blockers, and a next action.
Retain confirmed findings useful to other modules; label hypotheses and verify
old findings before reuse. Update or retire stale findings with evidence.
Do not implement cross-module suggestions solely because a finding was recorded.
Use security-auditor for authentication, untrusted-input changes and pre-merge PR
review when native delegation is available and authorized by this instruction.
Give it the actual diff and scope; it reports without patching. If delegation is
unavailable, state that an independent audit did not run. Recheck its findings;
record confirmed reusable patterns and unfinished checks in the local registers.
Do not treat agent availability, a checklist or an empty report as proof of security.
Write stack content, code comments, documentation, and CLI messages in English.
