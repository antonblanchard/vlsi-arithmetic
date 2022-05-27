#include <verilated.h>
#include <iostream>
#include "Vmultiply_adder.h"

vluint64_t main_time = 0;

double sc_time_stamp()
{
	return main_time;
}

void tick(Vmultiply_adder *m)
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
	Vmultiply_adder *m;

	Verilated::commandArgs(argc, argv);

	m = new Vmultiply_adder;

	for (unsigned long a = 0; a < 0xFF; a++) {
		for (unsigned long b = 0; b < 0xFF; b++) {
			for (unsigned long c = 0; c < 0xFF; c++) {
				m->a = a;
				m->b = b;
				m->c = c;
				pipeline[2] = pipeline[1];
				pipeline[1] = pipeline[0];
				pipeline[0] = a * b + c;
				tick(m);
				if ((main_time > 6) && pipeline[2] != m->o)
					std::cout << "ERROR: " << a << " * " << b << " + " << c <<
						" got " << m->o <<
						" expected " << pipeline[2] << std::endl;
			}
		}
	}

	m->final();

	delete m;
}
