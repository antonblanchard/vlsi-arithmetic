import unittest
import random
import math

from nmigen import Elaboratable, Module, Signal, Cat, Instance, Const
from nmigen.back import verilog
from nmigen.sim import Simulator, Settle


class Simple(Elaboratable):
    def __init__(self, bits=64):
        self.a = Signal(bits)
        self.b = Signal(bits)
        self.o = Signal(bits)

        self._bits = bits

    def elaborate(self, platform):
        m = Module()

        m.d.comb += self.o.eq(self.a+self.b)

        return m


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

    def _generate_and21_or2(self, a1, a2, b1, o):
        a21o = Instance(
            "sky130_fd_sc_a21o_1",
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


class BrentKung(Elaboratable):
    def __init__(self, bits=64, register_input=False, register_output=False):
        self.a = Signal(bits)
        self.b = Signal(bits)
        self.o = Signal(bits)

        self._bits = bits
        self._register_input = register_input
        self._register_output = register_output

    def _generate_and(self, a, b, o):
        self.m.d.comb += o.eq(a & b)

    def _generate_xor(self, a, b, o):
        self.m.d.comb += o.eq(a ^ b)

    def _generate_half_adder(self, a, b, s, co):
        self.m.d.comb += [
            s.eq(a ^ b),
            co.eq(a & b),
        ]

    def _generate_and21_or2(self, a, b, c, o):
        self.m.d.comb += o.eq((a & b) | c)

    def elaborate(self, platform):
        self.m = m = Module()

        a = Signal(self._bits)
        b = Signal(self._bits)
        if self._register_input:
            m.d.sync += [
                a.eq(self.a),
                b.eq(self.b),
            ]
        else:
            m.d.comb += [
                a.eq(self.a),
                b.eq(self.b),
            ]

        # Use arrays of 1 bit signals to make it easy to create
        # trees of p and g updates.
        p = [Signal() for i in range(self._bits)]
        g = [Signal() for i in range(self._bits)]

        for i in range(self._bits):
            self._generate_half_adder(a[i], b[i], p[i], g[i])

        # We need a copy of p
        p_tmp = [Signal() for i in range(self._bits)]
        for i in range(self._bits):
            m.d.comb += p_tmp[i].eq(p[i])

        # Calculate the p and g for the odd bits
        for i in range(1, int(math.log(self._bits, 2))+1):
            for j in range(2**i-1, self._bits, 2**i):
                pair = j - 2**(i-1)
                p_new = Signal()
                g_new = Signal()
                self._generate_and(p[j], p[pair], p_new)
                self._generate_and21_or2(p[j], g[pair], g[j], g_new)
                p[j] = p_new
                g[j] = g_new

        # Calculate p and go for the even bits
        for i in range(int(math.log(self._bits, 2)), 0, -1):
            for j in range(2**i + 2**(i-1) - 1, self._bits, 2**i):
                pair = j - 2**(i-1)
                p_new = Signal()
                g_new = Signal()
                self._generate_and(p[j], p[pair], p_new)
                self._generate_and21_or2(p[j], g[pair], g[j], g_new)
                p[j] = p_new
                g[j] = g_new

        # g is the carry out signal. We need to shift it left one bit then
        # xor it with the sum (ie p_tmp). Since we have a list of 1 bits, just
        # insert zero at the head of of the list
        g.insert(0, Const(0))

        o = Signal(self._bits)
        for i in range(self._bits):
            # This also flattens the list of bits when writing to o
            self._generate_xor(p_tmp[i], g[i], o[i])

        if self._register_output:
            m.d.sync += self.o.eq(o)
        else:
            m.d.comb += self.o.eq(o)

        return m

class SKY130BrentKung(SKY130, BrentKung):
    pass

if __name__ == "__main__":
    top = SKY130BrentKung(bits=64, register_input=True, register_output=True)
    with open("brent_kung.v", "w") as f:
        f.write(verilog.convert(top, ports = [top.a, top.b, top.o], strip_internal_attrs=True))

class TestCase(unittest.TestCase):
    def setUp(self):
        self.bits = 8
        self.dut = BrentKung(self.bits)

    def do_one_comb(self, a, b):
        yield self.dut.a.eq(a)
        yield self.dut.b.eq(b)
        yield Settle()
        res = (yield self.dut.o)
        expected = (a + b) & (pow(2, self.bits)-1)
        self.assertEqual(res, expected)

    def test_random(self):
        def bench():
            for i in range(10000):
                rand_a = random.getrandbits(self.bits)
                rand_b = random.getrandbits(self.bits)
                yield from self.do_one_comb(rand_a, rand_b)

        sim = Simulator(self.dut)
        sim.add_process(bench)
        with sim.write_vcd("brent_kung.vcd"):
            sim.run()

if __name__ == '__main__':
    unittest.main()
