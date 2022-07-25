from amaranth import Elaboratable, Instance


class SKY130HDProcess(Elaboratable):
    def _PoweredInstance(self, *args, **kwargs):
        if self._powered:
            kwargs.update({
                "i_VPWR": self.VPWR,
                "i_VPB": self.VPWR,
                "i_VGND": self.VGND,
                "i_VNB": self.VGND
            })
        return Instance(*args, **kwargs)

    def _generate_and(self, a, b, o):
        andgate = self._PoweredInstance(
            "sky130_fd_sc_hd__and2_1",
            i_A=a,
            i_B=b,
            o_X=o
        )

        self.m.submodules += andgate

    def _generate_xor(self, a, b, o):
        xorgate = self._PoweredInstance(
            "sky130_fd_sc_hd__xor2_1",
            i_A=a,
            i_B=b,
            o_X=o
        )

        self.m.submodules += xorgate

    def _generate_inv(self, a, o):
        invgate = self._PoweredInstance(
            "sky130_fd_sc_hd__inv_1",
            i_A=a,
            o_Y=o
        )

        self.m.submodules += invgate

    def _generate_full_adder(self, a, b, carry_in, sum_out, carry_out, name=None):
        fa = self._PoweredInstance(
            "sky130_fd_sc_hd__fa_1",
            o_COUT=carry_out,
            o_SUM=sum_out,
            i_A=a,
            i_B=b,
            i_CIN=carry_in
        )
        if name:
            self.m.submodules[name] = fa
        else:
            self.m.submodules += fa

    def _generate_half_adder(self, a, b, sum_out, carry_out, name=None):
        ha = self._PoweredInstance(
            "sky130_fd_sc_hd__ha_1",
            o_COUT=carry_out,
            o_SUM=sum_out,
            i_A=a,
            i_B=b
        )

        if name:
            self.m.submodules[name] = ha
        else:
            self.m.submodules += ha

    # Used in adder
    def _generate_ao21(self, a1, a2, b1, o):
        # 2-input AND into first input of 2-input OR
        a21o = self._PoweredInstance(
            "sky130_fd_sc_hd__a21o_1",
            o_X=o,
            i_A1=a1,
            i_A2=a2,
            i_B1=b1
        )

        self.m.submodules += a21o

    # Used in multiplier
    def _generate_ao22(self, a1, a2, b1, b2, o):
        # 2-input AND into both inputs of 2-input OR
        a22ogate = self._PoweredInstance(
            "sky130_fd_sc_hd__a22o_1",
            i_A1=a1,
            i_A2=a2,
            i_B1=b1,
            i_B2=b2,
            o_X=o
        )

        self.m.submodules += a22ogate

    # Used in multiplier
    def _generate_ao32(self, a1, a2, a3, b1, b2, o):
        # 3-input AND into first input, and 2-input AND into 2nd input of 2-input OR
        a32ogate = self._PoweredInstance(
            "sky130_fd_sc_hd__a32o_1",
            i_A1=a1,
            i_A2=a2,
            i_A3=a3,
            i_B1=b1,
            i_B2=b2,
            o_X=o
        )

        self.m.submodules += a32ogate
