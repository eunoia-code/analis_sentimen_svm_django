from django.shortcuts import render
from .models import DataLat, TbKatadasar, TbSentimen, TbProduct, TbData
from .serializers import ProductSerializer, LabelSerializer
from .the_function import the_function

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django_filters.rest_framework import DjangoFilterBackend
from django.core.files.storage import FileSystemStorage

import pandas as pd
# Create your views here.
def index(request):
    data_latih_jumlah = TbData.objects.all().count()
    kata_dasar_jumlah = TbKatadasar.objects.all().count()
    product_jumlah = TbProduct.objects.all().count()
    kata_sentimen_jumlah = TbSentimen.objects.all().count()
    
    context = {
        'dl': data_latih_jumlah,
        'kd': kata_dasar_jumlah,
        'pj': product_jumlah,
        'ks': kata_sentimen_jumlah
    }

    return render(request, 'dashboard.html', context)

def sentimen(request):
    data_produk = TbProduct.objects.all()

    context = {
        'data_produk' : data_produk
    }

    return render(request, 'sentimen.html', context)

def uji_svm(request):
    dbdata = TbData.objects.all().order_by('index_number').values()

    data = the_function(dbdata, 'from_db')
    print(type(data['idf']))
    context = {
        'status': True,
        'comment' : data['comment'],
        'sentimen': data['sentimen'],
        'query': data['query'],
        'tf': data['tf'],
        'df': data['df'],
        'idf': data['idf'],
        'tfidf': data['tfidf'],
        'prepare_data': data['prepare_data'],
        'label': data['training_data']
    }

    return render(request, 'uji_svm.html', context)

def sentimen_manual(request):
    if request.method == 'POST' and request.FILES['dataSheet']:
        myfile = request.FILES['dataSheet']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        print('Filename: ', uploaded_file_url)
        
        data = the_function(uploaded_file_url, 'manual')
        
        context = {
            'status': True,
            'comment' : data['comment'],
            # 'sentimen': data['sentimen'],
            # 'query': data['query'],
            # 'tf': data['tf'],
            # 'df': data['df'],
            # 'idf': data['idf'],
            # 'tfidf': data['tfidf'],
            # 'prepare_data': data['prepare_data'],
            'label': data['training_data']
        }

        return render(request, 'sentimen_manual.html', context)

    return render(request, 'sentimen_manual.html')

class getDataReviews(viewsets.ModelViewSet):
    queryset = TbProduct.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id']

@api_view(['GET'])
def emptyTableData(request):
    setx = TbData.objects.all().delete()
    return Response(status=status.HTTP_200_OK)

@api_view(['POST'])
def postDataLabels(request):
    if request.method == 'POST':
        serializer = LabelSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)