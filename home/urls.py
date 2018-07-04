from django.conf.urls import *
from . import views

urlpatterns = [
    url(r'^$', views.ContractInfo),
    url(r'^dogovor.pdf', views.ContractDownload),
]
