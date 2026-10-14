#!/usr/bin/env python3
"""Run Heliodor's ignored base-core smoke test on an isolated source copy."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "sources/heliodor"


def tree_sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        rel = item.relative_to(path).as_posix().encode()
        digest.update(len(rel).to_bytes(8, "big"))
        digest.update(rel)
        content_hash = hashlib.sha256(item.read_bytes()).digest()
        digest.update(content_hash)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stdout", required=True, type=pathlib.Path)
    parser.add_argument("--stderr", required=True, type=pathlib.Path)
    parser.add_argument("--archive-dir", required=True, type=pathlib.Path,
                        help="durable directory for transformed smoke inputs and metadata")
    parser.add_argument("--work-dir", type=pathlib.Path,
                        help="isolated build directory (defaults to a unique directory under TMPDIR)")
    args = parser.parse_args()

    veryl = shutil.which("veryl")
    if not veryl:
        parser.error("veryl is not on PATH; install the pinned toolchain before running")

    work = args.work_dir.resolve() if args.work_dir else pathlib.Path(
        tempfile.mkdtemp(prefix="heliodor-core-smoke-")
    )
    if work.exists() and any(work.iterdir()):
        parser.error(f"work directory must be empty: {work}")
    work.mkdir(parents=True, exist_ok=True)
    shutil.copytree(SOURCE / "src", work / "src")
    shutil.copy2(SOURCE / "Veryl.toml", work / "Veryl.toml")
    shutil.copy2(SOURCE / "Veryl.lock", work / "Veryl.lock")
    (work / "tb").mkdir()

    test = (SOURCE / "tb/test_smoke.veryl").read_text(encoding="utf-8")
    declaration = "    var imem: logic<32> [16];"
    if test.count(declaration) != 1:
        parser.error("pinned test_smoke imem declaration changed; review the isolated lint workaround")
    test = test.replace(declaration, "    #[allow(initial_assign)]\n" + declaration, 1)
    (work / "tb/test_smoke.veryl").write_text(test, encoding="utf-8")
    (work / "test").mkdir()
    shutil.copy2(SOURCE / "test/v4_smoke.hex", work / "test/v4_smoke.hex")

    archive = args.archive_dir.resolve()
    archive.mkdir(parents=True, exist_ok=True)
    shutil.copy2(work / "tb/test_smoke.veryl", archive / "test_smoke.veryl")
    shutil.copy2(work / "test/v4_smoke.hex", archive / "v4_smoke.hex")
    source_tree_hash = tree_sha256(work)
    metadata = {
        "source_commit": subprocess.check_output(
            ["git", "-C", str(SOURCE), "rev-parse", "HEAD"], text=True).strip(),
        "source_tree_sha256": source_tree_hash,
        "transformed_test_sha256": hashlib.sha256((work / "tb/test_smoke.veryl").read_bytes()).hexdigest(),
        "fixture_sha256": hashlib.sha256((work / "test/v4_smoke.hex").read_bytes()).hexdigest(),
        "command": [veryl, "test", "--include-ignored", "--test", "test_smoke"],
        "runner_invocation": [sys.executable, str(pathlib.Path(__file__).resolve()), *sys.argv[1:]],
    }
    (archive / "run-metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    args.stdout.parent.mkdir(parents=True, exist_ok=True)
    args.stderr.parent.mkdir(parents=True, exist_ok=True)
    command = [veryl, "test", "--include-ignored", "--test", "test_smoke"]
    with args.stdout.open("wb") as stdout, args.stderr.open("wb") as stderr:
        stdout.write((json.dumps(metadata, sort_keys=True) + "\n").encode())
        stdout.write(f"work_dir={work}\ncommand={' '.join(command)}\n".encode())
        stdout.flush()
        result = subprocess.run(command, cwd=work, stdout=stdout, stderr=stderr, check=False)
        stdout.write(f"runner_exit_code={result.returncode}\n".encode())
    print(f"work_dir={work}")
    print(f"command={' '.join(command)}")
    print(f"exit_code={result.returncode}")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
