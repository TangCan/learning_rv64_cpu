use bitloom_prelude::{ElaborateSession, FrozenHir, GroundType, Span};

pub fn rhdl_elaborate() -> Result<FrozenHir, bitloom_prelude::Diagnostics> {
    let p = Span::default();
    let bit = GroundType::UInt { width: 1 };
    let u2 = GroundType::UInt { width: 2 };
    let u3 = GroundType::UInt { width: 3 };
    let u32 = GroundType::UInt { width: 32 };
    let u128 = GroundType::UInt { width: 128 };
    let mut s = ElaborateSession::new("BitloomVectorCase");
    s.begin_module("BitloomVectorCase", p);
    s.add_input("clk", GroundType::Clock, p);
    s.add_input("rst", GroundType::Reset, p);
    s.add_input("vector_init", bit.clone(), p);
    s.add_input("vector_a_init", u128.clone(), p);
    s.add_input("vector_b_init", u128.clone(), p);
    s.add_input("vadd_enable", bit.clone(), p);
    s.add_input("vl", u3.clone(), p);
    s.add_input("sew", u2.clone(), p);
    s.add_input("lmul", u3.clone(), p);
    s.add_output("vector_wb_valid", bit.clone(), p);
    s.add_output("vector_unsupported", bit.clone(), p);
    s.add_output("vector_wb_data", u128.clone(), p);

    for name in ["vector_a", "vector_b", "vector_d"] {
        s.declare_reg(name, u128.clone(), p);
    }
    s.begin_combinational(p);
    s.declare_wire("zero128", u128.clone(), p);
    s.assign_lit("zero128", 0, p);
    for (name, input, width, value) in [
        ("vl_is_4", "vl", 3, 4),
        ("sew_is_32", "sew", 2, 2),
        ("lmul_is_1", "lmul", 3, 0),
    ] {
        s.declare_wire(name, GroundType::Bool, p);
        s.declare_wire(format!("{name}_constant"), GroundType::UInt { width }, p);
        s.assign_lit(format!("{name}_constant"), value, p);
        s.assign_eq(name, input, format!("{name}_constant"), p);
    }
    s.declare_wire("cfg_vl_sew", GroundType::Bool, p);
    s.assign_and("cfg_vl_sew", "vl_is_4", "sew_is_32", p);
    s.declare_wire("cfg_valid", GroundType::Bool, p);
    s.assign_and("cfg_valid", "cfg_vl_sew", "lmul_is_1", p);
    s.assign_and("vector_wb_valid", "vadd_enable", "cfg_valid", p);
    s.declare_wire("cfg_invalid", GroundType::Bool, p);
    s.assign_eq("cfg_invalid", "cfg_valid", "zero1", p);
    s.declare_wire("zero1", GroundType::UInt { width: 1 }, p);
    s.assign_lit("zero1", 0, p);
    s.assign_and("vector_unsupported", "vadd_enable", "cfg_invalid", p);

    let mut lanes = Vec::new();
    for lane in 0..4 {
        let a = format!("a{lane}");
        let b = format!("b{lane}");
        let sum = format!("sum{lane}");
        s.declare_wire(&a, u32.clone(), p);
        s.assign_slice(&a, "vector_a", lane * 32, 32, p);
        s.declare_wire(&b, u32.clone(), p);
        s.assign_slice(&b, "vector_b", lane * 32, 32, p);
        s.declare_wire(&sum, u32.clone(), p);
        s.assign_add(&sum, &a, &b, p);
        lanes.push(sum);
    }
    for (name, high, high_width, low, low_width) in [
        ("sum_lo", lanes[1].as_str(), 32, lanes[0].as_str(), 32),
        ("sum_mid", lanes[2].as_str(), 32, "sum_lo", 64),
        ("sum_all", lanes[3].as_str(), 32, "sum_mid", 96),
    ] {
        s.declare_wire(
            name,
            GroundType::UInt {
                width: high_width + low_width,
            },
            p,
        );
        s.assign_concat(name, high, low, p);
    }

    for (name, select, yes, no) in [
        ("vector_a_next", "rst", "zero128", "vector_a"),
        ("vector_b_next", "rst", "zero128", "vector_b"),
    ] {
        s.declare_wire(name, u128.clone(), p);
        s.assign_mux(name, select, yes, no, p);
    }
    s.declare_wire("vector_a_init_or_hold", u128.clone(), p);
    s.assign_mux(
        "vector_a_init_or_hold",
        "vector_init",
        "vector_a_init",
        "vector_a_next",
        p,
    );
    s.declare_wire("vector_b_init_or_hold", u128.clone(), p);
    s.assign_mux(
        "vector_b_init_or_hold",
        "vector_init",
        "vector_b_init",
        "vector_b_next",
        p,
    );
    s.declare_wire("vector_d_after_add", u128.clone(), p);
    s.assign_mux(
        "vector_d_after_add",
        "vector_wb_valid",
        "sum_all",
        "vector_d",
        p,
    );
    s.declare_wire("vector_d_after_init", u128.clone(), p);
    s.assign_mux(
        "vector_d_after_init",
        "vector_init",
        "zero128",
        "vector_d_after_add",
        p,
    );
    s.declare_wire("vector_d_next", u128.clone(), p);
    s.assign_mux("vector_d_next", "rst", "zero128", "vector_d_after_init", p);
    s.assign_net("vector_wb_data", "vector_d", p);
    s.end_process();

    s.begin_sequential(p);
    s.assign_reg_d_from("vector_a", "vector_a_init_or_hold", p);
    s.assign_reg_d_from("vector_b", "vector_b_init_or_hold", p);
    s.assign_reg_d_from("vector_d", "vector_d_next", p);
    s.end_process();
    s.end_module();
    s.finish()
}
