module BitloomVectorCase (
  input clk,
  input rst,
  input vector_init,
  input [127:0] vector_a_init,
  input [127:0] vector_b_init,
  input vadd_enable,
  input [2:0] vl,
  input [1:0] sew,
  input [2:0] lmul,
  output vector_wb_valid,
  output vector_unsupported,
  output [127:0] vector_wb_data
);
  reg [127:0] vector_a;
  reg [127:0] vector_b;
  reg [127:0] vector_d;
  wire [127:0] zero128;
  wire vl_is_4;
  wire [2:0] vl_is_4_constant;
  wire sew_is_32;
  wire [1:0] sew_is_32_constant;
  wire lmul_is_1;
  wire [2:0] lmul_is_1_constant;
  wire cfg_vl_sew;
  wire cfg_valid;
  wire cfg_invalid;
  wire zero1;
  wire [31:0] a0;
  wire [31:0] b0;
  wire [31:0] sum0;
  wire [31:0] a1;
  wire [31:0] b1;
  wire [31:0] sum1;
  wire [31:0] a2;
  wire [31:0] b2;
  wire [31:0] sum2;
  wire [31:0] a3;
  wire [31:0] b3;
  wire [31:0] sum3;
  wire [63:0] sum_lo;
  wire [95:0] sum_mid;
  wire [127:0] sum_all;
  wire [127:0] vector_a_next;
  wire [127:0] vector_b_next;
  wire [127:0] vector_a_init_or_hold;
  wire [127:0] vector_b_init_or_hold;
  wire [127:0] vector_d_after_add;
  wire [127:0] vector_d_after_init;
  wire [127:0] vector_d_next;
  assign zero128 = 0;
  assign vl_is_4_constant = 4;
  assign vl_is_4 = (vl == vl_is_4_constant);
  assign sew_is_32_constant = 2;
  assign sew_is_32 = (sew == sew_is_32_constant);
  assign lmul_is_1_constant = 0;
  assign lmul_is_1 = (lmul == lmul_is_1_constant);
  assign cfg_vl_sew = (vl_is_4 & sew_is_32);
  assign cfg_valid = (cfg_vl_sew & lmul_is_1);
  assign vector_wb_valid = (vadd_enable & cfg_valid);
  assign cfg_invalid = (cfg_valid == zero1);
  assign zero1 = 0;
  assign vector_unsupported = (vadd_enable & cfg_invalid);
  assign a0 = vector_a[31:0];
  assign b0 = vector_b[31:0];
  assign sum0 = a0 + b0;
  assign a1 = vector_a[63:32];
  assign b1 = vector_b[63:32];
  assign sum1 = a1 + b1;
  assign a2 = vector_a[95:64];
  assign b2 = vector_b[95:64];
  assign sum2 = a2 + b2;
  assign a3 = vector_a[127:96];
  assign b3 = vector_b[127:96];
  assign sum3 = a3 + b3;
  assign sum_lo = {sum1, sum0};
  assign sum_mid = {sum2, sum_lo};
  assign sum_all = {sum3, sum_mid};
  assign vector_a_next = (rst ? zero128 : vector_a);
  assign vector_b_next = (rst ? zero128 : vector_b);
  assign vector_a_init_or_hold = (vector_init ? vector_a_init : vector_a_next);
  assign vector_b_init_or_hold = (vector_init ? vector_b_init : vector_b_next);
  assign vector_d_after_add = (vector_wb_valid ? sum_all : vector_d);
  assign vector_d_after_init = (vector_init ? zero128 : vector_d_after_add);
  assign vector_d_next = (rst ? zero128 : vector_d_after_init);
  assign vector_wb_data = vector_d;
  always @(posedge clk) begin
    if (rst) begin
      vector_a <= 0;
      vector_b <= 0;
      vector_d <= 0;
    end else begin
      vector_a <= vector_a_init_or_hold;
      vector_b <= vector_b_init_or_hold;
      vector_d <= vector_d_next;
    end
  end
endmodule

