#!/usr/bin/env python
#-*- coding: utf-8 -*-

__author__ = "Martin Kondra"

import csv
import StanfordFromNLTK
import json
import nltk
import pickle
import nltk.classify
from sklearn.svm import LinearSVC
from sklearn import cross_validation

data = pickle.load(open("TaggedCorpus.p", "rb")) #lista de diccionarios (sentences)

def order(relation):
    if relation[2]<relation[3]: #CARGO está antes de PER
        return 0
    else:
        return 1

def distance(relation):
    distance = abs((relation[2])-(relation[3]))
    return distance

def bag(relation):
    d = []
    empresa = relation[0]
    sentence_index = relation[1]
    CARGO_index = int(relation[2])
    PER_index = int(relation[3])
    sentence = data[empresa]['sentence']
    min_boundarie = min(CARGO_index, PER_index)
    max_boundarie = max(CARGO_index, PER_index)
    for tup in sentence[min_boundarie+1:max_boundarie]:
        token = tup[0]
        d.append(token)
    d = tuple(d)
    return d

def bag_of_entities(relation):
    d = []
    empresa = relation[0]
    sentence_index = relation[1]
    CARGO_index = int(relation[2])
    PER_index = int(relation[3])
    sentence = data[empresa]['sentence']
    min_boundarie = min(CARGO_index, PER_index)
    max_boundarie = max(CARGO_index, PER_index)
    for tup in sentence[min_boundarie+1:max_boundarie]:
        token = tup[1]
        d.append(token)
    d = tuple(d)
    return d

def cargo_ner(relation):
    empresa = relation[0]
    sentence_index = relation[1]
    CARGO_index = relation[2]
    PER_index = relation[3]
    sentence = data[empresa]['sentence']
    entitie = sentence[CARGO_index][1]
    return entitie

def people_ner(relation):
    empresa = relation[0]
    sentence_index = relation[1]
    PER_index = relation[3]
    sentence = data[empresa]['sentence']
    entitie = sentence[PER_index][1]
    return entitie

def entitie_in_bag(relation):
    entities = [u'PERS', 'CARGO']
    empresa = relation[0]
    sentence_index = relation[1]
    CARGO_index = int(relation[2])
    PER_index = int(relation[3])
    sentence = data[empresa]['sentence']
    min_boundarie = min(CARGO_index, PER_index)
    max_boundarie = max(CARGO_index, PER_index)
    for tup in sentence[min_boundarie + 1:max_boundarie]:
        if tup[1] in entities:
            return True
    return False

test_relation = ['ACO GROUP\xc2\xa0S.A.', '15', '0', '6', 'True', '', '', '', '']
test_relation = [test_relation[0], int(test_relation[1]), int(test_relation[2]), int(test_relation[3]), test_relation[4]]
#print bag(relation)
#print order(test_relation)
#print tokens_between(relation)
#print entities(relation)

def feature_extractor(relation):
    features = {"people_ner": people_ner(relation),
                "cargo_ner": cargo_ner(relation),
                "order": order(relation),
                "bag": bag(relation),
                "bag_of_entities": bag_of_entities(relation),
                "entitie_in_bag": entitie_in_bag(relation),
                "distance": distance(relation)
                }
    return features

#print feature_extractor(relation)

#CROSS VALIDATION
def cross_validate():
    print 'Cross validating...'
    accuracy = []
    training_set = feature_sets
    cv = cross_validation.KFold(len(training_set), n_folds=10)
    print cv
    for traincv, testcv in cv:
        classifier = maxEnt.train(training_set[traincv[0]:traincv[len(traincv)-1]])
        accuracy.append(nltk.classify.util.accuracy(classifier, training_set[testcv[0]:testcv[len(testcv)-1]]))
    for item in accuracy:
        print 'accuracy', item

if __name__ == "__main__":
    with open('anotacion.csv', 'rb') as csvfile:
        relations = csv.reader(csvfile, delimiter=',', quotechar='|')
        relations = [((relation[0], int(relation[1]), int(relation[2]), int(relation[3])), relation[4]) for relation in
                     relations]
        # print relations[1]
        #for item in relations:
        #    print item
        #    r=item[0]
        #    a = feature_extractor(r)
        feature_sets = [(feature_extractor(r), t) for (r, t) in relations]
        size = int(len(feature_sets) * 0.1)  # split train_set (90%) and test_set (10$)
        # train_set, test_set, devtest_set = featuresets[size:-(size)], featuresets[:size], featuresets[-(size):]
        train_set = feature_sets[size:]
        test_set = feature_sets[:size]

    print 'Training...'
    #naiveBayes = nltk.NaiveBayesClassifier.train(train_set)
    #print naiveBayes.show_most_informative_features(50)

    #decisionTree = nltk.DecisionTreeClassifier.train(train_set)
    #print decisionTree.pseudocode()

    maxEnt = nltk.MaxentClassifier.train(train_set,algorithm="iis")
    print maxEnt.show_most_informative_features(50)
    print 'Dumping pickle...'
    pickle.dump(maxEnt, open("maxEntClassifier.p", "wb"))

    #print('naiveBayesAccuracy: {:4.2f}'.format(nltk.classify.accuracy(naiveBayes, test_set)))
    #print('decisionTreeAccuracy: {:4.2f}'.format(nltk.classify.accuracy(decisionTree, test_set)))
    #print('maxEntAccuracy: {:4.2f}'.format(nltk.classify.accuracy(maxEnt, test_set)))

    #cross_validate()