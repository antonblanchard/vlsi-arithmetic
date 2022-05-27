#!/bin/bash -e

export PATH=/home/anton_unencrypted/yosys.install/bin/:/home/anton_unencrypted/verilator.install/bin:$PATH

python multiplier.py --bits=8 --multiply-add --process=sky130 --register-input --register-middle --register-output --output=generated/multiplier_sky130_16.v
verilator -O3 -Wno-fatal -Wno-TIMESCALEMOD -CFLAGS -O3 --assert --cc --exe --build generated/multiplier_sky130_16.v sky130/sky130_fd_sc_hd_cutdown.v verilator/multiplier.cpp -o multiplier-verilator -top-module multiply_adder
obj_dir/multiplier-verilator

python adder.py --bits=64 --process=sky130 --output=generated/adder_sky130.v
yosys formal/adder.ys

python multiplier.py --bits=8 --process=sky130 --output=generated/multiplier_sky130.v
yosys formal/multiplier.ys

python multiplier.py --bits=8 --multiply-add --process=sky130 --output=generated/multiply_adder_sky130.v
yosys formal/multiply_adder.ys

python multiplier.py --bits=4 --multiply-add --process=sky130 --register-input --register-middle --register-output --output=generated/multiply_adder_pipelined_sky130.v
yosys formal/multiply_adder_pipelined.ys

#python -m unittest
