from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import DataLat, KataBaku, TbKatadasar, TbNormalisasi, TbPreprocessing, TbSentimen, TbProduct

import requests
from bs4 import BeautifulSoup

class ProductSerializer(serializers.HyperlinkedModelSerializer):
    url = "https://reviews.femaledaily.com/products/blush-76/blush/wardah/blush-on-71?cat=&cat_id=0&age_range=&skin_type=&skin_tone=&skin_undertone=&hair_texture=&hair_type=&order=newest&page="
    review = serializers.SerializerMethodField('getReview')

    def getReview(self, instance):
        request_object = self.context['request']
        jml = request_object.query_params.get('jumlah')
        
        data = []

        for i in range(int(jml)):
            page = requests.get(self.url+""+str(i+1))
            review = serializers.SerializerMethodField('getReview')

            soup = BeautifulSoup(page.content, 'html.parser')
            for el in soup.find_all("p", {"class": "text-content"}):
                data.append(el.text)

        return data


    class Meta:
        model = TbProduct
        fields = ['id', 'nama_product', 'url', 'kategori', 'review']
