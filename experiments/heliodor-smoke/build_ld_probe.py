#!/usr/bin/env python3
"""Build an isolated Heliodor LD probe fixture."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import shutil
import struct
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "experiments/rv64-ld-probe/ld.S"
LINKER = ROOT / "experiments/rv64-ld-probe/fixture.ld"
OUTPUT = ROOT / "experiments/heliodor-smoke/ld-probe.hex"
TOOLS = {
    "riscv64-unknown-elf-gcc": "3b2b5d5ad7f9c7821c8ca1b11c6c512f30e3d63dcbdc726836c1c7bc0bceed32",
    "riscv64-unknown-elf-objcopy": "0ed4d26870589f4ba1e5678b62305d66c2df6ee8906da706c830a6f42950c858",
    "riscv64-unknown-elf-nm": "efcf80cb84207546bba2dde494b1e6505ed5cc94b11d530a3fc44ea435f1c0d9",
}


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=pathlib.Path, default=SOURCE)
    parser.add_argument("--output", type=pathlib.Path, default=OUTPUT)
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    if not source.is_relative_to(ROOT) or not output.is_relative_to(ROOT) or not source.is_file():
        raise SystemExit("probe source/output must be project paths and source must exist")
    binaries = {name: shutil.which(name) for name in TOOLS}
    if any(path is None for path in binaries.values()):
        raise SystemExit("pinned RISC-V cross toolchain is unavailable")
    for name, expected in TOOLS.items():
        if sha256(pathlib.Path(binaries[name])) != expected:
            raise SystemExit(f"{name} SHA-256 differs from the pinned toolchain")
    nm = binaries["riscv64-unknown-elf-nm"]
    with tempfile.TemporaryDirectory(prefix="heliodor-ld-probe-") as name:
        temp = pathlib.Path(name)
        elf, raw = temp / "ld-probe.elf", temp / "ld-probe.bin"
        gcc_argv = [binaries["riscv64-unknown-elf-gcc"], "-march=rv64imac_zicsr", "-mabi=lp64",
                    "-nostdlib", "-nostartfiles", "-ffreestanding", f"-Wl,-T,{LINKER}",
                    "-Wl,--build-id=none", "-o", str(elf), str(source)]
        objcopy_argv = [binaries["riscv64-unknown-elf-objcopy"], "-O", "binary", str(elf), str(raw)]
        subprocess.run(gcc_argv, check=True)
        subprocess.run(objcopy_argv, check=True)
        symbols = subprocess.check_output([nm, "-n", str(elf)], text=True)
        symbol_values = {line.split()[-1]: int(line.split()[0], 16)
                         for line in symbols.splitlines() if len(line.split()) >= 3}
        image = raw.read_bytes().ljust(0x1008, b"\0")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("".join(f"{word:08x}\n" for word in struct.unpack("<" + "I" * (len(image) // 4), image)), encoding="ascii")
        output.with_suffix(".build.json").write_text(json.dumps({
            "source": str(source.relative_to(ROOT)), "source_sha256": sha256(source),
            "linker": str(LINKER.relative_to(ROOT)), "linker_sha256": sha256(LINKER),
            "fixture_sha256": sha256(output),
            "target_pc": f"0x{symbol_values['ld_target']:016x}",
            "data_address": f"0x{symbol_values['ld_data']:016x}",
            "gcc_argv": gcc_argv, "objcopy_argv": objcopy_argv,
            "tool_sha256": TOOLS,
        }, indent=2) + "\n", encoding="utf-8")
    print(f"built {output.relative_to(ROOT)}; ld_target=0x{symbol_values['ld_target']:016x}")


if __name__ == "__main__":
    main()
