module sky130_fd_sc_hd__and2 (
    X,
    A,
    B
);

    // Module ports
    output X;
    input  A;
    input  B;

    // Module supplies
    supply1 VPWR;
    supply0 VGND;
    supply1 VPB ;
    supply0 VNB ;

    // Local signals
    wire and0_out_X;

    //  Name  Output      Other arguments
    and and0 (and0_out_X, A, B           );
    buf buf0 (X         , and0_out_X     );

endmodule

module sky130_fd_sc_hd__and2_1 (
    X,
    A,
    B
);

    output X;
    input  A;
    input  B;

    // Voltage supply signals
    supply1 VPWR;
    supply0 VGND;
    supply1 VPB ;
    supply0 VNB ;

    sky130_fd_sc_hd__and2 base (
        .X(X),
        .A(A),
        .B(B)
    );

endmodule

module sky130_fd_sc_hd__xor2 (
    X,
    A,
    B
);

    // Module ports
    output X;
    input  A;
    input  B;

    // Local signals
    wire xor0_out_X;

    //  Name  Output      Other arguments
    xor xor0 (xor0_out_X, B, A           );
    buf buf0 (X         , xor0_out_X     );

endmodule

module sky130_fd_sc_hd__xor2_1 (
    X,
    A,
    B
);

    output X;
    input  A;
    input  B;

    // Voltage supply signals
    supply1 VPWR;
    supply0 VGND;
    supply1 VPB ;
    supply0 VNB ;

    sky130_fd_sc_hd__xor2 base (
        .X(X),
        .A(A),
        .B(B)
    );

endmodule

module sky130_fd_sc_hd__inv (
    Y,
    A
);

    // Module ports
    output Y;
    input  A;

    // Local signals
    wire not0_out_Y;

    //  Name  Output      Other arguments
    not not0 (not0_out_Y, A              );
    buf buf0 (Y         , not0_out_Y     );

endmodule

module sky130_fd_sc_hd__inv_1 (
    Y,
    A
);

    output Y;
    input  A;

    // Voltage supply signals
    supply1 VPWR;
    supply0 VGND;
    supply1 VPB ;
    supply0 VNB ;

    sky130_fd_sc_hd__inv base (
        .Y(Y),
        .A(A)
    );

endmodule

module sky130_fd_sc_hd__fa (
    COUT,
    SUM ,
    A   ,
    B   ,
    CIN
);

    // Module ports
    output COUT;
    output SUM ;
    input  A   ;
    input  B   ;
    input  CIN ;

    // Local signals
    wire or0_out     ;
    wire and0_out    ;
    wire and1_out    ;
    wire and2_out    ;
    wire nor0_out    ;
    wire nor1_out    ;
    wire or1_out_COUT;
    wire or2_out_SUM ;

    //  Name  Output        Other arguments
    or  or0  (or0_out     , CIN, B            );
    and and0 (and0_out    , or0_out, A        );
    and and1 (and1_out    , B, CIN            );
    or  or1  (or1_out_COUT, and1_out, and0_out);
    buf buf0 (COUT        , or1_out_COUT      );
    and and2 (and2_out    , CIN, A, B         );
    nor nor0 (nor0_out    , A, or0_out        );
    nor nor1 (nor1_out    , nor0_out, COUT    );
    or  or2  (or2_out_SUM , nor1_out, and2_out);
    buf buf1 (SUM         , or2_out_SUM       );

endmodule

module sky130_fd_sc_hd__fa_1 (
    COUT,
    SUM ,
    A   ,
    B   ,
    CIN
);

    output COUT;
    output SUM ;
    input  A   ;
    input  B   ;
    input  CIN ;

    // Voltage supply signals
    supply1 VPWR;
    supply0 VGND;
    supply1 VPB ;
    supply0 VNB ;

    sky130_fd_sc_hd__fa base (
        .COUT(COUT),
        .SUM(SUM),
        .A(A),
        .B(B),
        .CIN(CIN)
    );

endmodule

module sky130_fd_sc_hd__ha (
    COUT,
    SUM ,
    A   ,
    B
);

    // Module ports
    output COUT;
    output SUM ;
    input  A   ;
    input  B   ;

    // Local signals
    wire and0_out_COUT;
    wire xor0_out_SUM ;

    //  Name  Output         Other arguments
    and and0 (and0_out_COUT, A, B           );
    buf buf0 (COUT         , and0_out_COUT  );
    xor xor0 (xor0_out_SUM , B, A           );
    buf buf1 (SUM          , xor0_out_SUM   );

endmodule

module sky130_fd_sc_hd__ha_1 (
    COUT,
    SUM ,
    A   ,
    B
);

    output COUT;
    output SUM ;
    input  A   ;
    input  B   ;

    // Voltage supply signals
    supply1 VPWR;
    supply0 VGND;
    supply1 VPB ;
    supply0 VNB ;

    sky130_fd_sc_hd__ha base (
        .COUT(COUT),
        .SUM(SUM),
        .A(A),
        .B(B)
    );
endmodule

module sky130_fd_sc_hd__a21o (
    X ,
    A1,
    A2,
    B1
);

    // Module ports
    output X ;
    input  A1;
    input  A2;
    input  B1;

    // Local signals
    wire and0_out ;
    wire or0_out_X;

    //  Name  Output     Other arguments
    and and0 (and0_out , A1, A2         );
    or  or0  (or0_out_X, and0_out, B1   );
    buf buf0 (X        , or0_out_X      );

endmodule

module sky130_fd_sc_hd__a21o_1 (
    X ,
    A1,
    A2,
    B1
);

    output X ;
    input  A1;
    input  A2;
    input  B1;

    // Voltage supply signals
    supply1 VPWR;
    supply0 VGND;
    supply1 VPB ;
    supply0 VNB ;

    sky130_fd_sc_hd__a21o base (
        .X(X),
        .A1(A1),
        .A2(A2),
        .B1(B1)
    );

endmodule

module sky130_fd_sc_hd__a22o (
    X ,
    A1,
    A2,
    B1,
    B2
);

    // Module ports
    output X ;
    input  A1;
    input  A2;
    input  B1;
    input  B2;

    // Local signals
    wire and0_out ;
    wire and1_out ;
    wire or0_out_X;

    //  Name  Output     Other arguments
    and and0 (and0_out , B1, B2            );
    and and1 (and1_out , A1, A2            );
    or  or0  (or0_out_X, and1_out, and0_out);
    buf buf0 (X        , or0_out_X         );

endmodule

module sky130_fd_sc_hd__a22o_1 (
    X ,
    A1,
    A2,
    B1,
    B2
);

    output X ;
    input  A1;
    input  A2;
    input  B1;
    input  B2;

    // Voltage supply signals
    supply1 VPWR;
    supply0 VGND;
    supply1 VPB ;
    supply0 VNB ;

    sky130_fd_sc_hd__a22o base (
        .X(X),
        .A1(A1),
        .A2(A2),
        .B1(B1),
        .B2(B2)
    );

endmodule

module sky130_fd_sc_hd__a32o (
    X ,
    A1,
    A2,
    A3,
    B1,
    B2
);

    // Module ports
    output X ;
    input  A1;
    input  A2;
    input  A3;
    input  B1;
    input  B2;

    // Local signals
    wire and0_out ;
    wire and1_out ;
    wire or0_out_X;

    //  Name  Output     Other arguments
    and and0 (and0_out , A3, A1, A2        );
    and and1 (and1_out , B1, B2            );
    or  or0  (or0_out_X, and1_out, and0_out);
    buf buf0 (X        , or0_out_X         );

endmodule

module sky130_fd_sc_hd__a32o_1 (
    X ,
    A1,
    A2,
    A3,
    B1,
    B2
);

    output X ;
    input  A1;
    input  A2;
    input  A3;
    input  B1;
    input  B2;

    // Voltage supply signals
    supply1 VPWR;
    supply0 VGND;
    supply1 VPB ;
    supply0 VNB ;

    sky130_fd_sc_hd__a32o base (
        .X(X),
        .A1(A1),
        .A2(A2),
        .A3(A3),
        .B1(B1),
        .B2(B2)
    );

endmodule
