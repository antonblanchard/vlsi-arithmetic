# Unsigned multiplier using Booth radix 4 encoding and Dadda reduction

import math
import unittest
import random

from nmigen import Elaboratable, Module, Signal, Cat, Const, Instance
from nmigen.back import verilog
from nmigen.sim import Simulator, Settle


class FullAdder(Elaboratable):
    def __init__(self):
        self.a = Signal()
        self.b = Signal()
        self.carry_in = Signal()

        self.sum = Signal()
        self.carry_out = Signal()

    def elaborate(self, platform):
        m = Module()

        t = Signal(2)
        m.d.comb += [
            t.eq(self.a + self.b + self.carry_in),
            self.sum.eq(t[0]),
            self.carry_out.eq(t[1]),
        ]

        return m


class HalfAdder(Elaboratable):
    def __init__(self):
        self.a = Signal()
        self.b = Signal()

        self.sum = Signal()
        self.carry_out = Signal()

    def elaborate(self, platform):
        m = Module()

        t = Signal(2)
        m.d.comb += [
            t.eq(self.a + self.b),
            self.sum.eq(t[0]),
            self.carry_out.eq(t[1]),
        ]

        return m


class BoothRadix4(Elaboratable):
    def __init__(self):
        self.block = Signal(3)
        self.multiplicand = Signal(2)

        self.o = Signal()

    def elaborate(self, platform):
        m = Module()

        with m.Switch(self.block):
            with m.Case(0b000):
                m.d.comb += self.o.eq(0)
            with m.Case(0b001):
                m.d.comb += self.o.eq(self.multiplicand[1])
            with m.Case(0b010):
                m.d.comb += self.o.eq(self.multiplicand[1])
            with m.Case(0b011):
                m.d.comb += self.o.eq(self.multiplicand[0])
            with m.Case(0b100):
                m.d.comb += self.o.eq(~self.multiplicand[0])
            with m.Case(0b101):
                m.d.comb += self.o.eq(~self.multiplicand[1])
            with m.Case(0b110):
                m.d.comb += self.o.eq(~self.multiplicand[1])
            with m.Case(0b111):
                m.d.comb += self.o.eq(0)

        return m

class SchoolBook(Elaboratable):
    def __init__(self, bits=64):
        self.bits = bits

    def generate_partial_products(self):
        self.partial_products = [[] for i in range(len(multiplier)+len(multiplicand))]
        self.partial_products

class Dadda(Elaboratable):
    def reduce_partial_products(self):

class BoothDadda(Elaboratable):
    def __init__(self, bits=64):
        self.bits = bits

        self.a = Signal(bits)
        self.b = Signal(bits)

        self.o = Signal(bits*2)

    # Dadda heights are d(0) = 2, d(n+1) = floor(1.5*d(n))
    def _calc_dadda_heights(self, bits):
        d=2
        out=list()

        while d < bits:
            out.append(d)
            d = math.floor(1.5*d)

        out.reverse()

        return out

    def elaborate(self, platform):
        m = Module()

#        multiplier = Signal(self.bits+2)
#        multiplicand = Signal(self.bits+2)

#        # Add a zero in the LSB for both multiplicand and multiplier
#        m.d.comb += [
#            multiplier.eq(Cat(0, self.a)),
#            multiplicand.eq(Cat(0, self.b)),
#        ]
        multiplier = self.a
        multiplicand = self.b

        # Create a list of lists to store our partial products
        partial_products = [[] for i in range(len(multiplier)+len(multiplicand))]

#        # Step through the multiplier 2 bits at a time
#        for off_b in range(0, len(multiplier), 2):
#            # Select three bits of the multiplier at a time
#            block = multiplier[off_b:off_b+3]
#
#            # Step through the multiplicand 1 bit at a time
#            for off_m in range(len(multiplicand)):
#                #mand = multiplicand[off_m:off_m+2]
#
#                o = Signal()
#                partial_products[off_b + off_m].append(o)
#
#                booth = BoothRadix4()
#                name = "booth_b%d_m%d" % (off_b, off_m)
#                m.submodules[name] = booth
#
#                m.d.comb += [
#                    booth.block.eq(block),
#                    booth.multiplicand.eq(multiplicand[off_m:off_m+2]),
#                    o.eq(booth.o),
#                 ]

        for off_b in range(len(multiplier)):
            for off_m in range(len(multiplicand)):
                o = Signal()
                partial_products[off_b + off_m].append(o)
                m.d.comb += o.eq(multiplier[off_b] & multiplicand[off_m])


        # Dadda reduction
        #dadda_heights = self._calc_dadda_heights(min(len(multiplier), len(multiplicand) // 2))
        dadda_heights = self._calc_dadda_heights(min(len(multiplier), len(multiplicand)))

        iteration = 0

        # Loop until we have a depth of 2
        while max(len(x) for x in partial_products) > 2:
            for offset in range(len(partial_products)):
                subiteration = 0
                while len(partial_products[offset]) > dadda_heights[0]:
                    s = Signal()
                    c = Signal()

                    # Full adder of three bits if there are 2 or more extra elements
                    if len(partial_products[offset]) > (1 + dadda_heights[0]):
                        #fa = FullAdder()
                        #name = "dadda_fa_%d_%d_%d" % (iteration, offset, subiteration)
                        #m.submodules[name] = fa

                        i0 = partial_products[offset].pop(0)
                        i1 = partial_products[offset].pop(0)
                        i2 = partial_products[offset].pop(0)

                        #m.d.comb += [
                            #fa.a.eq(i0),
                            #fa.b.eq(i1),
                            #fa.carry_in.eq(i2),

                            #s.eq(fa.sum),
                            #c.eq(fa.carry_out),
                        #]

                        fa = Instance(
                            "FA",
                            i_a=i0,
                            i_b=i1,
                            i_carry_in=c,
                            o_sum=s,
                            o_carry_out=c,
                        )

                        m.submodules += fa

                    # Half adder of two bits if there is 1 extra element
                    else:
                        #ha = HalfAdder()
                        #name = "dadda_ha_%d_%d_%d" % (iteration, offset, subiteration)
                        #m.submodules[name] = ha

                        i0 = partial_products[offset].pop(0)
                        i1 = partial_products[offset].pop(0)

                        #m.d.comb += [
                            #ha.a.eq(i0),
                            #ha.b.eq(i1),

                            #s.eq(ha.sum),
                            #c.eq(ha.carry_out),
                        #]

                        ha = Instance(
                            "HA",
                            i_a=i0,
                            i_b=i1,
                            o_sum=s,
                            o_carry_out=c,
                        )

                    # result goes in bottom of column and carry goes in the top of the next column
                    partial_products[offset].append(s)
                    partial_products[offset+1].insert(0, c)

                    subiteration = subiteration + 1

            dadda_heights.pop(0)
            iteration = iteration + 1

        for offset in range(len(partial_products)):
            while len(partial_products[offset]) < 2:
                partial_products[offset].append(Const(0))

        r1 = Cat(partial_products[n][0] for n in range(len(partial_products)))
        r2 = Cat(partial_products[n][1] for n in range(len(partial_products)))

        m.d.comb += self.o.eq(r1+r2)

        print("done")

        return m


def doit():
    top = BoothDadda(bits=20)
    with open("booth.v", "w") as f:
        f.write(verilog.convert(top, ports = [top.a, top.b, top.o], strip_internal_attrs=True))

import cProfile
import re
cProfile.run('doit()')
exit(1)

if __name__ == "__main__":
    top = BoothDadda(bits=32)
    with open("booth.v", "w") as f:
        f.write(verilog.convert(top, ports = [top.a, top.b, top.o], strip_internal_attrs=True))



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
        self.dut = BoothDadda(16)

    def do_one_comb(self, a, b):
        yield self.dut.a.eq(a)
        yield self.dut.b.eq(b)
        yield Settle()
        res = (yield self.dut.o)
        self.assertEqual(res, a * b)

#    def test_cases(self):
#        def bench():
#            for (a, b) in [(x, y) for x in cases for y in cases]:
#                print("a %x b %x" % (a, b))
#                rand_a = random.getrandbits(64)
#                rand_b = random.getrandbits(64)
#                yield from self.do_one_comb(rand_a, rand_b)
#
#        sim = Simulator(self.dut)
#        sim.add_process(bench)
#        with sim.write_vcd("test.vcd"):
#            sim.run()

    def test_random(self):
        def bench():
            for i in range(1000):
                #rand_a = 3
                #rand_b = 2
                rand_a = random.getrandbits(16)
                rand_b = random.getrandbits(16)
                yield from self.do_one_comb(rand_a, rand_b)

        sim = Simulator(self.dut)
        sim.add_process(bench)
        with sim.write_vcd("test.vcd"):
            sim.run()

if __name__ == '__main__':
    unittest.main()
