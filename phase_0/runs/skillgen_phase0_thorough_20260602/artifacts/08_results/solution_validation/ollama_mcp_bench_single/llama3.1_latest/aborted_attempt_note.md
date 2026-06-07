# Aborted Attempt Note

An initial `llama3.1:latest` full-size training attempt was stopped manually
after 196 seconds while estimating runtime during baseline collection. At that
point, 2 of 40 baseline trajectories had completed and the command exited with
code 143.

The aborted attempt was preserved as:

- `train_aborted_stdout.txt`
- `train_aborted_stderr.txt`
- `train_aborted_command_status.json`

After the supervisor clarified that an 18-hour runtime window is acceptable, the
full-size run was restarted and writes to the required `train_stdout.txt`,
`train_stderr.txt`, and `train_command_status.json` files.
