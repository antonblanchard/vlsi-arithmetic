#!/bin/bash -e

VERILATOR_OPTS="-O3 -Wno-fatal -Wno-TIMESCALEMOD"
PROCESSES="sky130hd asap7"
ADDERS="brentkung koggestone hancarlson"

mkdir -p generated

TESTS=""

build_one_test () {
	PIPELINE_DEPTH="$1"
	shift
	ARGS="$*"

	# Exhaustive test of 8 bit multiply/adder for every process and adder type
	for PROCESS in ${PROCESSES}; do
		for ADDER in ${ADDERS}; do
			PIPELINE_CMD=$(echo $ARGS | sed -e 's/ --/-/g' -e 's/--//')
			VERILOG="generated/multiplier_${PROCESS}_${ADDER}_${PIPELINE_CMD}_8.v"
			BINARY=multiply-adder-${PROCESS}-${ADDER}_${PIPELINE_CMD}_8
			python3 multiplier.py --bits=8 --process=${PROCESS} --algorithm=${ADDER} --multiply-add ${ARGS} --output=${VERILOG}
			verilator ${VERILATOR_OPTS} -CFLAGS "-O3 -DPIPELINE_DEPTH=${PIPELINE_DEPTH}" --assert --cc --exe --build ${VERILOG} ${PROCESS}/${PROCESS}.v verilator/multiplier.cpp -o ${BINARY} -top-module multiply_adder
			TESTS="${TESTS} obj_dir/${BINARY}"
		done
	done
}

build_one_test 0 ""
build_one_test 1 "--register-input"
build_one_test 1 "--register-middle"
build_one_test 1 "--register-output"
build_one_test 2 "--register-input --register-middle"
build_one_test 2 "--register-input --register-output"
build_one_test 2 "--register-middle --register-output"
build_one_test 3 "--register-input --register-middle --register-output"

# Run N in parallel
N=4
for TEST in ${TESTS}; do
	echo $TEST
	$TEST &

	if [[ $(jobs -r -p | wc -l) -ge $N ]]; then
		wait -n
	fi
done
