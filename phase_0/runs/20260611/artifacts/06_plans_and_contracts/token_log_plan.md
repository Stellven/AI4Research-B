# Token Log Plan

Token-log collection and aggregation plan for SkillGen Table 4

Paper claim: Train token cost ranges from 2.2M to 10.2M tokens; mean is 5.6M tokens and mean cost is about $8.2 per generated skill.

## Benchmark Groups

| Benchmark | Dataset status | Paper train M tok | BASE tok/call | SKILL tok/call |
| --- | --- | --- | --- | --- |
| `ScienceWorld` | `ready_for_execution` | `2.2` | `1630` | `1977` |
| `PubMedQA` | `ready_for_execution` | `2.7` | `1173` | `2429` |
| `Mind2Web` | `ready_for_execution` | `5.2` | `4482` | `5919` |
| `MCPBench` | `ready_for_execution` | `7.5` | `4847` | `6000` |
| `tau-Bench` | `ready_for_execution` | `10.2` | `5813` | `6358` |

## Current Observed Logs

- No token logs found yet.

## Remaining Blockers

- Full benchmark runs have not produced Table 4 grouped token logs yet.
