
DIRECTORY_MASK = (1<<10)-1
TABLE_MASK = (1<<10)-1
OFFSET_MASK = (1<<12)-1

def translate(va):
    directory_offset = (va >> 22) & DIRECTORY_MASK
    table_offset = (va >> 12) & TABLE_MASK
    page_offset = (va) & OFFSET_MASK
    return [directory_offset, table_offset, page_offset]

if __name__=="__main__":
    print(translate(0xf31db3b))
