from cache import cache
from parser import inputParser, traceParser
from tqdm import tqdm
import math

def isNotPow2(val):
    log_val = math.log(val, 2)
    res_val = log_val - int(log_val)
    if (res_val == 0):
        return False
    else:
        return True

def main():
    confParser = inputParser("input/conf.txt")
    cacheSize, blockSize, assoc, assocType, replacementPolicy, traceFile = confParser.parse()
    # check if cSize, bSize and assoc are powers of 2:
    if (isNotPow2(cacheSize)):
        print("ERROR: Cache Size is not Power of 2, exiting...")
        exit()
    elif(isNotPow2(blockSize)):
        print("ERROR: Block Size is not Power of 2, exiting...")
        exit()
    elif(isNotPow2(assoc)):
        print("ERROR: Associativity is not Power of 2, exiting...")
        exit()

    if assocType == "SA":
        numSets = int(cacheSize / (blockSize * assoc))
    elif assocType == "DM":
        numSets = int(cacheSize / blockSize)
        assoc = 1
        replacementPolicy = "RANDOM"
    elif assocType == "FA":
        assoc = int(cacheSize/blockSize)
        numSets = 1
    else:
        raise ValueError("Invalid Associativity Type" + " " + assocType)

    cacheModule = cache(numSets, assoc, replacementPolicy)
    tracer = traceParser(traceFile)
    requests = tracer.parse()

    print("Running Simulation ...")
    for request in tqdm(requests):
        address = request[0]//blockSize
        accessType = request[1]
        cacheModule.memRequest(address, accessType)
    print()
    cacheModule.printStats()
    return

if __name__ == "__main__":
    print("============= SimCache: A Python-Based Uniprocessor Cache Simulator =============")
    print()
    main()
