#!/usr/bin/env python3
"""Create a private Heliodor RTL/testbench copy without the broken debug harness."""
from __future__ import annotations

import pathlib
import shutil
import tempfile
import argparse

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "sources/heliodor"
FIXTURE = pathlib.Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument("--case", choices=("baseline", "s-gates", "s-gates-v2", "s-gates-v3", "vs", "vs-v2", "vu", "vu-fcsr"), default="baseline")
args = parser.parse_args() if __name__ == "__main__" else parser.parse_args([])
WORK = pathlib.Path(tempfile.mkdtemp(prefix="heliodor-ssstateen-isolated-"))
shutil.copytree(SOURCE / "src", WORK / "src")
shutil.copy2(SOURCE / "Veryl.toml", WORK / "Veryl.toml")
shutil.copy2(SOURCE / "Veryl.lock", WORK / "Veryl.lock")
(WORK / "tb").mkdir()

# The normal 1 MiB arch harness is retained verbatim. The shared source also
# contains a debug harness with a 64K-word memory whose $readmemh initialization
# fails Veryl 0.22.0's check pass even when that module is not instantiated.
common = (SOURCE / "tb/test_arch_common.veryl").read_text(encoding="utf-8")
normal_harness = common.split("// Debug variant exposing core internals for stuck-test diagnosis.", 1)[0]

def replace_once(source: str, old: str, new: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"expected one harness anchor, found {count}: {old!r}")
    return source.replace(old, new, 1)

normal_harness = replace_once(
    normal_harness,
    "    var dram: logic<32> [1048576];",
    "    #[allow(initial_assign)]\n    var dram: logic<32> [1048576];",
)
normal_harness = replace_once(
    normal_harness,
    "    o_tohost: output logic<32>,\n",
    "    o_tohost: output logic<32>,\n    o_trace : output logic<64> [192],\n",
)
normal_harness = replace_once(
    normal_harness,
    "    let tohost_lo: logic<32> = dram[TOHOST_IDX[19:0]];\n",
    "    always_comb {\n"
    "        for i in 0..192 {\n"
    "            o_trace[i] = {dram[1029 + i * 2], dram[1028 + i * 2]};\n"
    "        }\n"
    "    }\n"
    "    let tohost_lo: logic<32> = dram[TOHOST_IDX[19:0]];\n",
)
test_module = r'''
#[test(test_arch_ssstateen)]
module test_arch_ssstateen {
    inst clk: $tb::clock_gen;
    inst rst: $tb::reset_gen ( clk );
    var pass  : logic    ;
    var fail  : logic    ;
    var tohost: logic<32>;
    var trace : logic<64> [192];
    inst h: test_arch_common_harness #(
        HEX_FILE  : "test/ssstateen/ssstateen_probe.hex",
        TOHOST_IDX: 1024,
    ) (
        clk          ,
        rst          ,
        o_pass  : pass,
        o_fail  : fail,
        o_tohost: tohost,
        o_trace : trace,
    );
    initial {
        rst.assert(clk);
        clk.next(20000);
        $display("ssstateen probe tohost=%h pass=%b fail=%b", tohost, pass, fail);
        for i in 0..192 {
            $display("ssstateen trace[%d]=%h", i, trace[i]);
        }
        for i in 150..158 {
            $assert(trace[i] == 64'd0, "S-mode stateen reads and readbacks remain zero");
        }
        $assert(trace[34] == 64'd3, "S-mode path has only the three explicit ecalls");
        $assert(trace[100] == 64'd21, "initial HS ecall marker reaches M");
        $assert(trace[101] == 64'd22, "HS-to-S ecall marker reaches M");
        $assert(trace[102] == 64'd42, "final S ecall marker reaches M");
        $display("SSSTATEEN_S_MODE_OBSERVATIONS_PASS");
        $assert(trace[12][2:1] == 2'b00, "sstateen0 JVT/FCSR are RO-zero");
        for i in 13..16 {
            $assert(trace[i] == 64'd0, "sstateen1-3 are RO-zero");
        }
        $assert(trace[16][56] == 1'b0, "hstateen0.P1P13 is RO-zero");
        $assert(trace[28][56] == 1'b0, "HS hstateen0.P1P13 is RO-zero");
        for i in 17..20 {
            $assert(trace[i][62:0] == 63'd0, "hstateen1-3 reserved bits are RO-zero");
        }
        for i in 29..32 {
            $assert(trace[i][62:0] == 63'd0, "HS hstateen1-3 reserved bits are RO-zero");
        }
        for i in 0..4 {
            $assert(trace[16+i][63] == 1'b1, "each M-mode hstateen write must set its defined SE0 bit");
            $assert(trace[28+i][63] == 1'b1, "each HS-mode hstateen write must set its defined SE bit");
        }
        $assert(trace[34] == 64'd23, "Ssstateen expected 20 gate traps and three mode-path ecalls");
        for i in 0..20 {
            $assert(trace[35+i] == 64'd2, "each blocked stateen/ENVCFG access must raise illegal instruction");
            $assert(trace[100+i] == i + 64'd1, "trap trace must identify each blocked access in order");
        }
        $assert(trace[55] == 64'd9, "initial HS ecall must reach M");
        $assert(trace[56] == 64'd9, "HS-to-S transition ecall must reach M");
        $assert(trace[57] == 64'd9, "final S ecall must reach M");
        $assert(trace[120] == 64'd21, "trap trace must identify the initial HS ecall");
        $assert(trace[121] == 64'd22, "trap trace must identify the HS-to-S ecall");
        $assert(trace[122] == 64'd42, "trap trace must identify the final S ecall");
        $assert(tohost == 32'h0000_002f, "Ssstateen marker combines trap count and hstateen0.SE0");
        $finish();
    }
}
'''
if args.case in ("s-gates", "s-gates-v2", "s-gates-v3"):
    test_module = r'''
#[test(test_arch_ssstateen)]
module test_arch_ssstateen {
    inst clk: $tb::clock_gen;
    inst rst: $tb::reset_gen ( clk );
    var pass  : logic;
    var fail  : logic;
    var tohost: logic<32>;
    var trace : logic<64> [192];
    inst h: test_arch_common_harness #(
        HEX_FILE  : "test/ssstateen/ssstateen_probe.hex",
        TOHOST_IDX: 1024,
    ) (
        clk, rst, o_pass: pass, o_fail: fail, o_tohost: tohost, o_trace: trace,
    );
    initial {
        rst.assert(clk);
        clk.next(20000);
        $display("ssstateen S-gate probe tohost=%h pass=%b fail=%b", tohost, pass, fail);
        for i in 0..192 { $display("ssstateen trace[%d]=%h", i, trace[i]); }
        $assert(trace[34] == 64'd6, "S sstateen0 read with M.SE0 clear must trap before enabled read");
        $assert(trace[37] == 64'd2, "M.SE0 clear must cause illegal-instruction trap");
        $assert(trace[102] == 64'd43, "trap must identify the S read attempted with M.SE0 clear");
        $assert(trace[158] == 64'd43, "S-mode clear-gate read must reach its completion marker if no trap occurs");
        $assert(trace[159] == 64'd0, "record the value returned by the clear-gate read");
        $assert(trace[161] == 64'd44, "gate-open S read must reach its completion marker");
        $finish();
    }
}
'''
if args.case == "s-gates-v2":
    test_module = test_module.replace(
        "        $finish();",
        "        $assert(trace[162] == 64'd2301 && trace[164] == 64'd2302, \"record M.SE0 clear/set controls\");\n"
        "        $assert(trace[163][63] == 1'b0, \"read back M.SE0 after clear\");\n"
        "        $assert(trace[165][63] == 1'b1, \"read back M.SE0 after set\");\n"
        "        $finish();",
    )
if args.case == "s-gates-v3":
    checks = "".join(
        f"        $assert(trace[{103+i}] == 64'd{43+i} && trace[{38+i}] == 64'd2, \"clear gate slot {i} traps with cause 2\");\n"
        f"        $assert(trace[{158+i}] == 64'd{43+i} && trace[{162+i}] == 64'd0, \"S clear access slot {i} is observed\");\n"
        f"        $assert(trace[{166+i}] == 64'd{47+i}, \"S set access slot {i} is observed\");\n"
        f"        $assert(trace[{170+i}] == 64'd0, \"S set readback slot {i} is recorded\");\n"
        f"        $assert(trace[{174+i}] == 64'd{2301+i} && trace[{178+i}] == 64'd0, \"M clear control slot {i} is recorded\");\n"
        f"        $assert(trace[{182+i}] == 64'd{2305+i} && trace[{186+i}][63] == 1'b1, \"M set control slot {i} is recorded\");\n"
        for i in range(4)
    )
    test_module = test_module.replace(
        "        $finish();",
        "        $assert(trace[34] == 64'd9, \"all four M.SE clear accesses trap, followed by enabled accesses\");\n"
        "        $assert(trace[174] == 64'd2301 && trace[178][63] == 1'b0, \"M.SE0 clear readback\");\n"
        "        $assert(trace[175] == 64'd2302 && trace[179][63] == 1'b0, \"M.SE1 clear readback\");\n"
        "        $assert(trace[176] == 64'd2303 && trace[180][63] == 1'b0, \"M.SE2 clear readback\");\n"
        "        $assert(trace[177] == 64'd2304 && trace[181][63] == 1'b0, \"M.SE3 clear readback\");\n"
        + checks + "        $finish();",
    )
    test_module = test_module.replace(
        "$assert(trace[34] == 64'd6, \"S sstateen0 read with M.SE0 clear must trap before enabled read\");",
        "$assert(trace[34] == 64'd9, \"all four M.SE clear accesses trap, followed by enabled accesses\");",
    )
if args.case in ("vs", "vs-v2", "vu", "vu-fcsr"):
    test_module = r'''
#[test(test_arch_ssstateen)]
module test_arch_ssstateen {
    inst clk: $tb::clock_gen;
    inst rst: $tb::reset_gen ( clk );
    var pass  : logic;
    var fail  : logic;
    var tohost: logic<32>;
    var trace : logic<64> [192];
    inst h: test_arch_common_harness #(
        HEX_FILE: "test/ssstateen/ssstateen_probe.hex",
        TOHOST_IDX: 1024,
    ) (
        clk, rst, o_pass: pass, o_fail: fail, o_tohost: tohost, o_trace: trace,
    );
    initial {
        rst.assert(clk);
        clk.next(20000);
        $display("ssstateen VS probe tohost=%h pass=%b fail=%b", tohost, pass, fail);
        for i in 0..192 { $display("ssstateen trace[%d]=%h", i, trace[i]); }
        $assert(tohost == 32'd1, "VS probe reaches terminal guest ecall");
        $assert(trace[0] == 64'd5, "four VS stateen accesses trap plus terminal ecall");
        for i in 0..4 { $assert(trace[1+i] == 64'd22, "VS CSR access causes virtual-instruction"); }
        for i in 0..4 { $assert(trace[65+i] == 64'd301+i, "VS trap records the CSR operation ID"); }
        $assert(trace[5] == 64'd10 && trace[65] == 64'd399, "terminal VS ecall reaches HS");
        for i in 0..4 { $assert(trace[148+i] == 64'd0, "H stateen gate readback is zero"); }
        $finish();
    }
}
'''
if args.case == "vs-v2":
    test_module = test_module.replace("trace[0] == 64'd5", "trace[0] == 64'd6")
    test_module = test_module.replace(
        "$assert(trace[5] == 64'd10 && trace[65] == 64'd399, \"terminal VS ecall reaches HS\");",
        "$assert(trace[5] == 64'd10 && trace[65] == 64'd399, \"first VS ecall reaches HS\");\n"
        "        $assert(trace[6] == 64'd10 && trace[70] == 64'd599, \"second VS ecall reaches HS\");\n"
        "        for i in 0..4 { $assert(trace[144+i] == 64'd2501+i, \"H clear control operation ID\"); }\n"
        "        for i in 0..4 { $assert(trace[156+i] == 64'd2511+i, \"H set control operation ID\"); }\n"
        "        for i in 0..4 { $assert(trace[160+i][63] == 1'b1, \"H set control readback\"); }\n"
        "        for i in 0..4 { $assert(trace[166+i] == 64'd0 && trace[170+i] == 64'd601+i, \"VS set phase read and completion\"); }",
    )
if args.case == "vu":
    test_module = r'''
#[test(test_arch_ssstateen)]
module test_arch_ssstateen {
    inst clk: $tb::clock_gen;
    inst rst: $tb::reset_gen ( clk );
    var pass  : logic;
    var fail  : logic;
    var tohost: logic<32>;
    var trace : logic<64> [192];
    inst h: test_arch_common_harness #(
        HEX_FILE: "test/ssstateen/ssstateen_probe.hex",
        TOHOST_IDX: 1024,
    ) (
        clk, rst, o_pass: pass, o_fail: fail, o_tohost: tohost, o_trace: trace,
    );
    initial {
        rst.assert(clk);
        clk.next(20000);
        $display("ssstateen VU probe tohost=%h pass=%b fail=%b", tohost, pass, fail);
        for i in 0..192 { $display("ssstateen trace[%d]=%h", i, trace[i]); }
        $assert(tohost == 32'd1, "VU probe reaches terminal guest ecall");
        $assert(trace[0] == 64'd5, "four VU stateen accesses trap plus terminal ecall");
        for i in 0..4 { $assert(trace[1+i] == 64'd2, "VU CSR access raises illegal-instruction"); }
        for i in 0..4 { $assert(trace[65+i] == 64'd301+i, "VU trap records the CSR operation ID"); }
        $assert(trace[5] == 64'd8 && trace[65] == 64'd399, "terminal VU ecall reaches HS");
        for i in 0..4 { $assert(trace[148+i] == 64'd0, "H stateen gate readback is zero"); }
        $finish();
    }
}
'''
if args.case == "vu-fcsr":
    test_module = r'''
#[test(test_arch_ssstateen)]
module test_arch_ssstateen {
    inst clk: $tb::clock_gen;
    inst rst: $tb::reset_gen ( clk );
    var pass  : logic;
    var fail  : logic;
    var tohost: logic<32>;
    var trace : logic<64> [192];
    inst h: test_arch_common_harness #(
        HEX_FILE: "test/ssstateen/ssstateen_probe.hex",
        TOHOST_IDX: 1024,
    ) (
        clk, rst, o_pass: pass, o_fail: fail, o_tohost: tohost, o_trace: trace,
    );
    initial {
        rst.assert(clk);
        clk.next(20000);
        $display("ssstateen VU FCSR probe tohost=%h pass=%b fail=%b", tohost, pass, fail);
        for i in 0..192 { $display("ssstateen trace[%d]=%h", i, trace[i]); }
        $assert(tohost == 32'd1, "VU FCSR probe reaches terminal guest ecall");
        $assert(trace[0] == 64'd1 && trace[1] == 64'd8, "only the terminal VU ecall traps");
        $assert(trace[65] == 64'd399, "terminal VU ecall operation ID");
        $assert(trace[140] == 64'd411 && trace[141] == 64'd412 && trace[142] == 64'd413, "VU FCSR operations complete");
        $assert(trace[136] == 64'd0 && trace[138] == 64'd1, "VU fflags read/write/readback");
        $assert(trace[164] == 64'd0, "H.FCSR write attempt reads back zero");
        $finish();
    }
}
'''
if args.case == "baseline":
    test_module = test_module.replace(
        "        $assert(trace[34] == 64'd3, \"S-mode path has only the three explicit ecalls\");\n", ""
    )
(WORK / "tb/test_arch_common.veryl").write_text(normal_harness + test_module, encoding="utf-8")
(WORK / "test/ssstateen").mkdir(parents=True)
fixture = {"s-gates": "ssstateen_probe_s_gates.hex",
           "s-gates-v2": "ssstateen_probe_s_gates_v2.hex",
           "s-gates-v3": "ssstateen_probe_s_gates_v3.hex",
           "vs": "ssstateen_probe_vs.hex",
           "vs-v2": "ssstateen_probe_vs_v2.hex",
           "vu": "ssstateen_probe_vu.hex",
           "vu-fcsr": "ssstateen_probe_vu_fcsr.hex"}.get(args.case, "ssstateen_probe_s.hex")
shutil.copy2(FIXTURE / fixture, WORK / "test/ssstateen/ssstateen_probe.hex")
print(WORK)
