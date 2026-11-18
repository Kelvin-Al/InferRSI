"""Build and validate InferRSI PR #506 from its public Git commit."""

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


REPOSITORY = "https://github.com/Kelvin-Al/InferRSI.git"
HEAD = "455f1c8afd2b796c2a3a40d259b3ded246e98d06"
PACKAGES = (
    "setuptools==83.0.0", "setuptools-scm==9.2.2", "wheel==0.47.0",
    "packaging==26.3", "PyYAML==6.0.3",
)
LIBRARY = "inferrsi/knowledge/data/skill_library"
CASE_DIR = f"{LIBRARY}/methods/inference-optimization-casebook"
PROJECTION_DIR = "inferrsi/knowledge/data/repo_packs/inferrsi/knowledge"
RESOURCES = (
    f"{CASE_DIR}/SKILL.md",
    f"{CASE_DIR}/cases/epd-cold-provisioning.json",
    f"{CASE_DIR}/cases/epd-cold-provisioning.md",
    f"{PROJECTION_DIR}/_provenance.json",
    f"{PROJECTION_DIR}/common/skills/inference-optimization-casebook.json",
)

INSTALLED_CHECK = '''
import hashlib
import json
from pathlib import Path
from importlib.resources import files
import inferrsi
from inferrsi.knowledge.catalog import search_knowledge
from inferrsi.knowledge.knowledge_operations import KnowledgeReader
from inferrsi.knowledge.knowledge_find import find, load_corpus

expected = json.loads(Path("resources.json").read_text(encoding="utf-8"))
root = Path(str(files("inferrsi")))
assert Path(inferrsi.__file__).resolve().is_relative_to(Path("installed").resolve())
for name, sha in expected.items():
    assert hashlib.sha256((root / name.removeprefix("inferrsi/")).read_bytes()).hexdigest() == sha
library = root / "knowledge/data/skill_library"
reader = KnowledgeReader(skill_root=library)
identity = "case.epd-cold-provisioning"
assert identity in reader.cases()
hit = next(row for row in find("EPD cold MMMU GPU allocation stage capacity",
                               load_corpus(library), limit=5)["items"] if row["id"] == identity)
from inferrsi.apps.cli import main
import contextlib
import io
stdout = io.StringIO()
with contextlib.redirect_stdout(stdout):
    assert main(hit["read_args"]) == 0
assert "## Cold observation" in json.loads(stdout.getvalue())["content"]
bundle = reader.read(identity)
for name in ("epd-cold-provisioning.md", "epd-cold-provisioning.json"):
    path = next(path for path in expected if path.endswith("/cases/" + name))
    assert hashlib.sha256(reader.resource(identity, name, revision=bundle.revision)).hexdigest() == expected[path]
card = next(row for row in search_knowledge(repo="inferrsi", limit=100)
            if row["id"] == "inferrsi.common.skills.inference_optimization_casebook")
for name, sha in expected.items():
    if "/skill_library/" in name:
        assert card["source_files"]["src/" + name] == sha
snapshot = json.loads((root / "knowledge/data/repo_packs/inferrsi/knowledge/_provenance.json").read_bytes())
assert card["sources"][0]["commit"] == snapshot["source_revision"]
print("Installed from verified wheel outside the checkout")
print("Five installed resource hashes match their Git blobs")
print("EPD free-text search returned an openable case; reader resource bytes match")
print("Generated card matches the three source hashes and shared provenance")
print("Case content revision:", bundle.revision)
'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify(output):
    output.mkdir()
    with tempfile.TemporaryDirectory(prefix="inferrsi-epd-") as directory:
        work = Path(directory)
        repo, env_dir = work / "checkout", work / "venv"
        repo.mkdir()
        report = {"public_repository": REPOSITORY, "expected_head": HEAD,
                  "python": sys.version.split()[0], "os": platform.system(),
                  "architecture": platform.machine(), "commands": []}
        env = {k: v for k, v in os.environ.items()
               if not k.startswith(("GIT_", "PIP_", "SETUPTOOLS_SCM_"))
               and k not in {"PYTHONPATH", "PYTHONHOME", "SOURCE_DATE_EPOCH"}}
        env.update(GIT_TERMINAL_PROMPT="0", PYTHONUTF8="1", PIP_DISABLE_PIP_VERSION_CHECK="1",
                   PIP_CONFIG_FILE=os.devnull, PIP_NO_INPUT="1")

        def clean(value):
            paths = ((work, "<work>"), (Path(sys.executable), "python"),
                     (Path(tempfile.gettempdir()), "<temp>"))
            for path, replacement in paths:
                for spelling in {str(path), path.as_posix()}:
                    value = re.sub(re.escape(spelling), replacement, value, flags=re.IGNORECASE)
            return value.replace("\r\n", "\n").replace("\r", "\n")

        def run(command, cwd=work, binary=False):
            result = subprocess.run(list(map(str, command)), cwd=cwd, env=env,
                                    capture_output=True, check=False)
            report["commands"].append({
                "command": [clean(str(part)) for part in command], "cwd": clean(str(cwd)),
                "exit_code": result.returncode,
                "stdout": None if binary else clean(result.stdout.decode("utf-8", "replace")).strip(),
                "stderr": clean(result.stderr.decode("utf-8", "replace")).strip(),
            })
            result.check_returncode()
            return result.stdout if binary else result.stdout.decode("utf-8").strip()

        def git(*args, binary=False):
            return run(["git", "--no-replace-objects", *args], repo, binary=binary)

        git("init", "--quiet")
        git("config", "core.autocrlf", "false")
        git("fetch", "--no-tags", "--depth=1", REPOSITORY, HEAD)
        git("checkout", "--quiet", "--detach", "FETCH_HEAD")
        report["actual_head"] = git("rev-parse", "HEAD")
        report["tree"] = git("rev-parse", "HEAD^{tree}")
        report["pre_build_status"] = git("status", "--porcelain=v1", "--untracked-files=all",
                                         "--ignored=matching")
        assert report["actual_head"] == HEAD and report["pre_build_status"] == ""
        env["SOURCE_DATE_EPOCH"] = git("show", "-s", "--format=%ct", HEAD)
        report["source_date_epoch"] = env["SOURCE_DATE_EPOCH"]
        expected = {}
        for path in RESOURCES:
            blob = git("cat-file", "blob", f"HEAD:src/{path}", binary=True)
            assert blob == (repo / "src" / path).read_bytes(), path
            expected[path] = sha(blob)
        report["git_and_checkout_sha256"] = expected

        run([sys.executable, "-m", "venv", env_dir])
        py = env_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
        run([py, "-m", "pip", "install", "--quiet", "--index-url", "https://pypi.org/simple",
             *PACKAGES])
        report["build_tools"] = json.loads(run([py, "-m", "pip", "list", "--format=json"]))
        dist = work / "dist"
        run([py, "-m", "pip", "wheel", "--no-deps", "--no-build-isolation", "--no-index",
             "--wheel-dir", dist, "."], repo)
        wheel, = dist.glob("*.whl")
        with zipfile.ZipFile(wheel) as archive:
            entries = {path: sha(archive.read(path)) for path in expected}
        assert entries == expected
        report["wheel"] = {"filename": wheel.name, "sha256": sha(wheel.read_bytes()),
                           "size_bytes": wheel.stat().st_size, "entry_sha256": entries}
        installed = work / "installed"
        run([py, "-m", "pip", "install", "--no-deps", "--no-index", "--target", installed, wheel])
        (work / "resources.json").write_text(json.dumps(expected), encoding="utf-8")
        installer = "import sys; sys.path.insert(0, 'installed');\n" + INSTALLED_CHECK
        run([py, "-I", "-c", installer])
        report["post_build_tracked_status"] = git("status", "--porcelain=v1",
                                                  "--untracked-files=no")
        assert report["post_build_tracked_status"] == ""
        (output / wheel.name).write_bytes(wheel.read_bytes())
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(report["commands"][-2]["stdout"])
        print(f"Head {HEAD} · tree {report['tree']}")
        print(f"Wheel {wheel.name} · SHA-256 {report['wheel']['sha256']}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New evidence directory")
    verify(parser.parse_args().output.resolve())
