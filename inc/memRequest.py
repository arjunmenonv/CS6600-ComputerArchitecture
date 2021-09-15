class memReq:
    def __init__(self, pid, virtAddr, reqType):
        self.pid = pid
        self.va = virtAddr
        self.typ = reqType
    def print(self):
        print("PID: {0}\t Virtual Address: {1}\t Type: {2}".format(self.pid, self.va, self.typ))
