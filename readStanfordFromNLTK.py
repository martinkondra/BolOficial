#!/usr/bin/env python
#-*- coding: utf-8 -*-

__author__ = "Martin Kondra"

import pickle
import codecs
import snowballstemmer


data = pickle.load(open("TaggedCorpus.p", "rb")) #lista de diccionarios (sentences)
output = codecs.open("output-sentences.txt", "w", "utf-8")

print 'Sentences with people and cargos: ', len(data), '\n'

for item in data.items():
    print item[0]
    output.write(item[0].decode('utf-8'))
    output.write('\n')
    for i in item[1].items():
        #print i
        output.write(str(i))
        output.write('\n')
    output.write('\n')
