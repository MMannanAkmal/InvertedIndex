# Mohammad Mannan Akmal
# 17L-4240
# Information Retrieval - B
# Part 2 - Inverted Index

import os
import re
import string
from sys import argv
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
    allpostings = list()
    docpostings = list()

    # defining list of all tokens
    tokens = list()

    count = 0   # REMOVE LATER

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

            tokens = tokens + stemmedTerms

            tcounter = 0
            for token in stemmedTerms:
                tcounter += 1
                # find termID
                tpos = tlist.index("\"" + token + "\"")
                termID = int(tlist[tpos - 1])
                posting = [termID, docID, tcounter]
                docpostings.append(posting)

            allpostings = allpostings + docpostings
            docpostings.clear()

        # REMOVE LATER
        count += 1
        if count % 50 == 0:
            print(count)

    # sorting postings on termID then docID then position
    allpostings.sort(key=lambda l: [l[0], l[1], l[2]])

    # remove duplicates from all tokens
    tokens = list(dict.fromkeys(tokens))

    inverted = [[0] * 3 for i in range(len(tokens))]

    prevDoc = 0
    prevTerm = 0

    iiFile = open("term_index.txt", "w+")

    # creating inverted index
    for posting in allpostings:
        tID = int(posting[0])
        inverted[tID - 1][0] = tID  # set first element of list as termID
        inverted[tID - 1][1] += 1  # increment occurrences in second element of list

        # delta encoding check
        if inverted[tID - 1][1] > 1:
            inverted[tID - 1].append(str(posting[1] - prevDoc) + "," + str(posting[2]))
        else:
            inverted[tID - 1].append(str(posting[1]) + "," + str(posting[2]))

        if prevTerm != posting[0]:
            inverted[tID - 1][2] += 1  # increment docs in second element of list
            prevDoc = posting[1]
        else:
            if prevDoc != posting[1]:
                inverted[tID - 1][2] += 1  # increment docs in second element of list
                prevDoc = posting[1]

        prevTerm = posting[0]

    for tuple in inverted:
        i = 0
        tupleID = tuple[0]
        while i < len(inverted[tupleID - 1]):
            if (i + 1) == len(inverted[tupleID - 1]):
                iiFile.write(str(inverted[tupleID - 1][i]))
            else:
                iiFile.write(str(inverted[tupleID - 1][i]) + " ")
            i += 1
        iiFile.write("\n")
else:
    # else display error
    print("Folder Does Not Exist")

# Inverted Index without Dictionary COMPLETE
