# Mohammad Mannan Akmal
# 17L-4240
# Information Retrieval - B
# Part 1 - Tokenizer

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
    # defining list of all tokens
    tokens = list()

    # create docids.txt with write permission
    docID = 0
    docfile = open("docids.txt", "w+")

    # read words from stoplist
    lineList = open("stoplist.txt").readlines()
    stopList = [i.strip() for i in lineList]

    # defining a stemmer
    ps = PorterStemmer()

    for filename in os.listdir(path):
        docID += 1
        # Using double quotes around the document name so integers dont interfere while searching
        # e.g. searching for the document name '4' gave wrong results
        docfile.write(str(docID) + "\t\"" + filename + "\"\n")

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
            # remove duplicates from stemmed terms
            stemmedTerms = list(dict.fromkeys(stemmedTerms))

            tokens = tokens + stemmedTerms

        if docID % 50 == 0:
            print("Documents read:\t" + str(docID) + "\r")

    # remove duplicates from all tokens
    tokens = list(dict.fromkeys(tokens))

    termID = 0
    termfile = open("termids.txt", "w+")

    for term in tokens:
        termID += 1
        # Using double quotes around the term so integers dont interfere while searching
        # e.g. searching for the term '42' gave wrong results
        termfile.write(str(termID) + "\t\"" + term + "\"\n")

else:
    # else display error
    print("Folder Does Not Exist")

# Tokenizer COMPLETE
