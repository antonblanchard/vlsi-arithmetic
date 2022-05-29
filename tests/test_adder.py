import unittest
import random
from amaranth.sim import Simulator, Settle

from process_none import ProcessNone
from adder import BrentKung, KoggeStone


class TestBrentKungAdder(BrentKung, ProcessNone):
    pass


class TestKoggeStoneAdder(KoggeStone, ProcessNone):
    pass


class TestCaseBrentKungRandom(unittest.TestCase):
    def setUp(self):
        self.bits = 64
        self.dut = TestBrentKungAdder(self.bits)

    def do_one_comb(self, a, b):
        yield self.dut.a.eq(a)
        yield self.dut.b.eq(b)
        yield Settle()
        res = (yield self.dut.o)
        expected = (a + b) & (pow(2, self.bits) - 1)
        self.assertEqual(res, expected)

    def test_random(self):
        def bench():
            for i in range(1000):
                rand_a = random.getrandbits(self.bits)
                rand_b = random.getrandbits(self.bits)
                yield from self.do_one_comb(rand_a, rand_b)

        sim = Simulator(self.dut)
        sim.add_process(bench)
        with sim.write_vcd("adder_random.vcd"):
            sim.run()


class TestCaseKoggeStoneRandom(unittest.TestCase):
    def setUp(self):
        self.bits = 64
        self.dut = TestKoggeStoneAdder(self.bits)

    def do_one_comb(self, a, b):
        yield self.dut.a.eq(a)
        yield self.dut.b.eq(b)
        yield Settle()
        res = (yield self.dut.o)
        expected = (a + b) & (pow(2, self.bits) - 1)
        self.assertEqual(res, expected)

    def test_random(self):
        def bench():
            for i in range(1000):
                rand_a = random.getrandbits(self.bits)
                rand_b = random.getrandbits(self.bits)
                yield from self.do_one_comb(rand_a, rand_b)

        sim = Simulator(self.dut)
        sim.add_process(bench)
        with sim.write_vcd("adder_random.vcd"):
            sim.run()


if __name__ == '__main__':
    unittest.main()
