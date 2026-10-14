from __future__ import annotations

import importlib.util
import pathlib
import struct
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
CASES = {"standard": 0x0000100F, "funct12": 0x0010100F,
         "rs1": 0x0000900F, "rd": 0x0000108F}


def load(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


kunming = load("kunminghu_topic_runner", ROOT / "experiments/kunminghu-smoke/run.py")
heliodor = load("heliodor_topic_runner", ROOT / "experiments/heliodor-smoke/run.py")
image_builder = load("zifencei_image_builder", ROOT / "experiments/rva23s64-zifencei/build_images.py")


def assert_equal_image_lengths(images: dict[str, bytes]) -> None:
    lengths = {len(image) for image in images.values()}
    assert len(lengths) <= 1, f"image lengths differ: {sorted(lengths)}"


def test_four_images_change_only_one_reserved_fence_i_field() -> None:
    root = ROOT / "experiments/rva23s64-zifencei"
    images = {}
    for case, expected in CASES.items():
        words = [int(line, 16) for line in (root / f"{case}.hex").read_text().splitlines()]
        image = struct.pack("<" + "I" * len(words), *words)
        assert words[8] == expected
        assert len(image) >= 0x1008
        images[case] = image
        source = (root / f"{case}.S").read_text()
        assert f".word   0x{expected:08x}" in source
    assert (root / "fixture.ld").read_text().find(". = 0x80000000;") >= 0
    assert_equal_image_lengths(images)
    standard = images["standard"]
    for case, image in images.items():
        differences = [i for i, (a, b) in enumerate(zip(standard, image)) if a != b]
        expected_diff = {"standard": [], "funct12": [34], "rs1": [33], "rd": [32]}[case]
        assert differences == expected_diff


def test_image_difference_rejects_mismatched_lengths() -> None:
    with pytest.raises(AssertionError, match="image lengths differ"):
        assert_equal_image_lengths({"standard": b"\0" * 8, "truncated": b"\0" * 4})


def test_image_builder_checks_cross_tool_versions_and_symbols(monkeypatch: pytest.MonkeyPatch,
                                                              tmp_path: pathlib.Path) -> None:
    def completed(stdout: str):
        return type("Completed", (), {"stdout": stdout, "stderr": "", "returncode": 0})()

    monkeypatch.setattr(image_builder.subprocess, "run", lambda *_args, **_kwargs:
                        completed(image_builder.EXPECTED_GCC + "\n"))
    image_builder.tool_version("gcc", image_builder.EXPECTED_GCC)
    monkeypatch.setattr(image_builder.subprocess, "run", lambda *_args, **_kwargs:
                        completed("unexpected compiler version\n"))
    with pytest.raises(SystemExit, match="expected"):
        image_builder.tool_version("gcc", image_builder.EXPECTED_GCC)
    tool = tmp_path / "cross-tool"
    tool.write_bytes(b"pinned tool bytes")
    import hashlib
    digest = hashlib.sha256(tool.read_bytes()).hexdigest()
    image_builder.verify_tool_hash(str(tool), digest)
    with pytest.raises(SystemExit, match="SHA-256"):
        image_builder.verify_tool_hash(str(tool), "0" * 64)

    elf = tmp_path / "fixture.elf"
    elf.write_bytes(b"fixture")
    monkeypatch.setattr(image_builder.subprocess, "run", lambda *_args, **_kwargs:
                        completed("0000000080000000 T _start\n0000000080000020 T fence_i_instruction\n"))
    assert image_builder.symbol_addresses("nm", elf) == {
        "_start": 0x80000000, "fence_i_instruction": 0x80000020}


def test_reserved_field_encodings_are_independent() -> None:
    assert CASES["funct12"] ^ CASES["standard"] == 1 << 20
    assert CASES["rs1"] ^ CASES["standard"] == 1 << 15
    assert CASES["rd"] ^ CASES["standard"] == 1 << 7


def test_kunminghu_classifies_unstarted_blocked_and_started_failure() -> None:
    blocked = kunming.classify_output("", 1)
    assert blocked["result"] == "blocked"
    started_fail = kunming.classify_output(kunming.FIRST_COMMIT, 1)
    assert started_fail["result"] == "run-fail"
    assert started_fail["cpu_started"] is True


def test_heliodor_observes_success_for_zifencei_label() -> None:
    output = ("[test_smoke] cy=5000 x10=0007 x11=000b commit=1651\n"
              "[test_smoke] x12=004d x13=000b\n[test_smoke] PASS\n"
              "v4 rv64ui-fence_i tohost=00000001 pass=1\n"
              "v4 rv64ui-fence_i PASS\n")
    started, values, passed, failed = heliodor.observe(output, 0, "v4 rv64ui-fence_i")
    assert started is True
    assert values["arch_tohost"] == 1 and values["arch_pass"] == 1
    assert passed is True and failed is False


def test_heliodor_classifies_unstarted_blocked_and_started_failure() -> None:
    blocked = heliodor.observe("", 1, "v4 rv64ui-fence_i")
    assert blocked[0] is False and blocked[2] is False
    started_fail = heliodor.observe("v4 rv64ui-fence_i tohost=00000003 pass=0", 0,
                                    "v4 rv64ui-fence_i")
    assert started_fail[0] is True and started_fail[2] is False and started_fail[3] is True


def test_heliodor_zifencei_does_not_infer_target_start_from_prior_smoke() -> None:
    prior_smoke_only = "[test_smoke] cy=5000 x10=0007 commit=1651\n[test_smoke] PASS\n"
    result = heliodor.observe(prior_smoke_only, 1, "v4 rv64ui-fence_i")
    assert result[0] is False and result[2] is False and result[3] is False


def test_heliodor_transforms_the_pinned_fence_i_arch_target() -> None:
    source = (ROOT / "sources/heliodor/tb/test_arch_common.veryl").read_text()
    result = heliodor.transform_arch_harness(
        source, target="test_arch_rv64ui_fence_i",
        fixture="test/zifencei/standard.hex", label="v4 rv64ui-fence_i")
    assert "test/zifencei/standard.hex" in result
    assert "v4 rv64ui-fence_i PASS" in result
    assert "module test_arch_rv64ui_fence_i" in result
    assert "test_arch_rv64ui_add" not in result


@pytest.mark.parametrize("replacement", ["", 'HEX_FILE  : "a.hex",\n        HEX_FILE: "b.hex",'])
def test_heliodor_rejects_missing_or_duplicate_fixture_anchor(replacement: str) -> None:
    source = (ROOT / "sources/heliodor/tb/test_arch_common.veryl").read_text()
    target = source.split("#[test(test_arch_rv64ui_fence_i)]", 1)[1].split("#[test(", 1)[0]
    target = "#[test(test_arch_rv64ui_fence_i)]" + target
    target = __import__("re").sub(r'HEX_FILE\s*:\s*"[^"]+"', replacement, target, count=1)
    source = source.replace(
        "#[test(test_arch_rv64ui_fence_i)]" + source.split("#[test(test_arch_rv64ui_fence_i)]", 1)[1].split("#[test(", 1)[0],
        target)
    with pytest.raises(ValueError, match="HEX_FILE anchor drifted"):
        heliodor.transform_arch_harness(source, target="test_arch_rv64ui_fence_i",
                                        fixture="test/zifencei/standard.hex")


def test_kunminghu_rejects_case_without_zifencei_topic(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["run.py", "--case", "standard"])
    with pytest.raises(SystemExit) as error:
        kunming.main()
    assert error.value.code == 2


def test_kunminghu_rejects_unsupported_case_stem_before_creating_evidence(
        tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    topic_dir = tmp_path / "experiments/rva23s64-zifencei"
    topic_dir.mkdir(parents=True)
    unsupported = topic_dir / "unknown.S"
    unsupported.write_text(".text\n", encoding="ascii")
    evidence = tmp_path / "evidence"
    monkeypatch.setattr(kunming, "ROOT", tmp_path)
    monkeypatch.setattr(sys, "argv", ["run.py", "--topic", "zifencei", "--input",
                                      str(unsupported), "--evidence-dir", str(evidence)])
    with pytest.raises(SystemExit) as error:
        kunming.main()
    assert error.value.code == 2
    assert not evidence.exists()
