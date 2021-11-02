# class definitions used for Pseudo LRU binary tree
class Node():
    def __init__(self, value = 0):
        self.value = value
        self.left = None
        self.right = None

class TreeStage():
    def __init__(self, stage_num:int):
        num_nodes = (1<<stage_num)
        self.nodes = []
        for _ in range(num_nodes):
            self.nodes.extend([Node()])

class Tree():
    def __init__(self, numStages:int):
        self.numStages = numStages
        self.stages = []
        self.root = TreeStage(0)
        curr_stage = self.root
        self.stages.extend([curr_stage])
        for i in range(1, self.numStages):
            prev_stage = curr_stage
            curr_stage = TreeStage(i)
            num_nodes_prev = 1<<(i-1)
            for j in range(num_nodes_prev):
                prev_stage.nodes[j].left = curr_stage.nodes[2*j]
                prev_stage.nodes[j].right = curr_stage.nodes[2*j + 1]
            self.stages.extend([curr_stage])

    def traverse(self, setIndex:int):
        exp = self.numStages - 1
        curr_node = self.root.nodes[0]     # root node
        for _ in range(self.numStages):
            dir = int(setIndex/(1<<exp))
            setIndex = setIndex % (1<<exp)
            exp -= 1
            curr_node.value = int(1 - dir)       # point node in the direction opp to that of the accessed node
            if (dir == 0):
                curr_node = curr_node.left
            else:
                curr_node = curr_node.right

    def getVictim(self):
        exp = self.numStages - 1
        curr_node = self.root.nodes[0]     # root node
        victIdx = 0
        for _ in range(self.numStages):
            dir = curr_node.value
            victIdx += dir*(1<<exp)
            exp -= 1
            curr_node.value = int(1 - dir)       # point node in the direction opp to that of the accessed node
            if (dir == 0):
                curr_node = curr_node.left
            else:
                curr_node = curr_node.right
        return victIdx

'''
# Test: Instantiate a tree
if __name__ == "__main__":
    testTree = Tree(4)
    testTree.traverse(0)
    testTree.traverse(2)
    testTree.traverse(11)
    for idx, stage in enumerate(testTree.stages):
        print(idx)
        for j, node in enumerate(stage.nodes):
            print(j, node.value)
    print(testTree.getVictim())
'''
