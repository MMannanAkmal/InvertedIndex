# Mohammad Mannan Akmal
# 17L-4240
# Information Retrieval - B
# Part 3 - Read Index

from sys import argv
from nltk import PorterStemmer

if len(argv) == 2:
    term = str(argv[1])
    term = term.strip()
    ps = PorterStemmer()
    stemmedTerm = ps.stem(term)
    checkTerm = "\"" + stemmedTerm + "\""
    with open("termids.txt", 'r') as termids:
        text = termids.read()
    lines = text.split()
    # lines.index(checkTerm)
    try:
        pos = lines.index(checkTerm)
    except ValueError:
        print("term does not exist in index")
    else:
        termID = lines[pos - 1]
        with open("term_index.txt", 'r') as index:
            indexText = index.read()
        indexText = indexText.split('\n')
        df = indexText[int(termID) - 1].split()[2]
        tf = indexText[int(termID) - 1].split()[1]
        print("Listing for term:\t", term)
        print("TERMID:\t", termID)
        print("Number of documents containing term:\t", df)
        print("Term frequency in corpus:\t", tf)
else:
    print("the number of arguments passed should be 1.")

# Read Index COMPLETE
