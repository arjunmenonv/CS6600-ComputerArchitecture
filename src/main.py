from conf import *
import instructionDecoder

def main():
    '''
    Main Simulator Loop
    '''
    with open(INS_FILE, 'r') as f:
        instructionsRaw = f.readlines()
    instructionsDecoded = [instructionDecoder.decode(i) for i in instructionsRaw]

    PC = 0
    for i in range(PC, PC+ISSUE_WIDTH, 1):
        dispatch(instructionsDecoded[i], asu, mu, du, lsu)
    return

if __name__=="__main__":
    print("In development. Check back later")
