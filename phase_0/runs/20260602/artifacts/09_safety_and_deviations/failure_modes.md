# Failure Modes And Blockers

- `hosted_llm_apis`: Experiments use hosted LLM APIs routed through OpenRouter; provider-side accelerator details are not exposed.
- `paid_token_budget`: The reported runs consume millions of tokens per generated skill and cite API pricing.
- `external_benchmark_assets`: Reproduction requires benchmark-specific datasets/environments and held-out split protocols.
- `proprietary_models`: Some evaluated base models are proprietary hosted models, so exact provider-side inference is not locally reproducible.
