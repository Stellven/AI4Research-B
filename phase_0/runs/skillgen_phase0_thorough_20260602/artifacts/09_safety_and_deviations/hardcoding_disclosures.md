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

## skillgen_external_source_catalog

- Description: The automation hardcodes official external-source candidates for missing SkillGen benchmark components.
- Reason: The POC needs to distinguish unresolved missing data from officially referenced sources that can be pulled into the run package.
- Impact: Only sources supported by official README/script/adapter evidence are treated as valid reproduction intake candidates.

## skillgen_transfer_and_token_claim_tables

- Description: The automation hardcodes the paper's transfer-model display names, transfer benchmark rows, and Table 4 token-cost benchmark rows.
- Reason: These claim-level runner plans are SkillGen-specific and need deterministic row/model names before execution artifacts can be generated.
- Impact: The route IDs, actual token logs, and benchmark outputs still need execution evidence before the corresponding claims can be reproduced.

## skillgen_canonical_benchmark_sources

- Description: The automation records canonical external benchmark repositories for paper-named benchmarks when the SkillGen checkout lacks complete runnable support.
- Reason: The user asked to fetch code for paper-indicated sources even when the paper does not provide a detailed SkillGen-compatible integration.
- Impact: Fetched canonical code is source evidence only until a SkillGen-compatible adapter, split contract, and execution plan are available.

## skillgen_direct_openai_fallback_deviation

- Description: Some additional target executions use a recorded official-code patch that routes openai/* chat calls directly to OpenAI when SKILLGEN_DIRECT_OPENAI_FOR_OPENAI_MODELS=1.
- Reason: The OpenRouter account returned insufficient-credit errors during approved execution, while the user's OpenAI key could execute the same OpenAI model routes.
- Impact: This is a human-visible execution deviation from the unpatched official checkout and must be considered when comparing results to the paper.

## skillgen_table4_reduced_poc_scale_deviation

- Description: Table 4 token groups were executed with reduced POC-scale configs rather than the full paper-scale Table 4 setup.
- Reason: The Phase 0 POC needed to clear non-structural API/cost blockers while keeping the run tractable inside the current project run directory.
- Impact: The run verifies token-log collection mechanics for the ready Table 4 groups, but it does not reproduce the paper's full-scale token totals.

## skillgen_table4_concurrency_retry_deviation

- Description: Some generated Table 4 configs used max_workers=4 for speed; Mind2Web was retried at max_workers=1 after an OpenAI TPM 429 rate-limit failure.
- Reason: Concurrency reduced wall-clock time for long ready targets, while the retry avoided a non-structural provider rate-limit blocker.
- Impact: Concurrency and retry behavior are recorded deviations that may affect latency and token timing, but the raw logs preserve the attempted and successful executions.
