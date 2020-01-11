# Mohammad Mannan Akmal
# 17L-4240
# Information Retrieval - B
# Part 1 - Running Queries
import sys
from math import log
from sys import argv
from bs4 import BeautifulSoup
from nltk import PorterStemmer


def process_queries():
    queryList = []
    topicList = []
    ps = PorterStemmer()
    soup = BeautifulSoup(open("topics.xml", errors="ignore"), "html.parser")
    # read words from stoplist
    lineList = open("stoplist.txt").readlines()
    stopList = [i.strip() for i in lineList]
    for topic in soup.find_all('topic'):
        topicList.append(topic['number'])

    queries = soup.find_all("query")
    for q in queries:
        query = str(q.text)
        # converting to lowercase
        query = query.lower()
        # turn string into list of words
        words = query.split()
        # extracting words not in stoplist
        words = [i for i in words if i not in stopList]
        # stem the tokens
        stemmedWords = [ps.stem(w) for w in words]
        queryList.append(stemmedWords)

    retList = []
    for i in range(len(topicList)):
        tempPair = [topicList[i], queryList[i]]
        retList.append(tempPair)

    return retList


def calculate_totalterms_average_doc_length():
    totalTerms = 0
    totalDocs = 0
    with open("term_index.txt", "r") as index:
        for line in index:
            termFrequency = line.split()
            totalTerms = totalTerms + int(termFrequency[1])
    with open("docids.txt", "r") as docids:
        for line in docids:
            totalDocs += 1
    return totalTerms, totalTerms / totalDocs


def find_termID(word):
    with open("termids.txt", "r") as tids:
        ids = tids.read()
        ids = ids.split()
        try:
            pos = ids.index("\"" + word + "\"")
        except ValueError:
            return 0
        pos -= 1
        return ids[pos]


def calculate_relevant_doc_tfs(termID):
    dList = []
    deltaList = []
    docList = []
    termCounts = []
    with open("term_index.txt", "r") as index:
        for i, line in enumerate(index):
            if i == (int(termID) - 1):
                postings = line.split()
    postings = postings[3:]
    for p in postings:
        deltaList.append(p.split(",")[0])
        lastDoc = 0
    for delta in deltaList:
        lastDoc = lastDoc + int(delta)
        dList.append(lastDoc)
    for d in dList:
        if d not in docList:
            docList.append(d)
            termCounts.append(dList.count(d))

    return docList, termCounts


def calculate_doc_lengths(docList):
    with open('term_index.txt', 'r') as f:
        text = f.read()
    lines = text.split('\n')

    docDict = {}

    i = 0
    x = 1
    loading = "Calculating Document Lengths"

    for l in lines:
        if i % 250 == 0:
            loading = "Calculating Document Lengths" + "." * x
            x += 1
            x = x % 5
            sys.stdout.write('\r' + loading)
        i += 1
        lastID = 0
        postings = l.split()
        postings = postings[3:]
        for p in postings:
            p = p.split(',')
            checkID = int(p[0])
            checkID += lastID
            if checkID in docList:
                if checkID in docDict:
                    docDict[checkID] += 1
                else:
                    docDict[checkID] = 1

            lastID = checkID

    docLengths = []
    for a in docDict:
        docLengths.append(docDict[a])

    return docLengths


def calculate_total_occurrences(termID):
    with open("term_index.txt", "r") as index:
        for i, line in enumerate(index):
            if i == (int(termID) - 1):
                stats = line.split()
    return int(stats[1])


def get_doc_name(docID):
    with open("docids.txt", "r") as docids:
        text = docids.read()
    text = text.split()
    return text[(docID * 2) - 1]


def calculate_dirichlet_word(w):
    # N/(N+mu)*tfDoc + mu/(N+mu)*tfCorpus
    termID = find_termID(w)
    retList = []
    if int(termID) > 0:
        totalTerms, mu = calculate_totalterms_average_doc_length()
        totalOccurrences = calculate_total_occurrences(termID)
        tfCorpus = totalOccurrences / totalTerms
        docList, termCounts = calculate_relevant_doc_tfs(termID)
        docLengths = calculate_doc_lengths(docList)

        for i in range(len(docList)):
            N = docLengths[i]
            tfDoc = termCounts[i] / N
            leftVal = N / (N + mu)
            rightVal = mu / (N + mu)
            dirValue = (leftVal * tfDoc) + (rightVal * tfCorpus)
            tempPair = [docList[i], dirValue]
            retList.append(tempPair)

    return retList


def calculate_dirichlet(q):
    topic = q[0]
    query = q[1]
    scores = {}
    for word in query:
        scoreList = calculate_dirichlet_word(word)
        for score in scoreList:
            if score[0] not in scores.keys():
                scores[score[0]] = score[1]
            else:
                scores[score[0]] *= score[1]
    scores = sorted(scores.items(), key=lambda x: x[1])
    rank = 1
    with open("dir_score.txt", "a") as scoreFile:
        for s in scores:
            scoreFile.write(str(topic))
            scoreFile.write("\t")
            scoreFile.write(get_doc_name(s[0]))
            scoreFile.write("\t")
            scoreFile.write(str(rank))
            scoreFile.write("\t")
            scoreFile.write(str(s[1]))
            scoreFile.write("\trun1")
            scoreFile.write("\n")
            rank += 1


def calculate_doc_frequency(termID):
    with open("term_index.txt", "r") as index:
        for i, line in enumerate(index):
            if i == (int(termID) - 1):
                stats = line.split()
    return int(stats[2])


def calculate_bm25_word(w, tfq):
    k1 = 1.2
    k2 = 100
    b = 0.75

    termID = find_termID(w)
    retList = []

    if int(termID) > 0:
        totalTerms, avdl = calculate_totalterms_average_doc_length()
        docList, termCounts = calculate_relevant_doc_tfs(termID)
        docLengths = calculate_doc_lengths(docList)
        df = calculate_doc_frequency(termID)

        for i in range(len(docList)):
            dl = docLengths[i]
            D = 0

            with open("docids.txt", "r") as docids:
                for line in docids:
                    D += 1
            tfd = termCounts[i] / dl
            K = k1 * ((1 - b) + b * (float(dl) / float(avdl)))

            firstVal = log((D + 0.5) / (df + 0.5))
            secondVal = ((1 + k1) * tfd) / (K + tfd)
            thirdVal = ((1 + k2) * tfq) / (k2 + tfq)

            bm25Val = firstVal * secondVal * thirdVal

            tempPair = [docList[i], bm25Val]
            retList.append(tempPair)

    return retList


def calculate_bm25(q):
    topic = q[0]
    query = q[1]
    scores = {}
    for word in query:
        tfq = query.count(word) / len(query)
        scoreList = calculate_bm25_word(word, tfq)
        for score in scoreList:
            if score[0] not in scores.keys():
                scores[score[0]] = score[1]
            else:
                scores[score[0]] += score[1]
    scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    rank = 1
    for s in scores:
        with open("bm25_score.txt", "a") as scoreFile:
            scoreFile.write(str(topic))
            scoreFile.write("\t")
            scoreFile.write(get_doc_name(s[0]))
            scoreFile.write("\t")
            scoreFile.write(str(rank))
            scoreFile.write("\t")
            scoreFile.write(str(s[1]))
            scoreFile.write("\trun1")
            scoreFile.write("\n")
            rank += 1


# manually enter corpus path in function "calculate_doc_lengths(docList)"
# MAIN starts here
function = str(argv[1])
# echo command line argument

print("You entered:\t" + function)
queryListMain = process_queries()

if function.lower() == "bm25":
    print("Scoring Function 1: Okapi BM25")
    fHandle = open("bm25_score.txt", "w+")  # Make File
    fHandle.close()
    for queryM in queryListMain:
        calculate_bm25(queryM)
        sys.stdout.write('\r')
        print(queryM)
elif function.lower() == "dirichlet":
    print("Scoring Function 2: Dirichlet Smoothing")
    fHandle = open("dir_score.txt", "w+")  # Make File
    fHandle.close()
    for queryM in queryListMain:
        calculate_dirichlet(queryM)
        sys.stdout.write('\r')
        print(queryM)
else:
    print("Invalid scoring function entered.")
