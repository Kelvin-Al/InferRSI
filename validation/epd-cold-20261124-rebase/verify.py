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
HEAD = "2d4e040aa0337cbfb9bf8fcd429d8a5639008de6"
PACKAGES = (
    "setuptools==83.0.0", "setuptools-scm==9.2.2", "wheel==0.47.0",
    "packaging==26.3", "PyYAML==6.0.3",
)
LIBRARY = "inferrsi/knowledge/data/skill_library"
CASE_DIR = f"{LIBRARY}/casebooks/inference/inference-optimization-casebook"
PROJECTION_DIR = f"{LIBRARY}/_compiled"
RESOURCES = (
    f"{CASE_DIR}/SKILL.md",
    f"{CASE_DIR}/cases/epd-cold-provisioning.json",
    f"{CASE_DIR}/cases/epd-cold-provisioning.md",
    f"{PROJECTION_DIR}/_provenance.json",
    f"{PROJECTION_DIR}/inputs.json",
)

INSTALLED_CHECK = '''
import hashlib
import io
import json
from contextlib import redirect_stdout
from importlib.resources import files
from pathlib import Path

import inferrsi
from inferrsi.apps.cli import main
from inferrsi.knowledge.knowledge_operations import KnowledgeReader
from inferrsi.knowledge.skill_catalog import skill_reference

expected = json.loads(Path("resources.json").read_text(encoding="utf-8"))
root = Path(str(files("inferrsi")))
assert Path(inferrsi.__file__).resolve().is_relative_to(Path("installed").resolve())
for name, sha in expected.items():
    assert hashlib.sha256((root / name.removeprefix("inferrsi/")).read_bytes()).hexdigest() == sha

library = root / "knowledge/data/skill_library"
owner = "casebooks/inference/inference-optimization-casebook"
compiled = json.loads((library / "_compiled/inputs.json").read_bytes())
manifest = json.loads((library / "_compiled/_provenance.json").read_bytes())
assert manifest["source_revision"] == "5f66620fbf63b76926aa8678806534a96f360b32"
skill = compiled["inference-optimization-casebook"]
for name in ("SKILL.md", "cases/epd-cold-provisioning.md", "cases/epd-cold-provisioning.json"):
    assert skill["files"][name] == expected[f"inferrsi/knowledge/data/skill_library/{owner}/{name}"]
case_path = skill_reference(library, "inference-optimization-casebook", "cases/epd-cold-provisioning.md")
assert case_path == library / owner / "cases/epd-cold-provisioning.md"

def cli(args):
    out = io.StringIO()
    with redirect_stdout(out):
        assert main(args) == 0
    return json.loads(out.getvalue())

identity = "case.epd-cold-provisioning"
found = cli(["find", "EPD cold MMMU GPU allocation stage capacity", "--limit", "5", "--json"])
hit = next(row for row in found["items"] if row["id"] == identity)
assert hit["path"] == f"{owner}/cases/epd-cold-provisioning.md"
opened = cli(hit["read_args"])
assert opened["id"] == identity
assert "## Position-balanced cold follow-up" in opened["content"]
assert opened["content"].encode("utf-8") == (library / hit["path"]).read_bytes()

reader = KnowledgeReader(skill_root=library)
bundle = reader.read(identity)
record = reader.resource(identity, "epd-cold-provisioning.json", revision=bundle.revision)
key = f"inferrsi/knowledge/data/skill_library/{owner}/cases/epd-cold-provisioning.json"
assert hashlib.sha256(record).hexdigest() == expected[key]
print("Installed outside the checkout; five resource hashes match Git blobs")
print("Compiled catalog contains the registered EPD case and source record")
print("Installed find returned and opened the EPD case:", hit["id"])
print("Case content revision:", bundle.revision)
'''


def sha(data):
    return hashlib.sha256(data).hexdigest()


def verify(output, temp_root=None):
    output.mkdir()
    with tempfile.TemporaryDirectory(prefix="epd-", dir=temp_root) as directory:
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
            if result.returncode:
                failure = report["commands"][-1]
                print(failure["stdout"] or "", file=sys.stderr)
                print(failure["stderr"], file=sys.stderr)
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
    parser.add_argument("--temp-root", type=Path, help="Optional short temporary parent directory")
    args = parser.parse_args()
    verify(args.output.resolve(), args.temp_root)
