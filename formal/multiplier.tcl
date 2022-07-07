yosys -import

read_verilog -defer gold/multiplier.v
chparam -set BITS $::env(BITS) gold_multiplier
prep -flatten -top gold_multiplier
splitnets -ports
design -stash gold

read_verilog $::env(VERILOG) $::env(PROCESS_VERILOG)
prep -flatten -top multiplier
splitnets -ports
design -stash gate

design -copy-from gold -as gold gold_multiplier
design -copy-from gate -as gate multiplier
equiv_make gold gate equiv
prep -flatten -top equiv

opt_clean -purge
#show -prefix equiv-prep -colors 1 -stretch

opt -full
equiv_simple
equiv_induct
equiv_status -assert
