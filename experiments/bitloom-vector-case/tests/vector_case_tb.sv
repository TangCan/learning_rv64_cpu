`timescale 1ns/1ps

module vector_case_tb;
  reg clk = 0;
  reg rst = 1;
  reg vector_init = 0;
  reg [127:0] vector_a_init = 0;
  reg [127:0] vector_b_init = 0;
  reg vadd_enable = 0;
  reg [2:0] vl = 4;
  reg [1:0] sew = 2;
  reg [2:0] lmul = 0;
  wire vector_wb_valid;
  wire vector_unsupported;
  wire [127:0] vector_wb_data;

  BitloomVectorCase dut (.*);
  always #5 clk = ~clk;

  task initialize_vectors(input [127:0] a, input [127:0] b);
    begin
      vector_a_init = a;
      vector_b_init = b;
      vector_init = 1;
      @(posedge clk);
      #1 vector_init = 0;
    end
  endtask

  task run_case(input [127:0] a, input [127:0] b, input [127:0] expected);
    begin
      initialize_vectors(a, b);
      vadd_enable = 1;
      #1;
      if (!vector_wb_valid || vector_unsupported)
        $fatal(1, "supported vadd.vv was not accepted");
      @(posedge clk);
      #1;
      if (vector_wb_data !== expected)
        $fatal(1, "vadd result %032h, expected %032h", vector_wb_data, expected);
      vadd_enable = 0;
    end
  endtask

  task reject_config(input [2:0] test_vl, input [1:0] test_sew, input [2:0] test_lmul);
    reg [127:0] previous;
    begin
      previous = vector_wb_data;
      vl = test_vl;
      sew = test_sew;
      lmul = test_lmul;
      vadd_enable = 1;
      #1;
      if (vector_wb_valid || !vector_unsupported)
        $fatal(1, "unsupported vtype/VL configuration was accepted");
      @(posedge clk);
      #1;
      if (vector_wb_data !== previous)
        $fatal(1, "unsupported configuration changed vector destination");
      vadd_enable = 0;
      vl = 4;
      sew = 2;
      lmul = 0;
    end
  endtask

  initial begin
    #12 rst = 0;
    run_case(
      128'h00000000_7fffffff_00000001_ffffffff,
      128'hffffffff_00000001_ffffffff_00000001,
      128'hffffffff_80000000_00000000_00000000
    );
    run_case(
      128'h7fffffff_ffffffff_80000000_00000000,
      128'h00000001_00000001_80000000_ffffffff,
      128'h80000000_00000000_00000000_ffffffff
    );
    reject_config(3, 2, 0);
    reject_config(4, 1, 0);
    reject_config(4, 2, 1);
    $display("PASS: VLEN=128 SEW=32 LMUL=1 VL=4 vadd.vv lanes and rejects");
    $finish;
  end
endmodule
