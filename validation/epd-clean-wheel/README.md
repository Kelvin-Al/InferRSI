# Clean-checkout wheel verification for InferRSI PR #506

The author built the retained wheel on Windows amd64 with Python 3.14.6 from
a new checkout of public PR commit
`455f1c8afd2b796c2a3a40d259b3ded246e98d06`. The transcript in
[`report.json`](report.json) records the actual commit, tree, clean status
before the build, tool versions, commands, exit codes and output. It also
records the SHA-256 hashes of five resources read with Git, compared with
their checkout files, wheel entries and installed package bytes.

The wheel is [inferrsi-0.1.dev1+g455f1c8af-py3-none-any.whl](inferrsi-0.1.dev1%2Bg455f1c8af-py3-none-any.whl).
Its SHA-256 is
`8506c97a5d3bdb34cf9a80e7d07e3725ca55677c4efff47ddd0e771eb720e2e2`.
Two author-run builds yielded that hash in this environment.

To repeat the check with Git and Python available, download
[`verify.py`](verify.py) and run it against a new output directory.

```bash
python verify.py --output epd-wheel-verification
```

The script fetches the full public commit into a fresh temporary checkout,
builds in a fresh virtual environment and runs the installed check outside
the checkout with isolated Python. The installed check resolves the EPD
free-text search result through its advertised CLI arguments and verifies
the case resources and generated card. Compare the archive hash using the
recorded Python, platform and build-tool versions. Resource hashes can
also be compared independently with the pinned Git blobs.

These are author-run packaging checks. Independent reproduction and the
repository's review CI remain pending. The H800 campaign retains its
INCONCLUSIVE qualification.
