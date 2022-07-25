module gf180mcu_fd_sc_mcu7t5v0__and2_1( A1, A2, Z );
input A1, A2;
output Z;

        and MGM_BG_0( Z, A1, A2 );

endmodule

module gf180mcu_fd_sc_mcu7t5v0__xor2_1( A2, A1, Z );
input A1, A2;
output Z;

        wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__xor2_1;

        not MGM_BG_0( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__xor2_1, A2 );

        wire Z_row1;

        and MGM_BG_1( Z_row1, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__xor2_1, A1 );

        wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__xor2_1;

        not MGM_BG_2( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__xor2_1, A1 );

        wire Z_row2;

        and MGM_BG_3( Z_row2, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__xor2_1, A2 );

        or MGM_BG_4( Z, Z_row1, Z_row2 );

endmodule

module gf180mcu_fd_sc_mcu7t5v0__inv_1( I, ZN );
input I;
output ZN;

        not MGM_BG_0( ZN, I );

endmodule

module gf180mcu_fd_sc_mcu7t5v0__addf_1( S, A, CI, B, CO );
input A, B, CI;
output CO, S;

        wire CO_row1;

        and MGM_BG_0( CO_row1, A, B );

        wire CO_row2;

        and MGM_BG_1( CO_row2, A, CI );

        wire CO_row3;

        and MGM_BG_2( CO_row3, B, CI );

        or MGM_BG_3( CO, CO_row1, CO_row2, CO_row3 );

        wire S_row1;

        and MGM_BG_4( S_row1, A, B, CI );

        wire B_inv_for_gf180mcu_fd_sc_mcu7t5v0__addf_1;

        not MGM_BG_5( B_inv_for_gf180mcu_fd_sc_mcu7t5v0__addf_1, B );

        wire CI_inv_for_gf180mcu_fd_sc_mcu7t5v0__addf_1;

        not MGM_BG_6( CI_inv_for_gf180mcu_fd_sc_mcu7t5v0__addf_1, CI );

        wire S_row2;

        and MGM_BG_7( S_row2, B_inv_for_gf180mcu_fd_sc_mcu7t5v0__addf_1, CI_inv_for_gf180mcu_fd_sc_mcu7t5v0__addf_1, A );

        wire A_inv_for_gf180mcu_fd_sc_mcu7t5v0__addf_1;

        not MGM_BG_8( A_inv_for_gf180mcu_fd_sc_mcu7t5v0__addf_1, A );

        wire S_row3;

        and MGM_BG_9( S_row3, A_inv_for_gf180mcu_fd_sc_mcu7t5v0__addf_1, CI_inv_for_gf180mcu_fd_sc_mcu7t5v0__addf_1, B );

        wire S_row4;

        and MGM_BG_10( S_row4, A_inv_for_gf180mcu_fd_sc_mcu7t5v0__addf_1, B_inv_for_gf180mcu_fd_sc_mcu7t5v0__addf_1, CI );

        or MGM_BG_11( S, S_row1, S_row2, S_row3, S_row4 );

endmodule

module gf180mcu_fd_sc_mcu7t5v0__addh_1( CO, A, B, S );
input A, B;
output CO, S;

        and MGM_BG_0( CO, A, B );

        wire B_inv_for_gf180mcu_fd_sc_mcu7t5v0__addh_1;

        not MGM_BG_1( B_inv_for_gf180mcu_fd_sc_mcu7t5v0__addh_1, B );

        wire S_row1;

        and MGM_BG_2( S_row1, B_inv_for_gf180mcu_fd_sc_mcu7t5v0__addh_1, A );

        wire A_inv_for_gf180mcu_fd_sc_mcu7t5v0__addh_1;

        not MGM_BG_3( A_inv_for_gf180mcu_fd_sc_mcu7t5v0__addh_1, A );

        wire S_row2;

        and MGM_BG_4( S_row2, A_inv_for_gf180mcu_fd_sc_mcu7t5v0__addh_1, B );

        or MGM_BG_5( S, S_row1, S_row2 );

endmodule

module gf180mcu_fd_sc_mcu7t5v0__aoi21_1( A2, ZN, A1, B );
input A1, A2, B;
output ZN;

        wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi21_1;

        not MGM_BG_0( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi21_1, A1 );

        wire B_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi21_1;

        not MGM_BG_1( B_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi21_1, B );

        wire ZN_row1;

        and MGM_BG_2( ZN_row1, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi21_1, B_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi21_1 );

        wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi21_1;

        not MGM_BG_3( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi21_1, A2 );

        wire ZN_row2;

        and MGM_BG_4( ZN_row2, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi21_1, B_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi21_1 );

        or MGM_BG_5( ZN, ZN_row1, ZN_row2 );

endmodule

module gf180mcu_fd_sc_mcu7t5v0__aoi22_1( B2, B1, ZN, A1, A2 );
input A1, A2, B1, B2;
output ZN;

        wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1;

        not MGM_BG_0( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1, A1 );

        wire B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1;

        not MGM_BG_1( B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1, B1 );

        wire ZN_row1;

        and MGM_BG_2( ZN_row1, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1, B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1 );

        wire B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1;

        not MGM_BG_3( B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1, B2 );

        wire ZN_row2;

        and MGM_BG_4( ZN_row2, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1, B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1 );

        wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1;

        not MGM_BG_5( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1, A2 );

        wire ZN_row3;

        and MGM_BG_6( ZN_row3, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1, B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1 );

        wire ZN_row4;

        and MGM_BG_7( ZN_row4, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1, B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__aoi22_1 );

        or MGM_BG_8( ZN, ZN_row1, ZN_row2, ZN_row3, ZN_row4 );

endmodule

module gf180mcu_fd_sc_mcu7t5v0__oai33_1( B3, B2, B1, ZN, A1, A2, A3 );
input A1, A2, A3, B1, B2, B3;
output ZN;

        wire A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai33_1;

        not MGM_BG_0( A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai33_1, A1 );

        wire A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai33_1;

        not MGM_BG_1( A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai33_1, A2 );

        wire A3_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai33_1;

        not MGM_BG_2( A3_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai33_1, A3 );

        wire ZN_row1;

        and MGM_BG_3( ZN_row1, A1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai33_1, A2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai33_1, A3_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai33_1 );

        wire B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai33_1;

        not MGM_BG_4( B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai33_1, B1 );

        wire B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai33_1;

        not MGM_BG_5( B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai33_1, B2 );

        wire B3_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai33_1;

        not MGM_BG_6( B3_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai33_1, B3 );

        wire ZN_row2;

        and MGM_BG_7( ZN_row2, B1_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai33_1, B2_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai33_1, B3_inv_for_gf180mcu_fd_sc_mcu7t5v0__oai33_1 );

        or MGM_BG_8( ZN, ZN_row1, ZN_row2 );

endmodule
