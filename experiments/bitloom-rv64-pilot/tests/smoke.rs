use std::collections::BTreeMap;

use bitloom_prelude::PortValues;
use bitloom_rv64_pilot::rhdl_elaborate;
use bitloom_sim::Sim;

fn addi(rd: u32, rs1: u32, immediate: i32) -> u32 {
    (((immediate as u32) & 0xfff) << 20) | (rs1 << 15) | (rd << 7) | 0x13
}

fn add(rd: u32, rs1: u32, rs2: u32) -> u32 {
    (rs2 << 20) | (rs1 << 15) | (rd << 7) | 0x33
}

fn reg(rd: u32, rs1: u32, rs2: u32, funct3: u32, funct7: u32) -> u32 {
    (rs2 << 20) | (rs1 << 15) | (funct3 << 12) | (rd << 7) | (funct7 << 25) | 0x33
}

fn branch(rs1: u32, rs2: u32, offset: i32, funct3: u32) -> u32 {
    let imm = (offset as u32) & 0x1fff;
    (((imm >> 12) & 1) << 31)
        | (((imm >> 5) & 0x3f) << 25)
        | (rs2 << 20)
        | (rs1 << 15)
        | (funct3 << 12)
        | (((imm >> 1) & 0xf) << 8)
        | (((imm >> 11) & 1) << 7)
        | 0x63
}

fn beq(rs1: u32, rs2: u32, offset: i32) -> u32 {
    branch(rs1, rs2, offset, 0)
}

fn bne(rs1: u32, rs2: u32, offset: i32) -> u32 {
    branch(rs1, rs2, offset, 1)
}

fn lui(rd: u32, immediate20: u32) -> u32 {
    ((immediate20 & 0x000f_ffff) << 12) | (rd << 7) | 0x37
}

fn auipc(rd: u32, immediate20: u32) -> u32 {
    ((immediate20 & 0x000f_ffff) << 12) | (rd << 7) | 0x17
}

fn jal(rd: u32, offset: i32) -> u32 {
    let imm = (offset as u32) & 0x1f_ffff;
    (((imm >> 20) & 1) << 31)
        | (((imm >> 1) & 0x3ff) << 21)
        | (((imm >> 11) & 1) << 20)
        | (((imm >> 12) & 0xff) << 12)
        | (rd << 7)
        | 0x6f
}

fn ld(rd: u32, rs1: u32, immediate: i32) -> u32 {
    (((immediate as u32) & 0xfff) << 20) | (rs1 << 15) | (3 << 12) | (rd << 7) | 0x03
}

fn ld_kind(rd: u32, rs1: u32, immediate: i32, funct3: u32) -> u32 {
    (ld(rd, rs1, immediate) & !(7 << 12)) | ((funct3 & 7) << 12)
}

fn sd(rs2: u32, rs1: u32, immediate: i32) -> u32 {
    let imm = (immediate as u32) & 0xfff;
    (((imm >> 5) & 0x7f) << 25) | (rs2 << 20) | (rs1 << 15) | (3 << 12) | ((imm & 0x1f) << 7) | 0x23
}

fn sd_kind(rs2: u32, rs1: u32, immediate: i32, funct3: u32) -> u32 {
    (sd(rs2, rs1, immediate) & !(7 << 12)) | ((funct3 & 7) << 12)
}

fn reset() -> Sim {
    let mut sim = Sim::new(rhdl_elaborate().expect("design elaborates"));
    let mut inputs = PortValues::default();
    inputs.set("rst", 1);
    inputs.set("instruction_in", 0x13);
    inputs.set("debug_reg_addr", 0);
    sim.set_inputs(inputs);
    sim.tick();
    let mut inputs = PortValues::default();
    inputs.set("rst", 0);
    inputs.set("instruction_in", 0x13);
    inputs.set("debug_reg_addr", 0);
    sim.set_inputs(inputs);
    sim
}

fn run_program(sim: &mut Sim, program: &BTreeMap<u64, u32>, cycles: usize) -> Vec<u64> {
    let mut pcs = Vec::new();
    for _ in 0..cycles {
        let pc = sim.ports().get("fetch_pc").unwrap_or(0);
        pcs.push(pc);
        let mut inputs = PortValues::default();
        inputs.set("rst", 0);
        inputs.set(
            "instruction_in",
            u64::from(program.get(&pc).copied().unwrap_or(0x0000_0013)),
        );
        inputs.set("debug_reg_addr", 0);
        sim.set_inputs(inputs.clone());
        sim.tick();
    }
    pcs
}

fn register(sim: &mut Sim, index: u64) -> u64 {
    let mut inputs = PortValues::default();
    inputs.set("rst", 0);
    inputs.set("instruction_in", 0x0000_0013);
    inputs.set("debug_reg_addr", index);
    sim.set_inputs(inputs);
    sim.settle();
    sim.ports().get("debug_reg_data").unwrap()
}

#[test]
fn addi_and_add_write_back_64_bit_registers() {
    let mut program = BTreeMap::new();
    program.insert(0, addi(5, 0, 42));
    program.insert(16, addi(6, 5, 3));
    program.insert(32, add(7, 5, 6));
    program.insert(48, addi(8, 0, -1));
    program.insert(56, addi(13, 0, 2047));
    program.insert(60, addi(14, 0, -2048));
    program.insert(64, reg(9, 8, 5, 0, 0x20)); // SUB
    program.insert(80, reg(10, 8, 5, 7, 0)); // AND
    program.insert(96, reg(11, 8, 5, 6, 0)); // OR
    program.insert(112, reg(12, 8, 5, 4, 0)); // XOR
    let mut sim = reset();
    run_program(&mut sim, &program, 32);

    assert_eq!(register(&mut sim, 5), 42);
    assert_eq!(register(&mut sim, 6), 45);
    assert_eq!(register(&mut sim, 7), 87);
    assert_eq!(register(&mut sim, 8), u64::MAX);
    assert_eq!(register(&mut sim, 13), 2047);
    assert_eq!(register(&mut sim, 14), u64::MAX - 2047);
    assert_eq!(register(&mut sim, 9), u64::MAX - 42);
    assert_eq!(register(&mut sim, 10), 42);
    assert_eq!(register(&mut sim, 11), u64::MAX, "OR result");
    assert_eq!(register(&mut sim, 12), u64::MAX - 42);
    assert_eq!(register(&mut sim, 0), 0);
}

#[test]
fn negative_branch_and_jal_offsets_redirect_to_previous_pc() {
    let mut branch_program = BTreeMap::new();
    branch_program.insert(0, addi(1, 0, 1));
    branch_program.insert(16, bne(1, 0, -8));
    branch_program.insert(20, addi(2, 0, 99));
    let mut branch_sim = reset();
    let pcs = run_program(&mut branch_sim, &branch_program, 16);
    assert!(pcs.contains(&8), "negative branch target must be fetched");
    assert_eq!(register(&mut branch_sim, 2), 0);

    let mut jal_program = BTreeMap::new();
    jal_program.insert(8, jal(3, -4));
    jal_program.insert(12, addi(4, 0, 99));
    let mut jal_sim = reset();
    let pcs = run_program(&mut jal_sim, &jal_program, 16);
    assert!(pcs.contains(&4), "negative JAL target must be fetched");
    assert_eq!(register(&mut jal_sim, 3), 12);
    assert_eq!(register(&mut jal_sim, 4), 0);
}

#[test]
fn conditional_branches_redirect_and_flush_wrong_path() {
    let mut program = BTreeMap::new();
    program.insert(0, addi(1, 0, 7));
    program.insert(24, beq(1, 1, 8));
    program.insert(28, addi(2, 0, 99));
    program.insert(32, addi(3, 0, 9));
    program.insert(36, bne(1, 0, 8));
    program.insert(40, addi(4, 0, 77));
    program.insert(44, addi(5, 0, 11));
    program.insert(48, beq(1, 0, 8)); // not taken
    program.insert(52, addi(6, 0, 13));
    program.insert(56, bne(1, 1, 8)); // not taken
    program.insert(60, addi(7, 0, 15));
    let mut sim = reset();
    let pcs = run_program(&mut sim, &program, 28);

    assert!(
        pcs.contains(&32),
        "BEQ fetch sequence must include its target"
    );
    assert!(
        pcs.contains(&44),
        "BNE fetch sequence must include its target"
    );
    assert_eq!(
        register(&mut sim, 2),
        0,
        "BEQ wrong-path write must be flushed"
    );
    assert_eq!(register(&mut sim, 3), 9);
    assert_eq!(
        register(&mut sim, 4),
        0,
        "BNE wrong-path write must be flushed"
    );
    assert_eq!(register(&mut sim, 5), 11);
    assert_eq!(register(&mut sim, 6), 13);
    assert_eq!(register(&mut sim, 7), 15);
}

#[test]
fn lui_auipc_and_jal_compute_architectural_results() {
    let mut program = BTreeMap::new();
    program.insert(0, lui(10, 0x12345));
    program.insert(4, auipc(11, 1));
    program.insert(8, jal(12, 8));
    program.insert(12, addi(13, 0, 1));
    program.insert(16, addi(14, 0, 7));
    let mut sim = reset();
    let pcs = run_program(&mut sim, &program, 20);

    assert!(
        pcs.contains(&16),
        "JAL fetch sequence must include its target"
    );
    assert_eq!(register(&mut sim, 10), 0x1234_5000);
    assert_eq!(register(&mut sim, 11), 0x1004);
    assert_eq!(register(&mut sim, 12), 12);
    assert_eq!(
        register(&mut sim, 13),
        0,
        "JAL wrong-path write must be flushed"
    );
    assert_eq!(register(&mut sim, 14), 7);
}

#[test]
fn unsupported_instruction_is_reported_without_writeback() {
    let mut sim = reset();
    // Invalid opcode and unsupported R-type function encoding both report unsupported.
    for instruction in [0xffff_ffff, reg(1, 0, 0, 1, 0)] {
        let mut inputs = PortValues::default();
        inputs.set("rst", 0);
        inputs.set("instruction_in", instruction.into());
        inputs.set("debug_reg_addr", 0);
        sim.set_inputs(inputs.clone());
        sim.tick();

        assert_eq!(sim.ports().get("unsupported_instruction"), Some(1));
        for _ in 0..2 {
            inputs.set("instruction_in", 0x13);
            sim.set_inputs(inputs.clone());
            sim.tick();
        }
        assert_eq!(sim.ports().get("wb_valid"), Some(0));
    }
}

#[test]
fn synchronous_ld_sd_round_trip_keeps_read_metadata_aligned() {
    let mut program = BTreeMap::new();
    program.insert(0, addi(1, 0, 0));
    program.insert(4, ld(2, 1, 0));
    program.insert(8, 0x13);
    program.insert(12, 0x13);
    program.insert(16, 0x13);
    program.insert(20, 0x13);
    program.insert(24, sd(2, 1, 8));
    program.insert(28, 0x13);
    program.insert(32, 0x13);
    program.insert(36, 0x13);
    program.insert(40, ld(3, 1, 8));
    program.insert(44, 0x13);
    program.insert(48, 0x13);
    let mut sim = reset();
    let mut store_events = Vec::new();
    let mut load_writebacks = Vec::new();
    let mut retired_pcs = Vec::new();
    let mut pcs = Vec::new();
    for _ in 0..24 {
        let pc = sim.ports().get("fetch_pc").unwrap_or(0);
        pcs.push(pc);
        let mut inputs = PortValues::default();
        inputs.set("rst", 0);
        inputs.set(
            "instruction_in",
            u64::from(program.get(&pc).copied().unwrap_or(0x13)),
        );
        inputs.set("debug_reg_addr", 0);
        sim.set_inputs(inputs);
        sim.tick();
        if sim.ports().get("store_valid") == Some(1) {
            store_events.push((
                sim.ports().get("store_pc"),
                sim.ports().get("store_addr"),
                sim.ports().get("store_data"),
            ));
        }
        if sim.ports().get("wb_valid") == Some(1) {
            load_writebacks.push((
                sim.ports().get("wb_pc"),
                sim.ports().get("wb_rd"),
                sim.ports().get("wb_data"),
            ));
        }
        if sim.ports().get("retire_valid") == Some(1) {
            retired_pcs.push(sim.ports().get("retire_pc"));
        }
    }

    assert_eq!(register(&mut sim, 2), 0x1122_3344_5566_7788);
    assert_eq!(register(&mut sim, 3), 0x1122_3344_5566_7788);
    assert!(pcs.contains(&4) && pcs.contains(&24) && pcs.contains(&40));
    assert!(store_events.contains(&(Some(24), Some(8), Some(0x1122_3344_5566_7788))));
    assert!(load_writebacks.contains(&(Some(4), Some(2), Some(0x1122_3344_5566_7788))));
    assert!(load_writebacks.contains(&(Some(40), Some(3), Some(0x1122_3344_5566_7788))));
    assert!(
        retired_pcs.contains(&Some(0))
            && retired_pcs.contains(&Some(4))
            && retired_pcs.contains(&Some(24))
            && retired_pcs.contains(&Some(40))
    );
}

#[test]
fn store_then_addi_retire_in_pc_order_once_each() {
    let mut program = BTreeMap::new();
    program.insert(0, sd(0, 0, 0));
    program.insert(4, addi(1, 0, 7));
    let mut sim = reset();
    let mut retired_pcs = Vec::new();
    for _ in 0..12 {
        let pc = sim.ports().get("fetch_pc").unwrap_or(0);
        let mut inputs = PortValues::default();
        inputs.set("rst", 0);
        inputs.set("instruction_in", u64::from(*program.get(&pc).unwrap_or(&0x13)));
        inputs.set("debug_reg_addr", 0);
        sim.set_inputs(inputs);
        sim.tick();
        if sim.ports().get("retire_valid") == Some(1) {
            retired_pcs.push(sim.ports().get("retire_pc").unwrap());
        }
    }
    assert_eq!(retired_pcs.iter().filter(|&&pc| pc == 0).count(), 1);
    assert_eq!(retired_pcs.iter().filter(|&&pc| pc == 4).count(), 1);
    assert!(
        retired_pcs.iter().position(|&pc| pc == 0) < retired_pcs.iter().position(|&pc| pc == 4),
        "retirement order: {retired_pcs:?}"
    );
}

#[test]
fn consecutive_load_responses_keep_their_pc_and_destination() {
    let mut program = BTreeMap::new();
    program.insert(0, addi(1, 0, 0));
    program.insert(4, 0x13);
    program.insert(8, 0x13);
    program.insert(12, 0x13);
    program.insert(16, ld(2, 1, 0));
    program.insert(20, ld(3, 1, 8));
    program.insert(24, addi(4, 0, 9));
    let mut sim = reset();
    let mut writebacks = Vec::new();
    let mut retired_pcs = Vec::new();
    for _ in 0..22 {
        let pc = sim.ports().get("fetch_pc").unwrap_or(0);
        let mut inputs = PortValues::default();
        inputs.set("rst", 0);
        inputs.set(
            "instruction_in",
            u64::from(program.get(&pc).copied().unwrap_or(0x13)),
        );
        inputs.set("debug_reg_addr", 0);
        sim.set_inputs(inputs);
        sim.tick();
        if sim.ports().get("wb_valid") == Some(1) {
            writebacks.push((
                sim.ports().get("wb_pc"),
                sim.ports().get("wb_rd"),
                sim.ports().get("wb_data"),
            ));
        }
        if sim.ports().get("retire_valid") == Some(1) {
            retired_pcs.push(sim.ports().get("retire_pc"));
        }
    }
    assert_eq!(register(&mut sim, 2), 0x1122_3344_5566_7788);
    assert_eq!(register(&mut sim, 3), 0x8877_6655_4433_2211);
    assert_eq!(register(&mut sim, 4), 9);
    assert!(writebacks.contains(&(Some(16), Some(2), Some(0x1122_3344_5566_7788))));
    assert!(writebacks.contains(&(Some(20), Some(3), Some(0x8877_6655_4433_2211))));
    assert!(writebacks.contains(&(Some(24), Some(4), Some(9))));
    assert!(retired_pcs.contains(&Some(20)) && retired_pcs.contains(&Some(24)));
}

#[test]
fn unaligned_and_out_of_range_memory_operations_are_unsupported() {
    for instruction in [
        ld(2, 0, 1),
        ld(2, 0, 64),
        sd(2, 0, 64),
        ld_kind(2, 0, 0, 2),
        sd_kind(2, 0, 0, 2),
    ] {
        let mut sim = reset();
        let mut inputs = PortValues::default();
        inputs.set("rst", 0);
        inputs.set("instruction_in", u64::from(instruction));
        inputs.set("debug_reg_addr", 0);
        sim.set_inputs(inputs.clone());
        let mut saw_unsupported = false;
        let mut wrote_invalid_load = false;
        let mut saw_store = false;
        for _ in 0..5 {
            sim.tick();
            saw_unsupported |= sim.ports().get("unsupported_instruction") == Some(1);
            saw_store |= sim.ports().get("store_valid") == Some(1);
            wrote_invalid_load |=
                sim.ports().get("wb_valid") == Some(1) && sim.ports().get("wb_pc") == Some(0);
            inputs.set("instruction_in", 0x13);
            sim.set_inputs(inputs.clone());
        }
        assert!(saw_unsupported);
        assert!(!saw_store);
        if instruction == ld(2, 0, 1) {
            assert!(!wrote_invalid_load);
        }
        assert_eq!(register(&mut sim, 2), 0);
        assert_eq!(sim.ports().get("store_valid"), Some(0));
    }
}

#[test]
fn signed_store_offset_accepts_last_word_and_rejects_first_word_past_memory() {
    let mut program = BTreeMap::new();
    program.insert(0, addi(1, 0, 64));
    program.insert(4, addi(2, 0, 77));
    program.insert(8, 0x13);
    program.insert(12, 0x13);
    program.insert(16, sd(2, 1, -8)); // address 0x38, final valid word
    program.insert(20, 0x13);
    program.insert(24, 0x13);
    program.insert(28, ld(3, 1, -8));
    program.insert(32, 0x13);
    program.insert(36, 0x13);
    program.insert(40, sd(2, 1, 0)); // address 0x40, outside memory
    program.insert(44, 0x13);
    program.insert(48, 0x13);
    program.insert(52, ld(4, 0, 0)); // invalid SD must not alter mem[0]
    program.insert(56, 0x13);
    program.insert(60, 0x13);
    program.insert(64, ld(5, 1, 0)); // first out-of-range LD
    let mut sim = reset();
    let mut saw_last_word_store = false;
    let mut saw_invalid_store = false;
    let mut fetched_invalid_load = false;
    for _ in 0..48 {
        let pc = sim.ports().get("fetch_pc").unwrap_or(0);
        let mut inputs = PortValues::default();
        inputs.set("rst", 0);
        inputs.set(
            "instruction_in",
            u64::from(*program.get(&pc).unwrap_or(&0x13)),
        );
        inputs.set("debug_reg_addr", 0);
        sim.set_inputs(inputs);
        fetched_invalid_load |= pc == 64;
        sim.tick();
        saw_last_word_store |= sim.ports().get("store_valid") == Some(1)
            && sim.ports().get("store_addr") == Some(0x38);
        saw_invalid_store |= sim.ports().get("unsupported_instruction") == Some(1)
            && sim.ports().get("store_valid") != Some(1);
    }
    assert!(saw_last_word_store);
    assert!(saw_invalid_store);
    assert!(fetched_invalid_load);
    assert_eq!(register(&mut sim, 3), 77);
    assert_eq!(register(&mut sim, 4), 0x1122_3344_5566_7788);
    assert_eq!(register(&mut sim, 5), 0);
}
