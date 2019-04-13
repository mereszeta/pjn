import http.client as client
import os
import nltk
import ex4


def ex5():
    con = client.HTTPConnection('localhost', port=9200)
    bigrams_dict = {}
    tokens_dict = {}
    for filename in os.listdir(os.getcwd() + '/ustawy'):
        with open('./ustawy/' + filename, 'r', encoding='utf-8') as file:
            text = "".join(file.readlines())
            text = text.replace('\\n', '').lower()
            con.request(method="POST", url="", body=text.encode('utf-8'))
            res = con.getresponse().readlines()
            tokens = []
            for i in range(0, len(res)):
                line = res[i].decode('utf-8')
                line = line.split('\t')
                if 'disamb\n' in line:
                    lemm = line[2].split(':')[0]
                    tokens.append(line[1] + ":" + lemm)
            for token in tokens:
                if token.split(":")[0].isalpha():
                    if token in tokens_dict:
                        tokens_dict[token] += 1
                    else:
                        tokens_dict[token] = 1
            bigrams = list(nltk.bigrams(tokens))
            bigrams = list(
                filter(lambda x: (x[0].split(":")[0].isalpha()) and (x[1].split(":")[0].isalpha()), bigrams))
            for bigram in bigrams:
                if bigram in bigrams_dict:
                    bigrams_dict[bigram] += 1
                else:
                    bigrams_dict[bigram] = 1
    llr = ex4.llr(bigrams_dict, tokens_dict)
    print(list(filter(lambda x: x[0][0].split(':')[1] == 'subst' and x[0][1].split(':')[1] in ["adj", "subst"], llr))[
          0:50])


if __name__ == "__main__":
    ex5()
