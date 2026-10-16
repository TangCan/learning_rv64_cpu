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
