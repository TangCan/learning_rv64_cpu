use bitloom_prelude::{ElaborateSession, GroundType, Span};

pub fn rhdl_elaborate() -> Result<bitloom_prelude::FrozenHir, bitloom_prelude::Diagnostics> {
    let span = Span::default();
    let mut session = ElaborateSession::new("BitloomRv64Pilot");
    session.begin_module("BitloomRv64Pilot", span);
    session.add_input("clk", GroundType::Clock, span);
    session.add_input("rst", GroundType::Reset, span);
    session.add_input("u64_in", GroundType::UInt { width: 64 }, span);
    session.add_output("u64_out", GroundType::UInt { width: 64 }, span);
    session.add_input("u128_in", GroundType::UInt { width: 128 }, span);
    session.add_output("u128_out", GroundType::UInt { width: 128 }, span);
    session.add_output("count_out", GroundType::UInt { width: 8 }, span);
    session.declare_reg("count", GroundType::UInt { width: 8 }, span);
    session.declare_sync_read_mem("memory", 16, 64, span);

    session.begin_sequential(span);
    session.assign_reg_d_inc("count", span);
    session.end_process();

    session.begin_combinational(span);
    session.assign_net("u64_out", "u64_in", span);
    session.assign_net("u128_out", "u128_in", span);
    session.assign_net("count_out", "count", span);
    session.end_process();
    session.end_module();
    session.finish()
}
