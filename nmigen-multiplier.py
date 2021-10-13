from nmigen import Elaboratable, Module, Signal
from nmigen.back import verilog

from nmigen.sim import Simulator, Settle

import unittest
import random

class Multiplier(Elaboratable):
    def __init__(self, bits=64, min_bits=16, register=False):
        self.bits = bits
        self.min_bits = min_bits
        self.register = register

        #assert...

        self.a = Signal(bits)
        self.b = Signal(bits)
        self.o = Signal(2*bits)

    def elaborate(self, platform):
        m = Module()

        halfbits = self.bits//2

        partial_a_0 = Signal(halfbits)
        partial_a_1 = Signal(halfbits)
        partial_b_0 = Signal(halfbits)
        partial_b_1 = Signal(halfbits)

        m.d.comb += [
            partial_a_0.eq(self.a.word_select(0, halfbits)),
            partial_a_1.eq(self.a.word_select(1, halfbits)),
            partial_b_0.eq(self.b.word_select(0, halfbits)),
            partial_b_1.eq(self.b.word_select(1, halfbits)),
        ]

        res_low = Signal(self.bits)
        res_mid_0 = Signal(self.bits)
        res_mid_1 = Signal(self.bits)
        res_hi = Signal(self.bits)

        tmp_o = Signal(self.bits*2)

        if self.bits > self.min_bits:
            m.submodules.mul_low = mul_low = Multiplier(halfbits, min_bits=self.min_bits, register=self.register)
            m.submodules.mid_0 = mid_0 = Multiplier(halfbits, min_bits=self.min_bits, register=self.register)
            m.submodules.mid_1 = mid_1 = Multiplier(halfbits, min_bits=self.min_bits, register=self.register)
            m.submodules.hi = hi = Multiplier(halfbits, min_bits=self.min_bits, register=self.register)
            m.d.comb += [
                mul_low.a.eq(partial_a_0),
                mul_low.b.eq(partial_b_0),

                mid_0.a.eq(partial_a_1),
                mid_0.b.eq(partial_b_0),

                mid_1.a.eq(partial_a_0),
                mid_1.b.eq(partial_b_1),

                hi.a.eq(partial_a_1),
                hi.b.eq(partial_b_1),

                tmp_o.eq(mul_low.o +
                          mid_0.o.shift_left(halfbits) +
                          mid_1.o.shift_left(halfbits) +
                          hi.o.shift_left(self.bits))
            ]
        else:
            m.d.comb += [
                res_low.eq(partial_a_0 * partial_b_0),
                res_mid_0.eq(partial_a_1 * partial_b_0),
                res_mid_1.eq(partial_a_0 * partial_b_1),
                res_hi.eq(partial_a_1 * partial_b_1),

                tmp_o.eq(res_low +
                          res_mid_0.shift_left(halfbits) +
                          res_mid_1.shift_left(halfbits) +
                          res_hi.shift_left(self.bits))
            ]

        if self.register:
            tmp2_o = Signal(self.bits*2, reset_less=True)
            m.d.sync += tmp2_o.eq(tmp_o)
            m.d.comb += self.o.eq(tmp2_o)
        else:
            m.d.comb += self.o.eq(tmp_o)

        return m


if __name__ == "__main__":
    top = Multiplier(bits=64, min_bits=8, register=False)
    with open("multiplier.v", "w") as f:
        f.write(verilog.convert(top, ports = [top.a, top.b, top.o], strip_internal_attrs=True))

    top = Multiplier(bits=64, min_bits=8, register=True)
    with open("multiplier_pipelined.v", "w") as f:
        f.write(verilog.convert(top, ports = [top.a, top.b, top.o], strip_internal_attrs=True))
    print("done")


cases = [
        0x0000000000000000,
        0x0000000000000001,
        0x0000000011111111,
        0x000000007fffffff,
        0x0000000080000000,
        0x00000000ffffffff,
        0x0000000100000000,
        0x0001020304050607,
        0x1111111111111111,
        0x7fffffffffffffff,
        0x8000000000000000,
        0x8888888888888888,
        0xffffffff00000000,
        0xffffffffffffffff,
        0X00ff00ff00ff00ff,
        0Xff00ff00ff00ff00,
        0xa5a5a5a5a5a5a5a5,
]

class TestCase(unittest.TestCase):
    def setUp(self):
        self.dut = Multiplier(64, min_bits=16, register=False)

    def do_one_comb(self, a, b):
        yield self.dut.a.eq(a)
        yield self.dut.b.eq(b)
        yield Settle()
        res = (yield self.dut.o)
        self.assertEqual(res, a * b)

    def test_cases(self):
        def bench():
            for (a, b) in [(x, y) for x in cases for y in cases]:
                print("a %x b %x" % (a, b))
                rand_a = random.getrandbits(64)
                rand_b = random.getrandbits(64)
                yield from self.do_one_comb(rand_a, rand_b)

        sim = Simulator(self.dut)
        sim.add_process(bench)
        with sim.write_vcd("test.vcd"):
            sim.run()

    def test_random(self):
        def bench():
            for i in range(1000):
                rand_a = random.getrandbits(64)
                rand_b = random.getrandbits(64)
                yield from self.do_one_comb(rand_a, rand_b)

        sim = Simulator(self.dut)
        sim.add_process(bench)
        with sim.write_vcd("test.vcd"):
            sim.run()


class PipelinedTestCase(unittest.TestCase):
    def setUp(self):
        self.dut = Multiplier(64, min_bits=16, register=True)

    def do_one_sync(self, cycles=4):
        rand_a = random.getrandbits(64)
        rand_b = random.getrandbits(64)
        yield self.dut.a.eq(rand_a)
        yield self.dut.b.eq(rand_b)

        for i in range(cycles):
            yield
            yield self.dut.a.eq(0)
            yield self.dut.b.eq(0)

        res = (yield self.dut.o)
        self.assertEqual(res, rand_a * rand_b)

    def test(self):
        def bench():
            for i in range(1000):
                yield from self.do_one_sync()

        sim = Simulator(self.dut)
        sim.add_clock(1e-9)
        sim.add_sync_process(bench)
        with sim.write_vcd("test.vcd"):
            sim.run()


if __name__ == '__main__':
    unittest.main()
