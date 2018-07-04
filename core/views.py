from lkbilling.settings import BILL_DOMAIN_URL, BILL_EXECUTER_PATH, BILL_JSON_PATH, BILL_USER, BILL_PSWD, BILL_DB_HOST, BILL_DB_USER, BILL_DB_PASSWORD, BILL_DB_NAME
from django.http import HttpResponseRedirect
import http.client, html
from lxml import etree
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime, date, time
import ssl

import pymysql.cursors
import csv
import json

# Create your views here.

class contract(object):
    title = ""
    comment = ""
    fc = ""
    status = ""
    dateCreated = ""
    balance = ""
    summa = ""
    email = ""
    tariff = []
    modules = []
    params = []
    

# Декоратор для проверки наличия сессии (проверка авторизации)
def session_required(func):
    def wrapped(request):
        cid = request.session.get('contractId')
    	# Если сессия с параметром cid существует -> вызываем декорируемую функцию
        if cid is not None:
            return func(request, cid)
        # Иначе редиректим на страницу авторизации
        else:
    	    return HttpResponseRedirect('/access/login/')
    return wrapped


def ContractParameters(request, cid):
    
    # Получаем текущую дату
    now = datetime.now()
    date = now.strftime("%d.%m.%Y")

    # Запрос на получение сводной информации о договоре
    conn = http.client.HTTPSConnection(BILL_DOMAIN_URL, context=ssl._create_unverified_context())
    conn.request("GET", "%s?user=%s&pswd=%s&module=contract&action=ContractInfo&cid=%s" % (BILL_EXECUTER_PATH, BILL_USER, BILL_PSWD, cid))
    rqst = conn.getresponse()
    xml = rqst.read()
    nodes = etree.XML(xml)
    conn.close()

    contract.title = nodes.xpath('/data/contract')[0].get('title')
    contract.comment = nodes.xpath('/data/contract')[0].get('comment')
    contract.fc = nodes.xpath('/data/contract')[0].get('fc')
    contract.status = nodes.xpath('/data/info/balance')[0].get('status')
    contract.dateCreated = nodes.xpath('/data/contract')[0].get('date1')
    contract.balance = nodes.xpath('/data/info/balance')[0].get('summa5')
    contract.summa = nodes.xpath('/data/info/balance')[0].get('summa3')
    contract.tariff = nodes.xpath('/data/info/tariff/item')
    contract.modules = nodes.xpath('/data/info/modules/item')

    # Добавляем в сессию ключ с информацией о типе договора (физ/юр)
    request.session['contractFc'] = contract.fc

    # Опеределяем принадлежность к группе (физ. или юр. лицо)
    if (contract.fc == "0"):
        pgid = 2
        print(pgid)
    else:
        pgid = 1
        print(pgid)

    
    # Запрос определяющий группу параметров (разный набор для физ. или юр. лиц)
    conn = http.client.HTTPSConnection(BILL_DOMAIN_URL, context=ssl._create_unverified_context())
    conn.request("GET", "%s?user=%s&pswd=%s&pgid=%s&module=contract&action=SetGrContract&cid=%s" % (BILL_EXECUTER_PATH, BILL_USER, BILL_PSWD, pgid, cid))
    rqst = conn.getresponse()
    conn.close()
    
    # Запрос на получаение необходимых параметров договора
    conn = http.client.HTTPSConnection(BILL_DOMAIN_URL, context=ssl._create_unverified_context())
    conn.request("GET", "%s?user=%s&pswd=%s&module=contract&action=ContractParameters&cid=%s" % (BILL_EXECUTER_PATH, BILL_USER, BILL_PSWD, cid))
    rqst = conn.getresponse()
    xml = rqst.read()
    nodes = etree.XML(xml)
    conn.close()
    
    contract.params = nodes.xpath('/data/parameters/parameter')
    
    contract.email = contract.params[0].get('value')
    
    # Добавляем к сессии переменную email
    request.session['email'] = contract.email

    return contract
	

def ifacesListFree(request, cid, deviceId):
    
    # Получаем параметры из POST запроса
    # Тип запроса
    typeRqst = request.POST.get('ajax')

    # Формируем запрос 
    # ================================================

    # Формируем заголовок запроса
    headers = {"Content-type": 'application/xop+xml; charset=utf-8; type="text/xml"'}

    #deviceInterfaceListFree
    #devicePortList

    # Формируем тело запроса
    params = '<?xml version="1.0" ?> \
	<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"> \
	  <S:Header> \
	    <auth xmlns="http://ws.base.kernel.bgbilling.bitel.ru/" user="%s" pswd="%s"> \
	    </auth> \
	  </S:Header> \
	  <S:Body> \
	    <ns5:deviceInterfaceListFree xmlns:ns5="http://common.resource.inventory.systems.oss.bitel.ru/" \
				         xmlns:common="http://common.bitel.ru" \
				         xmlns:xs="http://www.w3.org/2001/XMLSchema" \
				         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"> \
		<deviceId>%s</deviceId> \
		<dateFrom>2017-12-11T00:00:00+03:00</dateFrom> \
		<interfaceTitle/> \
	    </ns5:deviceInterfaceListFree> \
	  </S:Body> \
    </S:Envelope>' % (BILL_USER, BILL_PSWD, deviceId)

    # Отправляем запрос
    conn = http.client.HTTPSConnection(BILL_DOMAIN_URL, context=ssl._create_unverified_context())
    conn.request("POST", ("%s/ru.bitel.oss.systems.inventory.resource/4/DeviceInterfaceService" % BILL_EXECUTER_PATH), params , headers)
    rqst = conn.getresponse()
    xml = rqst.read()
    nodes = etree.XML(xml)
    conn.close()
    
    ifaceListObj = nodes.findall('.//return')
    
    return ifaceListObj

def conractSearch(mail):
    
    # Формируем запрос 
    # ================================================

    # Формируем заголовок запроса
    headers = {"Content-type": 'application/xop+xml; charset=utf-8; type="text/xml"'}


    # Формируем тело запроса

    params = '<?xml version="1.0" ?> \
	<S:Envelope xmlns:S="http://schemas.xmlsoap.org/soap/envelope/"> \
	    <S:Header> \
		<auth xmlns="http://ws.base.kernel.bgbilling.bitel.ru/" user="%s" pswd="%s"> \
		</auth> \
	    </S:Header> \
	<S:Body> \
	    <ns5:contractList xmlns:common="http://common.bitel.ru" \
			      xmlns:ns5="http://service.common.api.contract.kernel.bgbilling.bitel.ru/" \
			      xmlns:xs="http://www.w3.org/2001/XMLSchema" \
			      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"> \
				<fc xmlns="">-1</fc> \
				<groupMask xmlns="">0</groupMask> \
				<entityFilter xmlns="" entitySpecAttrIds="1" value="%s" xsi:type="ns5:filterEntityAttrText"></entityFilter> \
				<subContracts xmlns="">false</subContracts> \
				<closed xmlns="">false</closed> \
				<hidden xmlns="">false</hidden> \
				<page xmlns="" pageCount="0" pageIndex="1" pageSize="100" recordCount="0"></page> \
	    </ns5:contractList> \
	</S:Body> \
    </S:Envelope>' % (BILL_USER, BILL_PSWD, mail)

    # Отправляем запрос
    conn = http.client.HTTPSConnection(BILL_DOMAIN_URL, context=ssl._create_unverified_context())
    conn.request("POST", ("%s/ru.bitel.bgbilling.kernel.contract.api/ContractService" % BILL_EXECUTER_PATH), params , headers)
    rqst = conn.getresponse()
    xml = rqst.read()
    nodes = etree.XML(xml)
    conn.close()
    
    contractListObj = nodes.findall('.//return')

    #return contractListObj
    return xml
    
def getContractList(userName):

    # Формируем название таблицы из БД
    table_name = "contract_parameter_type_1"

    # Connect to the database
    connection = pymysql.connect(host = BILL_DB_HOST,
                                 user = BILL_DB_USER,
                                 password=BILL_DB_PASSWORD,
                                 db = BILL_DB_NAME,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    # Запрос на формирование таблицы
    try:
        with connection.cursor() as cursor:
            sql = "SELECT c.id, c.title, c.comment, c.pswd \
                    FROM `contract_parameter_type_1` cp \
                    JOIN `contract` c ON c.id = cp.cid \
                    WHERE `val`='%s'" % userName
            cursor.execute(sql)
            json_result = cursor.fetchall()
    finally:
        connection.close()


    return json_result

def contractPasswordChange(userName, newPswd):

    json_result = []

    # Получаем список связанных договоров с userName в виде JSON и определяем их количество
    contractListJSON = getContractList(userName)

    # Connect to the database
    conn = pymysql.connect(host = BILL_DB_HOST,
                           user = BILL_DB_USER,
                           password=BILL_DB_PASSWORD,
                           db = BILL_DB_NAME,
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    
    cursor = conn.cursor()

    # Перебираем в цикле вся связанные контракты
    for contract in contractListJSON:
	# Получаем id договора
        cid = contract['id']
        # Запрос на изменения поля pswd
        cursor.execute( "UPDATE contract SET `pswd`='%s' WHERE `id`='%d'" % (newPswd, cid) )
        json_result.append( cursor.fetchall() )
    conn.commit()

    return json_result
