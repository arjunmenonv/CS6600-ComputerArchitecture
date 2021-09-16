class mmu:
    def __init__(self):
        self.kfree_pages = range(0,256)
        self.ufree_pages = range(0,768)
