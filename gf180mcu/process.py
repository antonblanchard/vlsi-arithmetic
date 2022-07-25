from amaranth import Elaboratable, Instance, Signal


class GF180MCUProcess(Elaboratable):
    def _PoweredInstance(self, *args, **kwargs):
        if self._powered:
            kwargs.update({
                "i_VDD": self.VPWR,
                "i_VSS": self.VGND,
            })
        return Instance(*args, **kwargs)

    def _generate_and(self, a, b, o):
        andgate = self._PoweredInstance(
            "gf180mcu_fd_sc_mcu7t5v0__and2_1",
            i_A1=a,
            i_A2=b,
            o_Z=o
        )

        self.m.submodules += andgate

    def _generate_xor(self, a, b, o):
        xorgate = self._PoweredInstance(
            "gf180mcu_fd_sc_mcu7t5v0__xor2_1",
            i_A1=a,
            i_A2=b,
            o_Z=o
        )

        self.m.submodules += xorgate

    def _generate_inv(self, a, o):
        invgate = self._PoweredInstance(
            "gf180mcu_fd_sc_mcu7t5v0__inv_1",
            i_I=a,
            o_ZN=o
        )

        self.m.submodules += invgate

    def _generate_full_adder(self, a, b, carry_in, sum_out, carry_out, name=None):
        fa = self._PoweredInstance(
            "gf180mcu_fd_sc_mcu7t5v0__addf_1",
            o_CO=carry_out,
            o_S=sum_out,
            i_A=a,
            i_B=b,
            i_CI=carry_in
        )
        if name:
            self.m.submodules[name] = fa
        else:
            self.m.submodules += fa

    def _generate_half_adder(self, a, b, sum_out, carry_out, name=None):
        ha = self._PoweredInstance(
            "gf180mcu_fd_sc_mcu7t5v0__addh_1",
            o_CO=carry_out,
            o_S=sum_out,
            i_A=a,
            i_B=b
        )

        if name:
            self.m.submodules[name] = ha
        else:
            self.m.submodules += ha

    # Used in adder
    def _generate_ao21(self, a1, a2, b1, o):
        zn = Signal()

        # 2-input AND into first input of 2-input OR
        ao21gate = self._PoweredInstance(
            "gf180mcu_fd_sc_mcu7t5v0__aoi21_1",
            i_A1=a1,
            i_A2=a2,
            i_B=b1,
            o_ZN=zn
        )
        self.m.submodules += ao21gate

        inv1 = self._PoweredInstance(
            "gf180mcu_fd_sc_mcu7t5v0__inv_1",
            i_I=zn,
            o_ZN=o
        )
        self.m.submodules += inv1

    # Used in multiplier
    def _generate_ao22(self, a1, a2, b1, b2, o):
        zn = Signal()

        # 2-input AND into both inputs of 2-input OR
        ao22gate = self._PoweredInstance(
            "gf180mcu_fd_sc_mcu7t5v0__aoi22_1",
            i_A1=a1,
            i_A2=a2,
            i_B1=b1,
            i_B2=b2,
            o_ZN=zn
        )
        self.m.submodules += ao22gate

        inv1 = self._PoweredInstance(
            "gf180mcu_fd_sc_mcu7t5v0__inv_1",
            i_I=zn,
            o_ZN=o
        )
        self.m.submodules += inv1

    # Used in multiplier
    def _generate_oai33(self, a1, a2, a3, b1, b2, b3, o):
        # 2 3-input OR into 2-input NAND
        oai33gate = self._PoweredInstance(
            "gf180mcu_fd_sc_mcu7t5v0__oai33_1",
            i_A1=a1,
            i_A2=a2,
            i_A3=a3,
            i_B1=b1,
            i_B2=b2,
            i_B3=b3,
            o_ZN=o
        )

        self.m.submodules += oai33gate
