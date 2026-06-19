# Resource-Stalled Attempt Note

A restarted full-size `llama3.1:latest` training attempt was stopped manually
after local process inspection showed the Ollama runtime using a 131072-token
context with an approximately 22 GB loaded footprint on a 24 GB machine.

Observed progress before termination:

- Baseline trajectories completed: 7 of 40
- Last progress marker: `Baseline trajectories: 18%|...| 7/40 [13:09<1:00:28, 109.94s/it]`
- The next item did not complete after several additional polling windows.
- Command exit code after termination: 143

The resource-stalled attempt was preserved as:

- `train_resource_stalled_stdout.txt`
- `train_resource_stalled_stderr.txt`
- `train_resource_stalled_command_status.json`

The next attempt uses an env-gated local Ollama context limit so the same
OpenAI-compatible local route can run with less memory pressure.
