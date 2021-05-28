# from django.contrib.auth.models import User, Group
import enum
from rest_framework import serializers
from .models import KataBaku, TbSentimen, TbProduct

import requests
from bs4 import BeautifulSoup

import numpy as np
from itertools import cycle

import string
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    review = serializers.SerializerMethodField('getReview')
    # norm = serializers.SerializerMethodField('getNorm')

    def getReview(self, instance):
        url = instance.url
        url = url[:-1]
        request_object = self.context['request']
        jml = request_object.query_params.get('jumlah')
        
        review = []

        for i in range(int(jml)):
            page = requests.get(url+""+str(i+1))

            soup = BeautifulSoup(page.content, 'html.parser')
            for index, el in enumerate(soup.find_all("p", {"class": "text-content"})):
                # print("Proses ke-"+str(index))
                if index==6:
                # if True:                    
                    newText = self.PreprocessingFunction(el.text, jml)
                    review.append([el.text, newText])        

        return review

    def PreprocessingFunction(self, text, n):
        data = []

        # preprocessing
        text = self.CaseFolding(text)
        text = self.Tokenize(text)
        text = self.StandardWord(text)
        text = self.StopwordRemoval(text)
        text = self.Stemming(text)

        # tf-idf
        query = self.CreateQuery()
        tf = self.ComputeTF(query, text, n)

        return text
    
    def CaseFolding(self, text):
        return text.lower()

    def Tokenize(self, text):
        token = text.translate(str.maketrans('','',string.punctuation)).lower()
        return token.split(' ')
    
    def StandardWord(self, text):
        kataList = KataBaku.objects.all()
        kataTidakBakuList = list(KataBaku.objects.values_list('tidakbaku', flat=True))
        
        for i,j in enumerate(text):
            if str(text[i]) in kataTidakBakuList:
                text[i] = kataList[kataTidakBakuList.index(text[i])].baku

        return text

    def StopwordRemoval(self, text):
        factory = StopWordRemoverFactory()
        stopword = factory.create_stop_word_remover()
        
        text = ' '.join(text)
        removed = stopword.remove(text)

        return removed.split(' ')

    def Stemming(self, text):
        factory = StemmerFactory()
        stemmer = factory.create_stemmer()
        
        text = ' '.join([str(x) for x in text])
        katadasar = stemmer.stem(text)
        
        return katadasar    

    def CreateQuery(self):
        queryList = list(TbSentimen.objects.values_list('kata', flat=True))

        return queryList

    def ComputeTF(self, query, text, n):
        tokenText = text.split(' ')
        sentimenIndexList = list(TbSentimen.objects.values_list('sentimen', flat=True))
        
        dataQuery = {}

        for i in query:
            dataQuery[i] = 0

        for i, j in enumerate(tokenText):
            if i < len(tokenText)-1:
                # print(i, j, tokenText[i+1])
                if tokenText[i] in query:
                    # print(tokenText[i]+" -> "+sentimenIndexList[query.index(tokenText[i])])
                    dataQuery[tokenText[i]] += 1
                elif tokenText[i]+" "+tokenText[i+1] in query:
                    # print(tokenText[i]+" "+tokenText[i+1]+" -> "+sentimenIndexList[query.index(tokenText[i]+" "+tokenText[i+1])])
                    dataQuery[tokenText[i]+" "+tokenText[i+1]] += 1

        tf_document = {}
        for i in dataQuery:
            # tf_document[i] = 
            print(i, dataQuery[i])

        return dataQuery

    def LevenshteinDistance(self, s, t):
        rows = len(s)+1
        cols = len(t)+1
        dist = [[0 for x in range(cols)] for x in range(rows)]

        # source prefixes can be transformed into empty strings 
        # by deletions:
        for i in range(1, rows):
            dist[i][0] = i

        # target prefixes can be created from an empty source string
        # by inserting the characters
        for i in range(1, cols):
            dist[0][i] = i
            
        for col in range(1, cols):
            for row in range(1, rows):
                if s[row-1] == t[col-1]:
                    cost = 0
                else:
                    cost = 1
                dist[row][col] = min(dist[row-1][col] + 1,      # deletion
                                    dist[row][col-1] + 1,      # insertion
                                    dist[row-1][col-1] + cost) # substitution

        # for r in range(rows):
        #     print(dist[r])
    
        return dist[row][col]


    class Meta:
        model = TbProduct
        fields = ['id', 'nama_product', 'url', 'kategori', 'review']
