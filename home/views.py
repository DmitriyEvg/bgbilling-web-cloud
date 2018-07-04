from lkbilling.settings import BILL_DOMAIN_URL, BILL_EXECUTER_PATH, BILL_JSON_PATH, BILL_USER, BILL_PSWD, BILL_DB_HOST, BILL_DB_USER, BILL_DB_PASSWORD, BILL_DB_NAME
#from io import StringIO, BytesIO
#from xvfbwrapper import Xvfb
import pdfkit
from django.template.loader import get_template

from django.http import  HttpResponse, HttpResponseRedirect
import http.client, html
from lxml import etree
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime, date, time
from core.views import session_required, ContractParameters, getContractList
import ssl

# Create your views here.

@session_required
def ContractInfo(request, cid):
    request.session['currentURL'] = "/home/"

    # Получаем тип запроса
    typeRqst = request.POST.get('ajax')

    # Получаем текущую дату
    now = datetime.now()
    date = now.strftime("%d.%m.%Y")

    # Запрос на получение информацию по абонплатам:
    conn = http.client.HTTPSConnection("bill.your_domain.name", context=ssl._create_unverified_context())
    conn.request("GET", "%s?user=%s&pswd=%s&actualItemsDate=%s&module=npay&actualItemsOnly=1&action=ServiceObjectTable&mid=1&object_id=0&cid=%s" % (BILL_EXECUTER_PATH, BILL_USER, BILL_PSWD, date, cid) )
    rqst = conn.getresponse()
    xml = rqst.read()
    nodes = etree.XML(xml)
    conn.close()

    contractParams = ContractParameters(request, cid)

    request.session['contractTitle'] = contractParams.title

    serviceList = nodes.xpath('/data/table/data/row')

    servNames = ["INTERNET", "UNIT", "RACK", "PUBLIC IP", "VPS", "DEVICE"]
    servBG = ["bg-aqua", "bg-green", "bg-yellow", "bg-red", "bg-maroon", "bg-purple"]
    servIcons = ["1", "2", "3", "IP", "4", "5"]
    servCount = [0, 0, 0, 0, 0, 0]


    servProp = [
		["INTERNET / NETWORK", "bg-blue", "", "", 0, "/inet"],
		["COLLOCATION", "bg-green", "PatternFlyIcons-webfont", "", 0, "/collocation"],
		["RACK", "bg-yellow", "PatternFlyIcons-webfont", "", 0, "#"],
		["IP MANAGEMENT", "bg-red", "PatternFlyIcons-webfont", "IP", 0, "/inet/ipList"],
		["VPS", "bg-maroon", "PatternFlyIcons-webfont", "", 0, "/virt"],
		["DEVICE", "bg-purple", "PatternFlyIcons-webfont", "", 0, "#"],
		["SUPPORT / TICKETS", "bg-aqua", "", "", 0, "/support"]
	       ]

    for service in serviceList:
        if service.attrib['sid'] == '26':
            servProp[1][4] = service.attrib['col']
        if service.attrib['sid'] == '25':
    	    servProp[2][4] = service.attrib['col']
        if service.attrib['sid'] == '19':
            servProp[3][4] = service.attrib['col']
        if service.attrib['sid'] == '20':
            servProp[4][4] = service.attrib['col']
        if service.attrib['sid'] == '23':
            servProp[5][4] = service.attrib['col']

    contractListJSON = getContractList(request.session['username'])
    contractListCount = len(contractListJSON)
    
    return render(request,'ContractCommon.html',locals())

@session_required
def ContractDownload(request, cid):

    contractParams = ContractParameters(request, cid)

    template = get_template('/opt/lk4/templates/dogovor/dogovor.html')
    html  = template.render({"c_title": contractParams.title,
							 "c_dataCreated": contractParams.dateCreated,
							 "c_phone": contractParams.params[1].get('value'),
							 "c_shortName": contractParams.params[2].get('value'),
							 "c_fullName": contractParams.params[3].get('value'),
							 "c_uAddress": contractParams.params[4].get('value'),
							 "c_pAddress": contractParams.params[5].get('value'),
							 "c_inn": contractParams.params[6].get('value'),
							 "c_kpp": contractParams.params[7].get('value'),
							 "c_ogrn": contractParams.params[8].get('value'),
							 "c_fio": contractParams.params[9].get('value'),
							 "c_fioR": contractParams.params[10].get('value'),
							 "c_fioK": contractParams.params[11].get('value'),
							 "c_bank": contractParams.params[12].get('value'),
							 "c_ks": contractParams.params[13].get('value'),
							 "c_bik": contractParams.params[14].get('value'),
							 "c_rs": contractParams.params[15].get('value')
     			     })



    options = {
	'page-size': 'Letter',
	'margin-top': '0.75in',
	'margin-right': '0.75in',
	'margin-bottom': '0.95in',
	'margin-left': '0.75in',
	'footer-center': '[page]',
	'footer-spacing': 8,
	'encoding': "UTF-8",
    }


    #vdisplay = Xvfb()
    #vdisplay.start()
    # launch stuff inside virtual display here.
    pdf = pdfkit.from_string(html, False, options = options)
    #vdisplay.stop()

    # Формируем HTTP ответ в виде файла pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="dogovor.pdf"'
    response.write(pdf)

    return response
    
@session_required
def PageNotFound(request, cid):
    # Получаем тип запроса
    typeRqst = request.POST.get('ajax')

    return render(request,'404.html',locals())
