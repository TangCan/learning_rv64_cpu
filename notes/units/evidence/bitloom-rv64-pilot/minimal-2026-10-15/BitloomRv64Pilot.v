module BitloomRv64Pilot (
  input clk,
  input rst,
  input [63:0] u64_in,
  output [63:0] u64_out,
  input [127:0] u128_in,
  output [127:0] u128_out,
  output [7:0] count_out
);
  reg [7:0] count;
  reg [63:0] memory [0:15]; /* SyncReadMem */
  always @(posedge clk) begin
    if (rst) begin
      count <= 0;
    end else begin
      count <= count + 1;
    end
  end
  assign u64_out = u64_in;
  assign u128_out = u128_in;
  assign count_out = count;
endmodule
