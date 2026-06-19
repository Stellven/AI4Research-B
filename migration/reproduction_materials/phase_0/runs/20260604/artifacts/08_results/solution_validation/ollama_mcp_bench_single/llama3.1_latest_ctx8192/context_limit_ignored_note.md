# Context Limit Ignored Note

The `llama3.1:latest` ctx8192 attempt was stopped after local Ollama status
showed that the OpenAI-compatible endpoint still loaded the model with:

- `CONTEXT 131072`
- approximately `22 GB` loaded footprint

This indicates that the attempted `extra_body={"options": {"num_ctx": 8192}}`
route did not reduce Ollama's resident context for this model in this setup.
The run was stopped before investing the full benchmark window in the same
resource-bound behavior observed in the unconstrained `llama3.1:latest` run.

The logs and command status are preserved in this directory.
