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

    def _generate_booth_encoder(self, block, sign, sel):
        # sign is just the top bit
        self.m.d.comb += sign.eq(block[2])

        notblock = Signal(3)
        for i in range(3):
            self._generate_inv(block[i], notblock[i])

        sel_0 = Signal()
        sel_1 = Signal()

        # sel[0]:
        # 011 | 100
        # (~block[2] & block[1] & block[0]) | (block[2] & ~block[1] & ~block[0])
        t = Signal()
        self._generate_and(block[2], notblock[1], t)
        self._generate_and32_or2(notblock[2], block[1], block[0], t, notblock[0], sel_0)

        # sel[1]:
        # ?01 | ?10
        # (~block[1] & block[0]) | (block[1] & ~block[0])
        self._generate_and2_or2(notblock[1], block[0], block[1], notblock[0], sel_1)

        self.m.d.comb += sel.eq(Cat(sel_0, sel_1))

    def _generate_booth_mux(self, multiplicand, sel, sign, o):
        # ((multiplicand[0] & sel[0]) | (multiplicand[1] & sel[1])) ^ sign
        t = Signal()
        self._generate_and2_or2(multiplicand[0], sel[0], multiplicand[1], sel[1], t)
        self._generate_xor(t, sign, o)


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

    def _generate_booth_encoder(self, block, sign, sel):
        # This is the standard booth encoder. We output a sign bit
        # and a 2 bit multiplicand selector:

        # block sign sel  how this relates to multiplicand
        # 000   0   00    +0
        # 001   0   10   *+1
        # 010   0   10   *+1
        # 011   0   01   *+2
        # 100   1   01   *-2
        # 101   1   10   *-1
        # 110   1   10   *-1
        # 111   1   00    -0

        # sign is just the top bit
        self.m.d.comb += sign.eq(block[2])

        sel_0 = Signal()
        sel_1 = Signal()

        # sel[0]:
        # 011 | 100
        self.m.d.comb += sel_0.eq((~block[2] & block[1] & block[0]) | (block[2] & ~block[1] & ~block[0]))

        # sel[1]:
        # ?01 | ?10
        self.m.d.comb += sel_1.eq((~block[1] & block[0]) | (block[1] & ~block[0]))

        self.m.d.comb += sel.eq(Cat(sel_0, sel_1))

    def _generate_booth_mux(self, multiplicand, sel, sign, o):
        self.m.d.comb += o.eq(((multiplicand[0] & sel[0]) | (multiplicand[1] & sel[1])) ^ sign)

    def elaborate(self, platform):
        self.m = Module()

        self._gen_partial_products()
        self._acc_partial_products()
        self._final_adder()

        return self.m

class BoothRadix4(Multiplier):
    def _gen_partial_products(self):
        # Double check this
        self._partial_products = [[] for i in range((self._bits)*2+1)]

        multiplier = Signal(self._bits+3)
        multiplicand = Signal(self._bits+2)

        # Add a zero in the LSB of the multiplier and multiplicand
        self.m.d.comb += [
            multiplier.eq(Cat(Const(0), self.a, Const(0), Const(0))),
            multiplicand.eq(Cat(Const(0), self.b)),
        ]

        last_b = self._bits
        second_last_b = self._bits-2
        last_m = self._bits

        # Step through the multiplier 2 bits at a time
        for off_b in range(0, self._bits+1, 2):
            # ...selecting a block of three bits at a tie
            block = Signal(3, name="booth_block%d" % off_b)
            self.m.d.comb += block.eq(multiplier[off_b:off_b+3])

            sign = Signal(name="booth_block%d_sign" % off_b)
            sel = Signal(2, name="booth_block%d_sel" % off_b)
            self._generate_booth_encoder(block, sign, sel)

            # Step through the multiplicand 1 bit at a time
            for off_m in range(self._bits+1):
                # ...selecting 2 bits at a time
                mand = Signal(2, name="booth_block%d_mand%d" % (off_b, off_m))
                self.m.d.comb += mand.eq(multiplicand[off_m:off_m+2])

                o = Signal(name="booth_b%d_m%d" % (off_b, off_m))
                self._partial_products[off_b + off_m].append(o)

                self._generate_booth_mux(mand, sel, sign, o)

                if off_m == last_m:
                    notsign = Signal()
                    self.m.d.comb += notsign.eq(~sign)

                    if off_b == 0:
                        # Add (notsign, sign, sign) to top bits
                        self._partial_products[off_b + off_m + 1].append(sign)
                        self._partial_products[off_b + off_m + 2].append(sign)
                        self._partial_products[off_b + off_m + 3].append(notsign)
                    elif off_b == second_last_b:
                        self._partial_products[off_b + off_m + 1].append(notsign)
                    elif off_b != last_b:
                        # Add (1, notsign) to top bits
                        self._partial_products[off_b + off_m + 1].append(notsign)
                        self._partial_products[off_b + off_m + 2].append(Const(1))

                    # Why is sign for second block not 0?
                    if off_b != last_b:
                        # Add sign to lowest bit in block
                        self._partial_products[off_b].append(sign)

            # First row, add ASS
            # Other rows except final row, add 1A
            # All but final row, add the sign bit to lowest bit


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

class BoothRadix4Dadda(BoothRadix4, Dadda, Adder):
    pass

class SKY130BoothRadix4Dadda(SKY130, BoothRadix4, Dadda, Adder):
    pass

if __name__ == "__main__":
    top = SKY130BoothRadix4Dadda(bits=16)
    with open("test.v", "w") as f:
        f.write(verilog.convert(top, ports = [top.a, top.b, top.o], strip_internal_attrs=True))


class TestCase(unittest.TestCase):
    def setUp(self):
        self.bits=16
        self.dut = BoothRadix4Dadda(self.bits)

    def do_one_comb(self, a, b):
        yield self.dut.a.eq(a)
        yield self.dut.b.eq(b)
        yield Settle()
        res = (yield self.dut.o)
        self.assertEqual(res, a * b)

    def test_exhaustive(self):
        def bench():
            for a in range(int(math.pow(self.bits, 2))):
                for b in range(int(math.pow(self.bits, 2))):
                    yield from self.do_one_comb(a, b)

        sim = Simulator(self.dut)
        sim.add_process(bench)
        with sim.write_vcd("test.vcd"):
            sim.run()

    def test_random(self):
        def bench():
            for i in range(1000):
                rand_a = random.getrandbits(self.bits)
                rand_b = random.getrandbits(self.bits)
                yield from self.do_one_comb(rand_a, rand_b)

        sim = Simulator(self.dut)
        sim.add_process(bench)
        with sim.write_vcd("test.vcd"):
            sim.run()

if __name__ == '__main__':
    unittest.main()
