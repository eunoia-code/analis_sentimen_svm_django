import numpy as np
import pandas as pd
import math

from .models import KataBaku, TbSentimen, TbProduct

from sklearn import preprocessing
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

import string
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

class the_function:

    def PreprocessingFunction(self, text):
        # preprocessing
        text = self.CaseFolding(text)
        text = self.Tokenize(text)
        text = self.StandardWord(text)
        text = self.StopwordRemoval(text)
        text = self.Stemming(text)

        return text
    
    def CaseFolding(text):
        return text.lower()

    def Tokenize(text):
        token = text.translate(str.maketrans('','',string.punctuation)).lower()
        return token.split(' ')
    
    def StandardWord(text):
        kataList = KataBaku.objects.all()
        kataTidakBakuList = list(KataBaku.objects.values_list('tidakbaku', flat=True))
        
        for i,j in enumerate(text):
            if str(text[i]) in kataTidakBakuList:
                text[i] = kataList[kataTidakBakuList.index(text[i])].baku

        return text

    def StopwordRemoval(text):
        factory = StopWordRemoverFactory()
        stopword = factory.create_stop_word_remover()
        
        text = ' '.join(text)
        removed = stopword.remove(text)

        return removed.split(' ')

    def Stemming(text):
        factory = StemmerFactory()
        stemmer = factory.create_stemmer()
        
        text = ' '.join([str(x) for x in text])
        katadasar = stemmer.stem(text)
        
        return katadasar    

    def CreateQuery():
        queryList = TbSentimen.objects.values_list('kata', 'sentimen')

        return queryList

    def ComputeTF(query, text, index):
        tokenText = text.split(' ')
        
        dataQuery = {}

        xquery = [x[0] for x in query]

        for i in query:
            dataQuery[i[0]] = 0

        check = False
        for i in range(len(tokenText)):
            newToken = ''

            if check:
                check = False
                continue
            
            if i < len(tokenText)-1:
                newToken = tokenText[i]+" "+tokenText[i+1]
                if newToken in xquery:
                    # if index==1:
                    #     print(newToken)
                    dataQuery[newToken] += 1
                    check = True
                    i+=1

            if not check:
                newToken = tokenText[i]
                if newToken in xquery:
                    dataQuery[newToken] += 1

            # if index==1:
            #     print(newToken)

        return dataQuery

    def ComputeDF(query, tf, n):
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

    def ComputeIDF(query, df, n):
        idf = {}
        # xquery = [x[0] for x in query]

        for i in query:
            if df[i[0]]!=0:
                idf[i[0]] = math.log10(n/int(df[i[0]]))
            else:
                idf[i[0]] = 0
                
        return idf
    
    def ComputeTFIDF(tf, idf):
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

    def PrepareData(query, tfidf, sentimen):
        data = []
        
        index = 0
        for val in tfidf:
            temp = {}
            temp.update({'index' : index})

            for i, j in enumerate(val):
                # print(i,j, query[i][0])
                temp.update({query[i][0] : j})
        
            if sentimen[index] == 'positif':
                temp.update({'label' : 1})
            else:
                temp.update({'label' : 0})

            data.append(temp)

            index+=1

        return data

    def TrainingData(data):
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
                'index': str(j), 
                'class': str(y_combined[i]), 
                "type": 'train' if j in idx_train else 'test'
            })

        classifier = sorted(classifier, key = lambda i: i['index'])
        
        return classifier

    def sortList(e):
        return e['index']

    def __new__(self, data, tipe):
        review = []
        sentimen = []
        tf = []
        df = []
        idf = []
        tfidf = []
        # training_data = []

        query = self.CreateQuery()

        if tipe=='from_db':
            total_row = len(data)
            n = total_row
            # n=5
            for index, row in enumerate(data):
                if index < n:
                    print("Proses Ke-"+str(index+1))
                    review.append([row['review'], row['normalisation']])

                    TFS = self.ComputeTF(query, row['normalisation'], index)
                    tf.append(TFS)

                    tempLabel = ''
                    print(row['label'])
                    if row['label'] == '1':
                        tempLabel = 'positif'
                    else:
                        tempLabel = 'negatif'

                    sentimen.append(tempLabel)
                
            print(sentimen)
            df = self.ComputeDF(query, tf, n)
            idf = self.ComputeIDF(query, df, n)
            tfidf = self.ComputeTFIDF(tf, idf)
            prepare_data = self.PrepareData(query, tfidf, sentimen)
            training_data = self.TrainingData(prepare_data)


        if tipe=='manual':
            df = pd.read_csv(data) 
            total_row = df.No
            n = len(total_row)
            # n=5
            
            for index, row in df.iterrows():
                if index < n:
                    print("Proses Ke-"+str(index+1))
                    
                    newText = self.PreprocessingFunction(self, row['Review'])
                    review.append([row['Review'], newText])

                    TFS = self.ComputeTF(query, newText, index)

                    tf.append(TFS)
                    sentimen.append(row['Sentimen'])

            df = self.ComputeDF(query, tf, n)
            idf = self.ComputeIDF(query, df, n)
            tfidf = self.ComputeTFIDF(tf, idf)

            prepare_data = self.PrepareData(query, tfidf, sentimen)
            training_data = self.TrainingData(prepare_data)
        
        return {
            'comment': review,
            'sentimen': sentimen,
            'query': query,
            'tf': tf,
            'df': df,
            'idf': idf,
            'tfidf': tfidf,
            'prepare_data': prepare_data,
            'training_data': training_data
        }