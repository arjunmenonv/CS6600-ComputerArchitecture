#*************************************************************
# (C) COPYRIGHT 2016 Samsung Electronics
#
#*************************************************************
#  This shell file gives examples of launching simulations for all 4 categories of workloads


#set this variable to NumCores in your cluster machine for faster sims
num_parallel_jobs=16



###########  HOW TO RUN JOBS?  ################

# The following line will launch sims for all workloads when you run ./doit.sh (comment it if you dont want it to) 
./runall.pl -s ../sim/predictor -w temp -f  $num_parallel_jobs -d ../results/TournamentBPU

###########  HOW TO GET STATS?  ################

# This scripts creates stats, after all the earlier jobs finish
./getdata.pl -w temp -d ../results/TournamentBPU

################## GOOD LUCK! ##################
