import sys
import math
import argparse

from amaranth import Elaboratable, Module, Signal, Cat, Const
from amaranth.back import verilog

from process_sky130 import ProcessSKY130
from process_none import ProcessNone

from adder import BrentKungNone, BrentKungSKY130


class Multiplier(Elaboratable):
    def __init__(self, bits=64, multiply_add=False, register_input=False,
                 register_middle=False, register_output=False, powered=False):
        self.a = Signal(bits)
        self.b = Signal(bits)
        if multiply_add:
            self.c = Signal(bits * 2)
        self.o = Signal(bits * 2)

        if powered:
            self._powered = True
            self.VPWR = Signal()
            self.VGND = Signal()
        else:
            self._powered = False

        self._bits = bits
        self._multiply_add = multiply_add
        self._register_input = register_input
        self._register_middle = register_middle
        self._register_output = register_output

        # partial product generation writes to this
        self._partial_products = [[] for i in range(bits * 2)]

        # partial product accumulation writes to these
        self._final_a = Signal(bits * 2)
        self._final_b = Signal(bits * 2)

        # Final addition writes to this
        self.result = Signal(bits * 2)

        # We optionally register inputs, outputs and in between
        # partial product accumulation and the final addition.
        self.a_registered = Signal(bits, reset_less=True)
        self.b_registered = Signal(bits, reset_less=True)
        if multiply_add:
            self.c_registered = Signal(bits * 2, reset_less=True)
        self._final_a_registered = Signal(bits * 2, reset_less=True)
        self._final_b_registered = Signal(bits * 2, reset_less=True)

    def elaborate(self, platform):
        self.m = Module()

        if self._register_input:
            self.m.d.sync += self.a_registered.eq(self.a)
            self.m.d.sync += self.b_registered.eq(self.b)
            if self._multiply_add:
                self.m.d.sync += self.c_registered.eq(self.c)
        else:
            self.m.d.comb += self.a_registered.eq(self.a),
            self.m.d.comb += self.b_registered.eq(self.b),
            if self._multiply_add:
                self.m.d.comb += self.c_registered.eq(self.c)

        self._gen_partial_products()

        if self._multiply_add:
            for i in range(self._bits * 2):
                self._partial_products[i].append(self.c_registered[i])

        self._acc_partial_products()

        if self._register_middle:
            self.m.d.sync += self._final_a_registered.eq(self._final_a)
            self.m.d.sync += self._final_b_registered.eq(self._final_b)
        else:
            self.m.d.comb += self._final_a_registered.eq(self._final_a)
            self.m.d.comb += self._final_b_registered.eq(self._final_b)

        self._final_adder()

        o2 = Signal(self._bits * 2, reset_less=True)
        if self._register_output:
            self.m.d.sync += o2.eq(self.result)
        else:
            self.m.d.comb += o2.eq(self.result)

        self.m.d.comb += self.o.eq(o2)

        return self.m


class BoothRadix4(Elaboratable):
    def _generate_booth_encoder(self, block, sign, sel):
        # This is the standard booth encoder. We output a sign bit
        # and a 2 bit multiplicand selector:

        # block sign sel  how this relates to multiplicand
        # 000   0    00    +0
        # 001   0    10   *+1
        # 010   0    10   *+1
        # 011   0    01   *+2
        # 100   1    01   *-2
        # 101   1    10   *-1
        # 110   1    10   *-1
        # 111   1    00    -0

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

    def _gen_partial_products(self):
        # FIXME: We should avoid writing these top 2 bits
        self._partial_products = [[] for i in range((self._bits) * 2 + 2)]

        multiplier = Signal(self._bits + 3)
        multiplicand = Signal(self._bits + 2)

        # Add a zero in the LSB of the multiplier and multiplicand
        self.m.d.comb += [
            multiplier.eq(Cat(Const(0), self.a_registered, Const(0), Const(0))),
            multiplicand.eq(Cat(Const(0), self.b_registered)),
        ]

        last_b = self._bits
        second_last_b = self._bits - 2
        last_m = self._bits

        # Step through the multiplier 2 bits at a time
        for off_b in range(0, self._bits + 1, 2):
            # ...selecting a block of three bits at a tie
            block = Signal(3, name="booth_block%d" % off_b)
            self.m.d.comb += block.eq(multiplier[off_b:off_b + 3])

            sign = Signal(name="booth_block%d_sign" % off_b)
            sel = Signal(2, name="booth_block%d_sel" % off_b)
            self._generate_booth_encoder(block, sign, sel)

            # Step through the multiplicand 1 bit at a time
            for off_m in range(self._bits + 1):
                # ...selecting 2 bits at a time
                mand = Signal(2, name="booth_block%d_mand%d" % (off_b, off_m))
                self.m.d.comb += mand.eq(multiplicand[off_m:off_m + 2])

                o = Signal(name="booth_b%d_m%d" % (off_b, off_m))
                self._partial_products[off_b + off_m].append(o)

                self._generate_booth_mux(mand, sel, sign, o)

                if off_m == last_m:
                    notsign = Signal()
                    self._generate_inv(sign, notsign)

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

                    if off_b != last_b:
                        # Add sign to lowest bit in block
                        self._partial_products[off_b].append(sign)


class LongMultiplication(Elaboratable):
    def _gen_partial_products(self):
        for off_a in range(self._bits):
            for off_b in range(self._bits):
                o = Signal()
                self._partial_products[off_a + off_b].append(o)
                self._generate_and(self.a[off_a], self.b[off_b], o)


class Dadda(Elaboratable):
    # Dadda heights are d(0) = 2, d(n+1) = floor(1.5*d(n))
    def _calc_dadda_heights(self, bits):
        d = 2
        out = list()

        while d < bits:
            out.append(d)
            d = math.floor(1.5 * d)

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
                    # Put carry at bottom
                    # self._partial_products[offset+1].insert(0, c)
                    self._partial_products[offset + 1].append(c)

                    subiteration = subiteration + 1

            dadda_heights.pop(0)
            iteration = iteration + 1

        for offset in range(len(self._partial_products)):
            while len(self._partial_products[offset]) < 2:
                self._partial_products[offset].append(Const(0))

        self._final_a = Cat(self._partial_products[n][0] for n in range(len(self._partial_products)))
        self._final_b = Cat(self._partial_products[n][1] for n in range(len(self._partial_products)))


class InferredAdder(Elaboratable):
    def _final_adder(self):
        self.m.d.comb += self.result.eq(self._final_a_registered + self._final_b_registered)


class BrentKungNoneAdder(Elaboratable):
    def _final_adder(self):
        self.m.submodules.final_adder = adder = BrentKungNone(bits=self._bits * 2)

        self.m.d.comb += [
            adder.a.eq(self._final_a_registered),
            adder.b.eq(self._final_b_registered),
            self.result.eq(adder.o),
        ]


class BrentKungSKY130Adder(Elaboratable):
    def _final_adder(self):
        self.m.submodules.final_adder = adder = BrentKungSKY130(bits=self._bits * 2)

        self.m.d.comb += [
            adder.a.eq(self._final_a_registered),
            adder.b.eq(self._final_b_registered),
            self.result.eq(adder.o),
        ]
        if self._powered:
            self.m.d.comb += [
                adder.VPWR.eq(self.VPWR),
                adder.VGND.eq(self.VGND),
            ]


class BoothRadix4DaddaBrentKungNone(Multiplier, BoothRadix4, Dadda, ProcessNone, BrentKungNoneAdder):
    pass


class BoothRadix4DaddaBrentKungSKY130(Multiplier, BoothRadix4, Dadda, ProcessSKY130, BrentKungSKY130Adder):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create Verilog Multiplier')

    parser.add_argument('--bits', type=int,
                        help='Width in bits of adder', default=32)

    parser.add_argument('--multiply-add', action='store_true',
                        help='Multiply add (a*b+c)')

    parser.add_argument('--register-input', action='store_true',
                        help='Add a register stage to the input')

    parser.add_argument('--register-middle', action='store_true',
                        help='Add a register stage in between partial product '
                             'generation and partial product accumulation')

    parser.add_argument('--register-output', action='store_true',
                        help='Add a register stage to the output')

    parser.add_argument('--powered', action='store_true',
                        help='Add power pins (VPWR/VGND)')

    parser.add_argument('--process',
                        help='What process to build for, eg sky130')

    parser.add_argument('--output', type=argparse.FileType('w'), default=sys.stdout,
                        help='Write output to this file')

    args = parser.parse_args()

    mymultiplier = BoothRadix4DaddaBrentKungNone
    if args.process:
        if args.process == 'sky130':
            mymultiplier = BoothRadix4DaddaBrentKungSKY130
        else:
            print("Unknown process")
            exit(1)

    multiplier = mymultiplier(bits=args.bits, multiply_add=args.multiply_add,
                              register_input=args.register_input,
                              register_middle=args.register_middle,
                              register_output=args.register_output,
                              powered=args.powered)

    ports = [multiplier.a, multiplier.b, multiplier.o]
    name = 'multiplier'
    if args.multiply_add:
        ports.append(multiplier.c)
        name = 'multiply_adder'
    if args.powered:
        ports.extend([multiplier.VPWR, multiplier.VGND])

    args.output.write(verilog.convert(multiplier, ports=ports, name=name, strip_internal_attrs=True))
