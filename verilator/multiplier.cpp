#include <verilated.h>
#include <iostream>
#include "Vmultiplier.h"

vluint64_t main_time = 0;

double sc_time_stamp()
{
	return main_time;
}

int main(int argc, char** argv)
{
	Vmultiplier *m;

	Verilated::commandArgs(argc, argv);

	m = new Vmultiplier;

	for (unsigned long a = 0; a < 0xFFFF; a++) {
		for (unsigned long b = 0; b < 0xFFFF; b++) {
			m->a = a;
			m->b = b;
        		m->eval();
			if ((a * b) != m->o)
				std::cout << "ERROR: " << a << " * " << b <<
					" got " << m->o <<
					" expected " << a*b << std::endl;
		}
	}

	m->final();

	delete m;
}
