'''
Memory Request module

'''
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
        print("PID: {0}\t Virtual Address: {1}\t Type: {2}".format(self.pid, self.va, self.typ))
