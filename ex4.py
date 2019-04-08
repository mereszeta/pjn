import nltk
import os
import math


def f():
    # nltk.download("punkt")
    bigrams_dict = {}
    tokens_dict = {}
    for filename in os.listdir(os.getcwd() + '/ustawy'):
        with open('./ustawy/' + filename, 'r', encoding='utf-8') as file:
            text = "".join(file.readlines()).lower()
            text = text.replace('\\n', '')
            nltk_tokens = nltk.word_tokenize(text, language="Polish")
            for token in list(filter(lambda x: x.isalpha(), nltk_tokens)):
                if token in tokens_dict:
                    tokens_dict[token] += 1
                else:
                    tokens_dict[token] = 1
        partial = list(filter(bigrams_filter, list(nltk.bigrams(nltk_tokens))))
        for p in partial:
            if p in bigrams_dict:
                bigrams_dict[p] += 1
            else:
                bigrams_dict[p] = 1
    with open('ex4_bigrams.txt', 'w', encoding='utf-8') as res:
        res.write("".join([str(k) + ', ' + str(v) for k, v in bigrams_dict.items()]))
    print(pmi(bigrams_dict, tokens_dict)[0:30])
    print(llr(bigrams_dict, tokens_dict)[0:30])


def bigrams_filter(bigram):
    return bigram[0].isalpha() and bigram[1].isalpha() and (len(bigram[0]) > 1 or len(bigram[1]) > 1)


def get_total_count(provided_dict):
    res = 0
    for k, v in provided_dict.items():
        res += v
    return res


def pmi(bigrams, tokens):
    total_bigrams_count = get_total_count(bigrams)
    total_tokens_count = get_total_count(tokens)
    res = []
    for k, v in bigrams.items():
        pair_prob = v / total_bigrams_count
        first_prob = tokens[k[0]] / total_tokens_count
        second_prob = tokens[k[1]] / total_tokens_count
        pmi = math.log2(pair_prob / (first_prob * second_prob))
        res.append((k, pmi))
    res.sort(key=lambda x: x[1], reverse=True)
    return res


def llr(bigrams, tokens):
    total_tokens_count = get_total_count(tokens)
    res = []
    for k, v in bigrams.items():
        pair_count = v
        first_not_second = tokens[k[1]] - v
        second_not_first = tokens[k[0]] - v
        nor_second_nor_first = total_tokens_count - tokens[k[1]] - tokens[k[0]]
        llr = 2 * (pair_count + first_not_second + second_not_first + nor_second_nor_first) * (
                h([pair_count, first_not_second, second_not_first, nor_second_nor_first]) - h(
            [pair_count + second_not_first, first_not_second + nor_second_nor_first]) - h(
            [pair_count + first_not_second, second_not_first + nor_second_nor_first]))
        res.append((k, llr))
    res.sort(key=lambda x: x[1], reverse=True)
    return res


def h(arr):
    N = sum(arr)
    return sum([elem / N * math.log2((elem / N) + (1 if elem == 0 else 0)) for elem in arr])


if __name__ == "__main__":
    f()
