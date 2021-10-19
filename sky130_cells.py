from nmigen import Elaboratable, Instance

class SKY130(Elaboratable):
    def _generate_and(self, a, b, o):
        andgate = Instance(
            "sky130_fd_sc_hd__and2_1",
            i_A=a,
            i_B=b,
            o_X=o,
            #i_VPWR=
            #i_VGND=
            #i_VPB=
            #i_VNB=
        )

        self.m.submodules += andgate

    def _generate_xor(self, a, b, o):
        xorgate = Instance(
            "sky130_fd_sc_hd__xor2_1",
            i_A=a,
            i_B=b,
            o_X=o,
            #i_VPWR=
            #i_VGND=
            #i_VPB=
            #i_VNB=
        )

        self.m.submodules += xorgate

    def _generate_inv(self, a, o):
        invgate = Instance(
            "sky130_fd_sc_hd__inv_1",
            i_A=a,
            o_Y=o,
            #i_VPWR=
            #i_VGND=
            #i_VPB=
            #i_VNB=
        )

        self.m.submodules += invgate

    def _generate_full_adder(self, a, b, carry_in, sum_out, carry_out, name):
        fa = Instance(
            "sky130_fd_sc_hd__fa_1",
            o_COUT=carry_out,
            o_SUM=sum_out,
            i_A=a,
            i_B=b,
            i_CIN=carry_in,
            #i_VPWR=
            #i_VGND=
            #i_VPB=
            #i_VNB=
        )

        self.m.submodules[name] = fa

    def _generate_half_adder(self, a, b, sum_out, carry_out):
        ha = Instance(
            "sky130_fd_sc_hd__ha_1",
            o_COUT=carry_out,
            o_SUM=sum_out,
            i_A=a,
            i_B=b,
            #i_VPWR=
            #i_VGND=
            #i_VPB=
            #i_VNB=
        )

        self.m.submodules += ha

    # Used in adder
    def _generate_and21_or2(self, a1, a2, b1, o):
        # 2-input AND into first input of 2-input OR
        a21o = Instance(
            "sky130_fd_sc_hd__a21o_1",
            o_X=o,
            i_A1=a1,
            i_A2=a2,
            i_B1=b1,
            #i_VPWR=
            #i_VGND=
            #i_VPB=
            #i_VNB=
        )

        self.m.submodules += a21o

    # Used in multiplier
    def _generate_and2_or2(self, a1, a2, b1, b2, o):
        # 2-input AND into both inputs of 2-input OR
        a22ogate = Instance(
            "sky130_fd_sc_hd__a22o_1",
            i_A1=a1,
            i_A2=a2,
            i_B1=b1,
            i_B2=b2,
            o_X=o,
            #i_VPWR=
            #i_VGND=
            #i_VPB=
            #i_VNB=
        )

        self.m.submodules += a22ogate

    # Used in multiplier
    def _generate_and32_or2(self, a1, a2, a3, b1, b2, o):
        # 3-input AND into first input, and 2-input AND into 2nd input of 2-input OR
        a32ogate = Instance(
            "sky130_fd_sc_hd__a32o_1",
            i_A1=a1,
            i_A2=a2,
            i_A3=a3,
            i_B1=b1,
            i_B2=b2,
            o_X=o,
            #i_VPWR=
            #i_VGND=
            #i_VPB=
            #i_VNB=
        )

        self.m.submodules += a32ogate
