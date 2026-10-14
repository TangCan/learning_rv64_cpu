#!/usr/bin/env python3
"""Build and validate the four Story 6.4 RV64 images with the pinned cross tools."""
from __future__ import annotations

import pathlib
import shutil
import struct
import hashlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent
EXPECTED = {"standard": 0x0000100F, "funct12": 0x0010100F,
            "rs1": 0x0000900F, "rd": 0x0000108F}
EXPECTED_GCC = "riscv64-unknown-elf-gcc () 15.1.0"
EXPECTED_OBJCOPY = "GNU objcopy (GNU Binutils) 2.44"
EXPECTED_TOOL_SHA256 = {
    "riscv64-unknown-elf-gcc": "3b2b5d5ad7f9c7821c8ca1b11c6c512f30e3d63dcbdc726836c1c7bc0bceed32",
    "riscv64-unknown-elf-objcopy": "0ed4d26870589f4ba1e5678b62305d66c2df6ee8906da706c830a6f42950c858",
    "riscv64-unknown-elf-nm": "efcf80cb84207546bba2dde494b1e6505ed5cc94b11d530a3fc44ea435f1c0d9",
}


def verify_tool_hash(binary: str, expected: str) -> None:
    actual = hashlib.sha256(pathlib.Path(binary).read_bytes()).hexdigest()
    if actual != expected:
        raise SystemExit(f"{binary}: SHA-256 {actual}, expected {expected}")


def tool_version(binary: str, expected: str) -> None:
    result = subprocess.run([binary, "--version"], check=True, capture_output=True, text=True)
    version = (result.stdout + result.stderr).splitlines()[0]
    if version != expected:
        raise SystemExit(f"{binary}: version {version!r}, expected {expected!r}")


def symbol_addresses(nm: str, elf: pathlib.Path) -> dict[str, int]:
    result = subprocess.run([nm, "-n", str(elf)], check=True, capture_output=True, text=True)
    symbols: dict[str, int] = {}
    for line in result.stdout.splitlines():
        fields = line.split()
        if len(fields) == 3 and fields[2] in {"_start", "fence_i_instruction"}:
            symbols[fields[2]] = int(fields[0], 16)
    return symbols


def main() -> int:
    gcc = shutil.which("riscv64-unknown-elf-gcc")
    objcopy = shutil.which("riscv64-unknown-elf-objcopy")
    nm = shutil.which("riscv64-unknown-elf-nm")
    if not gcc or not objcopy or not nm:
        raise SystemExit("install the Story 6.1 pinned riscv64-unknown-elf GCC/binutils")
    verify_tool_hash(gcc, EXPECTED_TOOL_SHA256["riscv64-unknown-elf-gcc"])
    verify_tool_hash(objcopy, EXPECTED_TOOL_SHA256["riscv64-unknown-elf-objcopy"])
    verify_tool_hash(nm, EXPECTED_TOOL_SHA256["riscv64-unknown-elf-nm"])
    tool_version(gcc, EXPECTED_GCC)
    tool_version(objcopy, EXPECTED_OBJCOPY)
    images: dict[str, bytes] = {}
    with tempfile.TemporaryDirectory(prefix="zifencei-image-") as tmp_name:
        tmp = pathlib.Path(tmp_name)
        for case, word in EXPECTED.items():
            elf, raw = tmp / f"{case}.elf", tmp / f"{case}.bin"
            subprocess.run([gcc, "-march=rv64imac", "-mabi=lp64", "-nostdlib", "-nostartfiles",
                            "-Wl,--build-id=none", f"-Wl,-T,{ROOT / 'fixture.ld'}",
                            "-o", str(elf), str(ROOT / f"{case}.S")], check=True)
            subprocess.run([objcopy, "-O", "binary", str(elf), str(raw)], check=True)
            symbols = symbol_addresses(nm, elf)
            if symbols.get("_start") != 0x80000000:
                raise SystemExit(f"{case}: _start is {symbols.get('_start')!r}, expected 0x80000000")
            if symbols.get("fence_i_instruction") != 0x80000020:
                raise SystemExit(f"{case}: FENCE.I symbol is {symbols.get('fence_i_instruction')!r}, expected 0x80000020")
            image = raw.read_bytes().ljust(0x1008, b"\0")
            if len(image) != 0x1008:
                raise SystemExit(f"{case}: image is {len(image)} bytes, expected 0x1008")
            words = struct.unpack("<" + "I" * (len(image) // 4), image)
            if words[8] != word:
                raise SystemExit(f"{case}: FENCE.I at image offset 0x20 is 0x{words[8]:08x}, expected 0x{word:08x}")
            images[case] = image
    baseline = images["standard"]
    for case, image in images.items():
        if len(image) != len(baseline):
            raise SystemExit(f"{case}: image length {len(image)} differs from standard {len(baseline)}")
        allowed = set(range(32, 36))
        if any(a != b and i not in allowed for i, (a, b) in enumerate(zip(baseline, image))):
            raise SystemExit(f"{case}: bytes outside the FENCE.I word differ from standard")
        (ROOT / f"{case}.hex").write_text("".join(
            f"{word:08x}\n" for word in struct.unpack("<" + "I" * (len(image) // 4), image)),
            encoding="ascii")
    print("built and validated standard, funct12, rs1, rd images")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
