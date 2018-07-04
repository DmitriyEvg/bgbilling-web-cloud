from lkbilling.settings import BILL_DOMAIN_URL, BILL_EXECUTER_PATH, BILL_JSON_PATH, BILL_USER, BILL_PSWD, BILL_DB_HOST, BILL_DB_USER, BILL_DB_PASSWORD, BILL_DB_NAME
from django.http import  HttpResponse, HttpResponseRedirect
import http.client, html
from lxml import etree
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, date, time
from core.views import session_required, ContractParameters
import ssl

@session_required
def vpsManager(request, cid):
    request.session['currentURL'] = "/virt/"
    # Получаем тип запроса
    typeRqst = request.POST.get('ajax')


    username = request.session.get('contractTitle')
    password = request.session.get('password')
    
    response = render(request,'vpsManager.html',locals())
    request.session["contractChangeState"] = "false"
    
    return response
