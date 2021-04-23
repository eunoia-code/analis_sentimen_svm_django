from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import DataLat, KataBaku, TbKatadasar, TbNormalisasi, TbPreprocessing, TbSentimen, TbProduct

import requests
from bs4 import BeautifulSoup

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    review = serializers.SerializerMethodField('getReview')

    def getReview(self, instance):
        url = instance.url
        url = url[:-1]
        request_object = self.context['request']
        jml = request_object.query_params.get('jumlah')
        
        data = []

        for i in range(int(jml)):
            page = requests.get(url+""+str(i+1))
            review = serializers.SerializerMethodField('getReview')

            soup = BeautifulSoup(page.content, 'html.parser')
            for el in soup.find_all("p", {"class": "text-content"}):
                data.append(el.text)
 
        return data


    class Meta:
        model = TbProduct
        fields = ['id', 'nama_product', 'url', 'kategori', 'review']
