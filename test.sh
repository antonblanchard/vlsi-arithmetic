#!/bin/bash -e

export PATH=$PATH:/home/anton_unencrypted/yosys-install/bin/

python adder.py --bits=64 --process=sky130 --output=adder_sky130.v

yosys formal/adder.ys

python multiplier.py --bits=8 --process=sky130 --output=multiplier_sky130.v

yosys formal/multiplier.ys

python multiplier.py --bits=8 --multiply-add --process=sky130 --output=multiply_adder_sky130.v

yosys formal/multiply_adder.ys

python -m unittest
