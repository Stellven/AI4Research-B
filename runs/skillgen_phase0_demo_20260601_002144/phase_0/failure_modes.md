# Failure Modes And Blockers

- `hosted_llm_apis`: Official execution requires hosted LLM APIs routed through OpenRouter/OpenAI.
- `paid_token_budget`: Even the smoke run consumes paid/tokenized API calls.
- `api_keys_not_visible`: `OPENROUTER_API_KEY` and `OPENAI_API_KEY` are not visible in the current Codex shell environment.
- `readme_eval_cli_mismatch`: README eval command uses flags that current `eval_skill.py` does not define.
- `smoke_not_reproduction`: The selected AIME smoke target is a cost-control validation of official code, not reproduction of Table 1.
