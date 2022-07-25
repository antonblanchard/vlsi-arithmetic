#!/bin/bash -e

mkdir -p generated

PROCESSES="sky130hd asap7 gf180mcu"
ADDERS="brentkung koggestone hancarlson"

# Test adders
for PROCESS in ${PROCESSES}; do
	for ADDER in ${ADDERS}; do
		VERILOG=generated/adder_${PROCESS}_${ADDER}.v
		python3 adder.py --bits=64 --algorithm=${ADDER} --process=${PROCESS} --output=${VERILOG}
		BITS=64 VERILOG=${VERILOG} PROCESS_VERILOG=${PROCESS}/${PROCESS}.v yosys -c formal/adder.tcl
	done
done

# Test multipliers
for PROCESS in ${PROCESSES}; do
	for ADDER in ${ADDERS}; do
		VERILOG=generated/multiplier_${PROCESS}_${ADDER}.v
		python3 multiplier.py --bits=8 --algorithm=${ADDER} --process=${PROCESS} --output=${VERILOG}
		BITS=8 VERILOG=${VERILOG} PROCESS_VERILOG=${PROCESS}/${PROCESS}.v yosys -c formal/multiplier.tcl
	done
done

# Test multiply adders
for PROCESS in ${PROCESSES}; do
	for ADDER in ${ADDERS}; do
		VERILOG=generated/multiply_adder_${PROCESS}_${ADDER}.v
		python3 multiplier.py --bits=4 --multiply-add --algorithm=${ADDER} --process=${PROCESS} --output=${VERILOG}
		BITS=4 VERILOG=${VERILOG} PROCESS_VERILOG=${PROCESS}/${PROCESS}.v yosys -c formal/multiply_adder.tcl
	done
done

# Test multiply adder with pipelining
for PROCESS in ${PROCESSES}; do
	for ADDER in ${ADDERS}; do
		VERILOG=generated/multiply_adder_${PROCESS}_${ADDER}.v
		python3 multiplier.py --bits=4 --multiply-add --algorithm=${ADDER} --process=${PROCESS} --register-input --register-middle --register-output --output=${VERILOG}
		BITS=4 VERILOG=${VERILOG} PROCESS_VERILOG=${PROCESS}/${PROCESS}.v yosys -c formal/multiply_adder_pipelined.tcl
	done
done
