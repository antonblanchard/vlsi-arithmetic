yosys -import

read_verilog -defer gold/multiply_adder.v
chparam -set BITS $::env(BITS) gold_multiply_adder
prep -flatten -top gold_multiply_adder
splitnets -ports
design -stash gold

read_verilog $::env(VERILOG) $::env(PROCESS_VERILOG)
prep -flatten -top multiply_adder
splitnets -ports
design -stash gate

design -copy-from gold -as gold gold_multiply_adder
design -copy-from gate -as gate multiply_adder
equiv_make gold gate equiv
prep -flatten -top equiv

opt_clean -purge
#show -prefix equiv-prep -colors 1 -stretch

opt -full
equiv_simple
equiv_induct
equiv_status -assert
