# Script File to run C program and the python script for Plotting

gcc -O0 -o test -march=native L1_paramEst.c # avoid compiler optimisations
taskset -c 0 ./test                         # constrain to using 1 core
#
python3 plot_curves.py
