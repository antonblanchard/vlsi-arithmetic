yosys -import

read_verilog -defer gold/multiply_adder_pipelined.v
chparam -set BITS $::env(BITS) gold_multiply_adder_pipelined
prep -flatten -top gold_multiply_adder_pipelined
splitnets -ports
design -stash gold

read_verilog $::env(VERILOG) $::env(PROCESS_VERILOG)
prep -flatten -top multiply_adder
splitnets -ports
design -stash gate

design -copy-from gold -as gold gold_multiply_adder_pipelined
design -copy-from gate -as gate multiply_adder
equiv_make gold gate equiv
prep -flatten -top equiv

opt_clean -purge
#show -prefix equiv-prep -colors 1 -stretch

## method 1
opt -full
equiv_simple -seq 5
equiv_induct -seq 5
equiv_status -assert

## method 2
#equiv_struct -icells t:$adff t:$equiv
#equiv_simple -seq 5
#equiv_induct -seq 5
#equiv_status -assert

## method 3
#techmap -map +/adff2dff.v
#equiv_simple -seq 5
#equiv_induct -seq 5
#equiv_status -assert

## method 4
#clk2fflogic
#equiv_simple -seq 10
#equiv_induct -seq 10
#equiv_status -assert
