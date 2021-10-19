import math
import unittest
import random
from nmigen.sim import Simulator, Settle

from multiplier import BoothRadix4Dadda


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
