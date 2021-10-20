import math
import unittest
import random
from nmigen.sim import Simulator, Settle

from multiplier import BoothRadix4Dadda


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
        self.bits=64
        self.dut = BoothRadix4Dadda(self.bits)

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


class TestCaseExhaustive(unittest.TestCase):
    def setUp(self):
        self.bits=8
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
        with sim.write_vcd("multiplier_exhaustive.vcd"):
            sim.run()


class TestCaseRandom(unittest.TestCase):
    def setUp(self):
        self.bits=32
        self.dut = BoothRadix4Dadda(self.bits)

    def do_one_comb(self, a, b):
        yield self.dut.a.eq(a)
        yield self.dut.b.eq(b)
        yield Settle()
        res = (yield self.dut.o)
        self.assertEqual(res, a * b)

    def test_random(self):
        def bench():
            for i in range(1000):
                rand_a = random.getrandbits(self.bits)
                rand_b = random.getrandbits(self.bits)
                yield from self.do_one_comb(rand_a, rand_b)

        sim = Simulator(self.dut)
        sim.add_process(bench)
        with sim.write_vcd("multiplier_random.vcd"):
            sim.run()


class TestCasePipelined(unittest.TestCase):
    def setUp(self):
        self.bits = 64
        self.dut = BoothRadix4Dadda(bits=self.bits, register_input=True, register_middle=True, register_output=True)

    def do_one_sync(self, a, b, cycles=3):
        yield self.dut.a.eq(a)
        yield self.dut.b.eq(b)

        # Why do we need this extra yield? I don't understand something about the nmigen simulator
        yield

        for i in range(cycles):
            yield
            yield self.dut.a.eq(0)
            yield self.dut.b.eq(0)

        res = (yield self.dut.o)
        self.assertEqual(res, a * b)

    def test(self):
        def bench():
            for i in range(1000):
                rand_a = random.getrandbits(self.bits)
                rand_b = random.getrandbits(self.bits)
                yield from self.do_one_sync(rand_a, rand_b)

        sim = Simulator(self.dut)
        sim.add_clock(1e-9)
        sim.add_sync_process(bench)
        with sim.write_vcd("multiplier_pipelined.vcd"):
            sim.run()


if __name__ == '__main__':
    unittest.main()
