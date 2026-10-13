#!/usr/bin/env python3
"""Create a private Heliodor RTL/testbench copy without the broken debug harness."""
from __future__ import annotations

import pathlib
import shutil
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "sources/heliodor"
FIXTURE = pathlib.Path(__file__).resolve().parent
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
    "    o_tohost: output logic<32>,\n    o_trace : output logic<64> [64],\n",
)
normal_harness = replace_once(
    normal_harness,
    "    let tohost_lo: logic<32> = dram[TOHOST_IDX[19:0]];\n",
    "    always_comb {\n"
    "        for i in 0..64 {\n"
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
    var trace : logic<64> [64];
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
        for i in 0..64 {
            $display("ssstateen trace[%d]=%h", i, trace[i]);
        }
        $assert(tohost == 32'h0000_002b, "Ssstateen expected 20 gate traps and SE0=1");
        $finish();
    }
}
'''
(WORK / "tb/test_arch_common.veryl").write_text(normal_harness + test_module, encoding="utf-8")
(WORK / "test/ssstateen").mkdir(parents=True)
shutil.copy2(FIXTURE / "ssstateen_probe.hex", WORK / "test/ssstateen/ssstateen_probe.hex")
print(WORK)
