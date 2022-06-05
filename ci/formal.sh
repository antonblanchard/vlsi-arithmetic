#!/bin/bash -e

mkdir -p generated

python3 adder.py --bits=64 --algorithm=brentkung --process=sky130 --output=generated/adder_sky130.v
yosys formal/adder.ys

python3 adder.py --bits=64 --algorithm=koggestone --process=sky130 --output=generated/adder_sky130.v
yosys formal/adder.ys

python3 adder.py --bits=64 --algorithm=hancarlson --process=sky130 --output=generated/adder_sky130.v
yosys formal/adder.ys

python3 multiplier.py --bits=8 --process=sky130 --output=generated/multiplier_sky130.v
yosys formal/multiplier.ys

python3 multiplier.py --bits=4 --multiply-add --algorithm=brentkung --process=sky130 --output=generated/multiply_adder_sky130.v
yosys formal/multiply_adder.ys

python3 multiplier.py --bits=4 --multiply-add --algorithm=koggestone --process=sky130 --output=generated/multiply_adder_sky130.v
yosys formal/multiply_adder.ys

python3 multiplier.py --bits=4 --multiply-add --algorithm=hancarlson --process=sky130 --output=generated/multiply_adder_sky130.v
yosys formal/multiply_adder.ys

python3 multiplier.py --bits=4 --multiply-add --process=sky130 --register-input --register-middle --register-output --output=generated/multiply_adder_pipelined_sky130.v
yosys formal/multiply_adder_pipelined.ys

python3 multiplier.py --bits=4 --multiply-add --algorithm=brentkung --process=sky130 --register-input --register-middle --register-output --output=generated/multiply_adder_pipelined_sky130.v
yosys formal/multiply_adder_pipelined.ys

python3 multiplier.py --bits=4 --multiply-add --algorithm=koggestone --process=sky130 --register-input --register-middle --register-output --output=generated/multiply_adder_pipelined_sky130.v
yosys formal/multiply_adder_pipelined.ys

python3 multiplier.py --bits=4 --multiply-add --algorithm=hancarlson --process=sky130 --register-input --register-middle --register-output --output=generated/multiply_adder_pipelined_sky130.v
yosys formal/multiply_adder_pipelined.ys
