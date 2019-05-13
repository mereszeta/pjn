import logging
import math
import os
import csv
import re

from sklearn.metrics import classification_report
from sklearn.svm import LinearSVC
from sklearn.multiclass import OneVsRestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.pipeline import Pipeline
from flair.data_fetcher import NLPTaskDataFetcher
from flair.embeddings import WordEmbeddings, FlairEmbeddings, DocumentRNNEmbeddings
from flair.models import TextClassifier
from flair.trainers import ModelTrainer
from pathlib import Path
import random


def read_file(file): return file.readlines()


def read_updates():
    return read_directory('/ustawy_copy/first/', 'updates')


def read_standalones():
    return read_directory('/ustawy_copy/second/', 'standalones')


def read_directory(dirname, tag):
    bills = []
    for filename in os.listdir(os.getcwd() + dirname):
        with open('.' + dirname + filename, 'r', encoding='utf-8') as file:
            bills.append((read_file(file), tag))
    return bills


def divide_dataset(dataset):
    train, rest = train_test_split(dataset, train_size=0.6)
    test, validation = train_test_split(rest, test_size=.5)
    return train, test, validation


def full_content(lines):
    text = ''.join(lines)
    text = re.sub('\n', '', text)
    return re.sub(r' {2,}', ' ', text)


def ten_percents(lines): return ''.join(random.sample(lines, math.floor(len(lines) / 10))).replace('\\n', '')


def ten_lines(lines): return ''.join(random.sample(lines, 10 if len(lines) >= 10 else len(lines))).replace('\\n', '')


def one_line(lines): return random.choice(lines) if len(lines) != 0 else ""


def grid_search_svm():
    pipeline = Pipeline([('tfidf', TfidfVectorizer()), ('clf', OneVsRestClassifier(LinearSVC()))])
    parameters = {
        'tfidf__max_df': (0.25, 0.5, 0.75),
        'tfidf__ngram_range': [(1, 1), (1, 2), (1, 3)],
        "clf__estimator__C": [0.01, 0.1, 1],
        "clf__estimator__class_weight": ['balanced', None],
    }
    return GridSearchCV(pipeline, parameters, cv=2, n_jobs=2, verbose=3)


def prepare_datasets():
    updates = read_updates()
    standalones = read_standalones()
    train_u, test_u, validation_u = divide_dataset(updates)
    train_s, test_s, validation_s = divide_dataset(standalones)
    train = train_u + train_s
    test = test_u + test_s
    validation = validation_u + validation_s
    return train, test, validation


def get_x(dataset, func): return list(map(lambda x: func(x[0]), dataset))


def get_y(dataset): return list(map(lambda x: x[1], dataset))


def train_and_predict(train, test, func):
    train_x = get_x(train, func)
    train_y = get_y(train)
    test_x = get_x(test, func)
    test_y = get_y(test)
    grid_search = grid_search_svm().fit(train_x, train_y)
    best_clf = grid_search.best_estimator_
    predictions = best_clf.predict(test_x)
    return classification_report(test_y, predictions)


def write_csv(fileName, array, func):
    arr_mapped = list(map(lambda x: ['__label__' + x[1], func(x[0])], array))
    with open(fileName, 'w', encoding='utf-8') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(arr_mapped)


def train_flair(method_name):
    corpus = NLPTaskDataFetcher.load_classification_corpus(Path('./'), test_file='test_' + method_name + '.csv',
                                                           dev_file='validation_' + method_name + '.csv',
                                                           train_file='train_' + method_name + '.csv')
    word_embeddings = [WordEmbeddings('pl'), FlairEmbeddings('polish-forward'),
                       FlairEmbeddings('polish-backward')]
    document_embeddings = DocumentRNNEmbeddings(word_embeddings, hidden_size=512, reproject_words=True,
                                                reproject_words_dimension=256)
    classifier = TextClassifier(document_embeddings, label_dictionary=corpus.make_label_dictionary(), multi_label=False)
    trainer = ModelTrainer(classifier, corpus)
    try:
        trainer.train('./', max_epochs=10)
    except UnicodeError:
        pass


def main():
    # logging.getLogger('flair').setLevel(logging.ERROR)
    # train, test, validation = prepare_datasets()
    # for method in [full_content, ten_percents, ten_lines, one_line]:
    #     write_csv('test_' + method.__name__ + '.csv', test, method)
    #     write_csv('train_' + method.__name__ + '.csv', train, method)
    #     write_csv('validation_' + method.__name__ + '.csv', validation, method)
    #     res = train_and_predict(train, test, method)
    #     with open('res.txt', 'a', encoding='utf-8') as f:
    #         f.write(res)
    train_flair('one_line')



if __name__ == '__main__':
    main()
