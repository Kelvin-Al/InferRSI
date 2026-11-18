# InferRSI cold EPD follow-up validation

PR head: `255887cd3633a7e3eb59bd9bfca461641aa76f50`

The author ran the tests on that revision and checked its head before and after
the test run. The [JUnit result](junit.xml) recorded 133 passes with zero
failures, errors or skips. Hostname and timestamp attributes were omitted.

```text
python -m pytest tests/test_knowledge_contract.py tests/test_knowledge_operations.py tests/test_knowledge_find.py tests/test_skill_library.py tests/test_skill_index.py --tb=short
python tools/build_skill_index.py --source-revision 2dabbfe50ddddc872c030ba962b570fa2488e770 --check
python -m ruff check tests/test_knowledge_contract.py tests/test_knowledge_find.py
```

The targeted Ruff check and generator freshness check both exited successfully.
The generator reported 80 current skill records.

The [verification script](verify.py) fetched the exact public head into a clean
detached checkout, built the wheel with pinned build dependencies and installed
it outside the checkout. The [report](report.json) records the commands, Git
tree, artifact identity and five Git/wheel/installed resource hash checks. The
installed Knowledge case opened through the EPD search result and reader.

Wheel SHA-256: `42d1d956f6210bd28c26ef7f1925f7b555df9e55968559ab5b0382cf5b27555e`

This is author-executed evidence for the Knowledge update. The cold GPU
observations are retained separately with INCONCLUSIVE campaign acceptance.
