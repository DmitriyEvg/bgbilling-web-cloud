from lkbilling.settings import MAIN_DOMAIN, BILL_DOMAIN_URL, BILL_EXECUTER_PATH, BILL_JSON_PATH, BILL_USER, BILL_PSWD, BILL_DB_HOST, BILL_DB_USER, BILL_DB_PASSWORD, BILL_DB_NAME, BILL_MAIL, BILL_MAIL_PSWD, BILL_SMTP_HOST
import http.client, html
from django.http import HttpResponseRedirect
from django.contrib.auth import login
from django.contrib.auth.models import User
from lxml import etree
from django.shortcuts import render
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from core.views import session_required, ContractParameters, getContractList, contractPasswordChange
import json
import ssl
import urllib.parse
from urllib.parse import quote
import re
import random
import string
import smtplib
from datetime import datetime, date, time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import sqlite3
from time import sleep

# Create your views here.

# Отправка почты
def sendMail(mailTo, text='nothing'):

    server = smtplib.SMTP(BILL_SMTP_HOST, 587)
    server.starttls()

    msg = MIMEText(text, _charset='utf-8')
    msg['Subject'] = 'Код подтверждения'
    msg['From'] = BILL_MAIL
    msg['To'] = mailTo

    server.login(BILL_MAIL, BILL_MAIL_PSWD)
    server.sendmail(BILL_MAIL, mailTo,  msg.as_string())
    server.quit()


def Login(request):
    # Тип запроса
    typeRqst = request.POST.get('ajax')
    typeForm = "Login"
    return render(request,"login.html",locals())

def Recovery(request):
    # Тип запроса
    typeRqst = request.POST.get('ajax')
    # Получаем token из GET
    token = request.GET.get('token', '')
    
    # Если токен не пустой
    if (token != ""):
        # Подключаемся к БД с токенами
        conn = sqlite3.connect("recovery.sqlite")
        cursor = conn.cursor()
        # Получаем токен из БД
        cursor.execute( "SELECT username FROM recovery WHERE token='%s'" % token)
        json_result = cursor.fetchall()
        conn.commit()
        # Если ответ не пустой
        if (len(json_result) > 0):
            # Получаем userName
            userName = json_result[0][0]
            # Направляем на форму смены пароля
            typeForm = "passwordChange"
            return render(request,"login.html",locals())
        # Если ответ пустой
        else:
            typeForm = "tokenError"
            errorMsg = 'token не действителен'
            return render(request,"login.html",locals())
    # Если token пустой
    else:
        typeForm = "Recovery"
        return render(request,"login.html",locals())

def recoveryPassword(request):
    # Получаем userName и password из POST
    userName = request.POST.get('username')    
    password = request.POST.get('password')  
    
    # Установка нового пароля
    json_result = contractPasswordChange(userName, password)
    typeForm = "pswdChangeSuccess"
    
    # Удаление token'a из базы
    conn = sqlite3.connect("recovery.sqlite")
    cursor = conn.cursor()    
    cursor.execute( "DELETE FROM recovery WHERE username = '%s'" % userName )
    conn.commit()
    return render(request,"login.html",locals())
    
def sendRecovery(request):
    # Тип запроса
    typeRqst = request.POST.get('ajax')

    # Получаем userName из POST
    userName = request.POST.get('username')

    # Получаем список связанных договоров с userName в виде JSON и определяем их количество
    contractListJSON = getContractList(userName)
    contractListCount = len(contractListJSON)

    # Если количество договоров > 0 (т.е. договор существует)
    if (contractListCount > 0):
        # Генерируем token
        token = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        # Подключаемся к БД с токенами
        conn = sqlite3.connect("recovery.sqlite")
        cursor = conn.cursor()
        # Удаляем предыдущий токен (если есть)
        cursor.execute( "DELETE FROM recovery WHERE username = '%s'" % userName )
        # Вставляем данные в таблицу
        cursor.execute( "INSERT INTO recovery (username, token, date) VALUES ('%s', '%s', '%s')" % (userName, token, datetime.now()) )
        # Сохраняем изменения
        conn.commit()

        # Отправляем ссылку для восстановления пользователю
        sendMail(userName, 'https://' + MAIN_DOMAIN + '/access/recovery/?token=' + token )
        
        typeForm = "RecoveryMessage"
        return render(request,"login.html",locals())
    else:
        typeForm = "Recovery"
        errorMsg = "Аккаунт не существует"
        return render(request,"login.html",locals())

def Logout(request):

    # Тип запроса
    typeRqst = request.POST.get('ajax')

    typeForm = "Logout"
    if "username" in request.session:
        del request.session["username"]
    if "password" in request.session:
        del request.session["password"]
    if "contractId" in request.session:
        del request.session["contractId"]
    if "contractTitle" in request.session:
        del request.session["contractTitle"]
    return render(request,'login.html',locals())

def accountCreate(request):

    # Удаляем билет (если он был)
    if "regTicket" in request.session:
        del request.session["regTicket"]

    # Тип запроса
    typeRqst = request.POST.get('ajax')

    typeForm = "accountCreate"
    return render(request,"login.html",locals())

def Register(request):

    # Удаляем билет (если он был)
    if "regTicket" in request.session:
        del request.session["regTicket"]

    # Тип запроса
    typeRqst = request.POST.get('ajax')

    # Определяем повторный запрос или нет по GET параметру codeAccess
    refreshStatus = request.POST.get('codeAccess')

    # Если повторный
    if (refreshStatus == "refresh"):
        userName = request.session['username']
        password = request.session['password']
        codeAccess = str(random.randint(1000, 9999))
        request.session['codeAccess'] = codeAccess
        sendMail(userName, codeAccess )
        # Пауза 5 сек.
        sleep(5)
        # Рендерим login.html c типом формы - "Код доступа"
        typeForm = "codeAccess"
        return render(request,"login.html",locals())    
    else:
        # Получаем userName и Password из POST
        userName = request.POST.get('username', '')
        password = request.POST.get('password', '')
    
    # Получаем список связанных договоров с userName в виде JSON и определяем их количество
    contractListJSON = getContractList(userName)
    contractListCount = len(contractListJSON)

    # Если количество договоров > 0 => возвращаемся на стр. регистрации
    if (contractListCount > 0):
        # Выставляем ошибку и рендерим login.html c типом формы - "Создание аккаунта"
        typeForm = "accountCreate"
        errorMsg = "Данный Email занят"
        return render(request,"login.html",locals())
    else:
	#Cоздаем переменные сессии [username] / [password]
        request.session['username'] = userName
        request.session['password'] = password
        
        codeAccess = str(random.randint(1000, 9999))
        request.session['codeAccess'] = codeAccess
        sendMail(userName, codeAccess )
        
        # Рендерим login.html c типом формы - "Код доступа"
        typeForm = "codeAccess"
        return render(request,"login.html",locals())

def Requisite(request):

    # Тип запроса
    typeRqst = request.POST.get('ajax')

    # Проверяем наличие билета
    if "regTicket" in request.session:
        typeForm = "Requisite"
        return render(request,"login.html",locals())
    else:
        # Получаем код доступа из POST
        codeAccess = request.POST.get('codeAccess', '')
        # Если код доступа присутствует в запросе
        if (codeAccess != ""):
            # Если код доступа верен
            if (codeAccess == request.session['codeAccess']):
                # Выдаем билет на регистрацию через параметр сессии
                request.session['regTicket'] = "register_%s" % random.randint(0, 1000)
                # Рендерим login.html c типом формы - "Реквизиты"
                typeForm = "Requisite"
                return render(request,"login.html",locals())
            else:
                # Выставляем ошибку и рендерим login.html c типом формы - "Код доступа"
                typeForm = "codeAccess"
                errorMsg = "Ошибка подтверждения"
                return render(request,"login.html",locals())
        else:
            typeForm = "accountCreate"
            return render(request,"login.html",locals())

def Wellcome(request):
    # Тип запроса
    typeRqst = request.POST.get('ajax')

    # Проверяем наличие билета на регистрацию
    if "regTicket" in request.session:
	# Удаляем временный билет
        del request.session["regTicket"]
        
        # Получаем userName и Password
        userName = request.session['username']
        password = request.session['password']

        # Получаем тип Аккаунта
        accountType = request.POST.get('accountType', '')

        # Формируем данные договора из формы
        if accountType == "type1":
            # Формируем параметры договора (из POST и session) для физ. лиц
            phoneNumber = re.sub(r"[\(\)\+\- ]", "", request.POST.get('phoneNumber', ''))
            cParam = [
                [1,userName],
                [9,phoneNumber],
                [16,(request.POST.get('lastName', '') + " " + request.POST.get('firstName', ''))],
                ]
            # id шаблона для юр.лиц
            PATTERN_ID = 2
            # комментарий договора
            contractComment = quote(cParam[2][1])
        else:
            # Формируем параметры договора из (POST и session) для юр. лиц
            phoneNumber = re.sub(r"[\(\)\+\- ]", "", request.POST.get('cParam9', ''))
            cParam = [
                [1,userName],
                [2,request.POST.get('cParam2', '')],
                [3,request.POST.get('cParam3', '')],
                [4,request.POST.get('cParam4', '')],        
                [5,request.POST.get('cParam5', '')],
                [6,request.POST.get('cParam6', '')],
                [7,request.POST.get('cParam7', '')],
                [8,request.POST.get('cParam8', '')],
                [9,phoneNumber],
                [10,request.POST.get('cParam10', '')],
                [11,request.POST.get('cParam11', '')],
                [12,request.POST.get('cParam12', '')],
                [13,request.POST.get('cParam13', '')],
                [14,request.POST.get('cParam14', '')],
                [15,request.POST.get('cParam15', '')],
                [16,request.POST.get('cParam16', '')],
                ]
            # id шаблона для физ.лиц
            PATTERN_ID = 1
            # комментарий договора
            contractComment = quote(cParam[1][1])


        # Формируем GET запрос на создание договора и отправляем его в Billing
        conn = http.client.HTTPSConnection(BILL_DOMAIN_URL, context=ssl._create_unverified_context())
        conn.request("GET", "%s?user=%s&pswd=%s&date=06.04.2018&pattern_id=%s&module=contract&action=NewContract&sub_mode=0" % (BILL_EXECUTER_PATH, BILL_USER, BILL_PSWD,PATTERN_ID))
        rqst = conn.getresponse()
        xml = rqst.read()
        nodes = etree.XML(xml)
        conn.close()
        status = nodes.xpath('/data')[0].get('status')
        
        # Если статус "ОК" продолжаем заполнение
        if (status == "ok"):
            # Получаем id нового договора и создаем переменную сессии
            cid = nodes.xpath('/data/contract')[0].get('id')
            request.session['contractId'] = cid
            
            # Отправляем запрос на изменение пароля:
            conn = http.client.HTTPSConnection(BILL_DOMAIN_URL, context=ssl._create_unverified_context())
            conn.request("GET", "%s?user=%s&pswd=%s&module=contract&action=UpdateContractPassword&value=%s&cid=%s" % (BILL_EXECUTER_PATH, BILL_USER, BILL_PSWD, password, cid) )
            rqst = conn.getresponse()
            xml = rqst.read()
            nodes = etree.XML(xml)
            
            # Формируем GET запрос на изменения комментария
            conn = http.client.HTTPSConnection(BILL_DOMAIN_URL, context=ssl._create_unverified_context())
            conn.request("GET", "%s?user=%s&pswd=%s&patid=0&module=contract&action=UpdateContractTitleAndComment&comment=%s&cid=%s" % (BILL_EXECUTER_PATH, BILL_USER, BILL_PSWD,contractComment, cid))
            rqst = conn.getresponse()
            conn.close()            

            # Обновление данных договора, если (errorCheckInput = False)
            conn = http.client.HTTPSConnection(BILL_DOMAIN_URL, context=ssl._create_unverified_context())
            for param in cParam:
                paramId = param[0]
                paramValue = quote(param[1])
                if paramId != 9:
                    conn.request("GET", "%s?user=%s&pswd=%s&module=contract&action=UpdateParameterType1&pid=%s&value=%s&cid=%s" % (BILL_EXECUTER_PATH, BILL_USER, BILL_PSWD, paramId, paramValue, cid))
                    rqst = conn.getresponse()
                    conn.close()
                else:
                    conn.request("GET", "%s?user=%s&pswd=%s&comment1=&module=contract&count=1&action=UpdatePhoneInfo&pid=%s&phone1=%s&cid=%s" % (BILL_EXECUTER_PATH, BILL_USER, BILL_PSWD, paramId, paramValue, cid))
                    rqst = conn.getresponse()
                    conn.close()

            return HttpResponseRedirect('/access/contractData/')
            
        # Иначе -> выставляем ошибку и рендерим login.html c типом формы - "Создание аккаунта"
        else:
            typeForm = "accountCreate"
            errorMsg = "Ошибка создания договора, обратитесь в техподдержку"
            return render(request,"login.html",locals())
    else:
        return HttpResponseRedirect('/access/login/')

def Auth(request):

    # Получаем userName и Password из POST
    userName = request.POST.get('username', '')
    password = quote(request.POST.get('password', ''))
    
    # Получаем список связанных договоров с userName в виде JSON и определяем их количество
    contractListJSON = getContractList(userName)
    contractListCount = len(contractListJSON)
    
    request.session['contractList'] = contractListJSON

    # Если количество договоров равно 0 => возвращаемся на стр. авторизации
    if (contractListCount == 0):
        typeForm = "Login"
        errorLogin = "Логин не найден"
        return render(request,"login.html",locals())
    # Иначе
    else:
        # Проверяем на соответствие login/pswd через HTTP запрос по первому договору из JSON
        contractName = contractListJSON[0]['title']
        checkPswd = pswdVerification(contractName, password)

        # Если в ответе ОК
        if checkPswd == 'Ok':
    	    # Cоздаем переменные сессии [username] / [password]
            request.session['username'] = userName
            request.session['password'] = password
            
    	    # Если договор только один -> создаем переменные сессии [contractID] /[ contractTitle] / [contractPswd] -> редиректим в home
            if (contractListCount == 1):
                request.session['contractId'] = contractListJSON[0]['id']
                request.session['contractTitle'] = contractListJSON[0]['title']
                request.session['contractChangeState'] = 'true'
                return HttpResponseRedirect('/home/')
            else:
            # Иначе -> редиректим на стр. выбора договора
                request.session['currentURL'] = "/home/"
                return render(request,"contractSelect.html",locals())
        	
        # Если ошибка -> вызываем стр. авторизации с передачей "errorMassage"
        else:
            typeForm = "Login"
            errorPassword = "Ошибка пароля"
            return render(request,"login.html",locals())

# Функция проверки соответствия contractTitle / password
def pswdVerification(contractName, password):
    # Формируем GET запрос и отправляем его в Billing
    conn = http.client.HTTPSConnection(BILL_DOMAIN_URL, context=ssl._create_unverified_context())
    conn.request("GET", '%s/login?login=%s&password=%s' % (BILL_JSON_PATH, contractName, password) )
    rqst = conn.getresponse()
    json_string = rqst.read().decode('utf-8')
    conn.close()
    parsed_string = json.loads(json_string)
    status = parsed_string["status"]
    return status

def contractSelect(request):

    password = request.session['password']
    
    contractId =  request.GET.get('contractId')
    contractTitle =  request.GET.get('contractTitle')
    request.session['contractChangeState'] = 'true'

    checkPswd = pswdVerification(contractTitle, password)

    if checkPswd == 'Ok':
        request.session['contractId'] = contractId
        request.session['contractTitle'] = contractTitle
        return HttpResponseRedirect(request.session['currentURL'])
    else:
        return render(request,"login.html",locals())


@session_required
def pswdChange(request, cid):
    request.session['currentURL'] = "/access/pswdChange/"

    #contractParams = ContractParameters(request, cid)

    # Получаем параметры из POST запроса
    # Тип запроса
    typeRqst = request.POST.get('ajax')
    # Новый пароль + поле sendPswd
    newPswd =  request.POST.get('secret')
    sendPswd = request.POST.get('sendPswd')

    # Если запрос страницы пришел из формы
    if sendPswd:
	# Проверяем наличие данных в поле newPswd
        if newPswd:
            # Если данные присутствуют => отправляем запрос на изменение пароля:
            conn = http.client.HTTPSConnection(BILL_DOMAIN_URL)
            conn.request("GET", "%s?user=%s&pswd=%s&module=contract&action=UpdateContractPassword&value=%s&cid=%s" % (BILL_EXECUTER_PATH, BILL_USER, BILL_PSWD, newPswd, cid) )
            rqst = conn.getresponse()
            xml = rqst.read()
            nodes = etree.XML(xml)
            conn.close()
            status = nodes.xpath('/data')[0].get('status')
            if status == "error":
                formMsg = nodes.xpath('/data')[0].text
                typeMsg = "danger"
            else:
    	        formMsg = "Пароль успешно изменен."
    	        typeMsg = "success"
        # Если данных нет => выводим ошибку
        else:
            formMsg = "Поле \"Новый пароль\" обязательно для заполнения."
            typeMsg = "danger"


    return render(request,"pswdChange.html",locals())


@session_required
def contractData(request, cid):
    request.session['currentURL'] = "/access/contractData/"

    updateAction = False
    errorCheckInput = False

    contractParams = ContractParameters(request, cid)

    # Получаем параметры из POST запроса
    # Тип запроса
    typeRqst = request.POST.get('ajax')

    return render(request,"contractData.html",locals())

@session_required
def contractDataUpdate(request, cid):

    # Переменные для обработки вывода результатов
    updateAction = True        # обновление данных
    errorCheckInput = False    # присутствие ошибки в полях
    
    # Считываем текущии параметры договора из биллинга
    contractParams = ContractParameters(request, cid)

    # Получаем параметры из POST запроса
    # Тип запроса
    typeRqst = request.POST.get('ajax')

    # Проверка на заполненность данных
    for param in contractParams.params:
        paramId = param.attrib['pid']
        paramValue = len(request.POST.get('cParam' + paramId))
        if (paramValue == 0 and paramId != '7'):
            errorCheckInput = True


    # Обновление данных договора, если (errorCheckInput = False)
    if not errorCheckInput:
        conn = http.client.HTTPSConnection(BILL_DOMAIN_URL, context=ssl._create_unverified_context())
        for param in contractParams.params:
            paramId = param.attrib['pid']
            paramValue = urllib.parse.quote(request.POST.get('cParam' + paramId))
            if paramId != '9':
                conn.request("GET", "%s?user=%s&pswd=%s&module=contract&action=UpdateParameterType1&pid=%s&value=%s&cid=%s" % (BILL_EXECUTER_PATH, BILL_USER, BILL_PSWD, paramId, paramValue, cid))
                rqst = conn.getresponse()
                conn.close()
            else:
                conn.request("GET", "%s?user=%s&pswd=%s&comment1=&module=contract&count=1&action=UpdatePhoneInfo&pid=%s&phone1=%s&cid=%s" % (BILL_EXECUTER_PATH, BILL_USER, BILL_PSWD, paramId, paramValue, cid))
                rqst = conn.getresponse()
                conn.close()
            contractParams = ContractParameters(request, cid)

    return render(request,"contractData.html",locals())
