var xmlHttp = new XMLHttpRequest();
var general_url="https://your_domain.name"

// Слушатель для событий popstate
function setEventPopState(){
    window.addEventListener("popstate", function(e) {
	history_url_path = window.location.pathname.substr(0,window.location.pathname.length - 1);
	callPage(history_url_path,false);
    });
}

// Слушатель для событий onClick
function setEventClickAjax( selector ){
    $( selector ).click(function(event){
	event.preventDefault();
    element = event.target;
	tag = element.tagName;
    url = element.getAttribute('href');
	$( selector ).removeClass("active");
	if (tag == "A") element.className += " active";
    while ( url == null){
		element = element.parentNode;
        tag = element.tagName;
			if (tag == "LI"){
			return;
			}
	    $( selector ).removeClass("active");
		url = element.getAttribute('href');
		if (tag == "A") element.className += " active";
	}

	if (url.substring(0,1) != '#'){
	    callPage(url, true, "");
	} else {
	    //return;
	}
    });
}

// Фунуция для получения eToken'a для отправки POST запросов
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

//Функция для вставки HTML-кода, содержащего javascript
//el - элемент DOM, в который нужно вставить HTML
//html - собственно, сам HTML, который надо вставить

function InsertHTML(el, html)
{
el.innerHTML=html;
var scripts = el.getElementsByTagName("script");
var head = document.getElementsByTagName('head')[0];
	if (scripts.length > 0){
		for(j=0 ; j < scripts.length; j++){
		eval (scripts[j].innerHTML);
		var script = document.createElement('script');
		script.src = scripts[j].src;
		head.appendChild(script);
		}
	}
}

// POST Запрос "контента" страницы с заданным "url"
function callPage(url, history_enable, params){
    //document.getElementById("content-wrapper").style.opacity = "0";
    // Если history_enable = true -> сохраняем url в истории
        if (history_enable) history.pushState(null, null, general_url + url + '/');
    // Создать URL для подключения
        var full_url = general_url + url + '/';
    // Получаем eToken для POST запроса
        var csrftoken = getCookie('csrftoken');
    // Формируем тело запроса
	var body = 'ajax=true' + params;
    // Открываем соединение с сервером
	xmlHttp.open("POST", full_url, true);
    // Формируем заголовок запроса
	xmlHttp.setRequestHeader('X-CSRFToken', csrftoken);
	xmlHttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    // Установливаем функцию для сервера, которая выполнится после его ответа
	xmlHttp.onreadystatechange = updatePage;
    // Передаем запрос
	xmlHttp.send(body);
}

// Функция обработки ответа
function updatePage()  {
    if (xmlHttp.readyState == 4){
        var response = xmlHttp.responseText;
	// Проверяем пустой ответ или нет
	if (response.length > 0) {
    	    var div_content = document.getElementById("content-wrapper");
    	    InsertHTML(div_content, response);
            setEventClickAjax(".ajax");
            //document.getElementById("content-wrapper").style.opacity = "1";
    	}
    }
}


// Запрос html кода модального окна
function callModalPage(url, params){
    // Создать URL для подключения
        var full_url = general_url + url + '/';
    // Получаем eToken для POST запроса
        var csrftoken = getCookie('csrftoken');
    // Формируем тело запроса
	var body = 'ajax=true' + params;
    // Открываем соединение с сервером
	xmlHttp.open("POST", full_url, true);
    // Формируем заголовок запроса
	xmlHttp.setRequestHeader('X-CSRFToken', csrftoken);
	xmlHttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    // Установливаем функцию для сервера, которая выполнится после его ответа
	xmlHttp.onreadystatechange = updateModalDlg;
    // Передаем запрос
	xmlHttp.send(body);
}

// Функция обработки ответа
function updateModalDlg()  {
    if (xmlHttp.readyState == 4){
        var response = xmlHttp.responseText;
    	var modalDlgParent = document.getElementById("modalDlgParent");
    	InsertHTML(modalDlgParent, response);
    }
}


// Запрос ifacesList
function callIfaceList(url, params){
    // Создать URL для подключения
        var full_url = general_url + url + '/';
    // Получаем eToken для POST запроса
        var csrftoken = getCookie('csrftoken');
    // Формируем тело запроса
	var body = 'ajax=true' + params;
    // Открываем соединение с сервером
	xmlHttp.open("POST", full_url, true);
    // Формируем заголовок запроса
	xmlHttp.setRequestHeader('X-CSRFToken', csrftoken);
	xmlHttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    // Установливаем функцию для сервера, которая выполнится после его ответа
	xmlHttp.onreadystatechange = updateIfaceList;
    // Передаем запрос
	xmlHttp.send(body);
}

// Функция обработки ответа
function updateIfaceList()  {
    if (xmlHttp.readyState == 4){
        var response = xmlHttp.responseText;
    	var modalDlgParent = document.getElementById("ifaces");
    	InsertHTML(modalDlgParent, response);
    }
}


// Запрос unitUpdate
function callUnitUpdate(url, params){
    // Создать URL для подключения
        var full_url = general_url + url + '/';
    // Получаем eToken для POST запроса
        var csrftoken = getCookie('csrftoken');
    // Формируем тело запроса
	var body = 'ajax=true' + params;
    // Открываем соединение с сервером
	xmlHttp.open("POST", full_url, true);
    // Формируем заголовок запроса
	xmlHttp.setRequestHeader('X-CSRFToken', csrftoken);
	xmlHttp.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
    // Установливаем функцию для сервера, которая выполнится после его ответа
	xmlHttp.onreadystatechange = updateUnitUpdate;
    // Передаем запрос
	xmlHttp.send(body);
}

// Функция обработки ответа
function updateUnitUpdate()  {
    if (xmlHttp.readyState == 4){
        var response = xmlHttp.responseText;
        //alert(response);
    }
}