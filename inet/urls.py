from django.conf.urls import *
from . import views

urlpatterns = [
    url(r'^$', views.inetDetail),
    url(r'^ipList/', views.ipList),
]
