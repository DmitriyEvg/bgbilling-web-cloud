from lkbilling.settings import BILL_DOMAIN_URL, BILL_EXECUTER_PATH, BILL_JSON_PATH, BILL_USER, BILL_PSWD, BILL_DB_HOST, BILL_DB_USER, BILL_DB_PASSWORD, BILL_DB_NAME
import ssl
from io import StringIO, BytesIO
from xvfbwrapper import Xvfb
import pdfkit
from django.template.loader import get_template

from num2t4ru import decimal2text
import decimal

import pymysql.cursors
import csv
import json

from django.http import HttpResponse, HttpResponseRedirect
import http.client, html
import calendar
from lxml import etree
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, date, time
from core.views import session_required, ContractParameters

import ssl

# Create your views here.

@session_required
def ContractsDetailCSV(request, cid):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="somefilename.csv"'

    writer = csv.writer(response)
    writer.writerow(['First row', 'Foo', 'Bar', 'Baz'])
    writer.writerow(['Second row', 'A', 'B', 'C', '"Testing"', "Here's a quote"])

    return response


@session_required
def ConractsDetail(request, cid):

    # Получаем параметры из POST запроса
    # Тип запроса
    typeRqst = request.POST.get('ajax')

    # Получаем период из запроса
    year = request.POST.get('Year')
    month = request.POST.get('Month')
    # Если в запросе поля dateFrom или dateTo пустые, формируем период за текущий месяц
    if (year is None) or (month is None):
        now = datetime.now()
        year = str(now.year).zfill(4)
        month = str(now.month).zfill(2)
    
    
    # Формируем название таблицы из БД
    npay_table_name = "npay_detail_1_" + year + month
    
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
            sql = "SELECT c.id, c.title, c.comment, c.date1, s.title as srvName, n.col, n.summa, n.sid, n.treeId, ctl.title as pTariff, tp.title as gTariff \
        	    FROM contract c \
        	    JOIN %s n ON n.cid = c.id \
        	    JOIN service s ON n.sid = s.id \
        	    LEFT JOIN contract_tree_link ctl ON ctl.tree_id = n.treeId \
        	    LEFT JOIN tariff_plan tp ON tp.tree_id = n.treeId \
        	    ORDER BY c.comment" % npay_table_name

            cursor.execute(sql)
            json_result = cursor.fetchall()
            
            sql = "SELECT sum(summa) as total FROM %s" % npay_table_name
            cursor.execute(sql)
            summ_result = cursor.fetchall()
    finally:
        connection.close()


    return render(request,'ContractsDetail.html',locals())


@session_required
def BillDetail(request, cid):
    request.session['currentURL'] = "/bill/detail/"

    # Получаем параметры из POST запроса
    # Тип запроса
    typeRqst = request.POST.get('ajax')
    # Период
    dateFrom = request.POST.get('dateFrom')
    dateTo = request.POST.get('dateTo')

    # Если в запросе поля dateFrom или dateTo пустые, формируем период за текущий месяц
    if (dateFrom is None) or (dateTo is None):
        # Получаем текущую дату
        now = datetime.now()
        year = now.year
        maxDay = calendar.mdays[now.month]
        # Формируем период текущего месяца
        dateFrom = now.strftime("%Y-%m-01") + 'T00:00:00'
        dateTo = now.strftime("%Y-%m-") + '%sT23:59:59.999' % maxDay
    
    # Формируем запрос для получения данных по балансу:
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
		    <ns5:balanceDetailList xmlns:ns5="http://common.balance.contract.kernel.bgbilling.bitel.ru/" \
					   xmlns:common="http://common.bitel.ru" xmlns:xs="http://www.w3.org/2001/XMLSchema" \
					   xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"> \
			<contractId>%s</contractId> \
			<period dateFrom="%s" dateTo="%s"/> \
			<available>false</available> \
		    </ns5:balanceDetailList> \
		</S:Body> \
	</S:Envelope>' % (BILL_USER, BILL_PSWD, cid, dateFrom, dateTo)

    # Отправляем запрос
    conn = http.client.HTTPSConnection(BILL_DOMAIN_URL, context=ssl._create_unverified_context())
    conn.request("POST", ("%s/ru.bitel.bgbilling.kernel.contract.balance/BalanceService" % BILL_EXECUTER_PATH) , params , headers)
    rqst = conn.getresponse()
    xml = rqst.read()
    nodes = etree.XML(xml)
    conn.close()

    elements = nodes.findall('.//return')
    
    # Форматируем данные в красивый вид
    for element in elements:
        if 'date' in element.attrib:
            dateFromXML = element.attrib['date']
            element.attrib['date'] = dateFromXML[0:4] + '.' + dateFromXML[5:7] + '.' + dateFromXML[8:10]

        if 'sum' in element.attrib:
            element.attrib['sum'] = "%.2f" % float(element.attrib['sum'])

        if 'sumAfterChange' in element.attrib:
            element.attrib['sumAfterChange'] = "%.2f" % float(element.attrib['sumAfterChange'])
            
        if 'type' in element.attrib:
            if element.attrib['type'] == "1":
                element.attrib['type'] = "#daffef"
                element.attrib['sum'] = "+" + element.attrib['sum']

    contractParams = ContractParameters(request, cid)
    dateCreated = contractParams.dateCreated
    dateCreated = dateCreated[6:10] + '.' + dateCreated[3:5] + '.' + dateCreated[0:2]

    return render(request,'BillDetail.html',locals())

@session_required
def invoicePDF(request, cid):
    summa = float(request.POST.get('sum').replace(',', '.'))
    summaNDS = round(summa - (summa/1.18), 2)

    int_units = ((u'рубль', u'рубля', u'рублей'), 'm')
    exp_units = ((u'копейка', u'копейки', u'копеек'), 'f')
    summaTXT=decimal2text(
    		decimal.Decimal(summa),
		int_units=int_units,
    		exp_units=exp_units)

    # Получаем текущую дату
    months = ['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря']
    now = datetime.now()
    month = months[int(now.strftime("%m")) - 1]
    dateInvoice = now.strftime("%d ") + month + now.strftime(" %Y")
    numInvoice = 777
    
    
    contractParams = ContractParameters(request, cid)

    template = get_template('/opt/lkbilling/templates/invoice/invoice.html')
    html  = template.render({"c_title": contractParams.title,
			     "c_dateInvoice": dateInvoice,
			     "c_numInvoice": numInvoice,
			     "c_comment": contractParams.comment,
			     "c_dateCreated": contractParams.dateCreated,
			     "c_summa": summa,
			     "c_summaNDS": summaNDS,
			     "c_summaTXT": summaTXT.capitalize()
			     })
    
    options = {
	'margin-top': '0.7in',
	'margin-right': '0in',
	'margin-bottom': '0in',
	'margin-left': '0.7in',
	'encoding': "UTF-8",
	'custom-header' : [
        ('Accept-Encoding', 'gzip')
	],
	'cookie': [
    	    ('cookie-name1', 'cookie-value1'),
    	    ('cookie-name2', 'cookie-value2'),
	],
	'no-outline': None
    }

    vdisplay = Xvfb()
    vdisplay.start()
    # launch stuff inside virtual display here.
    pdf = pdfkit.from_url(StringIO(html), False, options = options)
    vdisplay.stop()

    # Формируем HTTP ответ в виде файла pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
    response.write(pdf)

    return response

@session_required
def yandexMoney(request, cid):
    return HttpResponseRedirect('https://money.yandex.ru')
    
    
@session_required
def proceedPaymant(request, cid):
    contractFc = request.session['contractFc']
    return render(request,'proceedPaymant.html',locals())
