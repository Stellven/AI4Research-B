# Pause / Resume Note

The `gemma3:12b` full training run was suspended to avoid compute and heat while
the machine was being moved.

Pause state:

- SkillGen wrapper shell PID: `57275`
- SkillGen Python child PID: `57293`
- Ollama model server PID: `53181`
- Progress at pause: baseline trajectory collection had reached `15/40`.
- Pause mechanism: `SIGSTOP` was sent to the Python child and Ollama model
  server, not `SIGTERM`.

Resume state:

- Resume mechanism: `SIGCONT` was sent to the Ollama model server and SkillGen
  Python child.
- The run continues writing to `train_stdout.txt` and `train_stderr.txt`.
