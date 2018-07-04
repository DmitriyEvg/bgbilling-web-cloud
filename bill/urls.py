from django.conf.urls import *
from . import views

urlpatterns = [
    url(r'^detail/', views.BillDetail),
    url(r'^proceedPaymant/', views.proceedPaymant),    
    url(r'^yandex/', views.yandexMoney),
    url(r'^invoice.pdf', views.invoicePDF),
    url(r'^contractsDetail/', views.ConractsDetail),
    url(r'^contractsDetail.csv',views.ContractsDetailCSV),
]
