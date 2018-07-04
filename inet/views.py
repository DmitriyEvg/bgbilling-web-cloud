from lkbilling.settings import BILL_DOMAIN_URL, BILL_EXECUTER_PATH, BILL_JSON_PATH, BILL_USER, BILL_PSWD, BILL_DB_HOST, BILL_DB_USER, BILL_DB_PASSWORD, BILL_DB_NAME
from django.http import  HttpResponse, HttpResponseRedirect
import http.client, html
from lxml import etree
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, date, time
from core.views import session_required, ContractParameters
import ssl
import pymysql.cursors
import json


@session_required
def inetDetail(request, cid):
    request.session['currentURL'] = "/inet/"

    json_ip = []

    # Получаем тип запроса
    typeRqst = request.POST.get('ajax')

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
            sql = "SELECT inetServ.id, inetServ.typeId, inetServ.deviceOptions, inetServ.vlan, inetType.title as inetTypeTitle, inetOpt.title as inetOptTitle \
        	FROM `inet_serv_4` inetServ \
        	JOIN `inet_serv_type_4` inetType ON inetServ.typeId = inetType.id \
        	LEFT JOIN `inet_option_4` inetOpt ON inetServ.deviceOptions = inetOpt.id \
        	WHERE (`contractId`=%s AND (`typeId`=1 OR `typeId`=5 OR `typeId`=14 OR `typeId`=17 OR `typeId`=28 OR `typeId`=31))" % cid

            cursor.execute(sql)
            json_services = cursor.fetchall()
            
            for service in json_services:
                if service['typeId'] == 1 or service['typeId'] == 5:
                    sql = "SELECT inetServ.addressFrom, inetServ.addressTo \
        		    FROM `inet_serv_4` inetServ \
        		    WHERE (`contractId`=%s AND `typeId`=2 AND `parentId`=%s)" % (cid, service['id'])
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    service.update({'ipCount': len(result)})
                    json_ip.append(result)
                    
                if service['typeId'] == 14:
                    sql = "SELECT inetServ.addressFrom, inetServ.addressTo \
        		    FROM `inet_serv_4` inetServ \
        		    WHERE (`contractId`=%s AND `typeId`=15 AND `vlan`=%s)" % (cid, service['vlan'])
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    service.update({'ipCount': len(result)})
                    json_ip.append(result)                    
                    
                if service['typeId'] == 28:
                    sql = "SELECT inetServ.addressFrom, inetServ.addressTo \
        		    FROM `inet_serv_4` inetServ \
        		    WHERE (`contractId`=%s AND `typeId`=29 AND `vlan`=%s)" % (cid, service['vlan'])
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    service.update({'ipCount': len(result)})
                    json_ip.append(result)              
                    
                if service['typeId'] == 31:
                    sql = "SELECT inetServ.addressFrom, inetServ.addressTo \
        		    FROM `inet_serv_4` inetServ \
        		    WHERE (`contractId`=%s AND `typeId`=31 AND `vlan`=%s)" % (cid, service['vlan'])
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    service.update({'ipCount': len(result)})
                    json_ip.append(result)                                                            
    finally:
        connection.close()



    return render(request,'inetDetail.html',locals())


@session_required
def ipList(request, cid):
    request.session['currentURL'] = "/inet/ipList/"

    json_services_all = []
    json_services = []
    json_ip = []

    # Получаем тип запроса
    typeRqst = request.POST.get('ajax')
    
    # get filter service
    servType = request.POST.get('servType')
    servVLAN = request.POST.get('servVLAN')

    # Connect to the database
    connection = pymysql.connect(host = BILL_DB_HOST,
                                 user = BILL_DB_USER,
                                 password=BILL_DB_PASSWORD,
                                 db = BILL_DB_NAME,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
    	    # Запрос списока всех интернет сервисов в формате sql
            sqlAllServList = "(`typeId`=1 OR `typeId`=5 OR `typeId`=14 OR `typeId`=17 OR `typeId`=28 OR `typeId`=31)"
            
	    #--------------------------------------------
    	    # Запрос на формирование списка сервисов
	    #--------------------------------------------
            sql = "SELECT inetServ.typeId, inetServ.vlan, inetType.title as inetTypeTitle \
        	FROM `inet_serv_4` inetServ \
        	JOIN `inet_serv_type_4` inetType ON inetServ.typeId = inetType.id \
        	WHERE (`contractId`=%s AND %s)" % (cid, sqlAllServList)

            cursor.execute(sql)
            json_services_all = cursor.fetchall()

	    #--------------------------------------------
    	    # Запрос на формирование списка IP адресов
	    #--------------------------------------------

	    # Если servType и servVLAN в post запросе не пустые => преобразуем sql запрос к виду
            if ((servType is not None) and (servVLAN is not None)):
                servType = int(servType)
                servVLAN = int(servVLAN)
                sqlFilter = "`typeId`=%s AND `vlan`=%s" % (servType, servVLAN)
            else:
            # Иначе => делаем запрос по всем интернет сервисам
                sqlFilter = sqlAllServList
            

            sql = "SELECT inetServ.id, inetServ.typeId, inetServ.deviceOptions, inetServ.vlan, inetType.title as inetTypeTitle, inetOpt.title as inetOptTitle \
        	FROM `inet_serv_4` inetServ \
        	JOIN `inet_serv_type_4` inetType ON inetServ.typeId = inetType.id \
        	LEFT JOIN `inet_option_4` inetOpt ON inetServ.deviceOptions = inetOpt.id \
        	WHERE (`contractId`=%s AND %s)" % (cid, sqlFilter)

            cursor.execute(sql)
            json_services = cursor.fetchall()
            
            for service in json_services:
                if service['typeId'] == 1 or service['typeId'] == 5:
                    sql = "SELECT inetServ.addressFrom, inetServ.addressTo, inetServ.comment \
        		    FROM `inet_serv_4` inetServ \
        		    WHERE (`contractId`=%s AND `typeId`=2 AND `parentId`=%s)" % (cid, service['id'])
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    for key in result:
                        key.update({'vlan': service['vlan']})
                        startIP = key.get('addressFrom')
                        endIP = key.get('addressTo')
                        key.update({'addressFrom': str(startIP[0]) + '.' + str(startIP[1]) + '.' + str(startIP[2]) + '.' + str(startIP[3]) + ' - ' + \
                                                 str(endIP[0]) + '.' + str(endIP[1]) + '.' + str(endIP[2]) + '.' + str(endIP[3]) })
                        strComment = key.get('comment')
                        key.update({'comment': strComment.split(';')})
                    json_ip.append(result)
                    
                if service['typeId'] == 14:
                    sql = "SELECT inetServ.addressFrom, inetServ.addressTo, inetServ.comment \
        		    FROM `inet_serv_4` inetServ \
        		    WHERE (`contractId`=%s AND `typeId`=15 AND `vlan`=%s)" % (cid, service['vlan'])
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    for key in result:
                        key.update({'vlan': service['vlan']})
                        binaryIP = key.get('addressFrom')
                        key.update({'addressFrom': str(binaryIP[0]) + '.' + str(binaryIP[1]) + '.' + str(binaryIP[2]) + '.' + str(binaryIP[3]) })
                        strComment = key.get('comment')
                        key.update({'comment': strComment.split(';')})
                    json_ip.append(result)                    
                    
                if service['typeId'] == 28:
                    sql = "SELECT inetServ.addressFrom, inetServ.addressTo, inetServ.comment \
        		    FROM `inet_serv_4` inetServ \
        		    WHERE (`contractId`=%s AND `typeId`=29 AND `vlan`=%s)" % (cid, service['vlan'])
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    for key in result:
                        key.update({'vlan': service['vlan']})
                        binaryIP = key.get('addressFrom')
                        key.update({'addressFrom': str(binaryIP[0]) + '.' + str(binaryIP[1]) + '.' + str(binaryIP[2]) + '.' + str(binaryIP[3]) })
                        strComment = key.get('comment')
                        key.update({'comment': strComment.split(';')})                        
                    json_ip.append(result)

                if service['typeId'] == 31:
                    sql = "SELECT inetServ.addressFrom, inetServ.addressTo, inetServ.comment \
        		    FROM `inet_serv_4` inetServ \
        		    WHERE (`contractId`=%s AND `typeId`=31 AND `vlan`=%s)" % (cid, service['vlan'])
                    cursor.execute(sql)
                    result = cursor.fetchall()
                    for key in result:
                        key.update({'vlan': service['vlan']})
                        startIP = key.get('addressFrom')
                        endIP = key.get('addressTo')                        
                        key.update({'addressFrom': str(startIP[0]) + '.' + str(startIP[1]) + '.' + str(startIP[2]) + '.' + str(startIP[3]) + ' - ' + \
                                                 str(endIP[0]) + '.' + str(endIP[1]) + '.' + str(endIP[2]) + '.' + str(endIP[3]) })                        
                        strComment = key.get('comment')
                        key.update({'comment': strComment.split(';')})                        
                    json_ip.append(result)
                
                ipReservCount = str(json_ip).count("Резерв")
                ipCollCount = str(json_ip).count("Collocation")
                ipInetCount = str(json_ip).count("Интернет")
                ipVPSCount = str(json_ip).count("VPS")
                ipRentCount = str(json_ip).count("Аренда")
                ipAllCount = ipReservCount + ipCollCount + ipInetCount + ipVPSCount + ipRentCount
    finally:
        connection.close()

    return render(request,'ipList.html',locals())