#!/usr/bin/env python
#-*- coding: utf-8 -*-

__author__ = "Martin Kondra"

from nltk import StanfordNERTagger
from nltk.tag.stanford import StanfordPOSTagger
import nltk
import pickle
import re

# StanfordPOSTagger
stanford_dir = '/home/martinkondra/stanford-postagger-full-2016-10-31/'
modelfile = stanford_dir + 'models/spanish.tagger'
jarfile = stanford_dir + 'stanford-postagger.jar'
posTag = StanfordPOSTagger(model_filename=modelfile, path_to_jar=jarfile)

#RegexTagger
pattern = [(r'(Presidente( Provisional)?)','CARGO'),
           (r'(PRESIDENTE( PROVISIONAL)?)','CARGO'),
           (r'(presidente( provisional)?)','CARGO'),
           (r'(Provisional)','CARGO'),
           (r'(provisional)','CARGO'),
           (r'(Vicepresidente)','CARGO'),
           (r'(VICEPRESIDENTE)','CARGO'),
           (r'(Socio(s)?)','CARGO'),
           (r'(SOCIO(S)?)','CARGO'),
           (r'(Gerente(es)?)','CARGO'),
           (r'(General(es)?)','CARGO'),
           (r'(general(es)?)','CARGO'),
           (r'(\bDirector(es)?\b)','CARGO'),
           (r'(\bDIRECTOR(ES)?\b)','CARGO'),
           (r'(\bDirectora\b)','CARGO'),
           (r'(\bDIRECTORA\b)','CARGO'),
           (r'(S.*ndico(s)?)','CARGO'),
           (r'(Titular(es)?)','CARGO'),
           (r'(TITULAR(ES)?)','CARGO'),
           (r'(titular(es)?)','CARGO'),
           (r'(Suplente(s)?)','CARGO'),
           (r'(suplente(s)?)','CARGO'),
           (r'(Vocal(es)?)','CARGO'),
           (r'(Delegado(s)?)','CARGO')]
reTag = nltk.RegexpTagger(pattern)

# NERTagger
stanford_dir = '/home/martinkondra/StanfordNER2016-10-31/'
jarfile = stanford_dir + 'stanford-ner.jar'
modelfile = stanford_dir + 'classifiers/spanish.ancora.distsim.s512.crf.ser.gz'
stTag = StanfordNERTagger(model_filename=modelfile, path_to_jar=jarfile) #ver cómo hacer para solamente taguear PERS

def joinTaggers(tagged1, tagged2):
    for i, sentence in enumerate(tagged1):
        for j, item in enumerate(sentence):
           if tagged2[i][j][1] == 'CARGO':
                tagged1[i][j] = (tagged1[i][j][0],'CARGO')
    return tagged1

def get_continuous_chunks(tagged_sent):
    continuous_chunk = []
    current_chunk = []

    for token, tag in tagged_sent:
        if tag != "O":
            current_chunk.append((token, tag))
        else:
            if current_chunk: # if the current chunk is not empty
                continuous_chunk.append(current_chunk)
                current_chunk = []
    # Flush the final current_chunk into the continuous_chunk, if any.
    if current_chunk:
        continuous_chunk.append(current_chunk)
    return continuous_chunk

def sentence_with_continuus_entities(tagged_sent, entitie):
    continuous_chunk = []
    current_chunk = []
    preps = [u'de', u'della']
    for token, tag in tagged_sent:
        if tag == entitie or token in preps:
            current_chunk.append((token, tag))
        else:
            if current_chunk:  # if the current chunk is not empty
                continuous_chunk.append(current_chunk)
                current_chunk = []
            continuous_chunk.append((token, tag))
    # Flush the final current_chunk into the continuous_chunk, if any.
    if current_chunk:
        continuous_chunk.append(current_chunk)
    return continuous_chunk

def getCargos(sentence):
    cargos = []
    for item in sentence:
        if item[1] == 'CARGO':
            cargos.append(item[0])
    return cargos

def getPeople(sentence):
    people = []
    for item in sentence:
        if item[1] == 'PERS':
            people.append(item[0])
    return people

def hasPeopleAndCargos(sentence):
    has_people = False
    has_cargo = False
    for item in sentence:
        if item[1] == 'CARGO':
            has_cargo = True
        elif item[1].encode('utf8') == 'PERS':
            has_people = True
    if has_cargo and has_people:
        return True

def joinEntities(sentence, entitie):
    sent = []
    sentence = sentence_with_continuus_entities(sentence, entitie)
    #print sentence
    #sentence = sentence_with_continuus_cargos(sentence)
    for item in sentence:
        if type(item) is list:
            entitie = []
            tag = item[0][1]
            for i in item:
                entitie.append(i[0])
            entitie = ' '.join(entitie)
            item = (entitie, tag)
        sent.append(item)
    return sent

def getTokenIndex(token, sentence):
    #token = token
    for i, item in enumerate(sentence):
        if item[0] == unicode(token):
            return i

def getIndexesFromEntitieList(entitie_list, sentence):
    i = 0
    entities_index = []
    for item in entitie_list:
        for j in range(i,len(sentence)):
            if sentence[j][0] == unicode(item):
                print sentence[j][0], j
                i = j+1
                entities_index.append(j)
    return entities_index

def sentence2text(sentence):
    text = []
    for item in sentence:
        text.append(item[0])
    text = ' '.join(text)
    return text

def getData(i, sentence):
    cargos = getCargos(sentence)
    people = getPeople(sentence)
    sentenceData = {}
    sentenceData['index'] = i
    sentenceData['sentence'] = sentence
    sentenceData['text'] = sentence2text(sentence)
    sentenceData['cargos'] = cargos
    #sentenceData['index_cargos'] = [getTokenIndex(i, sentence) for i in sentenceData['cargos']]
    sentenceData['index_cargos'] = getIndexesFromEntitieList(cargos, sentence)
    sentenceData['people'] = people
    #sentenceData['index_people'] = [getTokenIndex(i, sentence) for i in sentenceData['people']]
    sentenceData['index_people'] = getIndexesFromEntitieList(people, sentence)
    sentenceData['empresa'] = ''
    return sentenceData

def print_data(sentenceData):
    for item in sentenceData.items():
        print item
    print '\n'

def processing(sample):
    sample = sample.decode('utf-8')
    sentences = nltk.sent_tokenize(sample)
    tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    #postagged_sentences = [posTag.tag(sentence) for sentence in tokenized_sentences]
    nerTagged_sentences = [stTag.tag(sentence) for sentence in tokenized_sentences]
    reTagged_sentences = [reTag.tag(sentence) for sentence in tokenized_sentences]
    allTags = joinTaggers(nerTagged_sentences, reTagged_sentences)
    sentence_continuos_people = [joinEntities(sentence, 'PERS') for sentence in allTags]
    sentence_continuos_cargos = [joinEntities(sentence, 'CARGO') for sentence in sentence_continuos_people]
    return sentence_continuos_cargos

sample = 'PRESIDENTE a PRESIDENTE a PRESIDENTE a Carlos Perez.'

def testOneSentence(sample):
    data = []
    sentence_continuos_cargos = processing(sample)
    for i, sentence in enumerate(sentence_continuos_cargos):
        if hasPeopleAndCargos(sentence):
            sentenceData = getData(i, sentence)
            data.append(sentenceData)
            print_data(sentenceData)

def run(file): #iterate over lines, each line is an acta
    data = {}
    with open(file) as f:
        for i, acta in enumerate(f):
            if len(acta)>33: #saltea lineas vacías y separadores
                try:
                    print i
                    empresa = re.search('^(.*?)S\.A\.(U\.)?', acta)
                    empresa = empresa.group(0)
                    sentence_continuos_cargos = processing(acta)
                    sentences = []
                    for i, sentence in enumerate(sentence_continuos_cargos):
                        if hasPeopleAndCargos(sentence):
                            sentenceData = getData(i, sentence)
                            sentenceData['empresa'] = empresa
                            # print_data(sentenceData)
                            sentences.append(sentenceData)
                    data[empresa] = sentences
                    print data[empresa]
                except:
                    print '---------- Got error in acta ', i, empresa
    #print 'Dumping pickle...'
    #pickle.dump(data, open("TaggedCorpus.p", "wb"))


if __name__ == "__main__":
    #run('actas_01-01-2016_01-09-2016.txt')
    #run('4nuevasActas.txt')
    testOneSentence(sample)



#BUGs
#INDEX DE CARGOS Y PERSONAS, agarra la primera ocurrencia de cada uno -> fc get_cargos_index(), terminar de armarla
#AGREGAR CARGO PLURAL O ALGO ASÍ?