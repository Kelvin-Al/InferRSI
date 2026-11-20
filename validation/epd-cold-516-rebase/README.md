# Cold E:PD casebook rebase validation

PR head `3c0dc17adfad7e04819025372f4cee74c7e55ff9` rebased onto main at `1b826b5f9666a8b734000e1eb2990e582cdef876`.

The author-run [JUnit record](junit.xml) reports 203 passes, zero failures and
two skips for Windows symlink privileges. A short pytest temporary directory
kept copied fixture paths within Windows limits. Local host information and
temporary paths were omitted from the public JUnit file.

```sh
python -m pytest tests/test_knowledge_contract.py tests/test_knowledge_find.py tests/test_knowledge_operations.py tests/test_skill_catalog.py tests/test_skill_index.py tests/test_knowledge_install.py tests/test_knowledge_cli.py --basetemp <short-unused-temp-dir>
python tools/build_skill_index.py --source-revision 55cb1c5a945bae7e9dbd211b9f6662af143472dd --check
python tools/build_skill_coverage.py --check
python -m ruff check tests/test_knowledge_contract.py tests/test_knowledge_find.py
inferrsi find "EPD cold MMMU GPU allocation stage capacity" --limit 5 --json
```

The checkout CLI ranked `case.epd-cold-provisioning` first and opened the
position-balanced follow-up using its returned `read_args`. The two freshness
checks and targeted Ruff passed. Both case files match the preceding PR head.

The [verification script](verify.py) fetched the exact head into a clean
detached checkout, built a wheel and installed it in isolation. Its
[report](report.json) records the Git tree, build inputs, matching hashes for
five resources and the successful installed `find` and read. The run used
`--temp-root` with a short writable parent directory on Windows.

Wheel SHA-256 `0613c33d49bcf5aad3b077af2a65a72fa29556ab9aa784ff96c3393b7beb5be3`.

This evidence covers the rebase, registration and package retrieval. The
external experiments retain INCONCLUSIVE campaign acceptance.
