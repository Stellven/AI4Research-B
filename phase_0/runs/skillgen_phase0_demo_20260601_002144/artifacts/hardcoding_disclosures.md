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

## official_repo_url

- Description: The automation uses `https://github.com/yccm/SkillGen` as the official SkillGen code source.
- Reason: The paper-specific POC targets SkillGen and needs a deterministic official-code intake source.
- Impact: A different paper or fork requires a different code-intake contract.

## skillgen_aime_smoke_target

- Description: The first executable target is AIME with train_n=8, eval_n=4, and seed=42.
- Reason: The user requested the cheapest validation target for the preliminary Phase 0 POC.
- Impact: The smoke verdict does not reproduce the full SkillGen Table 1 claim.

## skillgen_smoke_models

- Description: The smoke command plan uses OpenRouter model names openai/gpt-5.4-nano and openai/gpt-5.4-mini.
- Reason: The existing smoke run used the cheapest available validation setup that still exercises official code.
- Impact: Changing provider routing or model availability may change cost, behavior, or reproducibility.

## skillgen_eval_parser

- Description: The result parser expects SkillGen eval_results.json, token usage JSON, and verification_summary.json shapes.
- Reason: The POC only needs to automate this paper's official-code output format.
- Impact: Other papers or future SkillGen output schemas need a different parser contract.

## skillgen_eval_cli_deviation

- Description: The command plan uses eval_skill.py --skill-repo/--dataset flags when the README example appears mismatched.
- Reason: The executable script parser is treated as the source of truth for the current official checkout.
- Impact: This is a recorded deviation from README text and must remain visible for human review.

## skillgen_all_claim_catalog

- Description: The all-claims automation uses a SkillGen-specific catalog of major empirical and executable claims.
- Reason: The POC is scoped to SkillGen.pdf and the paper's claims require paper-specific grouping before verification.
- Impact: The catalog is not a general claim extractor for arbitrary papers.

## skillgen_table1_rows_and_models

- Description: The all-claims matrix hardcodes the Table 1 row ids and eight paper model display names.
- Reason: These are needed to detect which full-paper claims can be matched to official-code data and model routes.
- Impact: Exact provider route IDs still need review before full unattended Table 1 execution.
