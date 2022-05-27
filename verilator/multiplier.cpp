#include <verilated.h>
#include <iostream>
#include "Vmultiplier.h"

vluint64_t main_time = 0;

double sc_time_stamp()
{
	return main_time;
}

void tick(Vmultiplier *m)
{
	m->clk = 1;
	m->eval();
#if VM_TRACE
	if (tfp)
		tfp->dump((double) main_time);
#endif
	main_time++;

	m->clk = 0;
	m->eval();
#if VM_TRACE
	if (tfp)
		tfp->dump((double) main_time);
#endif
	main_time++;
}

int main(int argc, char** argv)
{
	int32_t pipeline[3];
	Vmultiplier *m;

	Verilated::commandArgs(argc, argv);

	m = new Vmultiplier;

	for (unsigned long a = 0; a < 0xFFFF; a++) {
		for (unsigned long b = 0; b < 0xFFFF; b++) {
			m->a = a;
			m->b = b;
			pipeline[2] = pipeline[1];
			pipeline[1] = pipeline[0];
			pipeline[0] = a * b;
			tick(m);
			if ((main_time > 6) && pipeline[2] != m->o)
				std::cout << "ERROR: " << a << " * " << b <<
					" got " << m->o <<
					" expected " << pipeline[2] << std::endl;
		}
	}

	m->final();

	delete m;
}
