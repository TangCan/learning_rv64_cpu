use bitloom_prelude::GroundType;
use bitloom_rv64_pilot::rhdl_elaborate;
use bitloom_sim::Sim;

#[test]
fn counter_ticks_and_wide_ports_elaborate() {
    let design = rhdl_elaborate().expect("design elaborates");
    let module = &design.circuit().modules[0];
    assert_eq!(
        module
            .ports
            .iter()
            .find(|port| port.name == "u64_in")
            .unwrap()
            .ty,
        GroundType::UInt { width: 64 }
    );
    assert_eq!(
        module
            .ports
            .iter()
            .find(|port| port.name == "u128_in")
            .unwrap()
            .ty,
        GroundType::UInt { width: 128 }
    );

    let mut sim = Sim::new(design);
    sim.tick();
    assert_eq!(sim.ports().get("count_out"), Some(1));
    sim.tick();
    assert_eq!(sim.ports().get("count_out"), Some(2));
}
