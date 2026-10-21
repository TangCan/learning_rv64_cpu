---
title: 'Kunminghu 单条 RV64I LD 提交与结果观察'
type: 'feature'
created: '2026-10-16'
status: 'complete'
route: 'oneshot'
context:
  - '{project-root}/_agile-output/specs/spec-rv64-ld-dynamic-validation/SPEC.md'
  - '{project-root}/notes/units/load-v2.md'
  - '{project-root}/experiments/kunminghu-smoke/README.md'
---

## Goal

Use the existing locked Kunminghu runner and native commit trace to run one self-checking, naturally aligned RV64I `LD`, and require the target PC, instruction encoding, effective address, destination register value, and terminal good trap to match.

## Result

- Added `experiments/kunminghu-smoke/ld.S` and `--topic ld` runner support without modifying `sources/xiangshan`.
- Run `kunminghu-fixture-20261016T075949Z-3e81181d1d02` passed with NEMU difftest. Target commit: PC `0x80000008`, instruction `0x0002b303`, EA `0x80000040`, x6=`0x123456789abcdef0`; fixture reached GOODTRAP.
- Added focused parser tests; 2 tests passed. `py_compile` passed.
- DCache hit is not visible in the runner output and remains unverified. This input is not the Heliodor suite input and does not establish dual-core equivalence.
