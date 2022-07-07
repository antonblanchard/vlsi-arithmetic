import sys
import math
import argparse

from amaranth import Elaboratable, Module, Signal, Const
from amaranth.back import verilog

from sky130hd.process import SKY130HDProcess
from asap7.process import ASAP7Process
from none.process import NoneProcess


class AdderFramework(Elaboratable):
    def __init__(self, bits=64, register_input=False, register_output=False, powered=False):
        self.a = Signal(bits)
        self.b = Signal(bits)
        self.o = Signal(bits)

        if powered:
            self._powered = True
            self.VPWR = Signal()
            self.VGND = Signal()
        else:
            self._powered = False

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
        self._p = [Signal() for i in range(self._bits)]
        self._g = [Signal() for i in range(self._bits)]

        for i in range(self._bits):
            self._generate_half_adder(a[i], b[i], self._p[i], self._g[i])

        # We need a copy of p
        p_tmp = [Signal() for i in range(self._bits)]
        for i in range(self._bits):
            m.d.comb += p_tmp[i].eq(self._p[i])

        self._calculate_pg()

        # g is the carry out signal. We need to shift it left one bit then
        # xor it with the sum (ie p_tmp). Since we have a list of 1 bit
        # signals, just insert a constant zero signal at the head of of the
        # list to shift g.
        self._g.insert(0, Const(0))

        o = Signal(self._bits)
        for i in range(self._bits):
            # This also flattens the list of bits when writing to o
            self._generate_xor(p_tmp[i], self._g[i], o[i])

        o2 = Signal(self._bits, reset_less=True)
        if self._register_output:
            m.d.sync += o2.eq(o)
        else:
            m.d.comb += o2.eq(o)

        m.d.comb += self.o.eq(o2)
        return m


class BrentKung(AdderFramework):
    def _calculate_pg(self):
        # Calculate the p and g for the odd bits
        for level in range(1, int(math.log(self._bits, 2)) + 1):
            for bit_to in range(2**level - 1, self._bits, 2**level):
                bit_from = bit_to - 2**(level - 1)
                p_new = Signal()
                g_new = Signal()
                self._generate_and(self._p[bit_to], self._p[bit_from], p_new)
                self._generate_and21_or2(self._p[bit_to], self._g[bit_from], self._g[bit_to], g_new)
                self._p[bit_to] = p_new
                self._g[bit_to] = g_new

        # Calculate g for the even bits
        for level in range(int(math.log(self._bits, 2)), 0, -1):
            for bit_to in range(2**level + 2**(level - 1) - 1, self._bits, 2**level):
                bit_from = bit_to - 2**(level - 1)
                g_new = Signal()
                self._generate_and21_or2(self._p[bit_to], self._g[bit_from], self._g[bit_to], g_new)
                self._g[bit_to] = g_new


class KoggeStone(AdderFramework):
    def _calculate_pg(self):
        # Calculate p and g
        for level in range(0, int(math.log(self._bits, 2))):
            # Iterate backwards, because we want p and g from the previous iteration
            # and we update them as we go in this loop
            for bit_from in range(self._bits - 2**level - 1, -1, -1):
                bit_to = bit_from + 2**level
                p_new = Signal()
                g_new = Signal()
                self._generate_and(self._p[bit_from], self._p[bit_to], p_new)
                self._generate_and21_or2(self._p[bit_to], self._g[bit_from], self._g[bit_to], g_new)
                self._p[bit_to] = p_new
                self._g[bit_to] = g_new


# Han Carlson is Kogge Stone on odd bits, with a final stage to calculate the even bits
class HanCarlson(AdderFramework):
    def _calculate_pg(self):
        # Calculate p and g
        for level in range(0, int(math.log(self._bits, 2))):
            # Iterate backwards, because we want p and g from the previous iteration
            # and we update them as we go in this loop
            for bit_from in range(self._bits - 2**level - 1, -1, -1):
                bit_to = bit_from + 2**level
                # Kogge Stone on odd bits only
                if (bit_to & 1) == 0:
                    continue
                p_new = Signal()
                g_new = Signal()
                self._generate_and(self._p[bit_from], self._p[bit_to], p_new)
                self._generate_and21_or2(self._p[bit_to], self._g[bit_from], self._g[bit_to], g_new)
                self._p[bit_to] = p_new
                self._g[bit_to] = g_new

        # Now do the even bits, again working backwards
        for bit_from in range(self._bits - 3, 0, -2):
            bit_to = bit_from + 1
            g_new = Signal()
            self._generate_and21_or2(self._p[bit_to], self._g[bit_from], self._g[bit_to], g_new)
            self._g[bit_to] = g_new


class Inferred(Elaboratable):
    def __init__(self, bits=64, register_input=False, register_output=False, powered=False):
        self.a = Signal(bits)
        self.b = Signal(bits)
        self.o = Signal(bits)

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

        o = Signal(self._bits)
        self.m.d.comb += o.eq(self.a + self.b)

        o2 = Signal(self._bits, reset_less=True)
        if self._register_output:
            m.d.sync += o2.eq(o)
        else:
            m.d.comb += o2.eq(o)

        m.d.comb += self.o.eq(o2)
        return m


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create Verilog Adder')

    parser.add_argument('--bits', type=int,
                        help='Width in bits of adder', default=32)

    parser.add_argument('--register-input', action='store_true',
                        help='Add a register stage to the input')

    parser.add_argument('--register-output', action='store_true',
                        help='Add a register stage to the output')

    parser.add_argument('--process',
                        help='What process to build for, (none (default), sky130hd, asap7)')

    parser.add_argument('--algorithm',
                        help='Adder algorithm (brentkung (default), koggestone, hancarlson, inferred)')

    parser.add_argument('--powered', action='store_true',
                        help='Add power pins (VPWR/VGND)')

    parser.add_argument('--output', type=argparse.FileType('w'), default=sys.stdout,
                        help='Write output to this file')

    args = parser.parse_args()

    process = NoneProcess
    if args.process:
        if args.process == 'none':
            process = NoneProcess
        elif args.process == 'sky130hd':
            process = SKY130HDProcess
        elif args.process == 'asap7':
            process = ASAP7Process
        else:
            print("Unknown process")
            exit(1)

    algorithm = BrentKung
    if args.algorithm:
        if args.algorithm.lower() == 'brentkung':
            algorithm = BrentKung
        elif args.algorithm.lower() == 'koggestone':
            algorithm = KoggeStone
        elif args.algorithm.lower() == 'hancarlson':
            algorithm = HanCarlson
        elif args.algorithm.lower() == 'inferred':
            algorithm = Inferred
        else:
            print("Unknown algorithm")
            exit(1)

    class myadder(process, algorithm):
        pass

    adder = myadder(bits=args.bits, register_input=args.register_input,
                    register_output=args.register_output, powered=args.powered)

    ports = [adder.a, adder.b, adder.o]
    if args.powered:
        ports.extend([adder.VPWR, adder.VGND])

    args.output.write(verilog.convert(adder, ports=ports, name='adder', strip_internal_attrs=True))
