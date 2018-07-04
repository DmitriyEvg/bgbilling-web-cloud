var xmlHttp = new XMLHttpRequest();
var general_url="https://lk4.your_domain.name"

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

    // Если обычная ссылка <a href="...>
    if (tag == "A"){
      url = element.getAttribute('href');
      if (url.substring(0,1) != '#'){
        callPage(url, true, "");
      }
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
    // Если history_enable = true -> сохраняем url в истории
        if (history_enable) history.pushState(null, null, general_url + url);
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
    	    var div_content = document.getElementById("login-content");
    	    InsertHTML(div_content, response);
            setEventClickAjax(".ajax");
    	}
    }
}

function drawRegisterStep(step){
    switch (step) {
	case 1:
	    var width = "16.66%";
	    var status1 = "active";
	    var status2 = "";
	    var status3 = "";
	    break;
	case 2:
	    var width = "50%";
	    var status1 = "activated";
	    var status2 = "active";
	    var status3 = "";
	    break;
	case 3:
	    var width = "80%";
	    var status1 = "activated";
	    var status2 = "activated";
	    var status3 = "active";
	    break;
    }
    
    $("#login-header").empty();

    $("#login-header").append('\
    <div class="f1-steps">\
	<div class="f1-progress">\
	    <div class="f1-progress-line" data-now-value="16.66" data-number-of-steps="3" style="width: ' + width + ';"></div>\
	</div>\
	<div class="f1-step ' + status1 + '">\
	    <div class="f1-step-icon"><i class="fa fa-envelope"></i></div>\
	    <p class="wizard-msg">Код</br>подтверждения</p>\
	</div>\
	<div class="f1-step ' + status2 + '">\
	    <div class="f1-step-icon"><i class="fa fa-user"></i></div>\
	    <p class="wizard-msg">Тип</br>аккаунта</p>\
	</div>\
	<div class="f1-step ' + status3 + '">\
	    <div class="f1-step-icon"><i class="fa fa-info"></i></div>\
	    <p class="wizard-msg">Данные</p>\
	</div>\
    </div>\
    ');
    return true;
}
