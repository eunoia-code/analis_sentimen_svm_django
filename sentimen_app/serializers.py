# from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import KataBaku, TbSentimen, TbProduct

import requests
from bs4 import BeautifulSoup

import numpy as np
import pandas as pd
import math

from sklearn import preprocessing
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

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
        n = int(jml)*10
        # n = 5

        query = self.CreateQuery()

        review = []
        sentimen = []
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

                    review.append([el.text, newText, ])

                    TFS = self.ComputeTF(query, newText, index)

                    tf.append(TFS[0])
                    sentimen.append(TFS[1])

        df = self.ComputeDF(query, tf, n)
        idf = self.ComputeIDF(query, df, n)
        tfidf = self.ComputeTFIDF(tf, idf)

        prepare_data = self.PrepareData(query, tfidf, sentimen)
        training_data = self.TrainingData(prepare_data)

        return {
            'comment': review,
            'sentimen': sentimen,
            # 'query': query,
            'tf': tf,
            # 'df': df,
            # 'idf': idf,
            # 'tfidf': tfidf,
            # 'prepare_data': prepare_data,
            # 'training_data': training_data
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
        queryList = TbSentimen.objects.values_list('kata', 'sentimen')

        return queryList

    def ComputeTF(self, query, text, index):
        tokenText = text.split(' ')
        
        dataQuery = {}
        dataSentimen = {}

        xquery = [x[0] for x in query]

        sentimen = {
            'positif': 0,
            'negatif': 0
        }

        for i in query:
            dataQuery[i[0]] = 0
            dataSentimen[i[0]] = i[1]

        check = False
        for i in range(len(tokenText)):
            newToken = ''

            if check:
                check = False
                continue
            
            if i < len(tokenText)-1:
                newToken = tokenText[i]+" "+tokenText[i+1]
                if newToken in xquery:
                    if index==1:
                        print(newToken)
                    dataQuery[newToken] += 1
                    sentimen[dataSentimen[newToken]] += 1
                    check = True
                    i+=1

            if not check:
                newToken = tokenText[i]
                if newToken in xquery:
                    dataQuery[newToken] += 1
                    sentimen[dataSentimen[newToken]] += 1

            if index==1:
                print(newToken)

        return [dataQuery, sentimen]

    def ComputeDF(self, query, tf, n):
        df = {}
        for i in query:
            df[i[0]] = 0

        doc_total = [0 for i in range(n)]

        for i in range(len(df)):
            for k in range(len(doc_total)):
                # print(tf[k][query[i][0]])
                if tf[k][query[i][0]]>0:
                    df[query[i][0]] += 1
                
        return df

    def ComputeIDF(self, query, df, n):
        idf = {}
        # xquery = [x[0] for x in query]

        for i in query:
            if df[i[0]]!=0:
                idf[i[0]] = math.log10(n/int(df[i[0]]))
            else:
                idf[i[0]] = 0
                
        return idf
    
    def ComputeTFIDF(self, tf, idf):
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

    def PrepareData(self, query, tfidf, sentimen):
        data = []
        
        index = 0
        for val in tfidf:
            temp = {}
            temp.update({'index' : index})

            for i, j in enumerate(val):
                # print(i,j, query[i][0])
                temp.update({query[i][0] : j})
        
            if sentimen[index]['positif'] >= sentimen[index]['negatif']:
                temp.update({'label' : 1})
            else:
                temp.update({'label' : 0})

            data.append(temp)

            index+=1

        return data

    def TrainingData(self, data):
        df = pd.DataFrame(data)
        X = df.drop(['index', 'label'], axis=1)
        y = df['label']
        idx = df['index']

        X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(X, y, idx, test_size = 0.20)

        svclassifier = SVC(kernel='linear')
        
        svclassifier.fit(X_train, y_train)

        y_pred = svclassifier.predict(X_test)

        X_combined = np.r_[X_train, X_test]
        y_combined = np.r_[y_train, y_pred]
        idx_combined = np.r_[idx_train, idx_test]

        classifier = []

        for i, j in enumerate(idx_combined):
            classifier.append({
                'index': j, 
                'class': y_combined[i], 
                "type": 'train' if j in idx_train else 'test'
            })

        classifier = sorted(classifier, key = lambda i: i['index'])
        
        return classifier

    def sortList(e):
        return e['index']

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
