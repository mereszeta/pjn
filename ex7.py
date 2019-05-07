from gensim.models import Word2Vec, KeyedVectors
from gensim.test.utils import datapath
from matplotlib import pyplot
from sklearn.manifold import TSNE
import numpy as np


def main():
    # words = [['sąd::noun', 'wysoki::adj'], ['trybunał::noun', 'konstytucyjny::adj'], ['kodeks::noun', 'cywilny::adj'],
    #          'kpk::noun',
    #          ['sąd::noun', 'rejonowy::adj'], 'szkoda::noun', 'wypadek::noun', 'kolizja::noun',
    #          ['szkoda::noun', 'majatkowy::adj'],
    #          'nieszczęście::noun', 'rozwód::noun']
    model = KeyedVectors.load_word2vec_format("skip_gram_v100m8.w2v.txt", binary=False)
    # res = []
    # for word in words:
    #     try:
    #         res.append([word, model.wv.most_similar(positive=word)])
    #     except KeyError:
    #         res.append([word, []])
    # print(res)
    # equations = [
    #     ('ne#Sąd_Najwyższy::noun', 'konstytucja::noun', 'kpc::noun'),
    #     ('pasażer::noun', 'kobieta::noun', 'mężczyzna::noun'),
    #     ('samochód::noun', 'rzeka::noun', 'droga::noun')
    # ]
    # res = []
    # for equation in equations:
    #     print(equation)
    #     vec = model[equation[0]] + model[equation[1]] - model[equation[2]]
    #     res.append([equation, model.similar_by_vector(vector=vec)[0:5]])
    # print(res)
    words = ['szkoda::noun', 'strata::noun', 'uszczerbek::noun', 'szkoda_majątkowa::noun',
             'uszczerbek_na_zdrowiu::noun', 'krzywda::noun', 'niesprawiedliwość::noun', 'nieszczęście::noun']
    tsne = TSNE(2)
    vecs = []
    rand_words = np.random.choice(list(model.vocab.keys()), 1000)
    rand_words = np.append(rand_words, words)
    for word in rand_words:
        try:
            vecs.append(model.get_vector(word))
        except KeyError:
            pass
    res = tsne.fit_transform(vecs)
    print(res)
    pyplot.scatter(res[:len(words), 0], res[:len(words), 1], c='red')
    pyplot.scatter(res[len(words):, 0], res[len(words):, 1], c='yellow')
    pyplot.show()


if __name__ == '__main__':
    main()
