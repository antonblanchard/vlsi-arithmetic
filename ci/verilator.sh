#!/bin/bash -e

mkdir -p generated

python3 multiplier.py --bits=8 --algorithm=brentkung --multiply-add --process=sky130 --output=generated/multiplier_sky130_16.v
verilator -O3 -Wno-fatal -Wno-TIMESCALEMOD -CFLAGS "-O3 -DPIPELINE_DEPTH=0" --assert --cc --exe --build generated/multiplier_sky130_16.v sky130/sky130_fd_sc_hd_cutdown.v verilator/multiplier.cpp -o multiplier-verilator -top-module multiply_adder
obj_dir/multiplier-verilator

python3 multiplier.py --bits=8 --algorithm=koggestone --multiply-add --process=sky130 --register-input --output=generated/multiplier_sky130_16.v
verilator -O3 -Wno-fatal -Wno-TIMESCALEMOD -CFLAGS "-O3 -DPIPELINE_DEPTH=1" --assert --cc --exe --build generated/multiplier_sky130_16.v sky130/sky130_fd_sc_hd_cutdown.v verilator/multiplier.cpp -o multiplier-verilator -top-module multiply_adder
obj_dir/multiplier-verilator

python3 multiplier.py --bits=8 --algorithm=hancarlson --multiply-add --process=sky130 --register-middle --output=generated/multiplier_sky130_16.v
verilator -O3 -Wno-fatal -Wno-TIMESCALEMOD -CFLAGS "-O3 -DPIPELINE_DEPTH=1" --assert --cc --exe --build generated/multiplier_sky130_16.v sky130/sky130_fd_sc_hd_cutdown.v verilator/multiplier.cpp -o multiplier-verilator -top-module multiply_adder
obj_dir/multiplier-verilator

python3 multiplier.py --bits=8 --algorithm=brentkung --multiply-add --process=sky130 --register-output --output=generated/multiplier_sky130_16.v
verilator -O3 -Wno-fatal -Wno-TIMESCALEMOD -CFLAGS "-O3 -DPIPELINE_DEPTH=1" --assert --cc --exe --build generated/multiplier_sky130_16.v sky130/sky130_fd_sc_hd_cutdown.v verilator/multiplier.cpp -o multiplier-verilator -top-module multiply_adder
obj_dir/multiplier-verilator

python3 multiplier.py --bits=8 --algorithm=koggestone --multiply-add --process=sky130 --register-input --register-middle --output=generated/multiplier_sky130_16.v
verilator -O3 -Wno-fatal -Wno-TIMESCALEMOD -CFLAGS "-O3 -DPIPELINE_DEPTH=2" --assert --cc --exe --build generated/multiplier_sky130_16.v sky130/sky130_fd_sc_hd_cutdown.v verilator/multiplier.cpp -o multiplier-verilator -top-module multiply_adder
obj_dir/multiplier-verilator

python3 multiplier.py --bits=8 --algorithm=hancarlson --multiply-add --process=sky130 --register-input --register-output --output=generated/multiplier_sky130_16.v
verilator -O3 -Wno-fatal -Wno-TIMESCALEMOD -CFLAGS "-O3 -DPIPELINE_DEPTH=2" --assert --cc --exe --build generated/multiplier_sky130_16.v sky130/sky130_fd_sc_hd_cutdown.v verilator/multiplier.cpp -o multiplier-verilator -top-module multiply_adder
obj_dir/multiplier-verilator

python3 multiplier.py --bits=8 --algorithm=brentkung --multiply-add --process=sky130 --register-middle --register-output --output=generated/multiplier_sky130_16.v
verilator -O3 -Wno-fatal -Wno-TIMESCALEMOD -CFLAGS "-O3 -DPIPELINE_DEPTH=2" --assert --cc --exe --build generated/multiplier_sky130_16.v sky130/sky130_fd_sc_hd_cutdown.v verilator/multiplier.cpp -o multiplier-verilator -top-module multiply_adder
obj_dir/multiplier-verilator

python3 multiplier.py --bits=8 --algorithm=koggestone --multiply-add --process=sky130 --register-input --register-middle --register-output --output=generated/multiplier_sky130_16.v
verilator -O3 -Wno-fatal -Wno-TIMESCALEMOD -CFLAGS "-O3 -DPIPELINE_DEPTH=3" --assert --cc --exe --build generated/multiplier_sky130_16.v sky130/sky130_fd_sc_hd_cutdown.v verilator/multiplier.cpp -o multiplier-verilator -top-module multiply_adder
obj_dir/multiplier-verilator
