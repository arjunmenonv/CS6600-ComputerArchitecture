#*************************************************************
# (C) COPYRIGHT 2016 Samsung Electronics
#
#*************************************************************
#
#  This shell file gives examples of launching simulations for all 4 categories of workloads


# set this variable to NumCores in your cluster machine for faster sims
num_parallel_jobs=16
run_suite=custom

###########  HOW TO RUN JOBS?  ################

# The following line will launch sims for all workloads when you run ./doit.sh (comment it if you dont want it to)
##############################

time ./runall.pl -s ../sim/predictor -w $run_suite -f  $num_parallel_jobs -d ../results/TournamentBPUcustom
./getdata.pl -w $run_suite -noxxxx -d ../results/TournamentBPUcustom > ../results/TournamentBPUcustom/rollup
./getdata.pl -w $run_suite -s Predicted_Taken_Skew -noxxxx -d ../results/TournamentBPUcustom > ../results/TournamentBPUcustom/PTSresults
./getdata.pl -w $run_suite -s True_Taken_Skew -noxxxx -d ../results/TournamentBPUcustom > ../results/TournamentBPUcustom/TTSresults
./getdata.pl -w $run_suite -s Strong_Local_Bias -noxxxx -d ../results/TournamentBPUcustom > ../results/TournamentBPUcustom/SLBresults
./getdata.pl -w $run_suite -s Weak_Local_Bias -noxxxx -d ../results/TournamentBPUcustom > ../results/TournamentBPUcustom/WLBresults
./getdata.pl -w $run_suite -s Weak_Global_Bias -noxxxx -d ../results/TournamentBPUcustom > ../results/TournamentBPUcustom/WGBresults
./getdata.pl -w $run_suite -s Strong_Global_Bias -noxxxx -d ../results/TournamentBPUcustom > ../results/TournamentBPUcustom/SGBresults



################## GOOD LUCK! ##################
