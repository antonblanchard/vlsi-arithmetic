from amaranth import Elaboratable, Cat


class NoneProcess(Elaboratable):
    def _generate_and(self, a, b, o):
        self.m.d.comb += o.eq(a & b)

    def _generate_xor(self, a, b, o):
        self.m.d.comb += o.eq(a ^ b)

    def _generate_inv(self, a, o):
        self.m.d.comb += o.eq(~a)

    def _generate_full_adder(self, a, b, carry_in, sum_out, carry_out, name=None):
        self.m.d.comb += Cat(sum_out, carry_out).eq(a + b + carry_in)

    def _generate_half_adder(self, a, b, sum_out, carry_out, name=None):
        self.m.d.comb += Cat(sum_out, carry_out).eq(a + b)

    # Used in adder
    def _generate_ao21(self, a1, a2, b1, o):
        # 2-input AND into first input of 2-input OR
        self.m.d.comb += o.eq((a1 & a2) | b1)

    # Used in multiplier
    def _generate_ao22(self, a1, a2, b1, b2, o):
        # 2-input AND into both inputs of 2-input OR
        self.m.d.comb += o.eq((a1 & a2) | (b1 & b2))

    # Used in multiplier
    def _generate_ao32(self, a1, a2, a3, b1, b2, o):
        # 3-input AND into first input, and 2-input AND into 2nd input of 2-input OR
        self.m.d.comb += o.eq((a1 & a2 & a3) | (b1 & b2))
