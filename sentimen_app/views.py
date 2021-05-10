from django.shortcuts import render
from .models import DataLat, KataBaku, TbKatadasar, TbNormalisasi, TbPreprocessing, TbSentimen, TbProduct
from .serializers import ProductSerializer
from rest_framework import routers, serializers, viewsets, generics
from django_filters.rest_framework import DjangoFilterBackend

# Create your views here.
def index(request):
    data_latih_jumlah = DataLat.objects.all().count()
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

class getDataReviews(viewsets.ModelViewSet):
    queryset = TbProduct.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id']
