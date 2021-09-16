import argparse as ap
from inc.opts import *
from inc.parser import inputParser

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
