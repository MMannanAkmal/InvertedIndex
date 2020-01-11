# MAIN starts here
import os
from sys import argv

from bs4 import BeautifulSoup


def calculate_precision_at_k(k, relevantDocList, scoreDocList):
    count = 0
    for i in range(k):
        if scoreDocList[i][0][1:-1] in relevantDocList:
            count += 1
    return count / k


def calculate_avg_precision(topic, relevantDocList, scoreDocList):
    sum1 = 0
    for sd in scoreDocList:
        if sd[0][1:-1] in relevantDocList:
            sum1 += calculate_precision_at_k(int(sd[1]), relevantDocList, scoreDocList)
    return sum1 / len(relevantDocList)

def get_relevant_docs_for_query(relevanceList, topic):
    retList = []
    for line in relevanceList:
        if line[0] == topic:
            if int(line[3]) > 0:
                retList.append(line[2])
    return retList


def get_score_docs_for_query(scoreList, topic):
    retList = []
    for line in scoreList:  # <topic> <docid> <rank> <score> run1
        if line[0] == topic:
            retList.append([line[1], line[2]])
    return retList


def get_relevant_judgements(qrel):
    retList = []
    with open(qrel, 'r') as r:
        results = r.readlines()
    for r in results:
        retList.append(r.split())
    return retList


def get_scores(path):
    retList = []
    with open(path, 'r') as s:
        results = s.readlines()
    for r in results:
        retList.append(r.split())
    return retList


def get_topic_list():
    retList = []
    soup = BeautifulSoup(open("topics.xml", errors="ignore"), "html.parser")
    for topic in soup.find_all('topic'):
        retList.append(topic['number'])
    return retList


if len(argv) == 3:
    qrel = str(argv[1])
    path = str(argv[2])
    if os.path.exists(qrel):
        if os.path.exists(path):
            relevancies = get_relevant_judgements(qrel);  # <topic> 0 <docid> <grade>
            scores = get_scores(path)  # <topic> <docid> <rank> <score> run1
            topicList = get_topic_list()

            fHandle = open("report_dir.txt", 'w+')
            fHandle.write("\t\tP@05 P@10 P@20 P@30\n\n")
            fHandle.close()

            avgPList = []

            for t in topicList:
                relevantDocs = get_relevant_docs_for_query(relevancies, t)
                scoreDocs = get_score_docs_for_query(scores, t)

                avgPList.append(calculate_avg_precision(t, relevantDocs, scoreDocs))

                with open("report_dir.txt", 'a') as report:
                    report.write(t)
                    report.write(":\t")
                    report.write("{0:.2f}".format((calculate_precision_at_k(5, relevantDocs, scoreDocs))))
                    report.write(" ")
                    report.write("{0:.2f}".format((calculate_precision_at_k(10, relevantDocs, scoreDocs))))
                    report.write(" ")
                    report.write("{0:.2f}".format((calculate_precision_at_k(20, relevantDocs, scoreDocs))))
                    report.write(" ")
                    report.write("{0:.2f}".format((calculate_precision_at_k(30, relevantDocs, scoreDocs))))
                    report.write("\n")
            total = 0
            for avgP in avgPList:
                total += avgP
            MAP = total/len(topicList)
            with open("report_dir.txt", 'a') as report:
                report.write("\nMean Average Precision:\t")
                report.write(str(MAP))
        else:
            print("score file does not exist.")
    else:
        print("relevance judgements file does not exist.")
else:
    print("the number of command line arguments passed should be 2.")
