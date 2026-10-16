use bitloom_prelude::{ElaborateSession, GroundType, Span};

fn wire(session: &mut ElaborateSession, name: impl Into<String>, ty: &GroundType, span: Span) {
    session.declare_wire(name, ty.clone(), span);
}

fn reg(session: &mut ElaborateSession, name: impl Into<String>, ty: &GroundType, span: Span) {
    session.declare_reg(name, ty.clone(), span);
}

fn constant(session: &mut ElaborateSession, name: &str, width: u32, value: u64, span: Span) {
    wire(session, name, &GroundType::UInt { width }, span);
    session.assign_lit(name, value, span);
}

fn eq_const(
    session: &mut ElaborateSession,
    name: &str,
    source: &str,
    width: u32,
    value: u64,
    span: Span,
) {
    let constant_name = format!("{name}_constant");
    constant(session, &constant_name, width, value, span);
    wire(session, name, &GroundType::Bool, span);
    session.assign_eq(name, source, constant_name, span);
}

fn bool_and(session: &mut ElaborateSession, name: &str, lhs: &str, rhs: &str, span: Span) {
    wire(session, name, &GroundType::Bool, span);
    session.assign_and(name, lhs, rhs, span);
}

fn bool_or(session: &mut ElaborateSession, name: &str, lhs: &str, rhs: &str, span: Span) {
    wire(session, name, &GroundType::Bool, span);
    session.assign_or(name, lhs, rhs, span);
}

fn mux(
    session: &mut ElaborateSession,
    name: &str,
    select: &str,
    when_true: &str,
    when_false: &str,
    width: u32,
    span: Span,
) {
    wire(session, name, &GroundType::UInt { width }, span);
    session.assign_mux(name, select, when_true, when_false, span);
}

fn slice(
    session: &mut ElaborateSession,
    name: &str,
    source: &str,
    low: u32,
    width: u32,
    span: Span,
) {
    wire(session, name, &GroundType::UInt { width }, span);
    session.assign_slice(name, source, low, width, span);
}

fn concat(
    session: &mut ElaborateSession,
    name: &str,
    high: &str,
    high_width: u32,
    low: &str,
    low_width: u32,
    span: Span,
) {
    wire(
        session,
        name,
        &GroundType::UInt {
            width: high_width + low_width,
        },
        span,
    );
    session.assign_concat(name, high, low, span);
}

fn and_all(session: &mut ElaborateSession, name: &str, terms: &[String], span: Span) -> String {
    let mut value = terms[0].clone();
    for (index, term) in terms.iter().enumerate().skip(1) {
        let next = format!("{name}_{index}");
        bool_and(session, &next, &value, term, span);
        value = next;
    }
    value
}

fn or_all(session: &mut ElaborateSession, name: &str, terms: &[String], span: Span) -> String {
    let mut value = terms[0].clone();
    for (index, term) in terms.iter().enumerate().skip(1) {
        let next = format!("{name}_{index}");
        bool_or(session, &next, &value, term, span);
        value = next;
    }
    value
}

pub fn rhdl_elaborate() -> Result<bitloom_prelude::FrozenHir, bitloom_prelude::Diagnostics> {
    let p = Span::default();
    let u1 = &GroundType::UInt { width: 1 };
    let u3 = &GroundType::UInt { width: 3 };
    let u5 = &GroundType::UInt { width: 5 };
    let u7 = &GroundType::UInt { width: 7 };
    let u12 = &GroundType::UInt { width: 12 };
    let u20 = &GroundType::UInt { width: 20 };
    let u32 = &GroundType::UInt { width: 32 };
    let u64 = &GroundType::UInt { width: 64 };
    let mut s = ElaborateSession::new("BitloomRv64Pilot");
    s.begin_module("BitloomRv64Pilot", p);
    s.add_input("clk", GroundType::Clock, p);
    s.add_input("rst", GroundType::Reset, p);
    s.add_input("instruction_in", u32.clone(), p);
    s.add_input("debug_reg_addr", u5.clone(), p);
    s.add_output("fetch_pc", u64.clone(), p);
    s.add_output("debug_reg_data", u64.clone(), p);
    s.add_output("wb_valid", u1.clone(), p);
    s.add_output("wb_pc", u64.clone(), p);
    s.add_output("wb_rd", u5.clone(), p);
    s.add_output("wb_data", u64.clone(), p);
    s.add_output("unsupported_instruction", u1.clone(), p);

    // IF/ID, ID/EX, and EX/WB registers make each instruction's order explicit.
    for (name, ty) in [
        ("pc", u64),
        ("if_id_valid", u1),
        ("if_id_pc", u64),
        ("if_id_instruction", u32),
        ("id_ex_valid", u1),
        ("id_ex_pc", u64),
        ("id_ex_rs1", u64),
        ("id_ex_rs2", u64),
        ("id_ex_imm", u64),
        ("id_ex_rd", u5),
        ("id_ex_we", u1),
        ("id_ex_addi", u1),
        ("id_ex_add", u1),
        ("id_ex_sub", u1),
        ("id_ex_and", u1),
        ("id_ex_or", u1),
        ("id_ex_xor", u1),
        ("id_ex_lui", u1),
        ("id_ex_auipc", u1),
        ("id_ex_beq", u1),
        ("id_ex_bne", u1),
        ("id_ex_jal", u1),
        ("ex_wb_valid", u1),
        ("ex_wb_pc", u64),
        ("ex_wb_rd", u5),
        ("ex_wb_data", u64),
        ("ex_wb_we", u1),
    ] {
        reg(&mut s, name, ty, p);
    }
    for i in 1..32 {
        reg(&mut s, format!("x{i}"), u64, p);
    }
    s.begin_combinational(p);

    constant(&mut s, "zero1", 1, 0, p);
    constant(&mut s, "one1", 1, 1, p);
    constant(&mut s, "zero5", 5, 0, p);
    constant(&mut s, "zero64", 64, 0, p);
    constant(&mut s, "four64", 64, 4, p);
    constant(&mut s, "false_bool", 1, 0, p);
    constant(&mut s, "true_bool", 1, 1, p);

    // shortcut: unsupported encodings only raise unsupported_instruction; add trap state when exceptions enter scope.
    // Decode the instruction held in IF/ID.
    for (name, source, low, width, ty) in [
        ("opcode", "if_id_instruction", 0, 7, u7),
        ("rd", "if_id_instruction", 7, 5, u5),
        ("funct3", "if_id_instruction", 12, 3, u3),
        ("rs1_index", "if_id_instruction", 15, 5, u5),
        ("rs2_index", "if_id_instruction", 20, 5, u5),
        ("funct7", "if_id_instruction", 25, 7, u7),
        ("imm_i_bits", "if_id_instruction", 20, 12, u12),
        ("imm_u_bits", "if_id_instruction", 12, 20, u20),
    ] {
        wire(&mut s, name, ty, p);
        s.assign_slice(name, source, low, width, p);
    }
    for (name, bits) in [("imm_i", "imm_i_bits"), ("imm_u_signed", "imm_u_bits")] {
        wire(&mut s, name, u64, p);
        s.assign_sign_extend(name, bits, 64, p);
    }
    wire(&mut s, "imm_u", u64, p);
    s.assign_shl("imm_u", "imm_u_signed", "shift12", p);
    constant(&mut s, "shift12", 64, 12, p);

    slice(&mut s, "b12", "if_id_instruction", 31, 1, p);
    slice(&mut s, "b11", "if_id_instruction", 7, 1, p);
    slice(&mut s, "b10_5", "if_id_instruction", 25, 6, p);
    slice(&mut s, "b4_1", "if_id_instruction", 8, 4, p);
    constant(&mut s, "b0", 1, 0, p);
    concat(&mut s, "b_hi2", "b12", 1, "b11", 1, p);
    concat(&mut s, "b_hi8", "b_hi2", 2, "b10_5", 6, p);
    concat(&mut s, "b_hi12", "b_hi8", 8, "b4_1", 4, p);
    concat(&mut s, "imm_b_bits", "b_hi12", 12, "b0", 1, p);
    wire(&mut s, "imm_b", u64, p);
    s.assign_sign_extend("imm_b", "imm_b_bits", 64, p);

    slice(&mut s, "j20", "if_id_instruction", 31, 1, p);
    slice(&mut s, "j10_1", "if_id_instruction", 21, 10, p);
    slice(&mut s, "j11", "if_id_instruction", 20, 1, p);
    slice(&mut s, "j19_12", "if_id_instruction", 12, 8, p);
    constant(&mut s, "j0", 1, 0, p);
    concat(&mut s, "j_hi9", "j20", 1, "j19_12", 8, p);
    concat(&mut s, "j_hi10", "j_hi9", 9, "j11", 1, p);
    concat(&mut s, "j_hi20", "j_hi10", 10, "j10_1", 10, p);
    concat(&mut s, "imm_j_bits", "j_hi20", 20, "j0", 1, p);
    wire(&mut s, "imm_j", u64, p);
    s.assign_sign_extend("imm_j", "imm_j_bits", 64, p);

    let (op_i, op_r, op_lui, op_auipc, op_branch, op_jal) =
        ("op_i", "op_r", "op_lui", "op_auipc", "op_branch", "op_jal");
    for (name, value) in [
        (op_i, 0x13),
        (op_r, 0x33),
        (op_lui, 0x37),
        (op_auipc, 0x17),
        (op_branch, 0x63),
        (op_jal, 0x6f),
    ] {
        eq_const(&mut s, &format!("{name}_eq"), "opcode", 7, value, p);
    }
    for (name, value) in [
        ("f3_0", 0),
        ("f3_1", 1),
        ("f3_4", 4),
        ("f3_6", 6),
        ("f3_7", 7),
    ] {
        eq_const(&mut s, name, "funct3", 3, value, p);
    }
    for (name, value) in [("f7_0", 0), ("f7_20", 0x20)] {
        eq_const(&mut s, name, "funct7", 7, value, p);
    }

    for (op, opcode, funct3, funct7) in [
        ("addi", op_i, Some("f3_0"), None),
        ("add", op_r, Some("f3_0"), Some("f7_0")),
        ("sub", op_r, Some("f3_0"), Some("f7_20")),
        ("and", op_r, Some("f3_7"), Some("f7_0")),
        ("or", op_r, Some("f3_6"), Some("f7_0")),
        ("xor", op_r, Some("f3_4"), Some("f7_0")),
        ("beq", op_branch, Some("f3_0"), None),
        ("bne", op_branch, Some("f3_1"), None),
    ] {
        let mut terms = vec![format!("{opcode}_eq"), funct3.unwrap().to_owned()];
        if let Some(funct7) = funct7 {
            terms.push(funct7.to_owned());
        }
        let flag = and_all(&mut s, &format!("is_{op}"), &terms, p);
        wire(&mut s, format!("ctrl_{op}"), &GroundType::Bool, p);
        s.assign_net(format!("ctrl_{op}"), flag, p);
    }
    for (op, opcode) in [("lui", op_lui), ("auipc", op_auipc), ("jal", op_jal)] {
        wire(&mut s, format!("ctrl_{op}"), &GroundType::Bool, p);
        s.assign_net(format!("ctrl_{op}"), format!("{opcode}_eq"), p);
    }

    let supported_terms: Vec<String> = [
        "addi", "add", "sub", "and", "or", "xor", "lui", "auipc", "beq", "bne", "jal",
    ]
    .iter()
    .map(|name| format!("ctrl_{name}"))
    .collect();
    let supported = or_all(&mut s, "supported", &supported_terms, p);
    wire(&mut s, "unsupported", &GroundType::Bool, p);
    s.assign_eq("unsupported", supported, "false_bool", p);
    bool_and(&mut s, "illegal_raw", "if_id_valid", "unsupported", p);
    s.assign_net("unsupported_instruction", "illegal_raw", p);

    let write_terms: Vec<String> = [
        "addi", "add", "sub", "and", "or", "xor", "lui", "auipc", "jal",
    ]
    .iter()
    .map(|name| format!("ctrl_{name}"))
    .collect();
    let write_decode = or_all(&mut s, "write_decode", &write_terms, p);
    bool_and(&mut s, "write_valid", "if_id_valid", &write_decode, p);

    let mut imm_value = "zero64".to_owned();
    for (index, op, imm) in [
        (0, "addi", "imm_i"),
        (1, "beq", "imm_b"),
        (2, "bne", "imm_b"),
        (3, "jal", "imm_j"),
        (4, "lui", "imm_u"),
        (5, "auipc", "imm_u"),
    ] {
        let next = format!("decode_imm_{index}");
        mux(&mut s, &next, &format!("ctrl_{op}"), imm, &imm_value, 64, p);
        imm_value = next;
    }
    wire(&mut s, "decode_imm", u64, p);
    s.assign_net("decode_imm", imm_value, p);

    // A small register file is unrolled because this first slice has no memory subsystem.
    for (port, index_signal) in [
        ("rs1", "rs1_index"),
        ("rs2", "rs2_index"),
        ("debug", "debug_reg_addr"),
    ] {
        let mut selected = "zero64".to_owned();
        for i in 1..32 {
            let compare = format!("{port}_is_x{i}");
            eq_const(&mut s, &compare, index_signal, 5, i, p);
            let next = format!("{port}_select_x{i}");
            mux(&mut s, &next, &compare, &format!("x{i}"), &selected, 64, p);
            selected = next;
        }
        if port == "debug" {
            s.assign_net("debug_reg_data", selected, p);
        } else {
            wire(&mut s, format!("{port}_data"), u64, p);
            s.assign_net(format!("{port}_data"), selected, p);
        }
    }

    // Execute the decoded instruction and resolve BEQ/BNE/JAL in program order.
    for (name, lhs, rhs) in [
        ("r_add", "id_ex_rs1", "id_ex_rs2"),
        ("u_add", "id_ex_pc", "id_ex_imm"),
        ("sub_result", "id_ex_rs1", "id_ex_rs2"),
        ("and_result", "id_ex_rs1", "id_ex_rs2"),
        ("or_result", "id_ex_rs1", "id_ex_rs2"),
        ("xor_result", "id_ex_rs1", "id_ex_rs2"),
        ("branch_target", "id_ex_pc", "id_ex_imm"),
        ("jal_link", "id_ex_pc", "four64"),
        ("pc_plus4", "pc", "four64"),
    ] {
        wire(&mut s, name, u64, p);
        match name {
            "r_add" | "u_add" | "branch_target" | "jal_link" | "pc_plus4" => {
                s.assign_add(name, lhs, rhs, p)
            }
            "sub_result" => s.assign_sub(name, lhs, rhs, p),
            "and_result" => s.assign_and(name, lhs, rhs, p),
            "or_result" => s.assign_or(name, lhs, rhs, p),
            "xor_result" => s.assign_xor(name, lhs, rhs, p),
            _ => unreachable!(),
        }
    }
    mux(&mut s, "op2", "id_ex_addi", "id_ex_imm", "id_ex_rs2", 64, p);
    wire(&mut s, "addi_result", u64, p);
    s.assign_add("addi_result", "id_ex_rs1", "op2", p);
    wire(&mut s, "eq_operands", &GroundType::Bool, p);
    s.assign_eq("eq_operands", "id_ex_rs1", "id_ex_rs2", p);
    wire(&mut s, "not_equal", &GroundType::Bool, p);
    s.assign_eq("not_equal", "eq_operands", "false_bool", p);
    bool_and(&mut s, "take_beq", "id_ex_beq", "eq_operands", p);
    bool_and(&mut s, "take_bne", "id_ex_bne", "not_equal", p);
    bool_or(&mut s, "take_branch", "take_beq", "take_bne", p);
    bool_or(&mut s, "take_control", "take_branch", "id_ex_jal", p);
    bool_and(&mut s, "redirect", "id_ex_valid", "take_control", p);

    let mut alu_result = "zero64".to_owned();
    for (index, op, value) in [
        (0, "addi", "addi_result"),
        (1, "add", "r_add"),
        (2, "sub", "sub_result"),
        (3, "and", "and_result"),
        (4, "or", "or_result"),
        (5, "xor", "xor_result"),
        (6, "lui", "id_ex_imm"),
        (7, "auipc", "u_add"),
    ] {
        let next = format!("alu_result_{index}");
        mux(
            &mut s,
            &next,
            &format!("id_ex_{op}"),
            value,
            &alu_result,
            64,
            p,
        );
        alu_result = next;
    }
    mux(
        &mut s,
        "wb_data_next",
        "id_ex_jal",
        "jal_link",
        &alu_result,
        64,
        p,
    );
    bool_and(&mut s, "wb_we_next", "id_ex_valid", "id_ex_we", p);
    mux(
        &mut s,
        "pc_next",
        "redirect",
        "branch_target",
        "pc_plus4",
        64,
        p,
    );
    s.assign_net("fetch_pc", "pc", p);
    s.assign_net("wb_valid", "ex_wb_valid", p);
    s.assign_net("wb_pc", "ex_wb_pc", p);
    s.assign_net("wb_rd", "ex_wb_rd", p);
    s.assign_net("wb_data", "ex_wb_data", p);

    // shortcut: no forwarding or stalls; add them when tests require gapless dependent instructions.
    // Clock IF/ID -> ID/EX -> EX/WB; redirect flushes both younger instructions.
    let id_flush = "id_ex_invalid_after_redirect".to_owned();
    let if_flush = "if_id_invalid_after_redirect".to_owned();
    wire(&mut s, &id_flush, u1, p);
    wire(&mut s, &if_flush, u1, p);
    s.assign_mux(&id_flush, "redirect", "zero1", "if_id_valid", p);
    s.assign_mux(&if_flush, "redirect", "zero1", "one1", p);
    for i in 1..32 {
        let compare = format!("wb_is_x{i}");
        eq_const(&mut s, &compare, "ex_wb_rd", 5, i, p);
        let write = format!("write_x{i}");
        bool_and(&mut s, &write, "ex_wb_we", &compare, p);
        mux(
            &mut s,
            &format!("x{i}_next"),
            &write,
            "ex_wb_data",
            &format!("x{i}"),
            64,
            p,
        );
    }
    s.end_process();
    s.begin_sequential(p);
    s.assign_reg_d_from("pc", "pc_next", p);
    s.assign_reg_d_from("if_id_valid", if_flush, p);
    s.assign_reg_d_from("if_id_pc", "pc", p);
    s.assign_reg_d_from("if_id_instruction", "instruction_in", p);
    s.assign_reg_d_from("id_ex_valid", id_flush, p);
    s.assign_reg_d_from("id_ex_pc", "if_id_pc", p);
    s.assign_reg_d_from("id_ex_rs1", "rs1_data", p);
    s.assign_reg_d_from("id_ex_rs2", "rs2_data", p);
    s.assign_reg_d_from("id_ex_imm", "decode_imm", p);
    s.assign_reg_d_from("id_ex_rd", "rd", p);
    s.assign_reg_d_from("id_ex_we", "write_valid", p);
    for op in [
        "addi", "add", "sub", "and", "or", "xor", "lui", "auipc", "beq", "bne", "jal",
    ] {
        s.assign_reg_d_from(format!("id_ex_{op}"), format!("ctrl_{op}"), p);
    }
    s.assign_reg_d_from("ex_wb_valid", "wb_we_next", p);
    s.assign_reg_d_from("ex_wb_pc", "id_ex_pc", p);
    s.assign_reg_d_from("ex_wb_rd", "id_ex_rd", p);
    s.assign_reg_d_from("ex_wb_data", "wb_data_next", p);
    s.assign_reg_d_from("ex_wb_we", "wb_we_next", p);
    for i in 1..32 {
        s.assign_reg_d_from(format!("x{i}"), format!("x{i}_next"), p);
    }
    s.end_process();

    s.end_module();
    s.finish()
}
