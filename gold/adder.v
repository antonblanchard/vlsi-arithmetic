module gold_adder
#(
    parameter BITS=64
) (
    input [BITS-1:0] a,
    input [BITS-1:0] b,
    output [BITS-1:0] o
);
    assign o = a + b;
endmodule
