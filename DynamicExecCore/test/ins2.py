# Assembly code corresponding to ins2.txt
'''
                    Issued at           Finished at
ADD R1, R4, R2         0                    1
MUL R1, R3, R5         0                    2
DIV R2, R1, R4         2                    6
SUB R1, R1, R2         7                    8
LOD R6, R7, R8         3                    9
SUB R7, R6, R1         9                    10
MUL R3, R2, R5         7                    9
DIV R4, R3, R2         7                    11
STO R1, R5, R2         10                   16

Estimated Number of Cycles required: 17 (1 additional instruction to flush out RoB)
Reported Number of Cycles: 17
'''
