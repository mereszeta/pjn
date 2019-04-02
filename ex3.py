import json

import matplotlib.pyplot as plt
from elasticsearch import Elasticsearch
from elasticsearch.helpers import scan


def print_idx():
    res = []
    aggregate = {}
    client = Elasticsearch(hosts=["localhost"])
    for dobj in scan(client,
                     query={"query": {"match_all": {}}, "stored_fields": ["_id"]},
                     index="idx", doc_type="_doc"):
        res.append(dobj["_id"])
        term = client.mtermvectors(index="idx", doc_type="_doc", body={"ids": [dobj["_id"]]},
                                   fields=["content"],
                                   term_statistics=True, positions=False, offsets=False)
        for key, value in term["docs"][0]["term_vectors"]["content"]["terms"].items():
            if key.isalpha() and len(key) >= 2:
                if key in aggregate:
                    aggregate[key] += value["term_freq"]
                else:
                    aggregate[key] = value["term_freq"]
    aggregate_list = [[k, v] for k, v in aggregate.items()]
    aggregate_list.sort(key=lambda x: x[1], reverse=True)
    with open("ex3_terms.json", "w", encoding='utf-8') as out:
        aggregate = {str(k.encode('utf-8'), encoding='utf-8'): v for k, v in aggregate.items()}
        json.dump(aggregate, out)
    fig = plt.figure()
    ax = fig.add_subplot(2, 1, 1)
    ax.plot(list(map(lambda x: aggregate_list.index(x), aggregate_list)),
            list(map(lambda x: x[1], aggregate_list)),
            color='blue')

    ax.set_yscale('log')

    plt.show()
    words_in_dict = []
    with open('polimorfologik-2.1.txt', 'r', encoding='utf-8') as dict:
        lines = dict.readlines()
        for line in lines:
            words_in_dict.append(line.split(';')[1])
    print(words_in_dict)
    res5 = []
    res6 = []
    res7 = []
    for aggregate in aggregate_list:
        if aggregate[0] not in words_in_dict:
            res5.append(aggregate)
    res6 = res5[0:30]
    res7 = list(filter(lambda x: x[1] == 3, res5))[0:30]
    print(res5)
    print(res6)
    print(res7)
    aggregate_list = list(filter(lambda x: x not in res5, aggregate_list))
    lev_list = []
    for r in res7:
        lev_word = ""
        lev_score = len(r[0])
        for agg in list(reversed(aggregate_list)):
            sc = levenshtein_dist(r[0], agg[0])
            if sc <= lev_score:
                lev_word = agg[0]
                lev_score = sc
        lev_list.append([r[0], lev_word, lev_score])
    print(lev_list)


def levenshtein_dist(first, second):
    matrix = []
    for i in range(0, len(first) + 1):
        row = []
        for j in range(len(second) + 1):
            if i == 0:
                elem = j
            elif j == 0:
                elem = i
            else:
                elem = 0
            row.append(elem)
        matrix.append(row)
    # for every element in matrix (size(first)+1)x(size(second)+1)
    # if previous letters are the same just take element on diagonal(coordinates x-1,y-1)
    # if previous letters are the same take minimum of element on diagonal, on the left and on the top incremented by 1
    # return lower right corner of matrix(going left to right and top to bottom)
    for i in range(1, len(first) + 1):
        for j in range(1, len(second) + 1):
            if first[i - 1] == second[j - 1]:
                matrix[i][j] = matrix[i - 1][j - 1]
            else:
                matrix[i][j] = min(matrix[i - 1][j - 1] + 1, matrix[i][j - 1] + 1, matrix[i - 1][j] + 1)
    return matrix[len(first)][len(second)]


if __name__ == "__main__":
    print_idx()
