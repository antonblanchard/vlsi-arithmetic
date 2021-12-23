import sys
import math
import argparse

from amaranth import Elaboratable, Module, Signal, Const
from amaranth.back import verilog

from process_sky130 import ProcessSKY130
from process_none import ProcessNone


class BrentKung(Elaboratable):
    def __init__(self, bits=64, register_input=False, register_output=False):
        self.a = Signal(bits)
        self.b = Signal(bits)
        self.o = Signal(bits)
        self.VPWR = Signal()
        self.VGND = Signal()

        self._bits = bits
        self._register_input = register_input
        self._register_output = register_output

    def elaborate(self, platform):
        self.m = m = Module()

        a = Signal(self._bits, reset_less=True)
        b = Signal(self._bits, reset_less=True)
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

        # Calculate p and g for the even bits
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

        o2 = Signal(self._bits, reset_less=True)
        if self._register_output:
            m.d.sync += o2.eq(o)
        else:
            m.d.comb += o2.eq(o)

        m.d.comb += self.o.eq(o2)
        return m


class BrentKungNone(BrentKung, ProcessNone):
    pass


class BrentKungSKY130(BrentKung, ProcessSKY130):
    pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create Verilog Adder')

    parser.add_argument('--bits', type=int,
                        help='Width in bits of adder', default=32)

    parser.add_argument('--register-input', action='store_true',
                        help='Add a register stage to the input')

    parser.add_argument('--register-output', action='store_true',
                        help='Add a register stage to the output')

    parser.add_argument('--process',
                        help='What process to build for, eg sky130')

    parser.add_argument('--output', type=argparse.FileType('w'), default=sys.stdout,
                        help='Write output to this file')

    args = parser.parse_args()

    myadder = BrentKungNone
    if args.process:
        if args.process == 'sky130':
            myadder = BrentKungSKY130
        else:
            print("Unknown process")
            exit(1)

    adder = myadder(bits=args.bits, register_input=args.register_input, register_output=args.register_output)

    args.output.write(verilog.convert(adder, ports=[adder.a, adder.b, adder.o, adder.VPWR, adder.VGND], name='adder', strip_internal_attrs=True))
