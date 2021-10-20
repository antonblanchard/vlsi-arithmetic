PYTHON=python3
YOSYS=/home/anton_unencrypted/yosys-install/bin/yosys
VERILATOR=/home/anton_unencrypted/verilator.install/bin/verilator
VERILATOR_FLAGS=-O3 -Wno-fatal #--trace
VERILATOR_CFLAGS=-O3

adder_targets = adder_sky130.v adder_pipelined_sky130.v
#all: adder.v adder_sky130 multiplier.v multiplier_sky130.v

all: $(adder_targets)

$(adder_targets): 



adder.v adder_sky130.v: brent_kung.py
	$(PYTHON) brent_kung.py

Vtest: test.v sky130/primitives.v sky130/sky130_fd_sc_hd.v top.cpp
	$(VERILATOR) $(VERILATOR_FLAGS) -CFLAGS "$(VERILATOR_CFLAGS)" --assert --cc --exe --build $^ -o $@ -top-module test
	@cp -f obj_dir/Vtest Vtest

#brent_kung.v
#brent_kung_sky130.v

#booth_dadda_brent_kung.v
#booth_dadda_brent_kung_sky130.v
