# Cold EPD Knowledge tool-use check

This author-executed check exercised two prompts about one fixed four-H800 deployment. The Agent was a BF16 Qwen3.8-27B served locally with vLLM on one H800. The deployment scenario was cold single-image MMMU with Qwen2.5-VL-3B-Instruct. Both per-instance rates came from the immutable sizing plan linked in the run specification.

| Observation | Case absent | Original PR case | Structured draft |
| --- | ---: | ---: | ---: |
| Model submitted a successful Find query | 2/2 | 2/2 | 2/2 |
| Model opened the EPD case it found | 0/2 | 2/2 | 2/2 |
| Model submitted arithmetic after that read | 0/2 | 2/2 | 2/2 |
| Arithmetic implemented the bottleneck rule for all three allocations | 0/2 | 2/2 | 2/2 |

The generic calculator evaluated model-authored arithmetic. Each successful case-backed attempt independently used the smaller of the scaled E and PD rates. The capacities from the frozen input rates round to 25.10, 27.43, and 13.71 requests/s for 1E:3PD, 2E:2PD and 3E:1PD, respectively.

The original case bytes came from PR head `44dcedd204445c61f3c0169a65aedd9f3bb51620`. The isolated installed package check on the refreshed head recorded the same original case revision. The structured condition describes a separate experimental draft. The receipt reports author-executed observations on two task wordings for the same deployment. One case-absent trial repeatedly searched until the action limit. One structured-draft trial corrected unsupported calculator assignment syntax and succeeded on retry. The scope is tool use and use of recorded input values. Fresh calibration, sustained service behavior, SLOs and general agent efficacy remain unqualified.

- [Frozen protocol and scheduled arms](spec.json)
- [Task inputs](fixed-tasks.json)
- [Replayed tool actions, returned case hashes and calculations](fixed-tool-audit.json)
- [Conflict resolution and current-head checks](merge-validation.json)
- [Installed-wheel verification script](verify-wheel.py)

