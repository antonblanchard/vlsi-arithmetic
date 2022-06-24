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
#if PIPELINE_DEPTH > 0
	m->clk = 1;
	m->eval();
	main_time++;

	m->clk = 0;
	m->eval();
	main_time++;
#endif
}

int main(int argc, char** argv)
{
	int32_t pipeline[PIPELINE_DEPTH+1];
	Vmultiply_adder *m;

	Verilated::commandArgs(argc, argv);

	m = new Vmultiply_adder;

	for (unsigned long a = 0; a < 0xFF; a++) {
		for (unsigned long b = 0; b < 0xFF; b++) {
			for (unsigned long c = 0; c < 0xFF; c++) {
				m->a = a;
				m->b = b;
				m->c = c;

				m->eval();

				for (unsigned long i = PIPELINE_DEPTH; i > 0; i--)
					pipeline[i] = pipeline[i-1];

				pipeline[0] = a * b + c;

				if ((!PIPELINE_DEPTH || (main_time > 6)) && (pipeline[PIPELINE_DEPTH] != m->o))
					std::cout << "ERROR: " << a << " * " << b << " + " << c <<
						" got " << m->o <<
						" expected " << pipeline[PIPELINE_DEPTH] << std::endl;

				tick(m);
			}
		}
	}

	m->final();

	delete m;
}
