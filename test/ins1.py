# Assembly code corresponding to ins1.txt
'''
                    Issued at           Finished at
ADD R1, R2, R3         0                    1
SUB R4, R7, R8         1                    2
DIV R6, R5, R1         2                    6
MUL R7, R8, R9         1                    3
LOD R1, R4, R3         3                    9
MUL R6, R2, R1         9                   11
STO R1, R3, R5        10                   16

Estimated Number of Cycles required: 17 (1 additional instruction to flush out RoB)
Reported Number of Cycles: 17         
'''
