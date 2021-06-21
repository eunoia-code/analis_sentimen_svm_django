# from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import KataBaku, TbSentimen, TbProduct

import requests
from bs4 import BeautifulSoup

import numpy as np
import math

import string
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    review = serializers.SerializerMethodField('getReview')

    def getReview(self, instance):
        url = instance.url
        url = url[:-1]
        request_object = self.context['request']
        jml = request_object.query_params.get('jumlah')
        # n = int(jml)
        n = 3

        query = self.CreateQuery()
        review = []
        tf = []
        df = []
        idf = []
        tfidf = []

        for i in range(int(jml)):
            page = requests.get(url+""+str(i+1))

            soup = BeautifulSoup(page.content, 'html.parser')

            for index, el in enumerate(soup.find_all("p", {"class": "text-content"})):
                if index < n:                    
                    print("Proses ke-"+str(index))
                    
                    newText = self.PreprocessingFunction(el.text)

                    review.append([el.text, newText])

                    calcTF = self.ComputeTF(query, newText)
                    
                    tf.append(calcTF)

        df = self.ComputeDF(query, tf, n)
        idf = self.ComputeIDF(query, df, n)
        tfidf = self.ComputeTFIDF(tf, idf, n)

        print(tfidf)

        return {
            'comment': review,
            # 'tf': tf,
            # 'df': df,
            # 'idf': idf,
            # 'tfidf': tfidf
        }

    def PreprocessingFunction(self, text):
        # preprocessing
        text = self.CaseFolding(text)
        text = self.Tokenize(text)
        text = self.StandardWord(text)
        text = self.StopwordRemoval(text)
        text = self.Stemming(text)

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

    def ComputeTF(self, query, text):
        tokenText = text.split(' ')
        # sentimenIndexList = list(TbSentimen.objects.values_list('sentimen', flat=True))
        
        dataQuery = {}

        for i in query:
            dataQuery[i] = 0

        for i in range(len(tokenText)):
            if i < len(tokenText)-1:
                # print(i, j, tokenText[i+1])
                if tokenText[i] in query:
                    # print(tokenText[i]+" -> "+sentimenIndexList[query.index(tokenText[i])])
                    dataQuery[tokenText[i]] += 1
                elif tokenText[i]+" "+tokenText[i+1] in query:
                    # print(tokenText[i]+" "+tokenText[i+1]+" -> "+sentimenIndexList[query.index(tokenText[i]+" "+tokenText[i+1])])
                    dataQuery[tokenText[i]+" "+tokenText[i+1]] += 1

        return dataQuery

    def ComputeDF(self, query, tf, n):
        df = {}
        for i in query:
            df[i] = 0

        doc_total = [0 for i in range(n)]

        for i in range(len(df)):
            for k in range(len(doc_total)):
                if tf[k][query[i]]>0:
                    df[query[i]] += 1
                
        return df

    def ComputeIDF(self, query, df, n):
        idf = {}
        for i in query:
            if df[i]!=0:
                idf[i] = math.log10(n/int(df[i]))
            else:
                idf[i] = 0
                
        return idf
    
    def ComputeTFIDF(self, tf, idf, n):
        tfidf = []

        for i in range(len(tf)):
            # temp_W = {}
            temp_W = []
            for j in tf[i]:
                # print(i, j, tf[i][j], idf[j])
                # temp_W[j] = tf[i][j] * idf[j]
                temp_W.append(tf[i][j] * idf[j])
            
            # tfidf.append(temp_W)
            tfidf.append(temp_W)

        return tfidf

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
