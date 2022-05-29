import math
import unittest
import random
from amaranth.sim import Simulator, Settle

from multiplier import BoothRadix4DaddaBrentKungNone


class TestCasePipelined(unittest.TestCase):
    def setUp(self):
        self.bits = 64
        self.dut = BoothRadix4DaddaBrentKungNone(bits=self.bits, multiply_add=True, register_input=True, register_middle=True, register_output=True)

    def do_one_sync(self, a, b, c, cycles=3):
        yield self.dut.a.eq(a)
        yield self.dut.b.eq(b)
        yield self.dut.c.eq(c)
        yield # Why we need an extra yield?

        for i in range(cycles):
            yield
            yield self.dut.a.eq(0)
            yield self.dut.b.eq(0)
            yield self.dut.c.eq(0)

        res = (yield self.dut.o)
        self.assertEqual(res, a * b + c)

    def test(self):
        def bench():
            for i in range(100):
                rand_a = random.getrandbits(self.bits)
                rand_b = random.getrandbits(self.bits)
                rand_c = random.getrandbits(self.bits)
                yield from self.do_one_sync(rand_a, rand_b, rand_c)

        sim = Simulator(self.dut)
        sim.add_clock(1e-9)
        sim.add_sync_process(bench)
        with sim.write_vcd("multiply_adder_pipelined.vcd"):
            sim.run()


if __name__ == '__main__':
    unittest.main()
