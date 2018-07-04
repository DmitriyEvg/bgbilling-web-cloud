from django.conf.urls import *
from . import views

urlpatterns = [
    url(r'^$', views.collDetail),
    url(r'^ifaces/', views.ifacesListFree),
    url(r'^editUnit/', views.editUnit),
    url(r'^getIfacesFree/', views.getIfacesFree),
    url(r'^updateUnit/', views.updateUnit),
]
