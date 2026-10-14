#!/usr/bin/env python3
"""Build and validate the four Story 6.4 RV64 images with the pinned cross tools."""
from __future__ import annotations

import pathlib
import shutil
import struct
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent
EXPECTED = {"standard": 0x0000100F, "funct12": 0x0010100F,
            "rs1": 0x0000900F, "rd": 0x0000108F}


def main() -> int:
    gcc = shutil.which("riscv64-unknown-elf-gcc")
    objcopy = shutil.which("riscv64-unknown-elf-objcopy")
    if not gcc or not objcopy:
        raise SystemExit("install the Story 6.1 pinned riscv64-unknown-elf GCC/binutils")
    images: dict[str, bytes] = {}
    with tempfile.TemporaryDirectory(prefix="zifencei-image-") as tmp_name:
        tmp = pathlib.Path(tmp_name)
        for case, word in EXPECTED.items():
            elf, raw = tmp / f"{case}.elf", tmp / f"{case}.bin"
            subprocess.run([gcc, "-march=rv64imac", "-mabi=lp64", "-nostdlib", "-nostartfiles",
                            "-Wl,--build-id=none", f"-Wl,-T,{ROOT / 'fixture.ld'}",
                            "-o", str(elf), str(ROOT / f"{case}.S")], check=True)
            subprocess.run([objcopy, "-O", "binary", str(elf), str(raw)], check=True)
            image = raw.read_bytes().ljust(0x1008, b"\0")
            words = struct.unpack("<" + "I" * (len(image) // 4), image)
            if words[8] != word:
                raise SystemExit(f"{case}: FENCE.I at image offset 0x20 is 0x{words[8]:08x}, expected 0x{word:08x}")
            images[case] = image
    baseline = images["standard"]
    for case, image in images.items():
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
