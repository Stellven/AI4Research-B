# Benchmark Results

Status: `official_code_smoke_completed`

## Scope

This is an official-code AIME smoke validation. It is not a reproduction of the full SkillGen Table 1 claim.

## Construction-Time Verification

- Skill ID: `c9924dba-ba8a-4735-960c-bc07c129b57c`
- Paired N: `4`
- Baseline accuracy: `50.0%`
- Skill accuracy: `75.0%`
- Repairs: `2`
- Regressions: `1`
- Net gain: `1`
- Verification passed: `True`
- Training token usage: `59226`

## Held-Out Smoke Evaluation

- Model: `openai/gpt-5.4-nano`
- Paired N: `4`
- Baseline accuracy: `25.0%`
- Skill accuracy: `25.0%`
- Accuracy delta: `0.0%`
- Repairs: `0`
- Regressions: `0`
- Net gain: `0`
- Eval token usage: `14396`

## Additional Target Executions

### chemllmbench_property_prediction

- Claim status: `not_reproduced`
- Execution status: `official_code_eval_completed`
- Skill ID: `4c1bf7a1-f237-4900-98dd-7270b39e12d9`
- Skill status: `deprecated`
- Skill rejected: `True`
- Construction baseline accuracy: `50.0%`
- Construction skill accuracy: `50.0%`
- Construction net gain: `0`
- Verification passed: `False`
- Held-out model: `openai/gpt-5.4-nano`
- Held-out paired N: `10`
- Held-out baseline accuracy: `60.0%`
- Held-out skill accuracy: `60.0%`
- Held-out delta: `0.0%`
- Held-out net gain: `0`
- Train token usage: `46661`
- Eval token usage: `1514`

### chemllmbench_yield_prediction

- Claim status: `not_reproduced`
- Execution status: `official_code_eval_completed`
- Skill ID: `ad80410d-3091-43d5-93e2-8721d9f1837d`
- Skill status: `deprecated`
- Skill rejected: `True`
- Construction baseline accuracy: `100.0%`
- Construction skill accuracy: `100.0%`
- Construction net gain: `0`
- Verification passed: `False`
- Held-out model: `openai/gpt-5.4-nano`
- Held-out paired N: `10`
- Held-out baseline accuracy: `70.0%`
- Held-out skill accuracy: `70.0%`
- Held-out delta: `0.0%`
- Held-out net gain: `0`
- Train token usage: `60179`
- Eval token usage: `2931`

### mcp_bench_token

- Claim status: `not_reproduced`
- Execution status: `official_code_eval_completed`
- Skill ID: `b0dfb61d-84a8-42c9-8c98-50369635966c`
- Skill status: `deprecated`
- Skill rejected: `True`
- Construction baseline accuracy: `50.0%`
- Construction skill accuracy: `50.0%`
- Construction net gain: `0`
- Verification passed: `False`
- Held-out model: `openai/gpt-5.4-nano`
- Held-out paired N: `16`
- Held-out baseline accuracy: `93.8%`
- Held-out skill accuracy: `93.8%`
- Held-out delta: `0.0%`
- Held-out net gain: `0`
- Train token usage: `448252`
- Eval token usage: `120830`

### mind2web_token

- Claim status: `not_reproduced`
- Execution status: `official_code_eval_completed`
- Skill ID: `50227d88-7b7f-471d-81ae-d8456f4fc531`
- Skill status: `deprecated`
- Skill rejected: `True`
- Construction baseline accuracy: `75.0%`
- Construction skill accuracy: `50.0%`
- Construction net gain: `-1`
- Verification passed: `False`
- Held-out model: `openai/gpt-5.4-nano`
- Held-out paired N: `100`
- Held-out baseline accuracy: `54.0%`
- Held-out skill accuracy: `54.0%`
- Held-out delta: `0.0%`
- Held-out net gain: `0`
- Train token usage: `674323`
- Eval token usage: `265899`

### pubmedqa_token

- Claim status: `not_reproduced`
- Execution status: `official_code_eval_completed`
- Skill ID: `5d98c0bd-bada-4992-a666-6a75f89deb38`
- Skill status: `active`
- Skill rejected: `False`
- Construction baseline accuracy: `75.0%`
- Construction skill accuracy: `100.0%`
- Construction net gain: `1`
- Verification passed: `True`
- Held-out model: `openai/gpt-5.4-nano`
- Held-out paired N: `100`
- Held-out baseline accuracy: `74.0%`
- Held-out skill accuracy: `70.0%`
- Held-out delta: `-4.0%`
- Held-out net gain: `-4`
- Train token usage: `280169`
- Eval token usage: `167834`

### scienceworld_token

- Claim status: `partially_reproduced`
- Execution status: `official_code_eval_completed`
- Skill ID: `20d74b11-1654-4f2f-a0b5-d7502948b56d`
- Skill status: `active`
- Skill rejected: `False`
- Construction baseline accuracy: `25.0%`
- Construction skill accuracy: `100.0%`
- Construction net gain: `3`
- Verification passed: `True`
- Held-out model: `openai/gpt-5.4-nano`
- Held-out paired N: `100`
- Held-out baseline accuracy: `31.0%`
- Held-out skill accuracy: `35.0%`
- Held-out delta: `4.0%`
- Held-out net gain: `4`
- Train token usage: `588035`
- Eval token usage: `476046`

### tau_bench_retail

- Claim status: `not_reproduced`
- Execution status: `official_code_eval_completed`
- Skill ID: `28b0778e-7dd4-4f88-a89e-c4f39df3c9a1`
- Skill status: `deprecated`
- Skill rejected: `True`
- Construction baseline accuracy: `75.0%`
- Construction skill accuracy: `50.0%`
- Construction net gain: `-1`
- Verification passed: `False`
- Held-out model: `openai/gpt-5.4-nano`
- Held-out paired N: `30`
- Held-out baseline accuracy: `23.3%`
- Held-out skill accuracy: `23.3%`
- Held-out delta: `0.0%`
- Held-out net gain: `0`
- Train token usage: `1629346`
- Eval token usage: `1569988`
