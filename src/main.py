import argparse as ap
from inc.parser import inputParser

def args():
    parser = ap.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, metavar='file', help="Input file with requests", required=True)
    arg = parser.parse_args()
    return arg.input


def main():
    inFile = args()
    fileParser = inputParser(inFile)
    reqs = fileParser.parse()
    for req in reqs:
        req.print()

if __name__=="__main__":
    main()
    # print("Please check back later. In development")
