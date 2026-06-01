# Hardcoding Disclosures

## target_paper_scope

- Description: The demo is intentionally scoped to SkillGen.pdf.
- Reason: The user explicitly asked for a preliminary demo that only needs to work for this paper.
- Impact: The claim selector prioritizes SkillGen's paired-intervention/Table 1 claim shape.

## claim_selector_priority

- Description: The demo selects the Table 1 average-gains claim as the primary benchmark claim.
- Reason: The existing Phase 0 SkillGen note and the paper text identify it as the strongest Phase 0 target.
- Impact: Other SkillGen claims are not selected for the preliminary run, though they remain in the parsed paper text.

## execution_stop_policy

- Description: The demo blocks before official-code execution when hosted APIs, paid token use, external benchmark assets, or missing human approval are detected.
- Reason: Phase 0 rules require a human-visible command gate before risky or costly third-party execution.
- Impact: The demo produces a blocked validation package instead of running official benchmarks.
