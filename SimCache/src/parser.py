class inputParser:
    def __init__(self, inputFile:str):
        self.inputFile = inputFile
    def parse(self):
        replacementPolicies = ["RANDOM", "LRU", "PLRU"]
        with open(self.inputFile) as f:
            lines = f.read().splitlines()
        cacheSize = int(lines[0].split("\t")[0])
        blockSize = int(lines[1].split("\t")[0])
        associativity = int(lines[2].split("\t")[0])
        associativityType = "SA"
        if associativity < 2:
            if associativity == 1:
                associativityType = "DM"
            else:
                associativityType = "FA"
        replacementPolicy = replacementPolicies[int(lines[3].split("\t")[0])]
        traceFile = lines[4].strip()
        print("---------- Cache Configuration  ----------")
        print("Cache size: {}".format(cacheSize))
        print("Block size: {}".format(blockSize))
        print("Associativity: {}".format(associativity))
        print("  Type: {}".format(associativityType))
        if associativityType != "FA":
            print("  Number of Sets: {}".format(int(cacheSize/(blockSize*associativity))))
        print("Replacement Policy: {}".format(replacementPolicy))
        print("Trace File: {}".format(traceFile))
        print("------------------------------------------")
        print()
        return cacheSize, blockSize, associativity, associativityType, replacementPolicy, traceFile

class traceParser:
    def __init__(self, traceFile:str):
        self.traceFile = traceFile
    def parse(self):
        with open(self.traceFile) as f:
            lines = f.read().splitlines()
        trace = []
        for line in lines:
            tempTrace = line.split(" ")
            tempTrace[0] = int(tempTrace[0], 16)
            trace.append(tempTrace)
        return trace

if __name__ == "__main__":
    parser = inputParser("test/input.txt")
    cs, bs, a, at, rp, tf = parser.parse()
    print("Cache size: {}".format(cs))
    print("Block size: {}".format(bs))
    print("Associativity: {}".format(a))
    print("  Type: {}".format(at))
    print("Replacement Policy: {}".format(rp))
    print("Trace File: {}".format(tf))
    tracer = traceParser(tf)
    print(tracer.parse())
