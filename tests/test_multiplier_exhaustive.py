import math
import unittest
import random
from amaranth.sim import Simulator, Settle

from multiplier import BoothRadix4DaddaBrentKungNone


class TestCaseExhaustive(unittest.TestCase):
    def setUp(self):
        self.bits=8
        self.dut = BoothRadix4DaddaBrentKungNone(self.bits)

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
        with sim.write_vcd("multiplier_exhaustive.vcd"):
            sim.run()


if __name__ == '__main__':
    unittest.main()
