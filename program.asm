MOV @R1,R0
ADD #1, R0
MOV #1, R1
MOV @R1, R2
loop:
CMP R2, @R1
JLO skip_update
MOV @R1, R2
skip_update:
ADD #1, R1
CMP R0, R1
JLO loop
NOP





