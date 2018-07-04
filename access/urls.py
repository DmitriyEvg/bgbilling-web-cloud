from django.conf.urls import *
from . import views

urlpatterns = [
    url(r'^login/', views.Login),
    url(r'^logout/', views.Logout),    
    url(r'^auth/', views.Auth),
    url(r'^accountCreate/', views.accountCreate),
    url(r'^register/', views.Register),
    url(r'^requisite/', views.Requisite),
    url(r'^wellcome/', views.Wellcome),
    url(r'^contractSelect/', views.contractSelect),
    url(r'^pswdChange/', views.pswdChange),
    url(r'^contractData/', views.contractData),
    url(r'^contractDataUpdate/', views.contractDataUpdate),
    url(r'^recovery/', views.Recovery),
    url(r'^sendRecovery/', views.sendRecovery),
    url(r'^recoveryPassword/', views.recoveryPassword),
]
