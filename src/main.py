import argparse as ap
from inc.opts import *
from inc.parser import inputParser
from memory import *

def args():
    '''
    Parse command-line arguments

    '''
    parser = ap.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, metavar='file', help="Input file with requests", required=True)
    args = parser.parse_args()
    return args

def main():
    '''
    Main simulation function

    '''
    inFile = args().input
    fileParser = inputParser(inFile)
    reqs = fileParser.parse()
    for req in reqs:
        req.print()

    kfree_pages = range(256)
    ufree_pages = range(768)



if __name__=="__main__":
    main()
    # print("Please check back later. In development")


'''
Test run

userMem = memory()
kernelMem = memory(256, 1024, "kernel")
print("Testing __init__()")
userMem.updateLRU(65)
userMem.updateLRU(64)
kernelMem.updateLRU(9)
kernelMem.updateLRU(7)
kernelMem.updateLRU(8)
userMem.updateLRU(63)
userMem.updateLRU(0)
kernelMem.updateLRU(7)
kernelMem.updateLRU(0)
userMem.updateLRU(64)
print(userMem.LRUctr[0:6], userMem.LRUctr[62:66], userMem.freeFrames.qsize())
print(kernelMem.LRUctr[0:10], kernelMem.freeFrames.qsize())
print(userMem.evictFrame(), kernelMem.evictFrame())
print(userMem.invalidateEntry("user", 20))
print(kernelMem.invalidateEntry("kernel", 20))
'''
