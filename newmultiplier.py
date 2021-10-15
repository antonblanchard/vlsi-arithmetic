import math
import unittest
import random

from nmigen import Elaboratable, Module, Signal, Cat, Const, Instance
from nmigen.back import verilog
from nmigen.sim import Simulator, Settle


class SKY130(Elaboratable):
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

    def _generate_half_adder(self, a, b, sum_out, carry_out, name):
        fa = Instance(
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

        self.m.submodules[name] = fa

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

    def _generate_booth_encoder(self, block, multiplicand, o):
        pass


class Multiplier(Elaboratable):
    def __init__(self, bits=64):
        self.a = Signal(bits)
        self.b = Signal(bits)
        self.o = Signal(bits*2)

        self._bits = bits
        self._partial_products = [[] for i in range(bits*2)]
        self._final_a = Signal(bits*2)
        self._final_b = Signal(bits*2)

    def _gen_partial_products(self):
        pass

    def _acc_partial_products(self):
        pass

    def _final_adder(self):
        pass

    def _generate_full_adder(self, a, b, carry_in, sum_out, carry_out, name):
        self.m.d.comb += Cat(sum_out, carry_out).eq(a + b + carry_in) 

    def _generate_half_adder(self, a, b, sum_out, carry_out, name):
        self.m.d.comb += Cat(sum_out, carry_out).eq(a + b) 

    def _generate_and(self, a, b, o):
        self.m.d.comb += o.eq(a & b) 

    def _generate_booth_encoder(self, block, multiplicand, o):
        with self.m.Switch(block):
            with self.m.Case(0b000):
                self.m.d.comb += o.eq(0)
            with self.m.Case(0b001):
                self.m.d.comb += o.eq(multiplicand[1])
            with self.m.Case(0b010):
                self.m.d.comb += o.eq(multiplicand[1])
            with self.m.Case(0b011):
                self.m.d.comb += o.eq(multiplicand[0])
            with self.m.Case(0b100):
                self.m.d.comb += o.eq(~multiplicand[0])
            with self.m.Case(0b101):
                self.m.d.comb += o.eq(~multiplicand[1])
            with self.m.Case(0b110):
                self.m.d.comb += o.eq(~multiplicand[1])
            with self.m.Case(0b111):
                self.m.d.comb += o.eq(0)

    def elaborate(self, platform):
        self.m = Module()

        self._gen_partial_products()
        self._acc_partial_products()
        self._final_adder()

        return self.m


class SchoolBook(Multiplier):
    def _gen_partial_products(self):
        for off_a in range(self._bits):
            for off_b in range(self._bits):
                o = Signal()
                self._partial_products[off_a + off_b].append(o)
                self._generate_and(self.a[off_a], self.b[off_b], o)


class Adder(Multiplier):
    def _final_adder(self):
        self.m.d.comb += self.o.eq(self._final_a + self._final_b)


class Dadda(Multiplier):
    def _calc_dadda_heights(self, bits):
        d=2
        out=list()

        while d < bits:
            out.append(d)
            d = math.floor(1.5*d)

        out.reverse()

        return out

    def _acc_partial_products(self):
        height = max(len(x) for x in self._partial_products)
        dadda_heights = self._calc_dadda_heights(height)

        iteration = 0

        # Loop until we have a depth of 2
        while max(len(x) for x in self._partial_products) > 2:
            for offset in range(len(self._partial_products)):
                subiteration = 0
                while len(self._partial_products[offset]) > dadda_heights[0]:
                    s = Signal()
                    c = Signal()

                    # Full adder of three bits if there are 2 or more extra elements
                    if len(self._partial_products[offset]) > (1 + dadda_heights[0]):
                        i0 = self._partial_products[offset].pop(0)
                        i1 = self._partial_products[offset].pop(0)
                        i2 = self._partial_products[offset].pop(0)

                        name = "dadda_fa_%d_%d_%d" % (iteration, offset, subiteration)
                        self._generate_full_adder(i0, i1, i2, s, c, name)

                    # Half adder of two bits if there is 1 extra element
                    else:
                        i0 = self._partial_products[offset].pop(0)
                        i1 = self._partial_products[offset].pop(0)

                        name = "dadda_ha_%d_%d_%d" % (iteration, offset, subiteration)
                        self._generate_half_adder(i0, i1, s, c, name)

                    # result goes in bottom of column and carry goes in the top of the next column
                    self._partial_products[offset].append(s)
                    self._partial_products[offset+1].insert(0, c)

                    subiteration = subiteration + 1

            dadda_heights.pop(0)
            iteration = iteration + 1

        for offset in range(len(self._partial_products)):
            while len(self._partial_products[offset]) < 2:
                self._partial_products[offset].append(Const(0))

        self._final_a = Cat(self._partial_products[n][0] for n in range(len(self._partial_products)))
        self._final_b = Cat(self._partial_products[n][1] for n in range(len(self._partial_products)))


class SchoolBookDadda(SchoolBook, Dadda, Adder):
    pass

class SKY130SchoolBookDadda(SKY130, SchoolBook, Dadda, Adder):
    pass

if __name__ == "__main__":
    top = SKY130SchoolBookDadda(bits=16)
    with open("test.v", "w") as f:
        f.write(verilog.convert(top, ports = [top.a, top.b, top.o], strip_internal_attrs=True))


class TestCase(unittest.TestCase):
    def setUp(self):
        self.bits=16
        self.dut = SchoolBookDadda(self.bits)

    def do_one_comb(self, a, b):
        yield self.dut.a.eq(a)
        yield self.dut.b.eq(b)
        yield Settle()
        res = (yield self.dut.o)
        self.assertEqual(res, a * b)

    def test_random(self):
        def bench():
            for i in range(10000):
                rand_a = random.getrandbits(self.bits)
                rand_b = random.getrandbits(self.bits)
                yield from self.do_one_comb(rand_a, rand_b)

        sim = Simulator(self.dut)
        sim.add_process(bench)
        with sim.write_vcd("test.vcd"):
            sim.run()

if __name__ == '__main__':
    unittest.main()
