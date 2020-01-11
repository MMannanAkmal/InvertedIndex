# Mohammad Mannan Akmal
# 17L-4240
# Information Retrieval - B
# Part 2 - Inverted Index w/ Dictionary

import os
import re
import string
from sys import argv
from typing import Dict, List

from bs4 import BeautifulSoup
from nltk import PorterStemmer

# gets path from command line argument with whitespaces and turns list into str
path = ' '.join(argv[1:])
# echo input
print("You entered:\t" + path)

# check if path exits
if os.path.exists(path):
    # read words from stoplist
    lineList = open("stoplist.txt").readlines()
    stopList = [i.strip() for i in lineList]

    # defining a stemmer
    ps = PorterStemmer()

    # opening docids.txt
    dfile = open("docids.txt", "r")
    dfilecontent = dfile.read()
    dlist = dfilecontent.split()

    # opening termids.txt
    tfile = open("termids.txt", "r")
    tfilecontent = tfile.read()
    tlist = tfilecontent.split()

    tcounter = 0
    prevDoc = 0
    inverted: Dict[int, List[int]] = {}

    for filename in os.listdir(path):
        # finding docID
        dpos = dlist.index("\"" + filename + "\"")
        docID = int(dlist[dpos - 1])

        # adding filename to the path
        fpath = path + "\\" + filename

        # making the soup :P (opening file)
        soup = BeautifulSoup(open(fpath, errors="ignore"), "html.parser")
        body = soup.find("body")

        if body:
            # remove all unrelated text
            for extras in body(["style", "script"]):
                extras.extract()
            # removing non-ascii characters
            cleantext = ''.join(character for character in body.text if ord(character) < 128)
            # removing punctuation
            regex = re.compile('[%s]' % re.escape(string.punctuation))
            cleantext = re.sub(regex, '', cleantext)
            # standardizing whitespace
            cleantext = re.sub(r'\s+', ' ', cleantext)
            # converting to lowercase
            cleantext = cleantext.lower()
            # removing whitespace
            cleantext = cleantext.strip()
            # turn string into list of words
            textlist = cleantext.split()
            # extracting words not in stoplist
            textlist = [i for i in textlist if i not in stopList]
            # stem the tokens
            stemmedTerms = [ps.stem(term) for term in textlist]

            tcounter = 0

            for token in stemmedTerms:
                tcounter += 1
                # find termID
                tpos = tlist.index("\"" + token + "\"")
                termID = int(tlist[tpos - 1])

                if termID not in inverted:
                    inverted[termID] = [0, 0]

                # increment occurrence in corpus
                inverted[termID][0] += 1
                inverted[termID].append(str(docID) + "," + str(tcounter))

    checkList = list()
    for post in inverted:
        # calculate DF
        checkList.clear()
        for i in range(len(inverted[post]) - 2):
            p = inverted[post][i + 2]
            p = p.split(',')[0]
            if p not in checkList:
                checkList.append(p)
        inverted[post][1] = len(checkList)
        # delta encoding
        checkList.clear()
        for i in reversed(range(len(inverted[post]) - 3)):
            p = inverted[post][i + 3]
            other = p.split(',')[1]
            other = "," + other
            p = p.split(',')[0]
            q = inverted[post][i + 3 - 1]
            q = q.split(',')[0]
            inverted[post][i + 3] = str(int(p) - int(q)) + other


    iiFile = open("term_index_dict.txt", "w+")
    for i in inverted:
        iiFile.write(str(i) + " ")
        postings = inverted.get(i)
        counter = 0
        for element in postings:
            iiFile.write(str(element))
            counter += 1
            if counter != len(postings):
                iiFile.write(" ")

        iiFile.write("\n")

else:
    # else display error
    print("Folder Does Not Exist")

# Inverted Index with Dictionary COMPLETE
