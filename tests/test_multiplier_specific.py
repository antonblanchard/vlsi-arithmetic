import unittest
import random
from amaranth.sim import Simulator, Settle

from multiplier import BoothRadix4DaddaBrentKungNone


class TestCaseSpecific(unittest.TestCase):
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

    def setUp(self):
        self.bits = 64
        self.dut = BoothRadix4DaddaBrentKungNone(self.bits)

    def do_one_comb(self, a, b):
        yield self.dut.a.eq(a)
        yield self.dut.b.eq(b)
        yield Settle()
        res = (yield self.dut.o)
        self.assertEqual(res, a * b)

    def test_cases(self):
        def bench():
            for (a, b) in [(x, y) for x in self.cases for y in self.cases]:
                rand_a = random.getrandbits(self.bits)
                rand_b = random.getrandbits(self.bits)
                yield from self.do_one_comb(rand_a, rand_b)

        sim = Simulator(self.dut)
        sim.add_process(bench)
        with sim.write_vcd("multiplier_specific.vcd"):
            sim.run()


if __name__ == '__main__':
    unittest.main()
