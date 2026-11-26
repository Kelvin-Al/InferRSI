from contextlib import redirect_stdout
from hashlib import sha256
from importlib.resources import files
from io import StringIO
import json
from pathlib import Path
import sys
from zipfile import ZipFile

target, checkout, wheel = map(Path, sys.argv[1:])
sys.path.insert(0, str(target))
import inferrsi
from inferrsi.apps.cli import main
from inferrsi.knowledge.knowledge_find import find, load_corpus
from inferrsi.knowledge.knowledge_operations import KnowledgeReader

assert Path(inferrsi.__file__).is_relative_to(target)
root = Path(files("inferrsi").joinpath("knowledge", "data", "skill_library"))
identity = "case.epd-cold-provisioning"
results = find("EPD cold MMMU GPU allocation stage capacity", load_corpus(root), limit=5)
hit = next(item for item in results["items"] if item["id"] == identity)
output = StringIO()
with redirect_stdout(output):
    assert main(hit["read_args"]) == 0
payload = json.loads(output.getvalue())
bundle = KnowledgeReader(skill_root=root).read("checkout:" + identity)
assert payload["revision"] == bundle.revision and payload["id"] == identity
assert "## Position-balanced cold follow-up" in payload["content"]
relative = Path("inferrsi/knowledge/data/skill_library/casebooks/inference/inference-optimization-casebook/cases")
resources = {}
with ZipFile(wheel) as package:
    for name in ("epd-cold-provisioning.md", "epd-cold-provisioning.json"):
        rel = relative / name
        source = (checkout / "src" / rel).read_bytes()
        assert source == (target / rel).read_bytes() == package.read(rel.as_posix()) == bundle.content[name]
        resources[name] = sha256(source).hexdigest()
print(json.dumps({"wheel": wheel.name, "wheel_sha256": sha256(wheel.read_bytes()).hexdigest(),
                  "find_rank": next(i for i, x in enumerate(results["items"], 1) if x["id"] == identity),
                  "case_revision": bundle.revision, "source_wheel_install_bundle_sha256": resources}, indent=2))
