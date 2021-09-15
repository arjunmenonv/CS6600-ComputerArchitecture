'''
Input file parser module

'''
from inc.memRequest import memReq

class inputParser:
    '''
    Takes a file name (str) as argument

    Functions
    ---------
    parse(): returns list[memReq], from file self.inputFile

    '''
    def __init__(self, file):
        self.inputFile = file

    def parse(self):
        '''
        Takes input file, with read/write requests
        in the following format and converts them to
        a list of requests of type request

        pid address type

        '''
        requests = []
        with open(self.inputFile, "r") as f:
            for line in f:
                reqData = line.split()
                pid = int(reqData[0])
                va = int(reqData[1], base=16)
                typ = reqData[2]
                req = memReq(pid,va,typ)
                requests.append(req)
        return requests

if __name__=="__main__":
    parser = inputParser("input/input.txt")
    reqs = parser.parse()
    for req in reqs:
        req.print()
