from django.conf.urls import url, include
from django.urls import path
from . import views
from rest_framework import routers, serializers, viewsets

router = routers.DefaultRouter()
router.register('getDataReviews', views.getDataReviews, basename='review')

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^home/$', views.index, name='home'),
    url(r'^sentimen/$', views.sentimen, name='sentimen'),
    url(r'^uji_svm/$', views.uji_svm, name='uji_svm'),
    url(r'^sentimen_manual/$', views.sentimen_manual, name='sentimen_manual'),
    path('getData/', include(router.urls)),
    path('insert_review', views.postDataLabels, name="insert_review"),
    path('empty_data', views.emptyTableData, name="empty_data")
]
