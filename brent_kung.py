import unittest
import random
import math

from nmigen import Elaboratable, Module, Signal, Cat
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

        p_tmp = Signal(self._bits)
        g_tmp = Signal(self._bits)

        # Convert to per bit array
        self._generate_half_adder(a, b, p_tmp, g_tmp)

        # Use arrays of 1 bit signals to make it easy to create a
        # trees of p and g updates.
        p = [p_tmp[i] for i in range(self._bits)]
        g = [g_tmp[i] for i in range(self._bits)]

        for i in range(1, int(math.log(self._bits, 2))+1):
            for j in range(2**i-1, self._bits, 2**i):
                pair = j - 2**(i-1)
                p_new = Signal()
                g_new = Signal()
                self._generate_and(p[j], p[pair], p_new)
                self._generate_and21_or2(p[j], g[pair], g[j], g_new)
                p[j] = p_new
                g[j] = g_new

        for i in range(int(math.log(self._bits, 2)), 0, -1):
            for j in range(2**i + 2**(i-1) - 1, self._bits, 2**i):
                pair = j - 2**(i-1)
                p_new = Signal()
                g_new = Signal()
                self._generate_and(p[j], p[pair], p_new)
                self._generate_and21_or2(p[j], g[pair], g[j], g_new)
                p[j] = p_new
                g[j] = g_new

        g_flat = Signal(self._bits)
        m.d.comb += g_flat.eq(Cat(g[n] for n in range(self._bits)))

        o = Signal(self._bits)
        self._generate_xor(p_tmp, g_flat << 1, o)

        if self._register_output:
            m.d.sync += self.o.eq(o)
        else:
            m.d.comb += self.o.eq(o)

        return m

if __name__ == "__main__":
    top = BrentKung(bits=64, register_input=True, register_output=True)
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
