from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import KataBaku, TbProduct

import requests
from bs4 import BeautifulSoup

import numpy as np

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

import string
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

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
                # if index==0:
                if True:                    
                    newText = self.PreprocessingFunction(el.text)
                    review.append([el.text, newText])
                

        return review

    def PreprocessingFunction(self, text):
        data = []

        text = self.CaseFolding(text)
        text = self.Tokenize(text)
        text = self.StandardWord(text)
        text = self.StopwordRemoval(text)
        text = self.Stemming(text)

        # Call Kata Dasar Data
        # kataDasar = TbKatadasar.objects.all()
        # kd_list = list(kataDasar)

        # splitComment = obj.split()
        # for word in splitComment:
        #     for kd in kd_list:
        #         l_distance = self.LevenshteinDistance(word, str(kd))
        #         print(word, str(kd), l_distance, end="\n")
        #     print("\n")

        return text
    
    def CaseFolding(self, text):
        return text.lower()

    def Tokenize(self, text):
        token = text.translate(str.maketrans('','',string.punctuation)).lower()
        return word_tokenize(token)

    def StopwordRemoval(self, text):
        listStopword =  set(stopwords.words('indonesian'))

        removed = []
        for t in text:
            if t not in listStopword:
                removed.append(t)
        
        return removed

    def StandardWord(self, text):
        kataList = KataBaku.objects.all()
        kataTidakBakuList = list(KataBaku.objects.values_list('tidakbaku', flat=True))

        for i,j in enumerate(text):
            if str(text[i]) in kataTidakBakuList:
                text[i] = kataList[kataTidakBakuList.index(text[i])].baku

        return text

    def Stemming(self, text):
        factory = StemmerFactory()
        stemmer = factory.create_stemmer()
        
        text = ' '.join([str(x) for x in text])
        katadasar = stemmer.stem(text)
        
        return katadasar    

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
