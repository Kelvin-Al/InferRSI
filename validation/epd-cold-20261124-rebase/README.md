# EPD casebook rebase validation

This record covers PR #506 head `2d4e040aa0337cbfb9bf8fcd429d8a5639008de6` rebased onto main at
`3292402dbc9a22362ac47de28b0026c40c9bd96c`. The casebook and case files
have the same bytes as on the prior review head. Generated catalog inputs
and coverage were rebuilt from source commit `5f66620fbf63b76926aa8678806534a96f360b32`.

The [author-run JUnit record](junit.xml) reports 203 passes, zero failures
and two skips for Windows symlink privileges. The targeted run covered
Knowledge contract, Find, operations, skill catalog, index, install and
CLI tests. Both catalog and coverage freshness checks and targeted Ruff
passed. Checkout `find "EPD cold MMMU GPU allocation stage capacity"`
ranked the case first and its returned command opened the case.

The [verifier](verify.py) fetched the public head into a clean detached
checkout, built and installed the wheel outside that checkout, matched
five installed resource hashes to Git, and found and opened the case
from that non-editable installation. The [build report](report.json)
records the exact commands and resource comparisons.

Wheel SHA-256 `d10d3f864a85efda65f31401dc60348f9cfbfe10513495769421a96c7ffc28bd`.

Experiment acceptance remains INCONCLUSIVE.
