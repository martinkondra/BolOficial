#!/usr/bin/env python
#-*- coding: utf-8 -*-

__author__ = "Martin Kondra"

from features import *
import pickle

data = pickle.load(open("TaggedCorpus.p", "rb")) #lista de diccionarios (sentences)
maxEnt = pickle.load(open("maxEntClassifier.p", "rb")) #lista de diccionarios (sentences)

def sentence_candidates(empresa):
    candidates = []
    cargos = data[empresa]['index_cargos']
    people = data[empresa]['index_people']
    sentence = data[empresa]['index']
    for i in cargos:
        for j in people:
            t = (empresa, sentence, i, j)
            candidates.append(t)
    return candidates

def classify_candidates(empresa):
    cargos_true = []
    candidates = sentence_candidates(empresa)
    for item in candidates:
        is_rel = maxEnt.classify(feature_extractor(item))
        prob = maxEnt.prob_classify(feature_extractor(item)).prob('True')
        #print item, is_rel, prob
        if is_rel == 'True':
            cargos_true.append(item)
    return cargos_true

#classify_candidates('ROMANI VIAL\xc2\xa0S.A.')
#classify_candidates('BAZAR GROUP S.A.')

def true_relation2text(empresa):
    cargos_true = classify_candidates(empresa)
    true_relations = []
    for item in cargos_true:
        empresa = item[0]
        persona = data[empresa]['sentence'][item[2]][0]
        cargo = data[empresa]['sentence'][item[3]][0]
        t = (empresa, persona, cargo)
        true_relations.append(t)
    return true_relations

#print true_relation2text('BAZAR GROUP S.A.')

def all_true_relations():
    empresas = data.keys()
    for empresa in empresas:
        a = true_relation2text(empresa)
        for item in a:
            print item

all_true_relations()