'''
Memory Request module

'''

from src.translator import translate

class memReq:
    '''
    Structure to store PID, va, type of memory request

    Functions
    ---------
    print(): print the contents of the request

    '''
    def __init__(self, pid, virtAddr, reqType):
        self.pid = pid
        self.va = virtAddr
        self.typ = reqType

    def print(self):
        '''
        Print the contents of the request as:
        PID: {}    Virtual Address: {}    Type: {}

        '''
        offsets = translate(self.va)
        print("PID: {0}\tdirOffset: {1}\ttableOffset: {2}".format(self.pid, offsets[0], offsets[1]))
