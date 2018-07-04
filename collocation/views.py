from lkbilling.settings import BILL_DOMAIN_URL, BILL_EXECUTER_PATH, BILL_JSON_PATH, BILL_USER, BILL_PSWD, BILL_DB_HOST, BILL_DB_USER, BILL_DB_PASSWORD, BILL_DB_NAME
from django.http import  HttpResponse, HttpResponseRedirect
import http.client, html
from lxml import etree
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, date, time, timedelta
import locale
from core.views import session_required, ContractParameters, ifacesListFree
import ssl
import pymysql.cursors
import json


@session_required
def collDetail(request, cid):

    json_call = []

    # Получаем тип запроса
    typeRqst = request.POST.get('ajax')

    # get filter service
    rackId = request.POST.get('rackId')
    periodType = request.POST.get('periodType')
    currentDate = request.POST.get('currentDate')
    

    # Connect to the database
    connection = pymysql.connect(host = BILL_DB_HOST,
                                 user = BILL_DB_USER,
                                 password=BILL_DB_PASSWORD,
                                 db = BILL_DB_NAME,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    # Запрос на формирование данных по размещению
    try:
        with connection.cursor() as cursor:
            # Запрос списока всех стоек в формате sql
            sqlAllRacksList = "`typeId`=34"
            
            sql = "SELECT inetServ.deviceId, inetDevice.title \
        	FROM `inet_serv_4` inetServ \
        	JOIN `inet_device_tree_4` inetDevice ON inetServ.deviceId = inetDevice.id \
        	WHERE (`contractId`=%s AND %s) group by `deviceId`" % (cid, sqlAllRacksList)

            cursor.execute(sql)
            json_racks_all = cursor.fetchall()


            # Запрос списока всех юнитов в формате sql
            sqlAllUnitsList = "`typeId`=34"
            
	    # Если rackId в post запросе не пустые => преобразуем sqlAllUnitsList запрос к виду
            if rackId is not None:
                rackId = int(rackId)
                sqlAllUnitsList = sqlAllUnitsList + " AND `deviceId`=%s" % rackId
                
            #if currentDate is None:
            locale.setlocale(locale.LC_TIME, "ru_RU")
            currentDate = datetime.now()
                
            # Если periodType и dateSelected в post запросе не пустые => преобразуем sqlAllUnitsList запрос к виду
            if periodType is not None:
            
                periodType = str(periodType)
                
                if periodType == "selectWeek":
                    startWeekDate = currentDate - timedelta(days=currentDate.weekday())
                    endWeekDate = startWeekDate + timedelta(days=6)
                    periodVal = startWeekDate.strftime("%d/%m/%y") + " - " + endWeekDate.strftime("%d/%m/%y")
                elif periodType == "selectMonth":
                    periodVal = currentDate.strftime("%B %Y")
                elif periodType == "selectYear":
            	    periodVal = currentDate.strftime("%Y")
                elif periodType == "selectAll":
                    periodVal = "Все даты"
                else:
            	    periodVal = periodType
            else:
                periodType = "selectedAll"
                periodVal = "Все даты"
                
            sql = "SELECT inetServ.id, inetServ.title, inetServ.comment, inetServ.dateFrom, inetServ.dateTo \
        	FROM `inet_serv_4` inetServ \
        	WHERE (`contractId`=%s AND %s) ORDER BY inetServ.dateFrom DESC" % (cid, sqlAllUnitsList)
		#inetServ.dateTo IS NULL AND
            cursor.execute(sql)
            json_units = cursor.fetchall()
            
            for key in json_units:
                strComment = key.get('comment').replace("\n","")
                key.update({'comment': strComment.split(';')})
                titleArray = key.get('title').split('/')
                rackTitle = titleArray[0]
                unitTitle = titleArray[1]
                rackName = rackTitle.split(': ')[0]
                rackIndex = rackTitle.split(': ')[1]
                if int(rackIndex) < 10:
                    rackIndex = "0%s" % rackIndex
                unitName = unitTitle.split(' ')[0]
                unitIndex = unitTitle.split(' ')[1]
                if int(unitIndex) < 9:
                    unitIndex = '0%s' % unitIndex
                key.update({'title': '%s %s / %s %s' % (rackName, rackIndex, unitName, unitIndex)})
    finally:
        connection.close()



    return render(request,'collDetail.html',locals())


@session_required
def editUnit(request, cid):
    # Получаем тип запроса
    typeRqst = request.POST.get('ajax')

    # get service id
    unitId = request.POST.get('unitId')
    trIndex = request.POST.get('trIndex')

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

            sql = "SELECT inetServ.id, inetServ.parentId, inetServ.deviceId, inetServ.interfaceId, inetServ.comment, inetServ.dateFrom, inetServ.dateTo, inetDeviceTree.invDeviceId, invDevice.title as deviceTitle, invDevicePort.title as devicePortTitle \
                   FROM `inet_serv_4` inetServ \
                   JOIN `inet_device_tree_4` inetDeviceTree ON inetDeviceTree.id = inetServ.deviceId \
                   JOIN `inv_device_4` invDevice ON invDevice.id = inetDeviceTree.invDeviceId \
                   JOIN `inv_device_port_4` invDevicePort ON (invDevicePort.deviceId = inetDeviceTree.invDeviceId AND invDevicePort.port = inetServ.interfaceId) \
                   WHERE inetServ.id = %s" % unitId

            cursor.execute(sql)
            dataUnit = cursor.fetchall()
            
            sql = "SELECT * FROM `inet_device_tree_4` WHERE `parentId`=179"
            cursor.execute(sql)
            deviceCollJSON = cursor.fetchall()

    finally:
        connection.close()

    for key in dataUnit:
        inetServId = key.get('id')
        inetParentId = key.get('parentId')
        strComment = key.get('comment').replace("\n","").split(';')
        strDateFrom = key.get('dateFrom').strftime('%d-%m-%Y')
        strDeviceId = key.get('deviceId')
        strDeviceTitle = key.get('deviceTitle')
        invDeviceId = key.get('invDeviceId')
        strIfaceId = key.get('interfaceId')
        strIfaceTitle = key.get('devicePortTitle')
        
    ifaceList = ifacesListFree(request, cid, invDeviceId)
        
    return render(request,'editUnit.html',locals())


@session_required
def getIfacesFree(request, cid):
    # Получаем тип запроса
    typeRqst = request.POST.get('ajax')

    # get post params
    deviceId = int(request.POST.get('deviceId'))
    selectedDeviceId = int(request.POST.get('selectedDeviceId'))
    currentIfaceId = request.POST.get('currentIfaceId')
    currentIfaceTitle = request.POST.get('currentIfaceTitle')

    ifaceList = ifacesListFree(request, cid, deviceId)
    
    return render(request,'getIfacesFree.html',locals())
	
@session_required
def updateUnit(request, cid):
    
    # Получаем параметры из POST запроса
    # Тип запроса
    typeRqst = request.POST.get('ajax')

    # get update params
    servId = request.POST.get('id')
    servParentId = request.POST.get('parentId')

    dateFrom = request.POST.get('dateFrom')
    dateFromArray = dateFrom.split('-')
    dateFrom = "%s-%s-%sT00:00:00+03:00" % (dateFromArray[2], dateFromArray[1], dateFromArray[0])

    device =  request.POST.get('device')
    device = device.split(':')
    deviceId = device[0]

    ifaceId = request.POST.get('iface')

    comment1 = request.POST.get('comment1')
    comment2 = request.POST.get('comment2')
    comment3 = request.POST.get('comment3')
    comment4 = request.POST.get('comment4')
    comment5 = request.POST.get('comment5')
    comment6 = request.POST.get('comment6')
    
    comment = "%s;\n%s;\n%s;\n%s;\n%s;\n%s;\n" % (comment1, comment2, comment3, comment4, comment5, comment6)


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
	    <ns5:inetServUpdate xmlns:ns5="http://service.common.api.inet.modules.bgbilling.bitel.ru/" \
				xmlns:common="http://common.bitel.ru" \
				xmlns:xs="http://www.w3.org/2001/XMLSchema" \
				xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"> \
	      <inetServ accessCode="0" \
		    	cid="%s" \
			coid="0" \
			dateFrom="%s" \
			devState="0" \
			did="%s" \
			id="%s" \
			ifaceId="%s" \
			ipResId="0" \
			ipResSubsriptionId="0" \
			parentId="%s" \
			passw="" \
			scid="0" \
			sessCntLimit="0" \
			status="0" \
			typeId="34" \
			uname="" \
			vlan="-1"> \
		  <comment>%s</comment> \
		  <config/> \
		  <identifierList/> \
		  <macList/> \
	      </inetServ> \
	      <generateLogin>false</generateLogin> \
	      <generatePassword>false</generatePassword> \
	      <saWaitTimeout>0</saWaitTimeout> \
	    </ns5:inetServUpdate> \
	  </S:Body> \
    </S:Envelope>' % (BILL_USER, BILL_PSWD, cid, dateFrom, deviceId, servId, ifaceId, servParentId, comment)

    # Отправляем запрос
    conn = http.client.HTTPSConnection(BILL_DOMAIN_URL, context=ssl._create_unverified_context())
    conn.request("POST", ("%s/ru.bitel.bgbilling.modules.inet.api/4/InetServService" % BILL_EXECUTER_PATH), params.encode('utf8') , headers)
    rqst = conn.getresponse()
    xml = rqst.read()
    nodes = etree.XML(xml)
    conn.close()

    answer = nodes.findall('.//return')
    
    return render(request,'updateUnit.html',locals())
