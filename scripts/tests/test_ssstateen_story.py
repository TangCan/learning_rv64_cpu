import hashlib
import importlib.util
import json
import pathlib
import re
import shutil
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_ssstateen_gate_operations_have_stable_unique_ids():
    source = (ROOT / "experiments/ssstateen/kunminghu_probe_operation_ids.S").read_text(encoding="utf-8")
    hs = source.split("hs_blocked:", 1)[1].split("hs_enabled:", 1)[0]
    operations = []
    lines = hs.splitlines()
    for index, line in enumerate(lines):
        match = re.search(r"li\s+t6,\s*(\d+)", line)
        if not match:
            continue
        op_id = int(match.group(1))
        following = "\n".join(lines[index + 1:index + 3])
        op = re.search(r"\b(csr[wr]|ecall)\b(?:\s+(0x[0-9a-fA-F]+|[a-z0-9_.]+))?", following)
        assert op, f"operation {op_id} has no following CSR instruction/ecall"
        operations.append((op_id, op.group(1), op.group(2)))
    assert [item[0] for item in operations] == list(range(1, 22))
    assert len({item[0] for item in operations}) == 21
    assert operations[-1][1] == "ecall"
    assert sum(item[1] in {"csrw", "csrr"} for item in operations[:20]) == 20


def test_isolated_case_generation_selects_assertions_and_fixture(tmp_path):
    runner_path = ROOT / "experiments/ssstateen/run_isolated.py"
    spec = importlib.util.spec_from_file_location("isolated_ssstateen", runner_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    assert set(module.CASES) == set(module.FIXTURES)
    assert set(module.CASES) == set(module.CASE_ASSERTIONS)
    assert len(module.FIXTURES.values()) == len(set(module.FIXTURES.values()))
    fixtures = ROOT / "experiments/ssstateen"
    for case in module.CASES:
        result = subprocess.run(["python3", str(runner_path), "--case", case], check=True,
                                capture_output=True, text=True)
        workspace = pathlib.Path(result.stdout.strip().splitlines()[-1])
        try:
            generated = (workspace / "tb/test_arch_common.veryl").read_text()
            selected_fixture = fixtures / module.FIXTURES[case]
            assert module.CASE_ASSERTIONS[case] in generated
            assert (workspace / "test/ssstateen/ssstateen_probe.hex").read_bytes() == selected_fixture.read_bytes()
            assert 'HEX_FILE: "test/ssstateen/ssstateen_probe.hex"' in generated or \
                'HEX_FILE  : "test/ssstateen/ssstateen_probe.hex"' in generated
        finally:
            shutil.rmtree(workspace)
    try:
        module.fixture_for("unknown")
    except ValueError as exc:
        assert "unknown Ssstateen case" in str(exc)
    else:
        raise AssertionError("unknown case was accepted")


def test_rva23_runtime_matrix_completeness_and_operation_ids():
    spec = importlib.util.spec_from_file_location(
        "rva23_runtime_matrices", ROOT / "scripts/check_rva23_run_matrices.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    assert module.validate() == []


def _matrix_checker_fixture(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location(
        "rva23_runtime_matrices_negative", ROOT / "scripts/check_rva23_run_matrices.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    docs = tmp_path / "notes/units"
    docs.mkdir(parents=True)
    for name in ("rva23s64-ssnpm-v1.md", "rva23s64-ssstateen-v1.md"):
        shutil.copy2(ROOT / "notes/units" / name, docs / name)
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text(json.dumps({"snapshots": [{"runs": [{
        "id": "sample", "result": "run-pass", "operation_records": [{
            "operation_id": 1, "mode": "U", "csr": "sstateen0", "operation": "read",
            "expected": "value", "observed": "value",
        }],
    }]}]}), encoding="utf-8")
    monkeypatch.setattr(module, "ROOT", tmp_path)
    monkeypatch.setattr(module, "MANIFEST", manifest)
    return module, docs, manifest


def test_matrix_checker_reports_missing_heading_and_duplicate_required_rows(tmp_path, monkeypatch):
    module, docs, _manifest = _matrix_checker_fixture(tmp_path, monkeypatch)
    path = docs / "rva23s64-ssnpm-v1.md"
    path.write_text(path.read_text().replace("### 逐核、逐模式状态", "### missing"), encoding="utf-8")
    assert any("missing heading" in error for error in module.validate())

    module, docs, _manifest = _matrix_checker_fixture(tmp_path / "duplicate", monkeypatch)
    path = docs / "rva23s64-ssnpm-v1.md"
    text = path.read_text()
    row = next(line for line in text.splitlines() if line.startswith("| Integer load/store | `tested`"))
    text = text.replace("\n## Heliodor 案例与验证记录", f"\n{row}\n## Heliodor 案例与验证记录", 1)
    path.write_text(text, encoding="utf-8")
    assert any("duplicate rows" in error for error in module.validate())


def test_matrix_checker_reports_missing_row_state_and_evidence_reference(tmp_path, monkeypatch):
    module, docs, _manifest = _matrix_checker_fixture(tmp_path, monkeypatch)
    path = docs / "rva23s64-ssnpm-v1.md"
    lines = path.read_text().splitlines()
    for index, line in enumerate(lines):
        if line.startswith("| Zicfiss shadow-stack access |"):
            lines[index] = line.replace("Zicfiss shadow-stack access", "Removed row", 1)
        if line.startswith("| Atomic LR/SC/AMO |"):
            cells = line.strip().strip("|").split("|")
            cells[1] = " canonical behavior (state omitted) "
            cells[4] = " tested "
            cells[-1] = " none "
            lines[index] = "|" + "|".join(cells) + "|"
    text = "\n".join(lines) + "\n"
    path.write_text(text, encoding="utf-8")
    errors = module.validate()
    assert any("missing rows" in error for error in errors)
    assert any("no allowed evidence state" in error for error in errors)
    assert any("no evidence ID" in error for error in errors)


def test_matrix_checker_rejects_undefined_evidence_id(tmp_path, monkeypatch):
    module, docs, _manifest = _matrix_checker_fixture(tmp_path, monkeypatch)
    path = docs / "rva23s64-ssnpm-v1.md"
    lines = path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        if line.startswith("| Atomic LR/SC/AMO |"):
            cells = line.strip().strip("|").split("|")
            cells[-1] = " E99 "
            lines[index] = "|" + "|".join(cells) + "|"
            break
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    errors = module.validate()
    assert any("undefined evidence ID/range E99" in error for error in errors)


def test_matrix_checker_reports_invalid_result_duplicate_ids_and_missing_observation(tmp_path, monkeypatch):
    module, _docs, manifest = _matrix_checker_fixture(tmp_path, monkeypatch)
    data = json.loads(manifest.read_text())
    run = data["snapshots"][0]["runs"][0]
    run["result"] = "pass"
    run["operation_records"].append(dict(run["operation_records"][0], observed=""))
    run["operation_records"][0].pop("observed")
    manifest.write_text(json.dumps(data), encoding="utf-8")
    errors = module.validate()
    assert any("invalid result state" in error for error in errors)
    assert any("duplicate operation_id" in error for error in errors)
    assert any("missing observation" in error for error in errors)


def test_matrix_checker_reports_malformed_yaml_containers_without_crashing(tmp_path, monkeypatch):
    module, _docs, manifest = _matrix_checker_fixture(tmp_path, monkeypatch)
    manifest.write_text("[]\n", encoding="utf-8")
    assert any("root must be a mapping" in error for error in module.validate())
    manifest.write_text(json.dumps({"snapshots": [{"runs": {}}]}), encoding="utf-8")
    assert any("runs must be a list" in error for error in module.validate())
    manifest.write_text(json.dumps({"snapshots": ["not a mapping"]}), encoding="utf-8")
    assert any("must be a mapping" in error for error in module.validate())
    manifest.write_text(json.dumps({"snapshots": [{"runs": [{"result": [], "operation_records": {}}]}]}),
                        encoding="utf-8")
    errors = module.validate()
    assert any("invalid result state" in error for error in errors)
    assert any("operation_records must be a list" in error for error in errors)
    manifest.write_text(json.dumps({"snapshots": [{"runs": [{
        "result": "run-pass", "operation_records": [{
            "operation_id": [], "mode": "U", "csr": "sstateen0", "operation": "read",
            "expected": "value", "observed": "value",
        }],
    }]}]}), encoding="utf-8")
    assert any("operation_id must be an integer" in error for error in module.validate())


def test_ssstateen_m_operations_have_unique_trace_ids():
    source = (ROOT / "experiments/ssstateen/kunminghu_probe_operation_ids.S").read_text(encoding="utf-8")
    assert "csrw    pmpaddr0, t0" in source and "csrw    pmpcfg0, t0" in source
    runner = (ROOT / "experiments/kunminghu-smoke/run.py").read_text(encoding="utf-8")
    m_prefix = source.split("hs_blocked:", 1)[0]
    m_suffix = source.split("hs_enabled:", 1)[1].split("/* Assert M reset", 1)[0]
    m_handler = source.split("m_trap:", 1)[1].split("trap_resume:", 1)[0]
    operation_ids = [int(value) for text in (m_prefix, m_suffix, m_handler)
                     for value in re.findall(r"li\s+t6,\s*(\d+)", text)]
    assert len(operation_ids) == len(set(operation_ids))
    assert set(range(1001, 1005)).issubset(operation_ids)
    assert set(range(1091, 1099)).issubset(operation_ids)
    assert "def parse_ssstateen_trace" in runner
    assert "operation_records\": parse_ssstateen_trace" in runner


def test_kunminghu_operation_parser_handles_real_truncated_commit_trace():
    log = (ROOT / "notes/units/evidence/smoke/kunminghu-ssstateen-operation-trace-20261014/"
           "kunminghu-fixture-20261014T123122Z-069b00f3c8db/output.log").read_text(encoding="utf-8")
    runner_path = ROOT / "experiments/kunminghu-smoke/run.py"
    spec = importlib.util.spec_from_file_location("ssstateen_trace_runner", runner_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    rows = {row["operation_id"]: row for row in module.parse_ssstateen_trace(log)}

    assert rows[1021]["observed"] == "write instruction committed; source register value unavailable"
    assert rows[1021]["trace_pc"] == "0x00000000800000b8"
    assert "marker 1021 is absent" in rows[1021]["operation_id_source"]
    assert rows[1032]["observed"].startswith("readback=0x0000000000000001")
    assert rows[1]["cause_status"] == "not-reached"
    assert rows[21]["observed"].startswith("not-reached:")


def test_ssstateen_hs_gate_ids_map_all_four_s_and_h_csrs():
    runner_path = ROOT / "experiments/kunminghu-smoke/run.py"
    spec = importlib.util.spec_from_file_location("ssstateen_gate_specs", runner_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    operations = module.ssstateen_operation_specs()
    expected = {
        1: "sstateen0", 2: "sstateen0", 3: "sstateen1", 4: "sstateen1",
        5: "sstateen2", 6: "sstateen2", 7: "sstateen3", 8: "sstateen3",
        9: "hstateen0", 10: "hstateen0", 11: "hstateen1", 12: "hstateen1",
        13: "hstateen2", 14: "hstateen2", 15: "hstateen3", 16: "hstateen3",
        17: "henvcfg", 18: "henvcfg", 19: "senvcfg", 20: "senvcfg",
    }
    assert {op_id: operations[op_id]["csr"] for op_id in expected} == expected
    assert all(operations[op_id]["mode"] == "HS" for op_id in expected)


def test_hs_vs_probe_has_explicit_mode_and_virtual_trap_records():
    runner_path = ROOT / "experiments/kunminghu-smoke/run.py"
    spec = importlib.util.spec_from_file_location("ssstateen_virtual_specs", runner_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    operations = module.ssstateen_operation_specs("hs-vs-valid")
    assert [(operations[key]["mode"], operations[key]["csr"])
            for key in (2011, 2012, 2013, 2014, 2021, 2022, 2023)] == [
                ("HS", "sstateen0"), ("HS", "sstateen0"), ("HS", "hstateen0"),
                ("HS", "hstateen0"), ("VS", "sstateen0"), ("VS", "sstateen0"),
                ("VS", "ecall")]
    marker = (2023 << 20) | (31 << 7) | 0x13
    scause = (0x142 << 20) | (2 << 12) | (5 << 7) | 0x73
    trace = (f"[00] commit pc 0000000080000000 inst {marker:08x} wen 1 dst 31 data {2023:016x}\n"
             f"[01] commit pc 0000000080000004 inst {scause:08x} wen 1 dst 05 data {10:016x}\n")
    row = next(item for item in module.parse_ssstateen_trace(trace, "hs-vs-valid")
               if item["operation_id"] == 2023)
    assert row["observed_cause"] == 10
    assert row["expected_cause"] == 10
    assert row["cause_status"] == "observed in trap-handler cause CSR read"
    native_exception = (f"[00] commit pc 0000000080000000 inst {marker:08x} wen 1 dst 31 data {2023:016x}\n"
                        "[01] exception pc 0000000080000004 inst 00000073 cause 000000000000000a\n")
    row = next(item for item in module.parse_ssstateen_trace(native_exception, "hs-vs-valid")
               if item["operation_id"] == 2023)
    assert row["observed"] == "trap cause=10; CPU exception trace"
    assert row["observed_cause"] == 10
    assert row["trace_pc"] == "0x0000000080000004"
    controls = module.ssstateen_expected_controls("hs-vs-gates")
    assert controls["mode_path"] == "M -> HS -> VS -> HS -> VS -> HS"
    assert "cause 22" in controls["expected"]
    assert "sstateen0-3" in controls["expected"]

    gate_source = (ROOT / "experiments/ssstateen/kunminghu_probe_hs_vs_gates.S").read_text()
    restore = gate_source.split("open_vs_gate0:", 1)[1].split(".section .bss", 1)[0]
    assert "slli    t4, t4, 63" in restore
    assert "ori     t4, t4, 1" in restore
    assert "csrw    0x60c, t4" in restore
    gate_ops = module.ssstateen_operation_specs("hs-vs-gates")
    assert "preserve supported C bit" in gate_ops[2016]["expected"]
    assert "defined C bit" in gate_ops[2023]["expected"]
    assert gate_ops[2023]["expected_cause"] is None
    for slot in range(1, 4):
        assert gate_ops[2100 + slot]["operation"] == "write-gates-set"
        assert gate_ops[2103 + slot]["operation"] == "read"
        assert gate_ops[2103 + slot]["mode"] == "HS"
        assert gate_ops[2106 + slot]["operation"] == "write-gates-clear"
        assert gate_ops[2108 + slot * 3]["expected_cause"] == 22
    assert "verify H SE" in gate_source


def test_hs_vu_fcsr_probe_records_dynamic_misa_and_access_without_calling_it_a_gate_pass():
    runner_path = ROOT / "experiments/kunminghu-smoke/run.py"
    spec = importlib.util.spec_from_file_location("ssstateen_vu_specs", runner_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    fixture = (ROOT / "experiments/ssstateen/kunminghu_probe_hs_vu.S").read_text()
    assert "li      t0, 0x80" in fixture and "SPVP=0" in fixture
    assert "csrw    0x200, t0" in fixture
    assert "li      t0, 0x6800" in fixture

    trace_path = (ROOT / "notes/units/evidence/smoke/kunminghu-ssstateen-hs-vu-20261014/"
                  "kunminghu-fixture-20261014T130304Z-b0efa44f992a/stdout.log")
    operations = {row["operation_id"]: row for row in module.parse_ssstateen_trace(trace_path.read_text(), "hs-vu-fcsr")}
    assert operations[3001]["observed"] == "readback=0x80000000003411af; committed CSR read"
    assert operations[3002]["observed"].endswith("0000000000000000; committed CSR read")
    assert operations[3003]["observed"].endswith("0000000000000000; committed CSR read")
    assert operations[3004]["observed"].endswith("0000000000000000; committed CSR read")
    assert operations[3011]["mode"] == "VU"
    assert operations[3011]["observed"] == "readback=0x0000000000000000; committed CSR read"
    assert operations[3011]["expected_cause"] is None
    assert operations[3012]["observed_cause"] == 8
    assert "not a stateen-gate pass" in operations[3011]["expected"]


def test_hs_vs_gate_run_uses_csr_readback_when_native_trace_omits_t4_transforms():
    runner_path = ROOT / "experiments/kunminghu-smoke/run.py"
    spec = importlib.util.spec_from_file_location("ssstateen_trace_sources", runner_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    trace = (ROOT / "notes/units/evidence/smoke/kunminghu-ssstateen-hs-vs-gates-20261014/"
             "kunminghu-fixture-20261014T131239Z-b10452454932/output.log").read_text()
    rows = {row["operation_id"]: row for row in module.parse_ssstateen_trace(trace, "hs-vs-gates")}
    for write_id, read_id in ((2101, 2104), (2102, 2105), (2103, 2106)):
        assert "source register value unavailable" in rows[write_id]["observed"]
        assert rows[read_id]["observed"].startswith("readback=0x8000000000000000")


def test_hs_vs_gate_clear_traps_all_four_slots_and_restores_execution():
    runner_path = ROOT / "experiments/kunminghu-smoke/run.py"
    spec = importlib.util.spec_from_file_location("ssstateen_vs_gate_trace", runner_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    trace = (ROOT / "notes/units/evidence/smoke/kunminghu-ssstateen-hs-vs-gates-20261014/"
             "kunminghu-fixture-20261014T132255Z-b10452454932/output.log").read_text()
    rows = {row["operation_id"]: row for row in module.parse_ssstateen_trace(trace, "hs-vs-gates")}
    assert rows[2021]["observed_cause"] == 22
    for slot in range(1, 4):
        assert rows[2103 + slot]["observed"] == "readback=0x8000000000000000; committed CSR read"
        first_op = 2111 + (slot - 1) * 3
        assert rows[first_op]["observed_cause"] == 22
        assert rows[first_op + 1]["observed"] == "write-source=0xffffffffffffffff; CSR write committed"
        assert rows[first_op + 2]["observed"].startswith("readback=")
    assert rows[2024]["observed_cause"] == 10


def test_m_s_probe_has_clear_set_checks_for_all_sstateen_gates():
    runner_path = ROOT / "experiments/kunminghu-smoke/run.py"
    spec = importlib.util.spec_from_file_location("ssstateen_m_s_specs", runner_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    operations = module.ssstateen_operation_specs("m-s-gates")
    fixture = (ROOT / "experiments/ssstateen/kunminghu_probe_m_s.S").read_text()
    for slot in range(1, 4):
        base = 4030 + slot * 10
        assert operations[base + 1]["expected_cause"] == 9
        assert operations[base + 2]["expected_cause"] == 2
        assert operations[base + 3]["mode"] == "S"
        assert f"sstateen{slot}_blocked:" in fixture
    assert operations[4073]["expected_cause"] == 9
    assert "beq     a1, t1, clear_sstateen3" in fixture
    controls = module.ssstateen_expected_controls("m-s-gates")
    assert "M SE0-3" in controls["gate_state"]
    assert "each corresponding S CSR" in controls["expected"]


def test_kunminghu_operation_parser_does_not_call_trace_silence_not_reached():
    runner_path = ROOT / "experiments/kunminghu-smoke/run.py"
    spec = importlib.util.spec_from_file_location("ssstateen_trace_runner_no_trace", runner_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    rows = module.parse_ssstateen_trace("Core-0 instrCnt = 29,242, cycleCnt = 100,000\n")
    assert len(rows) == 147
    assert all(row["cause_status"].startswith("unavailable:") for row in rows)
    assert all(row["observed"].startswith("unavailable:") for row in rows)


def test_heliodor_fixture_asserts_only_normative_defined_bits():
    source = (ROOT / "experiments/ssstateen/run_isolated.py").read_text(encoding="utf-8")
    assert "trace[16+i][63]" in source and "trace[28+i][63]" in source
    assert "trace[12+i][63]" not in source and "trace[24+i][63]" not in source
    assert "sstateen0 JVT/FCSR are RO-zero" in source
    assert "sstateen1-3 are RO-zero" in source


def test_heliodor_s_gate_fixture_toggles_m_se0_and_records_both_s_reads():
    fixture = (ROOT / "experiments/ssstateen/ssstateen_probe_s_gates.S").read_text()
    runner = (ROOT / "experiments/ssstateen/run_isolated.py").read_text()
    makefile = (ROOT / "experiments/ssstateen/Makefile").read_text()
    assert "li      t6, 23" in fixture and "clear_m_se0:" in fixture
    assert "li      t6, 24" in fixture and "set_m_se0:" in fixture
    assert "li      t6, 43" in fixture and "csrr    t2, 0x10c" in fixture
    assert "sd      t2, 1272(t0)" in fixture and "sd      t2, 1280(t0)" in fixture
    assert 'parser.add_argument("--case", choices=CASES, default="baseline")' in runner
    assert '"vs-v2": "ssstateen_probe_vs_v2.hex"' in runner
    assert "ssstateen_probe_s_gates.hex" in runner
    assert "ssstateen_probe_s_gates_v2.hex" in runner
    assert "ssstateen_probe_s_gates_v3.hex" in runner
    assert "ssstateen_probe_s_gates.hex" in makefile
    assert "ssstateen_probe_s_gates_v3.hex" in makefile
    assert "ssstateen_probe_vs_v2.hex" in makefile
    assert "ssstateen_probe_vu.hex" in makefile
    assert "ssstateen_probe_vu_fcsr.hex" in makefile


def test_heliodor_all_slot_gate_fixture_records_control_and_access_ids():
    fixture = (ROOT / "experiments/ssstateen/ssstateen_probe_s_gates_v3.S").read_text()
    for slot in range(4):
        assert f"csrw    0x{0x30c+slot:03x}, zero" in fixture
        assert f"csrw    0x{0x30c+slot:03x}, t4" in fixture
        assert f"li      t6, {43+slot}" in fixture
        assert f"li      t6, {47+slot}" in fixture


def test_story_68_evidence_preserves_both_snapshot_outcomes_and_fixture_sha():
    manifest = json.loads((ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml").read_text())
    records = {record["id"]: record for snapshot in manifest["snapshots"]
               for record in snapshot.get("runs", []) if record.get("id", "").startswith("ssstateen-")}
    hel = records["ssstateen-heliodor-rerun-20261014"]
    kh = records["ssstateen-kunminghu-run-20261014"]
    assert hel["fixture_sha256_matches_baseline"] is True
    assert hel["result"] == "run-fail" and hel["cpu_started"] is True
    assert hel["observed_values"]["traps"] == [{"mode": "HS", "operation_id": 21, "cause": 9}]
    corrected = records["ssstateen-heliodor-corrected-assertions-20261014"]
    operation_ids = [item["operation_id"] for item in corrected["operation_records"]]
    assert len(operation_ids) == len(set(operation_ids))
    assert set(range(1, 22)).issubset(operation_ids)
    assert kh["result"] == "run-fail" and kh["cpu_started"] is True
    assert kh["observed_values"]["DUT_observed"]["mcause"] != kh["observed_values"]["NEMU_expected"]["mcause"]
    s_gates = records["ssstateen-heliodor-s-gates-20261014"]
    assert s_gates["result"] == "run-fail" and s_gates["cpu_started"] is True
    operations = {item["operation_id"]: item for item in s_gates["operation_records"]}
    assert operations[43]["observed_cause"] is None
    assert "completion marker 43" in operations[43]["observed"]
    assert operations[44]["observed"].startswith("readback=0x0")
    for record in (hel, kh):
        path = ROOT / record["input"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["input_sha256"]
    assert hashlib.sha256((ROOT / s_gates["input"]).read_bytes()).hexdigest() == s_gates["input_sha256"]
    all_slots = records["ssstateen-heliodor-s-gates-all-slots-20261014"]
    assert all_slots["result"] == "run-fail" and all_slots["cpu_started"] is True
    assert [item["operation_id"] for item in all_slots["operation_records"]] == [
        2301, 43, 2305, 47, 2302, 44, 2306, 48,
        2303, 45, 2307, 49, 2304, 46, 2308, 50,
    ]
    assert all(value == 0 for value in all_slots["observed_values"]["M_SE_set_readbacks"])
    assert all(item["trap"] is None for item in all_slots["observed_values"]["S_clear_reads"])
    assert hashlib.sha256((ROOT / all_slots["input"]).read_bytes()).hexdigest() == all_slots["input_sha256"]


def test_heliodor_vs_fixture_and_manifest_preserve_gate_open_blocker():
    fixture = (ROOT / "experiments/ssstateen/ssstateen_probe_vs_v2.S").read_text()
    manifest = json.loads((ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml").read_text())
    records = {record["id"]: record for snapshot in manifest["snapshots"]
               for record in snapshot.get("runs", [])}
    run = records["ssstateen-heliodor-vs-clear-set-20261014"]
    assert all(f"csrr    t1, 0x{0x10c + slot:03x}" in fixture for slot in range(4))
    assert all(f"csrw    0x{0x60c + slot:03x}, t1" in fixture for slot in range(4))
    assert run["result"] == "run-fail" and run["cpu_started"] is True
    assert run["observed_values"]["hstateen_set_attempt_readbacks"] == [0, 0, 0, 0]
    assert run["observed_values"]["VS_after_set_attempt_readbacks"] == [0, 0, 0, 0]
    assert [trap["cause"] for trap in run["observed_values"]["traps"]] == [10, 10]
    assert len({item["operation_id"] for item in run["operation_records"]}) == len(run["operation_records"])
    assert hashlib.sha256((ROOT / run["input"]).read_bytes()).hexdigest() == run["input_sha256"]


def test_heliodor_vu_records_privilege_faults_without_claiming_stateen_gate_pass():
    fixture = (ROOT / "experiments/ssstateen/ssstateen_probe_vu.S").read_text()
    runner = (ROOT / "experiments/ssstateen/run_isolated.py").read_text()
    manifest = json.loads((ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml").read_text())
    records = {record["id"]: record for snapshot in manifest["snapshots"]
               for record in snapshot.get("runs", [])}
    run = records["ssstateen-heliodor-vu-20261014"]
    assert "/* SPV=1, SPVP=0" in fixture and "/* SPP=0 */" in fixture
    assert "li      t3, 2\n    beq     t2, t3, resume_vs" in fixture
    assert '"vu": "ssstateen_probe_vu.hex"' in runner
    assert run["result"] == "run-pass" and run["cpu_started"] is True
    assert [op["observed_cause"] for op in run["operation_records"]] == [2, 2, 2, 2, 8]
    assert "not evidence of an H.SE gate pass" in run["evidence_method"]
    assert hashlib.sha256((ROOT / run["input"]).read_bytes()).hexdigest() == run["input_sha256"]


def test_heliodor_vu_fcsr_is_observed_but_does_not_claim_gate_open():
    fixture = (ROOT / "experiments/ssstateen/ssstateen_probe_vu_fcsr.S").read_text()
    runner = (ROOT / "experiments/ssstateen/run_isolated.py").read_text()
    manifest = json.loads((ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml").read_text())
    records = {record["id"]: record for snapshot in manifest["snapshots"]
               for record in snapshot.get("runs", [])}
    run = records["ssstateen-heliodor-vu-fcsr-20261014"]
    assert "0x6000" in fixture and "csrw    0x200" in fixture
    assert '"vu-fcsr": "ssstateen_probe_vu_fcsr.hex"' in runner
    assert run["result"] == "run-pass" and run["cpu_started"] is True
    assert run["observed_values"]["VU_fflags_initial"] == 0
    assert run["observed_values"]["VU_fflags_after_write"] == 1
    assert run["observed_values"]["H.FCSR_set_attempt_readback"] == 0
    assert [op["operation_id"] for op in run["operation_records"]] == [311, 312, 313, 399]
    assert "not a gate-open comparison" in run["evidence_method"]
    assert hashlib.sha256((ROOT / run["input"]).read_bytes()).hexdigest() == run["input_sha256"]


def test_ssstateen_parser_does_not_attribute_trap_epilogue_to_previous_csr():
    runner_path = ROOT / "experiments/kunminghu-smoke/run.py"
    spec = importlib.util.spec_from_file_location("ssstateen_no_stale_exception", runner_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    trace = (ROOT / "notes/units/evidence/smoke/kunminghu-ssstateen-operation-trace-20261014/"
             "kunminghu-fixture-20261014T123122Z-069b00f3c8db/output.log").read_text()
    rows = {row["operation_id"]: row for row in module.parse_ssstateen_trace(trace)}
    # The CSR's cause is available from the handler's mcause read; the later MRET
    # access-fault exception retains x31=1064 but is not the CSR instruction.
    assert rows[1064]["observed"] == "readback=0x0000000000000000; committed CSR read"
    assert rows[1064]["observed_cause"] == "no-trap (CSR instruction committed)"
    assert rows[1064]["trace_pc"] != "0x0000000080000554"


def test_ssstateen_goodtrap_selfcheck_recovers_traps_missing_from_native_labels():
    runner_path = ROOT / "experiments/kunminghu-smoke/run.py"
    spec = importlib.util.spec_from_file_location("ssstateen_goodtrap_trace", runner_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    trace = (ROOT / "notes/units/evidence/smoke/kunminghu-fixture-runs/"
             "kunminghu-fixture-20261014T151514Z-3e81181d1d02/output.log").read_text()
    rows = {row["operation_id"]: row for row in module.parse_ssstateen_trace(trace)}
    assert rows[1]["observed_cause"] == 2
    assert "fixture GOODTRAP self-check" in rows[1]["observed"]
    assert rows[1]["operation_id_source"].startswith("fixture trap-log array")
    assert rows[21]["observed_cause"] == 9
    assert rows[1071]["observed"].startswith("not-reached:")


def test_kunminghu_fixture_checks_exact_mstateen_warl_masks():
    fixture = (ROOT / "experiments/ssstateen/kunminghu_probe_operation_ids.S").read_text()
    runner_path = ROOT / "experiments/kunminghu-smoke/run.py"
    spec = importlib.util.spec_from_file_location("ssstateen_m_warl_specs", runner_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    assert "li      t2, 0xde00000000000001" in fixture
    assert fixture.count("bne     t1, t2, bad_trap") >= 4
    operations = module.ssstateen_operation_specs()
    assert [operations[1025 + i]["csr"] for i in range(4)] == [
        "mstateen0", "mstateen1", "mstateen2", "mstateen3",
    ]
    assert all(operations[1025 + i]["operation"] == "readback-after-write" for i in range(4))


def test_kunminghu_fixture_checks_each_implemented_stateen_field():
    fixture = (ROOT / "experiments/ssstateen/kunminghu_probe_operation_ids.S").read_text()
    runner_path = ROOT / "experiments/kunminghu-smoke/run.py"
    spec = importlib.util.spec_from_file_location("ssstateen_onehot_specs", runner_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    operations = module.ssstateen_operation_specs()
    assert fixture.count("    probe_field ") == 25
    readbacks = [operations[1102 + 2 * index] for index in range(20)]
    assert [item["operation"] for item in readbacks] == ["readback-one-hot"] * 20
    assert [item["csr"] for item in readbacks] == (
        ["mstateen0"] * 7 + ["mstateen1", "mstateen2", "mstateen3"] +
        ["hstateen0"] * 7 + ["hstateen1", "hstateen2", "hstateen3"]
    )
    assert all("WARL readback should equal 0x" in item["expected"] for item in readbacks)
    assert [operations[key]["csr"] for key in (1142, 1144, 1146, 1148, 1150)] == [
        "mstateen0", "mstateen1", "mstateen2", "mstateen3", "sstateen0",
    ]


def test_kunminghu_trace_decodes_one_hot_readbacks_as_reads():
    output = (ROOT / "notes/units/evidence/smoke/kunminghu-fixture-runs/"
              "kunminghu-fixture-20261014T154748Z-3e81181d1d02/output.log").read_text()
    runner_path = ROOT / "experiments/kunminghu-smoke/run.py"
    spec = importlib.util.spec_from_file_location("ssstateen_onehot_trace", runner_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    rows = {row["operation_id"]: row for row in module.parse_ssstateen_trace(output)}
    assert rows[1102]["observed"].startswith("readback=0x8000000000000000")
    assert rows[1122]["observed"].startswith("readback=0x8000000000000000")
    assert rows[1150]["observed"].startswith("readback=0x0000000000000001")
    assert rows[1119]["observed"].startswith("fixture write source=0x8000000000000000")
    assert "native source-register value unavailable" in rows[1119]["observed"]


def test_kunminghu_vs_fixture_covers_h_envcfg_clear_and_restore():
    fixture = (ROOT / "experiments/ssstateen/kunminghu_probe_hs_vs_gates.S").read_text()
    s_fixture = (ROOT / "experiments/ssstateen/kunminghu_probe_m_s.S").read_text()
    runner_path = ROOT / "experiments/kunminghu-smoke/run.py"
    spec = importlib.util.spec_from_file_location("ssstateen_vs_envcfg_specs", runner_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    assert "li      t6, 2120\n    csrr    t2, 0x10a" in fixture
    assert "li      t6, 2121\n    csrr    t2, 0x10a" in fixture
    assert "beq     t6, t1, open_vs_envcfg" in fixture
    operations = module.ssstateen_operation_specs("hs-vs-gates")
    assert operations[2120]["expected_cause"] == 22
    assert operations[2121]["operation"] == "read"
    assert "li      t1, 5                  /* H.SE0, H.SE1-3, and H.ENVCFG */" in fixture
    assert "bne     s0, t1, bad_trap" in s_fixture


def test_unimplemented_vu_custom_csr_probe_stays_unverified():
    manifest = json.loads((ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml").read_text())
    records = {record["id"]: record for snapshot in manifest["snapshots"]
               for record in snapshot.get("runs", [])}
    run = records["kunminghu-fixture-20261014T153123Z-3e81181d1d02"]
    assert run["result"] == "unverified"
    assert "0x800 has no implementation" in run["blocker"]
    assert "EX_II before virtual-instruction EX_VI" in run["blocker"]
    probe = {operation["operation_id"]: operation for operation in run["operation_records"]}[5001]
    assert probe["observed_cause"] == 2
    assert probe["expected_cause"] is None
