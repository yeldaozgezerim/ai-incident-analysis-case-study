# Methodology

1. Treat event records as observations, not causal conclusions.
2. Keep event time distinct from recording time; order the timeline by event time.
3. Count explicitly identified forwarded copies separately from independent observations.
4. Do not infer shared causes from timing alone.
5. Validate data shape and timestamps, but do not claim this authenticates sources.
6. This tool is read-only; operational changes require separate human review and authorization.

## Interpretation of the synthetic example

An authentication failure predates the limited deployment, so the deployment cannot automatically explain all symptoms. The forwarded copy demonstrates how duplicate messages can inflate apparent evidence volume. A queue delay alone does not prove payment failure. These are invented demonstration observations, not findings about a real client.
