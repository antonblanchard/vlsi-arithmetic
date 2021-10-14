# Unsigned multiplier using Booth radix 4 encoding and Dadda reduction

import math
import unittest
import random

from nmigen import Elaboratable, Module, Signal, Cat, Const
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

        multiplier = Signal(self.bits+1)
        multiplicand = Signal(self.bits+1)

        # Add a zero in the LSB for both multiplicand and multiplier
        m.d.comb += [
            multiplier.eq(Cat(0, self.a)),
            multiplicand.eq(Cat(0, self.b)),
        ]

        # Create a list of lists to store our partial products
        partial_products = [[] for i in range(self.bits*2)]

        # Step through the multiplier 2 bits at a time
        for off_b in range(0, self.bits, 2):
            # Select three bits of the multiplier at a time
            block = multiplier[off_b:off_b+3]

            # Step through the multiplicand 1 bit at a time
            for off_m in range(self.bits+1):
                mand = multiplicand[off_m:off_m+2]

                o = Signal()
                partial_products[off_b + off_m].append(o)

                booth = BoothRadix4()
                m.submodules += booth

                m.d.comb += [
                    booth.block.eq(block),
                    booth.multiplicand.eq(mand),
                    o.eq(booth.o),
                 ]

        # Dadda reduction
        dadda_heights = self._calc_dadda_heights(self.bits//2)

        # Loop until we have a depth of 2
        while max(len(x) for x in partial_products) > 2:
            print(max(len(x) for x in partial_products))
            print(dadda_heights)

            #for offset in range(len(partial_products)):
                #print("%d" % len(partial_products[offset]), end='')
            #print()

            for offset in range(len(partial_products)):
                while len(partial_products[offset]) > dadda_heights[0]:
                    s = Signal()
                    c = Signal()

                    # Full adder of three bits if there are 2 or more extra elements
                    if len(partial_products[offset]) > (1 + dadda_heights[0]):
                        fa = FullAdder()
                        m.submodules += fa

                        i0 = partial_products[offset].pop(0)
                        i1 = partial_products[offset].pop(0)
                        i2 = partial_products[offset].pop(0)

                        m.d.comb += [
                            fa.a.eq(i0),
                            fa.b.eq(i1),
                            fa.carry_in.eq(i2),

                            fa.sum.eq(s),
                            fa.carry_out.eq(c),
                        ]

                    # Half adder of two bits if there is 1 extra element
                    else:
                        ha = HalfAdder()
                        m.submodules += ha

                        i0 = partial_products[offset].pop(0)
                        i1 = partial_products[offset].pop(0)

                        m.d.comb += [
                            ha.a.eq(i0),
                            ha.b.eq(i1),

                            ha.sum.eq(s),
                            ha.carry_out.eq(c),
                        ]

                    # result goes in bottom of column and carry goes in the top of the next column
                    partial_products[offset].append(s)
                    partial_products[offset+1].insert(0, c)

            dadda_heights.pop(0)

        for offset in range(len(partial_products)):
            # Why
            if len(partial_products[offset]) == 0:
                partial_products[offset].append(Const(0))
                partial_products[offset].append(Const(0))

            elif len(partial_products[offset]) == 1:
                partial_products[offset].append(Const(0))

        r1 = Cat(partial_products[n][0] for n in range(len(partial_products)))
        r2 = Cat(partial_products[n][1] for n in range(len(partial_products)))

        #print(partial_products)
        #print(r1)
        #print(r2)

        m.d.comb += self.o.eq(r1+r2)

        return m


if __name__ == "__main__":
    top = BoothDadda(bits=4)
    with open("booth.v", "w") as f:
        f.write(verilog.convert(top, ports = [top.a, top.b, top.o], strip_internal_attrs=True))
